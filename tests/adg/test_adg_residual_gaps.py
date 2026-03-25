"""Residual gap coverage for static_scanner.py and builder.py.

Targets the uncovered lines from the coverage report after test_adg_visitors_rigorous.py:

  static_scanner.py residual gaps (lines 1545-2305):
  - _DecoratorVisitor._extract_decorator_name (Call node branch)
  - _SymbolInventoryVisitor: exports, __all__ filter, _extract_all, async fn, class,
    constant, type_alias, private skip, non-zero col_offset skip
  - _UnusedImportVisitor: dead_names / live_names properties, __future__ skip,
    star skip, asname handling, attribute usage tracking
  - _tag_dead_imports: re-tagging dead import edges
  - _detect_cycles: Kosaraju SCC, single-node SCC skip, empty graph
  - _emit_layer_violation_edges: forbidden cross-layer, same-layer skip,
    allowed-layer skip, L_UNKNOWN skip, dedup
  - _repo_relative: path outside repo_root (ValueError branch)
  - _scan_file: SyntaxError and OSError branches
  - _check_evidence_floors: floor pass and floor fail
  - _check_cardinality: LOW and HIGH violation branches
  - run_scanner_self_test: passes with sample code
  - ADGStaticScanner.scan_files: scan a specific file list
  - ADGStaticScanner.build_reverse_import_graph
  - ADGStaticScanner.module_layer_map

  builder.py residual gaps (lines 292, 347, 457, 465, 560, 588):
  - _populate_module_entities: skip already-existing adg_name (line 292)
  - _populate_symbol_entities: skip already-existing adg_target (line 347)
  - _compute_structural_metrics: cycle violation counting (line 457/465)
  - _collect_blind_spots: manifest is None path (line 588->exit)
"""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    ScanResult,
    _detect_cycles,
    _emit_layer_violation_edges,
    _tag_dead_imports,
    run_scanner_self_test,
)
from agentic_core.adg.schema_util import canonical_name
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_residual_gaps")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_residual_gaps", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_residual_gaps", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_residual_gaps", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_residual_gaps", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_residual_gaps", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_residual_gaps", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_residual_gaps", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_residual_gaps", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_residual_gaps", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_residual_gaps", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_residual_gaps", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_residual_gaps", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_residual_gaps", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_residual_gaps", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_residual_gaps", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_residual_gaps", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_residual_gaps", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_residual_gaps", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_residual_gaps", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_residual_gaps", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_residual_gaps", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_residual_gaps", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_residual_gaps", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_residual_gaps", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_residual_gaps", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_residual_gaps", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_residual_gaps", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_residual_gaps", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_residual_gaps", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_residual_gaps", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_residual_gaps", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_residual_gaps", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_residual_gaps", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_residual_gaps", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_residual_gaps", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_residual_gaps", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_residual_gaps", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_residual_gaps", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_residual_gaps", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_residual_gaps", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_residual_gaps", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_residual_gaps", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_residual_gaps", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_residual_gaps", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_residual_gaps", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_residual_gaps", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_residual_gaps", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_residual_gaps", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_residual_gaps", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_residual_gaps", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_residual_gaps", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_residual_gaps")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_residual_gaps", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_residual_gaps")
# REMOVED: emit_determinism_digest("p0", "test_adg_residual_gaps")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_residual_gaps", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_residual_gaps", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_residual_gaps", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_residual_gaps", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_residual_gaps", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_residual_gaps", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_residual_gaps", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_residual_gaps", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_residual_gaps", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_residual_gaps", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_residual_gaps", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_residual_gaps", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_residual_gaps", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_residual_gaps", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_residual_gaps", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_residual_gaps", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_residual_gaps", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_residual_gaps", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_residual_gaps", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_residual_gaps", "exec_snapshot_link")

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _parse(src: str) -> ast.Module:
    return ast.parse(src)


def _module_edge(from_path: str, to_path: str, rel_type: str = "imports") -> Edge:
    return Edge(
        from_name=canonical_name("Module", from_path),
        relation_type=rel_type,
        to_name=canonical_name("Module", to_path),
        edge_kind="import",
        source_file=from_path,
        line_no=1,
        symbol=to_path.replace("/", ".").replace(".py", ""),
    )


def _import_edge(from_path: str, symbol: str, edge_kind: str = "import") -> Edge:
    return Edge(
        from_name=canonical_name("Module", from_path),
        relation_type="imports",
        to_name=canonical_name("Symbol", symbol),
        edge_kind=edge_kind,
        source_file=from_path,
        line_no=1,
        symbol=symbol,
    )


# ─────────────────────────────────────────────────────────────────────────────
# _DecoratorVisitor — Call node branch in _extract_decorator_name
# ─────────────────────────────────────────────────────────────────────────────


