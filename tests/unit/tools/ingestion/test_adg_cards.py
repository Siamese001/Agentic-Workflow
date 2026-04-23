"""Unit tests for the ADG semantic card projector.

Uses an in-test SQLite fixture instead of a real ADG snapshot so tests are
deterministic and CI-friendly. Every card kind gets a shape-invariant test
(card_id, chroma_id, metadata primitives, snapshot_id).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Callable

import pytest

from tools.ingestion.adg_cards import (
    CardKind,
    HotspotCard,
    PathCard,
    SymbolCard,
    ViolationCard,
    coerce_metadata,
)
from tools.ingestion.adg_cards._helpers import (
    archetype_for,
    impact_score,
    layer_multiplier,
    surface_for,
)
from tools.ingestion.adg_cards.hotspot_emitter import emit_hotspot_cards
from tools.ingestion.adg_cards.path_emitter import emit_path_cards
from tools.ingestion.adg_cards.symbol_emitter import emit_symbol_cards
from tools.ingestion.adg_cards.violation_emitter import emit_violation_cards

SNAPSHOT_ID = "test_snapshot_0001"


@pytest.fixture(name="adg_fixture_db")
def _adg_fixture_db(tmp_path: Path) -> Path:
    """Minimal ADG schema with two nodes, one violation, one bypass, one bridge."""

    db = tmp_path / "adg.sqlite"
    conn = sqlite3.connect(db)
    try:
        conn.executescript(
            """
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT, entity_type TEXT, layer TEXT,
                identity_kind TEXT, confidence REAL, resolved_path TEXT,
                precision_type TEXT, span_start INT, span_end INT, span_line INT,
                span_column INT, span_end_line INT, span_end_column INT,
                logical_sequence_id TEXT, control_path_id TEXT, temporal_order INT,
                type_surface TEXT, enclosing_symbol TEXT
            );
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY, src_id INT, dst_id INT, relation_type TEXT,
                edge_kind TEXT, source_file TEXT, line_no INT, symbol TEXT,
                semantic_type TEXT, confidence_score REAL,
                source_span_start INT, source_span_end INT,
                source_span_line INT, source_span_column INT,
                target_span_start INT, target_span_end INT,
                target_span_line INT, target_span_column INT,
                dynamic_resolution TEXT
            );
            CREATE TABLE violations (
                id INTEGER PRIMARY KEY, edge_id INT, category TEXT, evidence TEXT,
                file_path TEXT, line_no INT, disposition TEXT, disposition_source TEXT,
                disposition_date TEXT, severity TEXT, violation_class TEXT
            );
            CREATE TABLE mv_hotspot_centrality (
                snapshot_id TEXT, node_id INT, adg_name TEXT, layer TEXT,
                resolved_path TEXT, fan_in INT, fan_out INT, degree INT,
                betweenness_approx REAL, degree_centrality REAL
            );
            CREATE TABLE mv_gateway_bypass_paths (
                snapshot_id TEXT, edge_id INT, src_file TEXT, src_layer TEXT,
                provider_symbol TEXT, source_file TEXT, line_no INT, bypass_type TEXT
            );
            CREATE TABLE mv_graph_chokepoint_bridges (
                snapshot_id TEXT, node_id INT, file_path TEXT, layer TEXT,
                fan_in INT, fan_out INT, bridge_score REAL, imbalance_ratio REAL,
                bridge_type TEXT
            );
            CREATE TABLE mv_dependency_cone_risk (
                snapshot_id TEXT, node_id INT, adg_name TEXT, layer TEXT,
                resolved_path TEXT, direct_fan_in INT, hop2_fan_in INT, hop3_fan_in INT,
                transitive_depth_approx INT, cone_risk_score REAL
            );
            CREATE TABLE mv_debt_concentration_hotspots (
                snapshot_id TEXT, file TEXT, layer TEXT,
                p0_count INT, p1_count INT, p2_count INT, p3_count INT,
                total_violations INT, total_debt_score REAL, hotspot_rank INT
            );
            CREATE TABLE mv_exemptions_near_critical_paths (
                snapshot_id TEXT, edge_id INT, file TEXT, layer TEXT,
                exemption_kind TEXT, source_file TEXT, line_no INT,
                criticality_score REAL, proximity_flag INT
            );
            """
        )
        snap = SNAPSHOT_ID
        conn.execute(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, enclosing_symbol)"
            " VALUES (1, 'mod_a', 'module', 'L3', 'x/a.py', NULL)"
        )
        conn.execute(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path)"
            " VALUES (2, 'fn_b', 'function', 'L5', 'x/b.py')"
        )
        conn.execute(
            "INSERT INTO mv_hotspot_centrality VALUES (?, 1, 'mod_a', 'L3', 'x/a.py', 12, 3, 15, 0.5, 0.2)",
            (snap,),
        )
        conn.execute(
            "INSERT INTO mv_hotspot_centrality VALUES (?, 2, 'fn_b', 'L5', 'x/b.py', 7, 2, 9, 0.3, 0.1)",
            (snap,),
        )
        conn.execute(
            "INSERT INTO mv_dependency_cone_risk VALUES (?, 1, 'mod_a', 'L3', 'x/a.py', 12, 40, 80, 3, 7.5)",
            (snap,),
        )
        conn.execute(
            "INSERT INTO mv_debt_concentration_hotspots VALUES (?, 'x/a.py', 'L3', 1, 2, 0, 0, 3, 9.9, 1)",
            (snap,),
        )
        conn.execute(
            "INSERT INTO violations VALUES (10, 100, 'antipattern', 'evidence-text',"
            " 'x/a.py', 42, 'open', 'linter', NULL, 'HIGH', 'safety')"
        )
        conn.execute(
            "INSERT INTO mv_exemptions_near_critical_paths VALUES (?, 100, 'x/a.py', 'L3', 'guardian',"
            " 'x/a.py', 42, 0.88, 1)",
            (snap,),
        )
        conn.execute(
            "INSERT INTO mv_gateway_bypass_paths VALUES (?, 500, 'x/a.py', 'L3', 'provider_x',"
            " 'x/a.py', 10, 'direct_provider_bypass')",
            (snap,),
        )
        conn.execute(
            "INSERT INTO mv_graph_chokepoint_bridges VALUES (?, 2, 'x/b.py', 'L5', 7, 2, 0.91, 3.5,"
            " 'high_impact_bridge')",
            (snap,),
        )
        conn.commit()
    finally:
        conn.close()
    return db


# ---------------------------------------------------------------------------
# Helper-level tests (pure functions)
# ---------------------------------------------------------------------------


def test_layer_multiplier_known_and_unknown() -> None:
    assert layer_multiplier("L5") == 2.0
    assert layer_multiplier("L2") == 1.0
    assert layer_multiplier("L99") == 1.0
    assert layer_multiplier(None) == 1.0


def test_surface_mapping() -> None:
    assert surface_for("L4") == "State"
    assert surface_for("L5") == "Security"
    assert surface_for("L6") == "Observability"
    assert surface_for(None) == "None"


def test_archetype_dispatch() -> None:
    assert archetype_for("L5", 3, 1) == "SAFETY_GATEKEEPER"
    assert archetype_for("L4", 3, 1) == "STATE_NODE"
    assert archetype_for("L3", 3, 1) == "ORCHESTRATOR"
    assert archetype_for("L2", 100, 1) == "CENTRAL_DEPENDENCY"
    assert archetype_for("L2", 1, 20) == "ORCHESTRATOR"  # fan_out dominance rule


def test_impact_score_monotone_in_fan_in() -> None:
    low = impact_score(1, 0, "L2")
    high = impact_score(1, 1000, "L2")
    assert high > low


def test_coerce_metadata_chroma_primitives() -> None:
    out = coerce_metadata({"a": 1, "b": None, "c": [1, 2], "d": "x"})
    assert out == {"a": 1, "b": "", "c": "[1, 2]", "d": "x"}


# ---------------------------------------------------------------------------
# Emitter tests (use the fixture DB)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "emitter, card_type, kind",
    [
        (emit_symbol_cards, SymbolCard, CardKind.SYMBOL),
        (emit_hotspot_cards, HotspotCard, CardKind.HOTSPOT),
        (emit_violation_cards, ViolationCard, CardKind.VIOLATION),
        (emit_path_cards, PathCard, CardKind.PATH),
    ],
)
def test_emitter_shape_invariants(
    adg_fixture_db: Path,
    emitter: Callable,
    card_type: type,
    kind: CardKind,
) -> None:
    cards = list(emitter(adg_fixture_db))
    assert cards, f"{kind.value} emitter produced no cards"
    for card in cards:
        assert isinstance(card, card_type)
        assert card.card_kind is kind
        assert card.card_id
        assert card.chroma_id().startswith(f"{kind.value}:")
        assert card.document and isinstance(card.document, str)
        assert card.snapshot_id == SNAPSHOT_ID
        for value in card.metadata.values():
            assert isinstance(value, (str, int, float, bool)), (
                f"non-primitive metadata for {kind.value}: {value!r}"
            )


def test_hotspot_archetype_reflects_layer(adg_fixture_db: Path) -> None:
    cards = {c.metadata["adg_name"]: c for c in emit_hotspot_cards(adg_fixture_db)}
    assert cards["mod_a"].metadata["archetype"] == "ORCHESTRATOR"
    # fn_b (L5) should be classified SAFETY_GATEKEEPER regardless of fan counts.
    assert cards["fn_b"].metadata["archetype"] == "SAFETY_GATEKEEPER"


def test_path_emitter_yields_both_kinds(adg_fixture_db: Path) -> None:
    kinds = {c.metadata["path_kind"] for c in emit_path_cards(adg_fixture_db)}
    assert kinds == {"gateway_bypass", "chokepoint_bridge"}


def test_violation_card_surfaces_exemption_context(adg_fixture_db: Path) -> None:
    (card,) = list(emit_violation_cards(adg_fixture_db))
    assert card.metadata["severity"] == "HIGH"
    assert card.metadata["exemption_kind"] == "guardian"
    assert card.metadata["criticality_score"] == pytest.approx(0.88)
