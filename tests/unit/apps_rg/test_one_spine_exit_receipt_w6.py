"""Wave 6: section Exit spine receipts — ExitDispositionReceipt authority."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2
from apps_rg.runtime.spine.exit_artifacts import (
    EXIT_DISPOSITION_RECEIPT_ARTIFACT,
    EXIT_REVIEW_PACKET_ARTIFACT,
    EXIT_SPINE_RECEIPT_ARTIFACT,
    SectionExitSpinePreconditionError,
    assert_section_exit_spine_preconditions,
    build_exit_disposition_receipt_for_section,
    exit_spine_kill_switch_enabled,
)
from apps_rg.runtime.spine.c0_fec_compose import (
    FEC_BRIDGE_ARTIFACT,
    build_spine_c0_fec_artifact,
)
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.section_l2_lane_integration import (
    finalize_section_l2_after_output,
    prepare_section_l2_before_provider,
)
from apps_rg.runtime.section_l2_spine_receipt import SEALED_L2_ARTIFACT
from tests.unit.apps_rg.test_one_spine_fec_bridge_w5a import W5A_SECTIONS, _args, _minimal_pool

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def _patch_spine_c0_for_w6_chain(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid live Chroma in full L2→Exit chain tests."""
    from agentic_core.runtime.contracts.final_evidence_contract import (
        FinalEvidenceContract,
        SUPPORT_STATUS_PASS,
    )
    from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF

    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")

    def _fake_c0_retrieve(**_: object) -> FinalEvidenceContract:
        return FinalEvidenceContract(
            request_id="req-w6-exit-chain",
            run_id="run-w6-exit-chain",
            app_id="apps_rg",
            trace_id="trace-w6-exit-chain",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="digest-w6-exit-chain",
            graph_expansion_refs=(C0_GRAPH_LANE_NA_REF,),
        )

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        _fake_c0_retrieve,
    )

    def _fake_evidence_room(**kwargs: object):
        from apps_rg.runtime.spine.c0_fec_compose import build_spine_c0_fec_artifact

        return build_spine_c0_fec_artifact(
            section_id=str(kwargs.get("section_id") or ""),
            front_spine=kwargs["front_spine"],
            pool=kwargs["pool"],
        )

    monkeypatch.setattr(
        "apps_rg.runtime.c0.evidence_room.run_section_c0_evidence_room",
        _fake_evidence_room,
    )


def _write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


@pytest.mark.parametrize("section_id", W5A_SECTIONS)
def test_exit_disposition_receipt_single_x3(section_id: str, tmp_path: Path):
    _write_json(
        tmp_path / "x3_disposition.json",
        {"x3_code": "X3_ALLOW", "pass": True, "decisive_reason": "test"},
    )
    _write_json(tmp_path / SEALED_L2_ARTIFACT, {"contract_type": "SealedL2Artifact"})
    payload: dict = {"sealed_l2_artifact_ref": SEALED_L2_ARTIFACT, "run_id": "r1"}
    edr = build_exit_disposition_receipt_for_section(
        section_id=section_id,
        runtime_payload=payload,
        artifact_dir=tmp_path,
    )
    assert edr["contract_type"] == "ExitDispositionReceipt"
    assert edr["canonical_exit_claimed"] is True
    assert edr["section_x3_authoritative"] is False
    assert edr["section_x3_mirror_only"] is True
    assert isinstance(edr.get("x3_disposition"), dict)
    assert edr["x3_disposition"].get("x3_code") == "X3_ALLOW"
    assert edr["durable_commit_occurred"] is False
    assert edr["runtime_exhaust_bundle_claimed"] is False
    assert edr["product_certification"] == "NOT_CLAIMED"


def test_product_visible_blocked_without_sealed_l2(tmp_path: Path):
    payload: dict = {"product_visible": True}
    with pytest.raises(SectionExitSpinePreconditionError, match="SealedL2Artifact|sealed_l2"):
        assert_section_exit_spine_preconditions(payload, tmp_path)


def test_exit_bypass_flag_blocked(tmp_path: Path):
    _write_json(tmp_path / SEALED_L2_ARTIFACT, {"contract_type": "SealedL2Artifact"})
    payload = {"product_visible": True, "exit_bypass_without_sealed_l2": True}
    with pytest.raises(SectionExitSpinePreconditionError, match="SealedL2Artifact|sealed_l2"):
        assert_section_exit_spine_preconditions(payload, tmp_path)


def test_fixture_bypass_skips_exit_preconditions(tmp_path: Path):
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        assert_section_exit_spine_preconditions({"product_visible": True}, tmp_path)
    finally:
        deactivate_fixture_dev_bypass()


@pytest.mark.parametrize("section_id", ("headline", "competencies"))
def test_full_l2_then_exit_chain(tmp_path: Path, section_id: str):
    spine = build_section_front_spine_from_args(
        section_id=section_id,
        args=_args(),
        repo_root=REPO,
    )
    pool = _minimal_pool(section_id)
    payload: dict = {"allowed_fact_ids": list(pool.allowed_fact_ids_ordered), "run_id": "w6_unit"}
    bridge = build_spine_c0_fec_artifact(
        section_id=section_id,
        front_spine=spine,
        pool=pool,
    )
    _write_json(tmp_path / FEC_BRIDGE_ARTIFACT, bridge.bridge_doc)
    payload["section_fec_bridge"] = bridge.bridge_doc
    payload["fec_bridge_ref"] = FEC_BRIDGE_ARTIFACT
    payload["evidence_contract_consumed"] = True
    _write_json(
        tmp_path / "compiled_prompt_artifact.json",
        {"evidence_contract_consumed": True, "fec_bridge_mode": "section_fec_bridge"},
    )
    prepare_section_l2_before_provider(tmp_path, section_id, payload, provider_lane="retired_provider_profile")
    _write_json(tmp_path / "provider_request.json", {})
    _write_json(tmp_path / "provider_response.json", {})
    _write_json(tmp_path / "l2_output.json", {"section_id": section_id})
    _write_json(tmp_path / "x2_gate_outputs.json", [{"gate_id": "g1", "pass": True}])
    _write_json(tmp_path / "x3_disposition.json", {"x3_code": "X3_ALLOW", "pass": True})
    finalize_section_l2_after_output(tmp_path, section_id, payload)
    finalize_section_exit_after_l2(tmp_path, section_id, payload)
    assert (tmp_path / EXIT_REVIEW_PACKET_ARTIFACT).is_file()
    assert (tmp_path / EXIT_DISPOSITION_RECEIPT_ARTIFACT).is_file()
    assert (tmp_path / EXIT_SPINE_RECEIPT_ARTIFACT).is_file()
    erp = json.loads((tmp_path / EXIT_REVIEW_PACKET_ARTIFACT).read_text(encoding="utf-8"))
    assert erp["sealed_l2_artifact_ref"] == SEALED_L2_ARTIFACT
    assert erp["section_x3_authoritative"] is False
    sealed = json.loads((tmp_path / SEALED_L2_ARTIFACT).read_text(encoding="utf-8"))
    assert sealed.get("canonical_exit_claimed") is False
    edr = json.loads((tmp_path / EXIT_DISPOSITION_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
    assert edr.get("canonical_exit_claimed") is True
    assert edr.get("exit_review_packet_ref") == EXIT_REVIEW_PACKET_ARTIFACT


def test_kill_switch_enabled_by_default():
    assert exit_spine_kill_switch_enabled() is True
