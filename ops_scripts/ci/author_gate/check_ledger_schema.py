#!/usr/bin/env python3
"""
check_ledger_schema.py — CI gate: decision ledger matches canonical DDL.

Uses the idempotent migrator in --check mode. Exits:
    0 = schema matches canonical DDL
    1 = drift detected
    2 = DB missing or migrator failure

Constitutional: no shell=True, subprocess.run with timeout, UTF-8 stdio.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MIGRATOR = REPO_ROOT / ".claude" / "governance/scripts" / "apply_ledger_schema.py"


def main() -> int:
    if not MIGRATOR.exists():
        print(f"[check_ledger_schema] Missing migrator: {MIGRATOR}", file=sys.stderr)
        return 2
    try:
        result = subprocess.run(
            [sys.executable, str(MIGRATOR), "--check"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("[check_ledger_schema] Migrator timed out", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"[check_ledger_schema] Migrator invocation failed: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(result.stdout)
    if result.returncode == 0:
        print("[check_ledger_schema] PASS — schema matches canonical DDL.")
        return 0
    if result.returncode == 1:
        print(
            "[check_ledger_schema] FAIL — drift detected. Run: python .claude/governance/scripts/apply_ledger_schema.py"
        )
        return 1
    sys.stderr.write(result.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
