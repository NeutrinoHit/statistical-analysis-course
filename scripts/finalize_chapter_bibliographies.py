#!/usr/bin/env python3
"""Keep only the current chapter's cited sources in rendered HTML pages."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK_CONFIG = ROOT / "ru" / "book" / "_quarto.yml"
HTML_CHAPTERS = ROOT / "_site" / "ru" / "book" / "chapters"

CHAPTER = re.compile(
    r"^\s*-\s+chapters/(\d{2}_[a-z0-9_]+)\.qmd\s*$", re.MULTILINE
)
CITATION = re.compile(
    r'(<span class="citation" data-cites="([^"]+)">)(.*?)(</span>)', re.DOTALL
)
REFS_OPEN = re.compile(r'<div id="refs"[^>]*>')
ENTRY_OPEN = re.compile(r'<div id="ref-([^"]+)"[^>]*>')
DIV_TOKEN = re.compile(r"<div\b[^>]*>|</div>")


def matching_div_end(text: str, opening: re.Match[str]) -> int:
    """Return the position just after the closing tag matching opening."""
    depth = 0
    for token in DIV_TOKEN.finditer(text, opening.start()):
        if token.group().startswith("</"):
            depth -= 1
            if depth == 0:
                return token.end()
        else:
            depth += 1
    raise ValueError("unclosed div")


def ordered_citation_keys(html: str, refs_start: int) -> list[str]:
    keys: list[str] = []
    for citation in CITATION.finditer(html, 0, refs_start):
        for key in citation.group(2).split():
            if key not in keys:
                keys.append(key)
    return keys


def bibliography_entries(html: str, start: int, end: int) -> dict[str, str]:
    entries: dict[str, str] = {}
    position = start
    while opening := ENTRY_OPEN.search(html, position, end):
        entry_end = matching_div_end(html, opening)
        entries[opening.group(1)] = html[opening.start():entry_end]
        position = entry_end
    return entries


def renumber_entry(entry: str, number: int) -> str:
    return re.sub(
        r'^(<div id="ref-[^"]+"[^>]*>\s*)\[\d+\]',
        rf"\g<1>[{number}]",
        entry,
        count=1,
        flags=re.DOTALL,
    )


def finalize(path: Path) -> int:
    html = path.read_text(encoding="utf-8")
    refs_open = REFS_OPEN.search(html)
    if refs_open is None:
        raise ValueError(f"{path}: missing #refs bibliography")
    refs_end = matching_div_end(html, refs_open)
    keys = ordered_citation_keys(html, refs_open.start())
    entries = bibliography_entries(html, refs_open.end(), refs_end)
    missing = [key for key in keys if key not in entries]
    if missing:
        raise ValueError(f"{path}: missing rendered references: {', '.join(missing)}")

    numbers = {key: index for index, key in enumerate(keys, start=1)}

    def replace_citation(match: re.Match[str]) -> str:
        citation_numbers = [str(numbers[key]) for key in match.group(2).split()]
        return match.group(1) + "[" + ", ".join(citation_numbers) + "]" + match.group(4)

    html = CITATION.sub(replace_citation, html)

    refs_open = REFS_OPEN.search(html)
    if refs_open is None:
        raise ValueError(f"{path}: bibliography disappeared during processing")
    refs_end = matching_div_end(html, refs_open)
    opening_tag = re.sub(
        r'\s+style="display:\s*none;?"', "", refs_open.group()
    )
    rendered_entries = [
        renumber_entry(entries[key], numbers[key]) for key in keys
    ]
    bibliography = opening_tag + "\n" + "\n".join(rendered_entries) + "\n</div>"
    html = html[:refs_open.start()] + bibliography + html[refs_end:]
    path.write_text(html, encoding="utf-8")
    return len(keys)


def main() -> None:
    chapter_stems = CHAPTER.findall(BOOK_CONFIG.read_text(encoding="utf-8"))
    counts: list[str] = []
    for stem in chapter_stems:
        html_path = HTML_CHAPTERS / f"{stem}.html"
        if not html_path.exists():
            raise SystemExit(f"Missing rendered chapter: {html_path}")
        counts.append(f"{stem}:{finalize(html_path)}")
    print("Chapter bibliographies: " + ", ".join(counts))


if __name__ == "__main__":
    main()
