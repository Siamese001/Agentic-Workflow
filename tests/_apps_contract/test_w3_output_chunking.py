"""Tests for apps_rg output chunking and lineage (W3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.chunking.resume_chunker import ResumeChunker, ResumeChunk


class TestResumeChunk:
    """Test ResumeChunk dataclass."""

    def test_chunk_creation(self):
        """Chunk can be created with all fields."""
        chunk = ResumeChunk(
            chunk_id="chunk_123",
            artifact_id="art_456",
            section_type="experience",
            content="Worked at Acme",
            content_hash="abc123",
            source_run_id="run_789",
            source_request_id="req_abc",
            source_input_intent_hash="intent_def",
            target_job_metadata={"company": "Acme", "role": "Engineer"},
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
            freshness_status="fresh",
            generated_at="2026-01-01T00:00:00Z",
            tenant_id="default",
            user_scope="anonymous",
            lineage_refs=["parent_1"],
            replay_refs=[],
            exit_disposition_ref="exit_ok",
            uwg_commit_receipt="receipt_123",
        )

        assert chunk.chunk_id == "chunk_123"
        assert chunk.section_type == "experience"

    def test_chunk_to_dict(self):
        """Chunk can be serialized to dict."""
        chunk = ResumeChunk(
            chunk_id="chunk_123",
            artifact_id="art_456",
            section_type="summary",
            content="Experienced engineer",
            content_hash="hash789",
            source_run_id="run_001",
            source_request_id="req_001",
            source_input_intent_hash="intent_001",
            target_job_metadata={"company": "Acme"},
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
            freshness_status="fresh",
            generated_at="2026-01-01T00:00:00Z",
            tenant_id="default",
            user_scope="user_123",
            lineage_refs=[],
            replay_refs=[],
            exit_disposition_ref="exit_ok",
            uwg_commit_receipt="receipt_001",
        )

        data = chunk.to_dict()

        assert data["chunk_id"] == "chunk_123"
        assert data["section_type"] == "summary"
        assert "lineage" in data
        assert data["lineage"]["source_input_intent_hash"] == "intent_001"

    def test_chunk_frozen(self):
        """Chunk is immutable."""
        chunk = ResumeChunk(
            chunk_id="chunk_123",
            artifact_id="art_456",
            section_type="header",
            content="John Doe",
            content_hash="hash",
            source_run_id="run_1",
            source_request_id="req_1",
            source_input_intent_hash="intent_1",
            target_job_metadata={},
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
            freshness_status="fresh",
            generated_at="2026-01-01T00:00:00Z",
            tenant_id="default",
            user_scope="user",
            lineage_refs=[],
            replay_refs=[],
            exit_disposition_ref="exit",
            uwg_commit_receipt="receipt",
        )

        with pytest.raises(AttributeError):
            chunk.content = "New content"


class TestResumeChunker:
    """Test resume chunking logic."""

    def test_chunker_creation(self):
        """Chunker can be created."""
        chunker = ResumeChunker()
        assert chunker is not None

    def test_chunks_include_all_sections(self):
        """All resume sections are chunked."""
        chunker = ResumeChunker()

        resume = {
            "header": "John Doe",
            "summary": "Experienced engineer",
            "experience": ["Job 1", "Job 2"],
            "skills": ["Python", "ML"],
        }

        run_context = {
            "run_id": "run_123",
            "policy_hash": "policy_v1",
            "blueprint_hash": "blueprint_v1",
        }

        chunks = chunker.chunk_resume(resume, run_context, "intent_hash_abc")

        section_types = {c.section_type for c in chunks}
        assert "header" in section_types
        assert "summary" in section_types
        assert "experience" in section_types
        assert "skills" in section_types

    def test_chunk_includes_intent_hash_lineage(self):
        """Each chunk links to source input intent hash."""
        chunker = ResumeChunker()

        resume = {"header": "John Doe"}
        run_context = {"run_id": "run_123"}
        intent_hash = "hash_abc_123"

        chunks = chunker.chunk_resume(resume, run_context, intent_hash)

        assert len(chunks) == 1
        assert chunks[0].source_input_intent_hash == intent_hash

    def test_chunk_content_hash_for_integrity(self):
        """Each chunk has content hash for integrity verification."""
        chunker = ResumeChunker()

        resume = {"header": "John Doe"}
        chunks = chunker.chunk_resume(resume, {"run_id": "run_123"}, "hash")

        assert chunks[0].content_hash is not None
        assert len(chunks[0].content_hash) == 32  # SHA-256 truncated

    def test_chunk_request_id_lineage(self):
        """Chunk includes request ID for lineage."""
        chunker = ResumeChunker()

        resume = {"summary": "Engineer"}
        run_context = {
            "run_id": "run_456",
            "request_id": "req_xyz",
        }

        chunks = chunker.chunk_resume(resume, run_context, "intent_hash")

        assert chunks[0].source_request_id == "req_xyz"

    def test_chunk_target_job_metadata(self):
        """Chunk includes target job metadata."""
        chunker = ResumeChunker()

        resume = {"experience": ["Job at Acme"]}
        run_context = {
            "run_id": "run_789",
            "target_job": {"company": "Acme", "role": "Engineer"},
        }

        chunks = chunker.chunk_resume(resume, run_context, "intent_hash")

        assert chunks[0].target_job_metadata["company"] == "Acme"

    def test_chunk_policy_blueprint_hashes(self):
        """Chunk includes policy and blueprint hashes."""
        chunker = ResumeChunker()

        resume = {"education": "BS in CS"}
        run_context = {
            "run_id": "run_001",
            "policy_hash": "policy_v2",
            "blueprint_hash": "blueprint_v3",
        }

        chunks = chunker.chunk_resume(resume, run_context, "intent_hash")

        assert chunks[0].policy_hash == "policy_v2"
        assert chunks[0].blueprint_hash == "blueprint_v3"

    def test_chunk_freshness_status(self):
        """Chunk is marked as fresh when created."""
        chunker = ResumeChunker()

        resume = {"header": "Jane Doe"}
        chunks = chunker.chunk_resume(resume, {"run_id": "run_1"}, "hash")

        assert chunks[0].freshness_status == "fresh"

    def test_chunk_generated_at_timestamp(self):
        """Chunk has generation timestamp."""
        chunker = ResumeChunker()

        resume = {"header": "Jane Doe"}
        chunks = chunker.chunk_resume(resume, {"run_id": "run_1"}, "hash")

        assert chunks[0].generated_at is not None
        assert "T" in chunks[0].generated_at  # ISO format

    def test_chunk_provenance_refs(self):
        """Chunk includes provenance references."""
        chunker = ResumeChunker()

        resume = {"certifications": ["AWS"]}
        run_context = {
            "run_id": "run_1",
            "exit_disposition_ref": "exit_ok_123",
            "uwg_commit_receipt": "receipt_456",
        }

        chunks = chunker.chunk_resume(resume, run_context, "hash")

        assert chunks[0].exit_disposition_ref == "exit_ok_123"
        assert chunks[0].uwg_commit_receipt == "receipt_456"

    def test_chunk_lineage_refs(self):
        """Chunk includes lineage references."""
        chunker = ResumeChunker()

        resume = {"projects": ["Project X"]}
        run_context = {
            "run_id": "run_1",
            "lineage_refs": ["parent_chunk_1", "parent_chunk_2"],
        }

        chunks = chunker.chunk_resume(resume, run_context, "hash")

        assert "parent_chunk_1" in chunks[0].lineage_refs

    def test_empty_resume_returns_empty_chunks(self):
        """Empty resume returns empty chunks list."""
        chunker = ResumeChunker()

        resume = {}
        chunks = chunker.chunk_resume(resume, {"run_id": "run_1"}, "hash")

        assert len(chunks) == 0

    def test_list_content_handling(self):
        """List content is joined with newlines."""
        chunker = ResumeChunker()

        resume = {"experience": ["Job 1", "Job 2", "Job 3"]}
        chunks = chunker.chunk_resume(resume, {"run_id": "run_1"}, "hash")

        assert "Job 1" in chunks[0].content
        assert "Job 2" in chunks[0].content

    def test_dict_content_handling(self):
        """Dict content is JSON serialized."""
        chunker = ResumeChunker()

        resume = {"header": {"name": "John", "title": "Engineer"}}
        chunks = chunker.chunk_resume(resume, {"run_id": "run_1"}, "hash")

        assert '"name": "John"' in chunks[0].content


class TestChunkContentHashing:
    """Test content hash generation."""

    def test_same_content_same_hash(self):
        """Same content produces same hash."""
        chunker = ResumeChunker()

        resume1 = {"header": "John Doe"}
        resume2 = {"header": "John Doe"}

        chunks1 = chunker.chunk_resume(resume1, {"run_id": "run_1"}, "hash1")
        chunks2 = chunker.chunk_resume(resume2, {"run_id": "run_2"}, "hash2")

        assert chunks1[0].content_hash == chunks2[0].content_hash

    def test_different_content_different_hash(self):
        """Different content produces different hash."""
        chunker = ResumeChunker()

        resume1 = {"header": "John Doe"}
        resume2 = {"header": "Jane Smith"}

        chunks1 = chunker.chunk_resume(resume1, {"run_id": "run_1"}, "hash1")
        chunks2 = chunker.chunk_resume(resume2, {"run_id": "run_2"}, "hash2")

        assert chunks1[0].content_hash != chunks2[0].content_hash


class TestChunkToDictSerialization:
    """Test chunk serialization."""

    def test_full_serialization(self):
        """Complete chunk can be serialized and contains all fields."""
        chunk = ResumeChunk(
            chunk_id="chunk_001",
            artifact_id="art_001",
            section_type="experience",
            content="Worked at Google",
            content_hash="hash123",
            source_run_id="run_001",
            source_request_id="req_001",
            source_input_intent_hash="intent_001",
            target_job_metadata={"company": "Acme", "role": "Engineer"},
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
            freshness_status="fresh",
            generated_at="2026-01-01T00:00:00Z",
            tenant_id="default",
            user_scope="user_123",
            lineage_refs=["parent_1"],
            replay_refs=["replay_1"],
            exit_disposition_ref="exit_ok",
            uwg_commit_receipt="receipt_123",
        )

        data = chunk.to_dict()

        # Verify structure
        assert data["chunk_id"] == "chunk_001"
        assert data["section_type"] == "experience"
        assert "lineage" in data
        assert "target_job_metadata" in data
        assert "scope" in data
        assert "provenance" in data

        # Verify lineage
        assert data["lineage"]["source_run_id"] == "run_001"
        assert data["lineage"]["source_input_intent_hash"] == "intent_001"

        # Verify scope
        assert data["scope"]["tenant_id"] == "default"

        # Verify provenance
        assert data["provenance"]["uwg_commit_receipt"] == "receipt_123"

    def test_serialization_json_serializable(self):
        """Serialized chunk can be JSON encoded."""
        chunk = ResumeChunk(
            chunk_id="chunk_001",
            artifact_id="art_001",
            section_type="summary",
            content="Summary text",
            content_hash="hash",
            source_run_id="run_1",
            source_request_id="req_1",
            source_input_intent_hash="intent_1",
            target_job_metadata={},
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
            freshness_status="fresh",
            generated_at="2026-01-01T00:00:00Z",
            tenant_id="default",
            user_scope="user",
            lineage_refs=[],
            replay_refs=[],
            exit_disposition_ref="exit",
            uwg_commit_receipt="receipt",
        )

        data = chunk.to_dict()
        json_str = json.dumps(data)

        assert json_str is not None
        assert len(json_str) > 0

        # Verify round-trip
        recovered = json.loads(json_str)
        assert recovered["chunk_id"] == "chunk_001"


class TestChunkerRunContextHandling:
    """Test chunker handling of run context."""

    def test_missing_optional_fields(self):
        """Chunker handles missing optional run_context fields."""
        chunker = ResumeChunker()

        resume = {"header": "John"}
        # Minimal run context
        run_context = {"run_id": "run_1"}

        chunks = chunker.chunk_resume(resume, run_context, "hash")

        assert chunks[0].source_run_id == "run_1"
        assert chunks[0].target_job_metadata == {}

    def test_unknown_section_types(self):
        """Chunker skips unknown section types (only known sections are chunked)."""
        chunker = ResumeChunker()

        resume = {"unknown_section": "Some content"}
        chunks = chunker.chunk_resume(resume, {"run_id": "run_1"}, "hash")

        # Unknown sections are skipped - only sections in SECTION_ORDER are chunked
        assert len(chunks) == 0


class TestChunkCommit:
    """Test chunk commitment via UWG (basic tests)."""

    def test_commit_function_exists(self):
        """Commit function exists and is callable."""
        from apps_rg.cache.chunk_commit import commit_chunks_via_exit

        assert callable(commit_chunks_via_exit)

    def test_build_receipt_function_exists(self):
        """Build receipt function exists."""
        from apps_rg.cache.chunk_commit import build_chunk_commit_receipt

        assert callable(build_chunk_commit_receipt)

    def test_build_receipt_structure(self):
        """Receipt has expected structure."""
        from apps_rg.cache.chunk_commit import build_chunk_commit_receipt

        chunk = ResumeChunk(
            chunk_id="chunk_001",
            artifact_id="art_001",
            section_type="experience",
            content="Content",
            content_hash="hash",
            source_run_id="run_1",
            source_request_id="req_1",
            source_input_intent_hash="intent_1",
            target_job_metadata={},
            policy_hash="policy_v1",
            blueprint_hash="blueprint_v1",
            freshness_status="fresh",
            generated_at="2026-01-01T00:00:00Z",
            tenant_id="default",
            user_scope="user",
            lineage_refs=[],
            replay_refs=[],
            exit_disposition_ref="exit",
            uwg_commit_receipt="receipt",
        )

        run_context = {
            "run_id": "run_1",
            "request_id": "req_1",
            "timestamp": "2026-01-01T00:00:00Z",
        }

        receipt = build_chunk_commit_receipt([chunk], "uwg_receipt_123", run_context)

        assert receipt["receipt_type"] == "chunk_commit"
        assert receipt["uwg_receipt"] == "uwg_receipt_123"
        assert receipt["chunks_committed"] == 1
        assert "chunk_001" in receipt["chunk_ids"]
        assert receipt["intent_hash"] == "intent_1"
