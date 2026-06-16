from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.section_l2_spine_receipt import SEALED_L2_ARTIFACT
from apps_rg.runtime.spine.exit_artifacts import EXIT_DISPOSITION_RECEIPT_ARTIFACT
from apps_rg.runtime.spine.front_contracts import deactivate_fixture_dev_bypass
from apps_rg.runtime.spine.governed_l6_shadow_compose import (
    GOVERNED_L6_SHADOW_MODE_SECTION,
    PROMOTION_STATUS_BLOCKED,
)
from apps_rg.runtime.spine.l6_eval_before_learn_receipt import (
    L6_EVAL_BEFORE_LEARN_RECEIPT_ARTIFACT,
)
from apps_rg.runtime.spine.spine_span_emit import (
    SPINE_SPAN_COVERAGE_RECEIPT,
    SPINE_SPAN_RECEIPT,
)
from apps_rg.runtime import section_runtime_exhaust_spine_receipt as subject


@pytest.fixture(autouse=True)
def _runtime_exhaust_test_env(monkeypatch: pytest.MonkeyPatch):
    deactivate_fixture_dev_bypass()
    monkeypatch.delenv("APPS_RG_SECTION_RUNTIME_EXHAUST_KILL_SWITCH", raising=False)
    monkeypatch.delenv("APPS_RG_L6_V40_SHADOW_EVAL", raising=False)
    monkeypatch.delenv("APPS_RG_SPINE_SPAN_EMIT", raising=False)
    monkeypatch.delenv("APPS_RG_SPINE_OTEL_SDK", raising=False)
    yield
    deactivate_fixture_dev_bypass()


def _write_json(path: Path, doc: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_runtime_exhaust_preconditions_fail_closed_with_bypass_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        subject.SectionRuntimeExhaustPreconditionError,
        match="exit_disposition",
    ):
        subject.assert_section_runtime_exhaust_preconditions(
            {"product_visible": True},
            tmp_path,
        )

    subject.assert_section_runtime_exhaust_preconditions(
        {"product_visible": False},
        tmp_path,
    )
    subject.assert_section_runtime_exhaust_preconditions(
        {"product_visible": True},
        tmp_path,
        non_product_certified=True,
    )

    monkeypatch.setenv("APPS_RG_SECTION_RUNTIME_EXHAUST_KILL_SWITCH", "0")
    subject.assert_section_runtime_exhaust_preconditions(
        {"product_visible": True},
        tmp_path,
    )

    monkeypatch.setenv("APPS_RG_SECTION_RUNTIME_EXHAUST_KILL_SWITCH", "1")
    _write_json(
        tmp_path / EXIT_DISPOSITION_RECEIPT_ARTIFACT,
        {"contract_type": "ExitDispositionReceipt"},
    )
    with pytest.raises(
        subject.SectionRuntimeExhaustPreconditionError,
        match="without ExitDispositionReceipt",
    ):
        subject.assert_section_runtime_exhaust_preconditions(
            {
                "product_visible": True,
                "runtime_exhaust_bypass_without_exit": True,
            },
            tmp_path,
        )


def test_l6_consume_gate_requires_bundle_and_handoff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        subject.SectionRuntimeExhaustPreconditionError,
        match="runtime_exhaust_bundle",
    ):
        subject.assert_section_l6_may_consume_exhaust(
            {"product_visible": True},
            tmp_path,
        )

    _write_json(
        tmp_path / subject.RUNTIME_EXHAUST_BUNDLE_ARTIFACT,
        {"contract_type": "RuntimeExhaustBundle"},
    )
    with pytest.raises(
        subject.SectionRuntimeExhaustPreconditionError,
        match="l6_shadow_handoff_receipt",
    ):
        subject.assert_section_l6_may_consume_exhaust(
            {"product_visible": True},
            tmp_path,
        )

    _write_json(
        tmp_path / subject.L6_SHADOW_HANDOFF_RECEIPT_ARTIFACT,
        {"contract_type": "L6ShadowHandoffReceipt"},
    )
    subject.assert_section_l6_may_consume_exhaust(
        {"product_visible": True},
        tmp_path,
    )

    (tmp_path / subject.RUNTIME_EXHAUST_BUNDLE_ARTIFACT).unlink()
    (tmp_path / subject.L6_SHADOW_HANDOFF_RECEIPT_ARTIFACT).unlink()
    subject.assert_section_l6_may_consume_exhaust(
        {"product_visible": False},
        tmp_path,
    )
    monkeypatch.setenv("APPS_RG_SECTION_RUNTIME_EXHAUST_KILL_SWITCH", "false")
    subject.assert_section_l6_may_consume_exhaust(
        {"product_visible": True},
        tmp_path,
    )


