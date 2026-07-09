"""Unit tests for spine section X3 finalize edge cases."""
# apps-test-model: SPINE BINDING
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from apps_rg.runtime.sections.section_final_materialized_binding import (
    augment_x2_payload_with_final_materialized_binding,
)
from apps_rg.runtime.spine.section_x3_finalize import (
    FINAL_MATERIALIZED_BLOCK_X3_CODE,
    FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT,
    FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID,
    finalize_section_lane_x3,
    lane_outcome_authorized_from_x3,
    persist_section_x3_mirror,
    refresh_section_exit_after_x3_change,
)


def _write_bound_x2_payload(
    artifact_dir: Path,
    *,
    section_id: str = "headline",
    gates: list[dict] | None = None,
) -> None:
    rows = gates or [{"gate_id": "x2_example", "pass": True}]
    failed = [str(g["gate_id"]) for g in rows if not bool(g.get("pass"))]
    payload = {
        "gates": rows,
        "failed_gates": failed,
        "x2_passed": sum(1 for g in rows if g.get("pass")),
        "x2_failed": len(failed),
        "total_x2_gates": len(rows),
    }
    (artifact_dir / "x2_gate_outputs.json").write_text(
        json.dumps(
            augment_x2_payload_with_final_materialized_binding(
                payload,
                artifact_dir=artifact_dir,
                section_id=section_id,
            )
        ),
        encoding="utf-8",
    )


def test_persist_section_x3_mirror_merges_extra(tmp_path: Path) -> None:
    x3 = SimpleNamespace(x3_code="X3_ALLOW", pass_=True)
    x3.to_dict = lambda: {"x3_code": "X3_ALLOW", "pass": True}  # type: ignore[method-assign]

    doc = persist_section_x3_mirror(
        tmp_path,
        x3,
        x3_doc_extra={"proof_eligible": True, "judge_proof_eligible": False},
    )
    assert doc["proof_eligible"] is True
    loaded = (tmp_path / "x3_disposition.json").read_text(encoding="utf-8")
    assert "proof_eligible" in loaded


