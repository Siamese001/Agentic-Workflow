"""Provenance Tracker - Granular data lineage tracking.

This module tracks the lineage of data, recording which sources were used
to generate which outputs, enabling full traceability and verification.
"""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


@dataclass
class SourceCitation:
    """Citation for a data source."""

    source_id: str
    uri: str
    snippet: str
    relevance_score: float
    citation_type: str = "source"
    verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "source_id": self.source_id,
            "uri": self.uri,
            "snippet": self.snippet,
            "relevance_score": self.relevance_score,
            "citation_type": self.citation_type,
            "verified": self.verified,
        }


class ArtifactLineage(BaseModel):
    """Lineage information for a generated artifact."""

    artifact_id: str
    generation_prompt: str
    used_sources: list[dict[str, Any]] = Field(default_factory=list)
    model_version: str
    timestamp: float = Field(default_factory=time.time)
    trace_id: str
    verification_status: str = "pending"
    verified_citations: list[str] = Field(default_factory=list)

    class Config:
        json_encoders = {}


class ProvenanceTracker:
    """Tracks data lineage for generated artifacts."""

    def __init__(self, storage_path: str = "./.provenance"):
        """Initialize provenance tracker.

        Args:
            storage_path: Path to store lineage data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.lineage_file = self.storage_path / "lineage.jsonl"
        self._active_context: dict[str, list[SourceCitation]] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            "lineages_recorded": 0,
            "sources_captured": 0,
            "verifications_completed": 0,
            "verification_rate": 0.0,
        }
        logger.info(f"Initialized ProvenanceTracker at {storage_path}")

    async def capture_context(self, trace_id: str, sources: list[tuple[str, str, float]]) -> None:
        """Capture context sources for a trace.

        Args:
            trace_id: Trace ID for tracking
            sources: List of (source_id, snippet, relevance) tuples
        """
        async with self._lock:
            citations = []
            for source_id, snippet, relevance in sources:
                citation = SourceCitation(
                    source_id=source_id,
                    uri=f"source://{source_id}",
                    snippet=snippet,
                    relevance_score=relevance,
                )
                citations.append(citation)
            self._active_context[trace_id] = citations
            self._stats["sources_captured"] += len(citations)
            logger.debug(f"Captured {len(citations)} sources for trace {trace_id}")

    async def record_generation(
        self,
        trace_id: str,
        artifact_id: str,
        output: str,
        model_version: str,
        generation_prompt: str | None = None,
    ) -> ArtifactLineage:
        """Record a generation with its lineage.

        Args:
            trace_id: Trace ID
            artifact_id: ID of generated artifact
            output: Generated output text
            model_version: Model version used
            generation_prompt: Prompt used for generation

        Returns:
            Artifact lineage record
        """
        async with self._lock:
            sources = self._active_context.get(trace_id, [])
            lineage = ArtifactLineage(
                artifact_id=artifact_id,
                generation_prompt=generation_prompt or "",
                used_sources=[c.to_dict() for c in sources],
                model_version=model_version,
                trace_id=trace_id,
            )
            await self._verify_citations(lineage, output)
            await self._store_lineage(lineage)
            if trace_id in self._active_context:
                del self._active_context[trace_id]
            self._stats["lineages_recorded"] += 1
            if lineage.verification_status == "verified":
                self._stats["verifications_completed"] += 1
            total = self._stats["lineages_recorded"]
            if total > 0:
                self._stats["verification_rate"] = self._stats["verifications_completed"] / total
            return lineage

    async def verify_citations(self, lineage: ArtifactLineage, output: str) -> ArtifactLineage:
        """Verify which sources were actually used.

        Args:
            lineage: Artifact lineage to verify
            output: Generated output text

        Returns:
            Updated lineage with verification results
        """
        return await self._verify_citations(lineage, output)

    async def _verify_citations(self, lineage: ArtifactLineage, output: str) -> None:
        """Internal method to verify citations.

        Args:
            lineage: Artifact lineage to update
            output: Generated output text
        """
        verified_sources = []
        verified_ids = []
        for source_dict in lineage.used_sources:
            citation = SourceCitation(**source_dict)
            similarity = self._calculate_similarity(citation.snippet, output)
            if similarity > 0.7 or self._has_exact_phrase(citation.snippet, output):
                citation.verified = True
                verified_ids.append(citation.source_id)
            verified_sources.append(citation.to_dict())
        lineage.used_sources = verified_sources
        lineage.verified_citations = verified_ids
        lineage.verification_status = "verified" if verified_ids else "failed"

    def _calculate_similarity(self, snippet: str, output: str) -> float:
        """Calculate similarity between snippet and output.

        Args:
            snippet: Source snippet
            output: Generated output

        Returns:
            Similarity score (0.0 to 1.0)
        """
        matcher = SequenceMatcher(None, snippet.lower(), output.lower())
        return matcher.ratio()

    # guardian: allow-magic-config
    def _has_exact_phrase(self, snippet: str, output: str, min_words: int = 3) -> bool:
        """Check if snippet contains an exact phrase in output.

        Args:
            snippet: Source snippet
            output: Generated output
            min_words: Minimum words for phrase match

        Returns:
            True if exact phrase found
        """
        words = snippet.lower().split()
        for i in range(len(words) - min_words + 1):
            phrase = " ".join(words[i : i + min_words])
            if phrase in output.lower():
                return True
        return False

    async def _store_lineage(self, lineage: ArtifactLineage) -> None:
        """Store lineage to file.

        Args:
            lineage: Lineage to store
        """
        try:
            lineage_json = json.dumps(lineage.dict(), default=str)
            async with asyncio.to_thread(self._append_lineage, lineage_json):
                pass
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to store lineage: {e}")
            raise

    def _append_lineage(self, lineage_json: str) -> None:
        """Append lineage to file (sync for file I/O).

        Args:
            lineage_json: JSON string to append
        """
        with open(self.lineage_file, "a", encoding="utf-8") as f:
            f.write(lineage_json + "\n")

    async def get_lineage(self, artifact_id: str) -> ArtifactLineage | None:
        """Get lineage for an artifact.

        Args:
            artifact_id: Artifact ID

        Returns:
            Lineage if found
        """
        try:
            async with asyncio.to_thread(self._read_lineage_file):
                pass
            for line in self._read_lineage_file():
                data = json.loads(line)
                if data.get("artifact_id") == artifact_id:
                    return ArtifactLineage(**data)
            return None
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to get lineage: {e}")
            return None

    def _read_lineage_file(self) -> list[str]:
        """Read lineage file lines.

        Returns:
            List of JSON lines
        """
        if not self.lineage_file.exists():
            return []
        with open(self.lineage_file, encoding="utf-8") as f:
            return f.readlines()

    # guardian: allow-magic-config
    async def search_lineage(
        self, trace_id: str | None = None, model_version: str | None = None, limit: int = 100
    ) -> list[ArtifactLineage]:
        """Search lineage records.

        Args:
            trace_id: Filter by trace ID
            model_version: Filter by model version
            limit: Maximum results

        Returns:
            List of matching lineages
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ProvenanceTracker.search_lineage")
        results = []
        try:
            lines = await asyncio.to_thread(self._read_lineage_file)
            for line in lines:
                data = json.loads(line)
                if trace_id and data.get("trace_id") != trace_id:
                    continue
                if model_version and data.get("model_version") != model_version:
                    continue
                results.append(ArtifactLineage(**data))
                if len(results) >= limit:
                    break
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to search lineage: {e}")
        return results

    async def cleanup(self, older_than_days: int = 30) -> int:
        """Clean up old lineage records.

        Args:
            older_than_days: Age threshold in days

        Returns:
            Number of records cleaned up
        """
        cutoff_time = time.time() - older_than_days * 24 * 3600
        try:
            lines = await asyncio.to_thread(self._read_lineage_file)
            kept_lines = []
            cleaned = 0
            for line in lines:
                data = json.loads(line)
                if data.get("timestamp", 0) > cutoff_time:
                    kept_lines.append(line)
                else:
                    cleaned += 1
            if cleaned > 0:
                async with asyncio.to_thread(self._write_lineage_file, kept_lines):
                    pass
                logger.info(f"Cleaned up {cleaned} old lineage records")
            return cleaned
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to cleanup lineage: {e}")
            return 0

    def _write_lineage_file(self, lines: list[str]) -> None:
        """Write lineage file (sync for file I/O).

        Args:
            lines: Lines to write
        """
        with open(self.lineage_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def get_stats(self) -> dict[str, Any]:
        """Get provenance tracker statistics.

        Returns:
            Statistics dictionary
        """
        return self._stats.copy()

    async def health_check(self) -> dict[str, Any]:
        """Check health of provenance tracker.

        Returns:
            Health status
        """
        try:
            storage_accessible = self.storage_path.exists() and self.storage_path.is_dir()
            file_size = 0
            if self.lineage_file.exists():
                file_size = self.lineage_file.stat().st_size
            return {
                "status": "healthy" if storage_accessible else "unhealthy",
                "storage_path": str(self.storage_path),
                "storage_accessible": storage_accessible,
                "lineage_file_size": file_size,
                "active_contexts": len(self._active_context),
                "stats": self._stats,
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "stats": self._stats}


_provenance_tracker: ProvenanceTracker | None = None
_tracker_lock = asyncio.Lock()


async def get_provenance_tracker() -> ProvenanceTracker:
    """Get global provenance tracker instance.

    Returns:
        ProvenanceTracker instance
    """
    global _provenance_tracker
    async with _tracker_lock:
        if _provenance_tracker is None:
            _provenance_tracker = ProvenanceTracker()
    return _provenance_tracker


class ProvenanceContext:
    """Context manager for provenance tracking."""

    def __init__(
        self, trace_id: str, sources: list[tuple[str, str, float]], tracker: ProvenanceTracker | None = None
    ):
        """Initialize provenance context.

        Args:
            trace_id: Trace ID
            sources: List of (source_id, snippet, relevance) tuples
            tracker: Provenance tracker instance
        """
        self.trace_id = trace_id
        self.sources = sources
        self.tracker = tracker

    async def __aenter__(self):
        """Enter context."""
        if not self.tracker:
            self.tracker = await get_provenance_tracker()
        await self.tracker.capture_context(self.trace_id, self.sources)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        pass

    async def record_generation(
        self, artifact_id: str, output: str, model_version: str, generation_prompt: str | None = None
    ) -> ArtifactLineage:
        """Record generation within context.

        Args:
            artifact_id: Artifact ID
            output: Generated output
            model_version: Model version
            generation_prompt: Generation prompt

        Returns:
            Artifact lineage
        """
        return await self.tracker.record_generation(
            self.trace_id, artifact_id, output, model_version, generation_prompt
        )


async def track_provenance(
    trace_id: str,
    sources: list[tuple[str, str, float]],
    artifact_id: str,
    output: str,
    model_version: str,
    generation_prompt: str | None = None,
) -> ArtifactLineage:
    """Track provenance for a generation.

    Args:
        trace_id: Trace ID
        sources: List of (source_id, snippet, relevance) tuples
        artifact_id: Artifact ID
        output: Generated output
        model_version: Model version
        generation_prompt: Generation prompt

    Returns:
        Artifact lineage
    """
    tracker = await get_provenance_tracker()
    async with ProvenanceContext(trace_id, sources, tracker):
        return await tracker.record_generation(
            trace_id, artifact_id, output, model_version, generation_prompt
        )


def provenance_tracked(extract_sources: Callable | None = None):
    """Decorator to automatically track provenance.

    Args:
        extract_sources: Function to extract sources from arguments

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            trace_id = None
            if args and hasattr(args[0], "trace_id"):
                trace_id = args[0].trace_id
            else:
                trace_id = f"trace_{int(time.time())}"
            sources = []
            if extract_sources:
                sources = extract_sources(*args, **kwargs)
            result = await func(*args, **kwargs)
            output = str(result)
            model_version = getattr(func, "_model_version", "unknown")
            if sources:
                await track_provenance(
                    trace_id, sources, f"artifact_{int(time.time())}", output, model_version
                )
            return result

        return async_wrapper

    return decorator
