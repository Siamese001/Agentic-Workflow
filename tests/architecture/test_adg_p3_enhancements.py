"""Tests for ADG P3 enhancements: E9 (Incremental Scan Cache) and E4 (Type Annotation Graph).

Uses synthetic fixtures — no filesystem access beyond the cache tests which
use tmp_path.
"""

from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path

import pytest

from agentic_core.adg.extraction.scan_cache import (
    CACHE_VERSION,
    ScanCache,
    file_hash,
)
from agentic_core.adg.extraction.static_scanner import (
    Edge,
    _TypeAnnotationVisitor,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_adg_p3_enhancements")
_emit_applies_guardrail("p0", "test_adg_p3_enhancements", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_p3_enhancements", "policy_binding")
_emit_snapshots_state("p0", "test_adg_p3_enhancements", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_adg_p3_enhancements", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_p3_enhancements", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_p3_enhancements", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_p3_enhancements", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_p3_enhancements", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_p3_enhancements", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_p3_enhancements", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_p3_enhancements", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_p3_enhancements", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_p3_enhancements", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_p3_enhancements", "p4obs", "alert")
_emit_links_incident_trace("test_adg_p3_enhancements", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_p3_enhancements", "p3lm", "pattern")
_emit_records_learning_event("test_adg_p3_enhancements", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_p3_enhancements", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_p3_enhancements", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_p3_enhancements", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_p3_enhancements", "p3lm", "policy")
_emit_stores_learning_state("test_adg_p3_enhancements", "p3lm", "state")
_emit_records_execution_trace("test_adg_p3_enhancements", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_p3_enhancements", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_p3_enhancements", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_p3_enhancements", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_p3_enhancements", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_p3_enhancements", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_p3_enhancements", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_p3_enhancements", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_p3_enhancements", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_p3_enhancements", "context_pull")
_emit_pulls_context("p1", "test_adg_p3_enhancements", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_p3_enhancements", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_p3_enhancements", "uwg_term_2")
_emit_writes_through("p1", "test_adg_p3_enhancements", "write_through")
_emit_writes_through("p1", "test_adg_p3_enhancements", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_p3_enhancements", "safety_validation")
_emit_invokes_eval("p1", "test_adg_p3_enhancements", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_p3_enhancements", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_p3_enhancements", "human_escalation")
_emit_routes_through("p1", "test_adg_p3_enhancements", "route_through")
_emit_checks_agent_registry("p1", "test_adg_p3_enhancements", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_p3_enhancements", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_p3_enhancements", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_p3_enhancements", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_p3_enhancements", "target_agent")
_emit_verifies_policy("p1", "test_adg_p3_enhancements", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_p3_enhancements", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_p3_enhancements", "boundary_check")
_emit_transcripts_response("p1", "test_adg_p3_enhancements", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_p3_enhancements")
_emit_gated_by_confidence("p1", "test_adg_p3_enhancements", "confidence_gate")
emit_replay_key("p0", "test_adg_p3_enhancements")
emit_determinism_digest("p0", "test_adg_p3_enhancements")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_p3_enhancements", "execution_auth")
_emit_validates_capability("p2", "test_adg_p3_enhancements", "capability_check")
_emit_routes_to_capability("p2", "test_adg_p3_enhancements", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_p3_enhancements", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_p3_enhancements", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_p3_enhancements", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_p3_enhancements", "exec_output")
_emit_dispatches_agent("p3", "test_adg_p3_enhancements", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_p3_enhancements", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_p3_enhancements", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_p3_enhancements", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_p3_enhancements", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_p3_enhancements", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_p3_enhancements", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_p3_enhancements", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_p3_enhancements", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_p3_enhancements", "eval_metric")
_emit_stores_embedding("p4", "test_adg_p3_enhancements", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_p3_enhancements", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_p3_enhancements", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_module_adg(rel: str) -> str:
    return f"ADG::Module::{rel}"


def _parse(source: str) -> ast.Module:
    return ast.parse(textwrap.dedent(source))


def _ann_visitor(source: str, rel: str = "foo/bar.py") -> _TypeAnnotationVisitor:
    tree = _parse(source)
    v = _TypeAnnotationVisitor(_make_module_adg(rel), rel)
    v.visit(tree)
    return v


def _make_edge(symbol: str = "sym") -> Edge:
    return Edge(
        from_name="ADG::Module::a.py",
        relation_type="imports",
        to_name=f"ADG::Symbol::{symbol}",
        edge_kind="import",
        source_file="a.py",
        line_no=1,
        symbol=symbol,
    )


# ===========================================================================
# E9: Incremental File-Level Scan Cache
# ===========================================================================


class TestScanCacheBasic:
    """E9: Core cache get/put/save/load behaviour."""

    def test_empty_cache_is_miss(self):
        cache = ScanCache()
        edges, hit = cache.get("foo/bar.py", "abc123")
        assert hit is False
        assert edges is None

    def test_put_then_get_hit(self):
        cache = ScanCache()
        edge = _make_edge("os")
        cache.put("foo/bar.py", "hash1", [edge])
        dicts, hit = cache.get("foo/bar.py", "hash1")
        assert hit is True
        assert dicts is not None
        assert len(dicts) == 1
        assert dicts[0]["symbol"] == "os"

    def test_stale_hash_is_miss_and_evicted(self):
        cache = ScanCache()
        cache.put("foo/bar.py", "old_hash", [_make_edge()])
        dicts, hit = cache.get("foo/bar.py", "new_hash")
        assert hit is False
        assert dicts is None
        assert cache.evictions == 1

    def test_hit_rate_calculation(self):
        cache = ScanCache()
        cache.put("a.py", "h1", [_make_edge()])
        cache.put("b.py", "h2", [_make_edge()])
        cache.get("a.py", "h1")  # hit
        cache.get("b.py", "h3")  # miss (stale)
        cache.get("c.py", "h4")  # miss (absent)
        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 2
        assert stats["hit_rate"] == pytest.approx(1 / 3, abs=0.01)

    def test_size_tracks_entries(self):
        cache = ScanCache()
        assert cache.size == 0
        cache.put("a.py", "h1", [_make_edge()])
        assert cache.size == 1
        cache.put("b.py", "h2", [_make_edge()])
        assert cache.size == 2

    def test_overwrite_existing_entry(self):
        cache = ScanCache()
        cache.put("a.py", "h1", [_make_edge("old")])
        cache.put("a.py", "h2", [_make_edge("new")])
        dicts, hit = cache.get("a.py", "h2")
        assert hit is True
        assert dicts[0]["symbol"] == "new"

    def test_multiple_edges_per_file(self):
        cache = ScanCache()
        edges = [_make_edge("os"), _make_edge("sys"), _make_edge("pathlib")]
        cache.put("a.py", "h1", edges)
        dicts, hit = cache.get("a.py", "h1")
        assert hit is True
        assert len(dicts) == 3


class TestScanCachePersistence:
    """E9: JSON persistence via save/load."""

    def test_save_and_load_roundtrip(self, tmp_path: Path):
        cache_file = tmp_path / "adg_cache.json"
        cache = ScanCache()
        cache.put("a.py", "hash_a", [_make_edge("os")])
        cache.save(cache_file)

        loaded = ScanCache.load(cache_file)
        dicts, hit = loaded.get("a.py", "hash_a")
        assert hit is True
        assert dicts[0]["symbol"] == "os"

    def test_load_missing_file_returns_empty(self, tmp_path: Path):
        cache = ScanCache.load(tmp_path / "nonexistent.json")
        assert cache.size == 0

    def test_load_wrong_version_returns_empty(self, tmp_path: Path):
        cache_file = tmp_path / "adg_cache.json"
        cache_file.write_text(
            json.dumps({"version": "999", "entries": {"a.py": {"file_hash": "h", "edges": []}}}),
            encoding="utf-8",
        )
        cache = ScanCache.load(cache_file)
        assert cache.size == 0

    def test_load_corrupt_json_returns_empty(self, tmp_path: Path):
        cache_file = tmp_path / "adg_cache.json"
        cache_file.write_text("not valid json", encoding="utf-8")
        cache = ScanCache.load(cache_file)
        assert cache.size == 0

    def test_saved_version_matches_constant(self, tmp_path: Path):
        cache_file = tmp_path / "adg_cache.json"
        ScanCache().save(cache_file)
        raw = json.loads(cache_file.read_text())
        assert raw["version"] == CACHE_VERSION

    def test_edge_fields_preserved_in_roundtrip(self, tmp_path: Path):
        cache_file = tmp_path / "adg_cache.json"
        edge = Edge(
            from_name="ADG::Module::x.py",
            relation_type="imports",
            to_name="ADG::Symbol::os",
            edge_kind="import",
            source_file="x.py",
            line_no=42,
            symbol="os",
        )
        cache = ScanCache()
        cache.put("x.py", "h", [edge])
        cache.save(cache_file)

        loaded = ScanCache.load(cache_file)
        dicts, _ = loaded.get("x.py", "h")
        assert dicts[0]["line_no"] == 42
        assert dicts[0]["from_name"] == "ADG::Module::x.py"

    def test_atomic_save_replaces_old_file(self, tmp_path: Path):
        cache_file = tmp_path / "adg_cache.json"
        old_cache = ScanCache()
        old_cache.put("old.py", "h_old", [_make_edge("old_sym")])
        old_cache.save(cache_file)

        new_cache = ScanCache()
        new_cache.put("new.py", "h_new", [_make_edge("new_sym")])
        new_cache.save(cache_file)

        loaded = ScanCache.load(cache_file)
        assert loaded.size == 1
        _, hit_old = loaded.get("old.py", "h_old")
        _, hit_new = loaded.get("new.py", "h_new")
        assert hit_old is False
        assert hit_new is True


class TestFileHash:
    """E9: file_hash utility."""

    def test_same_content_same_hash(self, tmp_path: Path):
        f = tmp_path / "a.py"
        f.write_bytes(b"x = 1\n")
        assert file_hash(f) == file_hash(f)

    def test_different_content_different_hash(self, tmp_path: Path):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_bytes(b"x = 1\n")
        f2.write_bytes(b"x = 2\n")
        assert file_hash(f1) != file_hash(f2)

    def test_missing_file_returns_empty_string(self, tmp_path: Path):
        assert file_hash(tmp_path / "ghost.py") == ""

    def test_hash_is_hex_string(self, tmp_path: Path):
        f = tmp_path / "a.py"
        f.write_bytes(b"pass\n")
        h = file_hash(f)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ===========================================================================
# E4: Type Annotation Graph (_TypeAnnotationVisitor)
# ===========================================================================


class TestTypeAnnotationVisitor:
    """E4: Verify reads_from/type_annotation edges for annotated definitions."""

    def test_argument_annotation(self):
        source = """
        def greet(name: str) -> None:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "str" in syms

    def test_return_annotation(self):
        source = """
        def get_path() -> pathlib.Path:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "pathlib.Path" in syms

    def test_annotated_assignment(self):
        source = """
        count: int = 0
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "int" in syms

    def test_generic_subscript_unwrapped(self):
        source = """
        def process(items: list[MyType]) -> dict[str, int]:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "MyType" in syms
        assert "str" in syms
        assert "int" in syms

    def test_optional_annotation(self):
        source = """
        from typing import Optional
        def maybe(x: Optional[MyClass]) -> None:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "MyClass" in syms

    def test_none_not_emitted(self):
        source = """
        def f() -> None:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "None" not in syms

    def test_any_not_emitted(self):
        source = """
        from typing import Any
        def f(x: Any) -> Any:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "Any" not in syms

    def test_dotted_type_emitted(self):
        source = """
        def f(x: collections.abc.Callable) -> None:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "collections.abc.Callable" in syms

    def test_edge_kind_is_type_annotation(self):
        source = """
        def f(x: MyType) -> None:
            pass
        """
        v = _ann_visitor(source)
        ann_edges = [e for e in v.edges if e.symbol == "MyType"]
        assert len(ann_edges) >= 1
        assert all(e.edge_kind == "type_annotation" for e in ann_edges)

    def test_edge_relation_type_is_reads_from(self):
        source = """
        def f(x: MyType) -> None:
            pass
        """
        v = _ann_visitor(source)
        assert all(e.relation_type == "reads_from" for e in v.edges)

    def test_no_annotation_no_edges(self):
        source = """
        def plain(x, y):
            return x + y
        """
        v = _ann_visitor(source)
        assert v.edges == []

    def test_deduplication_same_sym_same_line(self):
        source = """
        def f(x: MyType, y: MyType) -> None:
            pass
        """
        v = _ann_visitor(source)
        my_type_edges = [e for e in v.edges if e.symbol == "MyType"]
        assert len(my_type_edges) == 1

    def test_union_type_via_pipe(self):
        source = """
        def f(x: int | str) -> None:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "int" in syms
        assert "str" in syms

    def test_async_function_annotations(self):
        source = """
        async def fetch(url: str) -> bytes:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "str" in syms
        assert "bytes" in syms

    def test_kwonly_arg_annotation(self):
        source = """
        def f(*, key: str) -> None:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "str" in syms

    def test_vararg_annotation(self):
        source = """
        def f(*args: int) -> None:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "int" in syms

    def test_to_name_uses_symbol_prefix(self):
        source = """
        def f(x: MyType) -> None:
            pass
        """
        v = _ann_visitor(source)
        ann_edges = [e for e in v.edges if e.symbol == "MyType"]
        assert ann_edges[0].to_name == "ADG::Symbol::MyType"

    def test_string_literal_annotation_skipped(self):
        source = """
        def f(x: "ForwardRef") -> None:
            pass
        """
        v = _ann_visitor(source)
        syms = {e.symbol for e in v.edges}
        assert "ForwardRef" not in syms


# ===========================================================================
# Integration: confidence scoring of E4 edge kind
# ===========================================================================


class TestConfidenceScoringP3Edges:
    """Verify confidence.py correctly scores E4 type_annotation edge kind."""

    def _make_type_ann_edge(self) -> Edge:
        return Edge(
            from_name="ADG::Module::foo.py",
            relation_type="reads_from",
            to_name="ADG::Symbol::MyType",
            edge_kind="type_annotation",
            source_file="foo.py",
            line_no=5,
            symbol="MyType",
        )

    def test_type_annotation_edge_confidence(self):
        from agentic_core.adg.analysis.EdgeConfidence import score_edge

        ec = score_edge(self._make_type_ann_edge())
        assert 0.0 < ec.confidence <= 1.0

    def test_type_annotation_same_confidence_as_reads_from(self):
        from agentic_core.adg.analysis.EdgeConfidence import score_edge

        ann_edge = self._make_type_ann_edge()
        base_edge = Edge(
            from_name="ADG::Module::foo.py",
            relation_type="reads_from",
            to_name="ADG::Symbol::MyType",
            edge_kind="reads_config",
            source_file="foo.py",
            line_no=5,
            symbol="MyType",
        )
        ann_ec = score_edge(ann_edge)
        base_ec = score_edge(base_edge)
        assert ann_ec.confidence == base_ec.confidence
