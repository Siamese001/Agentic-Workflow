"""Tests for ADG Runtime Query Engine (R1) and GraphAwareCache (R7)."""

from __future__ import annotations

from agentic_core.adg.extraction.static_scanner import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    Edge,
    ScanManifest,
    ScanResult,
)
from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine
from agentic_core.cache.graph_aware_cache import GraphAwareCache


def _make_result(edges: list[Edge]) -> ScanResult:
    result = ScanResult(edges=edges, modules=[], digest="test", commit_sha="abc")
    return result


def _edge(from_name: str, rel: str, to_name: str, kind: str = "direct", sym: str = "", line: int = 1) -> Edge:
    return Edge(
        from_name=from_name,
        relation_type=rel,
        to_name=to_name,
        edge_kind=kind,
        source_file="test.py",
        line_no=line,
        symbol=sym,
    )


_M = "ADG::Module::"
_S = "ADG::Symbol::"


class TestADGRuntimeQueryEngine:
    def _engine(self, edges: list[Edge]) -> ADGRuntimeQueryEngine:
        return ADGRuntimeQueryEngine(_make_result(edges))

    def test_inheritance_index_built(self):
        edges = [
            _edge(
                f"{_M}agentic_core/agents/foo.py::ConcreteAgent",
                "implements",
                f"{_S}SovereignBaseAgent",
                sym="SovereignBaseAgent",
            ),
            _edge(
                f"{_M}agentic_core/agents/bar.py::OtherAgent",
                "implements",
                f"{_S}SovereignBaseAgent",
                sym="SovereignBaseAgent",
            ),
        ]
        engine = self._engine(edges)
        result = engine.find_agents_by_base_class("SovereignBaseAgent")
        assert len(result) == 2
        class_names = [r.split("::")[-1] for r in result]
        assert "ConcreteAgent" in class_names
        assert "OtherAgent" in class_names

    def test_inheritance_index_empty_on_unknown_base(self):
        engine = self._engine([])
        assert engine.find_agents_by_base_class("NonExistentBase") == []

    def test_reverse_deps_built(self):
        edges = [
            _edge(f"{_M}agentic_core/L3/agent.py", "imports", f"{_M}agentic_core/L1/base.py"),
            _edge(f"{_M}agentic_core/L3/other.py", "imports", f"{_M}agentic_core/L1/base.py"),
        ]
        engine = self._engine(edges)
        rev = engine.get_reverse_dependencies(f"{_M}agentic_core/L1/base.py")
        assert f"{_M}agentic_core/L3/agent.py" in rev
        assert f"{_M}agentic_core/L3/other.py" in rev

    def test_reverse_deps_empty_on_unused(self):
        engine = self._engine([])
        assert engine.get_reverse_dependencies(f"{_M}nothing.py") == set()

    def test_composition_index_built(self):
        edges = [
            _edge(
                f"{_M}agentic_core/L2/reasoning/my_agent.py::MyAgent",
                "instantiates",
                f"{_S}LLMGateway",
                kind="composition",
                sym="LLMGateway",
            ),
        ]
        engine = self._engine(edges)
        caps = engine.find_agents_by_capability("LLMGateway")
        assert len(caps) == 1
        assert caps[0].composed_symbol == "LLMGateway"

    def test_composition_index_empty_on_unknown(self):
        engine = self._engine([])
        assert engine.find_agents_by_capability("UnknownSymbol") == []

    def test_blast_radius_direct(self):
        edges = [
            _edge(f"{_M}agentic_core/L3/agent.py", "imports", f"{_M}agentic_core/L1/base.py"),
        ]
        engine = self._engine(edges)
        blast = engine.compute_blast_radius(["agentic_core/L1/base.py"])
        assert "agentic_core/L1/base.py" in blast
        assert "agentic_core/L3/agent.py" in blast

    def test_blast_radius_transitive(self):
        edges = [
            _edge(f"{_M}b.py", "imports", f"{_M}a.py"),
            _edge(f"{_M}c.py", "imports", f"{_M}b.py"),
        ]
        engine = self._engine(edges)
        blast = engine.compute_blast_radius(["a.py"])
        assert "b.py" in blast
        assert "c.py" in blast
        assert blast["c.py"] == 2

    def test_blast_radius_no_deps(self):
        engine = self._engine([])
        blast = engine.compute_blast_radius(["solo.py"])
        assert blast == {"solo.py": 0}

    def test_validate_import_path_allowed(self):
        engine = self._engine([])
        result = engine.validate_import_path(
            "agentic_core/L3_orchestration/x.py", "agentic_core/L1_cognition/y.py"
        )
        assert result.allowed is True

    def test_validate_import_path_forbidden(self):
        engine = self._engine([])
        result = engine.validate_import_path(
            "agentic_core/L0_routing/x.py", "agentic_core/L3_orchestration/y.py"
        )
        assert result.allowed is False

    def test_get_cache_invalidation_set(self):
        edges = [
            _edge(f"{_M}consumer.py", "imports", f"{_M}dep.py"),
        ]
        engine = self._engine(edges)
        inv_set = engine.get_cache_invalidation_set("dep.py")
        assert "consumer.py" in inv_set

    def test_stats_returns_dict(self):
        engine = self._engine([])
        stats = engine.stats()
        assert isinstance(stats, dict)
        assert "total_edges" in stats
        assert stats["total_edges"] == 0


