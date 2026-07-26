"""Write a capsule and its machine-readable manifest."""

from __future__ import annotations

import json
from pathlib import Path

from .capsule import Capsule


def write_capsule(capsule: Capsule, output: Path) -> tuple[Path, Path]:
    output.mkdir(parents=True, exist_ok=True)
    markdown_path = output / "context-capsule.md"
    manifest_path = output / "manifest.json"
    markdown_path.write_text(capsule.markdown, encoding="utf-8", newline="\n")
    manifest_path.write_text(
        json.dumps(capsule.manifest(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return markdown_path, manifest_path

