#!/usr/bin/env python3
"""Extract standalone chapter PDFs from a rendered Quarto book.

The script reads chapter sources from the book's ``_quarto.yml``, matches their
titles to the PDF outline, and copies each selected page range into its own PDF.
This keeps the standalone chapter visually identical to the corresponding pages
of the complete book.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parent.parent
logging.getLogger("pypdf").setLevel(logging.ERROR)


@dataclass(frozen=True)
class Chapter:
    slug: str
    title: str
    source: Path


def parse_front_matter_title(source: Path) -> str:
    lines = source.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Нет YAML-заголовка: {source}")

    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^title:\s*(.+?)\s*$", line)
        if match:
            value = match.group(1).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value

    raise ValueError(f"В YAML-заголовке нет title: {source}")


def configured_chapters(book_dir: Path) -> list[Chapter]:
    config = (book_dir / "_quarto.yml").read_text(encoding="utf-8")
    sources = re.findall(r"^\s*-\s+(chapters/[^\s#]+\.qmd)\s*$", config, re.MULTILINE)
    chapters: list[Chapter] = []
    for relative_source in sources:
        source = book_dir / relative_source
        chapters.append(
            Chapter(
                slug=source.stem,
                title=parse_front_matter_title(source),
                source=source,
            )
        )
    if not chapters:
        raise ValueError(f"В {book_dir / '_quarto.yml'} не найдены главы")
    return chapters


def outline_pages(reader: PdfReader) -> dict[str, int]:
    pages: dict[str, int] = {}

    def visit(items: list[object]) -> None:
        for item in items:
            if isinstance(item, list):
                visit(item)
                continue
            title = getattr(item, "title", None)
            if title:
                pages[str(title)] = reader.get_destination_page_number(item)

    visit(reader.outline)
    return pages


def extract_chapter(
    input_pdf: Path,
    output_pdf: Path,
    title: str,
    author: str,
    subject: str,
    start_page: int,
    end_page: int,
) -> None:
    writer = PdfWriter()
    writer.append(str(input_pdf), pages=(start_page, end_page), import_outline=False)
    writer.add_outline_item(title, 0)
    writer.add_metadata(
        {
            "/Title": title,
            "/Author": author,
            "/Subject": subject,
        }
    )
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with output_pdf.open("wb") as stream:
        writer.write(stream)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Подготовить отдельные PDF-главы из полной PDF-книги."
    )
    parser.add_argument("language", choices=("ru", "en"), help="язык книги")
    parser.add_argument(
        "chapters",
        nargs="*",
        metavar="CHAPTER",
        help="slug главы без .qmd; без списка извлекаются все главы",
    )
    args = parser.parse_args()

    book_dir = ROOT / args.language / "book"
    output_dir = ROOT / "_site" / args.language / "book"
    config = (book_dir / "_quarto.yml").read_text(encoding="utf-8")
    output_match = re.search(r"^\s*output-file:\s*([^\s#]+)\s*$", config, re.MULTILINE)
    if output_match:
        input_pdf = output_dir / f"{output_match.group(1).removesuffix('.pdf')}.pdf"
    else:
        candidates = list(output_dir.glob("*.pdf"))
        if len(candidates) != 1:
            parser.error(
                f"Не удалось однозначно определить полную PDF-книгу в {output_dir}"
            )
        input_pdf = candidates[0]
    if not input_pdf.is_file():
        parser.error(f"Сначала соберите полную PDF-книгу: {input_pdf}")

    chapters = configured_chapters(book_dir)
    chapters_by_slug = {chapter.slug: chapter for chapter in chapters}
    requested = args.chapters or [chapter.slug for chapter in chapters]
    unknown = sorted(set(requested) - chapters_by_slug.keys())
    if unknown:
        parser.error("Неизвестные главы: " + ", ".join(unknown))

    reader = PdfReader(str(input_pdf))
    author = str((reader.metadata or {}).get("/Author", ""))
    subject = (
        "Конспект главы курса «Статистический анализ данных»"
        if args.language == "ru"
        else "Standalone chapter from the statistical analysis course"
    )
    pages = outline_pages(reader)
    missing_titles = [chapter.title for chapter in chapters if chapter.title not in pages]
    if missing_titles:
        parser.error("В закладках PDF не найдены главы: " + "; ".join(missing_titles))

    ordered = sorted(chapters, key=lambda chapter: pages[chapter.title])
    back_cover = reader.named_destinations.get("neutrinohit-back-cover")
    content_end = (
        reader.get_destination_page_number(back_cover)
        if back_cover is not None else len(reader.pages)
    )
    end_pages: dict[str, int] = {}
    for index, chapter in enumerate(ordered):
        end_pages[chapter.slug] = (
            pages[ordered[index + 1].title] if index + 1 < len(ordered) else content_end
        )

    for slug in requested:
        chapter = chapters_by_slug[slug]
        start_page = pages[chapter.title]
        end_page = end_pages[slug]
        output_pdf = output_dir / "chapters" / f"{slug}.pdf"
        extract_chapter(
            input_pdf,
            output_pdf,
            chapter.title,
            author,
            subject,
            start_page,
            end_page,
        )
        print(
            f"{chapter.title}: страницы {start_page + 1}–{end_page} -> "
            f"{output_pdf.relative_to(ROOT)}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
