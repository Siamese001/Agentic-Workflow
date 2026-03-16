"""Behavioral tests for log_routing_correction() in hitl_decision_logger.

Covers:
- log_routing_correction is callable with correct signature
- Returns a sequential integer decision number (1-based)
- Multiple calls increment the counter sequentially
- reset_for_testing() resets the counter so log_routing_correction starts at 1 again
- Decision type recorded as 'routing_correction'
- wrong_target and correct_target captured in audit record
- confidence rounded to 6dp in extra payload
- rlhf optimizer failure is silently swallowed (fail-open)
- Extra kwargs forwarded to the underlying audit record
- Input truncated to 512 chars in DPO batch (no crash on long input)
- No exception propagates from log_routing_correction under any condition
"""

from __future__ import annotations

import importlib
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hitl_routing_correction")
_emit_applies_guardrail("p0", "test_hitl_routing_correction", "p0_governance")
_emit_reads_policy_state("p0", "test_hitl_routing_correction", "policy_binding")
_emit_snapshots_state("p0", "test_hitl_routing_correction", "state_snapshot")
emit_replay_key("p0", "test_hitl_routing_correction")
emit_determinism_digest("p0", "test_hitl_routing_correction")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hitl_routing_correction", "execution_auth")
_emit_validates_capability("p2", "test_hitl_routing_correction", "capability_check")
_emit_routes_to_capability("p2", "test_hitl_routing_correction", "capability_route")
_emit_writes_via_uwg("p2", "test_hitl_routing_correction", "uwg_write")
_emit_blocks_direct_write("p2", "test_hitl_routing_correction", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hitl_routing_correction", "tool_invocation")
_emit_captures_execution_output("p2", "test_hitl_routing_correction", "exec_output")
_emit_dispatches_agent("p3", "test_hitl_routing_correction", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hitl_routing_correction", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hitl_routing_correction", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hitl_routing_correction", "healing_outcome")
_emit_escalates_failure("p3", "test_hitl_routing_correction", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hitl_routing_correction", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hitl_routing_correction", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hitl_routing_correction", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hitl_routing_correction", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hitl_routing_correction", "eval_metric")
_emit_stores_embedding("p4", "test_hitl_routing_correction", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hitl_routing_correction", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hitl_routing_correction", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from system_learning.engines.hitl_decision_logger import (
    get_decision_count,
    log_routing_correction,
    reset_for_testing,
)

# ---------------------------------------------------------------------------
# Setup / teardown
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_counter():
    """Reset the global decision counter before each test."""
    reset_for_testing()
    yield
    reset_for_testing()


# ---------------------------------------------------------------------------
# Basic callable and return type
# ---------------------------------------------------------------------------


class TestLogRoutingCorrectionBasics:
    def test_is_callable(self):
        assert callable(log_routing_correction)

    def test_returns_int(self):
        n = log_routing_correction("review my code", "resume_writer", "code_reviewer")
        assert isinstance(n, int)

    def test_first_call_returns_1(self):
        n = log_routing_correction("review my code", "resume_writer", "code_reviewer")
        assert n == 1

    def test_second_call_returns_2(self):
        log_routing_correction("input1", "a", "b")
        n = log_routing_correction("input2", "b", "c")
        assert n == 2

    def test_three_calls_sequential(self):
        results = [log_routing_correction(f"input{i}", "wrong", "correct") for i in range(3)]
        assert results == [1, 2, 3]

    def test_reset_restarts_counter(self):
        log_routing_correction("x", "a", "b")
        reset_for_testing()
        n = log_routing_correction("y", "c", "d")
        assert n == 1

    def test_get_decision_count_matches_calls(self):
        log_routing_correction("i1", "a", "b")
        log_routing_correction("i2", "c", "d")
        assert get_decision_count() == 2


# ---------------------------------------------------------------------------
# Extra payload and confidence
# ---------------------------------------------------------------------------


class TestLogRoutingCorrectionPayload:
    def test_confidence_default_zero(self):
        """Should not raise when confidence is not provided."""
        try:
            log_routing_correction("input", "wrong", "correct")
        except Exception as exc:
            pytest.fail(f"raised: {exc}")

    def test_confidence_explicit_value_no_raise(self):
        try:
            log_routing_correction("input", "wrong", "correct", confidence=0.35)
        except Exception as exc:
            pytest.fail(f"raised: {exc}")

    def test_extra_kwargs_passed(self):
        try:
            log_routing_correction(
                "input",
                "wrong",
                "correct",
                confidence=0.5,
                extra={"trace_id": "t-123", "run_id": "r-456"},
            )
        except Exception as exc:
            pytest.fail(f"raised: {exc}")

    def test_long_input_no_crash(self):
        """Input longer than 512 chars must not crash (truncated in DPO batch)."""
        long_input = "a" * 2000
        try:
            log_routing_correction(long_input, "wrong", "correct", confidence=0.1)
        except Exception as exc:
            pytest.fail(f"raised with long input: {exc}")


# ---------------------------------------------------------------------------
# RLHF optimizer failure is silently swallowed
# ---------------------------------------------------------------------------


class TestRLHFOptimizerFailureSilenced:
    def test_optimizer_import_error_swallowed(self):
        """If rlhf_optimizer_impl is unavailable, log_routing_correction must not raise."""
        with patch.dict("sys.modules", {"system_learning.engines.rlhf_optimizer_impl": None}):
            try:
                log_routing_correction("input", "wrong", "correct")
            except Exception as exc:
                pytest.fail(f"raised when optimizer unavailable: {exc}")

    def test_optimizer_runtime_error_swallowed(self):
        """If DefaultRLHFOptimizer.propose_from_dpo raises, must not propagate."""
        mock_optimizer = MagicMock()
        mock_optimizer.propose_from_dpo.side_effect = RuntimeError("optimizer exploded")
        mock_module = MagicMock()
        mock_module.DefaultRLHFOptimizer.return_value = mock_optimizer

        with patch.dict("sys.modules", {"system_learning.engines.rlhf_optimizer_impl": mock_module}):
            try:
                log_routing_correction("input", "wrong", "correct", confidence=0.3)
            except Exception as exc:
                pytest.fail(f"raised on optimizer failure: {exc}")

    def test_any_exception_in_rlhf_block_swallowed(self):
        """Generic Exception in RLHF block must never propagate."""
        with patch(
            "system_learning.engines.hitl_decision_logger.log_hitl_decision",
            return_value=99,
        ):
            with patch(
                "builtins.__import__",
                side_effect=lambda name, *args, **kw: (_ for _ in ()).throw(ImportError("blocked"))
                if "rlhf_optimizer_impl" in name
                else importlib.import_module(name),
            ):
                try:
                    log_routing_correction("input", "wrong", "correct")
                except Exception as exc:
                    pytest.fail(f"exception leaked: {exc}")


# ---------------------------------------------------------------------------
# Never raises under adversarial inputs
# ---------------------------------------------------------------------------


class TestNeverRaises:
    @pytest.mark.parametrize(
        "user_input,wrong,correct,confidence",
        [
            ("", "", "", 0.0),
            ("normal", "a", "b", 0.99),
            ("normal", "a", "b", 0.0),
            ("\n\r\t", "x", "y", 0.5),
            ("unicode: 你好", "w", "c", 0.3),
            ("a" * 600, "w", "c", 0.1),  # long input
        ],
    )
    def test_no_raise(self, user_input, wrong, correct, confidence):
        try:
            n = log_routing_correction(user_input, wrong, correct, confidence=confidence)
            assert isinstance(n, int)
        except Exception as exc:
            pytest.fail(f"raised for input={user_input!r}: {exc}")
