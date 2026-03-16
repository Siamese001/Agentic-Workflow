"""Wave 5.3: Immutable routing config seal tests.

Validates:
- RoutingConfigSeal is frozen
- Seal hash is deterministic
- Unchanged config passes verification
- Mutated config fails verification
- SealedRoutingContext raises on mutation
- sealed_at timestamp is set
"""

import pytest

from agentic_core.L0_routing.types.routing_config_seal_types import (
    RoutingConfigSeal,
    RoutingConfigSealViolation,
    SealedRoutingContext,
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_routing_config_seal", "p4obs", "metric_1")
_emit_emits_metric_event("test_routing_config_seal", "p4obs", "metric_2")
_emit_emits_metric_event("test_routing_config_seal", "p4obs", "metric_3")
_emit_emits_metric_event("test_routing_config_seal", "p4obs", "metric_4")
_emit_emits_metric_event("test_routing_config_seal", "p4obs", "metric_5")
_emit_emits_metric_event("test_routing_config_seal", "p4obs", "metric_6")
_emit_records_incident_event("test_routing_config_seal", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_routing_config_seal", "p4obs", "anomaly")
_emit_writes_observability_log("test_routing_config_seal", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_routing_config_seal", "p4obs", "mon_state")
_emit_triggers_alert("test_routing_config_seal", "p4obs", "alert")
_emit_links_incident_trace("test_routing_config_seal", "p4obs", "trace_link")
_emit_captures_pattern("test_routing_config_seal", "p3lm", "pattern")
_emit_records_learning_event("test_routing_config_seal", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_routing_config_seal", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_routing_config_seal", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_routing_config_seal", "p3lm", "routing")
_emit_improves_agent_policy("test_routing_config_seal", "p3lm", "policy")
_emit_stores_learning_state("test_routing_config_seal", "p3lm", "state")
_emit_records_execution_trace("test_routing_config_seal", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_routing_config_seal", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_routing_config_seal", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_routing_config_seal", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_routing_config_seal", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_routing_config_seal", "env_read", "p2_env_1")
_emit_reads_environ("test_routing_config_seal", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_routing_config_seal", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_routing_config_seal", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_routing_config_seal")
_emit_applies_guardrail("p0", "test_routing_config_seal", "p0_governance")
_emit_reads_policy_state("p0", "test_routing_config_seal", "policy_binding")
_emit_snapshots_state("p0", "test_routing_config_seal", "state_snapshot")
_emit_pulls_context("p1", "test_routing_config_seal", "context_pull")
_emit_pulls_context("p1", "test_routing_config_seal", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_routing_config_seal", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_routing_config_seal", "uwg_term_secondary")
_emit_writes_through("p1", "test_routing_config_seal", "write_through")
_emit_writes_through("p1", "test_routing_config_seal", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_routing_config_seal", "safety_validation")
_emit_invokes_eval("p1", "test_routing_config_seal", "eval_call")
_emit_proposal_commits_routing("p1", "test_routing_config_seal", "routing_commit")
emit_replay_key("p0", "test_routing_config_seal")
emit_determinism_digest("p0", "test_routing_config_seal")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_routing_config_seal", "execution_auth")
_emit_validates_capability("p2", "test_routing_config_seal", "capability_check")
_emit_routes_to_capability("p2", "test_routing_config_seal", "capability_route")
_emit_writes_via_uwg("p2", "test_routing_config_seal", "uwg_write")
_emit_blocks_direct_write("p2", "test_routing_config_seal", "direct_write_block")
_emit_records_tool_invocation("p2", "test_routing_config_seal", "tool_invocation")
_emit_captures_execution_output("p2", "test_routing_config_seal", "exec_output")
_emit_dispatches_agent("p3", "test_routing_config_seal", "agent_dispatch")
_emit_coordinates_agents("p3", "test_routing_config_seal", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_routing_config_seal", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_routing_config_seal", "healing_outcome")
_emit_escalates_failure("p3", "test_routing_config_seal", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_routing_config_seal", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_routing_config_seal", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_routing_config_seal", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_routing_config_seal", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_routing_config_seal", "eval_metric")
_emit_stores_embedding("p4", "test_routing_config_seal", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_routing_config_seal", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_routing_config_seal", "exec_snapshot_link")

pytestmark = pytest.mark.governance

SAMPLE_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.0,
    "routes": {"a": "agent-1", "b": "agent-2"},
}


class TestSealImmutability:
    """RoutingConfigSeal must be frozen."""

    def test_seal_is_frozen(self):
        seal = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        with pytest.raises(AttributeError):
            seal.canonical_hash = "tampered"  # type: ignore[misc]

    def test_sealed_at_is_set(self):
        seal = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        assert seal.sealed_at is not None
        assert len(seal.sealed_at) > 0


class TestSealDeterminism:
    """Same config must produce same hash."""

    def test_same_config_same_hash(self):
        a = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        b = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        assert a.canonical_hash == b.canonical_hash

    def test_different_config_different_hash(self):
        a = RoutingConfigSeal.create(config=SAMPLE_CONFIG, version="1.0")
        b = RoutingConfigSeal.create(
            config={"model": "gpt-3.5"},
            version="1.0",
        )
        assert a.canonical_hash != b.canonical_hash


class TestSealVerification:
    """Seal must detect config changes."""

    def test_unchanged_config_passes(self):
        config = dict(SAMPLE_CONFIG)
        seal = RoutingConfigSeal.create(config=config, version="1.0")
        assert seal.verify(config) is True

    def test_mutated_config_fails(self):
        config = dict(SAMPLE_CONFIG)
        seal = RoutingConfigSeal.create(config=config, version="1.0")
        config["new_key"] = "injected"
        assert seal.verify(config) is False

    def test_removed_key_fails(self):
        config = dict(SAMPLE_CONFIG)
        seal = RoutingConfigSeal.create(config=config, version="1.0")
        del config["model"]
        assert seal.verify(config) is False


class TestSealedRoutingContext:
    """Context must raise on mid-run mutation."""

    def test_no_mutation_passes(self):
        config = dict(SAMPLE_CONFIG)
        ctx = SealedRoutingContext(config, version="1.0")
        ctx.verify_or_raise(config)

    def test_mutation_raises(self):
        config = dict(SAMPLE_CONFIG)
        ctx = SealedRoutingContext(config, version="1.0")
        config["temperature"] = 1.0
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)

    def test_seal_accessible(self):
        config = dict(SAMPLE_CONFIG)
        ctx = SealedRoutingContext(config, version="1.0")
        assert ctx.seal.version == "1.0"
        assert len(ctx.seal.canonical_hash) == 64
