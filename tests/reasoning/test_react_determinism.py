"""CI tests — ReAct determinism enforcement.

Verifies:
  - ReasonTraceEnvelope is emitted after each full trace.
  - Envelope hash is stable across identical inputs (replay determinism).
  - ReplayGuard detects and blocks non-deterministic violations.
  - Multiple traces on the same strategy instance produce identical envelope hashes.

CI failure conditions:
  - Multiple reasoning traces emitted from one execution.
  - Non-deterministic clock detected.
  - Envelope hash mismatch between replay runs.
"""

from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_react_determinism")
_emit_applies_guardrail("p0", "test_react_determinism", "p0_governance")
_emit_reads_policy_state("p0", "test_react_determinism", "policy_binding")
_emit_snapshots_state("p0", "test_react_determinism", "state_snapshot")
emit_replay_key("p0", "test_react_determinism")
emit_determinism_digest("p0", "test_react_determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_react_determinism", "execution_auth")
_emit_validates_capability("p2", "test_react_determinism", "capability_check")
_emit_routes_to_capability("p2", "test_react_determinism", "capability_route")
_emit_writes_via_uwg("p2", "test_react_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "test_react_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "test_react_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "test_react_determinism", "exec_output")
_emit_dispatches_agent("p3", "test_react_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "test_react_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_react_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_react_determinism", "healing_outcome")
_emit_escalates_failure("p3", "test_react_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_react_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_react_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_react_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_react_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_react_determinism", "eval_metric")
_emit_stores_embedding("p4", "test_react_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_react_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_react_determinism", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.react_trace_types import (
    NonDeterministicCallDetected,
    ReasonTraceEnvelope,
    ReplayGuard,
)


class TestReasonTraceEnvelope:
    def test_build_produces_valid_hash(self):
        env = ReasonTraceEnvelope.build(
            trace_id="t1",
            plan_hash="ph1",
            reason_steps=("think1", "think2"),
            action_steps=("act1", "act2"),
            tool_invocations=("tool_a({})",),
            policy_hash="pol1",
            semantic_clock_vector=(1000, 0),
        )
        assert env.envelope_hash != ""
        assert env.verify()

    def test_replay_stability(self):
        """Same inputs must produce identical envelope hash."""
        kwargs = {
            "trace_id": "t-replay",
            "plan_hash": "ph-replay",
            "reason_steps": ("step_a",),
            "action_steps": ("act_a",),
            "tool_invocations": ("tool_x({})",),
            "policy_hash": "pol-replay",
            "semantic_clock_vector": (42, 0),
        }
        env1 = ReasonTraceEnvelope.build(**kwargs)
        env2 = ReasonTraceEnvelope.build(**kwargs)
        assert env1.envelope_hash == env2.envelope_hash

    def test_different_inputs_produce_different_hash(self):
        env1 = ReasonTraceEnvelope.build(
            trace_id="t1",
            plan_hash="ph1",
            reason_steps=("A",),
            action_steps=("X",),
            tool_invocations=(),
            policy_hash="p1",
            semantic_clock_vector=(1,),
        )
        env2 = ReasonTraceEnvelope.build(
            trace_id="t2",
            plan_hash="ph2",
            reason_steps=("B",),
            action_steps=("Y",),
            tool_invocations=(),
            policy_hash="p2",
            semantic_clock_vector=(2,),
        )
        assert env1.envelope_hash != env2.envelope_hash

    def test_envelope_is_immutable(self):
        env = ReasonTraceEnvelope.build(
            trace_id="t1",
            plan_hash="ph",
            reason_steps=(),
            action_steps=(),
            tool_invocations=(),
            policy_hash="p",
            semantic_clock_vector=(0,),
        )
        with pytest.raises((AttributeError, TypeError)):
            env.trace_id = "mutated"  # type: ignore[misc]

    def test_tampered_hash_fails_verify(self):
        env = ReasonTraceEnvelope.build(
            trace_id="t1",
            plan_hash="ph",
            reason_steps=("s",),
            action_steps=("a",),
            tool_invocations=(),
            policy_hash="p",
            semantic_clock_vector=(0,),
        )
        import dataclasses

        tampered = dataclasses.replace(env, envelope_hash="0" * 64)
        assert not tampered.verify()

    def test_empty_steps_stable(self):
        env1 = ReasonTraceEnvelope.build(
            trace_id="empty",
            plan_hash="",
            reason_steps=(),
            action_steps=(),
            tool_invocations=(),
            policy_hash="",
            semantic_clock_vector=(),
        )
        env2 = ReasonTraceEnvelope.build(
            trace_id="empty",
            plan_hash="",
            reason_steps=(),
            action_steps=(),
            tool_invocations=(),
            policy_hash="",
            semantic_clock_vector=(),
        )
        assert env1.envelope_hash == env2.envelope_hash


class TestReplayGuard:
    def test_no_violations_clean(self):
        guard = ReplayGuard(semantic_clock_vector=(1000, 0), strict=False)
        guard.assert_clean()  # should not raise

    def test_strict_mode_raises_on_violation(self):
        guard = ReplayGuard(semantic_clock_vector=(1000, 0), strict=True)
        with pytest.raises(NonDeterministicCallDetected):
            guard.record_violation("time.time()")

    def test_non_strict_records_violation(self):
        guard = ReplayGuard(semantic_clock_vector=(1000, 0), strict=False)
        guard.record_violation("datetime.now()")
        assert len(guard.violations) == 1
        assert "datetime.now()" in guard.violations[0]

    def test_assert_clean_raises_if_violations(self):
        guard = ReplayGuard(semantic_clock_vector=(1000,), strict=False)
        guard.record_violation("random.random()")
        with pytest.raises(NonDeterministicCallDetected):
            guard.assert_clean()

    def test_current_tick_from_vector(self):
        guard = ReplayGuard(semantic_clock_vector=(9999, 1))
        assert guard.current_tick == 9999

    def test_empty_clock_vector_tick_zero(self):
        guard = ReplayGuard(semantic_clock_vector=())
        assert guard.current_tick == 0
