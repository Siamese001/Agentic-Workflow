"""Tests for tools/otel/exercise_real_otel_pipeline.py.

Closes the final deferred item from plan three-bucket-gap-remediation-069806:
real OTel emitter trace flow. Verifies the production-path exerciser:

  * Calls real W3-migrated emitter APIs (heal_router_otel, consensus_otel,
    runtime_span_emitter) and routes their spans through
    emit_spans_to_runtime_adg.
  * Constructs ADG-aligned spans (Phase 2) whose endpoints match
    consumer-edge tuples in the static snapshot, so the runtime view
    builder resolves them to TRIPLET_ATTESTED rows.
  * Reports per-emitter success and gen_ai semconv attribute presence.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.otel.exercise_real_otel_pipeline import (  # noqa: E402
    EmitterStats,
    ExerciseStats,
    _has_gen_ai_attrs,
    emit_consumer_edge_aligned_spans,
    exercise_consensus_otel,
    exercise_heal_router_otel,
    exercise_runtime_span_emitter,
)


# ---------------------------------------------------------------------------
# Fixture — synthetic snapshot with consumer-edge twin pairs
# ---------------------------------------------------------------------------


def _build_snapshot_with_consumer_edges(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            authority TEXT NOT NULL,
            bucket TEXT NOT NULL,
            resolution_status TEXT NOT NULL,
            authority_status TEXT NOT NULL,
            evidence_refs TEXT
        );
        """
    )
    # 4 nodes with module / registry-anchor adg_names mirroring the real
    # consumer-edge twin pattern.
    con.execute(
        "INSERT INTO nodes (adg_name) VALUES "
        "('ADG::Module::apps_lic/agents/profile.py')"
    )
    con.execute(
        "INSERT INTO nodes (adg_name) VALUES "
        "('Registry::Agent::apps_lic::profile_analysis_agent')"
    )
    con.execute("INSERT INTO nodes (adg_name) VALUES ('ADG::Module::other.py')")
    con.execute("INSERT INTO nodes (adg_name) VALUES ('Registry::MCP::tavily')")

    # Consumer-edge twin: bucket='static' + bucket='registry' on same triple.
    # Both twins carry authority='verified' (in-enum) post-W7-remediation.
    rows = [
        (1, 2, "references_agent_spec", "verified", "static"),
        (1, 2, "references_agent_spec", "verified", "registry"),
        (3, 4, "references_mcp_server", "verified", "static"),
        (3, 4, "references_mcp_server", "verified", "registry"),
    ]
    for src, dst, rel, auth, bucket in rows:
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, authority, "
            "bucket, resolution_status, authority_status) "
            "VALUES (?, ?, ?, ?, ?, 'V', 'A')",
            (src, dst, rel, auth, bucket),
        )
    con.commit()
    con.close()


@pytest.fixture
def consumer_snapshot(tmp_path: Path) -> Path:
    snap = tmp_path / "consumer.sqlite"
    _build_snapshot_with_consumer_edges(snap)
    return snap


# ---------------------------------------------------------------------------
# gen_ai attribute helper
# ---------------------------------------------------------------------------


class TestHasGenAiAttrs:
    def test_dict_attrs_with_gen_ai_key(self):
        span = {"attributes": {"gen_ai.operation.name": "invoke_agent"}}
        assert _has_gen_ai_attrs(span) is True

    def test_dict_attrs_without_gen_ai_key(self):
        span = {"attributes": {"app_name": "x", "tier": "HIGH"}}
        assert _has_gen_ai_attrs(span) is False

    def test_json_string_attrs(self):
        span = {"attributes": json.dumps({"gen_ai.operation.name": "invoke_workflow"})}
        assert _has_gen_ai_attrs(span) is True

    def test_invalid_json_attrs(self):
        span = {"attributes": "not json {"}
        assert _has_gen_ai_attrs(span) is False

    def test_empty_attrs(self):
        span = {"attributes": {}}
        assert _has_gen_ai_attrs(span) is False

    def test_no_attrs_key(self):
        span = {}
        assert _has_gen_ai_attrs(span) is False


# ---------------------------------------------------------------------------
# Phase 1 — real W3 emitter exercise
# ---------------------------------------------------------------------------


class TestExerciseHealRouterOtel:
    def test_succeeds_with_default_n(self):
        stats = exercise_heal_router_otel(n=2)
        assert isinstance(stats, EmitterStats)
        assert stats.name == "heal_router_otel"
        assert stats.error is None
        assert stats.invocations == 2
        assert stats.spans_persisted == 2

    def test_zero_n_skips_emission(self):
        stats = exercise_heal_router_otel(n=0)
        assert stats.invocations == 0
        assert stats.spans_persisted == 0
        assert stats.error is None


