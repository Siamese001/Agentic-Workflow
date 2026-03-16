"""
§1-Compliant tests for execute_ssot.py healing routing — tier decision matrix.

Coverage per §1.1 Required test dimensions:
  - Edge cases: boundary confidence values, FAIL_CLOSED, null reasoning, all exception types
  - State transitions: DETERMINISTIC / QWEN-approved / QWEN-declined / GEMINI / FAIL_CLOSED
  - Determinism: identical input → identical output, replay independence
  - Fail-closed: FAIL_CLOSED tier blocks regardless of confidence
  - Matrix: tier × enable_llm × confidence × Qwen-result × exception-type
  - Regression: minimal reproducer for each of the 5 bug fixes + adjacent near-miss

§1.2: No random inputs, no time-dependent behaviour, deterministic mocks only.
§1.2 mutation-sensitive: assertions MUST fail if guard clauses are removed or
comparisons flip (verified by comment where applicable).
"""

from __future__ import annotations

from typing import Any
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

_emit_records_execution_trace("p0", "evidence", "test_execute_ssot_routing_matrix")
_emit_applies_guardrail("p0", "test_execute_ssot_routing_matrix", "p0_governance")
_emit_reads_policy_state("p0", "test_execute_ssot_routing_matrix", "policy_binding")
_emit_snapshots_state("p0", "test_execute_ssot_routing_matrix", "state_snapshot")
emit_replay_key("p0", "test_execute_ssot_routing_matrix")
emit_determinism_digest("p0", "test_execute_ssot_routing_matrix")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execute_ssot_routing_matrix", "execution_auth")
_emit_validates_capability("p2", "test_execute_ssot_routing_matrix", "capability_check")
_emit_routes_to_capability("p2", "test_execute_ssot_routing_matrix", "capability_route")
_emit_writes_via_uwg("p2", "test_execute_ssot_routing_matrix", "uwg_write")
_emit_blocks_direct_write("p2", "test_execute_ssot_routing_matrix", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execute_ssot_routing_matrix", "tool_invocation")
_emit_captures_execution_output("p2", "test_execute_ssot_routing_matrix", "exec_output")
_emit_dispatches_agent("p3", "test_execute_ssot_routing_matrix", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execute_ssot_routing_matrix", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execute_ssot_routing_matrix", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execute_ssot_routing_matrix", "healing_outcome")
_emit_escalates_failure("p3", "test_execute_ssot_routing_matrix", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execute_ssot_routing_matrix", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execute_ssot_routing_matrix", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execute_ssot_routing_matrix", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execute_ssot_routing_matrix", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execute_ssot_routing_matrix", "eval_metric")
_emit_stores_embedding("p4", "test_execute_ssot_routing_matrix", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execute_ssot_routing_matrix", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execute_ssot_routing_matrix", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_CONF_X = 0.80  # SSOT constant — deterministic tier boundary
_CONF_Y = 0.50  # SSOT constant — deterministic tier boundary


def _make_confidence(value: float, reasoning: str = "test_violation") -> MagicMock:
    """Return a deterministic mock ConfidenceScore."""
    m = MagicMock()
    m.value = value
    m.reasoning = reasoning
    return m


_agent_counter = 0


def _fresh_agent() -> str:
    """Return a globally unique agent name — prevents cycle-detection false positives."""
    global _agent_counter
    _agent_counter += 1
    return f"test_agent_{_agent_counter}"


def _make_engine(*, enable_llm: bool = True, auto_approve: bool = False):
    from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

    return AutonomousDecisionEngine(enable_llm=enable_llm, auto_approve=auto_approve)


def _qwen_returns(decision: bool, reason: str = "test") -> Any:
    """Qwen arbiter that returns a fixed deterministic decision."""

    def _arbiter(*args, **kwargs):
        return {"decision": decision, "reason": reason}

    return _arbiter


# ---------------------------------------------------------------------------
# §1.1 State transitions — all 4 routing tiers
# ---------------------------------------------------------------------------


class TestRoutingTierStateTransitions:
    """Every tier transition path must be reachable and produce a distinct, deterministic result."""

    def test_deterministic_tier_returns_true(self):
        """conf > 0.80 → DETERMINISTIC → approved=True, model=deterministic-sovereign."""
        engine = _make_engine()
        conf = _make_confidence(0.85)
        approved, reason = engine.should_proceed_with_healing(
            conf, agent_name=_fresh_agent(), territory="test_territory"
        )
        assert approved is True
        assert "SOVEREIGN-AUTO" in reason
        assert engine.decisions_made[-1]["model"] == "deterministic-sovereign"

    def test_qwen_tier_approved_returns_true(self):
        """0.50 < conf ≤ 0.80 + Qwen returns True → approved=True."""
        engine = _make_engine()
        conf = _make_confidence(0.65)
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(True, "looks safe")):
            approved, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        assert approved is True
        assert "LLM-ARBITRATED-QWEN14B" in reason

    def test_qwen_tier_declined_returns_false(self):
        """0.50 < conf ≤ 0.80 + Qwen returns False → approved=False, QWEN14B-DECLINED in reason."""
        engine = _make_engine()
        conf = _make_confidence(0.65)
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False, "unsafe")):
            approved, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        assert approved is False
        assert "QWEN14B-DECLINED" in reason
        assert "agent logic governs" in reason

    def test_fail_closed_tier_always_returns_false(self):
        """FAIL_CLOSED routing tier → approved=False regardless of confidence."""
        from agentic_core.L0_routing.scripts.execute_ssot import RoutingTier

        engine = _make_engine()
        conf = _make_confidence(0.99)  # even maximum confidence
        # Inject FAIL_CLOSED routing decision via _route_decision (the internal method)
        mock_routing = MagicMock()
        mock_routing.tier = RoutingTier.FAIL_CLOSED
        mock_routing.gate_applied = "FORCED_FAIL"
        mock_routing.score = 0
        with patch.object(engine, "_route_decision", return_value=mock_routing):
            approved, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        assert approved is False
        assert "FAIL-CLOSED" in reason

    def test_gemini_tier_with_llm_enabled_returns_true(self):
        """conf ≤ 0.50 + enable_llm=True → Gemini tier → approved=True."""
        engine = _make_engine(enable_llm=True)
        conf = _make_confidence(0.40)
        approved, reason = engine.should_proceed_with_healing(
            conf, agent_name=_fresh_agent(), territory="test_territory"
        )
        assert approved is True
        assert "LLM-ARBITRATED" in reason or "GEMINI" in reason or "RECOVERY-PRO" in reason

    def test_gemini_tier_with_llm_disabled_returns_false(self):
        """conf ≤ 0.50 + enable_llm=False → manual review required → approved=False."""
        engine = _make_engine(enable_llm=False)
        conf = _make_confidence(0.40)
        approved, reason = engine.should_proceed_with_healing(
            conf, agent_name=_fresh_agent(), territory="test_territory"
        )
        assert approved is False
        assert "Manual Review Required" in reason
        assert "LLM disabled" in reason


# ---------------------------------------------------------------------------
# §1.1 Edge cases — boundary confidence values
# ---------------------------------------------------------------------------


class TestConfidenceBoundaryEdgeCases:
    """Boundary values per §1.1 — mutations to comparisons must flip these tests."""

    def test_conf_exactly_at_x_threshold_routes_to_qwen_not_deterministic(self):
        """conf == _CONF_X (0.80) — NOT > _CONF_X → should be QWEN tier, not DETERMINISTIC.

        Mutation-sensitive: if '>' were changed to '>=' this test would fail.
        """
        engine = _make_engine()
        conf = _make_confidence(_CONF_X)  # exactly 0.80
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
            approved, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        # Must NOT be DETERMINISTIC (which returns True with SOVEREIGN-AUTO)
        assert "SOVEREIGN-AUTO" not in reason
        assert engine.decisions_made[-1]["model"] != "deterministic-sovereign"

    def test_conf_just_above_x_threshold_routes_to_deterministic(self):
        """conf = 0.801 > _CONF_X → DETERMINISTIC.

        Adjacent near-miss: 0.800 must not be DETERMINISTIC, 0.801 must be.
        """
        engine = _make_engine()
        conf = _make_confidence(0.801)
        approved, reason = engine.should_proceed_with_healing(
            conf, agent_name=_fresh_agent(), territory="test_territory"
        )
        assert approved is True
        assert "SOVEREIGN-AUTO" in reason

    def test_conf_exactly_at_y_threshold_routes_to_gemini_not_qwen(self):
        """conf == _CONF_Y (0.50) — NOT > _CONF_Y → should be GEMINI, not QWEN.

        Regression for Fix #3 (was '<' instead of '<='): conf==0.50 with
        enable_llm=False must produce Manual Review Required.
        Mutation-sensitive: changing '<=' to '<' would cause this to pass Gemini
        block to LLM invocation instead.
        """
        engine = _make_engine(enable_llm=False)
        conf = _make_confidence(_CONF_Y)  # exactly 0.50
        approved, reason = engine.should_proceed_with_healing(
            conf, agent_name=_fresh_agent(), territory="test_territory"
        )
        assert approved is False
        assert "Manual Review Required" in reason
        # Must NOT have routed to QWEN
        assert "QWEN14B" not in reason

    def test_conf_just_above_y_threshold_routes_to_qwen_not_gemini(self):
        """conf = 0.501 > _CONF_Y → QWEN tier, not Gemini.

        Adjacent near-miss: 0.500 → GEMINI, 0.501 → QWEN.
        """
        engine = _make_engine(enable_llm=False)
        conf = _make_confidence(0.501)
        # Qwen will raise RuntimeError (WSL absent) → declined → approved=False
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
            approved, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        # Should be QWEN-declined, NOT Manual Review Required
        assert "Manual Review Required" not in reason
        assert "QWEN14B-DECLINED" in reason or engine.decisions_made[-1].get("model", "").startswith("Qwen")

    def test_conf_zero_routes_to_gemini(self):
        """conf = 0.0 (minimum) → GEMINI tier."""
        engine = _make_engine(enable_llm=True)
        conf = _make_confidence(0.0)
        approved, reason = engine.should_proceed_with_healing(
            conf, agent_name=_fresh_agent(), territory="test_territory"
        )
        assert approved is True
        assert "RECOVERY-PRO" in reason  # < 0.40 → RECOVERY-PRO label

    def test_conf_one_routes_to_deterministic(self):
        """conf = 1.0 (maximum) → DETERMINISTIC tier."""
        engine = _make_engine()
        conf = _make_confidence(1.0)
        approved, reason = engine.should_proceed_with_healing(
            conf, agent_name=_fresh_agent(), territory="test_territory"
        )
        assert approved is True
        assert "SOVEREIGN-AUTO" in reason


# ---------------------------------------------------------------------------
# §1.1 Exception matrix — all exception types caught in Qwen except clause
# ---------------------------------------------------------------------------


class TestQwenExceptionMatrix:
    """Every exception in the tuple must be caught; approved defaults to False.

    Regression for Fix #1: RuntimeError was previously NOT in the except clause,
    causing silent approved=True on WSL/vLLM failure.
    """

    @pytest.mark.parametrize(
        "exc_type,exc_msg",
        [
            (RuntimeError, "vLLM subprocess exited with code 1"),
            (OSError, "WSL binary not found"),
            (TimeoutError, "subprocess timed out after 30s"),
            (ImportError, "no module named qwen_invoker"),
            (AttributeError, "arbiter has no attribute invoke"),
            (ValueError, "JSON decode failed"),
            (KeyError, "missing key in vllm_result"),
        ],
    )
    def test_qwen_exception_caught_defaults_to_declined(self, exc_type, exc_msg):
        """All 7 exception types must be caught → qwen_approved=False → returns False."""
        engine = _make_engine()
        conf = _make_confidence(0.65)

        def _failing_arbiter(*args, **kwargs):
            raise exc_type(exc_msg)

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_failing_arbiter):
            approved, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )

        assert approved is False, (
            f"{exc_type.__name__} must be caught and default to declined (approved=False), "
            f"got approved={approved}. Reason: {reason}"
        )
        assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason

    def test_qwen_exception_does_not_leave_approved_true(self):
        """qwen_approved must start True but be set to False after any exception.

        Mutation-sensitive: if 'qwen_approved = False' were removed from the
        except block, this test would catch approved=True.
        """
        engine = _make_engine()
        conf = _make_confidence(0.65)

        def _runtime_error(*args, **kwargs):
            raise RuntimeError("WSL not available")

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_runtime_error):
            approved, _ = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )

        assert approved is False  # MUST be False, not the initial True default

    def test_unhandled_exception_type_not_swallowed(self):
        """Exception types NOT in the tuple (e.g. MemoryError) must propagate."""
        engine = _make_engine()
        conf = _make_confidence(0.65)

        def _memory_error(*args, **kwargs):
            raise MemoryError("OOM")

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_memory_error):
            with pytest.raises(MemoryError):
                engine.should_proceed_with_healing(
                    conf, agent_name=_fresh_agent(), territory="test_territory"
                )


