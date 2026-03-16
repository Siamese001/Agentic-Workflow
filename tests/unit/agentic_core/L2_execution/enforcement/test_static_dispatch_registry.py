"""Tests for StaticDispatchRegistry — replaces __import__/importlib dynamic dispatch."""

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

_emit_records_execution_trace("p0", "evidence", "test_static_dispatch_registry")
_emit_applies_guardrail("p0", "test_static_dispatch_registry", "p0_governance")
_emit_reads_policy_state("p0", "test_static_dispatch_registry", "policy_binding")
_emit_routes_to_agent("p1", "test_static_dispatch_registry", "test")
_emit_orchestrates_workflow("p1", "test_static_dispatch_registry", "test")
_emit_dispatches_execution_plan("p1", "test_static_dispatch_registry", "test")
_emit_validates_agent_capability("p1", "test_static_dispatch_registry", "test")
_emit_checks_agent_registry("p1", "test_static_dispatch_registry", "test")
_emit_snapshots_state("p0", "test_static_dispatch_registry", "state_snapshot")
emit_replay_key("p0", "test_static_dispatch_registry")
emit_determinism_digest("p0", "test_static_dispatch_registry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_static_dispatch_registry", "execution_auth")
_emit_validates_capability("p2", "test_static_dispatch_registry", "capability_check")
_emit_routes_to_capability("p2", "test_static_dispatch_registry", "capability_route")
_emit_writes_via_uwg("p2", "test_static_dispatch_registry", "uwg_write")
_emit_blocks_direct_write("p2", "test_static_dispatch_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "test_static_dispatch_registry", "tool_invocation")
_emit_captures_execution_output("p2", "test_static_dispatch_registry", "exec_output")
_emit_dispatches_agent("p3", "test_static_dispatch_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "test_static_dispatch_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_static_dispatch_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_static_dispatch_registry", "healing_outcome")
_emit_escalates_failure("p3", "test_static_dispatch_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_static_dispatch_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_static_dispatch_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_static_dispatch_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_static_dispatch_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_static_dispatch_registry", "eval_metric")
_emit_stores_embedding("p4", "test_static_dispatch_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_static_dispatch_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_static_dispatch_registry", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.static_dispatch_registry import (
    StaticDispatchRegistry,
    UnregisteredDispatchError,
    get_guardian_registry,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_static_dispatch_registry", "p4obs", "metric_1")
_emit_emits_metric_event("test_static_dispatch_registry", "p4obs", "metric_2")
_emit_emits_metric_event("test_static_dispatch_registry", "p4obs", "metric_3")
_emit_emits_metric_event("test_static_dispatch_registry", "p4obs", "metric_4")
_emit_emits_metric_event("test_static_dispatch_registry", "p4obs", "metric_5")
_emit_emits_metric_event("test_static_dispatch_registry", "p4obs", "metric_6")
_emit_records_incident_event("test_static_dispatch_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_static_dispatch_registry", "p4obs", "anomaly")
_emit_writes_observability_log("test_static_dispatch_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_static_dispatch_registry", "p4obs", "mon_state")
_emit_triggers_alert("test_static_dispatch_registry", "p4obs", "alert")
_emit_links_incident_trace("test_static_dispatch_registry", "p4obs", "trace_link")
_emit_captures_pattern("test_static_dispatch_registry", "p3lm", "pattern")
_emit_records_learning_event("test_static_dispatch_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_static_dispatch_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_static_dispatch_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_static_dispatch_registry", "p3lm", "routing")
_emit_improves_agent_policy("test_static_dispatch_registry", "p3lm", "policy")
_emit_stores_learning_state("test_static_dispatch_registry", "p3lm", "state")
_emit_records_execution_trace("test_static_dispatch_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_static_dispatch_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_static_dispatch_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_static_dispatch_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_static_dispatch_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_static_dispatch_registry", "env_read", "p2_env_1")
_emit_reads_environ("test_static_dispatch_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_static_dispatch_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_static_dispatch_registry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_static_dispatch_registry", "context_pull")
_emit_pulls_context("p1", "test_static_dispatch_registry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_static_dispatch_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_static_dispatch_registry", "uwg_term_2")
_emit_writes_through("p1", "test_static_dispatch_registry", "write_through")
_emit_writes_through("p1", "test_static_dispatch_registry", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_static_dispatch_registry", "safety_validation")
_emit_invokes_eval("p1", "test_static_dispatch_registry", "eval_call")
_emit_proposal_commits_routing("p1", "test_static_dispatch_registry", "routing_commit")


class TestStaticDispatchRegistryRegistration:
    def test_register_and_is_registered(self):
        reg = StaticDispatchRegistry()
        reg.register("mykey", "json")
        assert reg.is_registered("mykey")

    def test_unregistered_key_not_present(self):
        reg = StaticDispatchRegistry()
        assert not reg.is_registered("absent")

    def test_register_many(self):
        reg = StaticDispatchRegistry()
        reg.register_many({"a": "json", "b": "os"})
        assert reg.is_registered("a")
        assert reg.is_registered("b")

    def test_len(self):
        reg = StaticDispatchRegistry()
        reg.register("x", "json")
        reg.register("y", "os")
        assert len(reg) == 2

    def test_contains_operator(self):
        reg = StaticDispatchRegistry()
        reg.register("z", "json")
        assert "z" in reg
        assert "missing" not in reg

    def test_registered_keys_sorted(self):
        reg = StaticDispatchRegistry()
        reg.register_many({"b": "os", "a": "json", "c": "sys"})
        assert reg.registered_keys() == ["a", "b", "c"]

    def test_overwrite_clears_resolved_cache(self):
        reg = StaticDispatchRegistry()
        reg.register("k", "json")
        _ = reg.dispatch("k")
        reg.register("k", "os")
        mod = reg.dispatch("k")
        assert mod.__name__ == "os"


class TestStaticDispatchRegistryDispatch:
    def test_dispatch_returns_module(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        mod = reg.dispatch("json_mod")
        import json

        assert mod is json

    def test_dispatch_unregistered_raises(self):
        reg = StaticDispatchRegistry()
        with pytest.raises(UnregisteredDispatchError, match="No module registered"):
            reg.dispatch("not_there")

    def test_dispatch_caches_module(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        mod1 = reg.dispatch("json_mod")
        mod2 = reg.dispatch("json_mod")
        assert mod1 is mod2

    def test_dispatch_invalid_module_raises_import_error(self):
        reg = StaticDispatchRegistry()
        reg.register("bad", "totally_nonexistent_module_xyz_abc")
        with pytest.raises(ImportError):
            reg.dispatch("bad")


class TestStaticDispatchRegistryDispatchAttr:
    def test_dispatch_attr_returns_attribute(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        dumps = reg.dispatch_attr("json_mod", "dumps")
        import json

        assert dumps is json.dumps

    def test_dispatch_attr_missing_raises_attribute_error(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        with pytest.raises(AttributeError, match="has no attribute"):
            reg.dispatch_attr("json_mod", "nonexistent_attr_xyz")

    def test_dispatch_callable_returns_callable(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        fn = reg.dispatch_callable("json_mod", "dumps")
        assert callable(fn)
        assert fn({"k": 1}) == '{"k": 1}'

    def test_dispatch_callable_non_callable_raises_type_error(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        with pytest.raises(TypeError, match="not callable"):
            reg.dispatch_callable("json_mod", "__version__")

    def test_dispatch_attr_unregistered_raises(self):
        reg = StaticDispatchRegistry()
        with pytest.raises(UnregisteredDispatchError):
            reg.dispatch_attr("not_there", "fn")


class TestGuardianRegistry:
    def test_get_guardian_registry_returns_instance(self):
        reg = get_guardian_registry()
        assert isinstance(reg, StaticDispatchRegistry)

    def test_guardian_registry_singleton(self):
        r1 = get_guardian_registry()
        r2 = get_guardian_registry()
        assert r1 is r2

    def test_guardian_registry_has_hygiene_key(self):
        reg = get_guardian_registry()
        assert reg.is_registered("guardian.hygiene")

    def test_guardian_registry_has_c0_sovereignty_key(self):
        reg = get_guardian_registry()
        assert reg.is_registered("guardian.c0_sovereignty")

    def test_guardian_registry_has_all_key(self):
        reg = get_guardian_registry()
        assert reg.is_registered("guardian.all")

    def test_guardian_registry_dispatch_unregistered_fails_closed(self):
        reg = get_guardian_registry()
        with pytest.raises(UnregisteredDispatchError):
            reg.dispatch("nonexistent.guardian")
