#!/usr/bin/env python3
"""W11-M2.2 / M3 / M4 — patch fan-in matrix classifications (planning only)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MATRIX = REPO / "docs/reports/agent_inventory/w11_candidate_fanin_matrix.json"

PATCHES: dict[str, dict] = {
    "validation_orchestrator": {
        "proposed_final_classification": "ARCHIVE_CANDIDATE_AFTER_30D",
        "active_path_confidence": "LOW",
        "migration_required": True,
        "delete_readiness": "NO",
        "archive_readiness": "NO",
        "blocker": (
            "ADG import fan-in 0; E2 SSOT=l2_phase_pipeline; "
            "remove CI hollow/harness baselines after 30d quarantine"
        ),
        "w11_m22_note": (
            "No Python runtime importers; CI baselines + mirror_discovery are quarantine evidence"
        ),
    },
    "rg_reasoning_agents": {
        "proposed_final_classification": "QUARANTINE_30D",
        "active_path_confidence": "LOW",
        "migration_required": True,
        "delete_readiness": "NO",
        "archive_readiness": "NO",
        "blocker": (
            "11 test files + apps_shared rg_orchestrator_facade; "
            "zero product-path imports under apps_rg/runtime/sections or canonical_dispatch"
        ),
        "w11_m3_note": (
            "ADG import fan-in 0 all Rg* modules; migrate tests/facades before archive"
        ),
        "w11_m3_migration_targets": [
            "python -m apps_rg -> canonical_dispatch -> section lanes",
            "tests: retire or rewrite tests/unit/apps_rg/reasoning/* to lane harness",
            "facades: apps_shared/adapters/rg_orchestrator_facade.py (eval-only)",
        ],
    },
    "deprecated_dispatch_clis": {
        "proposed_final_classification": "QUARANTINE_30D",
        "active_path_confidence": "MEDIUM",
        "migration_required": True,
        "delete_readiness": "NO",
        "archive_readiness": "NO",
        "blocker": (
            "section lanes import dispatch PA/helper modules; "
            "retired python -m dispatch CLIs exit 2 — not product proof"
        ),
        "w11_m4_note": (
            "8 *_dispatch.py files; lanes are canonical product path; "
            "archive only helper extraction to sections/ complete"
        ),
    },
    "dry_run_dir": {
        "proposed_final_classification": "QUARANTINE_30D",
        "active_path_confidence": "LOW",
        "migration_required": True,
        "delete_readiness": "NO",
        "archive_readiness": "NO",
        "blocker": "contract tests + validate_exec_summary_graph_only_generation import",
        "w11_m4_note": "Not product proof; test_exec_summary_dry_run.py",
    },
    "orchestrate_full_resume": {
        "proposed_final_classification": "KEEP_TEST_SUPPORT_ONLY",
        "active_path_confidence": "MEDIUM",
        "migration_required": True,
        "delete_readiness": "NO",
        "archive_readiness": "NO",
        "blocker": (
            "KEEP_ROLLBACK_ONLY via APPS_RG_R4 legacy_full_resume; "
            "e2e tests; preflight references — not canonical W8 chain"
        ),
        "w11_m4_note": "Canonical product = __main__ -> apps_rg_dispatch -> canonical_dispatch",
    },
}


def main() -> None:
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    for cand in data["candidates"]:
        cid = cand["id"]
        if cid not in PATCHES:
            continue
        patch = PATCHES[cid]
        cand.update(patch)
    data["w11_m222_m3_m4"] = "2026-05-19"
    data["summary"]["archive_ready_count"] = sum(
        1 for c in data["candidates"] if c.get("archive_readiness") in ("YES", "DONE")
    )
    data["summary"]["migration_required_count"] = sum(
        1 for c in data["candidates"] if c.get("migration_required")
    )
    data["summary"]["blocked_count"] = sum(1 for c in data["candidates"] if c.get("blocker"))
    MATRIX.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps({k: PATCHES[k]["proposed_final_classification"] for k in PATCHES}, indent=2))


if __name__ == "__main__":
    main()