# ---------------------------------------------------------------------------
# §1.1 Matrix: enable_llm × confidence × tier
# ---------------------------------------------------------------------------


class TestEnableLLMConfidenceMatrix:
    """Interaction gate: feature flag (enable_llm) × confidence tier.

    §1.1 Matrix requirement: test all interacting gates.
    """

    @pytest.mark.parametrize(
        "conf_val,enable_llm,expected_approved,desc",
        [
            # Deterministic tier — enable_llm has NO effect
            (0.85, True, True, "det+llm_on"),
            (0.85, False, True, "det+llm_off → still auto-approved"),
            # QWEN tier — enable_llm has NO effect on routing (Qwen is WSL, not LLM flag)
            # Qwen will be mocked to return True
            (0.65, True, True, "qwen+llm_on+qwen_approved"),
            # Gemini tier — enable_llm=True → Gemini approves; enable_llm=False → blocked
            (0.40, True, True, "gemini+llm_on"),
            (0.40, False, False, "gemini+llm_off → manual review"),
            (0.50, False, False, "boundary=0.50+llm_off → manual review"),
        ],
    )
    def test_matrix(self, conf_val, enable_llm, expected_approved, desc):
        engine = _make_engine(enable_llm=enable_llm)
        conf = _make_confidence(conf_val)
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(True)):
            approved, _ = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        assert approved is expected_approved, f"[{desc}] expected {expected_approved}, got {approved}"


