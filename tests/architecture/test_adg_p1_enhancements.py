"""Tests for ADG P1 enhancements: E1 (Symbol Inventory), E5 (Cycle Detection), E6 (Dead Imports).

Each enhancement is tested with both positive (feature works) and
negative (no false positives) cases using synthetic AST fixtures.
"""

from __future__ import annotations

import ast
import textwrap

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    ScanResult,
    _detect_cycles,
    _SymbolInventoryVisitor,
    _tag_dead_imports,
    _UnusedImportVisitor,
)
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_p1_enhancements")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_p1_enhancements", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_p1_enhancements", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_p1_enhancements", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_p1_enhancements", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_p1_enhancements", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_p1_enhancements", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_p1_enhancements", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_p1_enhancements", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_p1_enhancements", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_p1_enhancements", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_p1_enhancements", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_p1_enhancements", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_p1_enhancements", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_p1_enhancements", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_p1_enhancements", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_p1_enhancements", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_p1_enhancements", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_p1_enhancements", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_p1_enhancements", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_p1_enhancements", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_p1_enhancements", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_p1_enhancements", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_p1_enhancements", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_p1_enhancements", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_p1_enhancements", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_p1_enhancements", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_p1_enhancements", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_p1_enhancements", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_p1_enhancements", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_p1_enhancements", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_p1_enhancements", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_p1_enhancements", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_p1_enhancements", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_p1_enhancements", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_p1_enhancements", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_p1_enhancements", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_p1_enhancements", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_p1_enhancements", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_p1_enhancements", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_p1_enhancements", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_p1_enhancements", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_p1_enhancements", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_p1_enhancements", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_p1_enhancements", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_p1_enhancements", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_p1_enhancements", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_p1_enhancements", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_p1_enhancements", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_p1_enhancements", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_p1_enhancements", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_p1_enhancements", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_p1_enhancements")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_p1_enhancements", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_p1_enhancements")
# REMOVED: emit_determinism_digest("p0", "test_adg_p1_enhancements")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_p1_enhancements", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_p1_enhancements", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_p1_enhancements", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_p1_enhancements", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_p1_enhancements", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_p1_enhancements", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_p1_enhancements", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_p1_enhancements", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_p1_enhancements", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_p1_enhancements", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_p1_enhancements", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_p1_enhancements", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_p1_enhancements", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_p1_enhancements", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_p1_enhancements", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_p1_enhancements", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_p1_enhancements", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_p1_enhancements", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_p1_enhancements", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_p1_enhancements", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_module_adg(rel: str) -> str:
    return f"ADG::Module::{rel}"


def _parse(source: str) -> ast.Module:
    return ast.parse(textwrap.dedent(source))


def _make_import_edge(from_mod: str, to_sym: str, symbol: str = "", line_no: int = 1) -> Edge:
    return Edge(
        from_name=from_mod,
        relation_type="imports",
        to_name=to_sym,
        edge_kind="import",
        source_file=from_mod,
        line_no=line_no,
        symbol=symbol,
    )


def _make_module_edge(from_rel: str, to_rel: str) -> Edge:
    return Edge(
        from_name=_make_module_adg(from_rel),
        relation_type="imports",
        to_name=_make_module_adg(to_rel),
        edge_kind="import",
        source_file=from_rel,
        line_no=1,
        symbol="",
    )


# ===========================================================================
# E1: Symbol Inventory (_SymbolInventoryVisitor)
# ===========================================================================


