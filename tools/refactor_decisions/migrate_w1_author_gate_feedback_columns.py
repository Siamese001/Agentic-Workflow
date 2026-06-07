#!/usr/bin/env python3
"""Forward-migrate Author-Gate ledger with W1 feedback-loop columns (additive, idempotent).

Plan: author-gate-feedback-loop-d4e8f1 (W1).

Writes a migration receipt under artifacts/governance/migration_receipts/.
"""

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
from tools.refactor_decisions.ledger_w1_schema import (  # noqa: E402
    W1_SCHEMA_TAG,
    ensure_w1_feedback_loop_columns,
    w1_schema_probe,
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
    receipt_path = receipt_dir / f"{ts}_author_gate_feedback_w1.json"

    if not REFACTOR_DECISION_LEDGER_DB.exists():
        if dry_run:
            print("dry_run: DB absent; would create on first ensure_row_hash / capture", flush=True)
            return 0
        sqlite3.connect(str(REFACTOR_DECISION_LEDGER_DB)).close()

    conn = sqlite3.connect(str(REFACTOR_DECISION_LEDGER_DB), timeout=30)
    try:
        added = ensure_w1_feedback_loop_columns(conn)
        probe = w1_schema_probe(conn)
        if not dry_run:
            conn.commit()
    finally:
        conn.close()

    if dry_run:
        print(json.dumps({"dry_run": True, "would_add": added, "probe": probe}, indent=2), flush=True)
        return 0

    files_to_hash = [
        REPO_ROOT / "tools" / "refactor_decisions" / "ledger_w1_schema.py",
        REPO_ROOT / "tools" / "refactor_decisions" / "precedent_capture_metadata.py",
        REPO_ROOT / "tools" / "refactor_decisions" / "author_gate_w1_bind.py",
        REPO_ROOT / ".claude" / "governance/scripts" / "post_agent_author_gate_capture.py",
        REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "post_cascade_author_gate_capture.py",
    ]
    checksums = {}
    for p in files_to_hash:
        if p.is_file():
            checksums[str(p.relative_to(REPO_ROOT)).replace("\\", "/")] = hashlib.sha256(
                p.read_bytes()
            ).hexdigest()[:16]

    receipt = {
        "change_id": "author_gate_feedback_w1",
        "plan_id": "author-gate-feedback-loop-d4e8f1",
        "wave": "W1",
        "timestamp_utc": ts,
        "w1_schema_tag": W1_SCHEMA_TAG,
        "git_head_short": _git_head_short(),
        "ledger_db": str(REFACTOR_DECISION_LEDGER_DB.relative_to(REPO_ROOT)).replace("\\", "/"),
        "columns_added_this_run": added,
        "schema_probe_after": probe,
        "changed_files": [str(p.relative_to(REPO_ROOT)).replace("\\", "/") for p in files_to_hash],
        "file_sha256_prefix": checksums,
        "verifier": "pytest tests/unit/tools/refactor_decisions/test_w1_ledger_schema.py",
        "rollback_note": "Restore ledger from backup; re-run captures are additive only — no automatic destructive downgrade.",
        "classification": "GOVERNANCE_LEDGER_ADDITIVE",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"W1 migration applied; receipt: {receipt_path.relative_to(REPO_ROOT)}", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Print probe only; do not commit receipt")
    args = ap.parse_args()
    return run_migration(dry_run=bool(args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