# ---------------------------------------------------------------------------
# §1.1 SSOT constants — no os.getenv leaks (Fix #2)
# ---------------------------------------------------------------------------


class TestSSOTModelIDDeterminism:
    """Qwen and Gemini model IDs must come from SSOT constants, not os.getenv.

    Regression for Fix #2: os.getenv calls were replaced with SSOT constants.
    Mutation-sensitive: if os.getenv is reintroduced, the env-cleared test fails.
    """

    def test_qwen_model_id_is_ssot_constant_not_env(self):
        """Qwen model ID in decision_data must equal the SSOT constant value."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_MODEL_ID

        engine = _make_engine()
        conf = _make_confidence(0.65)
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
            engine.should_proceed_with_healing(conf, agent_name=_fresh_agent(), territory="test_territory")
        assert engine.decisions_made[-1]["model"] == QWEN_14B_MODEL_ID

    def test_qwen_model_id_unaffected_by_env_var(self):
        """Unsetting QWEN_14B_MODEL env var must not change the model ID used."""
        import os

        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_MODEL_ID

        saved = os.environ.pop("QWEN_14B_MODEL", None)
        try:
            engine = _make_engine()
            conf = _make_confidence(0.65)
            with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
                engine.should_proceed_with_healing(
                    conf, agent_name=_fresh_agent(), territory="test_territory"
                )
            assert engine.decisions_made[-1]["model"] == QWEN_14B_MODEL_ID
        finally:
            if saved is not None:
                os.environ["QWEN_14B_MODEL"] = saved

    def test_gemini_model_id_is_hardcoded_ssot_not_env(self):
        """Gemini model ID in decision_data must be 'gemini-2.5-pro' (SSOT)."""
        import os

        saved = os.environ.pop("GEMINI_MODEL", None)
        try:
            engine = _make_engine(enable_llm=True)
            conf = _make_confidence(0.40)
            engine.should_proceed_with_healing(conf, agent_name=_fresh_agent(), territory="test_territory")
            assert engine.decisions_made[-1]["model"] == "gemini-2.5-pro"
        finally:
            if saved is not None:
                os.environ["GEMINI_MODEL"] = saved

    def test_env_var_injection_cannot_override_ssot_model(self):
        """Setting QWEN_14B_MODEL env var to a different value must NOT affect routing."""
        import os

        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_MODEL_ID

        os.environ["QWEN_14B_MODEL"] = "injected-malicious-model"
        try:
            engine = _make_engine()
            conf = _make_confidence(0.65)
            with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
                engine.should_proceed_with_healing(
                    conf, agent_name=_fresh_agent(), territory="test_territory"
                )
            # SSOT constant must win, not the env var
            assert engine.decisions_made[-1]["model"] == QWEN_14B_MODEL_ID
            assert engine.decisions_made[-1]["model"] != "injected-malicious-model"
        finally:
            del os.environ["QWEN_14B_MODEL"]


# ---------------------------------------------------------------------------
# §1.1 Determinism — identical input → identical output
# ---------------------------------------------------------------------------


class TestRoutingDeterminism:
    """§1.1 Determinism: same inputs must always produce the same outputs."""

    def test_deterministic_tier_is_idempotent(self):
        """Two engines with identical conf > 0.80 must produce identical results.

        Note: each call uses a fresh engine to avoid cycle-detection false positives.
        """
        agent = _fresh_agent()
        engine_a = _make_engine()
        engine_b = _make_engine()
        approved_a, reason_a = engine_a.should_proceed_with_healing(
            _make_confidence(0.90), agent_name=agent, territory="test_territory"
        )
        approved_b, reason_b = engine_b.should_proceed_with_healing(
            _make_confidence(0.90), agent_name=agent, territory="test_territory"
        )
        assert approved_a == approved_b
        # Reasons match except for the timestamp field — strip it for comparison
        import re

        def _strip_ts(s: str) -> str:
            return re.sub(r"\d{4}-\d{2}-\d{2}T[\d:.]+", "TS", s)

        assert _strip_ts(reason_a) == _strip_ts(reason_b)

    def test_qwen_decline_is_idempotent(self):
        """Same Qwen-declined conf must produce same result on repeated calls.

        Each call uses its own fresh engine + unique agent to avoid cycle-detection.
        """
        results = []
        for _ in range(3):
            e = _make_engine()
            conf = _make_confidence(0.65)
            with patch.object(e, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False, "unsafe")):
                results.append(
                    e.should_proceed_with_healing(conf, agent_name=_fresh_agent(), territory="test_territory")
                )
        # All approved flags must be identical (False)
        assert all(r[0] == results[0][0] for r in results)

    def test_decision_data_model_field_deterministic_across_runs(self):
        """decision_data['model'] for QWEN tier must be identical across runs."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_MODEL_ID

        models = []
        for _ in range(3):
            engine = _make_engine()
            conf = _make_confidence(0.65)
            with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
                engine.should_proceed_with_healing(
                    conf, agent_name=_fresh_agent(), territory="test_territory"
                )
            models.append(engine.decisions_made[-1]["model"])
        assert len(set(models)) == 1  # all identical
        assert models[0] == QWEN_14B_MODEL_ID

    def test_gemini_label_recovery_pro_below_040(self):
        """conf < 0.40 → RECOVERY-PRO label (deterministic label assignment)."""
        for conf_val in [0.0, 0.10, 0.20, 0.39]:
            engine = _make_engine(enable_llm=True)
            conf = _make_confidence(conf_val)
            _, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
            assert "RECOVERY-PRO" in reason, f"conf={conf_val} should produce RECOVERY-PRO, got: {reason}"

    def test_gemini_label_gemini_at_040_to_050(self):
        """0.40 ≤ conf ≤ 0.50 with llm enabled → GEMINI label (not RECOVERY-PRO)."""
        for conf_val in [0.40, 0.45]:
            engine = _make_engine(enable_llm=True)
            conf = _make_confidence(conf_val)
            _, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
            assert "RECOVERY-PRO" not in reason, f"conf={conf_val} should NOT produce RECOVERY-PRO"
            assert "LLM-ARBITRATED" in reason


