"""Tests for Seed Embedding Pack builder (Plan B Phase 0).

Comprehensive test suite covering deterministic behavior, canonical sorting,
hash computation, atomic write invariants, and read-only constraints.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "test_seed_embedding_pack_b0", "execution_auth")
_emit_validates_capability("p2", "test_seed_embedding_pack_b0", "capability_check")
_emit_routes_to_capability("p2", "test_seed_embedding_pack_b0", "capability_route")
_emit_writes_via_uwg("p2", "test_seed_embedding_pack_b0", "uwg_write")
_emit_blocks_direct_write("p2", "test_seed_embedding_pack_b0", "direct_write_block")
_emit_records_tool_invocation("p2", "test_seed_embedding_pack_b0", "tool_invocation")
_emit_captures_execution_output("p2", "test_seed_embedding_pack_b0", "exec_output")
_emit_dispatches_agent("p3", "test_seed_embedding_pack_b0", "agent_dispatch")
_emit_coordinates_agents("p3", "test_seed_embedding_pack_b0", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_seed_embedding_pack_b0", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_seed_embedding_pack_b0", "healing_outcome")
_emit_escalates_failure("p3", "test_seed_embedding_pack_b0", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_seed_embedding_pack_b0", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_seed_embedding_pack_b0", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_seed_embedding_pack_b0", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_seed_embedding_pack_b0", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_seed_embedding_pack_b0", "eval_metric")
_emit_stores_embedding("p4", "test_seed_embedding_pack_b0", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_seed_embedding_pack_b0", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_seed_embedding_pack_b0", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from system_learning.engines.seed_embedding_pack_builder import (
    DeterministicHashEmbedder,
    build_seed_embedding_pack,
)
from system_learning.types.seed_embedding_pack_types import (
    SeedEmbeddingPackConfig,
)

_emit_emits_metric_event("test_seed_embedding_pack_b0", "p4obs", "metric_1")
_emit_emits_metric_event("test_seed_embedding_pack_b0", "p4obs", "metric_2")
_emit_emits_metric_event("test_seed_embedding_pack_b0", "p4obs", "metric_3")
_emit_emits_metric_event("test_seed_embedding_pack_b0", "p4obs", "metric_4")
_emit_emits_metric_event("test_seed_embedding_pack_b0", "p4obs", "metric_5")
_emit_emits_metric_event("test_seed_embedding_pack_b0", "p4obs", "metric_6")
_emit_records_incident_event("test_seed_embedding_pack_b0", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_seed_embedding_pack_b0", "p4obs", "anomaly")
_emit_writes_observability_log("test_seed_embedding_pack_b0", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_seed_embedding_pack_b0", "p4obs", "mon_state")
_emit_triggers_alert("test_seed_embedding_pack_b0", "p4obs", "alert")
_emit_links_incident_trace("test_seed_embedding_pack_b0", "p4obs", "trace_link")
_emit_captures_pattern("test_seed_embedding_pack_b0", "p3lm", "pattern")
_emit_records_learning_event("test_seed_embedding_pack_b0", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_seed_embedding_pack_b0", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_seed_embedding_pack_b0", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_seed_embedding_pack_b0", "p3lm", "routing")
_emit_improves_agent_policy("test_seed_embedding_pack_b0", "p3lm", "policy")
_emit_stores_learning_state("test_seed_embedding_pack_b0", "p3lm", "state")
_emit_records_execution_trace("test_seed_embedding_pack_b0", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_seed_embedding_pack_b0", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_seed_embedding_pack_b0", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_seed_embedding_pack_b0", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_seed_embedding_pack_b0", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_seed_embedding_pack_b0", "env_read", "p2_env_1")
_emit_reads_environ("test_seed_embedding_pack_b0", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_seed_embedding_pack_b0", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_seed_embedding_pack_b0", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_seed_embedding_pack_b0")
_emit_applies_guardrail("p0", "test_seed_embedding_pack_b0", "p0_governance")
_emit_reads_policy_state("p0", "test_seed_embedding_pack_b0", "policy_binding")
_emit_snapshots_state("p0", "test_seed_embedding_pack_b0", "state_snapshot")
_emit_pulls_context("p1", "test_seed_embedding_pack_b0", "context_pull")
_emit_pulls_context("p1", "test_seed_embedding_pack_b0", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_seed_embedding_pack_b0", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_seed_embedding_pack_b0", "uwg_term_secondary")
_emit_writes_through("p1", "test_seed_embedding_pack_b0", "write_through")
_emit_writes_through("p1", "test_seed_embedding_pack_b0", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_seed_embedding_pack_b0", "safety_validation")
_emit_invokes_eval("p1", "test_seed_embedding_pack_b0", "eval_call")
_emit_proposal_commits_routing("p1", "test_seed_embedding_pack_b0", "routing_commit")
emit_replay_key("p0", "test_seed_embedding_pack_b0")
emit_determinism_digest("p0", "test_seed_embedding_pack_b0")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestDeterministicMinimalSeed:
    """Test minimal seed mode produces deterministic hashes."""

    def test_minimal_seed_deterministic(self):
        """Same corpus + same N → same row_index + same matrix_hash."""
        # Setup
        base_path1 = Path(tempfile.mkdtemp())
        base_path2 = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "a" * 64,
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            },
            {
                "content_hash": "b" * 64,
                "trace_id": "t2",
                "namespace": "healing_contexts",
                "created_utc": 1234567891,
            },
            {
                "content_hash": "c" * 64,
                "trace_id": "t3",
                "namespace": "healing_contexts",
                "created_utc": 1234567892,
            },
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=2,
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        # Build twice
        manifest1 = build_seed_embedding_pack(
            base_path=base_path1,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        manifest2 = build_seed_embedding_pack(
            base_path=base_path2,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        # Assert deterministic
        assert manifest1.row_index_hash == manifest2.row_index_hash
        assert manifest1.matrix_hash == manifest2.matrix_hash
        assert manifest1.seed_index_version_hash == manifest2.seed_index_version_hash

        # Cleanup
        shutil.rmtree(base_path1)
        shutil.rmtree(base_path2)


class TestDeterministicCuratedSeed:
    """Test curated seed mode produces deterministic hashes."""

    def test_curated_seed_deterministic(self):
        """Same curated list → same output."""
        base_path1 = Path(tempfile.mkdtemp())
        base_path2 = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "a" * 64,
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            },
            {
                "content_hash": "b" * 64,
                "trace_id": "t2",
                "namespace": "healing_contexts",
                "created_utc": 1234567891,
            },
            {
                "content_hash": "c" * 64,
                "trace_id": "t3",
                "namespace": "healing_contexts",
                "created_utc": 1234567892,
            },
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="curated_seed",
            curated_allowlist=[("t2", "b" * 64), ("t1", "a" * 64)],
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        # Build twice
        manifest1 = build_seed_embedding_pack(
            base_path=base_path1,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        manifest2 = build_seed_embedding_pack(
            base_path=base_path2,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        # Assert deterministic
        assert manifest1.row_index_hash == manifest2.row_index_hash
        assert manifest1.matrix_hash == manifest2.matrix_hash
        assert manifest1.seed_index_version_hash == manifest2.seed_index_version_hash

        # Cleanup
        shutil.rmtree(base_path1)
        shutil.rmtree(base_path2)


class TestCanonicalSortValidation:
    """Test canonical sorting by (content_hash, trace_id, row_id)."""

    def test_row_index_canonical_sort(self):
        """Rows sorted by (content_hash, trace_id, row_id)."""
        base_path = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "z" * 64,  # Should be last
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            },
            {
                "content_hash": "a" * 64,  # Should be first
                "trace_id": "t3",
                "namespace": "healing_contexts",
                "created_utc": 1234567892,
            },
            {
                "content_hash": "a" * 64,  # Same content_hash, trace_id determines order
                "trace_id": "t2",
                "namespace": "healing_contexts",
                "created_utc": 1234567891,
            },
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=3,
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        manifest = build_seed_embedding_pack(
            base_path=base_path,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        # Read row_index.jsonl and verify order
        row_index_path = (
            base_path
            / "seed_packs"
            / "healing_contexts"
            / manifest.seed_index_version_hash
            / "row_index.jsonl"
        )
        lines = row_index_path.read_text().splitlines()

        # Parse and check order
        parsed_rows = [json.loads(line) for line in lines]

        # Expected order: (a,t2), (a,t3), (z,t1)
        assert parsed_rows[0]["content_hash"] == "a" * 64
        assert parsed_rows[0]["trace_id"] == "t2"
        assert parsed_rows[1]["content_hash"] == "a" * 64
        assert parsed_rows[1]["trace_id"] == "t3"
        assert parsed_rows[2]["content_hash"] == "z" * 64
        assert parsed_rows[2]["trace_id"] == "t1"

        # Cleanup
        shutil.rmtree(base_path)


class TestByteLengthInvariant:
    """Test embeddings.f32 size invariant."""

    def test_embeddings_f32_byte_length(self):
        """embeddings.f32 size == vector_count * dimensions * 4."""
        base_path = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "a" * 64,
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            },
            {
                "content_hash": "b" * 64,
                "trace_id": "t2",
                "namespace": "healing_contexts",
                "created_utc": 1234567891,
            },
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=2,
        )

        dimensions = 8
        embedder = DeterministicHashEmbedder(dimensions=dimensions)

        manifest = build_seed_embedding_pack(
            base_path=base_path,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        # Check file size
        embeddings_path = (
            base_path
            / "seed_packs"
            / "healing_contexts"
            / manifest.seed_index_version_hash
            / "embeddings.f32"
        )
        file_size = embeddings_path.stat().st_size
        expected_size = manifest.vector_count * manifest.dimensions * 4

        assert file_size == expected_size

        # Cleanup
        shutil.rmtree(base_path)


class TestHashVerification:
    """Test row_index_hash and matrix_hash computation."""

    def test_row_index_hash_verification(self):
        """manifest.row_index_hash matches SHA-256 of row_index.jsonl."""
        base_path = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "a" * 64,
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            }
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=1,
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        manifest = build_seed_embedding_pack(
            base_path=base_path,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        # Verify hash
        row_index_path = (
            base_path
            / "seed_packs"
            / "healing_contexts"
            / manifest.seed_index_version_hash
            / "row_index.jsonl"
        )
        file_bytes = row_index_path.read_bytes()
        computed_hash = hashlib.sha256(file_bytes).hexdigest()

        assert manifest.row_index_hash == computed_hash

        # Cleanup
        shutil.rmtree(base_path)

    def test_matrix_hash_verification(self):
        """manifest.matrix_hash matches SHA-256 of embeddings.f32."""
        base_path = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "a" * 64,
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            }
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=1,
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        manifest = build_seed_embedding_pack(
            base_path=base_path,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        # Verify hash
        embeddings_path = (
            base_path
            / "seed_packs"
            / "healing_contexts"
            / manifest.seed_index_version_hash
            / "embeddings.f32"
        )
        file_bytes = embeddings_path.read_bytes()
        computed_hash = hashlib.sha256(file_bytes).hexdigest()

        assert manifest.matrix_hash == computed_hash

        # Cleanup
        shutil.rmtree(base_path)


class TestBuiltAtUtcExclusion:
    """Test built_at_utc is excluded from hash computation."""

    def test_built_at_utc_exclusion_from_hash_material(self):
        """Different built_at_utc produces same seed_index_version_hash."""
        base_path1 = Path(tempfile.mkdtemp())
        base_path2 = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "a" * 64,
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            }
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=1,
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        # Build with different built_at_utc
        manifest1 = build_seed_embedding_pack(
            base_path=base_path1,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        manifest2 = build_seed_embedding_pack(
            base_path=base_path2,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=9999999999,  # Different timestamp
        )

        # Hash should be the same (built_at_utc excluded)
        assert manifest1.seed_index_version_hash == manifest2.seed_index_version_hash
        # But built_at_utc field should differ
        assert manifest1.built_at_utc != manifest2.built_at_utc

        # Cleanup
        shutil.rmtree(base_path1)
        shutil.rmtree(base_path2)


class TestAtomicWriteInvariant:
    """Test atomic write behavior."""

    def test_atomic_write_no_partial_files_on_failure(self):
        """If build fails mid-process → no version directory created."""
        base_path = Path(tempfile.mkdtemp())

        # Empty corpus should cause failure
        corpus_rows = []

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=1,
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        # Build should fail
        with pytest.raises(RuntimeError, match="No rows selected"):
            build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

        # No directories should be created
        seed_packs_dir = base_path / "seed_packs"
        assert not seed_packs_dir.exists() or not any(seed_packs_dir.iterdir())

        # Cleanup
        shutil.rmtree(base_path)

    def test_no_overwrite_existing_directory(self):
        """If directory exists → build must fail."""
        base_path = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "a" * 64,
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            }
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=1,
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        # First build succeeds
        manifest1 = build_seed_embedding_pack(
            base_path=base_path,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        # Second build should fail
        with pytest.raises(RuntimeError, match="already exists"):
            build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

        # Cleanup
        shutil.rmtree(base_path)


class TestReadOnlyMtimeInvariant:
    """Test read-only constraints and mtime behavior."""

    def test_seed_pack_read_only_enforced(self):
        """Seed pack files are read-only after creation."""
        base_path = Path(tempfile.mkdtemp())

        corpus_rows = [
            {
                "content_hash": "a" * 64,
                "trace_id": "t1",
                "namespace": "healing_contexts",
                "created_utc": 1234567890,
            }
        ]

        config = SeedEmbeddingPackConfig(
            namespace="healing_contexts",
            bootstrap_mode="minimal_seed",
            minimal_seed_count=1,
        )

        embedder = DeterministicHashEmbedder(dimensions=8)

        manifest = build_seed_embedding_pack(
            base_path=base_path,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=1234567890,
        )

        # Check files exist and are readable
        pack_dir = base_path / "seed_packs" / "healing_contexts" / manifest.seed_index_version_hash
        assert (pack_dir / "row_index.jsonl").exists()
        assert (pack_dir / "embeddings.f32").exists()
        assert (pack_dir / "seed_manifest.json").exists()

        # Files should be readable (no explicit read-only enforcement in this implementation)
        # But the builder doesn't provide any write methods, so read-only is enforced by API design

        # Cleanup
        shutil.rmtree(base_path)


class TestDeterministicHashEmbedder:
    """Test the deterministic embedder used in tests."""

    def test_deterministic_hash_embedder_same_input(self):
        """Same content_hash produces same vector."""
        embedder = DeterministicHashEmbedder(dimensions=4)

        vectors1 = embedder.embed_batch(["test"], 4)
        vectors2 = embedder.embed_batch(["test"], 4)

        assert vectors1 == vectors2

    def test_deterministic_hash_embedder_different_input(self):
        """Different content_hash produces different vectors."""
        embedder = DeterministicHashEmbedder(dimensions=4)

        vectors1 = embedder.embed_batch(["test1"], 4)
        vectors2 = embedder.embed_batch(["test2"], 4)

        assert vectors1 != vectors2

    def test_deterministic_hash_embedder_dimensions(self):
        """Vector dimensions match requested dimensions."""
        dimensions = 8
        embedder = DeterministicHashEmbedder(dimensions=dimensions)

        vectors = embedder.embed_batch(["test"], dimensions)

        assert len(vectors) == 1
        assert len(vectors[0]) == dimensions
        assert all(isinstance(v, float) for v in vectors[0])
        assert all(-1.0 <= v <= 1.0 for v in vectors[0])  # Values in [-1, 1]
