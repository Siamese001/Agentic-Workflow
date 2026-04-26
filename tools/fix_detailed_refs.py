"""One-shot rewriter: strip '_detailed.md' -> '.md' inside docs/reference/.

Scope: only docs/reference/. Skips Transformer Templates (uppercase _DETAILED.md).
Edits both .md and .json files in place. Idempotent.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "docs" / "reference"
SKIP_DIRS = {"Transformer Templates", "_archive"}

OLD = "_detailed.md"
NEW = ".md"


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def main() -> int:
    if not ROOT.is_dir():
        print(f"ERROR: {ROOT} not found", file=sys.stderr)
        return 1

    targets = []
    for ext in (".md", ".json"):
        for p in ROOT.rglob(f"*{ext}"):
            if p.is_file() and not should_skip(p):
                targets.append(p)

    rewritten = 0
    total_replacements = 0
    for p in targets:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"SKIP (non-utf8): {p}")
            continue
        if OLD not in text:
            continue
        count = text.count(OLD)
        new_text = text.replace(OLD, NEW)
        p.write_text(new_text, encoding="utf-8")
        rewritten += 1
        total_replacements += count
        print(f"  {count:>3}x  {p.relative_to(ROOT)}")

    print(f"\nDONE: {total_replacements} replacements across {rewritten} files (scanned {len(targets)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
