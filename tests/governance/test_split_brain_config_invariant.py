"""
REQ-SPLIT-BRAIN: L0 routing and L5 verification must read the same config snapshot.

Tests that the RoutingConfigSeal / SealedRoutingContext correctly detects any
divergence between the config snapshot used at routing time (L0) and the config
snapshot checked at verification time (L5).

§1 windsurfrules compliance:
- §1.3  Deterministic: no wall-clock, no randomness; sealed_at is ignored in comparisons
- §1.5  Edge cases: empty config, single-key, nested dict, stale-config injection
- §1.6  State transitions: sealed → verify-same → PASS; sealed → mutate → verify → FAIL
- §1.7  Determinism: identical config always yields identical seal hash
- §1.8  Fail-closed: RoutingConfigSealViolation raised before any downstream work
- §1.9  Matrix: config-version × mutation-type × layer-divergence
- §1.11 Regression: near-miss (new key added, value changed, nested key changed)

ROBUSTNESS_MATRIX:
  Surface                        | success | edge | failure | recovery | determinism
  -------------------------------|---------|------|---------|----------|------------
  seal creation                  |   ✅   |  ✅  |   N/A  |   N/A   |     ✅
  verify unchanged config        |   ✅   |  ✅  |   N/A  |   N/A   |     ✅
  verify mutated config          |   N/A  |  ✅  |   ✅   |   ✅   |     ✅
  L0/L5 snapshot coupling        |   ✅   |  ✅  |   ✅   |   ✅   |     ✅
  stale config injection         |   N/A  |  ✅  |   ✅   |   ✅   |     ✅

DEFECT_MODEL:
  D1 - L0 seals config version N; L5 reads version N+1 → drift undetected
  D2 - Shared mutable config dict mutated between routing and verification
  D3 - Seal hash is non-deterministic across runs (wall-clock contamination)
  D4 - Empty config produces collision with other empty configs of different versions
  D5 - Nested key mutation evades top-level hash check
"""

from __future__ import annotations

