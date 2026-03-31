"""CI Guard 4: Duplicate test file detector.

Fails CI if any test files matching _1.py, _copy.py, or _backup.py suffix patterns exist.
These indicate accidental duplication during refactors.

Exit codes:
  0 = clean
  1 = duplicates found

Usage:
    python ops_scripts/ci/scan_duplicate_tests.py
"""

import sys
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = ROOT / TESTS_DIR
EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

DUP_SUFFIXES = ("_1.py", "_copy.py", "_backup.py", "_old.py", "_orig.py")
THRESHOLD = 0


def scan_duplicates() -> list[str]:
    found: list[str] = []
    for fpath in TESTS_DIR.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in fpath.parts):
            continue
        name = fpath.name
        if any(name.endswith(suffix) for suffix in DUP_SUFFIXES):
            found.append(str(fpath.relative_to(ROOT)).replace("\\", "/"))
    return sorted(found)


def main() -> int:
    duplicates = scan_duplicates()
    print(f"Duplicate test scan: found={len(duplicates)}  threshold={THRESHOLD}")
    if len(duplicates) > THRESHOLD:
        print(f"FAIL: {len(duplicates)} duplicate test files detected (threshold={THRESHOLD}):")
        for f in duplicates[:50]:
            print(f"  {f}")
        return 1
    print(f"OK: duplicate_tests={len(duplicates)} <= {THRESHOLD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
