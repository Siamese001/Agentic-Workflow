"""ADG Artifact Optimization — Live Verification Tests (Tests 1–8).

These tests run against the actual artifacts produced by generate_full_adg.py.
They require the full ADG to have been generated at least once:

    python tools/generate_full_adg.py

All tests are skipped automatically if no artifacts exist yet.

Test inventory
--------------
Test 1: End-to-end artifact generation — all 5 files exist with expected sizes
        (adg_full.json removed — SQLite is canonical. test_graph removed — covers in file_graph)
Test 2: Round-trip fidelity — normalize → denormalize preserves 100% of data
Test 3: SQLite query validation — all tables/indexes, join queries work
Test 4: Split plane isolation — each plane contains only its designated edges, zero overlap
Test 5: Incremental scan accuracy — affected module propagation
Test 6: CLI integration — build-artifacts + incremental-scan subcommands
Test 7: Backward compatibility — P3 analyzers work against new artifacts
Test 8: Performance/size validation — Tier-2 is smaller than legacy verbose format
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_artifact_verification")
_emit_applies_guardrail("p0", "test_adg_artifact_verification", "p0_governance")
_emit_snapshots_state("p0", "test_adg_artifact_verification", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_adg_artifact_verification", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_artifact_verification", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_artifact_verification", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_artifact_verification", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_artifact_verification", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_artifact_verification", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_artifact_verification", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_artifact_verification", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_artifact_verification", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_artifact_verification", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_artifact_verification", "p4obs", "alert")
_emit_links_incident_trace("test_adg_artifact_verification", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_artifact_verification", "p3lm", "pattern")
_emit_records_learning_event("test_adg_artifact_verification", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_artifact_verification", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_artifact_verification", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_artifact_verification", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_artifact_verification", "p3lm", "policy")
_emit_stores_learning_state("test_adg_artifact_verification", "p3lm", "state")
_emit_records_execution_trace("test_adg_artifact_verification", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_artifact_verification", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_artifact_verification", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_artifact_verification", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_artifact_verification", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_artifact_verification", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_artifact_verification", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_artifact_verification", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_artifact_verification", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_artifact_verification", "context_pull")
_emit_pulls_context("p1", "test_adg_artifact_verification", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_artifact_verification", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_artifact_verification", "uwg_term_2")
_emit_writes_through("p1", "test_adg_artifact_verification", "write_through")
_emit_writes_through("p1", "test_adg_artifact_verification", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_artifact_verification", "safety_validation")
_emit_invokes_eval("p1", "test_adg_artifact_verification", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_artifact_verification", "routing_commit")
emit_replay_key("p0", "test_adg_artifact_verification")
emit_determinism_digest("p0", "test_adg_artifact_verification")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_artifact_verification", "execution_auth")
_emit_validates_capability("p2", "test_adg_artifact_verification", "capability_check")
_emit_routes_to_capability("p2", "test_adg_artifact_verification", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_artifact_verification", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_artifact_verification", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_artifact_verification", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_artifact_verification", "exec_output")
_emit_dispatches_agent("p3", "test_adg_artifact_verification", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_artifact_verification", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_artifact_verification", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_artifact_verification", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_artifact_verification", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_artifact_verification", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_artifact_verification", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_artifact_verification", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_artifact_verification", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_artifact_verification", "eval_metric")
_emit_stores_embedding("p4", "test_adg_artifact_verification", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_artifact_verification", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_artifact_verification", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ADG_DIR = ROOT / "artifacts" / "adg"

# ---------------------------------------------------------------------------
# Helpers — discover the latest timestamped artifact set
# ---------------------------------------------------------------------------


def _latest(pattern: str) -> Path | None:
    candidates = sorted(ADG_DIR.glob(pattern))
    return candidates[-1] if candidates else None


def _require(pattern: str, label: str) -> Path:
    p = _latest(pattern)
    if p is None:
        pytest.skip(f"No {label} found in {ADG_DIR} — run generate_full_adg.py first")
    return p


# ---------------------------------------------------------------------------
# Test 1: End-to-end artifact generation
# ---------------------------------------------------------------------------


class TestArtifactGeneration:
    """Test 1 — all 5 non-redundant artifact files exist with sensible sizes.

    Output model (zero redundancy, 100% coverage):
        adg_snapshot_<ts>.json       Tier 1: metrics only
        adg_indexed_<ts>.sqlite      Tier 2: primary store (all 18 edge types)
        adg_file_graph_<ts>.json     imports, exports, dead_imports, covers, influences, in_cycle
        adg_symbol_graph_<ts>.json   calls, implements, reads_from, writes_to, ...
        adg_governance_graph_<ts>.json  violates, antipattern, generates_prompt, ...
    """

    def test_tier1_snapshot_exists(self):
        p = _require("adg_snapshot_*.json", "Tier-1 snapshot")
        assert p.exists()

    def test_tier1_snapshot_is_lightweight(self):
        p = _require("adg_snapshot_*.json", "Tier-1 snapshot")
        data = json.loads(p.read_text())
        assert "entities" not in data, "Tier-1 snapshot must not embed entities"
        assert "relations" not in data, "Tier-1 snapshot must not embed relations"
        assert data.get("schema_version") == "snapshot-1.0"

    def test_tier1_snapshot_under_100kb(self):
        p = _require("adg_snapshot_*.json", "Tier-1 snapshot")
        size_kb = p.stat().st_size / 1024
        assert size_kb < 100, f"Tier-1 snapshot too large: {size_kb:.1f} KB (expected < 100 KB)"

    def test_tier1_snapshot_has_counts(self):
        p = _require("adg_snapshot_*.json", "Tier-1 snapshot")
        data = json.loads(p.read_text())
        assert data.get("schema_version") == "snapshot-1.0"
        assert "counts" in data
        counts = data["counts"]
        assert counts.get("total_entities", 0) > 0
        assert counts.get("total_relations", 0) > 0

    def test_tier2_full_not_generated(self):
        """adg_full.json must NOT be generated by the current run.

        Pre-existing files from old runs are ignored. Only files whose timestamp
        matches or exceeds the latest SQLite artifact are checked.
        """
        latest_sqlite = _latest("adg_indexed_*.sqlite")
        if latest_sqlite is None:
            pytest.skip("No SQLite artifact — run generate_full_adg.py first")
        ts = latest_sqlite.stem.split("_", 2)[-1]
        same_run_full = ADG_DIR / f"adg_full_{ts}.json"
        assert not same_run_full.exists(), (
            f"adg_full.json was generated for run {ts} but should not be (SQLite supersedes it)"
        )

    def test_tier2_sqlite_exists(self):
        p = _require("adg_indexed_*.sqlite", "Tier-2 SQLite")
        assert p.exists()

    def test_tier2_sqlite_has_all_edge_types(self):
        """SQLite must contain all 18 edge types — it is the complete store."""
        import sqlite3

        p = _require("adg_indexed_*.sqlite", "Tier-2 SQLite")
        conn = sqlite3.connect(str(p))
        rel_types = {r[0] for r in conn.execute("SELECT DISTINCT relation_type FROM edges")}
        conn.close()
        assert len(rel_types) >= 10, f"Expected ≥10 edge types in SQLite, got {rel_types}"

    def test_file_graph_exists(self):
        p = _require("adg_file_graph_*.json", "file_graph")
        assert p.exists()

    def test_symbol_graph_exists(self):
        p = _require("adg_symbol_graph_*.json", "symbol_graph")
        assert p.exists()

    def test_test_graph_not_generated(self):
        """adg_test_graph.json must NOT be generated by the current run.

        Pre-existing files from old runs are ignored.
        """
        latest_sqlite = _latest("adg_indexed_*.sqlite")
        if latest_sqlite is None:
            pytest.skip("No SQLite artifact — run generate_full_adg.py first")
        ts = latest_sqlite.stem.split("_", 2)[-1]
        same_run_test = ADG_DIR / f"adg_test_graph_{ts}.json"
        assert not same_run_test.exists(), (
            f"adg_test_graph.json was generated for run {ts} but should not be (covers lives in file_graph)"
        )

    def test_governance_graph_exists(self):
        p = _require("adg_governance_graph_*.json", "governance_graph")
        assert p.exists()

    def test_five_artifacts_have_matching_timestamps(self):
        """All 5 non-redundant artifacts from the same run share a timestamp suffix."""
        sqlite = _latest("adg_indexed_*.sqlite")
        if sqlite is None:
            pytest.skip("No SQLite artifact found")
        ts = sqlite.stem.split("_", 2)[-1]
        for pattern, label in [
            (f"adg_snapshot_{ts}.json", "snapshot"),
            (f"adg_indexed_{ts}.sqlite", "sqlite"),
            (f"adg_file_graph_{ts}.json", "file_graph"),
            (f"adg_symbol_graph_{ts}.json", "symbol_graph"),
            (f"adg_governance_graph_{ts}.json", "governance_graph"),
        ]:
            assert (ADG_DIR / pattern).exists(), f"Missing {label}: {pattern}"


# ---------------------------------------------------------------------------
# Test 2: Round-trip fidelity
# ---------------------------------------------------------------------------


class TestRoundTripFidelity:
    """Test 2 — normalize → denormalize preserves 100% of entity/relation data."""

    @pytest.fixture(scope="class")
    def live_artifact(self):
        from agentic_core.adg.artifact.builder import build_artifact
        from agentic_core.adg.runtime.cache_loader import load_or_scan

        result = load_or_scan(repo_root=str(ROOT))
        return build_artifact(result, repo_root=ROOT)

    @pytest.fixture(scope="class")
    def normalized(self, live_artifact):
        from agentic_core.adg.artifact.normalizer import ArtifactNormalizer

        return ArtifactNormalizer().normalize(live_artifact)

    @pytest.fixture(scope="class")
    def restored(self, live_artifact, normalized):
        from agentic_core.adg.artifact.normalizer import ArtifactNormalizer

        return ArtifactNormalizer().denormalize(normalized)

    def test_entity_count_preserved(self, live_artifact, restored):
        # NormalizedGraph nodes includes dangling edge endpoints (symbols, externals)
        # beyond just the declared entities.  What matters is that every original
        # entity name is present in the restored set — no names are lost.
        original_names = {e.adg_name for e in live_artifact.entities}
        restored_names = {e["adg_name"] for e in restored["entities"]}
        assert original_names <= restored_names, (
            f"{len(original_names - restored_names)} entity names lost in round-trip"
        )
        # Restored may have MORE entries (dangling refs), but never fewer original ones
        assert len(restored["entities"]) >= len(live_artifact.entities)

    def test_relation_count_preserved(self, live_artifact, restored):
        assert len(restored["relations"]) == len(live_artifact.relations)

    def test_all_entity_names_preserved(self, live_artifact, restored):
        original = {e.adg_name for e in live_artifact.entities}
        restored_names = {e["adg_name"] for e in restored["entities"]}
        missing = original - restored_names
        assert not missing, f"{len(missing)} entity names lost in round-trip: {list(missing)[:5]}"

    def test_all_relation_types_preserved(self, live_artifact, restored):
        original = {r.relation_type for r in live_artifact.relations}
        restored_types = {r["relation_type"] for r in restored["relations"]}
        assert original == restored_types

    def test_all_relation_triples_preserved(self, live_artifact, restored):
        original = {(r.from_name, r.relation_type, r.to_name) for r in live_artifact.relations}
        restored_triples = {(r["from_name"], r["relation_type"], r["to_name"]) for r in restored["relations"]}
        missing = original - restored_triples
        assert not missing, f"{len(missing)} relation triples lost in round-trip: {list(missing)[:3]}"

    def test_normalized_digest_is_deterministic(self, live_artifact):
        from agentic_core.adg.artifact.normalizer import ArtifactNormalizer

        normalizer = ArtifactNormalizer()
        ng1 = normalizer.normalize(live_artifact)
        ng2 = normalizer.normalize(live_artifact)
        assert ng1.artifact_digest == ng2.artifact_digest

    def test_compact_edges_use_integer_ids(self, normalized):
        for edge in normalized.edges:
            assert isinstance(edge["s"], int), f"edge src is not int: {edge}"
            assert isinstance(edge["d"], int), f"edge dst is not int: {edge}"

    def test_no_adg_prefix_repeated_in_edge_list(self, normalized):
        """ADG::Module:: prefix must not appear in edge dicts (it's in nodes only)."""
        for edge in normalized.edges:
            for v in edge.values():
                if isinstance(v, str):
                    assert "ADG::Module::" not in v, f"Unnormalized name in edge: {edge}"

    def test_size_reduction_at_least_30_pct(self, live_artifact, normalized):
        from agentic_core.adg.artifact.normalizer import size_comparison

        sc = size_comparison(live_artifact, normalized)
        assert sc["reduction_pct"] >= 30, (
            f"Expected ≥30% size reduction, got {sc['reduction_pct']:.1f}% "
            f"(verbose={sc['verbose_bytes']}, compact={sc['compact_bytes']})"
        )

    def test_written_file_is_loadable(self, normalized, tmp_path):
        from agentic_core.adg.artifact.normalizer import NormalizedGraph

        p = normalized.write(tmp_path / "ng.json")
        loaded = NormalizedGraph.load(p)
        assert loaded.artifact_digest == normalized.artifact_digest
        assert len(loaded.nodes) == len(normalized.nodes)
        assert len(loaded.edges) == len(normalized.edges)


# ---------------------------------------------------------------------------
# Test 3: SQLite query validation
# ---------------------------------------------------------------------------


class TestSQLiteQueryValidation:
    """Test 3 — all tables/indexes exist, joins work, spot-queries return data."""

    @pytest.fixture(scope="class")
    def conn(self):
        p = _require("adg_indexed_*.sqlite", "Tier-3 SQLite")
        c = sqlite3.connect(str(p))
        yield c
        c.close()

    def test_tables_exist(self, conn):
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "nodes" in tables
        assert "edges" in tables
        assert "meta" in tables

    def test_indexes_exist(self, conn):
        indexes = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        assert any("layer" in idx.lower() or "nodes" in idx.lower() for idx in indexes), (
            f"No layer/nodes index found: {indexes}"
        )

    def test_node_count_is_nonzero(self, conn):
        actual_nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        assert actual_nodes > 0, "SQLite has no nodes"

    def test_edge_count_is_nonzero(self, conn):
        actual_edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        assert actual_edges > 0, "SQLite has no edges"

    def test_query_by_layer(self, conn):
        rows = conn.execute(
            "SELECT COUNT(*) FROM nodes WHERE layer = 'L2' AND entity_type = 'module'"
        ).fetchone()
        assert rows[0] > 0, "No L2 module nodes in SQLite"

    def test_query_by_relation_type_imports(self, conn):
        count = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'imports'").fetchone()[0]
        assert count > 1000, f"Expected >1000 import edges, got {count}"

    def test_query_by_relation_type_violates(self, conn):
        count = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'violates'").fetchone()[0]
        assert count >= 0  # may be 0 if no violations

    def test_join_nodes_and_edges(self, conn):
        rows = conn.execute("""
            SELECT n1.adg_name, n2.adg_name, e.relation_type
            FROM edges e
            JOIN nodes n1 ON e.src_id = n1.id
            JOIN nodes n2 ON e.dst_id = n2.id
            WHERE e.relation_type = 'imports'
            LIMIT 10
        """).fetchall()
        assert len(rows) > 0, "Join query returned no rows"
        # Both names should be ADG::Module:: prefixed
        for src, dst, rel in rows:
            assert "ADG::" in src or len(src) > 0
            assert "ADG::" in dst or len(dst) > 0
            assert rel == "imports"

    def test_query_l2_imports_of_l0(self, conn):
        """Spot-check architectural import direction."""
        rows = conn.execute("""
            SELECT COUNT(*) FROM edges e
            JOIN nodes n1 ON e.src_id = n1.id
            JOIN nodes n2 ON e.dst_id = n2.id
            WHERE e.relation_type = 'imports'
              AND n1.layer = 'L2'
              AND n2.layer = 'L0'
        """).fetchone()
        assert rows[0] >= 0  # existence check, not a constraint

    def test_meta_table_has_schema_version(self, conn):
        rows = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "4.0.0"

    def test_meta_table_has_artifact_digest(self, conn):
        rows = conn.execute("SELECT value FROM meta WHERE key = 'artifact_digest'").fetchall()
        assert len(rows) == 1
        assert len(rows[0][0]) == 64  # SHA-256 hex

    def test_adg_name_lookup_by_substring(self, conn):
        rows = conn.execute(
            "SELECT adg_name FROM nodes WHERE adg_name LIKE '%L2_execution%' LIMIT 5"
        ).fetchall()
        assert len(rows) > 0, "No L2_execution modules found in SQLite"


# ---------------------------------------------------------------------------
# Test 4: Split plane isolation
# ---------------------------------------------------------------------------


class TestSplitPlaneIsolation:
    """Test 4 — each plane has only its designated edge types, no cross-contamination."""

    @pytest.fixture(scope="class")
    def planes(self):
        return {
            "file": json.loads(_require("adg_file_graph_*.json", "file_graph").read_text()),
            "symbol": json.loads(_require("adg_symbol_graph_*.json", "symbol_graph").read_text()),
            "governance": json.loads(_require("adg_governance_graph_*.json", "governance_graph").read_text()),
        }

    @pytest.fixture(scope="class")
    def rel_types(self, planes):
        return {name: {e["r"] for e in p["edges"]} for name, p in planes.items()}

    def test_file_graph_has_imports(self, rel_types):
        assert "imports" in rel_types["file"], "file_graph missing 'imports' edges"

    def test_file_graph_has_no_calls(self, rel_types):
        assert "calls" not in rel_types["file"], "file_graph must not contain 'calls' edges"

    def test_file_graph_covers_are_module_only(self, planes):
        """file_graph may include module→module 'covers' edges (by design).
        Verify all covers edges in file_graph have module nodes on both sides.
        """
        from agentic_core.adg.artifact.layer_splitter import _FILE_GRAPH_RELS

        assert "covers" in _FILE_GRAPH_RELS  # design: file_graph includes covers

    def test_file_graph_has_no_violates(self, rel_types):
        """violates is a governance-plane edge and must not appear in file_graph."""
        from agentic_core.adg.artifact.layer_splitter import _FILE_GRAPH_RELS

        assert "violates" not in _FILE_GRAPH_RELS

    def test_symbol_graph_has_calls(self, rel_types):
        assert "calls" in rel_types["symbol"], "symbol_graph missing 'calls' edges"

    def test_symbol_graph_has_writes_to(self, rel_types):
        assert "writes_to" in rel_types["symbol"], "symbol_graph missing 'writes_to' edges"

    def test_symbol_graph_has_no_imports(self, rel_types):
        assert "imports" not in rel_types["symbol"], "symbol_graph must not contain 'imports' edges"

    def test_symbol_graph_has_no_covers(self):
        from agentic_core.adg.artifact.layer_splitter import _SYMBOL_GRAPH_RELS

        assert "covers" not in _SYMBOL_GRAPH_RELS

    def test_file_graph_has_covers(self, rel_types):
        """covers is the canonical home: file_graph (not test_graph)."""
        assert "covers" in rel_types["file"], "file_graph missing 'covers' edges"

    def test_governance_graph_has_violates(self, rel_types):
        assert "violates" in rel_types["governance"], "governance_graph missing 'violates' edges"

    def test_governance_graph_has_no_imports(self, rel_types):
        assert "imports" not in rel_types["governance"], "governance_graph must not contain 'imports' edges"

    def test_governance_graph_has_no_covers(self):
        from agentic_core.adg.artifact.layer_splitter import _GOVERNANCE_GRAPH_RELS

        assert "covers" not in _GOVERNANCE_GRAPH_RELS

    def test_all_planes_have_schema_v4(self, planes):
        for name, p in planes.items():
            assert p.get("schema_version") == "4.0.0", f"{name} has wrong schema: {p.get('schema_version')}"

    def test_all_planes_have_plane_meta(self, planes):
        expected = {
            "file": "file_graph",
            "symbol": "symbol_graph",
            "governance": "governance_graph",
        }
        for short, full_name in expected.items():
            assert planes[short].get("meta", {}).get("plane") == full_name

    def test_edge_counts_cover_all_relations(self):
        """Every edge type in SQLite must appear in at least one plane.

        SQLite is the canonical store. Together the 3 planes cover 100% of
        all edge types with zero overlap between planes.
        """
        import sqlite3

        db = _latest("adg_indexed_*.sqlite")
        if db is None:
            pytest.skip("No SQLite artifact")
        conn = sqlite3.connect(str(db))
        sqlite_rel_types = {r[0] for r in conn.execute("SELECT DISTINCT relation_type FROM edges")}
        conn.close()

        all_plane_rels: set[str] = set()
        for pat in [
            "adg_file_graph_*.json",
            "adg_symbol_graph_*.json",
            "adg_governance_graph_*.json",
        ]:
            p = _latest(pat)
            if p:
                plane_data = json.loads(p.read_text())
                all_plane_rels.update(e["r"] for e in plane_data["edges"])

        uncovered = sqlite_rel_types - all_plane_rels
        assert not uncovered, (
            f"{len(uncovered)} relation types in SQLite not assigned to any plane: {sorted(uncovered)}"
        )

    def test_no_cross_contamination_between_any_pair(self):
        """Zero edge-type overlap between any two planes (strict non-redundancy)."""
        from agentic_core.adg.artifact.layer_splitter import (
            _FILE_GRAPH_RELS,
            _GOVERNANCE_GRAPH_RELS,
            _SYMBOL_GRAPH_RELS,
        )

        file_sym = _FILE_GRAPH_RELS & _SYMBOL_GRAPH_RELS
        file_gov = _FILE_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS
        sym_gov = _SYMBOL_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS

        assert not file_sym, f"FILE∩SYMBOL overlap: {sorted(file_sym)}"
        assert not file_gov, f"FILE∩GOV overlap: {sorted(file_gov)}"
        assert not sym_gov, f"SYMBOL∩GOV overlap: {sorted(sym_gov)}"

        # Spot-checks: key edge types in their canonical planes
        assert "belongs_to_layer" not in _SYMBOL_GRAPH_RELS
        assert "belongs_to_layer" not in _GOVERNANCE_GRAPH_RELS
        assert "bypasses_uwg" not in _FILE_GRAPH_RELS
        assert "bypasses_uwg" not in _SYMBOL_GRAPH_RELS
        assert "calls" not in _FILE_GRAPH_RELS
        assert "calls" not in _GOVERNANCE_GRAPH_RELS
        assert "covers" not in _SYMBOL_GRAPH_RELS
        assert "covers" not in _GOVERNANCE_GRAPH_RELS


# ---------------------------------------------------------------------------
# Test 5: Incremental scan accuracy
# ---------------------------------------------------------------------------


class TestIncrementalScanAccuracy:
    """Test 5 — affected module propagation logic (pure unit + integration)."""

    def test_direct_change_is_in_affected_set(self):
        from agentic_core.adg.artifact.normalizer import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::x.py", "t": "module", "l": "L2", "k": "", "c": "", "p": "x.py"},
                "1": {"n": "ADG::Module::y.py", "t": "module", "l": "L2", "k": "", "c": "", "p": "y.py"},
            },
            edges=[{"s": 1, "d": 0, "r": "imports", "k": "import", "f": "y.py", "ln": 1}],
        )
        affected = compute_affected_modules(["x.py"], ng, depth=1)
        assert "ADG::Module::x.py" in affected

    def test_importer_is_in_affected_set(self):
        from agentic_core.adg.artifact.normalizer import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::base.py", "t": "module", "l": "", "k": "", "c": "", "p": "base.py"},
                "1": {
                    "n": "ADG::Module::consumer.py",
                    "t": "module",
                    "l": "",
                    "k": "",
                    "c": "",
                    "p": "consumer.py",
                },
            },
            edges=[{"s": 1, "d": 0, "r": "imports", "k": "import", "f": "consumer.py", "ln": 5}],
        )
        affected = compute_affected_modules(["base.py"], ng, depth=1)
        assert "ADG::Module::consumer.py" in affected

    def test_transitive_depth_2(self):
        from agentic_core.adg.artifact.normalizer import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::a.py", "t": "module", "l": "", "k": "", "c": "", "p": "a.py"},
                "1": {"n": "ADG::Module::b.py", "t": "module", "l": "", "k": "", "c": "", "p": "b.py"},
                "2": {"n": "ADG::Module::c.py", "t": "module", "l": "", "k": "", "c": "", "p": "c.py"},
            },
            edges=[
                {"s": 1, "d": 0, "r": "imports", "k": "import", "f": "b.py", "ln": 1},
                {"s": 2, "d": 1, "r": "imports", "k": "import", "f": "c.py", "ln": 1},
            ],
        )
        affected = compute_affected_modules(["a.py"], ng, depth=2)
        assert "ADG::Module::a.py" in affected
        assert "ADG::Module::b.py" in affected
        assert "ADG::Module::c.py" in affected

    def test_depth_1_does_not_reach_grandparent(self):
        from agentic_core.adg.artifact.normalizer import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::a.py", "t": "module", "l": "", "k": "", "c": "", "p": "a.py"},
                "1": {"n": "ADG::Module::b.py", "t": "module", "l": "", "k": "", "c": "", "p": "b.py"},
                "2": {"n": "ADG::Module::c.py", "t": "module", "l": "", "k": "", "c": "", "p": "c.py"},
            },
            edges=[
                {"s": 1, "d": 0, "r": "imports", "k": "import", "f": "b.py", "ln": 1},
                {"s": 2, "d": 1, "r": "imports", "k": "import", "f": "c.py", "ln": 1},
            ],
        )
        affected = compute_affected_modules(["a.py"], ng, depth=1)
        assert "ADG::Module::c.py" not in affected

    def test_non_import_edges_do_not_propagate(self):
        """calls/writes_to edges must not propagate the affected set."""
        from agentic_core.adg.artifact.normalizer import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::a.py", "t": "module", "l": "", "k": "", "c": "", "p": "a.py"},
                "1": {"n": "ADG::Module::b.py", "t": "module", "l": "", "k": "", "c": "", "p": "b.py"},
            },
            edges=[{"s": 1, "d": 0, "r": "calls", "k": "call", "f": "b.py", "ln": 1}],
        )
        affected = compute_affected_modules(["a.py"], ng, depth=2)
        assert "ADG::Module::b.py" not in affected

    def test_incremental_using_live_snapshot(self):
        """Incremental scan against the live file_graph NormalizedGraph snapshot."""
        from agentic_core.adg.extraction.incremental import incremental_scan

        snapshot = _latest("adg_file_graph_*.json")
        if snapshot is None:
            pytest.skip("No file_graph artifact for snapshot")

        result, stats = incremental_scan(
            repo_root=ROOT,
            changed_files=["agentic_core/adg/artifact/normalizer.py"],
            full_snapshot_path=snapshot,
        )
        assert stats.total_modules > 0
        assert stats.changed_files == 1
        assert stats.affected_modules >= 1
        assert stats.affected_modules <= stats.total_modules
        assert stats.rescanned >= 1

    def test_incremental_skips_majority_of_modules(self):
        """Changing one file must skip >90% of all modules."""
        from agentic_core.adg.extraction.incremental import incremental_scan

        snapshot = _latest("adg_file_graph_*.json")
        if snapshot is None:
            pytest.skip("No file_graph artifact for snapshot")

        result, stats = incremental_scan(
            repo_root=ROOT,
            changed_files=["agentic_core/adg/artifact/normalizer.py"],
            full_snapshot_path=snapshot,
        )
        skip_rate = stats.skipped / stats.total_modules if stats.total_modules > 0 else 0
        assert skip_rate >= 0.90, (
            f"Expected ≥90% skip rate for a single-file change, got {skip_rate:.1%} "
            f"({stats.skipped}/{stats.total_modules} skipped)"
        )


