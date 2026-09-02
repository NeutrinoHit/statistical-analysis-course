#!/usr/bin/env python3
"""Check structural rules that can be verified before rendering the RU book."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "ru" / "book"
QMD_SOURCES = sorted(BOOK.rglob("*.qmd"))
OJS_SOURCES = sorted(BOOK.rglob("*.ojs"))
TEXT_SOURCES = QMD_SOURCES + OJS_SOURCES

FORBIDDEN = {
    r'when-format="pdf"': 'use unless-format="html:js" for the PDF/EPUB fallback',
    r"\bclt-(?:widget|panel|summary)\b": "use the generic book-applet classes",
    r"\\newline\b": "start a new Markdown paragraph instead of using \\newline",
    r"наблюд[её]нн\w*": "replace the participle with «данные», «полученное значение» or «результат наблюдения»",
    r"\b(?:Основная идея|Главная мысль)\b": "state the point directly",
    r"\b(?:внезапно|незаметно|на самом деле|легко видеть|очевидно)\b": (
        "state the fact and its reason without a stock transition"
    ),
    r"analysis-pipeline": "use the generic process-flow component",
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


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def main() -> None:
    errors: list[str] = []
    identifiers: dict[str, tuple[Path, int]] = {}

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
