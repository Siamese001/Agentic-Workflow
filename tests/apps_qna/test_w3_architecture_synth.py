"""W3.3 tests — architecture content synthesis from ADG snapshot.

Strategy: build a minimal in-memory SQLite database that mimics the ADG
schema, write it to a tmp file, and exercise the synthesizers. This lets
the test suite run without depending on a real (~500 MB) ADG snapshot
being present in CI.

End-to-end test runs against the live snapshot when available and skips
gracefully otherwise.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from apps_qna.integrations.architecture_synth import (
    _empty_architecture_context,
    _has_table,
    _query_with_fallback,
    find_latest_snapshot,
    merge_architecture_into_extra_context,
    synthesize_architecture_blocks,
    synthesize_architecture_extra_context,
    synthesize_data_platform,
    synthesize_ds_to_platform,
    synthesize_global_engineering,
    synthesize_governance,
    synthesize_measurement,
    synthesize_productization,
    synthesize_semantic_grounding,
)


# --------------------------------------------------------------------------
# Fixture: synthetic ADG snapshot
# --------------------------------------------------------------------------


def _build_synthetic_snapshot(path: Path) -> None:
    """Write a minimal ADG-shaped SQLite snapshot for tests."""
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            resolved_path TEXT,
            layer TEXT
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            relation_type TEXT,
            source_file TEXT,
            dst_id INTEGER
        );
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY,
            severity_band TEXT
        );
        CREATE VIEW mv_graph_reverse_dependency_hotspots AS
            SELECT 'agentic_core/runtime/contracts/lifecycle.py' AS file_path,
                   'L_RUNTIME' AS layer,
                   1954 AS direct_inbound,
                   2.0 AS layer_criticality_weight
            UNION ALL SELECT 'agentic_core/L0_routing/config/path_constants.py',
                   'L0', 390, 2.0
            UNION ALL SELECT 'agentic_core/L2_execution/utils/write_gateway.py',
                   'L2', 81, 1.0;
        """
    )
    # Insert nodes covering each ADG layer + apps_*.
    nodes_data = [
        ("L0_routing.config", "agentic_core/L0_routing/config/path_constants.py", "L0"),
        ("L0_routing.bandit", "agentic_core/L0_routing/reasoning/namespace_bandit.py", "L0"),
        ("L1_cognition.retrieval", "agentic_core/L1_cognition/reasoning/retrieval_router.py", "L1"),
        ("L1_cognition.bge", "agentic_core/L1_cognition/reasoning/semantic_retriever.py", "L1"),
        ("L2_execution.uwg", "agentic_core/L2_execution/utils/write_gateway.py", "L2"),
        ("L2_execution.providers", "agentic_core/L2_execution/utils/providers.py", "L2"),
        ("L3_orchestration.healing", "agentic_core/L3_orchestration/healing.py", "L3"),
        ("L4_state.chroma", "agentic_core/L4_state/utils/client/chroma_client.py", "L4"),
        ("L5_safety.hitl", "agentic_core/L5_safety/runtime_gates/types.py", "L5"),
        ("L6_observability.promo", "agentic_core/L6_observability/promotion_gates.py", "L6"),
        ("L6_observability.regret", "agentic_core/L6_observability/regret_accounting.py", "L6"),
        ("embeddings.bge", "agentic_core/embeddings/bge_runtime.py", "L_SHARED"),
        ("ledgers.helpers", "tools/ledgers/hook_helpers.py", "L_TOOLS"),
        ("apps_qna.builder", "apps_qna/builder/card_pack_builder.py", "L_APP"),
        ("apps_qna.integrations", "apps_qna/integrations/spine_adapter.py", "L_APP"),
        ("apps_rg.engine", "apps_rg/engines/base_rg_engine.py", "L_APP"),
        ("apps_eval.engine", "apps_eval/engines/base_eval_engine.py", "L_APP"),
    ]
    for name, path_, layer in nodes_data:
        cur.execute(
            "INSERT INTO nodes (adg_name, resolved_path, layer) VALUES (?, ?, ?)",
            (name, path_, layer),
        )
    # Edges with semantic relation types
    edge_data = [
        ("imports", 100), ("imports", 100), ("imports", 100),
        ("flows_to", 25), ("flows_to", 25),
        ("writes_to", 12),
        ("emits_side_effect", 8),
        ("controls_flow", 5),
        ("reads_from", 30),
        ("resolves_callsite", 18),
    ]
    for rt, count in edge_data:
        for _ in range(count):
            cur.execute(
                "INSERT INTO edges (relation_type, source_file, dst_id) VALUES (?, ?, ?)",
                (rt, "test/file.py", 1),
            )
    # Violations across severity bands
    for band, n in [("P0", 3), ("P1", 8), ("P2", 14), ("P3", 22)]:
        for _ in range(n):
            cur.execute("INSERT INTO violations (severity_band) VALUES (?)", (band,))
    con.commit()
    con.close()


