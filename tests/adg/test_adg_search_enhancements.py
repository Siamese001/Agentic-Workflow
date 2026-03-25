"""Tests for ADG search enhancements — Accelerator #3.

Coverage matrix per §1.1:
- search_nodes with no filters: basic substring match, case-insensitive, sorted
- search_nodes with layer filter: exact match, case-insensitive, excludes wrong layer
- search_nodes with entity_type filter: exact match, case-insensitive
- search_nodes with both filters: AND semantics (must match both)
- search_nodes with empty substring + filters: return all nodes matching filters
- Edge cases: no matches, None filters, empty node field values
- Determinism: identical input → identical sorted output
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_search_enhancements")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_search_enhancements", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_search_enhancements", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_search_enhancements", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_adg_search_enhancements", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_search_enhancements", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_search_enhancements", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_search_enhancements", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_search_enhancements", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_search_enhancements", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_search_enhancements", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_search_enhancements", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_search_enhancements", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_search_enhancements", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_search_enhancements", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_search_enhancements", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_search_enhancements", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_search_enhancements", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_search_enhancements", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_search_enhancements", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_search_enhancements", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_search_enhancements", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_search_enhancements", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_search_enhancements", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_search_enhancements", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_search_enhancements", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_search_enhancements", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_search_enhancements", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_search_enhancements", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_search_enhancements", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_search_enhancements", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_search_enhancements", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_search_enhancements", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_search_enhancements", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_search_enhancements", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_search_enhancements", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_search_enhancements", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_search_enhancements", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_search_enhancements", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_search_enhancements", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_search_enhancements", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_search_enhancements", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_search_enhancements", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_search_enhancements", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_search_enhancements", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_search_enhancements", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_search_enhancements", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_search_enhancements", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_search_enhancements", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_search_enhancements", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_search_enhancements", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_search_enhancements", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_search_enhancements")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_search_enhancements", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_search_enhancements")
# REMOVED: emit_determinism_digest("p0", "test_adg_search_enhancements")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_search_enhancements", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_search_enhancements", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_search_enhancements", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_search_enhancements", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_search_enhancements", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_search_enhancements", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_search_enhancements", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_search_enhancements", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_search_enhancements", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_search_enhancements", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_search_enhancements", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_search_enhancements", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_search_enhancements", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_search_enhancements", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_search_enhancements", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_search_enhancements", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_search_enhancements", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_search_enhancements", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_search_enhancements", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_search_enhancements", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client_with_nodes(nodes: list[dict[str, str]]) -> object:
    """Build ADGRedisClient stub whose scan returns the given nodes.

    Uses index-based unique keys to avoid key collisions when multiple nodes
    share the same adg_name (e.g. same filename in different layers).
    """
    from tools.adg.adg_redis_query import ADGRedisClient

    client = ADGRedisClient.__new__(ADGRedisClient)
    r = MagicMock()

    keys = [f"adg:node:test_node_{i}" for i in range(len(nodes))]
    node_map = {keys[i]: nodes[i] for i in range(len(nodes))}

    r.scan.return_value = (0, keys)

    def hgetall(key: str) -> dict[str, str]:
        return node_map.get(key, {})

    r.hgetall.side_effect = hgetall
    client._r = r
    return client


# ===========================================================================
# search_nodes — no filters (baseline from previous implementation)
# ===========================================================================


class TestSearchNodesBaseline:
    def test_substring_match_case_insensitive(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "ADG::Module::apps_lic/DashboardAgent.py", "layer": "L4"},
            {"adg_name": "ADG::Module::apps_lic/RoutingAgent.py", "layer": "L4"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "dashboardagent")
        assert len(result) == 1
        assert "DashboardAgent" in result[0]["adg_name"]

    def test_no_match_returns_empty(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "ADG::Module::apps_lic/RoutingAgent.py", "layer": "L4"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "nonexistent_xyz_abc")
        assert result == []

    def test_empty_substring_returns_all_nodes(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0"},
            {"adg_name": "ADG::Module::b.py", "layer": "L2"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "")
        assert len(result) == 2

    def test_result_is_sorted_by_adg_name(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "z_module.py"},
            {"adg_name": "a_module.py"},
            {"adg_name": "m_module.py"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "")
        names = [n["adg_name"] for n in result]
        assert names == sorted(names)

    def test_deterministic_output(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "ADG::Module::foo.py", "layer": "L2"},
            {"adg_name": "ADG::Module::bar.py", "layer": "L2"},
        ]
        client = _make_client_with_nodes(nodes)
        r1 = ADGRedisClient.search_nodes(client, "")
        r2 = ADGRedisClient.search_nodes(client, "")
        assert r1 == r2


# ===========================================================================
# search_nodes — layer filter
# ===========================================================================


class TestSearchNodesLayerFilter:
    def test_layer_filter_returns_only_matching_layer(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "layer": "L0"},
            {"adg_name": "mod_b.py", "layer": "L2"},
            {"adg_name": "mod_c.py", "layer": "L0"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer="L0")
        assert len(result) == 2
        assert all(n["layer"] == "L0" for n in result)

    def test_layer_filter_case_insensitive(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "layer": "L2"},
            {"adg_name": "mod_b.py", "layer": "L4"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer="l2")
        assert len(result) == 1
        assert result[0]["layer"] == "L2"

    def test_layer_filter_no_match_returns_empty(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "layer": "L0"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer="L9")
        assert result == []

    def test_none_layer_does_not_filter(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "layer": "L0"},
            {"adg_name": "mod_b.py", "layer": "L5"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer=None)
        assert len(result) == 2

    def test_layer_filter_combined_with_substring(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "Router.py", "layer": "L0"},
            {"adg_name": "Router.py", "layer": "L2"},
            {"adg_name": "Dispatcher.py", "layer": "L0"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "router", layer="L0")
        assert len(result) == 1
        assert result[0]["layer"] == "L0"
        assert "Router" in result[0]["adg_name"]


# ===========================================================================
# search_nodes — entity_type filter
# ===========================================================================


class TestSearchNodesEntityTypeFilter:
    def test_entity_type_filter_returns_only_matching_type(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "entity_type": "module"},
            {"adg_name": "ClassA", "entity_type": "class"},
            {"adg_name": "func_a", "entity_type": "function"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", entity_type="class")
        assert len(result) == 1
        assert result[0]["entity_type"] == "class"

    def test_entity_type_filter_case_insensitive(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "MyClass", "entity_type": "Class"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", entity_type="class")
        assert len(result) == 1

    def test_entity_type_no_match_returns_empty(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod.py", "entity_type": "module"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", entity_type="dataclass")
        assert result == []

    def test_none_entity_type_does_not_filter(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod.py", "entity_type": "module"},
            {"adg_name": "MyClass", "entity_type": "class"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", entity_type=None)
        assert len(result) == 2


# ===========================================================================
# search_nodes — both filters (AND semantics)
# ===========================================================================


class TestSearchNodesBothFilters:
    def test_both_filters_must_both_match(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "AgentClass_L3", "layer": "L3", "entity_type": "class"},
            {"adg_name": "AgentClass_L4", "layer": "L4", "entity_type": "class"},
            {"adg_name": "AgentFunc_L3", "layer": "L3", "entity_type": "function"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "agent", layer="L3", entity_type="class")
        assert len(result) == 1
        assert result[0]["layer"] == "L3"
        assert result[0]["entity_type"] == "class"

    def test_both_filters_no_match_returns_empty(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "AgentClass_L3", "layer": "L3", "entity_type": "class"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "agent", layer="L5", entity_type="class")
        assert result == []

    def test_empty_substring_with_both_filters(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "A", "layer": "L2", "entity_type": "module"},
            {"adg_name": "B", "layer": "L2", "entity_type": "class"},
            {"adg_name": "C", "layer": "L4", "entity_type": "module"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer="L2", entity_type="module")
        assert len(result) == 1
        assert result[0]["adg_name"] == "A"

    def test_both_filters_deterministic(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "X", "layer": "L0", "entity_type": "module"},
            {"adg_name": "Y", "layer": "L0", "entity_type": "class"},
        ]
        client = _make_client_with_nodes(nodes)
        r1 = ADGRedisClient.search_nodes(client, "", layer="L0")
        r2 = ADGRedisClient.search_nodes(client, "", layer="L0")
        assert r1 == r2
