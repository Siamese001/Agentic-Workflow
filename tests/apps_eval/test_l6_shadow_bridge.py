from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def test_apps_eval_l6_shadow_bridge_emitted_when_requested(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_lic.dev.outreach_message",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
            emit_l6_handoff=True,
        )
    )

    assert "l6_shadow_bridge" in record.artifact_paths
    assert "l6_shadow_bridge_spans" in record.artifact_paths
    assert "l6_shadow_bridge_spans_jsonl" in record.artifact_paths

    bridge_path = Path(record.artifact_paths["l6_shadow_bridge"])
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))

    assert bridge["record_id"] == record.record_id
    assert bridge["g28_audit_completeness"]["verdict"] == "PASS"
    assert bridge["g29_learning_firewall"]["verdict"] == "PASS"
    assert bridge["current_run_mutated"] is False
    assert Path(record.artifact_paths["l6_shadow_bridge_spans"]).is_file()
    assert Path(record.artifact_paths["l6_shadow_bridge_spans_jsonl"]).is_file()


def test_completed_eval_bridge_keeps_projected_eval_rows_advisory(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
            emit_l6_handoff=True,
        )
    )

    parity_path = Path(record.artifact_paths["l6_apps_eval_grain_parity"])
    parity = json.loads(parity_path.read_text(encoding="utf-8"))

    assert parity["alignment_source"] == "contract_only_pseudo_rows"
    assert parity["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert parity["apps_eval_rows_bound"] is False
    assert parity["grain_parity_status"] == "WARN"
    assert parity["projection_consistency_only"] is True
    assert parity["independent_observations"] is False

    proposals_path = Path(record.artifact_paths["l6_microstep_future_run_proposals"])
    proposals = json.loads(proposals_path.read_text(encoding="utf-8"))
    assert proposals["schema_version"] == "agentic_core.l6_microstep_future_run_proposals.v1"


def test_apps_eval_live_adapter_cannot_disable_l6_handoff(tmp_path: Path) -> None:
    with pytest.raises(PermissionError, match="L6 shadow handoff is required"):
        run_eval(
            EvalRequest(
                suite_id="apps_rg.dev.resume_generation",
                mode="live_adapter",
                deterministic_only=False,
                out_dir=str(tmp_path),
                emit_l6_handoff=False,
            )
        )


def test_apps_eval_release_gate_cannot_disable_l6_handoff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_EVAL_RELEASE_GATE", "1")
    with pytest.raises(PermissionError, match="L6 shadow handoff is required"):
        run_eval(
            EvalRequest(
                suite_id="apps_rg.dev.resume_generation",
                mode="snapshot",
                deterministic_only=True,
                out_dir=str(tmp_path),
                emit_l6_handoff=False,
            )
        )
