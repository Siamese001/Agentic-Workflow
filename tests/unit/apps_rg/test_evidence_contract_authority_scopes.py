"""Authority-scope guards for apps_rg evidence-contract bridge artifacts."""

from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from unittest.mock import patch

import pytest


def test_c0_fec_bridge_declares_shape_only_scope_and_rejects_canonical_claim() -> None:
    from apps_rg.runtime.spine.c0_fec_compose import (
        FEC_BRIDGE_AUTHORITY_SCOPE,
        SectionFecBridgePreconditionError,
        assert_section_pa_fec_preconditions,
        pa_consumption_receipt_fields,
    )

    bridge = {
        "contract_type": "FinalEvidenceContractBridge",
        "fec_bridge_mode": "spine_c0_fec_compose",
        "route_contract_ref": "route_contract.json",
        "authority_scope": FEC_BRIDGE_AUTHORITY_SCOPE,
        "final_evidence_contract_authoritative": False,
        "canonical_c0_5_claimed": False,
    }
    runtime_payload = {"section_fec_bridge": bridge, "product_visible": True}

    assert_section_pa_fec_preconditions(runtime_payload)
    receipt = pa_consumption_receipt_fields(runtime_payload)
    assert receipt["fec_authority_scope"] == FEC_BRIDGE_AUTHORITY_SCOPE
    assert receipt["final_evidence_contract_authoritative"] is False

    bridge["canonical_c0_5_claimed"] = True
    with pytest.raises(SectionFecBridgePreconditionError, match="canonical_c0_5"):
        assert_section_pa_fec_preconditions(runtime_payload)


def test_section_x3_mirror_declares_non_core_exit_authority(tmp_path: Path) -> None:
    from apps_rg.runtime.spine.section_x3_finalize import (
        CORE_EXIT_AUTHORITY_SCOPE,
        LANE_X3_MIRROR_AUTHORITY_SCOPE,
        persist_section_x3_mirror,
    )

    doc = persist_section_x3_mirror(tmp_path, {"x3_code": "X3D", "pass": True})

    assert doc["authority_scope"] == LANE_X3_MIRROR_AUTHORITY_SCOPE
    assert doc["section_x3_mirror_only"] is True
    assert doc["core_exit_authority_scope"] == CORE_EXIT_AUTHORITY_SCOPE
    persisted = json.loads((tmp_path / "x3_disposition.json").read_text(encoding="utf-8"))
    assert persisted["authority_scope"] == LANE_X3_MIRROR_AUTHORITY_SCOPE


def test_exit_artifacts_scope_x1_x2_and_canonical_exit(tmp_path: Path) -> None:
    from apps_rg.runtime.spine import exit_artifacts as subject

    (tmp_path / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "g1", "pass": True}]}),
        encoding="utf-8",
    )
    (tmp_path / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3D", "pass": True}),
        encoding="utf-8",
    )

    x1 = subject.build_section_exit_x1_result(section_id="headline", artifact_dir=tmp_path)
    x2 = subject.build_section_exit_x2_result(section_id="headline", artifact_dir=tmp_path)
    edr = subject.build_exit_disposition_receipt_for_section(
        section_id="headline",
        runtime_payload={"run_id": "run-1"},
        artifact_dir=tmp_path,
    )

    assert x1["authority_scope"] == "apps_rg_x1d_judge_preflight_not_core_x1_gate"
    assert x2["authority_scope"] == subject.APP_X2_QUALITY_AUTHORITY_SCOPE
    assert x2["core_x2_matrix_authority"] is False
    assert edr["canonical_exit_authority_scope"] == subject.CORE_EXIT_AUTHORITY_SCOPE
    assert edr["section_x3_authority_scope"] == subject.LANE_X3_MIRROR_AUTHORITY_SCOPE


