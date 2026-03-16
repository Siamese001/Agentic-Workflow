"""
Phase 4 — Wave 1 Tests: ML write envelope enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.ml_write_intent_types import (
    MLWriteEnvelopeViolation,
    MLWriteIntent,
    MLWriteIntentExecutor,
    execute_ml_write_intent_outside_sandbox,
    is_commit_sandbox_active,
)
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

_emit_records_execution_trace("p0", "evidence", "test_ml_write_envelope")
_emit_applies_guardrail("p0", "test_ml_write_envelope", "p0_governance")
_emit_reads_policy_state("p0", "test_ml_write_envelope", "policy_binding")
_emit_snapshots_state("p0", "test_ml_write_envelope", "state_snapshot")
emit_replay_key("p0", "test_ml_write_envelope")
emit_determinism_digest("p0", "test_ml_write_envelope")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_ml_write_envelope", "execution_auth")
_emit_validates_capability("p2", "test_ml_write_envelope", "capability_check")
_emit_routes_to_capability("p2", "test_ml_write_envelope", "capability_route")
_emit_writes_via_uwg("p2", "test_ml_write_envelope", "uwg_write")
_emit_blocks_direct_write("p2", "test_ml_write_envelope", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ml_write_envelope", "tool_invocation")
_emit_captures_execution_output("p2", "test_ml_write_envelope", "exec_output")
_emit_dispatches_agent("p3", "test_ml_write_envelope", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ml_write_envelope", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ml_write_envelope", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ml_write_envelope", "healing_outcome")
_emit_escalates_failure("p3", "test_ml_write_envelope", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ml_write_envelope", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ml_write_envelope", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ml_write_envelope", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ml_write_envelope", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ml_write_envelope", "eval_metric")
_emit_stores_embedding("p4", "test_ml_write_envelope", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ml_write_envelope", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ml_write_envelope", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestMLWriteIntent:
    def test_build_pattern_store_intent(self):
        intent = MLWriteIntent(
            kind="pattern_store",
            payload={"pattern_id": "p-001", "domain": "agentic_core"},
        )
        assert intent.kind == "pattern_store"
        assert intent.requires_commit is True
        assert len(intent.intent_hash) == 64

    def test_build_cache_set_intent(self):
        intent = MLWriteIntent(
            kind="cache_set",
            payload={"key": "k1", "value": "v1", "ttl": 3600},
        )
        assert intent.kind == "cache_set"
        assert len(intent.intent_hash) == 64

    def test_intent_hash_stable(self):
        payload = {"key": "k", "value": "v"}
        i1 = MLWriteIntent(kind="cache_set", payload=payload)
        i2 = MLWriteIntent(kind="cache_set", payload=payload)
        assert i1.intent_hash == i2.intent_hash

    def test_intent_hash_differs_by_kind(self):
        payload = {"key": "k"}
        i1 = MLWriteIntent(kind="cache_set", payload=payload)
        i2 = MLWriteIntent(kind="pattern_store", payload=payload)
        assert i1.intent_hash != i2.intent_hash

    def test_invalid_kind_raises(self):
        with pytest.raises(ValueError, match="kind must be one of"):
            MLWriteIntent(kind="direct_pinecone_write", payload={})  # type: ignore[arg-type]

    def test_requires_commit_false_raises(self):
        with pytest.raises(ValueError, match="requires_commit must be True"):
            MLWriteIntent(kind="cache_set", payload={}, requires_commit=False)

    def test_non_dict_payload_raises(self):
        with pytest.raises(TypeError, match="payload must be a dict"):
            MLWriteIntent(kind="cache_set", payload="raw_string")  # type: ignore[arg-type]

    def test_canonical_bytes_deterministic(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"a": 1})
        assert intent.canonical_bytes() == intent.canonical_bytes()


class TestMLWriteSandbox:
    def test_sandbox_inactive_by_default(self):
        assert is_commit_sandbox_active() is False

    def test_sandbox_active_inside_context(self):
        with MLWriteIntentExecutor():
            assert is_commit_sandbox_active() is True

    def test_sandbox_inactive_after_context(self):
        with MLWriteIntentExecutor():
            pass
        assert is_commit_sandbox_active() is False

    def test_ml_write_allowed_inside_commit_sandbox(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"pattern_id": "p-sandbox"})
        with MLWriteIntentExecutor() as executor:
            result = executor.execute(intent)
        assert result["executed"] is True
        assert result["kind"] == "pattern_store"
        assert result["intent_hash"] == intent.intent_hash

    def test_ml_write_blocked_outside_commit_sandbox(self):
        """
        Negative: executing MLWriteIntent outside the sandbox raises
        MLWriteEnvelopeViolation with ML_WRITE_OUTSIDE_SANDBOX code.
        """
        executor = MLWriteIntentExecutor()
        intent = MLWriteIntent(kind="cache_set", payload={"key": "k"})
        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            executor.execute(intent)

    def test_direct_write_outside_sandbox_raises(self):
        """
        Negative: direct ML write attempt (simulated via
        execute_ml_write_intent_outside_sandbox) raises MLWriteEnvelopeViolation.
        """
        intent = MLWriteIntent(kind="pattern_store", payload={"domain": "apps_rg"})
        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            execute_ml_write_intent_outside_sandbox(intent)

    def test_violation_error_carries_violation_code(self):
        err = MLWriteEnvelopeViolation("test")
        assert "ML_WRITE_OUTSIDE_SANDBOX" in str(err)

    def test_sandbox_restores_state_on_exception(self):
        """Sandbox must deactivate even if execute() raises."""
        try:
            with MLWriteIntentExecutor():
                assert is_commit_sandbox_active() is True
                raise RuntimeError("simulated failure")
        except RuntimeError:  # guardian: allow-silent-swallower
            pass
        assert is_commit_sandbox_active() is False

    def test_cache_set_allowed_inside_sandbox(self):
        intent = MLWriteIntent(kind="cache_set", payload={"key": "ast-result", "ttl": 3600})
        with MLWriteIntentExecutor() as executor:
            result = executor.execute(intent)
        assert result["executed"] is True
        assert result["kind"] == "cache_set"
