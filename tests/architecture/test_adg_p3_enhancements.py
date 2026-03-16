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
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_p3_enhancements")
_emit_applies_guardrail("p0", "test_adg_p3_enhancements", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_p3_enhancements", "policy_binding")
_emit_snapshots_state("p0", "test_adg_p3_enhancements", "state_snapshot")
emit_replay_key("p0", "test_adg_p3_enhancements")
emit_determinism_digest("p0", "test_adg_p3_enhancements")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        from agentic_core.adg.analysis.confidence import score_edge

        ec = score_edge(self._make_type_ann_edge())
        assert 0.0 < ec.confidence <= 1.0

    def test_type_annotation_same_confidence_as_reads_from(self):
        from agentic_core.adg.analysis.confidence import score_edge

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