# ---------------------------------------------------------------------------
# §1.1 Qwen decision_data contents — state written correctly
# ---------------------------------------------------------------------------


class TestDecisionDataContents:
    """decision_data dict must have correct contents for each tier."""

    def test_deterministic_tier_decision_data(self):
        """DETERMINISTIC tier: decision=True, model=deterministic-sovereign, routing_tier=DETERMINISTIC."""
        engine = _make_engine()
        conf = _make_confidence(0.90)
        engine.should_proceed_with_healing(conf, agent_name=_fresh_agent(), territory="test_territory")
        d = engine.decisions_made[-1]
        assert d["decision"] is True
        assert d["model"] == "deterministic-sovereign"
        assert d["routing_tier"] == "DETERMINISTIC"

    def test_qwen_declined_decision_data(self):
        """QWEN-declined: decision=False, model=SSOT Qwen ID, routing_tier=QWEN."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_MODEL_ID

        engine = _make_engine()
        conf = _make_confidence(0.65)
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
            engine.should_proceed_with_healing(conf, agent_name=_fresh_agent(), territory="test_territory")
        d = engine.decisions_made[-1]
        assert d["decision"] is False
        assert d["model"] == QWEN_14B_MODEL_ID
        assert d["routing_tier"] == "QWEN"

    def test_gemini_blocked_decision_data(self):
        """GEMINI+llm_disabled: decision=False, model=gemini-2.5-pro, routing_tier=GEMINI."""
        engine = _make_engine(enable_llm=False)
        conf = _make_confidence(0.40)
        engine.should_proceed_with_healing(conf, agent_name=_fresh_agent(), territory="test_territory")
        d = engine.decisions_made[-1]
        assert d["decision"] is False
        assert d["model"] == "gemini-2.5-pro"
        assert d["routing_tier"] == "GEMINI"

    def test_fail_closed_decision_data(self):
        """FAIL_CLOSED: decision=False, always."""
        from agentic_core.L0_routing.scripts.execute_ssot import RoutingTier

        engine = _make_engine()
        conf = _make_confidence(0.99)
        mock_routing = MagicMock()
        mock_routing.tier = RoutingTier.FAIL_CLOSED
        mock_routing.gate_applied = "FORCED_FAIL"
        mock_routing.score = 0
        with patch.object(engine, "_route_decision", return_value=mock_routing):
            engine.should_proceed_with_healing(conf, agent_name=_fresh_agent(), territory="test_territory")
        d = engine.decisions_made[-1]
        assert d["decision"] is False


# ---------------------------------------------------------------------------
# §1.1 Qwen result parsing edge cases
# ---------------------------------------------------------------------------


class TestQwenResultParsing:
    """Edge cases in parsing Qwen's vllm_result dict."""

    def test_qwen_missing_decision_key_defaults_to_approved(self):
        """vllm_result without 'decision' key → .get('decision', True) → approved=True."""
        engine = _make_engine()
        conf = _make_confidence(0.65)

        def _no_decision_key(*args, **kwargs):
            return {"reason": "some reason but no decision key"}

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_no_decision_key):
            approved, _ = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        assert approved is True  # default=True per the .get() call

    def test_qwen_empty_dict_defaults_to_approved(self):
        """Empty vllm_result → .get('decision', True) → approved=True."""
        engine = _make_engine()
        conf = _make_confidence(0.65)

        def _empty_result(*args, **kwargs):
            return {}

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_empty_result):
            approved, _ = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        assert approved is True

    def test_qwen_reason_truncated_to_120_chars(self):
        """Qwen raw_reason is capped at [:120] chars in the final reason string."""
        engine = _make_engine()
        conf = _make_confidence(0.65)
        long_reason = "X" * 200  # 200 chars — must be truncated to 120

        def _long_reason(*args, **kwargs):
            return {"decision": True, "reason": long_reason}

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_long_reason):
            _, reason = engine.should_proceed_with_healing(
                conf, agent_name=_fresh_agent(), territory="test_territory"
            )
        # The embedded reason should not exceed 120 Xs
        assert "X" * 121 not in reason
        assert "X" * 120 in reason or "X" * 119 in reason  # within cap