class TestDecoratorVisitorCallBranch:
    def test_call_decorator_extracts_name(self):
        """@app.route('/') — decorator is a Call node, inner func is Attribute."""
        from agentic_core.adg.extraction.static_scanner import _DecoratorVisitor

        src = "@app.route('/')\ndef view(): pass\n"
        tree = _parse(src)
        module_adg = canonical_name("Module", "pkg/mod.py")
        visitor = _DecoratorVisitor(module_adg, "pkg/mod.py")
        visitor.visit(tree)
        dec_edges = [e for e in visitor.edges if e.relation_type == "decorated_by"]
        assert dec_edges, "Call-style decorator should emit decorated_by edge"
        assert any("route" in e.symbol or "app" in e.symbol for e in dec_edges)

    def test_bare_name_decorator(self):
        from agentic_core.adg.extraction.static_scanner import _DecoratorVisitor

        src = "@staticmethod\ndef foo(): pass\n"
        tree = _parse(src)
        module_adg = canonical_name("Module", "pkg/mod.py")
        visitor = _DecoratorVisitor(module_adg, "pkg/mod.py")
        visitor.visit(tree)
        dec_edges = [e for e in visitor.edges if e.relation_type == "decorated_by"]
        assert dec_edges
        assert dec_edges[0].symbol == "staticmethod"

    def test_governance_decorator_skipped(self):
        from agentic_core.adg.extraction.static_scanner import (
            _GOVERNANCE_WRITE_SYMBOLS,
            _DecoratorVisitor,
        )

        sym = next(iter(_GOVERNANCE_WRITE_SYMBOLS))
        src = f"@{sym}\ndef foo(): pass\n"
        tree = _parse(src)
        module_adg = canonical_name("Module", "pkg/mod.py")
        visitor = _DecoratorVisitor(module_adg, "pkg/mod.py")
        visitor.visit(tree)
        dec_edges = [e for e in visitor.edges if e.relation_type == "decorated_by"]
        assert not dec_edges, "Governance write decorator should be skipped"

    def test_class_decorator(self):
        from agentic_core.adg.extraction.static_scanner import _DecoratorVisitor

        src = "@dataclass\nclass Foo: pass\n"
        tree = _parse(src)
        module_adg = canonical_name("Module", "pkg/mod.py")
        visitor = _DecoratorVisitor(module_adg, "pkg/mod.py")
        visitor.visit(tree)
        dec_edges = [e for e in visitor.edges if e.relation_type == "decorated_by"]
        assert dec_edges
        assert dec_edges[0].symbol == "dataclass"


# ─────────────────────────────────────────────────────────────────────────────
# _SymbolInventoryVisitor
# ─────────────────────────────────────────────────────────────────────────────


class TestSymbolInventoryVisitor:
    def _visit(self, src: str, source_file: str = "pkg/mod.py"):
        from agentic_core.adg.extraction.static_scanner import _SymbolInventoryVisitor

        tree = _parse(src)
        module_adg = canonical_name("Module", source_file)
        visitor = _SymbolInventoryVisitor(module_adg, source_file)
        visitor.visit(tree)
        return visitor

    def test_public_function_exported(self):
        v = self._visit("def my_func(): pass\n")
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert any(e.symbol == "my_func" for e in exports)
        assert "my_func" in v.symbol_table

    def test_private_function_not_exported(self):
        v = self._visit("def _private(): pass\n")
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert not any(e.symbol == "_private" for e in exports)
        assert "_private" in v.symbol_table

    def test_async_function_exported(self):
        v = self._visit("async def async_handler(): pass\n")
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert any(e.symbol == "async_handler" for e in exports)

    def test_class_exported(self):
        v = self._visit("class MyClass: pass\n")
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert any(e.symbol == "MyClass" for e in exports)
        assert "MyClass" in v.symbol_table

    def test_constant_at_module_level_exported(self):
        v = self._visit("MY_CONST = 42\n")
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert any(e.symbol == "MY_CONST" for e in exports)

    def test_type_alias_exported(self):
        v = self._visit("MyAlias: int = 0\n")
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert any(e.symbol == "MyAlias" for e in exports)

    def test_dunder_all_filters_exports(self):
        src = "__all__ = ['pub_a']\ndef pub_a(): pass\ndef pub_b(): pass\n"
        v = self._visit(src)
        exports = [e for e in v.edges if e.relation_type == "exports"]
        syms = {e.symbol for e in exports}
        assert "pub_a" in syms
        assert "pub_b" not in syms, "__all__ should exclude pub_b"

    def test_dunder_all_tuple_form(self):
        src = "__all__ = ('alpha',)\ndef alpha(): pass\ndef beta(): pass\n"
        v = self._visit(src)
        exports = [e for e in v.edges if e.relation_type == "exports"]
        syms = {e.symbol for e in exports}
        assert "alpha" in syms
        assert "beta" not in syms

    def test_version_and_author_skipped(self):
        src = "__version__ = '1.0'\n__author__ = 'x'\nFOO = 1\n"
        v = self._visit(src)
        exports = [e for e in v.edges if e.relation_type == "exports"]
        syms = {e.symbol for e in exports}
        assert "__version__" not in syms
        assert "__author__" not in syms
        assert "FOO" in syms

    def test_non_zero_col_offset_assign_skipped(self):
        # Indented assignment (col_offset != 0) should not be collected
        src = "class Foo:\n    INNER = 1\n"
        v = self._visit(src)
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert not any(e.symbol == "INNER" for e in exports)

    def test_non_zero_col_offset_ann_assign_skipped(self):
        src = "class Foo:\n    x: int = 0\n"
        v = self._visit(src)
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert not any(e.symbol == "x" for e in exports)

    def test_export_edge_kind(self):
        v = self._visit("def foo(): pass\n")
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert all(e.edge_kind == "export" for e in exports)

    def test_export_to_name_contains_source_and_symbol(self):
        v = self._visit("def foo(): pass\n", "my/module.py")
        exports = [e for e in v.edges if e.relation_type == "exports"]
        assert exports
        assert "my/module.py" in exports[0].to_name
        assert "foo" in exports[0].to_name


