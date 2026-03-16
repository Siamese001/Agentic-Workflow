"""Tests for ADG P2 enhancements: E7 (Conditional Imports), E2 (Star Import Resolution), E3 (Decorator Graph).

Tests cover positive extraction, negative (no false positives), and edge-case
scenarios using synthetic AST fixtures.
"""

from __future__ import annotations

import ast
import textwrap

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    _DecoratorVisitor,
    _ImportVisitor,
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

_emit_records_execution_trace("p0", "evidence", "test_adg_p2_enhancements")
_emit_applies_guardrail("p0", "test_adg_p2_enhancements", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_p2_enhancements", "policy_binding")
_emit_snapshots_state("p0", "test_adg_p2_enhancements", "state_snapshot")
emit_replay_key("p0", "test_adg_p2_enhancements")
emit_determinism_digest("p0", "test_adg_p2_enhancements")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_p2_enhancements", "execution_auth")
_emit_validates_capability("p2", "test_adg_p2_enhancements", "capability_check")
_emit_routes_to_capability("p2", "test_adg_p2_enhancements", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_p2_enhancements", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_p2_enhancements", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_p2_enhancements", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_p2_enhancements", "exec_output")
_emit_dispatches_agent("p3", "test_adg_p2_enhancements", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_p2_enhancements", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_p2_enhancements", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_p2_enhancements", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_p2_enhancements", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_p2_enhancements", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_p2_enhancements", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_p2_enhancements", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_p2_enhancements", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_p2_enhancements", "eval_metric")
_emit_stores_embedding("p4", "test_adg_p2_enhancements", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_p2_enhancements", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_p2_enhancements", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_module_adg(rel: str) -> str:
    return f"ADG::Module::{rel}"


def _parse(source: str) -> ast.Module:
    return ast.parse(textwrap.dedent(source))


def _import_visitor(source: str, all_registry: dict | None = None) -> _ImportVisitor:
    tree = _parse(source)
    v = _ImportVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py", all_registry=all_registry)
    v.visit(tree)
    return v


# ===========================================================================
# E7: Conditional Import Classification
# ===========================================================================


class TestTypeCheckingGuard:
    """E7: Imports under TYPE_CHECKING should be tagged type_checking_import."""

    def test_type_checking_import_tagged(self):
        source = """
        from __future__ import annotations
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            import os
        """
        v = _import_visitor(source)
        import_edges = {e.symbol: e for e in v.edges if e.relation_type == "imports"}
        assert "os" in import_edges
        assert import_edges["os"].edge_kind == "type_checking_import"

    def test_type_checking_from_import_tagged(self):
        source = """
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from pathlib import Path
        """
        v = _import_visitor(source)
        import_edges = {e.symbol: e for e in v.edges if e.relation_type == "imports"}
        assert "pathlib.Path" in import_edges
        assert import_edges["pathlib.Path"].edge_kind == "type_checking_import"

    def test_regular_import_not_tagged(self):
        source = """
        import os
        """
        v = _import_visitor(source)
        import_edges = {e.symbol: e for e in v.edges if e.relation_type == "imports"}
        assert import_edges["os"].edge_kind == "import"

    def test_else_branch_of_type_checking_is_normal(self):
        """Imports in else branch of TYPE_CHECKING guard are unconditional."""
        source = """
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            import mypy_only
        else:
            import runtime_dep
        """
        v = _import_visitor(source)
        import_edges = {e.symbol: e for e in v.edges if e.relation_type == "imports"}
        assert import_edges.get("mypy_only", Edge.__new__(Edge)).edge_kind == "type_checking_import"
        assert import_edges["runtime_dep"].edge_kind == "import"


class TestOptionalImportGuard:
    """E7: Imports in try/except ImportError should be tagged optional_import."""

    def test_try_except_import_error_tagged(self):
        source = """
        try:
            import ujson as json
        except ImportError:
            import json
        """
        v = _import_visitor(source)
        import_edges = {e.symbol: e for e in v.edges if e.relation_type == "imports"}
        assert import_edges["ujson"].edge_kind == "import"
        assert import_edges["json"].edge_kind == "optional_import"

    def test_try_except_module_not_found_tagged(self):
        source = """
        try:
            from fast_lib import fast_func
        except ModuleNotFoundError:
            from slow_lib import slow_func as fast_func
        """
        v = _import_visitor(source)
        import_edges = [e for e in v.edges if e.relation_type == "imports"]
        kinds = {e.symbol: e.edge_kind for e in import_edges}
        assert kinds.get("slow_lib.slow_func") == "optional_import"
        assert kinds.get("fast_lib.fast_func") == "import"

    def test_except_other_exception_not_tagged(self):
        source = """
        try:
            import risky
        except RuntimeError:
            import fallback
        """
        v = _import_visitor(source)
        import_edges = {e.symbol: e for e in v.edges if e.relation_type == "imports"}
        assert import_edges["fallback"].edge_kind == "import"


class TestVersionGuardImport:
    """E7: Imports under sys.version_info guard should be tagged version_guard_import."""

    def test_version_info_compare_tagged(self):
        source = """
        import sys
        if sys.version_info >= (3, 11):
            from tomllib import loads
        """
        v = _import_visitor(source)
        import_edges = {e.symbol: e for e in v.edges if e.relation_type == "imports"}
        assert import_edges.get("tomllib.loads", Edge.__new__(Edge)).edge_kind == "version_guard_import"

    def test_version_info_attribute_guard_tagged(self):
        source = """
        import sys
        if sys.version_info.major >= 3:
            import typing_extensions
        """
        v = _import_visitor(source)
        import_edges = {e.symbol: e for e in v.edges if e.relation_type == "imports"}
        assert import_edges.get("typing_extensions", Edge.__new__(Edge)).edge_kind == "version_guard_import"


# ===========================================================================
# E2: Star Import Resolution
# ===========================================================================


class TestStarImportResolution:
    """E2: Star imports should be resolved against __all__ registry when available."""

    def test_star_import_without_registry_emits_star_edge(self):
        source = """
        from some.module import *
        """
        v = _import_visitor(source)
        star_edges = [e for e in v.edges if e.edge_kind == "star_import"]
        assert len(star_edges) == 1
        assert star_edges[0].symbol == "some.module.*"

    def test_star_import_resolved_against_registry(self):
        source = """
        from mypackage.utils import *
        """
        registry = {"mypackage.utils": ["helper", "parse", "format_output"]}
        v = _import_visitor(source, all_registry=registry)
        import_edges = {e.symbol for e in v.edges if e.relation_type == "imports"}
        assert "mypackage.utils.helper" in import_edges
        assert "mypackage.utils.parse" in import_edges
        assert "mypackage.utils.format_output" in import_edges
        star_edges = [e for e in v.edges if e.edge_kind == "star_import"]
        assert star_edges == []

    def test_star_import_resolved_no_star_edge_emitted(self):
        source = """
        from mypackage.utils import *
        """
        registry = {"mypackage.utils": ["foo", "bar"]}
        v = _import_visitor(source, all_registry=registry)
        assert v.star_import_count == 1
        assert v.star_resolved_count == 1

    def test_star_import_unresolved_tracked(self):
        source = """
        from unknown.pkg import *
        """
        v = _import_visitor(source, all_registry={})
        assert v.star_import_count == 1
        assert v.star_resolved_count == 0

    def test_star_import_resolved_edges_have_correct_from_name(self):
        source = """
        from pkg import *
        """
        registry = {"pkg": ["Alpha", "Beta"]}
        v = _import_visitor(source, all_registry=registry)
        from_names = {e.from_name for e in v.edges if e.relation_type == "imports"}
        assert from_names == {_make_module_adg("foo/bar.py")}

    def test_star_import_resolved_in_type_checking_context(self):
        """Resolved star imports inside TYPE_CHECKING retain type_checking_import kind."""
        source = """
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from stubs import *
        """
        registry = {"stubs": ["StubA", "StubB"]}
        v = _import_visitor(source, all_registry=registry)
        checking_edges = [e for e in v.edges if e.edge_kind == "type_checking_import"]
        symbols = {e.symbol for e in checking_edges}
        assert "stubs.StubA" in symbols
        assert "stubs.StubB" in symbols

    def test_regular_and_star_import_mixed(self):
        source = """
        import os
        from utils import *
        """
        registry = {"utils": ["helper"]}
        v = _import_visitor(source, all_registry=registry)
        symbols = {e.symbol for e in v.edges if e.relation_type == "imports"}
        assert "os" in symbols
        assert "utils.helper" in symbols


# ===========================================================================
# E3: Decorator Graph (G7)
# ===========================================================================


def _dec_visitor(source: str) -> _DecoratorVisitor:
    tree = _parse(source)
    v = _DecoratorVisitor(_make_module_adg("foo/bar.py"), "foo/bar.py")
    v.visit(tree)
    return v


class TestDecoratorVisitor:
    """E3: Verify decorator edges are emitted for decorated definitions."""

    def test_simple_function_decorator(self):
        source = """
        @my_decorator
        def func():
            pass
        """
        v = _dec_visitor(source)
        syms = {e.symbol for e in v.edges if e.relation_type == "influences"}
        assert "my_decorator" in syms

    def test_class_decorator(self):
        source = """
        @dataclass
        class MyModel:
            pass
        """
        v = _dec_visitor(source)
        syms = {e.symbol for e in v.edges if e.relation_type == "influences"}
        assert "dataclass" in syms

    def test_dotted_decorator_extracted(self):
        source = """
        @abc.abstractmethod
        def abstract():
            pass
        """
        v = _dec_visitor(source)
        syms = {e.symbol for e in v.edges if e.relation_type == "influences"}
        assert "abc.abstractmethod" in syms

    def test_parameterized_decorator(self):
        source = """
        @pytest.mark.parametrize("x", [1, 2])
        def test_foo(x):
            pass
        """
        v = _dec_visitor(source)
        syms = {e.symbol for e in v.edges if e.relation_type == "influences"}
        assert "pytest.mark.parametrize" in syms

    def test_multiple_decorators_on_one_function(self):
        source = """
        @first
        @second
        @third
        def multi():
            pass
        """
        v = _dec_visitor(source)
        syms = {e.symbol for e in v.edges if e.relation_type == "influences"}
        assert {"first", "second", "third"} <= syms

    def test_no_decorator_no_edge(self):
        source = """
        def plain():
            pass
        class Plain:
            pass
        """
        v = _dec_visitor(source)
        assert v.edges == []

    def test_edge_kind_is_decorator(self):
        source = """
        @my_dec
        def f():
            pass
        """
        v = _dec_visitor(source)
        dec_edges = [e for e in v.edges if e.relation_type == "influences"]
        assert all(e.edge_kind == "decorator" for e in dec_edges)

    def test_to_name_uses_symbol_prefix(self):
        source = """
        @route("/api")
        def handler():
            pass
        """
        v = _dec_visitor(source)
        dec_edges = [e for e in v.edges if e.relation_type == "influences"]
        assert all(e.to_name.startswith("ADG::Symbol::") for e in dec_edges)

    def test_async_function_decorator(self):
        source = """
        @async_dec
        async def async_handler():
            pass
        """
        v = _dec_visitor(source)
        syms = {e.symbol for e in v.edges if e.relation_type == "influences"}
        assert "async_dec" in syms

    def test_from_name_is_module_adg(self):
        source = """
        @dec
        def f():
            pass
        """
        v = _dec_visitor(source)
        from_names = {e.from_name for e in v.edges}
        assert from_names == {_make_module_adg("foo/bar.py")}

    def test_method_decorator_inside_class(self):
        source = """
        class MyClass:
            @staticmethod
            def static_method():
                pass
            @classmethod
            def class_method(cls):
                pass
        """
        v = _dec_visitor(source)
        syms = {e.symbol for e in v.edges if e.relation_type == "influences"}
        assert "staticmethod" in syms
        assert "classmethod" in syms


# ===========================================================================
# Integration: confidence scoring of E2/E3/E7 edge kinds
# ===========================================================================


class TestConfidenceScoringP2Edges:
    """Verify confidence.py correctly scores E2/E3/E7 edge types."""

    def _make_edge(self, relation_type: str, edge_kind: str) -> Edge:
        return Edge(
            from_name="ADG::Module::foo.py",
            relation_type=relation_type,
            to_name="ADG::Symbol::bar",
            edge_kind=edge_kind,
            source_file="foo.py",
            line_no=1,
            symbol="bar",
        )

    def test_type_checking_import_lower_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        edge = self._make_edge("imports", "type_checking_import")
        ec = score_edge(edge)
        base_import = score_edge(self._make_edge("imports", "import"))
        assert ec.confidence < base_import.confidence

    def test_optional_import_lower_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        edge = self._make_edge("imports", "optional_import")
        ec = score_edge(edge)
        base_import = score_edge(self._make_edge("imports", "import"))
        assert ec.confidence < base_import.confidence

    def test_star_import_lower_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        edge = self._make_edge("imports", "star_import")
        ec = score_edge(edge)
        base_import = score_edge(self._make_edge("imports", "import"))
        assert ec.confidence < base_import.confidence

    def test_decorator_edge_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        edge = self._make_edge("influences", "decorator")
        ec = score_edge(edge)
        assert 0.0 < ec.confidence <= 1.0
        assert ec.provenance == "ast_call_dynamic"

    def test_version_guard_import_lower_confidence(self):
        from agentic_core.adg.analysis.confidence import score_edge

        edge = self._make_edge("imports", "version_guard_import")
        ec = score_edge(edge)
        base_import = score_edge(self._make_edge("imports", "import"))
        assert ec.confidence < base_import.confidence