def test_finalize_section_lane_x3_writes_passing_final_materialized_contract(tmp_path: Path) -> None:
    x3 = SimpleNamespace(x3_code="X3_ALLOW", pass_=True)
    x3.to_dict = lambda: {"x3_code": "X3_ALLOW", "pass": True}  # type: ignore[method-assign]
    (tmp_path / "command_output.txt").write_text("Final section text.\n", encoding="utf-8")
    (tmp_path / "claim_ledger.json").write_text(
        json.dumps([{"claim_text": "Final section text.", "source_fact_ids": ["f1"]}]),
        encoding="utf-8",
    )
    (tmp_path / "l2_output.json").write_text('{"section_id":"headline"}\n', encoding="utf-8")
    _write_bound_x2_payload(tmp_path, section_id="headline")
    (tmp_path / "x1d_llm_judge_outputs.json").write_text(
        json.dumps(
            {
                "judges": [
                    {
                        "provider_key": "openai_chatgpt",
                        "evaluator_mode": "MODEL_BACKED",
                        "provider_status": "MODEL_BACKED_PASS",
                        "pass": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "section_repair_ledger.json").write_text(
        json.dumps({"authoritative_l2_source": "initial_llm", "authoritative_attempt": 1}),
        encoding="utf-8",
    )

    finalize_section_lane_x3(
        artifact_dir=tmp_path,
        section_id="headline",
        runtime_payload={"run_id": "r1"},
        x3_result=x3,
    )

    contract = json.loads(
        (tmp_path / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT).read_text(encoding="utf-8")
    )
    x3_doc = json.loads((tmp_path / "x3_disposition.json").read_text(encoding="utf-8"))
    assert contract["pass"] is True
    assert contract["final_materialized_output_ref"] == "command_output.txt"
    assert contract["final_claim_ledger_present"] is True
    assert contract["final_claim_ledger_row_count"] == 1
    assert contract["x1d_judge_outputs_present"] is True
    assert contract["x1d_all_model_backed_judges_pass"] is True
    assert contract["repair_ledger_authoritative_l2_source"] == "initial_llm"
    assert contract["acceptance_inputs"] == [
        "final_materialized_output",
        "claim_ledger",
        "x2_gate_outputs",
        "x2_final_materialized_input_binding",
        "x1d_judge_outputs",
        "section_repair_ledger",
        "declared_final_materialized_contracts",
    ]
    assert x3_doc["final_materialized_acceptance_ok"] is True
    assert x3_doc["final_materialized_acceptance_contract_ref"] == FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT


def test_finalize_section_lane_x3_blocks_allow_without_final_x1d_judges(tmp_path: Path) -> None:
    x3 = SimpleNamespace(x3_code="X3_ALLOW", pass_=True)
    x3.to_dict = lambda: {"x3_code": "X3_ALLOW", "pass": True}  # type: ignore[method-assign]
    (tmp_path / "command_output.txt").write_text("Final section text.\n", encoding="utf-8")
    (tmp_path / "claim_ledger.json").write_text(
        json.dumps([{"claim_text": "Final section text.", "source_fact_ids": ["f1"]}]),
        encoding="utf-8",
    )
    (tmp_path / "l2_output.json").write_text('{"section_id":"headline"}\n', encoding="utf-8")
    _write_bound_x2_payload(tmp_path, section_id="ey_bullets")

    finalize_section_lane_x3(
        artifact_dir=tmp_path,
        section_id="headline",
        runtime_payload={"run_id": "r1"},
        x3_result=x3,
    )

    contract = json.loads(
        (tmp_path / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT).read_text(encoding="utf-8")
    )
    x3_doc = json.loads((tmp_path / "x3_disposition.json").read_text(encoding="utf-8"))
    assert contract["pass"] is False
    assert "x1d_judge_outputs_missing" in contract["failure_reasons"]
    assert x3_doc["x3_code"] == FINAL_MATERIALIZED_BLOCK_X3_CODE
    assert lane_outcome_authorized_from_x3(x3_doc) is False


def test_finalize_section_lane_x3_blocks_declared_materialized_selection_failure(
    tmp_path: Path,
) -> None:
    x3 = SimpleNamespace(x3_code="X3_ALLOW", pass_=True)
    x3.to_dict = lambda: {"x3_code": "X3_ALLOW", "pass": True}  # type: ignore[method-assign]
    selection_contract = {
        "schema_version": "role_episode_final_materialized_selection_contract.v1",
        "expected_bullet_count": 3,
        "selected_source_fact_ids": ["f1", "f2"],
        "selected_unique_source_fact_count": 2,
        "rendered_bullet_count": 2,
        "rendered_source_fact_ids": ["f1", "f2"],
        "final_materialized_acceptance_ok": False,
    }
    l2_output = {
        "section_id": "ey_bullets",
        "bullets": [
            {"bullet_text": "First proof bullet.", "source_fact_ids": ["f1"]},
            {"bullet_text": "Second proof bullet.", "source_fact_ids": ["f2"]},
        ],
        "claim_ledger": [
            {"claim_text": "First proof bullet.", "source_fact_ids": ["f1"]},
            {"claim_text": "Second proof bullet.", "source_fact_ids": ["f2"]},
        ],
        "final_materialized_selection_contract": selection_contract,
        "final_materialized_acceptance_ok": False,
    }
    (tmp_path / "l2_output.json").write_text(json.dumps(l2_output), encoding="utf-8")
    (tmp_path / "claim_ledger.json").write_text(
        json.dumps(l2_output["claim_ledger"]),
        encoding="utf-8",
    )
    _write_bound_x2_payload(tmp_path, section_id="headline")
    (tmp_path / "x1d_llm_judge_outputs.json").write_text(
        json.dumps(
            {
                "judges": [
                    {
                        "provider_key": "openai_chatgpt",
                        "evaluator_mode": "MODEL_BACKED",
                        "provider_status": "MODEL_BACKED_PASS",
                        "pass": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    finalize_section_lane_x3(
        artifact_dir=tmp_path,
        section_id="ey_bullets",
        runtime_payload={"run_id": "r1"},
        x3_result=x3,
    )

    contract = json.loads(
        (tmp_path / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT).read_text(encoding="utf-8")
    )
    x3_doc = json.loads((tmp_path / "x3_disposition.json").read_text(encoding="utf-8"))
    assert contract["pass"] is False
    assert contract["declared_final_materialized_contracts_all_pass"] is False
    assert contract["declared_final_materialized_contract_failures"] == [
        "role_episode_final_materialized_selection_contract"
    ]
    assert "declared_final_materialized_contract_failed" in contract["failure_reasons"]
    assert x3_doc["x3_code"] == FINAL_MATERIALIZED_BLOCK_X3_CODE
    assert lane_outcome_authorized_from_x3(x3_doc) is False


def test_finalize_section_lane_x3_flags_allow_without_final_x2_contract(tmp_path: Path) -> None:
    x3 = SimpleNamespace(x3_code="X3_ALLOW", pass_=True)
    x3.to_dict = lambda: {"x3_code": "X3_ALLOW", "pass": True}  # type: ignore[method-assign]
    (tmp_path / "command_output.txt").write_text("Final section text.\n", encoding="utf-8")
    (tmp_path / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_failed", "pass": False}]}),
        encoding="utf-8",
    )

    finalize_section_lane_x3(
        artifact_dir=tmp_path,
        section_id="ey_bullets",
        runtime_payload={"run_id": "r2"},
        x3_result=x3,
    )

    contract = json.loads(
        (tmp_path / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT).read_text(encoding="utf-8")
    )
    x3_doc = json.loads((tmp_path / "x3_disposition.json").read_text(encoding="utf-8"))
    assert contract["pass"] is False
    assert contract["failed_gate_ids"] == ["x2_failed"]
    assert x3_doc["final_materialized_acceptance_ok"] is False
    assert x3_doc["final_materialized_acceptance_failure_gate"] == FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID
    assert x3_doc["x3_code"] == FINAL_MATERIALIZED_BLOCK_X3_CODE
    assert x3_doc["pass"] is False
    assert x3_doc["final_materialized_acceptance_original_x3_code"] == "X3_ALLOW"
    assert lane_outcome_authorized_from_x3(x3_doc) is False


def test_finalize_section_lane_x3_blocks_allow_without_x2_materialized_binding(
    tmp_path: Path,
) -> None:
    x3 = SimpleNamespace(x3_code="X3_ALLOW", pass_=True)
    x3.to_dict = lambda: {"x3_code": "X3_ALLOW", "pass": True}  # type: ignore[method-assign]
    (tmp_path / "command_output.txt").write_text("Final section text.\n", encoding="utf-8")
    (tmp_path / "claim_ledger.json").write_text(
        json.dumps([{"claim_text": "Final section text.", "source_fact_ids": ["f1"]}]),
        encoding="utf-8",
    )
    (tmp_path / "l2_output.json").write_text('{"section_id":"headline"}\n', encoding="utf-8")
    (tmp_path / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_example", "pass": True}]}),
        encoding="utf-8",
    )
    (tmp_path / "x1d_llm_judge_outputs.json").write_text(
        json.dumps(
            {
                "judges": [
                    {
                        "provider_key": "openai_chatgpt",
                        "evaluator_mode": "MODEL_BACKED",
                        "provider_status": "MODEL_BACKED_PASS",
                        "pass": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    finalize_section_lane_x3(
        artifact_dir=tmp_path,
        section_id="headline",
        runtime_payload={"run_id": "r1"},
        x3_result=x3,
    )

    contract = json.loads(
        (tmp_path / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT).read_text(encoding="utf-8")
    )
    x3_doc = json.loads((tmp_path / "x3_disposition.json").read_text(encoding="utf-8"))
    assert contract["pass"] is False
    assert contract["x2_final_materialized_binding_present"] is False
    assert "x2_final_materialized_binding_missing" in contract["failure_reasons"]
    assert x3_doc["x3_code"] == FINAL_MATERIALIZED_BLOCK_X3_CODE


def test_finalize_section_lane_x3_blocks_stale_x2_after_final_text_mutation(
    tmp_path: Path,
) -> None:
    x3 = SimpleNamespace(x3_code="X3_ALLOW", pass_=True)
    x3.to_dict = lambda: {"x3_code": "X3_ALLOW", "pass": True}  # type: ignore[method-assign]
    (tmp_path / "command_output.txt").write_text("Old section text.\n", encoding="utf-8")
    (tmp_path / "claim_ledger.json").write_text(
        json.dumps([{"claim_text": "Old section text.", "source_fact_ids": ["f1"]}]),
        encoding="utf-8",
    )
    (tmp_path / "l2_output.json").write_text(
        json.dumps({"section_id": "headline", "headline_line": "Old section text."}),
        encoding="utf-8",
    )
    _write_bound_x2_payload(tmp_path, section_id="headline")
    (tmp_path / "command_output.txt").write_text("New section text after repair.\n", encoding="utf-8")
    (tmp_path / "x1d_llm_judge_outputs.json").write_text(
        json.dumps(
            {
                "judges": [
                    {
                        "provider_key": "openai_chatgpt",
                        "evaluator_mode": "MODEL_BACKED",
                        "provider_status": "MODEL_BACKED_PASS",
                        "pass": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    finalize_section_lane_x3(
        artifact_dir=tmp_path,
        section_id="headline",
        runtime_payload={"run_id": "r1"},
        x3_result=x3,
    )

    contract = json.loads(
        (tmp_path / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT).read_text(encoding="utf-8")
    )
    assert contract["pass"] is False
    assert contract["x2_final_materialized_binding_pass"] is False
    assert (
        "x2_final_materialized_binding_final_materialized_output_sha256_mismatch"
        in contract["failure_reasons"]
    )


def test_persist_section_x3_mirror_preserves_final_materialized_block(tmp_path: Path) -> None:
    existing = {
        "x3_code": FINAL_MATERIALIZED_BLOCK_X3_CODE,
        "pass": False,
        "final_materialized_acceptance_contract_ref": FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT,
        "final_materialized_acceptance_ok": False,
        "final_materialized_acceptance_failure_gate": FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID,
        "final_materialized_acceptance_original_x3_code": "X3_ALLOW",
        "final_materialized_acceptance_original_pass": True,
    }
    (tmp_path / "x3_disposition.json").write_text(json.dumps(existing), encoding="utf-8")

    persisted = persist_section_x3_mirror(
        tmp_path,
        {"x3_code": "X3_ALLOW", "pass": True, "publish_disposition": "allowed"},
    )

    assert persisted["x3_code"] == FINAL_MATERIALIZED_BLOCK_X3_CODE
    assert persisted["pass"] is False
    assert persisted["publish_disposition"] == "allowed"
    assert persisted["final_materialized_acceptance_original_x3_code"] == "X3_ALLOW"
    assert persisted["final_materialized_acceptance_blocked"] is True
    assert lane_outcome_authorized_from_x3(persisted) is False


def test_persist_section_x3_mirror_does_not_preserve_stale_failure_on_explicit_pass(
    tmp_path: Path,
) -> None:
    existing = {
        "x3_code": FINAL_MATERIALIZED_BLOCK_X3_CODE,
        "pass": False,
        "final_materialized_acceptance_contract_ref": FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT,
        "final_materialized_acceptance_ok": False,
        "final_materialized_acceptance_failure_gate": FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID,
        "final_materialized_acceptance_original_x3_code": "X3_ALLOW",
        "final_materialized_acceptance_blocked": True,
        "blocked_by_gate": FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID,
    }
    (tmp_path / "x3_disposition.json").write_text(json.dumps(existing), encoding="utf-8")

    persisted = persist_section_x3_mirror(
        tmp_path,
        {
            "x3_code": "X3_ALLOW",
            "pass": True,
            "final_materialized_acceptance_contract_ref": FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT,
            "final_materialized_acceptance_ok": True,
        },
    )

    assert persisted["x3_code"] == "X3_ALLOW"
    assert persisted["pass"] is True
    assert "final_materialized_acceptance_failure_gate" not in persisted
    assert "final_materialized_acceptance_blocked" not in persisted
    assert lane_outcome_authorized_from_x3(persisted) is True


@patch("apps_rg.runtime.spine.section_x3_finalize.ExitEvalPipeline")
@patch("apps_rg.runtime.spine.exit_lane_hooks.finalize_section_exit_after_l2")
def test_finalize_section_lane_x3_writes_exit_receipt(
    mock_exit_hooks: MagicMock,
    mock_pipeline_cls: MagicMock,
    tmp_path: Path,
) -> None:
    mock_pipeline_cls.return_value.run.return_value = SimpleNamespace(
        disposition=SimpleNamespace(value="X3_DENY")
    )
    runtime_payload: dict = {"run_id": "r1", "request_id": "req1"}
    x3 = SimpleNamespace(
        x3_code="X3_REVIEW_JUDGE_SOFT_FAIL",
        pass_=False,
    )
    x3.to_dict = lambda: {"x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL", "pass": False}  # type: ignore[method-assign]

    (tmp_path / "sealed_l2_artifact.json").write_text(
        '{"schema_version":"section_sealed_l2_artifact_v1"}', encoding="utf-8"
    )
    runtime_payload["sealed_l2_artifact_ref"] = "sealed_l2_artifact.json"
    finalize_section_lane_x3(
        artifact_dir=tmp_path,
        section_id="executive_summary",
        runtime_payload=runtime_payload,
        x3_result=x3,
        skip_exit_receipts=False,
    )
    assert (tmp_path / "x3_disposition.json").is_file()
    mock_exit_hooks.assert_called_once()
    assert runtime_payload.get("spine_exit_eval_disposition") == "X3_DENY"


@patch("apps_rg.runtime.spine.section_x3_finalize.ExitEvalPipeline")
@patch("apps_rg.runtime.spine.exit_lane_hooks.finalize_section_exit_after_l2")
def test_refresh_section_exit_after_x3_change(
    mock_exit_hooks: MagicMock,
    mock_pipeline_cls: MagicMock,
    tmp_path: Path,
) -> None:
    mock_exit_hooks.reset_mock()
    runtime_payload = {"run_id": "r2"}
    (tmp_path / "sealed_l2_artifact.json").write_text(
        '{"schema_version":"section_sealed_l2_artifact_v1"}', encoding="utf-8"
    )
    runtime_payload["sealed_l2_artifact_ref"] = "sealed_l2_artifact.json"
    refresh_section_exit_after_x3_change(
        tmp_path,
        section_id="competencies",
        runtime_payload=runtime_payload,
        x3_doc={"x3_code": "X3_ALLOW", "pass": True},
    )
    mock_pipeline_cls.return_value.run.assert_called_once()
    mock_exit_hooks.assert_called_once()