class TestSymbolInventoryVisitor:
    """E1: Verify exports edges are emitted for public top-level symbols."""

    def test_public_function_emits_export_edge(self):
    """Test public_function_emits_export_edge runtime behavior."""
    # Arrange
    # TODO: Set up test data for public_function_emits_export_edge
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute public_function_emits_export_edge
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
            pass
        """
        tree = _parse(source)
        v = _SymbolInventoryVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py")
        v.visit(tree)
        symbols = {e.symbol for e in v.edges if e.relation_type == "exports"}
        assert "MyClass" in symbols

    def test_private_name_not_emitted_without_all(self):
        source = """
        def _private():
            pass
        class _Internal:
            pass
        """
        tree = _parse(source)
        v = _SymbolInventoryVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py")
        v.visit(tree)
        symbols = {e.symbol for e in v.edges if e.relation_type == "exports"}
        assert "_private" not in symbols
        assert "_Internal" not in symbols

    def test_all_controls_exports(self):
        source = """
        __all__ = ["PublicClass"]
        class PublicClass:
            pass
        class HiddenClass:
            pass
        """
        tree = _parse(source)
        v = _SymbolInventoryVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py")
        v.visit(tree)
        symbols = {e.symbol for e in v.edges if e.relation_type == "exports"}
        assert "PublicClass" in symbols
        assert "HiddenClass" not in symbols

    def test_constant_emits_export_edge(self):
        source = """
        MY_CONST = 42
        _PRIVATE_CONST = 99
        """
        tree = _parse(source)
        v = _SymbolInventoryVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py")
        v.visit(tree)
        symbols = {e.symbol for e in v.edges if e.relation_type == "exports"}
        assert "MY_CONST" in symbols
        assert "_PRIVATE_CONST" not in symbols

    def test_async_function_emits_export_edge(self):
    """Test async_function_emits_export_edge runtime behavior."""
    # Arrange
    # TODO: Set up test data for async_function_emits_export_edge
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute async_function_emits_export_edge
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
            pass
        """
        tree = _parse(source)
        v = _SymbolInventoryVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py")
        v.visit(tree)
        export_edges = [e for e in v.edges if e.relation_type == "exports"]
        assert len(export_edges) >= 1
        assert all(e.edge_kind == "export" for e in export_edges)

    def test_symbol_table_populated(self):
        source = """
        def greet():
            pass
        class Greeter:
            pass
        LIMIT = 10
        """
        tree = _parse(source)
        v = _SymbolInventoryVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py")
        v.visit(tree)
        assert "greet" in v.symbol_table
        assert "Greeter" in v.symbol_table
        assert "LIMIT" in v.symbol_table

    def test_to_name_uses_canonical_symbol_format(self):
        source = """
        def my_func():
            pass
        """
        tree = _parse(source)
        rel = "foo/bar.py"
        v = _SymbolInventoryVisitor(_make_module_adg(rel), rel)
        v.visit(tree)
        export_edges = [e for e in v.edges if e.symbol == "my_func"]
        assert len(export_edges) == 1
        assert export_edges[0].to_name == f"ADG::Symbol::{rel}::my_func"

    def test_empty_module_no_edges(self):
        tree = _parse("")
        v = _SymbolInventoryVisitor(_make_module_adg("empty.py"), "empty.py")
        v.visit(tree)
        assert v.edges == []

    def test_all_empty_list_emits_nothing(self):
        source = """
        __all__ = []
        def func():
            pass
        """
        tree = _parse(source)
        v = _SymbolInventoryVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py")
        v.visit(tree)
        export_edges = [e for e in v.edges if e.relation_type == "exports"]
        assert export_edges == []


# ===========================================================================
# E6: Unused Import Detection (_UnusedImportVisitor / _tag_dead_imports)
# ===========================================================================


