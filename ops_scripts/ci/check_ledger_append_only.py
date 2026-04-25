#!/usr/bin/env python3
"""
check_ledger_append_only.py — W4.1 CI gate.

Wraps `.windsurf/scripts/apply_append_only_triggers.py --check` with
bypass logging. Exits 1 if any ledger is missing its BEFORE UPDATE /
BEFORE DELETE triggers.

Bypass: LEDGER_APPEND_ONLY_BYPASS=1
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIG_SCRIPT = REPO_ROOT / ".windsurf" / "scripts" / "apply_append_only_triggers.py"
BYPASS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "ledger_append_only_bypass.jsonl"


def _log_bypass(reason: str) -> None:
    try:
        BYPASS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with BYPASS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "reason": reason,
                    }
                )
                + "\n"
            )
    except OSError:
        # guardian: allow-silent-swallow -- log unwritable: non-fatal
        pass


def main() -> int:
    if os.environ.get("LEDGER_APPEND_ONLY_BYPASS") == "1":
        _log_bypass("env:LEDGER_APPEND_ONLY_BYPASS=1")
        print("[check_ledger_append_only] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    if not MIG_SCRIPT.exists():
        print(
            f"[check_ledger_append_only] migration script missing: {MIG_SCRIPT} (fail-open)", file=sys.stderr
        )
        return 0

    try:
        r = subprocess.run(
            [sys.executable, str(MIG_SCRIPT), "--check"],
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
            cwd=str(REPO_ROOT),
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[check_ledger_append_only] script error: {exc}", file=sys.stderr)
        return 2

    print(r.stderr, file=sys.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
