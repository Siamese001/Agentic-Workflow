"""Integration tests for Seed Pack Full Build (Plan B Phase 5).

Full integration tests that call real OpenAI API when API key is available.
"""

from __future__ import annotations

import hashlib
import json
import os
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

_emit_authorize_and_execute("p2", "test_seed_pack_full_build_b5", "execution_auth")
_emit_validates_capability("p2", "test_seed_pack_full_build_b5", "capability_check")
_emit_routes_to_capability("p2", "test_seed_pack_full_build_b5", "capability_route")
_emit_writes_via_uwg("p2", "test_seed_pack_full_build_b5", "uwg_write")
_emit_blocks_direct_write("p2", "test_seed_pack_full_build_b5", "direct_write_block")
_emit_records_tool_invocation("p2", "test_seed_pack_full_build_b5", "tool_invocation")
_emit_captures_execution_output("p2", "test_seed_pack_full_build_b5", "exec_output")
_emit_dispatches_agent("p3", "test_seed_pack_full_build_b5", "agent_dispatch")
_emit_coordinates_agents("p3", "test_seed_pack_full_build_b5", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_seed_pack_full_build_b5", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_seed_pack_full_build_b5", "healing_outcome")
_emit_escalates_failure("p3", "test_seed_pack_full_build_b5", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_seed_pack_full_build_b5", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_seed_pack_full_build_b5", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_seed_pack_full_build_b5", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_seed_pack_full_build_b5", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_seed_pack_full_build_b5", "eval_metric")
_emit_stores_embedding("p4", "test_seed_pack_full_build_b5", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_seed_pack_full_build_b5", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_seed_pack_full_build_b5", "exec_snapshot_link")
from system_learning.engines.openai_embedder import OpenAIEmbedder
from system_learning.engines.seed_embedding_pack_builder import (
    DeterministicHashEmbedder,
    build_seed_embedding_pack,
)
from system_learning.types.seed_embedding_pack_types import (
    SeedEmbeddingPackConfig,
)

_emit_records_execution_trace("p0", "evidence", "test_seed_pack_full_build_b5")
_emit_applies_guardrail("p0", "test_seed_pack_full_build_b5", "p0_governance")
_emit_reads_policy_state("p0", "test_seed_pack_full_build_b5", "policy_binding")
_emit_snapshots_state("p0", "test_seed_pack_full_build_b5", "state_snapshot")
emit_replay_key("p0", "test_seed_pack_full_build_b5")
emit_determinism_digest("p0", "test_seed_pack_full_build_b5")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def has_openai_key() -> bool:
    """Check if OpenAI API key is available."""
    return bool(os.getenv("OPENAI_API_KEY"))


class TestSeedPackContractBuild:
    """Provider-agnostic contract tests for seed pack build structure.

    Uses DeterministicHashEmbedder — no external API dependency.
    Verifies the structural contract: files, hashes, sizing, and determinism.
    """

    def _make_corpus_rows(self, namespace: str, count: int) -> list[dict]:
        return [
            {
                "content_hash": hashlib.sha256(f"{namespace}_{i}".encode()).hexdigest(),
                "trace_id": f"trace_{i}",
                "namespace": namespace,
                "created_utc": 1_700_000_000 + i,
            }
            for i in range(count)
        ]

    @pytest.mark.integration_full_deps
    def test_contract_file_structure(self):
        """Build must produce seed_manifest.json, row_index.jsonl, embeddings.f32."""
        base_path = Path(tempfile.mkdtemp())
        try:
            embedder = DeterministicHashEmbedder(dimensions=64)
            config = SeedEmbeddingPackConfig(
                namespace="contract_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=3,
                embedding_model_version="deterministic-hash-v1",
            )
            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=self._make_corpus_rows("contract_ns", 3),
                embedder=embedder,
                built_at_utc=0,
            )
            pack_dir = base_path / "seed_packs" / "contract_ns" / manifest.seed_index_version_hash
            assert pack_dir.exists()
            for fname in ["seed_manifest.json", "row_index.jsonl", "embeddings.f32"]:
                assert (pack_dir / fname).exists(), f"Missing required file: {fname}"
        finally:
            shutil.rmtree(base_path)

    @pytest.mark.integration_full_deps
    def test_contract_hash_integrity(self):
        """Manifest hashes must match recomputed hashes of actual written files."""
        base_path = Path(tempfile.mkdtemp())
        try:
            embedder = DeterministicHashEmbedder(dimensions=64)
            config = SeedEmbeddingPackConfig(
                namespace="hash_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=2,
                embedding_model_version="deterministic-hash-v1",
            )
            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=self._make_corpus_rows("hash_ns", 2),
                embedder=embedder,
                built_at_utc=0,
            )
            pack_dir = base_path / "seed_packs" / "hash_ns" / manifest.seed_index_version_hash
            with open(pack_dir / "row_index.jsonl", "rb") as f:
                assert manifest.row_index_hash == hashlib.sha256(f.read()).hexdigest()
            with open(pack_dir / "embeddings.f32", "rb") as f:
                emb_bytes = f.read()
            assert manifest.matrix_hash == hashlib.sha256(emb_bytes).hexdigest()
            assert len(emb_bytes) == manifest.vector_count * 64 * 4  # 4 bytes per float32
        finally:
            shutil.rmtree(base_path)

    @pytest.mark.integration_full_deps
    def test_contract_seed_version_hash_determinism(self):
        """Same inputs to build must always produce identical seed_index_version_hash."""
        b1 = Path(tempfile.mkdtemp())
        b2 = Path(tempfile.mkdtemp())
        try:
            rows = self._make_corpus_rows("det_ns", 2)
            embedder = DeterministicHashEmbedder(dimensions=64)
            config = SeedEmbeddingPackConfig(
                namespace="det_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=2,
                embedding_model_version="deterministic-hash-v1",
            )
            m1 = build_seed_embedding_pack(
                base_path=b1, config=config, corpus_rows=rows, embedder=embedder, built_at_utc=0
            )
            m2 = build_seed_embedding_pack(
                base_path=b2, config=config, corpus_rows=rows, embedder=embedder, built_at_utc=0
            )
            assert m1.seed_index_version_hash == m2.seed_index_version_hash
        finally:
            shutil.rmtree(b1)
            shutil.rmtree(b2)


