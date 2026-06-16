from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.section_l2_spine_receipt import SEALED_L2_ARTIFACT
from apps_rg.runtime.spine import exit_artifacts as subject
from apps_rg.runtime.spine.front_contracts import deactivate_fixture_dev_bypass


@pytest.fixture(autouse=True)
def _exit_artifact_test_env(monkeypatch: pytest.MonkeyPatch):
    deactivate_fixture_dev_bypass()
    monkeypatch.delenv("APPS_RG_SECTION_EXIT_SPINE_KILL_SWITCH", raising=False)
    yield
    deactivate_fixture_dev_bypass()


def _write_json(path: Path, doc: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_preconditions_fail_closed_but_allow_non_product_modes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        subject.SectionExitSpinePreconditionError,
        match="SealedL2Artifact|sealed_l2",
    ):
        subject.assert_section_exit_spine_preconditions(
            {"product_visible": True},
            tmp_path,
        )

    subject.assert_section_exit_spine_preconditions(
        {"product_visible": False},
        tmp_path,
    )
    subject.assert_section_exit_spine_preconditions(
        {"product_visible": True},
        tmp_path,
        non_product_certified=True,
    )

    monkeypatch.setenv("APPS_RG_SECTION_EXIT_SPINE_KILL_SWITCH", "0")
    subject.assert_section_exit_spine_preconditions(
        {"product_visible": True},
        tmp_path,
    )


def test_exit_review_packet_prefers_runtime_refs_and_mirrors_x3(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / subject.SECTION_X3_DISPOSITION_ARTIFACT,
        {"x3_code": "X3_REVIEW", "decisive_reason": "fixture"},
    )

    packet = subject.build_exit_review_packet_for_section(
        section_id="executive_summary",
        runtime_payload={
            "run_id": "run-wave5",
            "sealed_l2_artifact_ref": "custom_sealed.json",
            "l2_execution_packet_ref": "custom_l2_packet.json",
            "compiled_prompt_artifact_ref": "custom_prompt.json",
            "final_evidence_contract_ref": "fec_fallback.json",
            "fec_bridge_ref": "fec_bridge_primary.json",
        },
        artifact_dir=tmp_path,
    )

    assert packet["contract_type"] == "ExitReviewPacket"
    assert packet["run_id"] == "run-wave5"
    assert packet["sealed_l2_artifact_ref"] == "custom_sealed.json"
    assert packet["l2_execution_packet_ref"] == "custom_l2_packet.json"
    assert packet["compiled_prompt_artifact_ref"] == "custom_prompt.json"
    assert packet["fec_bridge_ref"] == "fec_bridge_primary.json"
    assert packet["section_x3_authoritative"] is False
    assert packet["section_x3_mirror_only"] is True
    assert packet["canonical_exit_claimed"] is False
    assert packet["x3_disposition_snapshot"]["x3_code"] == "X3_REVIEW"


def test_x1_result_counts_judge_branches_and_fallback_shape(tmp_path: Path) -> None:
    _write_json(
        tmp_path / subject.X1D_JUDGE_OUTPUTS_ARTIFACT,
        {
            "judge_results": [
                {"dimension": "grounding", "provider_blocked": True},
                {"dimension": "style", "evaluator_mode": "MOCKED"},
                {"dimension": "shape", "provider_blocked": False},
            ]
        },
    )

    result = subject.build_section_exit_x1_result(
        section_id="headline",
        artifact_dir=tmp_path,
    )

    assert result["contract_type"] == "X1CheckoutResult"
    assert result["x1d_judge_outputs_ref"] == subject.X1D_JUDGE_OUTPUTS_ARTIFACT
    assert result["judge_count"] == 3
    assert result["blocked_judge_count"] == 1
    assert result["mocked_judge_count"] == 1
    assert result["checkout_status"] == "PARTIAL"
    assert result["product_certification"] == "NOT_CLAIMED"

    _write_json(
        tmp_path / subject.X1D_JUDGE_OUTPUTS_ARTIFACT,
        {"judges": [{"dimension": "grounding"}, {"dimension": "style"}]},
    )
    passing = subject.build_section_exit_x1_result(
        section_id="headline",
        artifact_dir=tmp_path,
    )
    assert passing["judge_count"] == 2
    assert passing["checkout_status"] == "PASS"

    (tmp_path / subject.X1D_JUDGE_OUTPUTS_ARTIFACT).unlink()
    missing = subject.build_section_exit_x1_result(
        section_id="headline",
        artifact_dir=tmp_path,
    )
    assert missing["x1d_judge_outputs_ref"] is None
    assert missing["checkout_status"] == "UNKNOWN"


