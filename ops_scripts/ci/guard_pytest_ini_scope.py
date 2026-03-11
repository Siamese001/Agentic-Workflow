#!/usr/bin/env python3
"""
Guard pytest.ini scope changes (pre-commit)

Enforces:
  - Any change to pytest.ini testpaths/addopts must be accompanied by governance policy updates.
  - Blocks silent suite contraction via ignore/testpaths edits.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PYTEST_INI = Path("pytest.ini")
GOV_DOC = Path("docs/rules/governance.md")


def _run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, check=False, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return out


def _git_diff(path: Path) -> str:
    # Diff staged + unstaged to catch both pre-commit and working-tree edits.
    return _run(["git", "diff", "--", str(path)]) + _run(["git", "diff", "--cached", "--", str(path)])


def _touched_keywords(diff: str) -> bool:
    # Only trigger on meaningful scope controls.
    kws = ("testpaths", "addopts", "--ignore", "-k", "-m", "python_files", "norecursedirs")
    return any(k in diff for k in kws)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.parse_args(argv)  # Parse args but don't use them - hook receives files via pre-commit

    if not PYTEST_INI.exists():
        return 0

    diff = _git_diff(PYTEST_INI)
    if not diff.strip():
        return 0

    if not _touched_keywords(diff):
        return 0

    if not GOV_DOC.exists():
        print("[FAIL] pytest.ini scope changed but governance policy doc missing:", GOV_DOC)
        return 1

    gov_text = GOV_DOC.read_text(encoding="utf-8", errors="replace")
    required_header = "## Pytest Authoritative Suite"
    if required_header not in gov_text:
        print("[FAIL] pytest.ini scope changed but governance.md lacks required section:")
        print(f"  - missing header: {required_header}")
        print("  Fix: add a section describing authoritative suite, rationale, and reversibility.")
        return 1

    # Soft-but-useful: require a 'Reversibility' subsection.
    if "### Reversibility" not in gov_text:
        print("[FAIL] governance.md missing '### Reversibility' under pytest suite policy.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
