#!/usr/bin/env python3
"""Generate the QR codes declared by ``.animation`` blocks with the shared NeutrinoHit generator.

The codes follow the book standard of neutrinohit-map/scripts/generate_qrcode.py:
rounded modules, ECC H, quiet border 4, globe logo at 0.32. A long address hides
the central alignment pattern under the logo, so each code is checked with zbarimg
at several sizes and gets a smaller logo if needed (build_robust_qr).

  python scripts/generate_book_qr.py           # create missing codes
  python scripts/generate_book_qr.py --force   # regenerate all codes
  python scripts/generate_book_qr.py --check   # only decode them and compare with url
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "ru" / "book" / "chapters"
GENERATOR = ROOT.parent / "neutrinohit-map" / "scripts" / "generate_qrcode.py"
SIDE_PX = 1200
URL_PATTERN = re.compile(r'\burl="([^"]+)"')
QR_PATTERN = re.compile(r'\bqr="([^"]+)"')


def load_generator():
    if not GENERATOR.is_file():
        raise SystemExit(f"Общий генератор QR не найден: {GENERATOR}")
    spec = importlib.util.spec_from_file_location("generate_qrcode", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def generate(generator, url: str, destination: Path) -> bool:
    """Write the code; True if the logo had to be reduced for a long address."""
    image, scale = generator.build_robust_qr(url, side_px=SIDE_PX)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.convert("L").save(destination, "PNG", dpi=(600, 600), optimize=True)
    return scale != generator.DEFAULT_SCALE


def decode(path: Path) -> str:
    result = subprocess.run(["zbarimg", "-q", "--raw", str(path)], capture_output=True, text=True)
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--force", action="store_true", help="пересоздать существующие файлы")
    parser.add_argument("--check", action="store_true", help="только декодировать коды и сравнить с url")
    args = parser.parse_args()

    found: dict[Path, str] = {}
    for url, destination in declarations():
        previous = found.get(destination)
        if previous is not None and previous != url:
            raise ValueError(f"{destination}: один файл назначен двум адресам")
        found[destination] = url

    if not args.check:
        # The shared generator lives in the sibling neutrinohit-map checkout, which
        # a CI build does not have; it is needed only when a code must be (re)made.
        todo = [(d, u) for d, u in sorted(found.items()) if args.force or not d.exists()]
        generator = load_generator() if todo else None
        created = reduced = 0
        for destination, url in todo:
            reduced += generate(generator, url, destination)
            created += 1
        print(f"QR-коды: создано {created}, всего объявлено {len(found)}, "
              f"с уменьшенным логотипом (длинный адрес) {reduced}")

    if not shutil.which("zbarimg"):
        print("zbarimg не найден (brew install zbar): коды не проверены")
        return 2 if args.check else 0
    wrong = [(d, u) for d, u in sorted(found.items()) if (decode(d) if d.exists() else "") != u]
    for destination, url in wrong:
        print(f"НЕВЕРНО {destination.relative_to(ROOT)}: {decode(destination) or 'не читается'} != {url}")
    print(f"Проверено {len(found)} QR-кодов: {'все совпадают с url' if not wrong else f'ошибок {len(wrong)}'}")
    return 1 if wrong else 0


if __name__ == "__main__":
    raise SystemExit(main())
