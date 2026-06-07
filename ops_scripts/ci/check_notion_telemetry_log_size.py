"""
check_notion_telemetry_log_size.py — CI gate NP5.

Verifies that the Notion Plans-DB telemetry JSONL files do not grow
unboundedly.  Warns when a log exceeds WARN_BYTES (5 MB) and errors when
it exceeds ERROR_BYTES (20 MB).

DS-4 of notion-plans-db-hygiene-deferred-scope-d4f7c1.

Exit codes:
    0   All logs within acceptable size.
    1   One or more logs exceed ERROR_BYTES (requires operator action).

Bypass: set ``NOTION_TELEMETRY_LOG_SIZE_BYPASS=1`` to force exit 0.
Fail-closed: set ``NOTION_TELEMETRY_LOG_SIZE_FAIL_CLOSED=1`` to treat
    WARN as ERROR.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

WARN_BYTES = 5 * 1024 * 1024   # 5 MB
ERROR_BYTES = 20 * 1024 * 1024  # 20 MB

WATCHED_LOGS = [
    REPO_ROOT / "artifacts" / "governance" / "plans_db_writes.jsonl",
    REPO_ROOT / "artifacts" / "governance" / "wave_lifecycle_notion.jsonl",
]

REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "notion_telemetry_log_size.json"


def _human(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


def main() -> int:
    if os.environ.get("NOTION_TELEMETRY_LOG_SIZE_BYPASS") == "1":
        print("NOTION_TELEMETRY_LOG_SIZE_BYPASS=1 — skipping log size check")
        return 0

    fail_closed = os.environ.get("NOTION_TELEMETRY_LOG_SIZE_FAIL_CLOSED") == "1"

    findings: list[dict] = []
    error_count = 0
    warn_count = 0

    for log_path in WATCHED_LOGS:
        if not log_path.exists():
            findings.append({
                "path": str(log_path.relative_to(REPO_ROOT)),
                "level": "INFO",
                "size_bytes": 0,
                "message": "not present",
            })
            continue

        size = log_path.stat().st_size
        rel = str(log_path.relative_to(REPO_ROOT))

        if size >= ERROR_BYTES:
            level = "ERROR"
            error_count += 1
            msg = (
                f"{rel}: {_human(size)} — exceeds ERROR threshold "
                f"({_human(ERROR_BYTES)}). Run rotation or archive the log."
            )
        elif size >= WARN_BYTES:
            level = "WARN"
            if fail_closed:
                error_count += 1
                level = "ERROR"
            else:
                warn_count += 1
            msg = (
                f"{rel}: {_human(size)} — exceeds WARN threshold "
                f"({_human(WARN_BYTES)}). Log rotation will trigger at "
                f"{_human(10 * 1024 * 1024)}."
            )
        else:
            level = "OK"
            msg = f"{rel}: {_human(size)} — within limits"

        findings.append({
            "path": rel,
            "level": level,
            "size_bytes": size,
            "message": msg,
        })

        print(f"  [{level}] {msg}")

    summary = {
        "errors": error_count,
        "warnings": warn_count,
        "findings": findings,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if error_count:
        print(f"\nNP5 FAIL — {error_count} log(s) exceed size limit")
        return 1

    print(f"\nNP5 OK — all telemetry logs within limits ({warn_count} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
