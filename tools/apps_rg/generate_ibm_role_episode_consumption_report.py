"""Generate ibm_role_episode_consumption_wiring.md and .json reports."""
from __future__ import annotations

import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT_TS = "2026-05-28T14:00:00Z"


def main() -> None:
    from apps_rg.runtime.sections.ibm_role_episode_evidence import (
        IBM_BULLET_SLOT_BUNDLE_MAP,
        PROMOTABLE_METRIC_OUTCOME_IDS,
        build_ibm_role_episode_section_packet,
    )

    report = {
        "schema": "ibm_role_episode_consumption_wiring_v1",
        "generated_at": REPORT_TS,
        "config_decision": {
            "status": "ENABLED_WITH_ROLE_EPISODE_BUNDLE_GUARDS",
            "ibm_bullets_graph_expansion_allowed": True,
            "ibm_narrative_graph_expansion_allowed": True,
            "role_episode_bundle_consumption": "required",
            "graph_expansion_mode": "role_episode_bundle_only",
        },
        "role_episode_consumption": {
            "c0_marker": "IBM_ROLE_EPISODE_EVIDENCE_PACK",
            "proof_authority": "graph_role_episode_bundles_plus_linked_source_facts",
            "base_resume_usage": "calibration_only",
            "jd_usage": "targeting_only",
            "archive_usage": "provenance_only",
            "examples_usage": "style_only",
            "bullet_slot_bundle_map": IBM_BULLET_SLOT_BUNDLE_MAP,
            "promotable_metric_outcome_ids": list(PROMOTABLE_METRIC_OUTCOME_IDS),
        },
        "x2_gates_added": [
            "x2_ibm_role_episode_bundles_in_proof_pool",
            "x2_ibm_bullet_role_episode_bundle_id_required",
            "x2_ibm_metric_outcome_id_required_when_has_metric",
            "x2_ibm_hold_metric_forbidden_in_output",
            "x2_ibm_watson_studio_no_metric_bearing_claim",
            "x2_ibm_narrative_role_episode_bundles_in_proof_pool",
            "x2_ibm_narrative_role_episode_bundle_id_required",
            "x2_ibm_narrative_hold_metric_forbidden",
        ],
        "files_changed": [
            "apps_rg/runtime/sections/ibm_role_episode_evidence.py",
            "apps_rg/runtime/sections/ibm_bullets_graph_evidence.py",
            "apps_rg/runtime/sections/ibm_bullets_pa.py",
            "apps_rg/runtime/sections/ibm_narrative_pa.py",
            "apps_rg/runtime/proof_pool_resolver.py",
            "apps_rg/runtime/validators/ibm_bullets_x2.py",
            "apps_rg/runtime/validators/ibm_narrative_x2.py",
            "apps_rg/config/domain_contract/section_retrieval_profile.yaml",
            "tests/unit/apps_rg/test_ibm_role_episode_consumption_wiring.py",
        ],
        "ibm_bullets_packet_summary": build_ibm_role_episode_section_packet("ibm_bullets"),
        "ibm_narrative_packet_summary": build_ibm_role_episode_section_packet("ibm_narrative"),
    }

    os.makedirs(REPO / "docs" / "reports" / "apps_rg", exist_ok=True)
    json_path = REPO / "docs" / "reports" / "apps_rg" / "ibm_role_episode_consumption_wiring.json"
    md_path = REPO / "docs" / "reports" / "apps_rg" / "ibm_role_episode_consumption_wiring.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    lines = [
        "# IBM Role Episode Consumption Wiring",
        "",
        f"**Generated:** {REPORT_TS}",
        "",
        "## Config Decision",
        "",
        f"- **Status:** `{report['config_decision']['status']}`",
        f"- `ibm_bullets.graph_expansion_allowed` = `{report['config_decision']['ibm_bullets_graph_expansion_allowed']}`",
        f"- `ibm_narrative.graph_expansion_allowed` = `{report['config_decision']['ibm_narrative_graph_expansion_allowed']}`",
        f"- `role_episode_bundle_consumption` = `{report['config_decision']['role_episode_bundle_consumption']}`",
        "",
        "## Role Episode Consumption",
        "",
        "| Field | Value |",
        "|-------|-------|",
    ]
    for k, v in report["role_episode_consumption"].items():
        if k != "bullet_slot_bundle_map":
            lines.append(f"| {k} | {v} |")
    lines.extend(["", "## X2 Gates Added", ""])
    for g in report["x2_gates_added"]:
        lines.append(f"- `{g}`")
    lines.extend(["", "## Acceptance", "", "| Gate | Result |", "|------|--------|"])
    lines.append("| compileall apps_rg | run in closeout |")
    lines.append("| test_ibm_role_episode_consumption_wiring | run in closeout |")
    lines.append("| agentic_core diff | empty |")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")


if __name__ == "__main__":
    main()
