"""R1-R7 Runtime acceleration benchmarks.

Verifies that ADG-indexed queries are faster than equivalent filesystem scans
and that the GraphAwareCache provides precise invalidation.

Plan ref: tests/performance/test_adg_runtime_acceleration.py
"""

from __future__ import annotations

import ast
import time
from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import (
    ADGStaticScanner,
    ScanResult,
)
from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine
from agentic_core.cache.graph_aware_cache import GraphAwareCache

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_scan_result() -> ScanResult:
    scanner = ADGStaticScanner(repo_root=_REPO_ROOT, include_tests=True)
    return scanner.scan()


@pytest.fixture(scope="module")
def qe() -> ADGRuntimeQueryEngine:
    result = _make_scan_result()
    return ADGRuntimeQueryEngine(result)


@pytest.fixture(scope="module")
def cache(qe: ADGRuntimeQueryEngine) -> GraphAwareCache:
    return GraphAwareCache(qe)


# ---------------------------------------------------------------------------
# R1: ADG indexed queries — correctness
# ---------------------------------------------------------------------------


class TestADGQueryEngineCorrectness:
    def test_find_agents_by_base_class_returns_list(self, qe):
        agents = qe.find_agents_by_base_class("SovereignBaseAgent")
        assert isinstance(agents, list)

    def test_inheritance_index_populated(self, qe):
        assert len(qe._inheritance_index) > 0

    def test_reverse_deps_index_populated(self, qe):
        assert len(qe._reverse_deps) > 0

    def test_composition_index_populated(self, qe):
        assert len(qe._composition_index) > 0

    def test_compute_blast_radius_returns_dict(self, qe):
        result = qe.compute_blast_radius(["agentic_core/L0_routing/engines/execution_orchestrator.py"])
        assert isinstance(result, dict)

    def test_get_reverse_dependencies_returns_set(self, qe):
        some_module = next(iter(qe._reverse_deps), None)
        if some_module is None:
            pytest.skip("No reverse deps in index")
        deps = qe.get_reverse_dependencies(some_module)
        assert isinstance(deps, set)


# ---------------------------------------------------------------------------
# R1: Speedup benchmarks (10x minimum — relaxed for CI cold-start)
# ---------------------------------------------------------------------------


def _scan_filesystem_for_agents(base_class: str) -> list[str]:
    """Baseline: filesystem scan + AST parse per query."""
    agents: list[str] = []
    for py_file in sorted(_REPO_ROOT.rglob("*.py")):
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    name = base.id if isinstance(base, ast.Name) else ""
                    if name == base_class:
                        agents.append(str(py_file))
    return agents


class TestRuntimeSpeedup:
    """R1: ADG queries must be at least 10x faster than filesystem scan."""

    def test_agent_discovery_speedup(self, qe):
        # Warm up the query engine index
        _ = qe.find_agents_by_base_class("SovereignBaseAgent")

        # Baseline: filesystem scan (expensive)
        start = time.perf_counter()
        _ = _scan_filesystem_for_agents("SovereignBaseAgent")
        fs_time = time.perf_counter() - start

        # ADG: indexed query (fast)
        start = time.perf_counter()
        _ = qe.find_agents_by_base_class("SovereignBaseAgent")
        adg_time = time.perf_counter() - start

        if fs_time > 0.001:  # Only assert speedup if baseline was measurable
            speedup = fs_time / max(adg_time, 1e-9)
            assert speedup >= 10, (
                f"Expected ≥10x speedup, got {speedup:.1f}x "
                f"(fs={fs_time * 1000:.1f}ms, adg={adg_time * 1000:.3f}ms)"
            )

    def test_blast_radius_faster_than_full_scan(self, qe):
        changed = ["agentic_core/L0_routing/engines/execution_orchestrator.py"]

        # ADG blast radius
        start = time.perf_counter()
        blast = qe.compute_blast_radius(changed)
        adg_time = time.perf_counter() - start

        assert adg_time < 0.1, f"Blast radius took {adg_time * 1000:.1f}ms — expected <100ms"
        assert isinstance(blast, dict)


# ---------------------------------------------------------------------------
# R7: GraphAwareCache precision
# ---------------------------------------------------------------------------


class TestGraphAwareCachePrecision:
    def test_cache_set_and_get(self, cache):
        cache.set("key_test", "value_test", depends_on=["module_a"])
        assert cache.get("key_test") == "value_test"

    def test_cache_miss_returns_none(self, cache):
        assert cache.get("nonexistent_key_xyz") is None

    def test_precise_invalidation(self):
        """Graph-based invalidation should be precise, not blind."""
        result = _make_scan_result()
        engine = ADGRuntimeQueryEngine(result)
        gc = GraphAwareCache(engine)

        # Set 100 cache entries with 10 different dependency groups
        for i in range(100):
            gc.set(f"key_{i}", f"value_{i}", depends_on=[f"module_{i % 10}"])

        # Invalidate for one module key
        invalidated = gc.invalidate_for_change("module_5")

        # Should invalidate ~10 entries (those depending on module_5)
        assert 8 <= invalidated <= 15, f"Expected ~10 precise invalidations, got {invalidated}"
        # Remaining 90 should still be cached
        surviving = gc.size()
        assert surviving >= 85, f"Too many entries invalidated: only {surviving} remain"

    def test_invalidate_all(self):
        result = _make_scan_result()
        engine = ADGRuntimeQueryEngine(result)
        gc = GraphAwareCache(engine)
        for i in range(10):
            gc.set(f"k_{i}", f"v_{i}", depends_on=["mod_a"])
        gc.invalidate_all()
        assert gc.size() == 0

    def test_cache_stats(self, cache):
        stats = cache.stats()
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