# ─────────────────────────────────────────────────────────────────────────────
# _UnusedImportVisitor
# ─────────────────────────────────────────────────────────────────────────────


class TestUnusedImportVisitor:
    def _visit(self, src: str):
        from agentic_core.adg.extraction.static_scanner import _UnusedImportVisitor

        tree = _parse(src)
        visitor = _UnusedImportVisitor()
        visitor.visit(tree)
        return visitor

    def test_used_import_is_live(self):
        src = "import os\nos.path.join('a', 'b')\n"
        v = self._visit(src)
        assert "os" in v.live_names
        assert "os" not in v.dead_names

    def test_unused_import_is_dead(self):
        src = "import os\n"
        v = self._visit(src)
        assert "os" in v.dead_names
        assert "os" not in v.live_names

    def test_future_import_excluded(self):
        src = "from __future__ import annotations\n"
        v = self._visit(src)
        assert "annotations" not in v.imported_names
        assert "annotations" not in v.dead_names

    def test_star_import_excluded(self):
        src = "from some.module import *\n"
        v = self._visit(src)
        assert "*" not in v.imported_names

    def test_asname_tracks_local(self):
        src = "import numpy as np\nnp.array([1])\n"
        v = self._visit(src)
        assert "np" in v.live_names
        assert "numpy" not in v.imported_names  # "np" is the local name

    def test_from_import_asname(self):
        src = "from pathlib import Path as P\nP('/')\n"
        v = self._visit(src)
        assert "P" in v.live_names

    def test_from_import_dead(self):
        src = "from pathlib import Path\n"
        v = self._visit(src)
        assert "Path" in v.dead_names

    def test_attribute_usage_tracks_base(self):
        src = "import json\nx = json.loads('{}')\n"
        v = self._visit(src)
        assert "json" in v.live_names

    def test_del_target_counts_as_usage(self):
        src = "import os\ndel os\n"
        v = self._visit(src)
        assert "os" in v.live_names

    def test_import_plain_name_first_segment(self):
        """'import a.b.c' registers 'a' as the local name."""
        src = "import os.path\n"
        v = self._visit(src)
        assert "os" in v.imported_names


# ─────────────────────────────────────────────────────────────────────────────
# _tag_dead_imports
# ─────────────────────────────────────────────────────────────────────────────


class TestTagDeadImports:
    def test_dead_import_re_tagged(self):
        edge = _import_edge("pkg/mod.py", "unused_mod")
        result = _tag_dead_imports([edge], {"unused_mod"})
        assert len(result) == 1
        assert result[0].relation_type == "dead_imports"
        assert result[0].edge_kind == "dead_import"
        assert result[0].symbol == "unused_mod"

    def test_live_import_unchanged(self):
        edge = _import_edge("pkg/mod.py", "os")
        result = _tag_dead_imports([edge], set())
        assert result[0].relation_type == "imports"
        assert result[0].edge_kind == "import"

    def test_dotted_symbol_last_segment_match(self):
        edge = _import_edge("pkg/mod.py", "some.pkg.DeadClass")
        result = _tag_dead_imports([edge], {"DeadClass"})
        assert result[0].relation_type == "dead_imports"

    def test_non_imports_relation_unchanged(self):
        edge = Edge(
            from_name="ADG::Module::a.py",
            relation_type="calls",
            to_name="ADG::Symbol::foo",
            edge_kind="call",
            source_file="a.py",
            line_no=1,
            symbol="foo",
        )
        result = _tag_dead_imports([edge], {"foo"})
        assert result[0].relation_type == "calls"

    def test_mixed_list(self):
        dead_edge = _import_edge("pkg/mod.py", "dead_mod")
        live_edge = _import_edge("pkg/mod.py", "live_mod")
        result = _tag_dead_imports([dead_edge, live_edge], {"dead_mod"})
        rels = [e.relation_type for e in result]
        assert rels[0] == "dead_imports"
        assert rels[1] == "imports"

    def test_empty_dead_names(self):
        edge = _import_edge("pkg/mod.py", "some_mod")
        result = _tag_dead_imports([edge], set())
        assert result[0].relation_type == "imports"

    def test_empty_edges(self):
        assert _tag_dead_imports([], {"anything"}) == []


