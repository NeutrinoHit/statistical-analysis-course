#!/usr/bin/env python3
"""Check structural rules that can be verified before rendering the RU book."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "ru" / "book"
BOOK_CONFIG = BOOK / "_quarto.yml"
SLIDES = ROOT / "ru" / "slides"
SLIDES_CONFIG = SLIDES / "_quarto.yml"
SLIDES_INDEX = SLIDES / "index.qmd"
EXERCISES_INDEX = SLIDES / "exercises" / "index.qmd"
COURSE_INDEX = ROOT / "pages" / "index.html"
MAKEFILE = ROOT / "Makefile"
BIBLIOGRAPHY = ROOT / "shared" / "bib" / "references.bib"
QMD_SOURCES = sorted(BOOK.rglob("*.qmd"))
OJS_SOURCES = sorted(BOOK.rglob("*.ojs"))
TEXT_SOURCES = QMD_SOURCES + OJS_SOURCES
PUBLISHED_LECTURE_COUNT = 13

FORBIDDEN = {
    r'when-format="pdf"': 'use unless-format="html:js" for the PDF/EPUB fallback',
    r"\bclt-(?:widget|panel|summary)\b": "use the generic book-applet classes",
    r"\\newline\b": "start a new Markdown paragraph instead of using \\newline",
    r"наблюд[её]нн\w*\s+данн\w*": (
        "replace «наблюдённые данные» with «данные» or «результат наблюдения»"
    ),
    r"\b(?:Основная идея|Главная мысль)\b": "state the point directly",
    r"\b(?:внезапно|незаметно|на самом деле|легко видеть|очевидно)\b": (
        "state the fact and its reason without a stock transition"
    ),
    r"analysis-pipeline": "use the generic process-flow component",
    r"^\{#eq-[A-Za-z0-9_-]+(?:\s+[^}]*)?\}\s*$": (
        "attach the equation identifier to the closing $$ delimiter"
    ),
    r"^`\{ojs\}\s*$": "use a fenced OJS block with three backticks",
    r"\bfig-alt=": "put alternative text in the Markdown image description for EPUB compatibility",
    r"^:{3,}\s+book-applet\s*$": "put .book-applet in the OJS cell options",
    r'^:{3,}\s+\{\.content-visible\s+\.book-applet\s+when-format="html:js"\}': (
        "do not wrap OJS in a fenced Div; put .book-applet in the cell options"
    ),
}

INCLUDE = re.compile(r"\{\{<\s*include\s+([^ >]+)\s*>\}\}")
OJS_CELL = re.compile(r"^```\{ojs\}\n(.*?)\n```$", re.MULTILINE | re.DOTALL)
IDENTIFIER = re.compile(r"\{#((?:eq|fig|tbl)-[A-Za-z0-9_-]+)(?:[ }])")
FIGURE = re.compile(r"^!\[[^]]*\]\([^)]+\)(.*)$")
BOOK_CHAPTER = re.compile(r"^\s*-\s+chapters/(\d{2}_[a-z0-9_]+)\.qmd\s*$", re.MULTILINE)
SLIDE_SOURCE = re.compile(r"^\s{4}-\s+(\d{2}_[a-z0-9_]+)\.qmd\s*$", re.MULTILINE)
VISIBLE_LECTURE = re.compile(r'<span class="lecture-index">(\d{2})</span>')
EXERCISE_INDEX_ENTRY = re.compile(
    r"^(\d{2})\. \[[^]]+\]\((\d{2}_[a-z0-9_]+_exercises)\.html\)$",
    re.MULTILINE,
)
BIB_ENTRY = re.compile(r"^@[A-Za-z]+\{([^,]+),", re.MULTILINE)
BIB_CITATION = re.compile(r"@([A-Za-z][A-Za-z0-9:_-]+)")


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def exercise_includes(source: Path) -> list[Path]:
    """Return resolved exercise includes used by a QMD source."""
    text = source.read_text(encoding="utf-8")
    return [
        (source.parent / match.group(1)).resolve()
        for match in INCLUDE.finditer(text)
        if "_includes/exercises/" in match.group(1)
    ]


def check_course_alignment(errors: list[str]) -> None:
    """Check the one-to-one lecture, chapter, exercise and PDF contract."""
    book_config = BOOK_CONFIG.read_text(encoding="utf-8")
    slides_config = SLIDES_CONFIG.read_text(encoding="utf-8")
    slides_index = SLIDES_INDEX.read_text(encoding="utf-8")
    exercises_index = EXERCISES_INDEX.read_text(encoding="utf-8")
    course_index = COURSE_INDEX.read_text(encoding="utf-8")
    makefile = MAKEFILE.read_text(encoding="utf-8")
    bibliography_keys = set(
        BIB_ENTRY.findall(BIBLIOGRAPHY.read_text(encoding="utf-8"))
    )

    chapters = BOOK_CHAPTER.findall(book_config)
    slides = SLIDE_SOURCE.findall(slides_config)
    expected_visible = [f"{number:02d}" for number in range(1, PUBLISHED_LECTURE_COUNT + 1)]
    visible = VISIBLE_LECTURE.findall(slides_index)

    if len(chapters) != PUBLISHED_LECTURE_COUNT:
        errors.append(
            f"{BOOK_CONFIG.relative_to(ROOT)}: expected {PUBLISHED_LECTURE_COUNT} "
            f"published chapters, found {len(chapters)}"
        )
    if len(slides) != PUBLISHED_LECTURE_COUNT:
        errors.append(
            f"{SLIDES_CONFIG.relative_to(ROOT)}: expected {PUBLISHED_LECTURE_COUNT} "
            f"published lecture sources, found {len(slides)}"
        )
    if visible != expected_visible:
        errors.append(
            f"{SLIDES_INDEX.relative_to(ROOT)}: visible lecture numbers must be "
            f"01--{PUBLISHED_LECTURE_COUNT:02d} without gaps"
        )

    chapter_numbers = [stem.split("_", 1)[0] for stem in chapters]
    if chapter_numbers != expected_visible:
        errors.append(
            f"{BOOK_CONFIG.relative_to(ROOT)}: chapter numbers must be "
            f"01--{PUBLISHED_LECTURE_COUNT:02d} without gaps"
        )

    if not re.search(r"^citeproc:\s*false\s*$", book_config, re.MULTILINE):
        errors.append(
            f"{BOOK_CONFIG.relative_to(ROOT)}: citeproc must be disabled so that "
            "chapter-bibliographies.lua can number sources within each chapter"
        )
    if "assets/filters/chapter-bibliographies.lua" not in book_config:
        errors.append(
            f"{BOOK_CONFIG.relative_to(ROOT)}: missing chapter-bibliographies.lua filter"
        )

    expected_slide_numbers = expected_visible
    slide_numbers = [stem.split("_", 1)[0] for stem in slides]
    if slide_numbers != expected_slide_numbers:
        errors.append(
            f"{SLIDES_CONFIG.relative_to(ROOT)}: lecture source prefixes must be "
            f"01--{PUBLISHED_LECTURE_COUNT:02d} in publication order"
        )
    if slide_numbers != chapter_numbers:
        errors.append(
            f"{SLIDES_CONFIG.relative_to(ROOT)}: lecture and chapter numbers must match"
        )

    exercise_entries = EXERCISE_INDEX_ENTRY.findall(exercises_index)
    exercise_numbers = [number for number, _ in exercise_entries]
    expected_exercise_stems = [f"{stem}_exercises" for stem in slides]
    exercise_stems = [stem for _, stem in exercise_entries]
    if exercise_numbers != expected_visible or exercise_stems != expected_exercise_stems:
        errors.append(
            f"{EXERCISES_INDEX.relative_to(ROOT)}: exercise list must follow lectures "
            f"01--{PUBLISHED_LECTURE_COUNT:02d} without gaps"
        )

    pdf_block = re.search(
        r"^RU_PDF_CHAPTERS\s*:=\s*\\\n(.*?)(?:\n\n)",
        makefile,
        flags=re.MULTILINE | re.DOTALL,
    )
    pdf_chapters = re.findall(r"\b\d{2}_[a-z0-9_]+\b", pdf_block.group(1)) if pdf_block else []
    if pdf_chapters != chapters:
        errors.append(
            f"{MAKEFILE.relative_to(ROOT)}: RU_PDF_CHAPTERS must match the published book chapters"
        )

    for position, (slide_stem, chapter_stem) in enumerate(
        zip(slides, chapters, strict=False), start=1
    ):
        chapter = BOOK / "chapters" / f"{chapter_stem}.qmd"
        wrapper = SLIDES / "exercises" / f"{slide_stem}_exercises.qmd"
        exercises = ROOT / "_includes" / "exercises" / f"{chapter_stem}-ru.qmd"

        for path, role in (
            (chapter, "chapter"),
            (wrapper, "exercise page"),
            (exercises, "exercise include"),
        ):
            if not path.exists():
                errors.append(
                    f"lecture {position:02d}: missing {role}: {path.relative_to(ROOT)}"
                )

        if chapter.exists() and exercise_includes(chapter) != [exercises.resolve()]:
            errors.append(
                f"{chapter.relative_to(ROOT)}: chapter {position:02d} must include only "
                f"{exercises.relative_to(ROOT)}"
            )
        if chapter.exists():
            chapter_text = chapter.read_text(encoding="utf-8")
            literature_position = chapter_text.find("## Литература {.unnumbered}")
            refs_position = chapter_text.find("::: {#refs}")
            exercise_position = chapter_text.find("{{< include ../../../_includes/exercises/")
            if literature_position < 0 or refs_position < 0:
                errors.append(
                    f"{chapter.relative_to(ROOT)}: every published chapter requires "
                    "a Literature section and one #refs Div"
                )
            elif not exercise_position < literature_position < refs_position:
                errors.append(
                    f"{chapter.relative_to(ROOT)}: Literature must follow the exercise include"
                )
            cited_keys = bibliography_keys.intersection(BIB_CITATION.findall(chapter_text))
            if not cited_keys:
                errors.append(
                    f"{chapter.relative_to(ROOT)}: every published chapter requires "
                    "at least one bibliographic citation"
                )
        if wrapper.exists() and exercise_includes(wrapper) != [exercises.resolve()]:
            errors.append(
                f"{wrapper.relative_to(ROOT)}: lecture {position:02d} must include only "
                f"{exercises.relative_to(ROOT)}"
            )

        expected_slide_links = (
            f'{slide_stem}.html',
            f'exercises/{slide_stem}_exercises.html',
            f'../book/chapters/{chapter_stem}.pdf',
            f'../book/chapters/{chapter_stem}.html',
        )
        for link in expected_slide_links:
            if link not in slides_index:
                errors.append(
                    f"{SLIDES_INDEX.relative_to(ROOT)}: lecture {position:02d} is missing link {link}"
                )

        expected_course_links = (
            f'./ru/slides/{slide_stem}.html',
            f'./ru/slides/exercises/{slide_stem}_exercises.html',
            f'./ru/book/chapters/{chapter_stem}.pdf',
            f'./ru/book/chapters/{chapter_stem}.html',
        )
        for link in expected_course_links:
            if link not in course_index:
                errors.append(
                    f"{COURSE_INDEX.relative_to(ROOT)}: lecture {position:02d} is missing link {link}"
                )


def main() -> None:
    errors: list[str] = []
    identifiers: dict[str, tuple[Path, int]] = {}

    check_course_alignment(errors)

    for source in TEXT_SOURCES:
        text = source.read_text(encoding="utf-8")
        relative = source.relative_to(ROOT)

        for pattern, message in FORBIDDEN.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
                errors.append(f"{relative}:{line_number(text, match.start())}: {message}")

        if source.suffix == ".qmd" and "::: chapter-opening" in text:
            opening = text.split("::: chapter-opening", 1)[1].split(":::", 1)[0]
            if "chapter-opening-label" not in opening:
                errors.append(f"{relative}: chapter-opening requires chapter-opening-label")

        if source.suffix == ".qmd":
            for cell in OJS_CELL.finditer(text):
                body = cell.group(1)
                cell_line = line_number(text, cell.start())
                if "//| classes: book-applet" not in body:
                    errors.append(
                        f"{relative}:{cell_line}: OJS cell requires classes: book-applet"
                    )
                if "{{< include " not in body:
                    errors.append(
                        f"{relative}:{cell_line}: move OJS code to assets/applets and include it"
                    )

        for match in INCLUDE.finditer(text):
            target = (source.parent / match.group(1)).resolve()
            if not target.exists():
                errors.append(
                    f"{relative}:{line_number(text, match.start())}: include not found: {match.group(1)}"
                )

        for match in IDENTIFIER.finditer(text):
            identifier = match.group(1)
            location = (source, line_number(text, match.start()))
            if identifier in identifiers:
                previous, previous_line = identifiers[identifier]
                errors.append(
                    f"{relative}:{location[1]}: duplicate #{identifier}; "
                    f"first used in {previous.relative_to(ROOT)}:{previous_line}"
                )
            else:
                identifiers[identifier] = location

        if source.suffix == ".ojs":
            for number, line in enumerate(text.splitlines(), 1):
                if line.startswith(":::") or line.startswith("```"):
                    errors.append(
                        f"{relative}:{number}: OJS include must contain code only"
                    )
                if line.startswith("//|"):
                    errors.append(
                        f"{relative}:{number}: put OJS cell options in the chapter fence"
                    )
                if 'style="' in line:
                    errors.append(
                        f"{relative}:{number}: use a reusable book-applet class instead of inline CSS"
                    )

        if source.parent == BOOK / "chapters":
            for pattern in (r"\{=html\}", r"<style(?:\s|>)", r"<script(?:\s|>)"):
                for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                    errors.append(
                        f"{relative}:{line_number(text, match.start())}: "
                        "move chapter HTML/CSS/JavaScript to a reusable component"
                    )
            for number, line in enumerate(text.splitlines(), 1):
                figure = FIGURE.match(line)
                if figure and "{#fig-" not in figure.group(1):
                    errors.append(f"{relative}:{number}: figure requires a #fig- identifier")

    large_assets = [
        path for path in (BOOK / "assets").rglob("*")
        if path.is_file() and path.stat().st_size > 15 * 1024 * 1024
    ]
    for path in large_assets:
        errors.append(
            f"{path.relative_to(ROOT)}: asset is larger than 15 MiB; document its need and licence"
        )

    if errors:
        print("Book source checks failed:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print(
        "Book source checks passed: "
        f"{len(QMD_SOURCES)} QMD files, {len(OJS_SOURCES)} OJS includes, "
        f"{len(identifiers)} cross-reference IDs"
    )


if __name__ == "__main__":
    main()