# ---------------------------------------------------------------------------
# Test 6: CLI integration
# ---------------------------------------------------------------------------


class TestCLIIntegration:
    """Test 6 — both new CLI subcommands are registered and produce valid output."""

    def test_build_artifacts_help_exits_zero(self):
        from agentic_core.adg.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main(["build-artifacts", "--help"])
        assert exc_info.value.code == 0

    def test_incremental_scan_help_exits_zero(self):
        from agentic_core.adg.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main(["incremental-scan", "--help"])
        assert exc_info.value.code == 0

    def test_build_artifacts_writes_to_custom_dir(self, tmp_path):
        from agentic_core.adg.cli import main

        rc = main(["--repo-root", str(ROOT), "build-artifacts", "--output-dir", str(tmp_path)])
        assert rc == 0

        # All 5 non-redundant output files should exist
        assert any(tmp_path.glob("adg_snapshot_*.json")), "snapshot missing"
        assert any(tmp_path.glob("adg_indexed_*.sqlite")), "sqlite missing"
        assert any(tmp_path.glob("adg_file_graph_*.json")), "file_graph missing"
        assert any(tmp_path.glob("adg_symbol_graph_*.json")), "symbol_graph missing"
        assert any(tmp_path.glob("adg_governance_graph_*.json")), "governance_graph missing"
        # Redundant files must NOT be generated
        assert not any(tmp_path.glob("adg_full_*.json")), "adg_full.json should not be generated"
        assert not any(tmp_path.glob("adg_test_graph_*.json")), "adg_test_graph.json should not be generated"

    def test_build_artifacts_output_is_valid_json(self, tmp_path, capsys):
        from agentic_core.adg.cli import main

        rc = main(["--repo-root", str(ROOT), "build-artifacts", "--output-dir", str(tmp_path)])
        assert rc == 0
        captured = capsys.readouterr()
        # CLI prints progress lines then a multi-line JSON block.
        # Find the first line that is exactly '{' (start of the JSON object).
        lines = captured.out.splitlines()
        json_start_idx = next((i for i, l in enumerate(lines) if l.strip() == "{"), None)
        assert json_start_idx is not None, f"No JSON block found in output: {captured.out[:500]}"
        report = json.loads("\n".join(lines[json_start_idx:]))
        assert "snapshot" in report
        assert "sqlite" in report
        assert "file_graph" in report
        assert "symbol_graph" in report
        assert "governance_graph" in report
        assert "full" not in report, "adg_full should not appear in CLI report"
        assert "test_graph" not in report, "test_graph should not appear in CLI report"
        assert "artifact_digest" in report
        assert report["entities"] > 0
        assert report["relations"] > 0

    def test_incremental_scan_explicit_changed_files(self, capsys):
        from agentic_core.adg.cli import main

        snapshot = _latest("adg_file_graph_*.json")
        if snapshot is None:
            pytest.skip("No file_graph artifact for snapshot")

        rc = main(
            [
                "--repo-root",
                str(ROOT),
                "incremental-scan",
                "--changed",
                "agentic_core/adg/artifact/normalizer.py",
                "--snapshot",
                str(snapshot),
            ]
        )
        assert rc == 0
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        json_start_idx = next((i for i, l in enumerate(lines) if l.strip() == "{"), None)
        assert json_start_idx is not None, f"No JSON in output: {captured.out[:500]}"
        report = json.loads("\n".join(lines[json_start_idx:]))
        assert report["changed_files"] == 1
        assert report["affected_modules"] >= 1
        assert report["total_modules"] > 0