# ─────────────────────────────────────────────────────────────────────────────
# _detect_cycles
# ─────────────────────────────────────────────────────────────────────────────


class TestDetectCycles:
    def _make_result(self, edges: list[Edge]) -> ScanResult:
        modules = list({e.source_file for e in edges if e.source_file and e.source_file != "_"})
        return ScanResult(edges=edges, modules=modules)

    def test_no_edges_returns_empty(self):
        result = ScanResult(edges=[], modules=[])
        assert _detect_cycles(result) == []

    def test_no_module_module_edges_returns_empty(self):
        """Only symbol-to-symbol edges: no cycle."""
        edge = Edge(
            from_name="ADG::Symbol::foo",
            relation_type="imports",
            to_name="ADG::Symbol::bar",
            edge_kind="import",
            source_file="foo.py",
            line_no=1,
            symbol="bar",
        )
        result = ScanResult(edges=[edge], modules=["foo.py"])
        assert _detect_cycles(result) == []

    def test_simple_two_node_cycle(self):
        """A -> B -> A forms a cycle."""
        a = "agentic_core/L0_routing/mod_a.py"
        b = "agentic_core/L0_routing/mod_b.py"
        edges = [
            _module_edge(a, b),
            _module_edge(b, a),
        ]
        result = self._make_result(edges)
        cycle_edges = _detect_cycles(result)
        assert cycle_edges, "Two-node mutual import should produce in_cycle edges"
        assert all(e.relation_type == "in_cycle" for e in cycle_edges)
        assert all(e.edge_kind == "cycle" for e in cycle_edges)
        # Both A and B should appear
        members = {e.from_name for e in cycle_edges}
        assert canonical_name("Module", a) in members
        assert canonical_name("Module", b) in members

    def test_three_node_cycle(self):
        a = "agentic_core/L0_routing/a.py"
        b = "agentic_core/L0_routing/b.py"
        c = "agentic_core/L0_routing/c.py"
        edges = [
            _module_edge(a, b),
            _module_edge(b, c),
            _module_edge(c, a),
        ]
        result = self._make_result(edges)
        cycle_edges = _detect_cycles(result)
        assert len(cycle_edges) == 3
        members = {e.from_name for e in cycle_edges}
        assert canonical_name("Module", a) in members
        assert canonical_name("Module", b) in members
        assert canonical_name("Module", c) in members

    def test_single_node_self_loop_forms_no_scc(self):
        """A -> A (self-loop) is a cycle of size 1 and should be skipped
        (Kosaraju emits SCCs with >1 node only)."""
        a = "agentic_core/L0_routing/self.py"
        edge = _module_edge(a, a)
        result = self._make_result([edge])
        cycle_edges = _detect_cycles(result)
        assert cycle_edges == [], "Self-loop SCC size=1, should be skipped"

    def test_dag_no_cycle(self):
        a = "agentic_core/L0_routing/a.py"
        b = "agentic_core/L0_routing/b.py"
        c = "agentic_core/L0_routing/c.py"
        edges = [_module_edge(a, b), _module_edge(b, c)]
        result = self._make_result(edges)
        assert _detect_cycles(result) == []

    def test_cycle_to_name_is_adg_cycle_node(self):
        a = "agentic_core/L0_routing/a.py"
        b = "agentic_core/L0_routing/b.py"
        edges = [_module_edge(a, b), _module_edge(b, a)]
        result = self._make_result(edges)
        cycle_edges = _detect_cycles(result)
        assert all(e.to_name.startswith("ADG::Cycle::") for e in cycle_edges)

    def test_cycle_symbol_contains_hash(self):
        a = "agentic_core/L0_routing/a.py"
        b = "agentic_core/L0_routing/b.py"
        edges = [_module_edge(a, b), _module_edge(b, a)]
        result = self._make_result(edges)
        cycle_edges = _detect_cycles(result)
        assert all(e.symbol.startswith("cycle:") for e in cycle_edges)

    def test_calls_relation_also_counted(self):
        """'calls' edges between modules also count toward cycle detection."""
        a = "agentic_core/L0_routing/a.py"
        b = "agentic_core/L0_routing/b.py"
        edges = [
            _module_edge(a, b, "calls"),
            _module_edge(b, a, "calls"),
        ]
        result = self._make_result(edges)
        cycle_edges = _detect_cycles(result)
        assert cycle_edges, "calls-relation cycle should be detected"


# ─────────────────────────────────────────────────────────────────────────────
# _emit_layer_violation_edges
# ─────────────────────────────────────────────────────────────────────────────


