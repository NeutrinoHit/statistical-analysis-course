#!/usr/bin/env python3
"""Remove browser-only code from a Quarto EPUB and validate its container."""

from __future__ import annotations

import argparse
import os
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree


SCRIPT = re.compile(rb"\s*<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
IFRAME = re.compile(rb"<iframe\b", re.IGNORECASE)
REMOTE_MEDIA = re.compile(
    rb"<(?:audio|img|source|video)\b[^>]*\bsrc=[\"']https?://",
    re.IGNORECASE,
)
NAV_ITEM = re.compile(
    rb'(<item\b[^>]*\bid="nav"[^>]*\bproperties=")([^"]*)(")',
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a static, self-contained EPUB after Quarto rendering."
    )
    parser.add_argument("epub", type=Path, help="EPUB file produced by Quarto")
    return parser.parse_args()


def validate(entries: list[tuple[zipfile.ZipInfo, bytes]]) -> None:
    names = [info.filename for info, _ in entries]
    if not names or names[0] != "mimetype":
        raise SystemExit("EPUB requires an uncompressed mimetype entry first")

    mimetype = entries[0]
    if mimetype[0].compress_type != zipfile.ZIP_STORED:
        raise SystemExit("EPUB mimetype entry must be stored without compression")
    if mimetype[1] != b"application/epub+zip":
        raise SystemExit("Unexpected EPUB mimetype")

    for info, data in entries:
        if not info.filename.endswith((".xhtml", ".opf", ".ncx")):
            continue
        if SCRIPT.search(data):
            raise SystemExit(f"Browser script remains in {info.filename}")
        if IFRAME.search(data):
            raise SystemExit(f"iframe remains in {info.filename}")
        if REMOTE_MEDIA.search(data):
            raise SystemExit(f"Remote media remains in {info.filename}")
        try:
            ElementTree.fromstring(data)
        except ElementTree.ParseError as error:
            raise SystemExit(f"Invalid XML in {info.filename}: {error}") from error


def main() -> None:
    epub = parse_args().epub.resolve()
    if not epub.is_file():
        raise SystemExit(f"EPUB not found: {epub}")
    original_mode = epub.stat().st_mode

    with zipfile.ZipFile(epub) as archive:
        entries = []
        removed_scripts = 0
        for info in archive.infolist():
            data = archive.read(info.filename)
            if info.filename.endswith(".xhtml"):
                data, count = SCRIPT.subn(b"", data)
                removed_scripts += count
            entries.append((info, data))

    nav_uses_mathml = any(
        info.filename == "EPUB/nav.xhtml" and b"<math" in data
        for info, data in entries
    )
    if nav_uses_mathml:
        updated_entries = []
        for info, data in entries:
            if info.filename == "EPUB/content.opf":
                def add_mathml(match: re.Match[bytes]) -> bytes:
                    properties = match.group(2).split()
                    if b"mathml" not in properties:
                        properties.append(b"mathml")
                    return match.group(1) + b" ".join(properties) + match.group(3)

                data, count = NAV_ITEM.subn(add_mathml, data, count=1)
                if count != 1:
                    raise SystemExit("Could not update the EPUB navigation manifest entry")
            updated_entries.append((info, data))
        entries = updated_entries

    with tempfile.NamedTemporaryFile(
        prefix=f".{epub.stem}-", suffix=".epub", dir=epub.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)

    try:
        with zipfile.ZipFile(temporary, "w") as archive:
            for info, data in entries:
                if info.filename == "mimetype":
                    info.compress_type = zipfile.ZIP_STORED
                archive.writestr(info, data)

        with zipfile.ZipFile(temporary) as archive:
            rewritten = [(info, archive.read(info.filename)) for info in archive.infolist()]
        validate(rewritten)
        os.chmod(temporary, original_mode)
        os.replace(temporary, epub)
    finally:
        if temporary.exists():
            temporary.unlink()

    print(
        "EPUB подготовлен: "
        f"удалено браузерных скриптов — {removed_scripts}; "
        f"MathML в оглавлении — {'да' if nav_uses_mathml else 'нет'}"
    )


if __name__ == "__main__":
    main()
