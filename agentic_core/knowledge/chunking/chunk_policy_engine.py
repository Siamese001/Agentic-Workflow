"""Chunk Policy Engine.

Unified policy application for chunking with strategy selection based on corpus type.
Metadata enrichment during chunking with corpus-aware processing.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.knowledge.chunking.chunking_modes import (
    Chunk,
    ChunkingEngine,
)
from agentic_core.knowledge.chunking.corpus_classifier import (
    CorpusClassifier,
    CorpusType,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class ChunkPolicy:
    """Policy configuration for chunking."""
    strategy: str
    chunk_size: int
    overlap: int
    preserve_boundaries: bool = True
    enrich_metadata: bool = True
    corpus_type: CorpusType | None = None
    custom_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkResult:
    """Result of chunking with policy."""
    chunks: list[Chunk]
    policy: ChunkPolicy
    corpus_type: CorpusType
    metadata: dict[str, Any]


class ChunkPolicyEngine:
    """Unified chunking policy engine with corpus-aware strategy selection.

    The ChunkPolicyEngine provides intelligent chunking strategy selection
    based on corpus classification, eliminating generic defaults.
    """

    def __init__(
        self,
        corpus_classifier: CorpusClassifier | None = None,
        chunking_engine: ChunkingEngine | None = None,
    ):
        """Initialize the chunk policy engine.

        Args:
            corpus_classifier: Classifier for corpus type detection
            chunking_engine: Engine for executing chunking strategies
        """
        self.classifier = corpus_classifier or CorpusClassifier()
        self.engine = chunking_engine or ChunkingEngine()

        # Corpus-specific policies
        self._policies = self._setup_default_policies()

        log.info("ChunkPolicyEngine initialized")

    def _setup_default_policies(self) -> dict[CorpusType, ChunkPolicy]:
        """Setup default policies for each corpus type."""
        return {
            CorpusType.POLICY: ChunkPolicy(
                strategy="section_aware",
                chunk_size=512,
                overlap=64,
                preserve_boundaries=True,
                enrich_metadata=True,
                corpus_type=CorpusType.POLICY,
                custom_params={
                    "heading_priority": True,
                    "parent_child_links": True,
                },
            ),
            CorpusType.INCIDENT_TRACE: ChunkPolicy(
                strategy="semantic_object",
                chunk_size=256,
                overlap=32,
                preserve_boundaries=True,
                enrich_metadata=True,
                corpus_type=CorpusType.INCIDENT_TRACE,
                custom_params={
                    "event_boundary_priority": True,
                    "temporal_metadata": True,
                },
            ),
            CorpusType.CODE_CONFIG: ChunkPolicy(
                strategy="semantic_object",
                chunk_size=384,
                overlap=48,
                preserve_boundaries=True,
                enrich_metadata=True,
                corpus_type=CorpusType.CODE_CONFIG,
                custom_params={
                    "symbol_extraction": True,
                    "dependency_tracking": True,
                    "block_aware": True,
                },
            ),
            CorpusType.VISUAL_TABLE: ChunkPolicy(
                strategy="fixed_token",
                chunk_size=128,
                overlap=16,
                preserve_boundaries=True,
                enrich_metadata=True,
                corpus_type=CorpusType.VISUAL_TABLE,
                custom_params={
                    "element_aware": True,
                    "multimodal_flags": True,
                },
            ),
            CorpusType.GENERAL: ChunkPolicy(
                strategy="overlap_window",
                chunk_size=256,
                overlap=32,
                preserve_boundaries=False,
                enrich_metadata=True,
                corpus_type=CorpusType.GENERAL,
                custom_params={},
            ),
        }

    def chunk_document(
        self,
        content: str,
        doc_id: str = "",
        file_path: Path | None = None,
        policy: ChunkPolicy | None = None,
    ) -> ChunkResult:
        """Chunk a document using appropriate policy.

        Args:
            content: Document content to chunk
            doc_id: Document identifier
            file_path: Optional file path for classification
            policy: Optional explicit policy (auto-detect if None)

        Returns:
            ChunkResult with chunks and metadata
        """
        trace_id = f"chunk_{doc_id}_{int(time.time())}" if doc_id else f"chunk_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L2_EXECUTION, "ChunkPolicyEngine.chunk_document"
        )

        # Determine policy if not provided
        if policy is None:
            classification = self.classifier.classify(content, file_path)
            policy = self._policies.get(
                classification.corpus_type,
                self._policies[CorpusType.GENERAL]
            )
            corpus_type = classification.corpus_type
        else:
            corpus_type = policy.corpus_type or CorpusType.GENERAL

        # Execute chunking with selected strategy
        chunks = self.engine.chunk(content, doc_id, strategy=policy.strategy)

        # Enrich metadata if enabled
        metadata = {
            "corpus_type": corpus_type.value,
            "strategy": policy.strategy,
            "chunk_count": len(chunks),
            "total_tokens": sum(len(chunk.content) for chunk in chunks),
        }

        if policy.enrich_metadata:
            chunks = self._enrich_chunks(chunks, policy, corpus_type)
            metadata["enriched"] = True

        _emit_records_telemetry_event(
            "chunking",
            f"completed_{corpus_type.value}_{len(chunks)}_chunks"
        )

        return ChunkResult(
            chunks=chunks,
            policy=policy,
            corpus_type=corpus_type,
            metadata=metadata,
        )

    def chunk_batch(
        self,
        documents: list[dict[str, Any]],
    ) -> list[ChunkResult]:
        """Chunk multiple documents.

        Args:
            documents: List of dicts with 'content', 'doc_id', 'file_path' keys

        Returns:
            List of ChunkResult objects
        """
        results = []
        for doc in documents:
            result = self.chunk_document(
                content=doc["content"],
                doc_id=doc.get("doc_id", ""),
                file_path=doc.get("file_path"),
            )
            results.append(result)
        return results

    def set_policy(self, corpus_type: CorpusType, policy: ChunkPolicy) -> None:
        """Set custom policy for a corpus type.

        Args:
            corpus_type: Corpus type to set policy for
            policy: Policy configuration
        """
        policy.corpus_type = corpus_type
        self._policies[corpus_type] = policy
        log.info(f"Updated policy for {corpus_type.value}")

    def get_policy(self, corpus_type: CorpusType) -> ChunkPolicy:
        """Get policy for a corpus type.

        Args:
            corpus_type: Corpus type to get policy for

        Returns:
            ChunkPolicy for the corpus type
        """
        return self._policies.get(corpus_type, self._policies[CorpusType.GENERAL])

    def _enrich_chunks(
        self,
        chunks: list[Chunk],
        policy: ChunkPolicy,
        corpus_type: CorpusType,
    ) -> list[Chunk]:
        """Enrich chunk metadata based on corpus type."""
        enriched = []

        for i, chunk in enumerate(chunks):
            # Add corpus-specific metadata
            if corpus_type == CorpusType.POLICY:
                chunk.metadata["heading_context"] = self._extract_headings(chunk.content)
                chunk.metadata["section_level"] = self._detect_section_level(chunk.content)

            elif corpus_type == CorpusType.INCIDENT_TRACE:
                chunk.metadata["temporal_order"] = i
                chunk.metadata["event_markers"] = self._extract_event_markers(chunk.content)

            elif corpus_type == CorpusType.CODE_CONFIG:
                chunk.metadata["symbols"] = self._extract_symbols(chunk.content)
                chunk.metadata["code_blocks"] = self._detect_code_blocks(chunk.content)

            elif corpus_type == CorpusType.VISUAL_TABLE:
                chunk.metadata["visual_elements"] = self._count_visual_elements(chunk.content)
                chunk.metadata["multimodal"] = True

            # Add common metadata
            chunk.metadata["corpus_type"] = corpus_type.value
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunks)

            enriched.append(chunk)

        return enriched

    def _extract_headings(self, content: str) -> list[str]:
        """Extract heading lines from content."""
        import re
        headings = []
        for line in content.split('\n'):
            if re.match(r'^#{1,6}\s+', line):
                headings.append(line.strip())
        return headings

    def _detect_section_level(self, content: str) -> int:
        """Detect the minimum heading level in content."""
        import re
        levels = []
        for line in content.split('\n'):
            match = re.match(r'^(#{1,6})\s+', line)
            if match:
                levels.append(len(match.group(1)))
        return min(levels) if levels else 0

    def _extract_event_markers(self, content: str) -> list[str]:
        """Extract event/timestamp markers."""
        import re
        markers = []
        timestamp_pattern = r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'
        for match in re.finditer(timestamp_pattern, content):
            markers.append(match.group())
        return markers

    def _extract_symbols(self, content: str) -> list[str]:
        """Extract code symbols (function/class names)."""
        import re
        symbols = []
        # Match function definitions
        for match in re.finditer(r'(?:def|function|class)\s+(\w+)', content):
            symbols.append(match.group(1))
        return symbols

    def _detect_code_blocks(self, content: str) -> int:
        """Count code blocks in content."""
        return content.count('```') // 2

    def _count_visual_elements(self, content: str) -> int:
        """Count visual elements (images, tables)."""
        import re
        images = len(re.findall(r'!\[.*?\]\(.*?\)', content))
        tables = len(re.findall(r'\|[-:]+\|', content))
        return images + tables


# Global instance
_global_engine: ChunkPolicyEngine | None = None


def get_chunk_policy_engine() -> ChunkPolicyEngine:
    """Get or create the global chunk policy engine."""
    global _global_engine
    if _global_engine is None:
        _global_engine = ChunkPolicyEngine()
    return _global_engine


import time
