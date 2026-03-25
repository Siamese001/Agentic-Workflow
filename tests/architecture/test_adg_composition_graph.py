"""Architecture tests for ADG composition graph (Graph 6, H5) and config reads (Graph 5, H4).

Plan ref: tests/architecture/test_adg_composition_graph.py
"""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    _AttributeVisitor,
    _CompositionVisitor,
    _DynamicExecutionVisitor,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_adg_composition_graph", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_composition_graph", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_composition_graph", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_composition_graph", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_composition_graph", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_composition_graph", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_composition_graph", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_composition_graph", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_composition_graph", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_composition_graph", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_composition_graph", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_composition_graph", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_composition_graph", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_composition_graph", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_composition_graph", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_composition_graph", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_composition_graph", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_composition_graph", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_composition_graph", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_composition_graph", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_composition_graph", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_composition_graph", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_composition_graph", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_composition_graph", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_composition_graph", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_composition_graph", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_composition_graph", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_composition_graph", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_composition_graph")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_composition_graph", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_composition_graph", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_composition_graph", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_adg_composition_graph", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_composition_graph", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_composition_graph", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_composition_graph", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_adg_composition_graph", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_composition_graph", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_composition_graph", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_composition_graph", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_composition_graph", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_composition_graph", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_composition_graph", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_composition_graph", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_composition_graph", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_composition_graph", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_composition_graph", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_composition_graph", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_composition_graph", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_composition_graph", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_composition_graph", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_composition_graph", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_composition_graph")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_composition_graph", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_composition_graph")
# REMOVED: emit_determinism_digest("p0", "test_adg_composition_graph")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_composition_graph", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_composition_graph", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_composition_graph", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_composition_graph", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_composition_graph", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_composition_graph", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_composition_graph", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_composition_graph", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_composition_graph", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_composition_graph", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_composition_graph", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_composition_graph", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_composition_graph", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_composition_graph", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_composition_graph", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_composition_graph", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_composition_graph", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_composition_graph", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_composition_graph", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_composition_graph", "exec_snapshot_link")


def _visit_comp(source: str, source_file: str = "test.py") -> list[Edge]:
    tree = ast.parse(source)
    visitor = _CompositionVisitor("ADG::Module::test", source_file)
    visitor.visit(tree)
    return visitor.edges


def _visit_attr(source: str, source_file: str = "test.py") -> list[Edge]:
    tree = ast.parse(source)
    visitor = _AttributeVisitor("ADG::Module::test", source_file)
    visitor.visit(tree)
    return visitor.edges


def _visit_dyn(source: str, source_file: str = "test.py") -> list[Edge]:
    tree = ast.parse(source)
    visitor = _DynamicExecutionVisitor("ADG::Module::test", source_file)
    visitor.visit(tree)
    return visitor.edges


class TestCompositionGraph:
    """Graph 6 — object composition in __init__ (instantiates edges)."""

    def test_self_assignment_in_init(self):
        src = """
class MyAgent:
    def __init__(self):
        self.provider = SomeProvider()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        assert edges[0].relation_type == "instantiates"
        assert edges[0].edge_kind == "composition"
        assert edges[0].symbol == "SomeProvider"

    def test_noise_constructors_excluded(self):
        src = """
class MyAgent:
    def __init__(self):
        self.data = dict()
        self.items = list()
        self.path = Path("/tmp")
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_outside_init_excluded(self):
        src = """
class MyAgent:
    def run(self):
        self.x = SomeProvider()
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_non_self_target_excluded(self):
        src = """
class MyAgent:
    def __init__(self):
        local = SomeProvider()
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_qualified_constructor(self):
        src = """
class MyAgent:
    def __init__(self):
        self.client = some.module.Client()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        assert edges[0].symbol == "Client"

    def test_multiple_compositions(self):
        src = """
class MyAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.cache = RedisCache()
"""
        edges = _visit_comp(src)
        assert len(edges) == 2
        syms = {e.symbol for e in edges}
        assert syms == {"LLMClient", "RedisCache"}


class TestConfigReadGraph:
    """Graph 5 — env/config reads (reads_from edges)."""

    def test_os_getenv_detected(self):
        src = "x = os.getenv('KEY')\n"
        edges = _visit_attr(src)
        assert any(e.relation_type == "reads_from" and e.edge_kind == "reads_env" for e in edges)

    def test_os_environ_detected(self):
        src = "x = os.environ.get('KEY')\n"
        edges = _visit_attr(src)
        assert any(e.edge_kind == "reads_env" for e in edges)


class TestDynamicExecutionGraph:
    """GF — dynamic execution (dynamic_exec edges, RULE_F)."""

    def test_eval_detected(self):
        src = "result = eval('1+1')\n"
        edges = _visit_dyn(src)
        assert any(e.edge_kind == "dynamic_exec" and e.symbol == "eval" for e in edges)

    def test_exec_detected(self):
        src = "exec('x = 1')\n"
        edges = _visit_dyn(src)
        assert any(e.edge_kind == "dynamic_exec" for e in edges)

    def test_importlib_detected(self):
        src = "importlib.import_module('some.mod')\n"
        edges = _visit_dyn(src)
        assert any(e.edge_kind == "dynamic_exec" for e in edges)

    def test_plain_call_not_flagged(self):
        src = "result = some_function()\n"
        edges = _visit_dyn(src)
        assert edges == []
