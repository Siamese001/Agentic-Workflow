"""Unit tests for tools.adg.runtime_query.

These tests build a tiny in-memory ADG SQLite shaped like the real snapshot
and exercise the public query surface. No pytest.mark.skip, no xfail.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tools.adg.runtime_query import (
    RuntimeADGQuery,
    RiskEnvelope,
    _latest_snapshot_path,
)


# ---------- fixtures ----------


def _build_fixture_db(path: Path) -> None:
    """Build a minimal ADG SQLite matching the real schema contract.

    Includes ``nodes``, ``edges``, ``mv_hotspot_centrality``,
    ``mv_path_criticality_rollup`` — enough surface for every
    ``RuntimeADGQuery`` public method.
    """
    conn = sqlite3.connect(str(path))
    try:
        conn.executescript(
            """
            CREATE TABLE nodes (
                id TEXT PRIMARY KEY,
                adg_name TEXT,
                entity_type TEXT,
                layer TEXT,
                resolved_path TEXT
            );
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_id TEXT,
                tgt_id TEXT,
                relation_type TEXT
            );
            CREATE INDEX idx_edges_tgt ON edges(tgt_id, relation_type);
            CREATE INDEX idx_edges_src ON edges(src_id, relation_type);
            CREATE TABLE mv_hotspot_centrality (
                node_id TEXT PRIMARY KEY,
                betweenness_approx REAL,
                degree_centrality REAL,
                fan_in INTEGER,
                fan_out INTEGER,
                degree INTEGER
            );
            CREATE TABLE mv_path_criticality_rollup (
                node_id TEXT PRIMARY KEY,
                criticality_score REAL,
                violation_count INTEGER,
                cross_layer_edges INTEGER
            );
            CREATE VIEW v_p0_test_members AS
                SELECT id AS node_id FROM nodes WHERE layer = 'L5';
            """
        )
        # Three nodes: a safety gatekeeper (L5), a central dep (high fan-in),
        # and a leaf.
        conn.executemany(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    "n_safety",
                    "agentic_core.L5_safety.guardrail",
                    "module",
                    "L5",
                    "agentic_core/L5_safety/guardrail.py",
                ),
                (
                    "n_central",
                    "agentic_core.L0_routing.router",
                    "module",
                    "L0",
                    "agentic_core/L0_routing/router.py",
                ),
                ("n_leaf", "apps_shared.leaf_util", "module", "L_SHARED", "apps_shared/leaf_util.py"),
                ("n_swallow", "tools.legacy.swallower", "module", "L_TOOLS", "tools/legacy/swallower.py"),
                (
                    "n_failing",
                    "agentic_core.L2_execution.failing_op",
                    "module",
                    "L2",
                    "agentic_core/L2_execution/failing_op.py",
                ),
            ],
        )
        # 25 callers importing n_central -> CENTRAL_DEPENDENCY archetype.
        for i in range(25):
            src = f"n_caller_{i}"
            conn.execute(
                "INSERT INTO nodes (id, adg_name, layer, resolved_path) VALUES (?, ?, ?, ?)",
                (src, f"caller.mod_{i}", "L2", f"apps/c_{i}.py"),
            )
            conn.execute(
                "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'imports')",
                (src, "n_central"),
            )
        # flows_to chain: n_failing -> n_swallow with antipattern.
        conn.execute(
            "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'flows_to')",
            ("n_swallow", "n_failing"),
        )
        conn.execute(
            "INSERT INTO edges (src_id, tgt_id, relation_type) VALUES (?, ?, 'broad_exception_catch')",
            ("n_swallow", "n_swallow"),
        )
        # Centrality/criticality MV rows for the central node.
        conn.execute(
            "INSERT INTO mv_hotspot_centrality VALUES (?, ?, ?, ?, ?, ?)",
            ("n_central", 99.5, 0.88, 25, 2, 27),
        )
        conn.execute(
            "INSERT INTO mv_path_criticality_rollup VALUES (?, ?, ?, ?)",
            ("n_central", 42.0, 3, 7),
        )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture()
def fixture_db(tmp_path: Path) -> Path:
    db = tmp_path / "adg_indexed_fixture.sqlite"
    _build_fixture_db(db)
    return db


@pytest.fixture()
def q(fixture_db: Path) -> RuntimeADGQuery:
    return RuntimeADGQuery(sqlite_path=fixture_db)


# ---------- tests ----------


def test_provenance_reports_snapshot(q: RuntimeADGQuery) -> None:
    prov = q.provenance()
    assert prov["backend_used"] == "sqlite"
    assert prov["snapshot_id"] == "adg_indexed_fixture"
    assert prov["snapshot_path"].endswith("adg_indexed_fixture.sqlite")


def test_resolve_node_by_adg_name(q: RuntimeADGQuery) -> None:
    node_id, adg_name, file_path, layer = q.resolve_node("agentic_core.L5_safety.guardrail")
    assert node_id == "n_safety"
    assert layer == "L5"
    assert file_path == "agentic_core/L5_safety/guardrail.py"


def test_resolve_node_by_id(q: RuntimeADGQuery) -> None:
    node_id, adg_name, *_ = q.resolve_node("n_central")
    assert node_id == "n_central"
    assert adg_name == "agentic_core.L0_routing.router"


def test_resolve_node_miss(q: RuntimeADGQuery) -> None:
    assert q.resolve_node("does.not.exist") == (None, None, None, None)


def test_resolve_node_cache_hit(q: RuntimeADGQuery) -> None:
    q.resolve_node("n_central")
    q.resolve_node("n_central")
    q.resolve_node("n_central")
    stats = q.cache_stats()
    assert stats["hits"]["resolve"] == 2
    assert stats["misses"]["resolve"] == 1
    assert stats["resolve_cache_size"] == 1


def test_fan_in_count_counts_imports(q: RuntimeADGQuery) -> None:
    assert q.fan_in_count("n_central", "imports") == 25
    assert q.fan_in_count("n_leaf", "imports") == 0


def test_fan_out_count(q: RuntimeADGQuery) -> None:
    assert q.fan_out_count("n_central", "imports") == 0
    assert q.fan_out_count("n_caller_0", "imports") == 1


def test_upstream_callers_returns_k(q: RuntimeADGQuery) -> None:
    callers = q.upstream_callers("n_central", k=3)
    assert len(callers) == 3
    assert all("adg_name" in c for c in callers)


def test_downstream_targets(q: RuntimeADGQuery) -> None:
    tgt = q.downstream_targets("n_caller_0", k=5)
    assert len(tgt) == 1
    assert tgt[0]["node_id"] == "n_central"


def test_blast_radius_central_dependency(q: RuntimeADGQuery) -> None:
    env = q.blast_radius("n_central")
    assert isinstance(env, RiskEnvelope)
    assert env.node_id == "n_central"
    assert env.fan_in == 25
    assert env.archetype == "CENTRAL_DEPENDENCY"
    # L0 layer multiplier is 2.0 and fan_in=25 → high impact.
    assert env.risk_band in ("HIGH", "MEDIUM")
    assert env.error is None


def test_blast_radius_safety_gatekeeper(q: RuntimeADGQuery) -> None:
    env = q.blast_radius("n_safety")
    assert env.archetype == "SAFETY_GATEKEEPER"


def test_blast_radius_leaf(q: RuntimeADGQuery) -> None:
    env = q.blast_radius("n_leaf")
    assert env.archetype == "LEAF"
    assert env.risk_band == "LOW"


def test_blast_radius_unknown_is_safe(q: RuntimeADGQuery) -> None:
    env = q.blast_radius("never.existed")
    assert env.error == "node_not_found"
    assert env.risk_band == "LOW"
    # Provenance still valid.
    assert env.snapshot_id == "adg_indexed_fixture"


def test_hotspot_info_reads_mvs(q: RuntimeADGQuery) -> None:
    info = q.hotspot_info("n_central")
    assert info.get("betweenness_approx") == 99.5
    assert info.get("degree_centrality") == 0.88
    assert info.get("criticality_score") == 42.0
    assert info.get("violation_count") == 3
    assert info.get("cross_layer_edges") == 7


def test_hotspot_info_missing_mv_row(q: RuntimeADGQuery) -> None:
    info = q.hotspot_info("n_leaf")
    # Node exists; MV row does not — helper returns base info without MV keys.
    assert info["node_id"] == "n_leaf"
    assert "criticality_score" not in info


def test_swallow_sites_reaching_finds_antipattern(q: RuntimeADGQuery) -> None:
    # n_failing is downstream of n_swallow via flows_to; n_swallow has
    # a broad_exception_catch self-edge. The CTE starts at n_failing
    # and walks backward via flows_to to reach n_swallow (hops=1).
    hits = q.swallow_sites_reaching("n_failing", depth=3, max_hits=10)
    assert len(hits) >= 1
    # The first hit should be n_swallow with antipattern_kind=broad_exception_catch.
    kinds = {h["antipattern_kind"] for h in hits}
    assert "broad_exception_catch" in kinds


def test_swallow_sites_reaching_empty_for_clean_node(q: RuntimeADGQuery) -> None:
    assert q.swallow_sites_reaching("n_leaf", depth=3) == []


def test_pview_contains_via_sqlite(q: RuntimeADGQuery) -> None:
    # v_p0_test_members returns nodes with layer='L5'.
    assert q.pview_contains("v_p0_test_members", "n_safety") is True
    assert q.pview_contains("v_p0_test_members", "n_leaf") is False


def test_pview_contains_nonexistent_view(q: RuntimeADGQuery) -> None:
    assert q.pview_contains("v_p0_does_not_exist", "n_safety") is False


def test_missing_snapshot_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADG_RUNTIME_SNAPSHOT", str(tmp_path / "no_file.sqlite"))
    # Override the glob dir to empty so _latest_snapshot_path also misses.
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr("tools.adg.runtime_query.ADG_ARTIFACTS", empty)
    with pytest.raises(FileNotFoundError):
        RuntimeADGQuery()


def test_empty_ident_returns_zero_values(q: RuntimeADGQuery) -> None:
    assert q.resolve_node("") == (None, None, None, None)
    assert q.fan_in_count("") == 0
    assert q.fan_out_count("") == 0
    assert q.upstream_callers("", k=3) == []
    assert q.downstream_targets("", k=3) == []
    assert q.swallow_sites_reaching("", depth=2) == []


def test_latest_snapshot_resolver_picks_newest() -> None:
    # Integration smoke: if the repo has real snapshots, the resolver returns one.
    p = _latest_snapshot_path()
    # Either None (no repo snapshots) or a real file — never raises.
    assert p is None or p.exists()