class TestGraphAwareCache:
    def _cache(self, edges: list[Edge] | None = None) -> GraphAwareCache:
        engine = ADGRuntimeQueryEngine(_make_result(edges or []))
        return GraphAwareCache(engine)

    def test_set_and_get(self):
        cache = self._cache()
        cache.set("key1", "value1", depends_on=[])
        assert cache.get("key1") == "value1"

    def test_get_missing_returns_none(self):
        cache = self._cache()
        assert cache.get("nonexistent") is None

    def test_explicit_invalidate(self):
        cache = self._cache()
        cache.set("k", "v", depends_on=[])
        assert cache.invalidate("k") is True
        assert cache.get("k") is None

    def test_explicit_invalidate_missing(self):
        cache = self._cache()
        assert cache.invalidate("missing") is False

    def test_graph_driven_invalidation(self):
        edges = [
            _edge(f"{_M}consumer.py", "imports", f"{_M}dep.py"),
        ]
        cache = self._cache(edges)
        cache.set("result1", 42, depends_on=["consumer.py"])
        cache.set("unrelated", 99, depends_on=["other.py"])
        evicted = cache.invalidate_for_change("dep.py")
        assert evicted == 1
        assert cache.get("result1") is None
        assert cache.get("unrelated") == 99

    def test_invalidate_all(self):
        cache = self._cache()
        cache.set("a", 1, depends_on=[])
        cache.set("b", 2, depends_on=[])
        count = cache.invalidate_all()
        assert count == 2
        assert cache.size() == 0

    def test_size(self):
        cache = self._cache()
        assert cache.size() == 0
        cache.set("x", 1, depends_on=[])
        assert cache.size() == 1

    def test_stats(self):
        cache = self._cache()
        stats = cache.stats()
        assert stats["size"] == 0


class TestScanManifest:
    def test_to_dict(self):
        m = ScanManifest(scanner_version="2.0.0", schema_version="2.0")
        d = m.to_dict()
        assert d["scanner_version"] == "2.0.0"
        assert "scanner_self_test_passed" in d

    def test_scan_result_to_dict_roundtrip(self):
        result = ScanResult(
            edges=[
                _edge(f"{_M}a.py", "imports", f"{_M}b.py"),
            ],
            modules=["a.py", "b.py"],
            digest="abc123",
            commit_sha="sha1",
        )
        d = result.to_dict()
        restored = ScanResult.from_dict(d)
        assert restored.digest == "abc123"
        assert restored.commit_sha == "sha1"
        assert len(restored.edges) == 1
        assert restored.modules == ["a.py", "b.py"]