class TestUnusedImportVisitor:
    """E6: Verify dead/live import classification."""

    def test_used_import_is_live(self):
        source = """
        import os
        x = os.path.join("a", "b")
        """
        tree = _parse(source)
        v = _UnusedImportVisitor()
        v.visit(tree)
        assert "os" in v.live_names
        assert "os" not in v.dead_names

    def test_unused_import_is_dead(self):
        source = """
        import sys
        x = 1
        """
        tree = _parse(source)
        v = _UnusedImportVisitor()
        v.visit(tree)
        assert "sys" in v.dead_names
        assert "sys" not in v.live_names

    def test_from_import_used_is_live(self):
        source = """
        from pathlib import Path
        p = Path("/tmp")
        """
        tree = _parse(source)
        v = _UnusedImportVisitor()
        v.visit(tree)
        assert "Path" in v.live_names

    def test_from_import_unused_is_dead(self):
        source = """
        from pathlib import Path
        x = 1
        """
        tree = _parse(source)
        v = _UnusedImportVisitor()
        v.visit(tree)
        assert "Path" in v.dead_names

    def test_aliased_import_tracks_alias(self):
        source = """
        import numpy as np
        arr = np.array([1, 2, 3])
        """
        tree = _parse(source)
        v = _UnusedImportVisitor()
        v.visit(tree)
        assert "np" in v.live_names
        assert "numpy" not in v.imported_names

    def test_aliased_import_dead(self):
        source = """
        import json as j
        x = 1
        """
        tree = _parse(source)
        v = _UnusedImportVisitor()
        v.visit(tree)
        assert "j" in v.dead_names

    def test_star_import_skipped(self):
        source = """
        from os.path import *
        """
        tree = _parse(source)
        v = _UnusedImportVisitor()
        v.visit(tree)
        assert "*" not in v.imported_names
        assert len(v.imported_names) == 0

    def test_multiple_imports_mixed(self):
        source = """
        import os
        import sys
        from pathlib import Path
        x = os.getcwd()
        p = Path("/")
        """
        tree = _parse(source)
        v = _UnusedImportVisitor()
        v.visit(tree)
        assert "os" in v.live_names
        assert "Path" in v.live_names
        assert "sys" in v.dead_names


class TestTagDeadImports:
    """E6: Verify _tag_dead_imports re-tags edges correctly."""

    def test_dead_import_edge_retagged(self):
        edges = [
            _make_import_edge("ADG::Module::a.py", "ADG::Symbol::sys", symbol="sys"),
        ]
        result = _tag_dead_imports(edges, dead_names={"sys"})
        assert len(result) == 1
        assert result[0].relation_type == "dead_imports"
        assert result[0].edge_kind == "dead_import"

    def test_live_import_edge_unchanged(self):
        edges = [
            _make_import_edge("ADG::Module::a.py", "ADG::Symbol::os", symbol="os"),
        ]
        result = _tag_dead_imports(edges, dead_names={"sys"})
        assert result[0].relation_type == "imports"
        assert result[0].edge_kind == "import"

    def test_empty_dead_names_no_changes(self):
        edges = [
            _make_import_edge("ADG::Module::a.py", "ADG::Symbol::os", symbol="os"),
            _make_import_edge("ADG::Module::a.py", "ADG::Symbol::sys", symbol="sys"),
        ]
        result = _tag_dead_imports(edges, dead_names=set())
        assert all(e.relation_type == "imports" for e in result)

    def test_non_import_edges_untouched(self):
        edges = [
            Edge(
                from_name="ADG::Module::a.py",
                relation_type="calls",
                to_name="ADG::Symbol::foo",
                edge_kind="call",
                source_file="a.py",
                line_no=1,
                symbol="foo",
            ),
        ]
        result = _tag_dead_imports(edges, dead_names={"foo"})
        assert result[0].relation_type == "calls"

    def test_from_import_symbol_tail_matched(self):
        edges = [
            _make_import_edge(
                "ADG::Module::a.py",
                "ADG::Symbol::pathlib.Path",
                symbol="pathlib.Path",
            ),
        ]
        result = _tag_dead_imports(edges, dead_names={"Path"})
        assert result[0].relation_type == "dead_imports"


# ===========================================================================
# E5: Cyclic Dependency Detection (_detect_cycles)
# ===========================================================================


def _make_scan_result_with_edges(edges: list[Edge]) -> ScanResult:
    result = ScanResult()
    result.edges = sorted(set(edges))
    result.modules = []
    return result


