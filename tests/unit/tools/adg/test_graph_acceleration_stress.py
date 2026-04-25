"""
Stress and hardening tests for graph acceleration.

Covers:
- Input validation & SQL injection guards
- Concurrent reads
- Large-graph performance
- Edge cases (empty graph, self-loops, duplicates, missing tables)
- Resource lifecycle (context manager, repeated open/close)
- Malformed schema tolerance
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "tools"))

from tools.adg.analysis.sqlite_direct import (  # noqa: E402
    GraphQueryHelper,
    _validate_relation_types,
)
from tools.adg.analysis.duckdb_integration import DuckDBGraphAnalyzer  # noqa: E402
from tools.adg.analysis.networkx_analysis import NetworkXAnalyzer  # noqa: E402
from tools.adg.analysis.materialized_views import MaterializedViewManager  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #


def _make_db(tmp_path: Path, nodes: list, edges: list) -> str:
    db = tmp_path / "stress.sqlite"
    conn = sqlite3.connect(str(db))
    conn.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            layer TEXT,
            node_type TEXT,
            file_path TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE edges (
            src_id INTEGER,
            tgt_id INTEGER,
            relation_type TEXT
        )
    """)
    conn.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?)", nodes)
    conn.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)
    conn.commit()
    conn.close()
    return str(db)


@pytest.fixture
def small_db(tmp_path):
    nodes = [
        (1, "alpha", "L0_routing", "function", "a.py"),
        (2, "beta", "L1_cognition", "class", "b.py"),
        (3, "gamma", "L2_execution", "function", "c.py"),
    ]
    edges = [
        (1, 2, "imports"),
        (2, 3, "calls"),
        (1, 1, "self_ref"),  # self-loop
        (1, 2, "imports"),  # duplicate edge
    ]
    return _make_db(tmp_path, nodes, edges)


@pytest.fixture
def empty_db(tmp_path):
    return _make_db(tmp_path, [], [])


@pytest.fixture
def large_db(tmp_path):
    """5000 nodes, ~20000 edges across 6 layers."""
    layers = [f"L{i}_layer" for i in range(6)]
    nodes = [(i, f"node_{i}", layers[i % 6], "function", f"file_{i // 100}.py") for i in range(1, 5001)]
    edges = []
    for i in range(1, 5001):
        # Each node has ~4 outgoing edges to nearby nodes
        for offset in (1, 7, 23, 101):
            tgt = ((i + offset - 1) % 5000) + 1
            edges.append((i, tgt, "imports" if offset % 2 else "calls"))
    return _make_db(tmp_path, nodes, edges)


# --------------------------------------------------------------------------- #
# Input validation / SQL injection                                            #
# --------------------------------------------------------------------------- #


class TestInputValidation:
    def test_validate_relation_types_rejects_injection(self):
        with pytest.raises(ValueError):
            _validate_relation_types(["imports; DROP TABLE nodes"])
        with pytest.raises(ValueError):
            _validate_relation_types(["imports' OR 1=1--"])
        with pytest.raises(ValueError):
            _validate_relation_types([""])
        with pytest.raises(TypeError):
            _validate_relation_types("imports")  # type: ignore[arg-type]

    def test_validate_relation_types_accepts_valid(self):
        assert _validate_relation_types(None) is None
        assert _validate_relation_types([]) is None
        assert _validate_relation_types(["imports", "calls"]) == ["imports", "calls"]

    def test_find_nodes_rejects_non_string(self, small_db):
        with GraphQueryHelper(small_db) as h:
            with pytest.raises(TypeError):
                h.find_nodes_by_name(123)  # type: ignore[arg-type]

    def test_find_nodes_empty_returns_empty(self, small_db):
        with GraphQueryHelper(small_db) as h:
            assert h.find_nodes_by_name("") == []

    def test_find_nodes_like_wildcard_escaped(self, small_db):
        """LIKE wildcards in user input must not match unintended rows."""
        with GraphQueryHelper(small_db) as h:
            # '%' as literal should not match anything (no node contains literal %)
            assert h.find_nodes_by_name("%", exact_match=False) == []
            assert h.find_nodes_by_name("_", exact_match=False) == []

    def test_fan_in_rejects_non_int(self, small_db):
        with GraphQueryHelper(small_db) as h:
            with pytest.raises(TypeError):
                h.get_fan_in("1")  # type: ignore[arg-type]

    def test_execute_query_rejects_writes(self, small_db):
        with GraphQueryHelper(small_db) as h:
            with pytest.raises(ValueError):
                h.execute_query("DELETE FROM nodes")
            with pytest.raises(ValueError):
                h.execute_query("DROP TABLE nodes")
            with pytest.raises(ValueError):
                h.execute_query("UPDATE nodes SET adg_name='x'")

    def test_execute_query_rejects_multistatement(self, small_db):
        with GraphQueryHelper(small_db) as h:
            with pytest.raises(ValueError):
                h.execute_query("SELECT 1; DROP TABLE nodes")

    def test_execute_query_rejects_empty(self, small_db):
        with GraphQueryHelper(small_db) as h:
            with pytest.raises(ValueError):
                h.execute_query("")
            with pytest.raises(ValueError):
                h.execute_query("   ")

    def test_execute_query_allows_with_clause(self, small_db):
        with GraphQueryHelper(small_db) as h:
            res = h.execute_query("WITH x AS (SELECT 1 AS v) SELECT v FROM x")
            assert res == [{"v": 1}]


