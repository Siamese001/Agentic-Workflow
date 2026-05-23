"""Wave 7: section RuntimeExhaustBundle after Exit; L6 post-run handoff only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2
from apps_rg.runtime.spine.exit_artifacts import EXIT_DISPOSITION_RECEIPT_ARTIFACT
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
from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
    finalize_section_runtime_exhaust_before_l6,
    gate_section_l6_shadow_after_exhaust,
)
from apps_rg.runtime.section_runtime_exhaust_spine_receipt import (
    L6_SHADOW_HANDOFF_RECEIPT_ARTIFACT,
    RUNTIME_EXHAUST_BUNDLE_ARTIFACT,
    RUNTIME_EXHAUST_RECEIPT_ARTIFACT,
    SectionRuntimeExhaustPreconditionError,
    assert_section_runtime_exhaust_preconditions,
    runtime_exhaust_kill_switch_enabled,
)
from tests.unit.apps_rg.test_one_spine_fec_bridge_w5a import W5A_SECTIONS, _args, _minimal_pool

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def _patch_spine_c0_for_w7_chain(monkeypatch: pytest.MonkeyPatch) -> None:
    from agentic_core.runtime.contracts.final_evidence_contract import (
        FinalEvidenceContract,
        SUPPORT_STATUS_PASS,
    )
    from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF

    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")

    def _fake_c0_retrieve(**_: object) -> FinalEvidenceContract:
        return FinalEvidenceContract(
            request_id="req-w7-exhaust-chain",
            run_id="run-w7-exhaust-chain",
            app_id="apps_rg",
            trace_id="trace-w7-exhaust-chain",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="digest-w7-exhaust-chain",
            graph_expansion_refs=(C0_GRAPH_LANE_NA_REF,),
        )

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        _fake_c0_retrieve,
    )


def _write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


@pytest.mark.parametrize("section_id", W5A_SECTIONS)
def test_runtime_exhaust_bundle_contract_shape(section_id: str, tmp_path: Path):
    _write_json(tmp_path / EXIT_DISPOSITION_RECEIPT_ARTIFACT, {
        "contract_type": "ExitDispositionReceipt",
        "x3_disposition": {"x3_code": "X3_ALLOW", "pass": True},
        "sealed_l2_artifact_ref": SEALED_L2_ARTIFACT,
    })
    _write_json(tmp_path / SEALED_L2_ARTIFACT, {"contract_type": "SealedL2Artifact"})
    payload: dict = {"run_id": "w7", "product_visible": True}
    paths = finalize_section_runtime_exhaust_before_l6(
        tmp_path, section_id, payload, repo_root=REPO
    )
    bundle = json.loads(paths["runtime_exhaust_bundle"].read_text(encoding="utf-8"))
    assert bundle["contract_type"] == "RuntimeExhaustBundle"
    assert bundle["exit_disposition_receipt_ref"] == EXIT_DISPOSITION_RECEIPT_ARTIFACT
    assert bundle["sealed_l2_artifact_ref"] == SEALED_L2_ARTIFACT
    assert bundle["x3_code"] == "X3_ALLOW"
    assert bundle["artifact_inventory"]
    assert bundle["durable_commit_occurred"] is False
    assert bundle["product_certification"] == "NOT_CLAIMED"
    handoff = json.loads((tmp_path / L6_SHADOW_HANDOFF_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
    assert handoff["no_l6_current_run_rescue_assertion"] is True
    assert handoff["l6_can_change_exit_disposition"] is False


def test_exhaust_blocked_without_exit_disposition(tmp_path: Path):
    payload: dict = {"product_visible": True}
    with pytest.raises(SectionRuntimeExhaustPreconditionError, match="exit_disposition"):
        assert_section_runtime_exhaust_preconditions(payload, tmp_path)


def test_l6_gate_blocked_without_exhaust_bundle(tmp_path: Path):
    _write_json(tmp_path / EXIT_DISPOSITION_RECEIPT_ARTIFACT, {"contract_type": "ExitDispositionReceipt"})
    payload: dict = {"product_visible": True}
    with pytest.raises(SectionRuntimeExhaustPreconditionError, match="runtime_exhaust_bundle"):
        gate_section_l6_shadow_after_exhaust(tmp_path, payload)


def test_fixture_bypass_skips_exhaust_preconditions(tmp_path: Path):
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        assert_section_runtime_exhaust_preconditions({"product_visible": True}, tmp_path)
        gate_section_l6_shadow_after_exhaust(tmp_path, {"product_visible": True})
    finally:
        deactivate_fixture_dev_bypass()


@pytest.mark.parametrize("section_id", ("headline", "competencies"))
def test_full_exit_then_exhaust_chain(tmp_path: Path, section_id: str):
    spine = build_section_front_spine_from_args(section_id=section_id, args=_args(), repo_root=REPO)
    pool = _minimal_pool(section_id)
    payload: dict = {"allowed_fact_ids": list(pool.allowed_fact_ids_ordered), "run_id": "w7_chain"}
    bridge = build_spine_c0_fec_artifact(
        section_id=section_id,
        front_spine=spine,
        pool=pool,
    )
    _write_json(tmp_path / FEC_BRIDGE_ARTIFACT, bridge.bridge_doc)
    payload["section_fec_bridge"] = bridge.bridge_doc
    payload["fec_bridge_ref"] = FEC_BRIDGE_ARTIFACT
    _write_json(tmp_path / "compiled_prompt_artifact.json", {"evidence_contract_consumed": True})
    prepare_section_l2_before_provider(tmp_path, section_id, payload, provider_lane="qwen_vllm")
    _write_json(tmp_path / "l2_output.json", {})
    _write_json(tmp_path / "x3_disposition.json", {"x3_code": "X3_ALLOW", "pass": True})
    finalize_section_l2_after_output(tmp_path, section_id, payload)
    finalize_section_exit_after_l2(tmp_path, section_id, payload)
    finalize_section_runtime_exhaust_before_l6(tmp_path, section_id, payload, repo_root=REPO)
    assert (tmp_path / RUNTIME_EXHAUST_BUNDLE_ARTIFACT).is_file()
    assert (tmp_path / RUNTIME_EXHAUST_RECEIPT_ARTIFACT).is_file()
    gate_section_l6_shadow_after_exhaust(tmp_path, payload)


def test_kill_switch_enabled_by_default():
    assert runtime_exhaust_kill_switch_enabled() is True