class TestEmitLayerViolationEdges:
    def _result_with_import(self, from_path: str, symbol: str) -> ScanResult:
        edge = Edge(
            from_name=canonical_name("Module", from_path),
            relation_type="imports",
            to_name=canonical_name("Symbol", symbol),
            edge_kind="import",
            source_file=from_path,
            line_no=1,
            symbol=symbol,
        )
        return ScanResult(edges=[edge], modules=[from_path])

    def test_non_imports_edge_skipped(self):
        edge = Edge(
            from_name=canonical_name("Module", "agentic_core/L0_routing/a.py"),
            relation_type="calls",
            to_name=canonical_name("Symbol", "agentic_core.L5_safety.foo"),
            edge_kind="call",
            source_file="agentic_core/L0_routing/a.py",
            line_no=1,
            symbol="agentic_core.L5_safety.foo",
        )
        result = ScanResult(edges=[edge], modules=["agentic_core/L0_routing/a.py"])
        assert _emit_layer_violation_edges(result) == []

    def test_unknown_from_layer_skipped(self):
        edge = Edge(
            from_name=canonical_name("Module", "random/unknown/path.py"),
            relation_type="imports",
            to_name=canonical_name("Symbol", "agentic_core.L5_safety.foo"),
            edge_kind="import",
            source_file="random/unknown/path.py",
            line_no=1,
            symbol="agentic_core.L5_safety.foo",
        )
        result = ScanResult(edges=[edge], modules=["random/unknown/path.py"])
        assert _emit_layer_violation_edges(result) == []

    def test_unknown_to_layer_skipped(self):
        result = self._result_with_import(
            "agentic_core/L0_routing/a.py",
            "some.unknown.third_party.module",
        )
        assert _emit_layer_violation_edges(result) == []

    def test_same_layer_import_not_a_violation(self):
        result = self._result_with_import(
            "agentic_core/L0_routing/a.py",
            "agentic_core.L0_routing.b",
        )
        assert _emit_layer_violation_edges(result) == []

    def test_violation_emits_violates_edge(self):
        from agentic_core.adg.schema_util import ALLOWED_LAYER_EDGES

        # Find a pair (from_layer, to_layer) not in ALLOWED_LAYER_EDGES
        all_layers = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
        layer_to_path = {
            "L0": "agentic_core/L0_routing/a.py",
            "L1": "agentic_core/L1_cognition/b.py",
            "L2": "agentic_core/L2_execution/c.py",
            "L3": "agentic_core/L3_orchestration/d.py",
            "L4": "agentic_core/L4_integration/e.py",
            "L5": "agentic_core/L5_safety/f.py",
            "L6": "agentic_core/L6_runtime/g.py",
        }
        violating_pair = None
        for fl in all_layers:
            for tl in all_layers:
                if fl != tl and (fl, tl) not in ALLOWED_LAYER_EDGES:
                    if fl in layer_to_path and tl in layer_to_path:
                        violating_pair = (layer_to_path[fl], layer_to_path[tl])
                        break
            if violating_pair:
                break
        if violating_pair is None:


        from_path, to_path = violating_pair
        to_symbol = to_path.replace("/", ".").replace(".py", "")
        result = self._result_with_import(from_path, to_symbol)
        violations = _emit_layer_violation_edges(result)
        assert violations, "Expected violates edge for forbidden layer import"
        assert all(e.relation_type == "violates" for e in violations)

    def test_allowed_layer_import_not_violated(self):
        from agentic_core.adg.schema_util import ALLOWED_LAYER_EDGES

        if not ALLOWED_LAYER_EDGES:

        fl, tl = next(iter(ALLOWED_LAYER_EDGES))
        layer_to_path = {
            "L0": "agentic_core/L0_routing/a.py",
            "L1": "agentic_core/L1_cognition/b.py",
            "L2": "agentic_core/L2_execution/c.py",
            "L3": "agentic_core/L3_orchestration/d.py",
            "L4": "agentic_core/L4_integration/e.py",
            "L5": "agentic_core/L5_safety/f.py",
            "L6": "agentic_core/L6_runtime/g.py",
        }
        if fl not in layer_to_path or tl not in layer_to_path:

        from_path = layer_to_path[fl]
        to_symbol = layer_to_path[tl].replace("/", ".").replace(".py", "")
        result = self._result_with_import(from_path, to_symbol)
        violations = _emit_layer_violation_edges(result)
        assert not violations, "Allowed layer import should not produce violates edge"

    def test_violation_dedup_same_triple(self):
        """Two imports from same module with same layer pair → only one violates edge."""
        from agentic_core.adg.schema_util import ALLOWED_LAYER_EDGES

        all_layers = ["L0", "L1", "L2", "L3"]
        layer_to_path = {
            "L0": "agentic_core/L0_routing/a.py",
            "L1": "agentic_core/L1_cognition/b.py",
            "L2": "agentic_core/L2_execution/c.py",
            "L3": "agentic_core/L3_orchestration/d.py",
        }
        violating_pair = None
        for fl in all_layers:
            for tl in all_layers:
                if fl != tl and (fl, tl) not in ALLOWED_LAYER_EDGES:
                    if fl in layer_to_path and tl in layer_to_path:
                        violating_pair = (layer_to_path[fl], layer_to_path[tl])
                        break
            if violating_pair:
                break
        if violating_pair is None:

        from_path, to_path = violating_pair
        to_symbol1 = to_path.replace("/", ".").replace(".py", "") + ".Alpha"
        to_symbol2 = to_path.replace("/", ".").replace(".py", "") + ".Beta"
        edges = [
            Edge(
                from_name=canonical_name("Module", from_path),
                relation_type="imports",
                to_name=canonical_name("Symbol", to_symbol1),
                edge_kind="import",
                source_file=from_path,
                line_no=1,
                symbol=to_symbol1,
            ),
            Edge(
                from_name=canonical_name("Module", from_path),
                relation_type="imports",
                to_name=canonical_name("Symbol", to_symbol2),
                edge_kind="import",
                source_file=from_path,
                line_no=2,
                symbol=to_symbol2,
            ),
        ]
        result = ScanResult(edges=edges, modules=[from_path])
        violations = _emit_layer_violation_edges(result)
        assert len(violations) == 1, "Dedup on (from_module, from_layer, to_layer)"