# ---------------------------------------------------------------------------
# §1.1 Replay / state independence
# ---------------------------------------------------------------------------


class TestReplayIndependence:
    """§1.1 Determinism: engine state must not contaminate subsequent calls."""

    def test_healing_count_increments_per_approval(self):
        """_healing_count increments only on approved decisions."""
        engine = _make_engine()
        assert engine._healing_count == 0

        # Approved: DETERMINISTIC (unique agent to avoid cycle detection)
        engine.should_proceed_with_healing(_make_confidence(0.90), agent_name=_fresh_agent(), territory="t")
        assert engine._healing_count == 1

        # Not approved: QWEN-declined (unique agent)
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
            engine.should_proceed_with_healing(
                _make_confidence(0.65), agent_name=_fresh_agent(), territory="t"
            )
        assert engine._healing_count == 1  # no increment for declined

    def test_call_path_tracks_approved_agents_only(self):
        """_call_path records agent_name only for approved decisions."""
        engine = _make_engine()
        approved_agent = _fresh_agent()
        declined_agent = _fresh_agent()
        engine.should_proceed_with_healing(_make_confidence(0.90), agent_name=approved_agent, territory="t")
        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
            engine.should_proceed_with_healing(
                _make_confidence(0.65), agent_name=declined_agent, territory="t"
            )

        assert approved_agent in engine._call_path
        assert declined_agent not in engine._call_path

    def test_decisions_made_appended_for_every_call(self):
        """decisions_made accumulates one entry per call, regardless of outcome."""
        engine = _make_engine()
        for _ in range(3):
            with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=_qwen_returns(False)):
                engine.should_proceed_with_healing(
                    _make_confidence(0.65), agent_name=_fresh_agent(), territory="t"
                )
        assert len(engine.decisions_made) == 3
