"""Architecture tests for ADG inheritance graph (Graph 3, H3).

Plan ref: tests/architecture/test_adg_inheritance_graph.py
"""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    _InheritanceVisitor,
    run_scanner_self_test,
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

_emit_records_execution_trace("p0", "evidence", "test_adg_inheritance_graph")
_emit_applies_guardrail("p0", "test_adg_inheritance_graph", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_inheritance_graph", "policy_binding")
_emit_snapshots_state("p0", "test_adg_inheritance_graph", "state_snapshot")
emit_replay_key("p0", "test_adg_inheritance_graph")
emit_determinism_digest("p0", "test_adg_inheritance_graph")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_inheritance_graph", "execution_auth")
_emit_validates_capability("p2", "test_adg_inheritance_graph", "capability_check")
_emit_routes_to_capability("p2", "test_adg_inheritance_graph", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_inheritance_graph", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_inheritance_graph", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_inheritance_graph", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_inheritance_graph", "exec_output")
_emit_dispatches_agent("p3", "test_adg_inheritance_graph", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_inheritance_graph", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_inheritance_graph", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_inheritance_graph", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_inheritance_graph", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_inheritance_graph", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_inheritance_graph", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_inheritance_graph", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_inheritance_graph", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_inheritance_graph", "eval_metric")
_emit_stores_embedding("p4", "test_adg_inheritance_graph", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_inheritance_graph", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_inheritance_graph", "exec_snapshot_link")


def _parse_and_visit(
    source: str,
    module_adg: str = "ADG::Module::test",
    source_file: str = "test.py",
) -> list[Edge]:
    tree = ast.parse(source)
    visitor = _InheritanceVisitor(module_adg, source_file)
    visitor.visit(tree)
    return visitor.edges


class TestInheritanceGraph:
    """Graph 3 — class inheritance (implements) edges."""

    def test_single_base_class(self):
        src = """
class ConcreteAgent(SovereignBaseAgent):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        e = edges[0]
        assert e.relation_type == "implements"
        assert e.symbol == "SovereignBaseAgent"
        assert e.edge_kind == "unresolved"

    def test_multiple_inheritance(self):
        src = """
class MultiAgent(BaseA, BaseB):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 2
        syms = {e.symbol for e in edges}
        assert syms == {"BaseA", "BaseB"}

    def test_object_base_excluded(self):
        src = """
class PlainClass(object):
    pass
"""
        edges = _parse_and_visit(src)
        assert edges == []

    def test_internal_base_resolved(self):
        src = """
class MyAgent(agentic_core.base.SovereignBaseAgent):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        assert edges[0].edge_kind == "resolved_internal"

    def test_external_qualified_base(self):
        src = """
class MyModel(pydantic.BaseModel):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        assert edges[0].edge_kind == "external"

    def test_no_bases(self):
        src = """
class Standalone:
    pass
"""
        edges = _parse_and_visit(src)
        assert edges == []

    def test_nested_class_captured(self):
        src = """
class Outer:
    class Inner(SomeBase):
        pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        assert edges[0].symbol == "SomeBase"

    def test_line_number_recorded(self):
        src = "\nclass Agent(Base):\n    pass\n"
        edges = _parse_and_visit(src)
        assert edges[0].line_no == 2


class TestScannerSelfTestS1:
    """S1: Scanner self-test validates all graph types."""

    def test_self_test_passes(self):
        assert run_scanner_self_test() is True