class TestExerciseConsensusOtel:
    def test_succeeds_with_default_n(self):
        stats = exercise_consensus_otel(n=2)
        assert stats.name == "consensus_otel"
        assert stats.error is None
        assert stats.invocations == 2

    def test_zero_n_skips_emission(self):
        stats = exercise_consensus_otel(n=0)
        assert stats.invocations == 0
        assert stats.error is None


class TestExerciseRuntimeSpanEmitter:
    def test_succeeds_with_default_n(self):
        stats = exercise_runtime_span_emitter(n=2)
        assert stats.name == "runtime_span_emitter"
        assert stats.error is None
        assert stats.invocations == 2
        # Each invocation produces multiple spans (trace_root + step_seal +
        # exit_disposition) → spans_persisted should exceed invocations.
        assert stats.spans_persisted >= stats.invocations

    def test_module_level_gen_ai_discriminator_is_present(self):
        """W3 deliverable check — module-level _GEN_AI_OPERATION exists."""
        import agentic_core.L6_system_learning.runtime_adg.runtime_span_emitter as mod

        assert hasattr(mod, "_GEN_AI_OPERATION")
        assert mod._GEN_AI_OPERATION  # non-empty


# ---------------------------------------------------------------------------
# Phase 2 — Consumer-edge aligned span emission
# ---------------------------------------------------------------------------


class TestEmitConsumerEdgeAlignedSpans:
    def test_emits_spans_for_consumer_tuples(self, consumer_snapshot: Path):
        emitted, persisted, gen_ai = emit_consumer_edge_aligned_spans(
            consumer_snapshot, n_traces=3, edges_per_trace=2
        )
        # 3 traces × 2 edges/trace × 2 spans/edge (src + dst) = 12 spans
        assert emitted == 12
        assert persisted == 3
        assert gen_ai is True

    def test_returns_zero_when_no_consumer_edges(self, tmp_path: Path):
        # Snapshot with NO registry rows -> no consumer-edge tuples.
        snap = tmp_path / "empty.sqlite"
        con = sqlite3.connect(snap)
        con.executescript(
            """
            CREATE TABLE nodes (id INTEGER PRIMARY KEY AUTOINCREMENT, adg_name TEXT NOT NULL);
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_id INTEGER NOT NULL, dst_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL, edge_kind TEXT, source_file TEXT,
                line_no INTEGER, symbol TEXT,
                authority TEXT NOT NULL, bucket TEXT NOT NULL,
                resolution_status TEXT NOT NULL, authority_status TEXT NOT NULL,
                evidence_refs TEXT
            );
            """
        )
        con.execute("INSERT INTO nodes (adg_name) VALUES ('ADG::a')")
        con.execute("INSERT INTO nodes (adg_name) VALUES ('ADG::b')")
        con.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, authority, "
            "bucket, resolution_status, authority_status) "
            "VALUES (1, 2, 'imports', 'verified', 'static', 'V', 'A')"
        )
        con.commit()
        con.close()
        emitted, persisted, gen_ai = emit_consumer_edge_aligned_spans(
            snap, n_traces=5, edges_per_trace=4
        )
        assert emitted == 0
        assert persisted == 0
        assert gen_ai is False

    def test_emitted_spans_have_gen_ai_operation_name(self, consumer_snapshot: Path):
        # Only verify that the function returns gen_ai_attr_present=True
        # when consumer edges exist. The actual span dicts are interior,
        # but the test in test_has_gen_ai_attrs covers the detector.
        _, _, gen_ai = emit_consumer_edge_aligned_spans(
            consumer_snapshot, n_traces=1, edges_per_trace=1
        )
        assert gen_ai is True


# ---------------------------------------------------------------------------
# ExerciseStats success rollup
# ---------------------------------------------------------------------------


class TestExerciseStats:
    def test_all_emitters_succeeded_when_no_results(self):
        # Empty result list => trivially all-succeeded (vacuous truth).
        stats = ExerciseStats()
        assert stats.all_emitters_succeeded() is True

    def test_all_emitters_succeeded_when_clean(self):
        stats = ExerciseStats(
            emitter_results=[
                EmitterStats(name="x", invocations=3, spans_persisted=3, error=None),
                EmitterStats(name="y", invocations=2, spans_persisted=4, error=None),
            ]
        )
        assert stats.all_emitters_succeeded() is True

    def test_any_emitter_error_marks_failure(self):
        stats = ExerciseStats(
            emitter_results=[
                EmitterStats(name="x", invocations=3, error=None),
                EmitterStats(name="y", invocations=0, error="ImportError: foo"),
            ]
        )
        assert stats.all_emitters_succeeded() is False

    def test_zero_invocations_marks_failure(self):
        stats = ExerciseStats(
            emitter_results=[
                EmitterStats(name="x", invocations=0, error=None),
            ]
        )
        assert stats.all_emitters_succeeded() is False
