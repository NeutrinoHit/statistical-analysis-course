#!/usr/bin/env python3
"""Wait until rendered site artifacts exist and are non-empty."""

from __future__ import annotations

import argparse
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser.parse_args()


def missing_files(paths: list[Path]) -> list[Path]:
    return [path for path in paths if not path.is_file() or path.stat().st_size == 0]


def main() -> int:
    args = parse_args()
    deadline = time.monotonic() + args.timeout

    while True:
        missing = missing_files(args.paths)
        if not missing:
            print(f"Site output check passed: {len(args.paths)} files")
            return 0
        if time.monotonic() >= deadline:
            print("Site output check failed; missing or empty files:")
            for path in missing:
                print(f"  - {path}")
            return 1
        time.sleep(0.25)


if __name__ == "__main__":
    raise SystemExit(main())