def test_runtime_exhaust_bundle_records_inventory_trace_refs_and_exit_x3(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact_dir = repo / "artifacts" / "lane"
    artifact_dir.mkdir(parents=True)
    _write_json(
        artifact_dir / EXIT_DISPOSITION_RECEIPT_ARTIFACT,
        {
            "run_id": "run-from-exit",
            "x3_code": "X3_REVIEW",
            "x3_disposition": {"x3_code": "X3_ALLOW", "pass": True},
        },
    )
    for name in (
        "route_contract.json",
        "final_evidence_contract_bridge.json",
        "l2_execution_packet.json",
        "exit_review_packet.json",
        "provider_request.json",
        "provider_response.json",
        "x2_gate_outputs.json",
        "x1d_llm_judge_outputs.json",
        "exit_spine_receipt.json",
        "l2_spine_receipt.json",
    ):
        _write_json(artifact_dir / name, {"name": name})
    _write_json(artifact_dir / "post_runtime" / "shadow.json", {"ok": True})

    bundle = subject.build_runtime_exhaust_bundle_for_section(
        section_id="headline",
        runtime_payload={"sealed_l2_artifact_ref": "custom_sealed.json"},
        artifact_dir=artifact_dir,
        repo_root=repo,
    )

    assert bundle["contract_type"] == "RuntimeExhaustBundle"
    assert bundle["run_id"] == "run-from-exit"
    assert bundle["sealed_l2_artifact_ref"] == "custom_sealed.json"
    assert bundle["x3_code"] == "X3_ALLOW"
    assert bundle["x3_disposition"] == {"x3_code": "X3_ALLOW", "pass": True}
    assert bundle["runtime_terminal_boundary"] == "post_exit_disposition"
    assert bundle["durable_commit_occurred"] is False
    assert bundle["product_certification"] == "NOT_CLAIMED"
    assert bundle["spine_runtime_exhaust_bundle_claimed"] is True
    assert bundle["proof_refs"] == {
        "exit_spine_receipt": "exit_spine_receipt.json",
        "l2_spine_receipt": "l2_spine_receipt.json",
    }
    assert bundle["trace_refs"]["route_contract.json"] == (
        "artifacts/lane/route_contract.json"
    )
    assert bundle["trace_refs"]["provider_response.json"] == (
        "artifacts/lane/provider_response.json"
    )
    assert {"name": "post_runtime/shadow.json", "kind": "file", "section_id": "headline"} in bundle[
        "artifact_inventory"
    ]
    assert bundle["artifact_inventory_count"] == len(bundle["artifact_inventory"])


def test_runtime_exhaust_receipt_status_and_l6_v40_flag(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {"run_id": "run-receipt", "sealed_l2_artifact_ref": SEALED_L2_ARTIFACT}

    missing = subject.build_runtime_exhaust_receipt(
        section_id="competencies",
        runtime_payload=payload,
        artifact_dir=tmp_path,
    )
    assert missing["exhaust_spine_status"] == "FAIL"
    assert missing["l6_v40_shadow_eval_enabled"] is False

    _write_json(
        tmp_path / EXIT_DISPOSITION_RECEIPT_ARTIFACT,
        {"contract_type": "ExitDispositionReceipt"},
    )
    _write_json(
        tmp_path / subject.RUNTIME_EXHAUST_BUNDLE_ARTIFACT,
        {"contract_type": "RuntimeExhaustBundle"},
    )
    monkeypatch.setenv("APPS_RG_L6_V40_SHADOW_EVAL", "yes")
    passing = subject.build_runtime_exhaust_receipt(
        section_id="competencies",
        runtime_payload=payload,
        artifact_dir=tmp_path,
    )
    assert passing["exhaust_spine_status"] == "PASS"
    assert passing["runtime_exhaust_kill_switch_enabled"] is True
    assert passing["l6_v40_shadow_eval_enabled"] is True
    assert "section_RuntimeExhaustBundle" in passing["observed_chain"]
    assert passing["product_certification"] == "NOT_CLAIMED"


def test_l6_shadow_handoff_receipt_uses_exhaust_x3_and_blocks_promotion(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / subject.RUNTIME_EXHAUST_BUNDLE_ARTIFACT,
        {"x3_code": "X3_BLOCK"},
    )

    handoff = subject.build_l6_shadow_handoff_receipt(
        section_id="ibm_bullets",
        runtime_payload={"run_id": "run-handoff"},
        artifact_dir=tmp_path,
    )

    assert handoff["contract_type"] == "L6ShadowHandoffReceipt"
    assert handoff["runtime_exhaust_bundle_ref"] == subject.RUNTIME_EXHAUST_BUNDLE_ARTIFACT
    assert handoff["exit_disposition_receipt_ref"] == EXIT_DISPOSITION_RECEIPT_ARTIFACT
    assert handoff["handoff_phase"] == "post_runtime_exhaust_only"
    assert handoff["observed_x3_code"] == "X3_BLOCK"
    assert handoff["no_l6_current_run_rescue_assertion"] is True
    assert handoff["no_l6_current_run_mutation_assertion"] is True
    assert handoff["l6_can_change_x3"] is False
    assert handoff["l6_can_change_exit_disposition"] is False
    assert handoff["product_certification"] == "NOT_CLAIMED"


def test_emit_runtime_exhaust_artifacts_writes_payload_refs_and_guard_receipts(
    tmp_path: Path,
) -> None:
    repo = tmp_path
    artifact_dir = repo / "lane"
    artifact_dir.mkdir()
    _write_json(
        artifact_dir / EXIT_DISPOSITION_RECEIPT_ARTIFACT,
        {
            "contract_type": "ExitDispositionReceipt",
            "run_id": "run-emit",
            "x3_disposition": {"x3_code": "X3_ALLOW", "pass": True},
            "x3_code": "X3_ALLOW",
        },
    )
    _write_json(artifact_dir / SEALED_L2_ARTIFACT, {"contract_type": "SealedL2Artifact"})
    _write_json(artifact_dir / "provider_response.json", {"text": "ok"})
    payload = {"run_id": "run-emit", "product_visible": True}

    paths = subject.emit_section_runtime_exhaust_spine_artifacts(
        artifact_dir,
        section_id="unify_bullets",
        runtime_payload=payload,
        repo_root=repo,
    )

    assert set(paths) == {
        "runtime_exhaust_bundle",
        "runtime_exhaust_receipt",
        "l6_shadow_handoff_receipt",
    }
    assert all(path.is_file() for path in paths.values())
    assert payload["runtime_exhaust_bundle_ref"] == subject.RUNTIME_EXHAUST_BUNDLE_ARTIFACT
    assert payload["runtime_exhaust_receipt_ref"] == subject.RUNTIME_EXHAUST_RECEIPT_ARTIFACT
    assert payload["l6_shadow_handoff_receipt_ref"] == subject.L6_SHADOW_HANDOFF_RECEIPT_ARTIFACT
    assert payload["l6_post_runtime_boundary_sealed"] is True
    assert payload["l6_eval_before_learn_receipt_ref"] == L6_EVAL_BEFORE_LEARN_RECEIPT_ARTIFACT

    governed = payload["governed_l6_handoff_envelope"]
    assert governed["governed_l6_shadow_mode"] == GOVERNED_L6_SHADOW_MODE_SECTION
    assert governed["promotion_status"] == PROMOTION_STATUS_BLOCKED
    assert governed["runtime_exhaust_bundle_ref"] == subject.RUNTIME_EXHAUST_BUNDLE_ARTIFACT
    assert governed["exit_disposition_ref"] == EXIT_DISPOSITION_RECEIPT_ARTIFACT
    assert governed["observed_x3_code"] == "X3_ALLOW"

    bundle = _read_json(paths["runtime_exhaust_bundle"])
    receipt = _read_json(paths["runtime_exhaust_receipt"])
    handoff = _read_json(paths["l6_shadow_handoff_receipt"])
    eval_receipt = _read_json(artifact_dir / L6_EVAL_BEFORE_LEARN_RECEIPT_ARTIFACT)
    span_row = json.loads((artifact_dir / SPINE_SPAN_RECEIPT).read_text(encoding="utf-8").splitlines()[0])
    span_coverage = _read_json(artifact_dir / SPINE_SPAN_COVERAGE_RECEIPT)

    assert bundle["x3_code"] == "X3_ALLOW"
    assert receipt["exhaust_spine_status"] == "PASS"
    assert handoff["observed_x3_code"] == "X3_ALLOW"
    assert eval_receipt["promotion_allowed"] is False
    assert eval_receipt["runtime_exhaust_bundle_ref"] == subject.RUNTIME_EXHAUST_BUNDLE_ARTIFACT
    assert span_row["layer_key"] == "L6"
    assert span_row["extra"]["handoff_phase"] == "post_runtime_exhaust_only"
    assert span_coverage["schema_version"] == "apps_rg_spine_span_coverage_v1"