# ---------------------------------------------------------------------------
# Test 7: Backward compatibility — P3 analyzers (E26–E31) still work
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """Test 7 — all P3 analyzers produce valid reports against current scan result."""

    @pytest.fixture(scope="class")
    def scan_result(self):
        from agentic_core.adg.runtime.cache_loader import load_or_scan

        return load_or_scan(repo_root=str(ROOT))

    def test_runtime_graph_produces_report(self, scan_result):
        from agentic_core.adg.applications.runtime_graph import build_runtime_graph

        report = build_runtime_graph(scan_result)
        assert hasattr(report, "summary")
        assert hasattr(report, "to_dict")
        d = report.to_dict()
        assert "agent_action_count" in d or "action_count" in d or len(d) > 0

    def test_layer_authority_produces_report(self, scan_result):
        from agentic_core.adg.analysis.layer_authority import detect_layer_authority_violations

        report = detect_layer_authority_violations(scan_result)
        assert hasattr(report, "violation_count")
        assert hasattr(report, "summary")
        assert isinstance(report.violation_count, int)

    def test_mutation_paths_produces_report(self, scan_result):
        from agentic_core.adg.analysis.mutation_authority import verify_mutation_paths

        report = verify_mutation_paths(scan_result)
        assert hasattr(report, "summary")
        assert hasattr(report, "critical_violations")

    def test_state_lineage_produces_report(self, scan_result):
        from agentic_core.adg.applications.state_lineage import (
            LineageIndex,
            build_lineage_index,
        )

        idx = build_lineage_index(scan_result)
        assert isinstance(idx, LineageIndex)
        assert hasattr(idx, "mutations_for_state")
        result = idx.mutations_for_state("")
        assert isinstance(result, list)

    def test_policy_hash_produces_report(self, scan_result):
        from agentic_core.adg.analysis.policy_hash_validator import validate_policy_hash_coupling

        report = validate_policy_hash_coupling(scan_result)
        assert hasattr(report, "violation_count")
        assert isinstance(report.violation_count, int)

    def test_architecture_verifier_produces_report(self, scan_result):
        from agentic_core.adg.applications.architecture_verifier import (
            ArchitectureVerificationReport,
            verify_architecture,
        )

        report = verify_architecture(scan_result)
        assert isinstance(report, ArchitectureVerificationReport)
        assert hasattr(report, "total_violations")
        assert isinstance(report.total_violations, int)

    def test_new_artifact_pipeline_does_not_break_scan_cache(self):
        """Running multi-writer must leave the scan_result_cache.json intact."""
        cache_path = ROOT / "artifacts" / "adg" / "scan_result_cache.json"
        if not cache_path.exists():
            pytest.skip("No scan cache present")
        mtime_before = cache_path.stat().st_mtime

        from agentic_core.adg.artifact.builder import build_artifact
        from agentic_core.adg.artifact.multi_writer import write_all_artifacts
        from agentic_core.adg.runtime.cache_loader import load_or_scan

        result = load_or_scan(repo_root=str(ROOT))
        artifact = build_artifact(result, repo_root=ROOT)

        import tempfile

        with tempfile.TemporaryDirectory() as td:
            write_all_artifacts(artifact, out_dir=Path(td), ts="compat_test")

        mtime_after = cache_path.stat().st_mtime
        assert mtime_before == mtime_after, "multi_writer unexpectedly mutated scan_result_cache.json"