# ─────────────────────────────────────────────────────────────────────────────
# _repo_relative ValueError branch
# ─────────────────────────────────────────────────────────────────────────────


class TestRepoRelative:
    def test_path_outside_repo_root(self):
        from agentic_core.adg.extraction.static_scanner import _repo_relative

        repo_root = Path("C:/some/repo")
        outside = Path("C:/other/location/file.py")
        result = _repo_relative(outside, repo_root)
        # Should not raise; returns str with forward slashes
        assert isinstance(result, str)
        assert "/" in result or result.endswith(".py")

    def test_path_inside_repo_root(self):
        from agentic_core.adg.extraction.static_scanner import _repo_relative

        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            fp = repo_root / "pkg" / "mod.py"
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text("x=1")
            result = _repo_relative(fp, repo_root)
            assert result == "pkg/mod.py"


# ─────────────────────────────────────────────────────────────────────────────
# _scan_file error branches
# ─────────────────────────────────────────────────────────────────────────────


class TestScanFileErrorBranches:
    def test_syntax_error_returns_empty_edges_and_true(self):
        from agentic_core.adg.extraction.static_scanner import _scan_file

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            bad = repo / "bad.py"
            bad.write_text("def (broken:\n", encoding="utf-8")
            edges, had_error = _scan_file(bad, repo)
        assert edges == []
        assert had_error is True

    def test_valid_file_returns_edges_and_false(self):
        from agentic_core.adg.extraction.static_scanner import _scan_file

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            ok = repo / "ok.py"
            ok.write_text("import os\n", encoding="utf-8")
            edges, had_error = _scan_file(ok, repo)
        assert had_error is False


# ─────────────────────────────────────────────────────────────────────────────
# _check_evidence_floors
# ─────────────────────────────────────────────────────────────────────────────


class TestCheckEvidenceFloors:
    def test_all_floors_met_returns_true(self):
        from agentic_core.adg.extraction.static_scanner import (
            _MIN_EVIDENCE_FLOORS,
            _check_evidence_floors,
        )

        # Build enough edges for every floor
        edges = []
        for relation, floor in _MIN_EVIDENCE_FLOORS.items():
            for i in range(floor):
                edges.append(
                    Edge(
                        from_name=f"ADG::Module::mod{i}.py",
                        relation_type=relation,
                        to_name=f"ADG::Symbol::sym{i}",
                        edge_kind="import",
                        source_file=f"mod{i}.py",
                        line_no=i + 1,
                        symbol=f"sym{i}",
                    )
                )
        result = ScanResult(edges=edges, modules=[f"mod{i}.py" for i in range(5)])
        assert _check_evidence_floors(result) is True

    def test_floor_not_met_returns_false(self):
        from agentic_core.adg.extraction.static_scanner import (
            _MIN_EVIDENCE_FLOORS,
            _check_evidence_floors,
        )

        if not _MIN_EVIDENCE_FLOORS:

        # Use an empty result — all floors will be 0
        result = ScanResult(edges=[], modules=[])
        # If any floor > 0, check returns False
        if any(v > 0 for v in _MIN_EVIDENCE_FLOORS.values()):
            assert _check_evidence_floors(result) is False


# ─────────────────────────────────────────────────────────────────────────────
# _check_cardinality
# ─────────────────────────────────────────────────────────────────────────────