@pytest.fixture
def synthetic_snapshot(tmp_path: Path) -> Path:
    snap = tmp_path / "test_adg_indexed.sqlite"
    _build_synthetic_snapshot(snap)
    # Pad the file so it clears the _MIN_SNAPSHOT_BYTES check when we
    # later test find_latest_snapshot. SQLite VACUUM achieves nothing
    # here; instead we just append zeros to the file.
    with open(snap, "ab") as f:
        f.write(b"\x00" * (1_100_000 - snap.stat().st_size))
    return snap


# --------------------------------------------------------------------------
# Snapshot resolution
# --------------------------------------------------------------------------


def test_find_latest_snapshot_returns_largest_in_dir(tmp_path: Path) -> None:
    # Create three files: small (stub), medium, large.
    small = tmp_path / "adg_indexed_small.sqlite"
    medium = tmp_path / "adg_indexed_medium.sqlite"
    large = tmp_path / "adg_indexed_large.sqlite"
    small.write_bytes(b"\x00" * 1000)  # below _MIN_SNAPSHOT_BYTES
    medium.write_bytes(b"\x00" * 1_500_000)
    large.write_bytes(b"\x00" * 5_000_000)
    found = find_latest_snapshot(tmp_path)
    assert found == large


def test_find_latest_snapshot_returns_none_when_empty(tmp_path: Path) -> None:
    assert find_latest_snapshot(tmp_path) is None