class TestDuckDBHardening:
    def test_custom_query_blocks_writes(self, small_db):
        a = DuckDBGraphAnalyzer(small_db)
        try:
            for q in [
                "DELETE FROM adg.nodes",
                "DROP TABLE adg.nodes",
                "INSERT INTO adg.nodes VALUES (99,'x','y','z','w')",
                "ATTACH 'evil.db' AS e",
                "PRAGMA database_list",
            ]:
                result = a.execute_custom_query(q)
                assert "error" in result, f"Should reject: {q}"
        finally:
            a.close()

    def test_custom_query_blocks_multistatement(self, small_db):
        a = DuckDBGraphAnalyzer(small_db)
        try:
            r = a.execute_custom_query("SELECT 1; SELECT 2")
            assert "error" in r
        finally:
            a.close()

    def test_custom_query_allows_select(self, small_db):
        a = DuckDBGraphAnalyzer(small_db)
        try:
            r = a.execute_custom_query("SELECT COUNT(*) AS c FROM adg.nodes")
            assert r.get("row_count") == 1
            assert r["rows"][0][0] == 3
        finally:
            a.close()

    def test_custom_query_truncates_large_result(self, large_db):
        a = DuckDBGraphAnalyzer(large_db)
        try:
            r = a.execute_custom_query(
                "SELECT n1.id FROM adg.nodes n1, adg.nodes n2"  # cartesian = 25M rows
            )
            assert r["row_count"] <= 10_000
            assert r.get("truncated") is True
        finally:
            a.close()


# --------------------------------------------------------------------------- #
# Edge cases                                                                  #
# --------------------------------------------------------------------------- #


class TestEdgeCases:
    def test_empty_graph_helper(self, empty_db):
        with GraphQueryHelper(empty_db) as h:
            assert h.find_nodes_by_name("anything") == []
            assert h.get_fan_in(1) == []
            assert h.get_fan_out(1) == []
            stats = h.get_graph_statistics()
            assert stats["total_nodes"] == 0
            assert stats["total_edges"] == 0

    def test_empty_graph_networkx(self, empty_db):
        a = NetworkXAnalyzer(empty_db)
        try:
            assert a.analyze_pagerank() == []
            assert a.detect_communities() == {}
            summary = a.get_graph_summary()
            assert summary["nodes"] == 0
        finally:
            a.close()

    def test_self_loop_handled(self, small_db):
        with GraphQueryHelper(small_db) as h:
            # node 1 has a self-loop; fan_in and fan_out should both include it
            fin = h.get_fan_in(1, relation_types=["self_ref"])
            fout = h.get_fan_out(1, relation_types=["self_ref"])
            assert len(fin) == 1
            assert len(fout) == 1

    def test_duplicate_edges_counted(self, small_db):
        with GraphQueryHelper(small_db) as h:
            # 1->2 imports appears twice in fixture
            fout = h.get_fan_out(1, relation_types=["imports"])
            assert len(fout) == 2

    def test_missing_db_raises(self, tmp_path):
        with pytest.raises(ValueError):
            GraphQueryHelper(str(tmp_path / "does_not_exist.sqlite"))

    def test_corrupt_schema_tolerated(self, tmp_path):
        """DB with no nodes/edges tables → execute_query returns [] on error."""
        db = tmp_path / "corrupt.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE wrong (x INTEGER)")
        conn.commit()
        conn.close()
        with GraphQueryHelper(str(db)) as h:
            # Querying nonexistent table should not crash
            assert h.execute_query("SELECT * FROM nodes") == []

    def test_materialized_views_idempotent(self, small_db):
        """Creating the same view twice should not error (DROP IF EXISTS)."""
        m = MaterializedViewManager(small_db)
        try:
            m.create_centrality_view()
            m.create_centrality_view()  # second call must succeed
            stats = m.get_view_stats()
            assert "mv_node_centrality" in stats
        finally:
            m.close()


