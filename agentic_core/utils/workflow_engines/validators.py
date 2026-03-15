"""
Chunk Validators

Validates chunk manifests for size, overlap sanity, duplicates, and orphans.
All validators are deterministic and zero-dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .policies import Chunk, ChunkManifest
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class ChunkQualityReport:
    """Validation report for a chunk manifest."""

    doc_id: str
    policy_name: str
    total_chunks: int
    duplicates: int
    orphan_chunks: int
    oversized_chunks: int
    undersized_chunks: int
    overlap_violations: int
    duplicate_chunk_ids: list[str] = field(default_factory=list)
    orphan_chunk_ids: list[str] = field(default_factory=list)
    oversized_chunk_ids: list[str] = field(default_factory=list)
    undersized_chunk_ids: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True iff no violations detected."""
        return (
            self.duplicates == 0
            and self.orphan_chunks == 0
            and (self.oversized_chunks == 0)
            and (self.overlap_violations == 0)
        )

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "policy_name": self.policy_name,
            "total_chunks": self.total_chunks,
            "duplicates": self.duplicates,
            "orphan_chunks": self.orphan_chunks,
            "oversized_chunks": self.oversized_chunks,
            "undersized_chunks": self.undersized_chunks,
            "overlap_violations": self.overlap_violations,
            "duplicate_chunk_ids": self.duplicate_chunk_ids,
            "orphan_chunk_ids": self.orphan_chunk_ids,
            "oversized_chunk_ids": self.oversized_chunk_ids,
            "undersized_chunk_ids": self.undersized_chunk_ids,
            "messages": self.messages,
            "is_valid": self.is_valid,
        }


class MaxChunkSizeValidator:
    """Flags chunks exceeding a maximum token count."""

    # guardian: allow-magic-config
    def __init__(self, max_tokens: int = 1024):
        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")
        self.max_tokens = max_tokens

    def validate(self, chunks: list[Chunk]) -> list[str]:
        """Return list of chunk_ids that exceed max_tokens."""
        return [c.chunk_id for c in chunks if c.token_count > self.max_tokens]


class MinChunkSizeValidator:
    """Flags chunks below a minimum token count (potential orphans)."""

    # guardian: allow-magic-config
    def __init__(self, min_tokens: int = 10):
        if min_tokens < 0:
            raise ValueError(f"min_tokens must be non-negative, got {min_tokens}")
        self.min_tokens = min_tokens

    def validate(self, chunks: list[Chunk]) -> list[str]:
        """Return list of chunk_ids that are below min_tokens."""
        return [c.chunk_id for c in chunks if c.token_count < self.min_tokens]


class OverlapSanityValidator:
    """Verifies that overlapping windows don't produce identical chunks."""

    def validate(self, chunks: list[Chunk]) -> int:
        """Return number of consecutive identical-content chunk pairs."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OverlapSanityValidator.validate")

        violations = 0
        for i in range(len(chunks) - 1):
            if chunks[i].content.strip() == chunks[i + 1].content.strip():
                violations += 1
        return violations


class DuplicateChunkDetector:
    """Detects chunks with duplicate content across the manifest."""

    def detect(self, chunks: list[Chunk]) -> list[str]:
        """Return list of chunk_ids whose content is a duplicate of an earlier chunk."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DuplicateChunkDetector.detect")

        seen: set[str] = set()
        duplicates: list[str] = []
        for chunk in chunks:
            content_key = chunk.content.strip().lower()
            if content_key in seen:
                duplicates.append(chunk.chunk_id)
            else:
                seen.add(content_key)
        return duplicates


class OrphanChunkDetector:
    """Detects chunks with no meaningful content (empty or whitespace-only)."""

    def detect(self, chunks: list[Chunk]) -> list[str]:
        """Return list of chunk_ids with empty or whitespace-only content."""
        return [c.chunk_id for c in chunks if not c.content.strip()]


class ChunkManifestValidator:
    """Runs all validators against a ChunkManifest and produces a ChunkQualityReport."""

    # guardian: allow-magic-config
    def __init__(self, max_chunk_tokens: int = 1024, min_chunk_tokens: int = 10):
        self.max_validator = MaxChunkSizeValidator(max_tokens=max_chunk_tokens)
        self.min_validator = MinChunkSizeValidator(min_tokens=min_chunk_tokens)
        self.overlap_validator = OverlapSanityValidator()
        self.duplicate_detector = DuplicateChunkDetector()
        self.orphan_detector = OrphanChunkDetector()

    def validate(self, manifest: ChunkManifest) -> ChunkQualityReport:
        """Validate all chunks in a manifest.

        Args:
            manifest: ChunkManifest to validate

        Returns:
            ChunkQualityReport with all detected violations
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ChunkManifestValidator.validate")

        chunks = manifest.chunks
        messages: list[str] = []
        oversized = self.max_validator.validate(chunks)
        undersized = self.min_validator.validate(chunks)
        overlap_violations = self.overlap_validator.validate(chunks)
        duplicates = self.duplicate_detector.detect(chunks)
        orphans = self.orphan_detector.detect(chunks)
        if oversized:
            messages.append(f"{len(oversized)} chunk(s) exceed max token limit")
        if orphans:
            messages.append(f"{len(orphans)} orphan chunk(s) detected (empty content)")
        if duplicates:
            messages.append(f"{len(duplicates)} duplicate chunk(s) detected")
        if overlap_violations > 0:
            messages.append(f"{overlap_violations} overlap sanity violation(s) detected")
        return ChunkQualityReport(
            doc_id=manifest.doc_id,
            policy_name=manifest.policy_name,
            total_chunks=len(chunks),
            duplicates=len(duplicates),
            orphan_chunks=len(orphans),
            oversized_chunks=len(oversized),
            undersized_chunks=len(undersized),
            overlap_violations=overlap_violations,
            duplicate_chunk_ids=duplicates,
            orphan_chunk_ids=orphans,
            oversized_chunk_ids=oversized,
            undersized_chunk_ids=undersized,
            messages=messages,
        )


__all__ = [
    "ChunkQualityReport",
    "MaxChunkSizeValidator",
    "MinChunkSizeValidator",
    "OverlapSanityValidator",
    "DuplicateChunkDetector",
    "OrphanChunkDetector",
    "ChunkManifestValidator",
]