def test_prompt_assembly_projection_names_are_canonical_with_legacy_aliases() -> None:
    from agentic_core.prompt_governance.prompt_assembly import input_contracts as ic

    assert ic.L1PlanContract is ic.PAL1PlanProjection
    assert ic.L0RouteContract is ic.PAL0RouteProjection
    assert ic.C0EvidenceContract is ic.PAC0EvidenceProjection

    bundle = ic.upstream_bundle_from_dicts(
        plan_contract={"plan_id": "p", "l5_certification_ref": "cert"},
        route_contract={"route_id": "r", "l5_certification_ref": "cert"},
        evidence_contract={"status": "PASS"},
    )
    assert isinstance(bundle.plan, ic.PAL1PlanProjection)
    assert isinstance(bundle.route, ic.PAL0RouteProjection)
    assert isinstance(bundle.evidence, ic.PAC0EvidenceProjection)


def test_l2_envelope_receipts_are_not_canonical_sealed_l2_authority() -> None:
    from apps_rg.runtime.bindings import l2_envelope_contracts as c

    names = {f.name for f in fields(c.AttemptReceipt)}
    assert "authority_scope" in names
    assert "canonical_l2_artifact_authority" in names

    det = c.DeterminismBundle(
        blueprint_hash="b",
        policy_hash="p",
        prompt_hash="h",
        input_hash="i",
        replay_key="rk",
        attempt_seed="seed",
    )
    lineage = c.LineageRoot(parent_route_id="route", parent_plan_id="plan", parent_step_id=None)
    receipt = c.AttemptReceipt(
        attempt_receipt_id="attempt",
        validation_packet_id="validation",
        attempt_count=1,
        determinism=det,
        lineage=lineage,
        trace_id="trace",
        span_id="span",
        latency_ms=0.0,
        tokens_used=0,
        return_code=0,
        result_class=c.ResultClass.SUCCESS,
    )
    assert receipt.authority_scope == c.L2_ENVELOPE_AUTHORITY_SCOPE
    assert receipt.canonical_l2_artifact_authority is False


def test_x1d_preflight_and_l6_shadow_are_advisory_scoped(tmp_path: Path) -> None:
    from apps_rg.runtime.shadow.l6_handoff_packet import (
        L6_LEGACY_HANDOFF_AUTHORITY_SCOPE,
        build_l6_shadow_handoff_dict,
    )
    from apps_rg.runtime.shadow.l6_shadow_learning import (
        L6_LEARNING_AUTHORITY_SCOPE,
        build_l6_shadow_learning_record,
    )
    from apps_rg.runtime.x1d_judge_policy import (
        X1D_JUDGE_PREFLIGHT_AUTHORITY_SCOPE,
        preflight_x1d_judge_policy,
    )

    preflight = preflight_x1d_judge_policy(environ={}, configured_judge_csv="gemini_pro")
    assert preflight["authority_scope"] == X1D_JUDGE_PREFLIGHT_AUTHORITY_SCOPE
    assert preflight["core_x1_gate_authority"] is False

    (tmp_path / "l2_output.json").write_text(
        json.dumps({"run_id": "run-1", "runtime_generation_status": "DONE"}),
        encoding="utf-8",
    )
    (tmp_path / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3D", "pass": True}),
        encoding="utf-8",
    )
    (tmp_path / "x2_gate_outputs.json").write_text(json.dumps({"gates": []}), encoding="utf-8")
    (tmp_path / "x1d_llm_judge_outputs.json").write_text(json.dumps({"judges": []}), encoding="utf-8")

    with patch.dict("os.environ", {"APPS_RG_GOVERNED_L6_SHADOW_SKIP": "1"}):
        handoff = build_l6_shadow_handoff_dict(
            artifact_dir=tmp_path,
            repo_root=tmp_path,
            section_id="headline",
            prompt_id="prompt",
            temperature=None,
            max_tokens=None,
        )
    assert handoff["authority_scope"] == L6_LEGACY_HANDOFF_AUTHORITY_SCOPE
    assert handoff["legacy_shadow_summary_only"] is True
    assert handoff["future_run_only"] is True

    learning = build_l6_shadow_learning_record(
        artifact_dir=tmp_path,
        repo_root=tmp_path,
        section_id="headline",
        lane_key="headline",
    )
    assert learning["authority_scope"] == L6_LEARNING_AUTHORITY_SCOPE
    assert learning["future_run_only"] is True
