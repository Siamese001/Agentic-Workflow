"""Contract: every generated lane emits consumable c0_metrics via FEC bridge wire."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.bindings.section_lane_c0_metrics import (
    C0_METRICS_FILENAME,
    CANONICAL_C0_METRICS_SUPPORT_STATUSES,
    build_section_c0_metrics_x2_gates,
    load_section_lane_c0_metrics,
    validate_c0_metrics_document,
)
from apps_rg.runtime.bindings.c0_metrics_writer import SCHEMA_VERSION
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.spine.c0_fec_compose import wire_spine_c0_fec_for_section
from apps_rg.runtime.spine.front_contracts import build_section_front_spine_from_args
from apps_rg.runtime.proof_pool_resolver import SectionProofPool

REPO = Path(__file__).resolve().parents[2]


def _args() -> SimpleNamespace:
    return SimpleNamespace(
        target_company="Acme Corp",
        target_title="VP Engineering",
        target_role="VP Engineering",
        jd_text="Lead platform engineering and agentic systems.",
        briefing="Emphasize regulated delivery.",
        base_resume_ref="",
    )


def _minimal_pool(section: str) -> SectionProofPool:
    fid = f"bul_{section}_001"
    return SectionProofPool(
        section=section,
        proof_source="augmented_skills_graph",
        proof_pool_ref="apps_rg/fixtures/graph.json",
        proof_pool_digest="digest",
        selected_fact_plan={"facts": [{"fact_id": fid, "claim_text": "Built platform."}]},
        allowed_fact_ids_ordered=[fid],
        allowed_fact_ids={fid},
        bullet_rows=[],
        proof_pool_metadata={
            "proof_pool_type": "augmented_skills_graph",
            "augmented_skills_graph_present": True,
            "graph_ref": "apps_rg/fixtures/graph.json",
            "graph_version": "v1",
            "c03_graphrag_bound": {
                "support_status": "SUPPORTED",
                "graph_lineage_refs": ["ref:graph:version:v1"],
                "final_evidence_contract_snapshot": {
                    "evidence_items": [{"evidence_id": f"evidence:graph:{fid}"}],
                    "support_status": "SUPPORTED",
                    "support_target_met": True,
                },
            },
        },
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="base.json",
        base_resume_json_hash="hash",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )


@pytest.mark.parametrize("section_id", GENERATED_LANES)
def test_wire_section_fec_bridge_emits_c0_metrics_all_lanes(
    tmp_path: Path,
    section_id: str,
) -> None:
    lane_dir = tmp_path / section_id
    lane_dir.mkdir()
    spine = build_section_front_spine_from_args(
        section_id=section_id,
        args=_args(),
        repo_root=REPO,
    )
    pool = _minimal_pool(section_id)
    payload: dict = {"run_id": f"wire_{section_id}", "section_id": section_id}
    wire_spine_c0_fec_for_section(
        artifact_dir=lane_dir,
        section_id=section_id,
        front_spine=spine,
        pool=pool,
        runtime_payload=payload,
    )
    metrics_path = lane_dir / C0_METRICS_FILENAME
    assert metrics_path.is_file(), f"{section_id}: missing {C0_METRICS_FILENAME}"
    metrics = load_section_lane_c0_metrics(lane_dir)
    assert metrics is not None
    ok, reason = validate_c0_metrics_document(metrics)
    assert ok, f"{section_id}: {reason}"
    assert metrics["schema_version"] == SCHEMA_VERSION
    assert metrics["support_status"] in CANONICAL_C0_METRICS_SUPPORT_STATUSES
    assert payload.get("c0_metrics_ref") == C0_METRICS_FILENAME
    assert "support_status" in payload
    assert "support_target_met" in payload

    gates = build_section_c0_metrics_x2_gates(metrics, section_id=section_id)
    assert len(gates) == 2
    assert all(g["pass"] for g in gates), [g for g in gates if not g["pass"]]