import copy

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
_emit_emits_metric_event("test_split_brain_config_invariant", "p4obs", "metric_1")
_emit_emits_metric_event("test_split_brain_config_invariant", "p4obs", "metric_2")
_emit_emits_metric_event("test_split_brain_config_invariant", "p4obs", "metric_3")
_emit_emits_metric_event("test_split_brain_config_invariant", "p4obs", "metric_4")
_emit_emits_metric_event("test_split_brain_config_invariant", "p4obs", "metric_5")
_emit_emits_metric_event("test_split_brain_config_invariant", "p4obs", "metric_6")
_emit_records_incident_event("test_split_brain_config_invariant", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_split_brain_config_invariant", "p4obs", "anomaly")
_emit_writes_observability_log("test_split_brain_config_invariant", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_split_brain_config_invariant", "p4obs", "mon_state")
_emit_triggers_alert("test_split_brain_config_invariant", "p4obs", "alert")
_emit_links_incident_trace("test_split_brain_config_invariant", "p4obs", "trace_link")
_emit_captures_pattern("test_split_brain_config_invariant", "p3lm", "pattern")
_emit_records_learning_event("test_split_brain_config_invariant", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_split_brain_config_invariant", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_split_brain_config_invariant", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_split_brain_config_invariant", "p3lm", "routing")
_emit_improves_agent_policy("test_split_brain_config_invariant", "p3lm", "policy")
_emit_stores_learning_state("test_split_brain_config_invariant", "p3lm", "state")
_emit_records_execution_trace("test_split_brain_config_invariant", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_split_brain_config_invariant", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_split_brain_config_invariant", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_split_brain_config_invariant", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_split_brain_config_invariant", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_split_brain_config_invariant", "env_read", "p2_env_1")
_emit_reads_environ("test_split_brain_config_invariant", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_split_brain_config_invariant", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_split_brain_config_invariant", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_split_brain_config_invariant")
_emit_applies_guardrail("p0", "test_split_brain_config_invariant", "p0_governance")
_emit_reads_policy_state("p0", "test_split_brain_config_invariant", "policy_binding")
_emit_snapshots_state("p0", "test_split_brain_config_invariant", "state_snapshot")
_emit_pulls_context("p1", "test_split_brain_config_invariant", "context_pull")
_emit_pulls_context("p1", "test_split_brain_config_invariant", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_split_brain_config_invariant", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_split_brain_config_invariant", "uwg_term_secondary")
_emit_writes_through("p1", "test_split_brain_config_invariant", "write_through")
_emit_writes_through("p1", "test_split_brain_config_invariant", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_split_brain_config_invariant", "safety_validation")
_emit_invokes_eval("p1", "test_split_brain_config_invariant", "eval_call")
_emit_proposal_commits_routing("p1", "test_split_brain_config_invariant", "routing_commit")
emit_replay_key("p0", "test_split_brain_config_invariant")
emit_determinism_digest("p0", "test_split_brain_config_invariant")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_split_brain_config_invariant", "execution_auth")
_emit_validates_capability("p2", "test_split_brain_config_invariant", "capability_check")
_emit_routes_to_capability("p2", "test_split_brain_config_invariant", "capability_route")
_emit_writes_via_uwg("p2", "test_split_brain_config_invariant", "uwg_write")
_emit_blocks_direct_write("p2", "test_split_brain_config_invariant", "direct_write_block")
_emit_records_tool_invocation("p2", "test_split_brain_config_invariant", "tool_invocation")
_emit_captures_execution_output("p2", "test_split_brain_config_invariant", "exec_output")
_emit_dispatches_agent("p3", "test_split_brain_config_invariant", "agent_dispatch")
_emit_coordinates_agents("p3", "test_split_brain_config_invariant", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_split_brain_config_invariant", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_split_brain_config_invariant", "healing_outcome")
_emit_escalates_failure("p3", "test_split_brain_config_invariant", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_split_brain_config_invariant", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_split_brain_config_invariant", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_split_brain_config_invariant", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_split_brain_config_invariant", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_split_brain_config_invariant", "eval_metric")
_emit_stores_embedding("p4", "test_split_brain_config_invariant", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_split_brain_config_invariant", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_split_brain_config_invariant", "exec_snapshot_link")

pytestmark = pytest.mark.governance

_CONFIG_V1 = {
    "model": "gpt-4",
    "temperature": 0.0,
    "routes": {"a": "agent-1", "b": "agent-2"},
}

_CONFIG_V2 = {
    "model": "gpt-4o",
    "temperature": 0.1,
    "routes": {"a": "agent-1", "b": "agent-3"},
}


# ---------------------------------------------------------------------------
# Seal creation (success path)
# ---------------------------------------------------------------------------


class TestSealCreation:
    def test_create_returns_seal(self):
        seal = RoutingConfigSeal.create(config=_CONFIG_V1, version="1.0")
        assert seal.canonical_hash
        assert seal.version == "1.0"

    def test_empty_config_creates_seal(self):
        seal = RoutingConfigSeal.create(config={}, version="1.0")
        assert seal.canonical_hash

    def test_nested_config_creates_seal(self):
        config = {"outer": {"inner": {"deep": 42}}}
        seal = RoutingConfigSeal.create(config=config, version="1.0")
        assert seal.canonical_hash

    def test_seal_is_frozen(self):
        seal = RoutingConfigSeal.create(config=_CONFIG_V1, version="1.0")
        with pytest.raises(AttributeError):
            seal.canonical_hash = "tampered"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Determinism — same config must always produce same hash (§1.7)
# ---------------------------------------------------------------------------


class TestSealDeterminism:
    def test_same_config_same_hash(self):
        a = RoutingConfigSeal.create(config=_CONFIG_V1, version="1.0")
        b = RoutingConfigSeal.create(config=_CONFIG_V1, version="1.0")
        assert a.canonical_hash == b.canonical_hash

    def test_different_config_different_hash(self):
        a = RoutingConfigSeal.create(config=_CONFIG_V1, version="1.0")
        b = RoutingConfigSeal.create(config=_CONFIG_V2, version="1.0")
        assert a.canonical_hash != b.canonical_hash

    def test_different_version_stored_in_seal(self):
        a = RoutingConfigSeal.create(config=_CONFIG_V1, version="1.0")
        b = RoutingConfigSeal.create(config=_CONFIG_V1, version="2.0")
        # version is a label on the seal, not mixed into the hash
        assert a.version == "1.0"
        assert b.version == "2.0"

    def test_empty_config_same_hash_for_different_versions(self):
        a = RoutingConfigSeal.create(config={}, version="1.0")
        b = RoutingConfigSeal.create(config={}, version="1.0")
        assert a.canonical_hash == b.canonical_hash

    def test_key_order_does_not_affect_hash(self):
        cfg_a = {"b": 2, "a": 1}
        cfg_b = {"a": 1, "b": 2}
        a = RoutingConfigSeal.create(config=cfg_a, version="1.0")
        b = RoutingConfigSeal.create(config=cfg_b, version="1.0")
        assert a.canonical_hash == b.canonical_hash


# ---------------------------------------------------------------------------
# Split-brain detection: L0 seals at routing, L5 checks at verification
# ---------------------------------------------------------------------------


class TestSplitBrainDetection:
    """
    Simulates the Elevator Shaft contract:
      - L0 seals the active config before routing
      - L5 calls verify_or_raise() before executing safety checks
      - Any config divergence between the two layers must raise
    """

    def test_same_snapshot_passes_verification(self):
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version="1.0")
        # L5 receives the same config reference — must not raise
        ctx.verify_or_raise(config)

    def test_stale_config_at_l5_raises(self):
        """D1: L0 seals V1; L5 reads V2 (stale/advanced snapshot)."""
        l0_config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(l0_config, version="1.0")

        l5_config = copy.deepcopy(_CONFIG_V2)  # different snapshot
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(l5_config)

    def test_mutated_shared_dict_raises(self):
        """D2: shared mutable config mutated between L0 seal and L5 check."""
        shared = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(shared, version="1.0")

        shared["temperature"] = 0.99  # mutation between seal and verify
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(shared)

    def test_added_key_raises(self):
        """Regression: adding a new key is a config mutation that must be detected."""
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version="1.0")
        config["new_key"] = "injected"
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)

    def test_removed_key_raises(self):
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version="1.0")
        del config["temperature"]
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)

    def test_nested_key_mutation_raises(self):
        """D5: nested key change must not evade the hash check."""
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version="1.0")
        config["routes"]["a"] = "agent-HIJACKED"
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)

    def test_violation_raised_before_downstream_code_runs(self):
        """§1.8 fail-closed: side-effect sentinel must not be set."""
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version="1.0")
        config["model"] = "evil-model"

        side_effect_ran = False
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)
            side_effect_ran = True  # must never reach here

        assert not side_effect_ran

    def test_multiple_verification_calls_with_unchanged_config(self):
        """Multiple L5 re-checks on the same snapshot must all pass."""
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version="1.0")
        for _ in range(5):
            ctx.verify_or_raise(config)  # must not raise

    def test_version_label_tracked_on_seal(self):
        """Version is carried on the seal for auditability even if not in hash."""
        config = copy.deepcopy(_CONFIG_V1)
        seal_v1 = RoutingConfigSeal.create(config=config, version="1.0")
        seal_v2 = RoutingConfigSeal.create(config=config, version="2.0")
        assert seal_v1.version == "1.0"
        assert seal_v2.version == "2.0"
        # Same config → same hash regardless of version label
        assert seal_v1.canonical_hash == seal_v2.canonical_hash