class TestCheckCardinality:
    def test_no_violations_when_empty_result(self):
        from agentic_core.adg.extraction.static_scanner import (
            _check_cardinality,
        )

        result = ScanResult(edges=[], modules=[])
        violations = _check_cardinality(result)
        # Only LOW violations expected (if any lower bounds > 0)
        for v in violations:
            assert "CARDINALITY LOW" in v

    def test_high_violation_detected(self):
        from agentic_core.adg.extraction.static_scanner import (
            _CARDINALITY_RANGES,
            _check_cardinality,
        )

        if not _CARDINALITY_RANGES:

        relation, (lo, hi) = next(iter(_CARDINALITY_RANGES.items()))
        # Create hi+1 edges to trigger HIGH violation
        edges = [
            Edge(
                from_name=f"ADG::Module::mod{i}.py",
                relation_type=relation,
                to_name=f"ADG::Symbol::sym{i}",
                edge_kind="import",
                source_file=f"mod{i}.py",
                line_no=i + 1,
                symbol=f"sym{i}",
            )
            for i in range(hi + 1)
        ]
        result = ScanResult(edges=edges, modules=[])
        violations = _check_cardinality(result)
        high_violations = [v for v in violations if "CARDINALITY HIGH" in v]
        assert high_violations, f"Expected HIGH violation for {relation}"

    def test_low_violation_detected(self):
        from agentic_core.adg.extraction.static_scanner import (
            _CARDINALITY_RANGES,
            _check_cardinality,
        )

        if not _CARDINALITY_RANGES:

        # find a relation with lo > 0
        target_rel = None
        for relation, (lo, hi) in _CARDINALITY_RANGES.items():
            if lo > 0:
                target_rel = relation
                break
        if target_rel is None:

        result = ScanResult(edges=[], modules=[])
        violations = _check_cardinality(result)
        low_violations = [v for v in violations if "CARDINALITY LOW" in v and target_rel in v]
        assert low_violations


# ─────────────────────────────────────────────────────────────────────────────
# run_scanner_self_test
# ─────────────────────────────────────────────────────────────────────────────


class TestRunScannerSelfTest:
    def test_self_test_passes(self):
        assert run_scanner_self_test() is True

    def test_self_test_returns_bool(self):
        result = run_scanner_self_test()
        assert isinstance(result, bool)


# ─────────────────────────────────────────────────────────────────────────────
# ADGStaticScanner.scan_files
# ─────────────────────────────────────────────────────────────────────────────


