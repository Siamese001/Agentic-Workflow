"""Unit tests for W2.2 graph-era alias layer (typed-edge-role-facet-guardrails-a6f3d2)."""
from __future__ import annotations

import pytest

from apps_rg.runtime.graph_era_aliases import (
    FACT_ERA_TO_GRAPH_ERA,
    GRAPH_ERA_FIELD_ALIASES,
    emit_graph_era_aliases,
    read_allowed_graph_evidence_ids,
    read_graph_evidence_id,
    read_graph_evidence_ids,
    read_selected_graph_evidence_plan,
)


def test_alias_map_covers_canonical_w22_pairs() -> None:
    """W2.2 canonical alias pairs from the plan."""
    assert GRAPH_ERA_FIELD_ALIASES == {
        "selected_graph_evidence_plan": "selected_fact_plan",
        "allowed_graph_evidence_ids": "allowed_fact_ids",
        "graph_evidence_ids": "source_fact_ids",
        "graph_evidence_id": "fact_id",
    }


def test_reverse_map_is_bijection() -> None:
    """Reverse map is a clean inverse."""
    assert FACT_ERA_TO_GRAPH_ERA == {v: k for k, v in GRAPH_ERA_FIELD_ALIASES.items()}
    assert len(FACT_ERA_TO_GRAPH_ERA) == len(GRAPH_ERA_FIELD_ALIASES)


def test_emit_aliases_copies_fact_to_graph() -> None:
    """Producer emits fact-era only → alias layer adds graph-era twin."""
    record: dict = {"source_fact_ids": ["fact_a", "fact_b"], "fact_id": "fact_a"}
    out = emit_graph_era_aliases(record)
    assert out is record
    assert record["graph_evidence_ids"] == ["fact_a", "fact_b"]
    assert record["graph_evidence_id"] == "fact_a"
    # Fact-era keys remain.
    assert record["source_fact_ids"] == ["fact_a", "fact_b"]
    assert record["fact_id"] == "fact_a"


def test_emit_aliases_copies_graph_to_fact_for_backcompat() -> None:
    """Producer emits graph-era only → alias layer back-fills fact-era for unmigrated readers."""
    record: dict = {"graph_evidence_ids": ["m_1", "m_2"]}
    emit_graph_era_aliases(record)
    assert record["source_fact_ids"] == ["m_1", "m_2"]


def test_emit_aliases_no_op_when_both_equal() -> None:
    """Both names present with equal payloads → no change."""
    record: dict = {
        "source_fact_ids": ["x"],
        "graph_evidence_ids": ["x"],
    }
    before = dict(record)
    emit_graph_era_aliases(record)
    assert record == before


def test_emit_aliases_raises_on_divergent_payloads() -> None:
    """Producer set both names with different payloads → ValueError (bug)."""
    record: dict = {
        "source_fact_ids": ["a"],
        "graph_evidence_ids": ["b"],
    }
    with pytest.raises(ValueError, match="divergent values for alias pair"):
        emit_graph_era_aliases(record)


def test_read_graph_evidence_ids_prefers_graph_era() -> None:
    """Reader returns graph-era when present, ignoring fact-era."""
    record = {
        "source_fact_ids": ["fact_a"],
        "graph_evidence_ids": ["graph_a", "graph_b"],
    }
    assert read_graph_evidence_ids(record) == ["graph_a", "graph_b"]


def test_read_graph_evidence_ids_falls_back_to_fact_era() -> None:
    """Reader falls back to fact-era when graph-era missing."""
    record = {"source_fact_ids": ["fact_a", "fact_b"]}
    assert read_graph_evidence_ids(record) == ["fact_a", "fact_b"]


def test_read_graph_evidence_ids_empty_when_missing() -> None:
    """No fact-era + no graph-era → empty list."""
    assert read_graph_evidence_ids({}) == []
    assert read_graph_evidence_ids({"unrelated": [1]}) == []


def test_read_graph_evidence_ids_normalizes_string_and_dedupes() -> None:
    """String becomes single-item list; duplicates stripped; blanks filtered."""
    assert read_graph_evidence_ids({"graph_evidence_ids": "single"}) == ["single"]
    assert read_graph_evidence_ids(
        {"graph_evidence_ids": ["a", "a", "", " b ", "b"]}
    ) == ["a", "b"]


def test_read_graph_evidence_id_singular() -> None:
    """Singular read prefers graph-era, falls back to fact_id."""
    assert read_graph_evidence_id({"graph_evidence_id": "g1"}) == "g1"
    assert read_graph_evidence_id({"fact_id": "f1"}) == "f1"
    assert read_graph_evidence_id({}) == ""
    # Graph-era wins.
    assert read_graph_evidence_id({"graph_evidence_id": "g", "fact_id": "f"}) == "g"


def test_read_allowed_graph_evidence_ids() -> None:
    """Allowed-list reader has the same pattern."""
    assert read_allowed_graph_evidence_ids(
        {"allowed_graph_evidence_ids": ["a", "b"]}
    ) == ["a", "b"]
    assert read_allowed_graph_evidence_ids({"allowed_fact_ids": ["a"]}) == ["a"]
    assert read_allowed_graph_evidence_ids({}) == []


def test_read_selected_graph_evidence_plan() -> None:
    """Plan reader returns the raw object (graph-era preferred)."""
    record = {"selected_graph_evidence_plan": {"k": "v"}}
    assert read_selected_graph_evidence_plan(record) == {"k": "v"}
    record2 = {"selected_fact_plan": {"k2": "v2"}}
    assert read_selected_graph_evidence_plan(record2) == {"k2": "v2"}
    assert read_selected_graph_evidence_plan({}) is None