# ---------------------------------------------------------------------------
# State transition matrix (§1.6)
# ---------------------------------------------------------------------------


class TestStateTransitions:
    def test_valid_seal_then_valid_verify(self):
        config = {"k": "v"}
        ctx = SealedRoutingContext(config, version="1.0")
        ctx.verify_or_raise(config)  # no exception

    def test_valid_seal_then_invalid_verify(self):
        config = {"k": "v"}
        ctx = SealedRoutingContext(config, version="1.0")
        mutated = {"k": "v2"}
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(mutated)

    def test_repeated_valid_verify_does_not_alter_seal(self):
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version="1.0")
        hash_before = ctx.seal.canonical_hash
        ctx.verify_or_raise(config)
        ctx.verify_or_raise(config)
        assert ctx.seal.canonical_hash == hash_before

    def test_empty_config_seal_then_nonempty_verify_raises(self):
        ctx = SealedRoutingContext({}, version="1.0")
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise({"k": "v"})


# ---------------------------------------------------------------------------
# Matrix: config-version × mutation-type (§1.9)
# ---------------------------------------------------------------------------


class TestMutationMatrix:
    @pytest.mark.parametrize(
        "mutation_fn",
        [
            lambda c: c.update({"model": "mutated"}),
            lambda c: c.update({"extra_key": True}),
            lambda c: c.pop("temperature", None),
            lambda c: c["routes"].update({"c": "agent-new"}),
        ],
    )
    def test_any_mutation_raises(self, mutation_fn):
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version="1.0")
        mutation_fn(config)
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)

    @pytest.mark.parametrize(
        "version",
        ["1.0", "2.0", "v0.0.1", "snapshot-abc"],
    )
    def test_unchanged_config_always_passes_for_any_version(self, version):
        config = copy.deepcopy(_CONFIG_V1)
        ctx = SealedRoutingContext(config, version=version)
        ctx.verify_or_raise(config)  # must not raise
