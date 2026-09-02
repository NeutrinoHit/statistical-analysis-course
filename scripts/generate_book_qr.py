#!/usr/bin/env python3
"""Generate branded QR codes declared by ``.animation`` blocks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import qrcode
from PIL import Image
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "ru" / "book" / "chapters"
LOGO = ROOT / "shared" / "figures" / "dvnlogo.png"
URL_PATTERN = re.compile(r'\burl="([^"]+)"')
QR_PATTERN = re.compile(r'\bqr="([^"]+)"')


def declarations() -> list[tuple[str, Path]]:
    result: list[tuple[str, Path]] = []
    for source in sorted(CHAPTERS.glob("*.qmd")):
        for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            if ".animation" not in line:
                continue
            url_match = URL_PATTERN.search(line)
            qr_match = QR_PATTERN.search(line)
            if not url_match or not qr_match:
                raise ValueError(f"{source}:{line_number}: блок .animation требует url и qr")
            destination = (source.parent / qr_match.group(1)).resolve()
            qr_root = (ROOT / "ru" / "book" / "assets" / "qr").resolve()
            if destination.parent != qr_root:
                raise ValueError(f"{source}:{line_number}: QR-код должен находиться в {qr_root}")
            result.append((url_match.group(1), destination))
    return result


def generate(url: str, destination: Path) -> None:
    code = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=24,
        border=4,
    )
    code.add_data(url)
    code.make(fit=True)
    image = code.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(radius_ratio=0.8),
        embedded_image_path=str(LOGO),
    ).convert("RGB")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="пересоздать существующие файлы")
    args = parser.parse_args()

    found: dict[Path, str] = {}
    for url, destination in declarations():
        previous = found.get(destination)
        if previous is not None and previous != url:
            raise ValueError(f"{destination}: один файл назначен двум адресам")
        found[destination] = url

    created = 0
    for destination, url in sorted(found.items()):
        if args.force or not destination.exists():
            generate(url, destination)
            created += 1
    print(f"QR-коды: создано {created}, всего объявлено {len(found)}")


if __name__ == "__main__":
    main()