class TestSeedPackFullBuild:
    """Integration tests for full seed pack build with OpenAI."""

    @pytest.mark.integration_full_deps
    @pytest.mark.skipif(not has_openai_key(), reason="OPENAI_API_KEY not available")
    def test_build_small_pack_real_api(self):
        """Build pack from 3-5 corpus rows using real OpenAI API."""
        # Create temporary directory for build
        base_path = Path(tempfile.mkdtemp())

        try:
            # Create minimal corpus for testing
            corpus_rows = [
                {
                    "content_hash": hashlib.sha256(f"test_content_{i}".encode()).hexdigest(),
                    "trace_id": f"test_trace_{i}",
                    "namespace": "test_namespace",
                    "created_utc": 1234567890 + i,
                }
                for i in range(3)  # Use 3 rows for testing
            ]

            # Initialize OpenAI embedder
            embedder = OpenAIEmbedder(model="text-embedding-3-large")

            # Get model info
            model_info = embedder.get_model_info()
            dimensions = model_info["dimensions"]

            # Create config for full build
            config = SeedEmbeddingPackConfig(
                namespace="test_namespace",
                bootstrap_mode="full",
                embedding_model_version="text-embedding-3-large",
                embedding_model_checksum=embedder.get_model_checksum(),
                canonicalization_version="v1",
                dimensions=dimensions,
            )

            # Build seed pack
            builder = SeedEmbeddingPackBuilder()
            built_at_utc = 1234567890

            manifest = builder.build(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=built_at_utc,
            )

            # Validate manifest dimensions matches vector length
            assert manifest.dimensions == dimensions
            assert manifest.vector_count == len(corpus_rows)
            assert manifest.namespace == "test_namespace"
            assert manifest.bootstrap_mode == "full"
            assert manifest.embedding_model_version == "text-embedding-3-large"

            # Verify pack directory exists
            pack_dir = base_path / "seed_packs" / "test_namespace" / manifest.seed_index_version_hash
            assert pack_dir.exists()

            # Load and validate files
            manifest_path = pack_dir / "seed_manifest.json"
            row_index_path = pack_dir / "row_index.jsonl"
            embeddings_path = pack_dir / "embeddings.f32"

            assert all(p.exists() for p in [manifest_path, row_index_path, embeddings_path])

            # Recompute hashes to validate
            with open(row_index_path, "rb") as f:
                row_index_bytes = f.read()
            computed_row_index_hash = hashlib.sha256(row_index_bytes).hexdigest()

            with open(embeddings_path, "rb") as f:
                embeddings_bytes = f.read()
            computed_matrix_hash = hashlib.sha256(embeddings_bytes).hexdigest()

            # Validate hash matches
            assert manifest.row_index_hash == computed_row_index_hash
            assert manifest.matrix_hash == computed_matrix_hash

            # Validate seed_index_version_hash matches recompute
            # Load canonical manifest without hash fields
            with open(manifest_path, encoding="utf-8") as f:
                json.load(f)

            # Build canonical manifest for recomputation
            canonical_manifest = {
                "namespace": manifest.namespace,
                "bootstrap_mode": manifest.bootstrap_mode,
                "embedding_model_version": manifest.embedding_model_version,
                "embedding_model_checksum": manifest.embedding_model_checksum,
                "canonicalization_version": manifest.canonicalization_version,
                "dimensions": manifest.dimensions,
                "vector_count": manifest.vector_count,
            }
            canonical_bytes = json.dumps(canonical_manifest, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )

            # Recompute seed_index_version_hash
            recomputed_seed_hash = hashlib.sha256(
                computed_row_index_hash.encode() + computed_matrix_hash.encode() + canonical_bytes
            ).hexdigest()

            assert manifest.seed_index_version_hash == recomputed_seed_hash

            # Validate embeddings file size
            expected_size = len(corpus_rows) * dimensions * 4  # 4 bytes per float32
            assert len(embeddings_bytes) == expected_size

        finally:
            shutil.rmtree(base_path)

    @pytest.mark.integration_full_deps
    @pytest.mark.skipif(not has_openai_key(), reason="OPENAI_API_KEY not available")
    def test_openai_dimensions_from_api(self):
        """Verify dimensions come from API response, not hardcoded."""
        embedder = OpenAIEmbedder(model="text-embedding-3-large")
        model_info = embedder.get_model_info()

        # text-embedding-3-large should have 3072 dimensions
        assert model_info["dimensions"] == 3072
        assert model_info["model"] == "text-embedding-3-large"

    @pytest.mark.integration_full_deps
    @pytest.mark.skipif(not has_openai_key(), reason="OPENAI_API_KEY not available")
    def test_embed_batch_real_api(self):
        """Test embed_batch with real API call."""
        embedder = OpenAIEmbedder(model="text-embedding-3-large")

        texts = ["Hello world", "Test embedding", "OpenAI API test"]
        embeddings = embedder.embed_batch(texts)

        # Should return list of embeddings
        assert len(embeddings) == len(texts)

        # Each embedding should be a list of floats
        for embedding in embeddings:
            assert isinstance(embedding, list)
            assert len(embedding) == 3072  # text-embedding-3-large dimensions
            assert all(isinstance(x, float) for x in embedding)

        # Embeddings should be different for different texts
        assert embeddings[0] != embeddings[1]
        assert embeddings[1] != embeddings[2]

    @pytest.mark.integration_full_deps
    @pytest.mark.skipif(not has_openai_key(), reason="OPENAI_API_KEY not available")
    def test_newline_normalization_real_api(self):
        """Test newline normalization with real API."""
        embedder = OpenAIEmbedder(model="text-embedding-3-large")

        # Text with newlines
        text_with_newlines = "Line 1\nLine 2\r\nLine 3"
        text_with_spaces = "Line 1 Line 2 Line 3"

        embeddings = embedder.embed_batch([text_with_newlines, text_with_spaces])

        # Should produce same embeddings (newlines normalized to spaces)
        assert embeddings[0] == embeddings[1]

    @pytest.mark.integration_full_deps
    @pytest.mark.skipif(not has_openai_key(), reason="OPENAI_API_KEY not available")
    def test_model_checksum_consistency(self):
        """Model checksum should be consistent across instances."""
        checksum1 = OpenAIEmbedder().get_model_checksum()
        checksum2 = OpenAIEmbedder().get_model_checksum()

        assert checksum1 == checksum2
        assert len(checksum1) == 16
