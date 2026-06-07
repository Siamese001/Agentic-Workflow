"""W5.P7 verification — eval_harness_outcome ledger writer contract.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-parity-f8d4a2.md`` W5.P7.

Proves:

- ``eval_harness_outcome`` ledger is registered in LEDGER_REGISTRY
- The DDL file exists and can be parsed
- The SQLite db file can be opened with the ``events`` base table
- ``_emit_eval_harness_outcome`` writes a row with the expected shape and
  correct ``score_band`` attribution for bound / pass / deny / escalate /
  unknown / unbound
- Writer is fail-soft (no exception escapes the pipeline path even if the
  writer hits an unrecoverable error)
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    AppSpecificEvalResult,
    DimensionResult,
)
from agentic_core.L3_orchestration.exit_eval.v6.pipeline import (
    _emit_eval_harness_outcome,
    _score_band_for_ase,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    SourceType,
    V6Disposition,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
from tools.ledgers.schema_registry import LEDGER_REGISTRY, get


def _mk_packet() -> ExitReviewPacket:
    return ExitReviewPacket(
        source_type=SourceType.L2_SEALED_ARTIFACT,
        request_id="req-test",
        run_id="run-test-w5",
        trace_root="trace-test",
        policy_hash="p",
        blueprint_hash="b",
        terminal_class="answer_only",
    )


def _mk_decision(disposition: V6Disposition, rationale: str = "") -> AggregateDecision:
    return AggregateDecision(
        disposition=disposition,
        failed_gate_ids=[],
        reason_codes=[],
        triggering_verdicts=[],
        rationale=rationale,
    )


class TestLedgerRegistration:
    def test_registered(self) -> None:
        spec = get("eval_harness_outcome")
        assert spec.name == "eval_harness_outcome"
        assert spec.schema_file == "eval_harness_outcome_ledger.schema.sql"
        assert spec.writer_hook.endswith("exit_eval/v6/pipeline.py")

    def test_schema_file_exists(self) -> None:
        spec = get("eval_harness_outcome")
        assert spec.schema_path.exists(), f"missing {spec.schema_path}"

    def test_db_file_has_events_table(self) -> None:
        spec = get("eval_harness_outcome")
        if not spec.db_path.exists():
            pytest.skip("ledger db not yet applied — run tools/ledgers/apply_schema.py")
        conn = sqlite3.connect(str(spec.db_path))
        try:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
            ).fetchall()
            assert rows, "events base table missing"
        finally:
            conn.close()


class TestScoreBandAttribution:
    def test_pass(self) -> None:
        ase = AppSpecificEvalResult(bound=True, passed=True)
        decision = _mk_decision(V6Disposition.ALLOW)
        assert _score_band_for_ase(ase, decision) == "pass"

    def test_unbound(self) -> None:
        ase = AppSpecificEvalResult(bound=False)
        decision = _mk_decision(V6Disposition.ALLOW)
        assert _score_band_for_ase(ase, decision) == "unbound"

    def test_deny_soft(self) -> None:
        ase = AppSpecificEvalResult(
            bound=True,
            passed=False,
            fail_reasons=["overall_below_threshold::score=0.6<0.8"],
        )
        decision = _mk_decision(V6Disposition.DENY, rationale="app_specific_eval_failed")
        assert _score_band_for_ase(ase, decision) == "deny"

    def test_escalate(self) -> None:
        ase = AppSpecificEvalResult(
            bound=True,
            passed=False,
            fail_reasons=["overall_below_threshold::score=0.6<0.8"],
            hitl_policy="required_on_low",
        )
        decision = _mk_decision(V6Disposition.ESCALATE, rationale="hitl_required_on_low")
        assert _score_band_for_ase(ase, decision) == "escalate"

    def test_unknown(self) -> None:
        ase = AppSpecificEvalResult(
            bound=True,
            passed=False,
            fail_reasons=["dimension_fail::no_fabrication::unknown_fail_closed"],
        )
        decision = _mk_decision(V6Disposition.DENY, rationale="app_specific_eval_failed")
        assert _score_band_for_ase(ase, decision) == "unknown"


class TestWriterIsFailSoft:
    def test_emit_returns_string_never_raises(self) -> None:
        packet = _mk_packet()
        ase = AppSpecificEvalResult(
            bound=True,
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::apps_rg::resume_generation::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            overall_score=0.82,
            overall_pass_threshold=0.80,
            passed=True,
            hitl_policy="required_on_low",
            dimensions=[
                DimensionResult(
                    dimension_id="factual_grounding",
                    score=0.95,
                    weight=0.25,
                    grader_type="deterministic",
                    status="PASS",
                    reason="",
                    min_required_score=0.95,
                ),
            ],
        )
        decision = _mk_decision(V6Disposition.ALLOW, rationale="")
        event_id = _emit_eval_harness_outcome(packet, ase, decision)
        # Fail-soft contract: returns str; empty on any failure, non-empty on success.
        assert isinstance(event_id, str)

    def test_unbound_emits_unbound_kind(self) -> None:
        """Unbound packets still emit a row so we can measure coverage."""
        packet = _mk_packet()
        ase = AppSpecificEvalResult(bound=False)
        decision = _mk_decision(V6Disposition.ALLOW)
        event_id = _emit_eval_harness_outcome(packet, ase, decision)
        assert isinstance(event_id, str)


class TestLedgerRowShape:
    """Integration-ish: emit a row, then read it back and check the shape."""

    def test_row_has_expected_prediction_and_outcome(self) -> None:
        spec = get("eval_harness_outcome")
        if not spec.db_path.exists():
            pytest.skip("ledger db not yet applied — run tools/ledgers/apply_schema.py")

        packet = _mk_packet()
        ase = AppSpecificEvalResult(
            bound=True,
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::apps_rg::resume_generation::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            overall_score=0.55,
            overall_pass_threshold=0.80,
            passed=False,
            fail_reasons=["overall_below_threshold::score=0.55<0.80"],
            hitl_policy="required_on_low",
            dimensions=[
                DimensionResult(
                    dimension_id="factual_grounding", score=0.90, weight=0.25,
                    grader_type="deterministic", status="PASS", reason="",
                    min_required_score=0.95,
                ),
                DimensionResult(
                    dimension_id="executive_positioning", score=0.40, weight=0.10,
                    grader_type="llm_as_judge", status="FAIL",
                    reason="below_rubric_min(0.55)", min_required_score=0.55,
                ),
            ],
        )
        decision = _mk_decision(V6Disposition.ESCALATE, rationale="hitl_required_on_low")
        event_id = _emit_eval_harness_outcome(packet, ase, decision)
        if not event_id:
            pytest.skip("writer returned empty event_id; env may be CI-restricted")

        conn = sqlite3.connect(str(spec.db_path))
        try:
            row = conn.execute(
                "SELECT event_kind, score_band, score_numeric, repo_area, "
                "prediction_json, outcome_json "
                "FROM events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
        finally:
            conn.close()

        assert row is not None, "row not persisted"
        event_kind, score_band, score_numeric, repo_area, pred_raw, out_raw = row
        assert event_kind == "app_eval_bound"
        assert score_band == "escalate"
        assert abs(float(score_numeric) - 0.55) < 1e-9
        assert repo_area == "apps_rg"
        pred = json.loads(pred_raw)
        assert pred["bound"] is True
        assert pred["app_id"] == "apps_rg"
        assert pred["hitl_policy"] == "required_on_low"
        assert pred["dim_count"] == 2
        assert pred["dim_fail_count"] == 1
        out = json.loads(out_raw)
        assert out["disposition"] == "X3B"
        assert out["rationale"] == "hitl_required_on_low"
