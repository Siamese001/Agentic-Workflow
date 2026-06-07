#!/usr/bin/env python3
"""Forward-migrate Author-Gate ledger decision_signals W2 columns (additive)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB  # noqa: E402
from tools.refactor_decisions.ledger_w2_schema import (  # noqa: E402
    W2_SCHEMA_TAG,
    ensure_w2_decision_signal_columns,
    w2_schema_probe,
)


def _git_head_short() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
            check=False,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def run_migration(*, dry_run: bool) -> int:
    REFACTOR_DECISION_LEDGER_DB.parent.mkdir(parents=True, exist_ok=True)
    receipt_dir = REPO_ROOT / "artifacts" / "governance" / "migration_receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt_path = receipt_dir / f"{ts}_author_gate_feedback_w2.json"

    if not REFACTOR_DECISION_LEDGER_DB.exists():
        if dry_run:
            print("dry_run: DB absent; W2 columns apply on first capture init", flush=True)
            return 0
        sqlite3.connect(str(REFACTOR_DECISION_LEDGER_DB)).close()

    conn = sqlite3.connect(str(REFACTOR_DECISION_LEDGER_DB), timeout=30)
    try:
        added = ensure_w2_decision_signal_columns(conn)
        probe = w2_schema_probe(conn)
        if not dry_run:
            conn.commit()
    finally:
        conn.close()

    if dry_run:
        print(json.dumps({"dry_run": True, "would_add": added, "probe": probe}, indent=2), flush=True)
        return 0

    files_to_hash = [
        REPO_ROOT / "tools" / "refactor_decisions" / "ledger_w2_schema.py",
        REPO_ROOT / "tools" / "refactor_decisions" / "author_gate_w2_signals.py",
        REPO_ROOT / ".cursor" / "scripts" / "post_cursor_agent_author_gate_capture.py",
        REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf" / "post_cascade_author_gate_capture.py",
    ]
    checksums = {}
    for p in files_to_hash:
        if p.is_file():
            checksums[str(p.relative_to(REPO_ROOT)).replace("\\", "/")] = hashlib.sha256(
                p.read_bytes()
            ).hexdigest()[:16]

    receipt = {
        "change_id": "author_gate_feedback_w2",
        "plan_id": "author-gate-feedback-loop-d4e8f1",
        "wave": "W2",
        "timestamp_utc": ts,
        "w2_schema_tag": W2_SCHEMA_TAG,
        "git_head_short": _git_head_short(),
        "ledger_db": str(REFACTOR_DECISION_LEDGER_DB.relative_to(REPO_ROOT)).replace("\\", "/"),
        "columns_added_this_run": added,
        "schema_probe_after": probe,
        "changed_files": [str(p.relative_to(REPO_ROOT)).replace("\\", "/") for p in files_to_hash],
        "file_sha256_prefix": checksums,
        "verifier": "pytest tests/unit/tools/refactor_decisions/test_w2_ledger_schema.py tests/unit/tools/refactor_decisions/test_author_gate_w2_golden_packet.py",
        "rollback_note": "Restore ledger from backup; additive columns only.",
        "classification": "GOVERNANCE_LEDGER_ADDITIVE",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"W2 migration applied; receipt: {receipt_path.relative_to(REPO_ROOT)}", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return run_migration(dry_run=bool(args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