def test_x2_result_accepts_dict_and_list_shapes(tmp_path: Path) -> None:
    _write_json(
        tmp_path / subject.X2_GATE_OUTPUTS_ARTIFACT,
        {
            "gates": [
                {"gate_id": "g_pass", "pass": True},
                {"id": "legacy_fail", "pass": False},
                "ignored",
            ]
        },
    )

    failing = subject.build_section_exit_x2_result(
        section_id="unify_bullets",
        artifact_dir=tmp_path,
    )

    assert failing["contract_type"] == "X2AggregationResult"
    assert failing["x2_gate_outputs_ref"] == subject.X2_GATE_OUTPUTS_ARTIFACT
    assert failing["gate_count"] == 2
    assert failing["failed_gate_ids"] == ["legacy_fail"]
    assert failing["aggregation_status"] == "FAIL"
    assert failing["product_certification"] == "NOT_CLAIMED"

    _write_json(
        tmp_path / subject.X2_GATE_OUTPUTS_ARTIFACT,
        [{"gate_id": "g1", "pass": True}, {"gate_id": "g2", "pass": True}],
    )
    passing = subject.build_section_exit_x2_result(
        section_id="unify_bullets",
        artifact_dir=tmp_path,
    )
    assert passing["gate_count"] == 2
    assert passing["failed_gate_ids"] == []
    assert passing["aggregation_status"] == "PASS"

    (tmp_path / subject.X2_GATE_OUTPUTS_ARTIFACT).write_text("{", encoding="utf-8")
    invalid = subject.build_section_exit_x2_result(
        section_id="unify_bullets",
        artifact_dir=tmp_path,
    )
    assert invalid["gate_count"] == 0
    assert invalid["aggregation_status"] == "UNKNOWN"


def test_exit_spine_receipt_requires_sealed_l2_and_canonical_exit_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_SECTION_EXIT_SPINE_KILL_SWITCH", "false")
    payload = {"run_id": "run-spine", "sealed_l2_artifact_ref": SEALED_L2_ARTIFACT}

    missing = subject.build_exit_spine_receipt(
        section_id="competencies",
        runtime_payload=payload,
        artifact_dir=tmp_path,
    )
    assert missing["exit_spine_status"] == "FAIL"
    assert missing["canonical_exit_claimed_on_exit_receipt"] is False
    assert missing["exit_spine_kill_switch_enabled"] is False

    _write_json(tmp_path / SEALED_L2_ARTIFACT, {"contract_type": "SealedL2Artifact"})
    sealed_only = subject.build_exit_spine_receipt(
        section_id="competencies",
        runtime_payload=payload,
        artifact_dir=tmp_path,
    )
    assert sealed_only["exit_spine_status"] == "FAIL"

    _write_json(
        tmp_path / subject.EXIT_DISPOSITION_RECEIPT_ARTIFACT,
        {"canonical_exit_claimed": True},
    )
    passing = subject.build_exit_spine_receipt(
        section_id="competencies",
        runtime_payload=payload,
        artifact_dir=tmp_path,
    )
    assert passing["exit_spine_status"] == "PASS"
    assert passing["canonical_exit_claimed_on_exit_receipt"] is True
    assert passing["canonical_exit_claimed_on_sealed_l2"] is False
    assert "exit_disposition_receipt" in passing["observed_chain"]
    assert passing["product_certification"] == "NOT_CLAIMED"


def test_emit_section_exit_spine_artifacts_writes_files_and_payload_refs(
    tmp_path: Path,
) -> None:
    _write_json(tmp_path / SEALED_L2_ARTIFACT, {"contract_type": "SealedL2Artifact"})
    _write_json(
        tmp_path / subject.SECTION_X3_DISPOSITION_ARTIFACT,
        {"x3_code": "X3_ALLOW", "pass": True},
    )
    _write_json(
        tmp_path / subject.X1D_JUDGE_OUTPUTS_ARTIFACT,
        {"judges": [{"dimension": "grounding"}]},
    )
    _write_json(
        tmp_path / subject.X2_GATE_OUTPUTS_ARTIFACT,
        [{"gate_id": "x2_shape", "pass": True}],
    )
    payload = {"run_id": "run-emit", "sealed_l2_artifact_ref": SEALED_L2_ARTIFACT}

    paths = subject.emit_section_exit_spine_artifacts(
        tmp_path,
        section_id="ibm_bullets",
        runtime_payload=payload,
    )

    assert set(paths) == {
        "exit_review_packet",
        "section_exit_x1_result",
        "section_exit_x2_result",
        "exit_disposition_receipt",
        "exit_spine_receipt",
    }
    assert all(path.is_file() for path in paths.values())
    assert payload["exit_review_packet_ref"] == subject.EXIT_REVIEW_PACKET_ARTIFACT
    assert payload["exit_disposition_receipt_ref"] == subject.EXIT_DISPOSITION_RECEIPT_ARTIFACT
    assert payload["exit_spine_receipt_ref"] == subject.EXIT_SPINE_RECEIPT_ARTIFACT
    assert payload["canonical_exit_authority_ref"] == subject.EXIT_DISPOSITION_RECEIPT_ARTIFACT
    assert payload["section_x3_authoritative"] is False

    x1 = _read_json(paths["section_exit_x1_result"])
    x2 = _read_json(paths["section_exit_x2_result"])
    edr = _read_json(paths["exit_disposition_receipt"])
    receipt = _read_json(paths["exit_spine_receipt"])

    assert x1["checkout_status"] == "PASS"
    assert x2["aggregation_status"] == "PASS"
    assert edr["x3_code"] == "X3_ALLOW"
    assert edr["canonical_exit_claimed"] is True
    assert receipt["exit_spine_status"] == "PASS"
    assert receipt["runtime_exhaust_bundle_claimed"] is False
