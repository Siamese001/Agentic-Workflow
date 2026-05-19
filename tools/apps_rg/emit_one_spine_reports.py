#!/usr/bin/env python3
"""Emit one-spine Wave 1 inventory + Wave 2 guardrail closeout reports."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from apps_rg.runtime.one_spine_inventory import build_one_spine_section_path_inventory  # noqa: E402
from apps_rg.runtime.section_spine_terminology import (  # noqa: E402
    EXPLICIT_NON_CLAIMS,
    section_lane_spine_classification,
)

OUT_DIR = REPO / "docs/reports/apps_rg"

CLOSEOUT_EXPLICIT_NON_CLAIMS: tuple[str, ...] = (
    *EXPLICIT_NON_CLAIMS,
    "no claim that all apps_rg contract tests pass",
    "no claim of full canonical product certification",
    "no claim that pre-existing contract failures were resolved",
    "no claim that the section CLI is fully migrated into canonical C0/PA/L2/Exit unless the canonical contract chain is emitted",
)

CONTRACT_SUITE_FOLLOWUP_GAP = (
    "Broad tests/_apps_contract suite needs bounded follow-up triage: full run aborted "
    "~22 minutes at ~48% with no final summary and many F markers (non-dispositive)."
)


def _suite_status() -> dict[str, str]:
    return {
        "ONE_SPINE_TARGETED_TESTS": "PASS",
        "UNIT_GUARDRAILS": "PASS",
        "FULL_APPS_CONTRACT_SUITE": "INCOMPLETE_ABORTED",
        "PRODUCT_CERTIFICATION": "NOT_CLAIMED",
    }


def _accepted_evidence() -> dict[str, Any]:
    return {
        "one_spine_contract_tests": "tests/_apps_contract/test_one_spine_section_path_contracts.py — 5/5 PASS (run separately)",
        "unit_guardrail_tests": "tests/unit/apps_rg/test_one_spine_section_guardrails.py — 7/7 PASS (run separately)",
        "combined_targeted_run": "12/12 PASS when run together",
        "full_apps_contract_suite": (
            "Attempted; aborted ~22 min at ~48% with visible F markers and no final summary — "
            "documented as incomplete; non-dispositive for product certification"
        ),
        "full_unit_apps_rg_suite": (
            "Attempted separately: 642 passed / 20 failed / 6 skipped — failures outside one-spine scope; "
            "not used as wave PASS gate"
        ),
        "targeted_proof_scope": (
            "One-spine kill-switch / guardrail tests are green and stand as targeted proof for this wave only"
        ),
    }


def _inventory_md(inv: dict) -> str:
    lines = [
        "# One-spine section path inventory (Wave 1)",
        "",
        f"Generated: {inv['generated_at_utc']}",
        "",
        "## Summary",
        "",
        f"- **TWO_PATHS_FOUND:** {inv['two_paths_found']}",
        f"- **CANONICAL_SPINE_TARGET:** {' → '.join(inv['canonical_spine_target'])}",
        "",
        "## Path A — Section CLI (`python -m apps_rg --section <lane>`)",
        "",
        f"- Entry: `{inv['path_a_section_cli']['entry']}`",
        f"- Dispatch: `{inv['path_a_section_cli']['dispatch']}`",
        f"- Exemplar: `{inv['path_a_section_cli']['exemplar_module']}`",
        f"- Observed chain: {' → '.join(inv['path_a_section_cli']['observed_chain'])}",
        "",
        "## Path B — Integrated R4 spine (no `--section`)",
        "",
        f"- Dispatch: `{inv['path_b_canonical_r4']['dispatch']}`",
        f"- C0/PA: `{inv['path_b_canonical_r4']['c0_pa_wiring']}`",
        "",
        "## Contract bypass matrix",
        "",
        "| Contract | Section emits canonical | Substitute | R4 emits |",
        "|----------|-------------------------|------------|----------|",
    ]
    for row in inv["contract_bypass_matrix"]:
        lines.append(
            f"| {row['contract_type']} | {row['section_cli_emits_canonical']} | "
            f"{row['section_cli_substitute']} | {row['canonical_r4_emits']} |"
        )
    lines.extend(["", "## Misnamed C0 artifacts", ""])
    for m in inv["misnamed_c0_artifacts"]:
        lines.append(
            f"- **{m['path']}**: `{m['current_name']}` → `{m['recommended_name']}` "
            f"(changed_now={m.get('changed_now')}) — {m.get('reason', '')}"
        )
    lines.extend(["", "## Explicit non-claims", ""])
    for c in inv["explicit_non_claims"]:
        lines.append(f"- {c}")
    lines.extend(["", "## Open gaps", ""])
    for g in inv["open_gaps"]:
        lines.append(f"- {g}")
    lines.append("")
    return "\n".join(lines)


def _closeout(inv: dict) -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    open_gaps = list(inv["open_gaps"])
    if CONTRACT_SUITE_FOLLOWUP_GAP not in open_gaps:
        open_gaps.append(CONTRACT_SUITE_FOLLOWUP_GAP)
    return {
        "schema_version": "one_spine_guardrail_closeout_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "waves_completed": ["1", "2"],
        "status": "PARTIAL",
        "status_note": (
            "PARTIAL — not PASS. Wave 1-2 inventory, guardrails, and targeted one-spine tests pass. "
            "Full tests/_apps_contract certification is NOT claimed: broad run aborted with no final "
            "summary (non-dispositive). Product certification NOT_CLAIMED."
        ),
        "suite_status": _suite_status(),
        "accepted_evidence": _accepted_evidence(),
        "two_paths_found": inv["two_paths_found"],
        "canonical_spine_target": inv["canonical_spine_target"],
        "section_cli_status": inv["section_cli_status"],
        "guardrails_added": [
            "apps_rg/runtime/section_spine_terminology.py",
            "apps_rg/runtime/one_spine_inventory.py",
            "c03_graphrag_bound enrich_section_graph_binding_doc metadata",
            "executive_summary_proof_bundle spine_classification",
            "input_authority_prompt_block truthful graph substrate line",
            "tests/unit/apps_rg/test_one_spine_section_guardrails.py",
            "tests/_apps_contract/test_one_spine_section_path_contracts.py",
        ],
        "renames_or_aliases": inv["misnamed_c0_artifacts"],
        "explicit_non_claims": list(CLOSEOUT_EXPLICIT_NON_CLAIMS),
        "open_gaps": open_gaps,
        "forbidden_files_touched": {"agentic_core": False, "explanation": "apps_rg-local only"},
        "tests_added_or_updated": [
            "tests/unit/apps_rg/test_one_spine_section_guardrails.py",
            "tests/_apps_contract/test_one_spine_section_path_contracts.py",
        ],
        "spine_classification_sample": section_lane_spine_classification(),
    }


def _closeout_md(co: dict) -> str:
    lines = [
        "# One-spine guardrail closeout (Wave 2)",
        "",
        f"Generated: {co['generated_at_utc']}",
        f"**STATUS: {co['status']}** (not PASS)",
        "",
        co.get("status_note", ""),
        "",
        "## Suite status",
        "",
        "| Gate | Status |",
        "|------|--------|",
    ]
    for gate, status in co.get("suite_status", {}).items():
        lines.append(f"| {gate} | {status} |")
    lines.extend(["", "## Accepted evidence (this wave only)", ""])
    for key, val in co.get("accepted_evidence", {}).items():
        lines.append(f"- **{key}:** {val}")
    lines.extend(["", "## Guardrails added", ""])
    for g in co["guardrails_added"]:
        lines.append(f"- `{g}`")
    lines.extend(["", "## Renames / aliases", ""])
    for m in co["renames_or_aliases"]:
        lines.append(f"- {m['path']}: {m['current_name']} → {m['recommended_name']}")
    lines.extend(["", "## Explicit non-claims", ""])
    for c in co.get("explicit_non_claims", []):
        lines.append(f"- {c}")
    lines.extend(["", "## Open gaps", ""])
    for g in co["open_gaps"]:
        lines.append(f"- {g}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inv = build_one_spine_section_path_inventory()
    co = _closeout(inv)
    (OUT_DIR / "one_spine_section_path_inventory.json").write_text(
        json.dumps(inv, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "one_spine_section_path_inventory.md").write_text(
        _inventory_md(inv),
        encoding="utf-8",
    )
    (OUT_DIR / "one_spine_guardrail_closeout.json").write_text(
        json.dumps(co, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "one_spine_guardrail_closeout.md").write_text(
        _closeout_md(co),
        encoding="utf-8",
    )
    print(f"Wrote reports under {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
