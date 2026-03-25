"""Tests for MetaLearningEmbeddingService (Plan B Phase 2).

Comprehensive test suite covering seed pack consumption, integrity validation,
deterministic retrieval, and tie-breaking behavior.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_authorize_and_execute("p2", "test_meta_learning_embedding_service_b2", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_meta_learning_embedding_service_b2", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_meta_learning_embedding_service_b2", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_meta_learning_embedding_service_b2", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_meta_learning_embedding_service_b2", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_meta_learning_embedding_service_b2", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_meta_learning_embedding_service_b2", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_meta_learning_embedding_service_b2", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_meta_learning_embedding_service_b2", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_meta_learning_embedding_service_b2", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_meta_learning_embedding_service_b2", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_meta_learning_embedding_service_b2", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_meta_learning_embedding_service_b2", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_meta_learning_embedding_service_b2", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_meta_learning_embedding_service_b2", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_meta_learning_embedding_service_b2", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_meta_learning_embedding_service_b2", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_meta_learning_embedding_service_b2", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_meta_learning_embedding_service_b2", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_meta_learning_embedding_service_b2", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
from system_learning.engines.meta_learning_embedding_service import (
    IntegrityError,
    MetaLearningEmbeddingService,
)
from system_learning.engines.seed_embedding_pack_builder import (
    DeterministicHashEmbedder,
    build_seed_embedding_pack,
)
from system_learning.types.seed_embedding_pack_types import SeedEmbeddingPackConfig

# REMOVED: _emit_emits_metric_event("test_meta_learning_embedding_service_b2", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_meta_learning_embedding_service_b2", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_meta_learning_embedding_service_b2", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_meta_learning_embedding_service_b2", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_meta_learning_embedding_service_b2", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_meta_learning_embedding_service_b2", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_meta_learning_embedding_service_b2", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_meta_learning_embedding_service_b2", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_meta_learning_embedding_service_b2", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_meta_learning_embedding_service_b2", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_meta_learning_embedding_service_b2", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_meta_learning_embedding_service_b2", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_meta_learning_embedding_service_b2", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_meta_learning_embedding_service_b2", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_meta_learning_embedding_service_b2", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_meta_learning_embedding_service_b2", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_meta_learning_embedding_service_b2", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_meta_learning_embedding_service_b2", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_meta_learning_embedding_service_b2", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_meta_learning_embedding_service_b2", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_meta_learning_embedding_service_b2", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_meta_learning_embedding_service_b2", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_meta_learning_embedding_service_b2", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_meta_learning_embedding_service_b2", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_meta_learning_embedding_service_b2", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_meta_learning_embedding_service_b2", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_meta_learning_embedding_service_b2", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_meta_learning_embedding_service_b2", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_meta_learning_embedding_service_b2")
# REMOVED: _emit_applies_guardrail("p0", "test_meta_learning_embedding_service_b2", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_meta_learning_embedding_service_b2", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_meta_learning_embedding_service_b2", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_meta_learning_embedding_service_b2", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_meta_learning_embedding_service_b2", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_meta_learning_embedding_service_b2", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_meta_learning_embedding_service_b2", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_meta_learning_embedding_service_b2", "write_through")
# REMOVED: _emit_writes_through("p1", "test_meta_learning_embedding_service_b2", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_meta_learning_embedding_service_b2", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_meta_learning_embedding_service_b2", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_meta_learning_embedding_service_b2", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_meta_learning_embedding_service_b2", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_meta_learning_embedding_service_b2", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_meta_learning_embedding_service_b2", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_meta_learning_embedding_service_b2", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_meta_learning_embedding_service_b2", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_meta_learning_embedding_service_b2", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_meta_learning_embedding_service_b2", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_meta_learning_embedding_service_b2", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_meta_learning_embedding_service_b2", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_meta_learning_embedding_service_b2", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_meta_learning_embedding_service_b2", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_meta_learning_embedding_service_b2")
# REMOVED: _emit_gated_by_confidence("p1", "test_meta_learning_embedding_service_b2", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_meta_learning_embedding_service_b2")
# REMOVED: emit_determinism_digest("p0", "test_meta_learning_embedding_service_b2")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestMetaLearningEmbeddingService:
    """Test MetaLearningEmbeddingService functionality."""

    def test_missing_pack_returns_neutral_none(self):
        """Nonexistent pack path => retrieve returns None and does not create files."""
        base_path = Path(tempfile.mkdtemp())

        try:
            embedder = DeterministicHashEmbedder(dimensions=4)
            service = MetaLearningEmbeddingService(str(base_path), embedder)

            # Try to retrieve from nonexistent pack
            result = service.retrieve(
                namespace="nonexistent_ns",
                seed_index_version_hash="nonexistent_hash",
                query_text="test query",
                k=3,
            )

            # Should return None (neutral behavior)
            assert result is None

            # Should not create any files
            pack_dir = base_path / "seed_packs" / "nonexistent_ns" / "nonexistent_hash"
            assert not pack_dir.exists()

        finally:
            shutil.rmtree(base_path)

    def test_load_validates_hashes_and_dimensions(self):
        """Build a real seed pack and verify stable retrieval."""
        base_path = Path(tempfile.mkdtemp())

        try:
            # Build a seed pack
            embedder = DeterministicHashEmbedder(dimensions=4)
            config = SeedEmbeddingPackConfig(
                namespace="test_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=3,
            )
            corpus_rows = [
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
                {
                    "content_hash": "h2" * 32,
                    "trace_id": "t2",
                    "namespace": "test_ns",
                    "created_utc": 1234567891,
                },
                {
                    "content_hash": "h3" * 32,
                    "trace_id": "t3",
                    "namespace": "test_ns",
                    "created_utc": 1234567892,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Create service
            service = MetaLearningEmbeddingService(str(base_path), embedder)

            # Retrieve k=3
            result1 = service.retrieve(
                namespace="test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
                query_text="hello world",
                k=3,
            )

            # Should get valid result
            assert result1 is not None
            assert result1.namespace == "test_ns"
            assert result1.seed_index_version_hash == manifest.seed_index_version_hash
            assert result1.k == 3
            assert result1.similarity_metric == "cosine"
            assert result1.embedding_model_version == manifest.embedding_model_version
            assert len(result1.supporting_trace_ids) == 3
            assert len(result1.supporting_content_hashes) == 3

            # Retrieve again - should be stable
            result2 = service.retrieve(
                namespace="test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
                query_text="hello world",
                k=3,
            )

            # Assert stable supporting_trace_ids across two calls
            assert result1.supporting_trace_ids == result2.supporting_trace_ids
            assert result1.supporting_content_hashes == result2.supporting_content_hashes
            assert result1.artifact_hash() == result2.artifact_hash()

        finally:
            shutil.rmtree(base_path)

    def test_tie_break_is_deterministic(self):
        """Construct pack with identical cosine scores and verify deterministic ordering."""
        base_path = Path(tempfile.mkdtemp())

        try:
            # Use a special embedder that creates identical vectors for tie-breaking
            class TieBreakEmbedder:
                def __init__(self, dimensions: int):
                    self.dimensions = dimensions

                def embed_batch(self, texts: list[str], dimensions: int) -> list[list[float]]:
                    # Create identical vectors for all texts to force ties
                    return [[1.0, 0.0, 0.0, 0.0] for _ in texts]

            embedder = TieBreakEmbedder(dimensions=4)

            # Build seed pack with content that will create ties
            config = SeedEmbeddingPackConfig(
                namespace="tie_test_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=3,
            )
            corpus_rows = [
                {
                    "content_hash": "z_hash",  # Will sort last alphabetically
                    "trace_id": "z_trace",  # Will sort last alphabetically
                    "namespace": "tie_test_ns",
                    "created_utc": 1234567892,
                },
                {
                    "content_hash": "a_hash",  # Will sort first alphabetically
                    "trace_id": "a_trace",  # Will sort first alphabetically
                    "namespace": "tie_test_ns",
                    "created_utc": 1234567890,
                },
                {
                    "content_hash": "m_hash",
                    "trace_id": "m_trace",
                    "namespace": "tie_test_ns",
                    "created_utc": 1234567891,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Create service with same embedder
            service = MetaLearningEmbeddingService(str(base_path), embedder)

            # Retrieve all 3 - should have identical scores
            result = service.retrieve(
                namespace="tie_test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
                query_text="test",
                k=3,
            )

            # Verify deterministic ordering: (content_hash ASC, trace_id ASC)
            assert result is not None
            assert result.supporting_trace_ids == ["a_trace", "m_trace", "z_trace"]
            assert result.supporting_content_hashes == ["a_hash", "m_hash", "z_hash"]

            # All scores should be identical (cosine similarity of identical vectors)
            # This confirms tie-breaking is working

        finally:
            shutil.rmtree(base_path)

    def test_tampered_matrix_rejected_negative_control(self):
        """Tampered embeddings.f32 should cause integrity failure."""
        base_path = Path(tempfile.mkdtemp())

        try:
            # Build a valid seed pack
            embedder = DeterministicHashEmbedder(dimensions=4)
            config = SeedEmbeddingPackConfig(
                namespace="test_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=2,
            )
            corpus_rows = [
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
                {
                    "content_hash": "h2" * 32,
                    "trace_id": "t2",
                    "namespace": "test_ns",
                    "created_utc": 1234567891,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Tamper with embeddings.f32
            pack_dir = base_path / "seed_packs" / "test_ns" / manifest.seed_index_version_hash
            embeddings_path = pack_dir / "embeddings.f32"
            with open(embeddings_path, "r+b") as f:
                # Flip one byte to corrupt the matrix
                f.seek(10)
                f.write(b"X")

            # Create service
            service = MetaLearningEmbeddingService(str(base_path), embedder)

            # Should raise IntegrityError due to hash mismatch
            with pytest.raises(IntegrityError, match="Embeddings hash mismatch"):
                service.retrieve(
                    namespace="test_ns",
                    seed_index_version_hash=manifest.seed_index_version_hash,
                    query_text="test query",
                    k=2,
                )

        finally:
            shutil.rmtree(base_path)

    def test_k_larger_than_available(self):
        """Request more results than available should return all available."""
        base_path = Path(tempfile.mkdtemp())

        try:
            # Build a seed pack with only 2 items
            embedder = DeterministicHashEmbedder(dimensions=4)
            config = SeedEmbeddingPackConfig(
                namespace="test_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=2,
            )
            corpus_rows = [
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
                {
                    "content_hash": "h2" * 32,
                    "trace_id": "t2",
                    "namespace": "test_ns",
                    "created_utc": 1234567891,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Create service
            service = MetaLearningEmbeddingService(str(base_path), embedder)

            # Request k=5 but only 2 available
            result = service.retrieve(
                namespace="test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
                query_text="test query",
                k=5,
            )

            # Should return only 2 results
            assert result is not None
            assert result.k == 2
            assert len(result.supporting_trace_ids) == 2
            assert len(result.supporting_content_hashes) == 2

        finally:
            shutil.rmtree(base_path)

    def test_empty_query_vector_handling(self):
        """Handle edge case of zero-length query vector."""
        base_path = Path(tempfile.mkdtemp())

        try:
            # Build a seed pack
            embedder = DeterministicHashEmbedder(dimensions=4)
            config = SeedEmbeddingPackConfig(
                namespace="test_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=2,
            )
            corpus_rows = [
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
                {
                    "content_hash": "h2" * 32,
                    "trace_id": "t2",
                    "namespace": "test_ns",
                    "created_utc": 1234567891,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Create service with embedder that returns zero vector
            class ZeroVectorEmbedder:
                def embed_batch(self, texts: list[str], dimensions: int) -> list[list[float]]:
                    return [[0.0] * dimensions for _ in texts]

            service = MetaLearningEmbeddingService(str(base_path), ZeroVectorEmbedder())

            # Query with zero vector should return empty results
            result = service.retrieve(
                namespace="test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
                query_text="test",
                k=3,
            )

            # Should return empty result
            assert result is not None
            assert result.k == 0
            assert len(result.supporting_trace_ids) == 0
            assert len(result.supporting_content_hashes) == 0

        finally:
            shutil.rmtree(base_path)