class TestScanFiles:
    def test_scan_files_returns_result(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            f = repo / "mod.py"
            f.write_text("import os\n", encoding="utf-8")
            scanner = ADGStaticScanner(repo_root=repo)
            result = scanner.scan_files(["mod.py"])
        assert isinstance(result, ScanResult)
        assert "mod.py" in result.modules

    def test_scan_files_nonexistent_file_skipped(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scanner = ADGStaticScanner(repo_root=repo)
            result = scanner.scan_files(["nonexistent.py"])
        assert result.modules == []

    def test_scan_files_non_py_skipped(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            f = repo / "file.txt"
            f.write_text("not python", encoding="utf-8")
            scanner = ADGStaticScanner(repo_root=repo)
            result = scanner.scan_files(["file.txt"])
        assert result.modules == []

    def test_scan_files_digest_computed(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            f = repo / "mod.py"
            f.write_text("import os\n", encoding="utf-8")
            scanner = ADGStaticScanner(repo_root=repo)
            result = scanner.scan_files(["mod.py"])
        assert result.digest is not None and len(result.digest) == 64


# ─────────────────────────────────────────────────────────────────────────────
# ADGStaticScanner.build_reverse_import_graph
# ─────────────────────────────────────────────────────────────────────────────


class TestBuildReverseImportGraph:
    def test_reverse_graph_basic(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        edges = [
            _import_edge("pkg/a.py", "os"),
            _import_edge("pkg/b.py", "os"),
        ]
        result = ScanResult(edges=edges, modules=["pkg/a.py", "pkg/b.py"])
        scanner = ADGStaticScanner(repo_root=Path("."))
        rev = scanner.build_reverse_import_graph(result)
        os_node = canonical_name("Symbol", "os")
        assert os_node in rev
        assert sorted(rev[os_node]) == sorted(
            [
                canonical_name("Module", "pkg/a.py"),
                canonical_name("Module", "pkg/b.py"),
            ]
        )

    def test_reverse_graph_only_imports(self):
        """Non-imports edges should not appear in reverse graph."""
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        edges = [
            Edge(
                from_name=canonical_name("Module", "a.py"),
                relation_type="calls",
                to_name=canonical_name("Symbol", "foo"),
                edge_kind="call",
                source_file="a.py",
                line_no=1,
                symbol="foo",
            )
        ]
        result = ScanResult(edges=edges, modules=["a.py"])
        scanner = ADGStaticScanner(repo_root=Path("."))
        rev = scanner.build_reverse_import_graph(result)
        assert canonical_name("Symbol", "foo") not in rev

    def test_reverse_graph_no_duplicates(self):
        """Same module importing same symbol twice → one entry."""
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        edge1 = _import_edge("pkg/a.py", "os")
        edge2 = _import_edge("pkg/a.py", "os")
        result = ScanResult(edges=[edge1, edge2], modules=["pkg/a.py"])
        scanner = ADGStaticScanner(repo_root=Path("."))
        rev = scanner.build_reverse_import_graph(result)
        os_node = canonical_name("Symbol", "os")
        assert rev[os_node].count(canonical_name("Module", "pkg/a.py")) == 1

    def test_reverse_graph_sorted(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        edges = [
            _import_edge("pkg/b.py", "mylib"),
            _import_edge("pkg/a.py", "mylib"),
        ]
        result = ScanResult(edges=edges, modules=["pkg/a.py", "pkg/b.py"])
        scanner = ADGStaticScanner(repo_root=Path("."))
        rev = scanner.build_reverse_import_graph(result)
        mylib_node = canonical_name("Symbol", "mylib")
        assert rev[mylib_node] == sorted(rev[mylib_node])

    def test_reverse_graph_empty(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        result = ScanResult(edges=[], modules=[])
        scanner = ADGStaticScanner(repo_root=Path("."))
        assert scanner.build_reverse_import_graph(result) == {}


# ─────────────────────────────────────────────────────────────────────────────
# ADGStaticScanner.module_layer_map
# ─────────────────────────────────────────────────────────────────────────────


class TestModuleLayerMap:
    def test_known_layer_modules(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        result = ScanResult(
            edges=[],
            modules=[
                "agentic_core/L0_routing/mod.py",
                "agentic_core/L1_cognition/mod.py",
            ],
        )
        scanner = ADGStaticScanner(repo_root=Path("."))
        mapping = scanner.module_layer_map(result)
        assert mapping[canonical_name("Module", "agentic_core/L0_routing/mod.py")] == "L0"
        assert mapping[canonical_name("Module", "agentic_core/L1_cognition/mod.py")] == "L1"

    def test_unknown_layer(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        result = ScanResult(
            edges=[],
            modules=["random/path/mod.py"],
        )
        scanner = ADGStaticScanner(repo_root=Path("."))
        mapping = scanner.module_layer_map(result)
        assert mapping[canonical_name("Module", "random/path/mod.py")] == "L_UNKNOWN"

    def test_empty_modules(self):
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        result = ScanResult(edges=[], modules=[])
        scanner = ADGStaticScanner(repo_root=Path("."))
        assert scanner.module_layer_map(result) == {}


# ─────────────────────────────────────────────────────────────────────────────
# builder — duplicate entity skip (line 292 / line 347)
# ─────────────────────────────────────────────────────────────────────────────


class TestBuilderDuplicateEntitySkip:
    def test_duplicate_module_not_added_twice(self):
        from agentic_core.adg.artifact.builder_types import build_artifact

        result = ScanResult(
            edges=[],
            modules=[
                "agentic_core/L0_routing/mod.py",
                "agentic_core/L0_routing/mod.py",  # duplicate
            ],
        )
        art = build_artifact(result)
        module_adg = canonical_name("Module", "agentic_core/L0_routing/mod.py")
        module_entities = [e for e in art.entities if e.adg_name == module_adg]
        assert len(module_entities) == 1, "Duplicate module should only appear once"

    def test_duplicate_symbol_target_not_added_twice(self):
        from agentic_core.adg.artifact.builder_types import build_artifact

        edge1 = _import_edge("agentic_core/L0_routing/a.py", "os")
        edge2 = _import_edge("agentic_core/L0_routing/b.py", "os")
        result = ScanResult(
            edges=[edge1, edge2],
            modules=["agentic_core/L0_routing/a.py", "agentic_core/L0_routing/b.py"],
        )
        art = build_artifact(result)
        os_node = canonical_name("Symbol", "os")
        os_entities = [e for e in art.entities if e.adg_name == os_node]
        assert len(os_entities) == 1, "Same symbol target should only appear once"


# ─────────────────────────────────────────────────────────────────────────────
# builder — _collect_blind_spots: manifest is None path
# ─────────────────────────────────────────────────────────────────────────────


class TestCollectBlindSpotsNoManifest:
    def test_no_manifest_parse_failure_defaults_zero(self):
        from agentic_core.adg.artifact.builder_types import build_artifact

        result = ScanResult(edges=[], modules=[])
        result.manifest = None  # type: ignore[assignment]
        art = build_artifact(result)
        assert art.blind_spots.parse_failure_count == 0
        assert art.blind_spots.parse_failure_files == []


# ─────────────────────────────────────────────────────────────────────────────
# builder — in_cycle edges produce correct structural_metrics
# ─────────────────────────────────────────────────────────────────────────────


class TestBuilderCycleMetrics:
    def test_in_cycle_edges_counted_in_by_relation_type(self):
        from agentic_core.adg.artifact.builder_types import build_artifact

        a = "agentic_core/L0_routing/a.py"
        b = "agentic_core/L0_routing/b.py"
        cycle_node = canonical_name("Cycle", "abc123hash0000")
        edges = [
            Edge(
                from_name=canonical_name("Module", a),
                relation_type="in_cycle",
                to_name=cycle_node,
                edge_kind="cycle",
                source_file=a,
                line_no=0,
                symbol="cycle:abc123hash0000",
            ),
            Edge(
                from_name=canonical_name("Module", b),
                relation_type="in_cycle",
                to_name=cycle_node,
                edge_kind="cycle",
                source_file=b,
                line_no=0,
                symbol="cycle:abc123hash0000",
            ),
        ]
        result = ScanResult(edges=edges, modules=[a, b])
        art = build_artifact(result)
        assert "in_cycle" in art.structural_metrics.by_relation_type
        assert art.structural_metrics.by_relation_type["in_cycle"] == 2