class TestDetectCycles:
    """E5: Verify SCC-based cycle detection produces correct in_cycle edges."""

    def test_simple_two_node_cycle(self):
        edges = [
            _make_module_edge("a.py", "b.py"),
            _make_module_edge("b.py", "a.py"),
        ]
        result = _make_scan_result_with_edges(edges)
        cycle_edges = _detect_cycles(result)
        assert len(cycle_edges) >= 2
        assert all(e.relation_type == "in_cycle" for e in cycle_edges)
        assert all(e.edge_kind == "cycle" for e in cycle_edges)

    def test_three_node_cycle(self):
        edges = [
            _make_module_edge("a.py", "b.py"),
            _make_module_edge("b.py", "c.py"),
            _make_module_edge("c.py", "a.py"),
        ]
        result = _make_scan_result_with_edges(edges)
        cycle_edges = _detect_cycles(result)
        assert len(cycle_edges) == 3
        cycle_nodes = {e.to_name for e in cycle_edges}
        assert len(cycle_nodes) == 1

    def test_no_cycle_dag(self):
        edges = [
            _make_module_edge("a.py", "b.py"),
            _make_module_edge("b.py", "c.py"),
        ]
        result = _make_scan_result_with_edges(edges)
        cycle_edges = _detect_cycles(result)
        assert cycle_edges == []

    def test_self_loop_not_a_multi_node_scc(self):
        edges = [
            _make_module_edge("a.py", "a.py"),
        ]
        result = _make_scan_result_with_edges(edges)
        cycle_edges = _detect_cycles(result)
        assert cycle_edges == []

    def test_two_independent_cycles(self):
        edges = [
            _make_module_edge("a.py", "b.py"),
            _make_module_edge("b.py", "a.py"),
            _make_module_edge("c.py", "d.py"),
            _make_module_edge("d.py", "c.py"),
        ]
        result = _make_scan_result_with_edges(edges)
        cycle_edges = _detect_cycles(result)
        cycle_nodes = {e.to_name for e in cycle_edges}
        assert len(cycle_nodes) == 2

    def test_empty_graph_no_cycles(self):
        result = _make_scan_result_with_edges([])
        cycle_edges = _detect_cycles(result)
        assert cycle_edges == []

    def test_cycle_node_uses_adg_cycle_prefix(self):
        edges = [
            _make_module_edge("a.py", "b.py"),
            _make_module_edge("b.py", "a.py"),
        ]
        result = _make_scan_result_with_edges(edges)
        cycle_edges = _detect_cycles(result)
        assert all(e.to_name.startswith("ADG::Cycle::") for e in cycle_edges)

    def test_non_module_edges_excluded_from_cycle_detection(self):
        """Edges where from_name or to_name is a Symbol (not a Module) are excluded."""
        edges = [
            Edge(
                from_name=_make_module_adg("a.py"),
                relation_type="reads_from",
                to_name="ADG::Symbol::some.config.VALUE",
                edge_kind="import",
                source_file="a.py",
                line_no=1,
                symbol="VALUE",
            ),
            Edge(
                from_name="ADG::Symbol::some.config.VALUE",
                relation_type="reads_from",
                to_name=_make_module_adg("a.py"),
                edge_kind="import",
                source_file="some/config.py",
                line_no=1,
                symbol="",
            ),
        ]
        result = _make_scan_result_with_edges(edges)
        cycle_edges = _detect_cycles(result)
        assert len(cycle_edges) == 0

    def test_cycle_hash_deterministic(self):
        edges = [
            _make_module_edge("a.py", "b.py"),
            _make_module_edge("b.py", "a.py"),
        ]
        result = _make_scan_result_with_edges(edges)
        run1 = _detect_cycles(result)
        run2 = _detect_cycles(result)
        assert [e.to_name for e in run1] == [e.to_name for e in run2]

    def test_calls_edges_included_in_cycle_detection(self):
    """Test calls_edges_included_in_cycle_detection runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute calls_edges_included_in_cycle_detection
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        cycle_edges = _detect_cycles(result)
        assert len(cycle_edges) >= 2


# ===========================================================================
# Integration: confidence scoring of new edge types
# ===========================================================================


class TestConfidenceScoringNewEdges:
    """Verify confidence.py correctly scores E1/E5/E6 edge types."""

    def test_exports_edge_scores_1_0(self):
        from agentic_core.adg.analysis.EdgeConfidence import score_edge

        edge = Edge(
            from_name="ADG::Module::foo.py",
            relation_type="exports",
            to_name="ADG::Symbol::foo.py::MyClass",
            edge_kind="export",
            source_file="foo.py",
            line_no=5,
            symbol="MyClass",
        )
        ec = score_edge(edge)
        assert ec.confidence == 1.0
        assert ec.provenance == "ast_symbol_inventory"

    def test_dead_imports_edge_scores_1_0(self):
        from agentic_core.adg.analysis.EdgeConfidence import score_edge

        edge = Edge(
            from_name="ADG::Module::foo.py",
            relation_type="dead_imports",
            to_name="ADG::Symbol::sys",
            edge_kind="dead_import",
            source_file="foo.py",
            line_no=1,
            symbol="sys",
        )
        ec = score_edge(edge)
        assert ec.confidence == 1.0
        assert ec.provenance == "ast_dead_import"

    def test_in_cycle_edge_scores_0_95(self):
        from agentic_core.adg.analysis.EdgeConfidence import score_edge

        edge = Edge(
            from_name="ADG::Module::a.py",
            relation_type="in_cycle",
            to_name="ADG::Cycle::abcdef1234567890",
            edge_kind="cycle",
            source_file="a.py",
            line_no=0,
            symbol="cycle:abcdef1234567890",
        )
        ec = score_edge(edge)
        assert ec.confidence == 0.95
        assert ec.provenance == "ast_cycle_detection"


# ===========================================================================
# Integration: repair routing of new edge types
# ===========================================================================


class TestRepairRoutingNewEdges:
    """Verify repair.py routes E5 and E6 edges to the right agents."""

    def _cycle_edge(self) -> Edge:
        return Edge(
            from_name="ADG::Module::a.py",
            relation_type="in_cycle",
            to_name="ADG::Cycle::abc123",
            edge_kind="cycle",
            source_file="a.py",
            line_no=0,
            symbol="cycle:abc123",
        )

    def _dead_edge(self) -> Edge:
        return Edge(
            from_name="ADG::Module::a.py",
            relation_type="dead_imports",
            to_name="ADG::Symbol::sys",
            edge_kind="dead_import",
            source_file="a.py",
            line_no=1,
            symbol="sys",
        )

    def test_cycle_routes_to_architecture_governor(self):
        from agentic_core.adg.analysis.RepairRoute import route_violations

        routes = route_violations([self._cycle_edge()])
        assert len(routes) == 1
        assert routes[0].recommended_agent == "ArchitectureGovernorAgent"
        assert routes[0].ci_lane == "layer_guard"
        assert routes[0].severity == "high"

    def test_dead_import_routes_to_dependency_repair(self):
        from agentic_core.adg.analysis.RepairRoute import route_violations

        routes = route_violations([self._dead_edge()])
        assert len(routes) == 1
        assert routes[0].recommended_agent == "DependencyRepairAgent"
        assert routes[0].ci_lane == "dep_check"
        assert routes[0].severity == "low"

    def test_route_violations_sorted_by_severity(self):
        from agentic_core.adg.analysis.RepairRoute import route_violations

        routes = route_violations([self._dead_edge(), self._cycle_edge()])
        severities = [r.severity for r in routes]
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        assert sorted(severities, key=lambda s: order[s]) == severities
