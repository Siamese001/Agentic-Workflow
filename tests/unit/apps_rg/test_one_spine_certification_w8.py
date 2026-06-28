"""Wave 8: one-spine certification and proof eligibility receipts."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
)
from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2
from apps_rg.runtime.spine.c0_fec_compose import (
    build_spine_c0_fec_artifact,
    emit_spine_c0_fec_artifacts,
)
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
    emit_section_front_spine_receipts,
)
from apps_rg.runtime.section_l2_lane_integration import (
    finalize_section_l2_after_output,
    prepare_section_l2_before_provider,
)
from apps_rg.runtime.section_one_spine_certification import (
    ONE_SPINE_CERTIFICATION_RECEIPT_ARTIFACT,
    PRODUCT_CERTIFICATION_RECEIPT_ARTIFACT,
    PROOF_ELIGIBILITY_RECEIPT_ARTIFACT,
    SectionOneSpineCertificationPreconditionError,
    assert_certification_preconditions,
    emit_section_one_spine_certification_artifacts,
    inspect_one_spine_chain,
)
from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
    finalize_section_runtime_exhaust_before_l6,
)
from tests.unit.apps_rg.test_one_spine_fec_bridge_w5a import W5A_SECTIONS, _args, _minimal_pool

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def _mock_spine_c0_retrieve(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake(**_: object) -> FinalEvidenceContract:
        return FinalEvidenceContract(
            request_id="req-w8",
            run_id="run-w8",
            app_id="apps_rg",
            trace_id="trace-w8",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="d" * 64,
            evidence_items=(
                EvidenceItem(
                    source="fact:bul_001",
                    content="Harness chain proof.",
                    source_type="proof_pool",
                ),
            ),
        )

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        _fake,
    )


def _write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _minimal_chain(tmp_path: Path, section_id: str) -> dict:
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        spine = build_section_front_spine_from_args(
            section_id=section_id, args=_args(), repo_root=REPO
        )
        pool = _minimal_pool(section_id)
        payload: dict = {
            "allowed_fact_ids": list(pool.allowed_fact_ids_ordered),
            "run_id": "w8",
            "product_visible": True,
            "artifact_dir": str(tmp_path),
        }
        emit_section_front_spine_receipts(tmp_path, spine)
        bridge = build_spine_c0_fec_artifact(
            section_id=section_id,
            front_spine=spine,
            pool=pool,
        )
        emit_spine_c0_fec_artifacts(tmp_path, bridge)
        payload["section_fec_bridge"] = bridge.bridge_doc
        payload["_section_front_spine"] = spine
    finally:
        deactivate_fixture_dev_bypass()
    _write_json(
        tmp_path / "compiled_prompt_artifact.json",
        {
            "evidence_contract_consumed": True,
            "fec_bridge_mode": "section_fec_bridge",
            "raw_proof_pool_direct_to_pa": False,
        },
    )
    prepare_section_l2_before_provider(tmp_path, section_id, payload, provider_lane="retired_provider_profile")
    _write_json(tmp_path / "provider_request.json", {})
    _write_json(tmp_path / "provider_response.json", {})
    _write_json(tmp_path / "l2_output.json", {})
    _write_json(tmp_path / "x2_gate_outputs.json", [{"gate_id": "g1", "pass": True}])
    _write_json(tmp_path / "x3_disposition.json", {"x3_code": "X3_BLOCK", "pass": False})
    finalize_section_l2_after_output(tmp_path, section_id, payload)
    finalize_section_exit_after_l2(tmp_path, section_id, payload)
    finalize_section_runtime_exhaust_before_l6(tmp_path, section_id, payload, repo_root=REPO)
    return payload


@pytest.mark.parametrize("section_id", W5A_SECTIONS)
def test_inspect_chain_complete_after_full_run(section_id: str, tmp_path: Path):
    _minimal_chain(tmp_path, section_id)
    chain = inspect_one_spine_chain(tmp_path)
    assert chain["all_required_artifacts_present"] is True
    assert chain["required_chain_complete"] is True


def test_missing_artifact_blocks_chain_complete(tmp_path: Path):
    _minimal_chain(tmp_path, "headline")
    (tmp_path / "exit_disposition_receipt.json").unlink()
    chain = inspect_one_spine_chain(tmp_path)
    assert chain["required_chain_complete"] is False


def test_certification_emits_three_receipts(tmp_path: Path):
    payload = _minimal_chain(tmp_path, "headline")
    proof_bundle = {
        "proof_eligible": True,
        "test_only_mock_provider": False,
        "test_only_mock_judges": False,
    }
    emit_section_one_spine_certification_artifacts(
        tmp_path,
        section_id="headline",
        runtime_payload=payload,
        proof_bundle=proof_bundle,
        runtime_generation_status="REAL_LLM",
    )
    assert (tmp_path / ONE_SPINE_CERTIFICATION_RECEIPT_ARTIFACT).is_file()
    assert (tmp_path / PROOF_ELIGIBILITY_RECEIPT_ARTIFACT).is_file()
    assert (tmp_path / PRODUCT_CERTIFICATION_RECEIPT_ARTIFACT).is_file()
    cert = json.loads((tmp_path / ONE_SPINE_CERTIFICATION_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
    assert cert["required_chain_complete"] is True
    pe = json.loads((tmp_path / PROOF_ELIGIBILITY_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
    assert pe["fixture_dev_only"] is False
    assert pe["x3_allow_is_separate_from_chain"] is True
    pc = json.loads((tmp_path / PRODUCT_CERTIFICATION_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
    assert pc["full_apps_contract_suite_certified"] is False
    assert pc["durable_write_certified"] is False


def test_x3_block_still_chain_complete(tmp_path: Path):
    payload = _minimal_chain(tmp_path, "unify_bullets")
    chain = inspect_one_spine_chain(tmp_path)
    assert chain["required_chain_complete"] is True
    pe = json.loads(
        emit_section_one_spine_certification_artifacts(
            tmp_path,
            section_id="unify_bullets",
            runtime_payload=payload,
            proof_bundle={"proof_eligible": False},
            runtime_generation_status="REAL_LLM",
        )["proof_eligibility_receipt"].read_text(encoding="utf-8")
    )
    assert pe["x3_code"] == "X3_BLOCK"
    cert = json.loads((tmp_path / ONE_SPINE_CERTIFICATION_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
    assert cert["x3_allow_required_for_chain"] is False


def test_fixture_dev_blocks_product_certification(tmp_path: Path):
    payload = _minimal_chain(tmp_path, "competencies")
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        emit_section_one_spine_certification_artifacts(
            tmp_path,
            section_id="competencies",
            runtime_payload=payload,
            proof_bundle={"proof_eligible": True},
            runtime_generation_status="REAL_LLM",
        )
        pc = json.loads((tmp_path / PRODUCT_CERTIFICATION_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
        assert pc["product_certification"] == "NOT_CLAIMED"
        assert pc["fixture_dev_only"] is True
    finally:
        deactivate_fixture_dev_bypass()


def test_certification_bypass_raises(tmp_path: Path):
    _minimal_chain(tmp_path, "headline")
    chain = inspect_one_spine_chain(tmp_path)
    with pytest.raises(SectionOneSpineCertificationPreconditionError):
        assert_certification_preconditions(
            {"certification_bypass_without_chain": True, "product_visible": True},
            tmp_path,
            chain=chain,
            product_certification="ONE_SPINE_SECTION_CERTIFIED",
        )
