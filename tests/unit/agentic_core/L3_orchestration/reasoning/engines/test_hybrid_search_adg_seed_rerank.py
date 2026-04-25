"""Unit tests for HybridSearchEngine ADG-seed + ADG-rerank (Wave F).

Builds a small synthetic ADG SQLite (nodes + mv_hotspot_centrality) per test
so behavior is deterministic and independent of the live snapshot. Asserts:

* ``_adg_rerank`` is additive (never reorders by itself), preserves score for
  rows with no ADG linkage, and applies the §23 layer multiplier.
* ``adg_seed`` extracts identifier tokens, matches against adg_name tail,
  ranks by centrality, and honors the limit + optional layer_filter.
* The pipeline degrades gracefully when the ADG path is missing.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchEngine,
    HybridSearchResult,
)


@pytest.fixture(name="adg_db")
def _adg_db(tmp_path: Path) -> Path:
    db = tmp_path / "adg.sqlite"
    conn = sqlite3.connect(db)
    try:
        conn.execute(
            """
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                layer TEXT,
                resolved_path TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE mv_hotspot_centrality (
                snapshot_id TEXT,
                node_id INTEGER,
                adg_name TEXT,
                layer TEXT,
                resolved_path TEXT,
                fan_in INTEGER,
                fan_out INTEGER,
                degree INTEGER,
                betweenness_approx REAL,
                degree_centrality REAL
            )
            """
        )
        # 101 — L5 safety module, high centrality
        # 202 — L3 orchestration, medium centrality
        # 303 — L6 observability, low centrality
        # 404 — unknown layer, no MV row (missing from hotspots)
        conn.executemany(
            "INSERT INTO nodes (id, adg_name, layer, resolved_path) VALUES (?,?,?,?)",
            [
                (
                    101,
                    "ADG::Symbol::agentic_core.L5_safety.gateway.Guardian",
                    "L5",
                    "agentic_core/L5_safety/gateway.py",
                ),
                (
                    202,
                    "ADG::Symbol::agentic_core.L3_orchestration.router.Router",
                    "L3",
                    "agentic_core/L3_orchestration/router.py",
                ),
                (
                    303,
                    "ADG::Symbol::agentic_core.L6_observability.tracer.Tracer",
                    "L6",
                    "agentic_core/L6_observability/tracer.py",
                ),
                (404, "ADG::Module::some/unknown_module.py", "L_UNKNOWN", "some/unknown_module.py"),
            ],
        )
        conn.executemany(
            "INSERT INTO mv_hotspot_centrality VALUES (?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    "snap1",
                    101,
                    "ADG::Symbol::Guardian",
                    "L5",
                    "agentic_core/L5_safety/gateway.py",
                    100,
                    5,
                    105,
                    50.0,
                    0.8,
                ),
                (
                    "snap1",
                    202,
                    "ADG::Symbol::Router",
                    "L3",
                    "agentic_core/L3_orchestration/router.py",
                    40,
                    10,
                    50,
                    5.0,
                    0.4,
                ),
                (
                    "snap1",
                    303,
                    "ADG::Symbol::Tracer",
                    "L6",
                    "agentic_core/L6_observability/tracer.py",
                    5,
                    2,
                    7,
                    0.1,
                    0.05,
                ),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return db


def _result(chunk_id: str, score: float, **meta) -> HybridSearchResult:
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=f"content:{chunk_id}",
        metadata=dict(meta),
        combined_score=score,
        source="vector",
        vector_score=score,
    )


# ---------------------------------------------------------------------------
# _adg_rerank
# ---------------------------------------------------------------------------


def test_rerank_empty_results(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    assert engine._adg_rerank([]) == []


def test_rerank_no_adg_path_returns_input(tmp_path: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(tmp_path / "missing.sqlite"))
    rows = [_result("c1", 0.5, adg_node_id=101, layer="L5")]
    out = engine._adg_rerank(rows)
    assert [r.combined_score for r in out] == [0.5]


def test_rerank_applies_layer_multiplier_and_centrality(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    rows = [
        _result("c-l5", 0.5, adg_node_id=101, layer="L5"),  # bonus = 0.15*2.0*0.8 = 0.24
        _result("c-l3", 0.5, adg_node_id=202, layer="L3"),  # bonus = 0.15*1.75*0.4 = 0.105
        _result("c-l6", 0.5, adg_node_id=303, layer="L6"),  # bonus = 0.15*0.75*0.05 = 0.0056
        _result("c-none", 0.5),  # no adg_node_id → unchanged
    ]
    out = engine._adg_rerank(rows)
    by_id = {r.chunk_id: r for r in out}
    assert by_id["c-l5"].combined_score == pytest.approx(0.5 + 0.15 * 2.0 * 0.8)
    assert by_id["c-l3"].combined_score == pytest.approx(0.5 + 0.15 * 1.75 * 0.4)
    assert by_id["c-l6"].combined_score == pytest.approx(0.5 + 0.15 * 0.75 * 0.05)
    assert by_id["c-none"].combined_score == 0.5


def test_rerank_passes_through_unknown_node_id(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    # node 404 exists in `nodes` but NOT in mv_hotspot_centrality.
    rows = [_result("c", 0.5, adg_node_id=404, layer="L_UNKNOWN")]
    out = engine._adg_rerank(rows)
    assert out[0].combined_score == 0.5


def test_rerank_unparseable_node_id_passes_through(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    rows = [_result("c", 0.5, adg_node_id="not-an-int", layer="L5")]
    out = engine._adg_rerank(rows)
    assert out[0].combined_score == 0.5


def test_rerank_is_additive_does_not_reorder(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    rows = [
        _result("a", 0.9, adg_node_id=303, layer="L6"),  # small bonus
        _result("b", 0.5, adg_node_id=101, layer="L5"),  # big bonus
    ]
    out = engine._adg_rerank(rows)
    # Output order must match input order — rerank does not sort.
    assert [r.chunk_id for r in out] == ["a", "b"]


def test_rerank_falls_back_to_mv_layer_when_metadata_layer_missing(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    rows = [_result("c", 0.5, adg_node_id=101)]  # no layer on the result
    out = engine._adg_rerank(rows)
    # Should use mv_hotspot_centrality.layer=L5 → multiplier=2.0
    assert out[0].combined_score == pytest.approx(0.5 + 0.15 * 2.0 * 0.8)


# ---------------------------------------------------------------------------
# adg_seed
# ---------------------------------------------------------------------------


def test_seed_finds_symbol_by_name(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    out = engine.adg_seed("Please explain Guardian behavior")
    assert len(out) == 1
    assert out[0]["node_id"] == 101
    assert out[0]["layer"] == "L5"
    assert out[0]["degree_centrality"] == pytest.approx(0.8)


def test_seed_ranks_by_centrality(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    # Query mentions both Router and Tracer — higher centrality wins.
    out = engine.adg_seed("how does Router relate to Tracer")
    assert [r["node_id"] for r in out] == [202, 303]


def test_seed_respects_limit(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    out = engine.adg_seed("Guardian Router Tracer", limit=2)
    assert len(out) == 2
    # Top-2 by centrality: Guardian (0.8), Router (0.4).
    assert [r["node_id"] for r in out] == [101, 202]


def test_seed_empty_query_returns_empty(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    assert engine.adg_seed("") == []
    assert engine.adg_seed("   ") == []


def test_seed_short_tokens_ignored(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    # All tokens < 3 chars — nothing to match.
    assert engine.adg_seed("a is to be") == []


def test_seed_layer_filter(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    out = engine.adg_seed("Guardian Router Tracer", layer_filter="L3")
    assert len(out) == 1
    assert out[0]["node_id"] == 202


def test_seed_missing_adg_returns_empty(tmp_path: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(tmp_path / "missing.sqlite"))
    assert engine.adg_seed("Guardian") == []


def test_seed_limit_zero_returns_empty(adg_db: Path) -> None:
    engine = HybridSearchEngine(adg_db_path=str(adg_db))
    assert engine.adg_seed("Guardian", limit=0) == []