def test_find_latest_snapshot_returns_none_when_dir_missing(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    assert find_latest_snapshot(missing) is None


# --------------------------------------------------------------------------
# Query helpers
# --------------------------------------------------------------------------


def test_query_with_fallback_returns_rows_on_success(synthetic_snapshot: Path) -> None:
    rows = _query_with_fallback(
        synthetic_snapshot,
        "SELECT COUNT(*) FROM nodes",
        fallback=[],
    )
    assert rows
    assert rows[0][0] > 0


def test_query_with_fallback_returns_fallback_on_error(synthetic_snapshot: Path) -> None:
    rows = _query_with_fallback(
        synthetic_snapshot,
        "SELECT * FROM nonexistent_table",
        fallback=[],
    )
    assert rows == []


def test_has_table_true_for_existing_table(synthetic_snapshot: Path) -> None:
    assert _has_table(synthetic_snapshot, "nodes")
    assert _has_table(synthetic_snapshot, "edges")
    assert _has_table(synthetic_snapshot, "mv_graph_reverse_dependency_hotspots")


def test_has_table_false_for_missing_table(synthetic_snapshot: Path) -> None:
    assert not _has_table(synthetic_snapshot, "definitely_not_a_table")


# --------------------------------------------------------------------------
# Per-slot synthesizers
# --------------------------------------------------------------------------


def test_synthesize_architecture_blocks_emits_layer_topology(synthetic_snapshot: Path) -> None:
    blocks = synthesize_architecture_blocks(synthetic_snapshot)
    headings = [b["heading"] for b in blocks]
    assert any("Layer topology" in h for h in headings)
    # Layer block should mention L0, L1, L2 etc.
    layer_block = next(b for b in blocks if "Layer topology" in b["heading"])
    bullets_text = "\n".join(layer_block["bullets"])
    assert "L0" in bullets_text or "L1" in bullets_text


def test_synthesize_architecture_blocks_emits_hotspots(synthetic_snapshot: Path) -> None:
    blocks = synthesize_architecture_blocks(synthetic_snapshot)
    headings = [b["heading"] for b in blocks]
    assert any("hotspot" in h.lower() for h in headings)


def test_synthesize_architecture_blocks_emits_semantic_edges(synthetic_snapshot: Path) -> None:
    blocks = synthesize_architecture_blocks(synthetic_snapshot)
    headings = [b["heading"] for b in blocks]
    assert any("Semantic edge" in h or "edge" in h.lower() for h in headings)


def test_synthesize_data_platform_returns_anchors_and_points(synthetic_snapshot: Path) -> None:
    anchors, points = synthesize_data_platform(synthetic_snapshot)
    # The synthetic snapshot has embeddings + L4 entries, so anchors must be non-empty.
    assert anchors
    assert points  # talking points fire when anchors exist


def test_synthesize_measurement_returns_anchors_and_points(synthetic_snapshot: Path) -> None:
    anchors, points = synthesize_measurement(synthetic_snapshot)
    assert anchors  # L6_observability + tools/ledgers entries present
    assert points


def test_synthesize_governance_returns_surfaces_and_points(synthetic_snapshot: Path) -> None:
    surfaces, points = synthesize_governance(synthetic_snapshot)
    # UWG anchor is hard-coded so surfaces is always populated.
    assert surfaces
    # P0/P1/P2/P3 violation summary must surface (we inserted those rows).
    band_text = "\n".join(surfaces)
    assert any(band in band_text for band in ("P0", "P1", "P2", "P3"))
    assert points


def test_synthesize_semantic_grounding_returns_points(synthetic_snapshot: Path) -> None:
    points = synthesize_semantic_grounding(synthetic_snapshot)
    assert points
    # Should mention semantic edge counts since we inserted them.
    text = "\n".join(points)
    assert "flows_to" in text or "writes_to" in text or "Semantic" in text


def test_synthesize_ds_to_platform_returns_anchors_and_points(synthetic_snapshot: Path) -> None:
    anchors, points = synthesize_ds_to_platform(synthetic_snapshot)
    # Lifecycle anchors are always present (hard-coded).
    assert anchors
    assert points


def test_synthesize_global_engineering_returns_anchors(synthetic_snapshot: Path) -> None:
    anchors, points = synthesize_global_engineering(synthetic_snapshot)
    # Synthetic snapshot has apps_qna, apps_rg, apps_eval entries.
    assert anchors
    text = "\n".join(anchors)
    assert "apps_" in text


def test_synthesize_productization_returns_points_and_kpis(synthetic_snapshot: Path) -> None:
    points, kpis = synthesize_productization(synthetic_snapshot)
    # Productization is hard-coded from resume facts.
    assert points
    assert kpis
    assert any("$22M" in k for k in kpis)


# --------------------------------------------------------------------------
# Top-level surface
# --------------------------------------------------------------------------


def test_synthesize_architecture_extra_context_returns_all_keys(synthetic_snapshot: Path) -> None:
    ctx = synthesize_architecture_extra_context(synthetic_snapshot)
    expected_keys = set(_empty_architecture_context().keys())
    assert set(ctx.keys()) == expected_keys


def test_synthesize_architecture_extra_context_handles_no_snapshot(tmp_path: Path) -> None:
    """When no ADG snapshot exists, every slot is empty."""
    missing = tmp_path / "no_such_file.sqlite"
    ctx = synthesize_architecture_extra_context(missing)
    expected_keys = set(_empty_architecture_context().keys())
    assert set(ctx.keys()) == expected_keys
    for value in ctx.values():
        assert value == [] or value == []


def test_merge_architecture_preserves_operator_curated_values(synthetic_snapshot: Path) -> None:
    """Operator-curated values must NOT be overwritten."""
    extra_context = {
        "architecture_content_blocks": [
            {"heading": "Operator's block", "bullets": ["custom bullet"]},
        ],
        "data_platform_anchors": ["operator anchor"],
        "data_platform_talking_points": [],  # empty -> synth fills
    }
    merged = merge_architecture_into_extra_context(
        extra_context, snapshot=synthetic_snapshot
    )
    # Operator value preserved.
    assert merged["architecture_content_blocks"][0]["heading"] == "Operator's block"
    assert merged["data_platform_anchors"] == ["operator anchor"]
    # Empty slot got synthesized content.
    assert merged["data_platform_talking_points"]


def test_merge_architecture_does_not_mutate_input(synthetic_snapshot: Path) -> None:
    extra_context = {"architecture_content_blocks": []}
    original_id = id(extra_context)
    merged = merge_architecture_into_extra_context(
        extra_context, snapshot=synthetic_snapshot
    )
    assert id(merged) != original_id
    # Input still has its original empty list.
    assert extra_context["architecture_content_blocks"] == []


# --------------------------------------------------------------------------
# End-to-end against the real ADG snapshot (skip gracefully if missing)
# --------------------------------------------------------------------------


def test_real_snapshot_synthesis_works_when_available() -> None:
    """Smoke test against the actual ADG snapshot if it exists in CI."""
    snapshot = find_latest_snapshot()
    if snapshot is None:
        return  # CI without an ADG snapshot — skip.
    ctx = synthesize_architecture_extra_context(snapshot)
    # On a real snapshot, at least architecture_content_blocks should
    # have data (every realistic ADG has a nodes table with layers).
    assert "architecture_content_blocks" in ctx
    # Productization KPIs are hard-coded from resume facts and always present.
    assert ctx["productization_kpi_anchors"]
    assert any("$22M" in k for k in ctx["productization_kpi_anchors"])
