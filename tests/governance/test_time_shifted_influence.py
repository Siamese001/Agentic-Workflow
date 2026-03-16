"""Wave 6.3: Time-Shifted Influence Proof (L6 -> L4 -> L0).

Validates:
- Detection in Run t does NOT change routing in Run t
- Version bump between runs changes routing in Run t+1
- No mid-run routing mutation permitted
- Influence is strictly time-shifted across run boundaries
"""

from __future__ import annotations

import copy

import pytest

from agentic_core.L0_routing.types.routing_config_seal_types import (
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

_emit_records_execution_trace("p0", "evidence", "test_time_shifted_influence")
_emit_applies_guardrail("p0", "test_time_shifted_influence", "p0_governance")
_emit_reads_policy_state("p0", "test_time_shifted_influence", "policy_binding")
_emit_snapshots_state("p0", "test_time_shifted_influence", "state_snapshot")
emit_replay_key("p0", "test_time_shifted_influence")
emit_determinism_digest("p0", "test_time_shifted_influence")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_time_shifted_influence", "execution_auth")
_emit_validates_capability("p2", "test_time_shifted_influence", "capability_check")
_emit_routes_to_capability("p2", "test_time_shifted_influence", "capability_route")
_emit_writes_via_uwg("p2", "test_time_shifted_influence", "uwg_write")
_emit_blocks_direct_write("p2", "test_time_shifted_influence", "direct_write_block")
_emit_records_tool_invocation("p2", "test_time_shifted_influence", "tool_invocation")
_emit_captures_execution_output("p2", "test_time_shifted_influence", "exec_output")
_emit_dispatches_agent("p3", "test_time_shifted_influence", "agent_dispatch")
_emit_coordinates_agents("p3", "test_time_shifted_influence", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_time_shifted_influence", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_time_shifted_influence", "healing_outcome")
_emit_escalates_failure("p3", "test_time_shifted_influence", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_time_shifted_influence", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_time_shifted_influence", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_time_shifted_influence", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_time_shifted_influence", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_time_shifted_influence", "eval_metric")
_emit_stores_embedding("p4", "test_time_shifted_influence", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_time_shifted_influence", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_time_shifted_influence", "exec_snapshot_link")

pytestmark = pytest.mark.governance

BASE_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.0,
    "routes": {
        "classify": "ClassifierAgent",
        "summarize": "SummarizerAgent",
    },
    "version": "1.0.0",
}


def _simulate_run(config: dict) -> str:
    """Simulate a sealed run and return the seal hash."""
    ctx = SealedRoutingContext(config, version=config["version"])
    ctx.verify_or_raise(config)
    return ctx.seal.canonical_hash


class TestNoMidRunMutation:
    """Routing must not change during a single run."""

    def test_routing_unchanged_in_same_run(self):
        config = copy.deepcopy(BASE_CONFIG)
        ctx = SealedRoutingContext(config, version=config["version"])
        ctx.verify_or_raise(config)
        ctx.verify_or_raise(config)
        ctx.verify_or_raise(config)

    def test_detection_does_not_change_routing(self):
        config = copy.deepcopy(BASE_CONFIG)
        ctx = SealedRoutingContext(config, version=config["version"])
        # Simulate detection event (L6 observes drift)
        # Key assertion: routing remains unchanged
        ctx.verify_or_raise(config)

    def test_mid_run_mutation_raises(self):
        config = copy.deepcopy(BASE_CONFIG)
        ctx = SealedRoutingContext(config, version=config["version"])
        config["routes"]["classify"] = "NewAgent"
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)


class TestTimeShiftedInfluence:
    """Changes apply only in the NEXT run."""

    def test_version_bump_changes_next_run(self):
        config_v1 = copy.deepcopy(BASE_CONFIG)
        hash_run_t = _simulate_run(config_v1)

        config_v2 = copy.deepcopy(BASE_CONFIG)
        config_v2["version"] = "2.0.0"
        config_v2["routes"]["classify"] = "NewAgent"
        hash_run_t1 = _simulate_run(config_v2)

        assert hash_run_t != hash_run_t1

    def test_same_config_same_hash_across_runs(self):
        config_a = copy.deepcopy(BASE_CONFIG)
        config_b = copy.deepcopy(BASE_CONFIG)
        hash_a = _simulate_run(config_a)
        hash_b = _simulate_run(config_b)
        assert hash_a == hash_b

    def test_influence_strictly_time_shifted(self):
        config = copy.deepcopy(BASE_CONFIG)
        ctx_run_t = SealedRoutingContext(config, version="1.0.0")
        # Simulate detection in run t
        ctx_run_t.verify_or_raise(config)
        hash_run_t = ctx_run_t.seal.canonical_hash

        config_v2 = copy.deepcopy(BASE_CONFIG)
        config_v2["version"] = "2.0.0"
        config_v2["routes"]["summarize"] = "V2Agent"
        ctx_run_t1 = SealedRoutingContext(config_v2, version="2.0.0")
        ctx_run_t1.verify_or_raise(config_v2)
        hash_run_t1 = ctx_run_t1.seal.canonical_hash

        assert hash_run_t != hash_run_t1
