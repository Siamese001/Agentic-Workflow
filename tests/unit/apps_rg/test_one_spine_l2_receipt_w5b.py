"""Wave 5B: section L2 spine receipts after PA (all product-visible lanes)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.spine.c0_fec_compose import FEC_BRIDGE_ARTIFACT, wire_spine_c0_fec_for_section
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.section_l2_lane_integration import (
    finalize_section_l2_after_output,
    prepare_section_l2_before_provider,
)
from apps_rg.runtime.section_l2_spine_receipt import (
    L2_EXECUTION_PACKET_ARTIFACT,
    L2_SPINE_RECEIPT_ARTIFACT,
    SEALED_L2_ARTIFACT,
    SectionL2SpinePreconditionError,
    assert_section_l2_spine_preconditions,
    build_l2_execution_packet_for_section,
    l2_spine_kill_switch_enabled,
)
from tests.unit.apps_rg.test_one_spine_fec_bridge_w5a import W5A_SECTIONS, _args, _minimal_pool

REPO = Path(__file__).resolve().parents[3]


def _write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


@pytest.mark.parametrize("section_id", W5A_SECTIONS)
def test_l2_execution_packet_contract_shape(section_id: str):
    payload = {
        "run_id": "run_test",
        "compiled_prompt_artifact_ref": "compiled_prompt_artifact.json",
        "fec_bridge_ref": FEC_BRIDGE_ARTIFACT,
        "section_fec_bridge": {"fec_bridge_mode": "section_fec_bridge", "route_contract_ref": "route_contract.json"},
        "evidence_contract_consumed": True,
    }
    pkt = build_l2_execution_packet_for_section(
        section_id=section_id,
        runtime_payload=payload,
        provider_lane="qwen_vllm",
        model_lane="test-model",
    )
    assert pkt["contract_type"] == "L2ExecutionPacket"
    assert pkt["producer_stage"] in ("PA", "section_runtime_adapter")
    assert pkt["consumer_stage"] == "L2"
    assert pkt["route_contract_ref"] == "route_contract.json"
    assert pkt["fec_bridge_ref"] == FEC_BRIDGE_ARTIFACT
    assert pkt["compiled_prompt_artifact_ref"] == "compiled_prompt_artifact.json"
    assert pkt["execution_lane"] == section_id
    assert pkt["direct_l4_write_allowed"] is False
    assert pkt["product_certification"] == "NOT_CLAIMED"


def test_product_visible_blocked_without_compiled_and_fec(tmp_path: Path):
    payload: dict = {"product_visible": True}
    with pytest.raises(SectionL2SpinePreconditionError, match="compiled_prompt"):
        assert_section_l2_spine_preconditions(payload, tmp_path)
    _write_json(tmp_path / "compiled_prompt_artifact.json", {"template_id": "t"})
    with pytest.raises(SectionL2SpinePreconditionError, match="FEC"):
        assert_section_l2_spine_preconditions(payload, tmp_path)


def test_l2_bypass_flag_blocked(tmp_path: Path):
    _write_json(tmp_path / "compiled_prompt_artifact.json", {"template_id": "t"})
    _write_json(tmp_path / FEC_BRIDGE_ARTIFACT, {"fec_bridge_mode": "section_fec_bridge"})
    payload = {"product_visible": True, "l2_bypass_without_packet": True}
    with pytest.raises(SectionL2SpinePreconditionError, match="L2ExecutionPacket"):
        assert_section_l2_spine_preconditions(payload, tmp_path)


def test_fixture_bypass_skips_l2_preconditions(tmp_path: Path):
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        assert_section_l2_spine_preconditions({"product_visible": True}, tmp_path)
    finally:
        deactivate_fixture_dev_bypass()


@pytest.mark.parametrize("section_id", ("headline", "competencies"))
def test_prepare_finalize_emits_l2_artifacts(tmp_path: Path, section_id: str):
    spine = build_section_front_spine_from_args(
        section_id=section_id,
        args=_args(),
        repo_root=REPO,
    )
    pool = _minimal_pool(section_id)
    payload: dict = {"allowed_fact_ids": list(pool.allowed_fact_ids_ordered), "run_id": "w5b_unit"}
    wire_spine_c0_fec_for_section(
        artifact_dir=tmp_path,
        section_id=section_id,
        front_spine=spine,
        pool=pool,
        runtime_payload=payload,
    )
    _write_json(
        tmp_path / "compiled_prompt_artifact.json",
        {
            "evidence_contract_consumed": True,
            "fec_bridge_mode": "section_fec_bridge",
            "raw_proof_pool_direct_to_pa": False,
        },
    )
    prepare_section_l2_before_provider(
        tmp_path,
        section_id,
        payload,
        provider_lane="qwen_vllm",
    )
    assert (tmp_path / L2_EXECUTION_PACKET_ARTIFACT).is_file()
    pkt = json.loads((tmp_path / L2_EXECUTION_PACKET_ARTIFACT).read_text(encoding="utf-8"))
    assert pkt["route_contract_ref"] == "route_contract.json"
    _write_json(tmp_path / "provider_request.json", {"model": "m"})
    _write_json(tmp_path / "provider_response.json", {"content": "x"})
    _write_json(tmp_path / "l2_output.json", {"section_id": section_id})
    _write_json(tmp_path / "x2_gate_outputs.json", [])
    _write_json(tmp_path / "x3_disposition.json", {"x3_code": "ALLOW"})
    finalize_section_l2_after_output(tmp_path, section_id, payload)
    sealed = json.loads((tmp_path / SEALED_L2_ARTIFACT).read_text(encoding="utf-8"))
    assert sealed["contract_type"] == "SealedL2Artifact"
    assert sealed["l2_execution_packet_ref"] == L2_EXECUTION_PACKET_ARTIFACT
    assert sealed["durable_commit_occurred"] is False
    assert sealed["canonical_exit_claimed"] is False
    assert sealed["product_certification"] == "NOT_CLAIMED"
    receipt = json.loads((tmp_path / L2_SPINE_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
    assert receipt["l2_alignment_mode"] == "section_l2_spine_receipt"
    assert receipt["spine_mode"] == "section_lane_modular"
    assert receipt["runtime_exhaust_bundle_claimed"] is False


def test_kill_switch_enabled_by_default():
    assert l2_spine_kill_switch_enabled() is True