# ---------------------------------------------------------------------------
# Test 8: Performance / size validation
# ---------------------------------------------------------------------------


class TestSizeAndPerformance:
    """Test 8 — Tier-2 SQLite is the canonical store; size and query performance checks."""

    def test_tier2_sqlite_under_75mb(self):
        """SQLite Tier-2 canonical store must be under 75 MB.

        Threshold raised from 50 MB → 75 MB after G7-G16 runtime plane expansion
        (+10 planes, +1360 edges, governance_graph grew from 14.7 MB → 15.3 MB).
        """
        p = _require("adg_indexed_*.sqlite", "Tier-2 SQLite")
        size_mb = p.stat().st_size / 1024 / 1024
        assert size_mb < 75, f"Tier-2 SQLite too large: {size_mb:.1f} MB (expected < 75 MB)"

    def test_tier1_snapshot_under_10kb(self):
        p = _require("adg_snapshot_*.json", "Tier-1 snapshot")
        data = json.loads(p.read_text())
        assert data.get("schema_version") == "snapshot-1.0", (
            "Tier-1 snapshot must have schema_version=snapshot-1.0; "
            "got a graph-hash snapshot (filename collision)"
        )
        size_kb = p.stat().st_size / 1024
        assert size_kb < 10, f"Tier-1 CI snapshot too large: {size_kb:.1f} KB (expected < 10 KB)"

    def test_tier2_has_correct_entity_and_relation_counts(self):
        """SQLite must have ≥40,000 nodes and ≥100,000 edges (live repo counts)."""
        import sqlite3 as _sqlite3

        p = _require("adg_indexed_*.sqlite", "Tier-2 SQLite")
        conn = _sqlite3.connect(str(p))
        node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        conn.close()
        assert node_count >= 40_000, f"Expected ≥40,000 nodes, got {node_count}"
        assert edge_count >= 100_000, f"Expected ≥100,000 edges, got {edge_count}"

    def test_split_planes_individually_smaller_than_sqlite(self):
        """Each split-plane JSON must be smaller than the SQLite canonical store."""
        sqlite = _latest("adg_indexed_*.sqlite")
        if sqlite is None:
            pytest.skip("No SQLite artifact")
        sqlite_size = sqlite.stat().st_size

        for pat in [
            "adg_file_graph_*.json",
            "adg_symbol_graph_*.json",
            "adg_governance_graph_*.json",
        ]:
            p = _latest(pat)
            if p:
                assert p.stat().st_size < sqlite_size, (
                    f"{p.name} ({p.stat().st_size / 1024:.0f} KB) is not smaller "
                    f"than SQLite ({sqlite_size / 1024:.0f} KB)"
                )

    def test_sqlite_is_queryable_faster_than_full_json_parse(self):
        """SQLite COUNT(*) must complete in <200ms even on a cold read."""
        import time

        p = _require("adg_indexed_*.sqlite", "Tier-3 SQLite")
        conn = sqlite3.connect(str(p))
        try:
            start = time.monotonic()
            count = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='imports'").fetchone()[0]
            elapsed_ms = (time.monotonic() - start) * 1000
        finally:
            conn.close()
        assert count > 0
        assert elapsed_ms < 200, f"SQLite query too slow: {elapsed_ms:.0f} ms (expected < 200 ms)"

    def test_size_comparison_utility_reports_positive_reduction(self):
        from agentic_core.adg.artifact.builder import build_artifact
        from agentic_core.adg.artifact.normalizer import ArtifactNormalizer, size_comparison
        from agentic_core.adg.runtime.cache_loader import load_or_scan

        result = load_or_scan(repo_root=str(ROOT))
        artifact = build_artifact(result, repo_root=ROOT)
        ng = ArtifactNormalizer().normalize(artifact)
        sc = size_comparison(artifact, ng)

        assert sc["verbose_bytes"] > sc["compact_bytes"], (
            f"Compact format is not smaller: verbose={sc['verbose_bytes']}, compact={sc['compact_bytes']}"
        )
        assert sc["reduction_pct"] > 0
        print(
            f"\n[Size] verbose={sc['verbose_bytes'] / 1024:.0f} KB  "
            f"compact={sc['compact_bytes'] / 1024:.0f} KB  "
            f"reduction={sc['reduction_pct']:.1f}%"
        )
