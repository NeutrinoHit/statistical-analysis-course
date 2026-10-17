#!/usr/bin/env python3
"""Make data-notebook attributes in rendered slides relative to the project.

{{< embed >}} writes the absolute source path of the notebook into the
data-notebook attribute of the rendered HTML. The path names the build machine
and has no use on the public site. As a Quarto post-render script (Quarto sets
QUARTO_PROJECT_DIR and QUARTO_PROJECT_OUTPUT_FILES) this rewrites it to the
path relative to the project, for example notebooks/binomial_pmf_demo.qmd.
"""

from __future__ import annotations

import os
from pathlib import Path


def prefixes(project: Path) -> list[str]:
    paths = {str(project.absolute()), str(project.resolve())}
    return [f'data-notebook="{path}/' for path in sorted(paths)]


def strip_source_paths(project: Path, outputs: list[str]) -> int:
    changed = 0
    for name in outputs:
        html = Path(name)
        if html.suffix != ".html" or not html.is_file():
            continue
        text = html.read_text(encoding="utf-8")
        updated = text
        for prefix in prefixes(project):
            updated = updated.replace(prefix, 'data-notebook="')
        if updated != text:
            html.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def main() -> None:
    project = Path(os.environ.get("QUARTO_PROJECT_DIR", Path.cwd()))
    outputs = os.environ.get("QUARTO_PROJECT_OUTPUT_FILES", "").splitlines()
    strip_source_paths(project, outputs)


if __name__ == "__main__":
    main()