# --------------------------------------------------------------------------- #
# Resource lifecycle                                                          #
# --------------------------------------------------------------------------- #


class TestResourceLifecycle:
    def test_context_manager_closes(self, small_db):
        with GraphQueryHelper(small_db) as h:
            h.find_nodes_by_name("alpha")
        # After exit, conn should be closed
        with pytest.raises(sqlite3.ProgrammingError):
            h.conn.execute("SELECT 1")

    def test_repeated_open_close(self, small_db):
        for _ in range(50):
            h = GraphQueryHelper(small_db)
            h.find_nodes_by_name("alpha")
            h.close()

    def test_close_is_idempotent(self, small_db):
        h = GraphQueryHelper(small_db)
        h.close()
        h.close()  # second close should not raise


# --------------------------------------------------------------------------- #
# Concurrency                                                                 #
# --------------------------------------------------------------------------- #


class TestConcurrency:
    def test_concurrent_readers_same_db(self, small_db):
        """16 threads reading the same DB through separate helpers must not fail."""
        errors: list = []

        def worker():
            try:
                h = GraphQueryHelper(small_db)
                for _ in range(20):
                    assert h.find_nodes_by_name("alpha")
                    assert h.get_fan_out(1) is not None
                h.close()
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(16)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        assert not errors, f"Concurrent readers raised: {errors}"

    def test_concurrent_duckdb_analyzers(self, small_db):
        """Each thread gets its own analyzer (DuckDB conn is not thread-safe)."""
        errors: list = []

        def worker():
            try:
                a = DuckDBGraphAnalyzer(small_db)
                a.get_layer_distribution()
                a.close()
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        assert not errors, f"Concurrent DuckDB analyzers raised: {errors}"


# --------------------------------------------------------------------------- #
# Performance                                                                 #
# --------------------------------------------------------------------------- #


class TestPerformance:
    def test_large_graph_fan_in_under_1s(self, large_db):
        with GraphQueryHelper(large_db) as h:
            start = time.perf_counter()
            for nid in (1, 100, 1000, 4999):
                fin = h.get_fan_in(nid)
                assert isinstance(fin, list)
            elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Fan-in queries too slow: {elapsed:.3f}s"

    def test_large_graph_layer_distribution_under_2s(self, large_db):
        a = DuckDBGraphAnalyzer(large_db)
        try:
            start = time.perf_counter()
            d = a.get_layer_distribution()
            elapsed = time.perf_counter() - start
            assert d["total_layers"] == 6
            assert elapsed < 2.0, f"Layer distribution too slow: {elapsed:.3f}s"
        finally:
            a.close()

    def test_large_graph_materialized_views_under_5s(self, large_db):
        m = MaterializedViewManager(large_db)
        try:
            start = time.perf_counter()
            m.create_layer_dependency_view()
            m.create_chokepoint_view()
            elapsed = time.perf_counter() - start
            stats = m.get_view_stats()
            assert stats["mv_layer_dependencies"] > 0
            assert elapsed < 5.0, f"MV creation too slow: {elapsed:.3f}s"
        finally:
            m.close()

    def test_large_graph_networkx_pagerank_under_10s(self, large_db):
        a = NetworkXAnalyzer(large_db)
        try:
            start = time.perf_counter()
            scores = a.analyze_pagerank()
            elapsed = time.perf_counter() - start
            assert len(scores) == 5000
            assert elapsed < 10.0, f"PageRank on 5k nodes too slow: {elapsed:.3f}s"
        finally:
            a.close()


# --------------------------------------------------------------------------- #
# Result row caps                                                             #
# --------------------------------------------------------------------------- #


class TestResultCaps:
    def test_fan_in_capped(self, large_db):
        """Fan-in results are bounded; should not blow up memory."""
        with GraphQueryHelper(large_db) as h:
            res = h.get_fan_in(1)
            # Whatever the actual count, it must not exceed _MAX_RESULT_ROWS
            assert len(res) <= 100_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
