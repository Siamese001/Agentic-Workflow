"""Tests for ADG composition graph (Graph 6, H5) — _CompositionVisitor."""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    _AttributeVisitor,
    _CompositionVisitor,
    _DynamicExecutionVisitor,
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

_emit_records_execution_trace("p0", "evidence", "test_adg_composition_graph")
_emit_applies_guardrail("p0", "test_adg_composition_graph", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_composition_graph", "policy_binding")
_emit_snapshots_state("p0", "test_adg_composition_graph", "state_snapshot")
emit_replay_key("p0", "test_adg_composition_graph")
emit_determinism_digest("p0", "test_adg_composition_graph")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_composition_graph", "execution_auth")
_emit_validates_capability("p2", "test_adg_composition_graph", "capability_check")
_emit_routes_to_capability("p2", "test_adg_composition_graph", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_composition_graph", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_composition_graph", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_composition_graph", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_composition_graph", "exec_output")
_emit_dispatches_agent("p3", "test_adg_composition_graph", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_composition_graph", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_composition_graph", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_composition_graph", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_composition_graph", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_composition_graph", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_composition_graph", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_composition_graph", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_composition_graph", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_composition_graph", "eval_metric")
_emit_stores_embedding("p4", "test_adg_composition_graph", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_composition_graph", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_composition_graph", "exec_snapshot_link")


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


class TestCompositionVisitor:
    def test_self_assignment_in_init(self):
        src = """
class MyAgent:
    def __init__(self):
        self.provider = SomeProvider()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        e = edges[0]
        assert e.relation_type == "instantiates"
        assert e.edge_kind == "composition"
        assert e.symbol == "SomeProvider"

    def test_noise_constructors_excluded(self):
        src = """
class MyAgent:
    def __init__(self):
        self.data = dict()
        self.items = list()
        self.val = str()
        self.p = Path("/tmp")
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_non_init_method_excluded(self):
        src = """
class MyAgent:
    def run(self):
        self.local = SomeProvider()
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_non_self_assignment_excluded(self):
        src = """
class MyAgent:
    def __init__(self):
        local_var = SomeProvider()
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_multiple_compositions(self):
        src = """
class BigAgent:
    def __init__(self):
        self.llm = LLMGateway()
        self.store = VectorStore()
        self.router = SemanticRouter()
"""
        edges = _visit_comp(src)
        assert len(edges) == 3
        symbols = {e.symbol for e in edges}
        assert symbols == {"LLMGateway", "VectorStore", "SemanticRouter"}

    def test_class_name_in_from(self):
        src = """
class SpecificAgent:
    def __init__(self):
        self.dep = DepClass()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        assert "SpecificAgent" in edges[0].from_name

    def test_attribute_constructor(self):
        src = """
class Agent:
    def __init__(self):
        self.client = llm_provider.OpenAIClient()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        assert edges[0].symbol == "OpenAIClient"


class TestAttributeVisitor:
    def test_os_getenv(self):
        src = """
import os
val = os.getenv("KEY")
"""
        edges = _visit_attr(src)
        assert any(e.relation_type == "reads_from" and "getenv" in e.symbol for e in edges)

    def test_os_environ(self):
        src = """
import os
val = os.environ.get("KEY")
"""
        edges = _visit_attr(src)
        assert any(e.relation_type == "reads_from" for e in edges)

    def test_no_false_positives_on_regular_calls(self):
        src = """
result = some_func()
x = other.method()
"""
        edges = _visit_attr(src)
        assert edges == []


class TestDynamicExecutionVisitor:
    def test_eval_detected(self):
        src = """
result = eval("1+1")
"""
        edges = _visit_dyn(src)
        assert len(edges) == 1
        assert edges[0].symbol == "eval"
        assert edges[0].edge_kind == "dynamic_exec"

    def test_exec_detected(self):
        src = """
exec("print('hello')")
"""
        edges = _visit_dyn(src)
        assert any(e.symbol == "exec" for e in edges)

    def test_importlib_detected(self):
        src = """
import importlib
mod = importlib.import_module("some.mod")
"""
        edges = _visit_dyn(src)
        assert any("import_module" in e.symbol for e in edges)

    def test_regular_calls_not_flagged(self):
        src = """
result = my_function()
x = obj.method()
"""
        edges = _visit_dyn(src)
        assert edges == []
