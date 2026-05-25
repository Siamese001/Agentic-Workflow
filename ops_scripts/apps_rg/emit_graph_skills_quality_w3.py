#!/usr/bin/env python3
"""W3: controlled graph v2 migration + receipt."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.graph_v2_quality_migration import run_w3_migration

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
RECEIPT_JSON = REPORTS / "graph_v2_migration_receipt.json"
W3_JSON = REPORTS / "graph_skills_quality_w3_graph_v2.json"
RECEIPT_W3 = REPORTS / "graph_skills_quality_w3_receipt.json"


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def main() -> int:
    migration = run_w3_migration(repo_root=REPO, apply_patches=True, rematerialize_sqlite=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    RECEIPT_JSON.write_text(json.dumps(migration, indent=2) + "\n", encoding="utf-8")

    w3_aggregate = {
        "schema": "graph_skills_quality_w3_graph_v2_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_id": PLAN_ID,
        "wave": "W3",
        "status": migration.get("status"),
        "graph_v2_digest_pinned": migration.get("graph_v2_digest_pinned"),
        "active_orphan_count_after": migration.get("active_orphan_count_after"),
        "controlled_migration_count": len(migration.get("controlled_migrations") or []),
        "phase_gate_g_w3": {
            "gate": "G-W3",
            "status": "PASS" if migration.get("status") == "PASS" else "FAIL",
            "zero_active_orphans": migration.get("active_orphan_count_after") == 0,
            "graph_v2_digest_pinned": bool(migration.get("graph_v2_digest_pinned")),
            "rollback_doc_exists": (REPO / "docs/apps_rg/graph_skills_graph_v2_rollback.md").is_file(),
        },
        "migration_receipt": RECEIPT_JSON.relative_to(REPO).as_posix(),
    }
    W3_JSON.write_text(json.dumps(w3_aggregate, indent=2) + "\n", encoding="utf-8")

    cmd = [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w3.py"]
    code = 0 if migration.get("status") == "PASS" else 1
    receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "wave_id": "W3",
        "proof_class": "DETERMINISTIC_RUNTIME_PROOF",
        "command": " ".join(cmd),
        "command_argv": cmd,
        "cwd": str(REPO),
        "env_vars": {},
        "exit_code": code,
        "artifact_paths": [
            RECEIPT_JSON.relative_to(REPO).as_posix(),
            W3_JSON.relative_to(REPO).as_posix(),
            RECEIPT_W3.relative_to(REPO).as_posix(),
            migration.get("backup_v1_path"),
            migration.get("rollback_doc"),
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "phase_gate": {"gate": "G-W3", "status": "PASS" if code == 0 else "FAIL"},
    }
    RECEIPT_W3.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": code == 0, "status": migration.get("status"), "receipt": str(RECEIPT_JSON)}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
