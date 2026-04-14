"""Chunking Modes - Pipeline B Step 2

Implements spec-compliant chunking modes from Agentic Retrieval Models v9:
- FixedToken: Fixed-size token chunks
- OverlapWindow: Sliding window with overlap
- SectionAware: Section/heading-based chunking
- SemanticObject: Semantic unit chunking

Provides multiple chunking strategies for different document types.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)
from tqdm import tqdm


@dataclass
class Chunk:
    """Document chunk with metadata."""

    id: str
    content: str
    start_pos: int
    end_pos: int
    chunk_type: str = "text"
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk(self, text: str, doc_id: str = "") -> list[Chunk]:
        """Chunk text into pieces.

        Args:
            text: Text to chunk
            doc_id: Document identifier

        Returns:
            List of chunks
        """
        pass


class FixedTokenChunker(ChunkingStrategy):
    """Fixed-size token chunking.

    Chunks text into fixed-size pieces by token count.
    """

    def __init__(self, tokens_per_chunk: int = 512, overlap_tokens: int = 50):
        """Initialize fixed token chunker.

        Args:
            tokens_per_chunk: Tokens per chunk (default 512)
            overlap_tokens: Overlap between chunks (default 50)
        """
        self.tokens_per_chunk = tokens_per_chunk
        self.overlap_tokens = overlap_tokens
        self.approx_chars_per_token = 4  # Rough estimate

    def chunk(self, text: str, doc_id: str = "") -> list[Chunk]:
        """Chunk text into fixed-size pieces."""
        _emit_records_execution_trace(
            f"chunk_fixed_{doc_id}",
            LayerSegment.L2_EXECUTION,
            "FixedTokenChunker.chunk",
        )

        chunks = []
        chars_per_chunk = self.tokens_per_chunk * self.approx_chars_per_token
        overlap_chars = self.overlap_tokens * self.approx_chars_per_token

        start = 0
        chunk_idx = 0

        while start < len(text):
            end = min(start + chars_per_chunk, len(text))

            # Extend to word boundary
            if end < len(text):
                while end < len(text) and text[end] not in " \n\t":
                    end += 1

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        id=f"{doc_id}_fixed_{chunk_idx}",
                        content=chunk_text,
                        start_pos=start,
                        end_pos=end,
                        chunk_type="fixed_token",
                        metadata={
                            "tokens_estimated": len(chunk_text) // self.approx_chars_per_token,
                            "strategy": "fixed_token",
                        },
                    )
                )
                chunk_idx += 1

            # Move start with overlap
            start = end - overlap_chars if end < len(text) else end
            if start >= end:  # Prevent infinite loop
                start = end

        return chunks


class OverlapWindowChunker(ChunkingStrategy):
    """Sliding window chunking with overlap.

    Uses sliding windows with configurable stride.
    """

    def __init__(self, window_size: int = 400, stride: int = 200):
        """Initialize overlap window chunker.

        Args:
            window_size: Window size in tokens (default 400)
            stride: Stride between windows in tokens (default 200)
        """
        self.window_size = window_size
        self.stride = stride
        self.approx_chars_per_token = 4

    def chunk(self, text: str, doc_id: str = "") -> list[Chunk]:
        """Chunk text using sliding windows."""
        _emit_records_execution_trace(
            f"chunk_overlap_{doc_id}",
            LayerSegment.L2_EXECUTION,
            "OverlapWindowChunker.chunk",
        )

        chunks = []
        window_chars = self.window_size * self.approx_chars_per_token
        stride_chars = self.stride * self.approx_chars_per_token

        start = 0
        chunk_idx = 0

        while start < len(text):
            end = min(start + window_chars, len(text))

            chunk_text = text[start:end].strip()
            if len(chunk_text) > 50:  # Minimum chunk size
                chunks.append(
                    Chunk(
                        id=f"{doc_id}_overlap_{chunk_idx}",
                        content=chunk_text,
                        start_pos=start,
                        end_pos=end,
                        chunk_type="overlap_window",
                        metadata={
                            "window_size_tokens": self.window_size,
                            "stride_tokens": self.stride,
                            "strategy": "overlap_window",
                        },
                    )
                )
                chunk_idx += 1

            start += stride_chars

        return chunks


class SectionAwareChunker(ChunkingStrategy):
    """Section/heading-aware chunking.

    Chunks based on document structure (headings, sections).
    """

    def __init__(self, max_section_tokens: int = 1000):
        """Initialize section-aware chunker.

        Args:
            max_section_tokens: Max tokens per section (default 1000)
        """
        self.max_section_tokens = max_section_tokens
        self.approx_chars_per_token = 4

        # Heading patterns
        self.heading_patterns = [
            r"^#{1,6}\s+(.+)$",  # Markdown headings
            r"^(.+)\n[=-]+$",  # Underlined headings
            r"^\d+\.\s+(.+)$",  # Numbered sections
            r"^[A-Z][A-Z\s]+$",  # ALL CAPS headings
        ]

    def _find_headings(self, text: str) -> list[tuple[int, str]]:
        """Find all headings in text.

        Returns:
            List of (position, heading_text) tuples
        """
        headings = []
        lines = text.split("\n")
        pos = 0

        for i, line in enumerate(lines):
            for pattern in self.heading_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    headings.append((pos, line.strip()))
                    break
            pos += len(line) + 1  # +1 for newline

        return headings

    def chunk(self, text: str, doc_id: str = "") -> list[Chunk]:
        """Chunk text by sections."""
        _emit_records_execution_trace(
            f"chunk_section_{doc_id}",
            LayerSegment.L2_EXECUTION,
            "SectionAwareChunker.chunk",
        )

        headings = self._find_headings(text)

        if not headings:
            # No headings found, fall back to fixed token
            return FixedTokenChunker().chunk(text, doc_id)

        chunks = []
        max_chars = self.max_section_tokens * self.approx_chars_per_token

        for i, (start_pos, heading) in tqdm(enumerate(headings), desc="Processing", unit="item"):
            # Section extends to next heading or end
            if i + 1 < len(headings):
                end_pos = headings[i + 1][0]
            else:
                end_pos = len(text)

            section_text = text[start_pos:end_pos].strip()

            # If section too large, subdivide
            if len(section_text) > max_chars:
                sub_chunks = self._subdivide_section(section_text, start_pos, max_chars)
                for j, (sub_start, sub_end, sub_text) in tqdm(
                    enumerate(sub_chunks), desc="Processing", unit="item"
                ):
                    chunks.append(
                        Chunk(
                            id=f"{doc_id}_section_{i}_{j}",
                            content=sub_text,
                            start_pos=sub_start,
                            end_pos=sub_end,
                            chunk_type="section_aware",
                            metadata={
                                "heading": heading,
                                "section_index": i,
                                "subsection_index": j,
                                "strategy": "section_aware",
                            },
                        )
                    )
            else:
                chunks.append(
                    Chunk(
                        id=f"{doc_id}_section_{i}",
                        content=section_text,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        chunk_type="section_aware",
                        metadata={
                            "heading": heading,
                            "section_index": i,
                            "strategy": "section_aware",
                        },
                    )
                )

        return chunks

    def _subdivide_section(
        self,
        section_text: str,
        section_start: int,
        max_chars: int,
    ) -> list[tuple[int, int, str]]:
        """Subdivide a large section into smaller chunks."""
        sub_chunks = []
        start = 0

        while start < len(section_text):
            end = min(start + max_chars, len(section_text))

            # Extend to paragraph boundary
            if end < len(section_text):
                while end < len(section_text) and section_text[end : end + 2] != "\n\n":
                    end += 1

            chunk_text = section_text[start:end].strip()
            if chunk_text:
                sub_chunks.append(
                    (
                        section_start + start,
                        section_start + end,
                        chunk_text,
                    )
                )

            start = end

        return sub_chunks


class SemanticObjectChunker(ChunkingStrategy):
    """Semantic object chunking.

    Chunks based on semantic units (paragraphs, sentences, semantic boundaries).
    """

    def __init__(self, target_tokens: int = 300, max_tokens: int = 500):
        """Initialize semantic object chunker.

        Args:
            target_tokens: Target tokens per chunk (default 300)
            max_tokens: Maximum tokens per chunk (default 500)
        """
        self.target_tokens = target_tokens
        self.max_tokens = max_tokens
        self.approx_chars_per_token = 4

    def _split_into_units(self, text: str) -> list[tuple[int, int, str, str]]:
        """Split text into semantic units.

        Returns:
            List of (start, end, unit_type, content) tuples
        """
        units = []
        pos = 0

        # Split into paragraphs first
        paragraphs = re.split(r"\n\n+", text)

        for para in tqdm(paragraphs, desc="Processing", unit="item"):
            para = para.strip()
            if not para:
                continue

            para_len = len(para)

            # Check if paragraph is small enough
            if para_len <= self.max_tokens * self.approx_chars_per_token:
                units.append((pos, pos + para_len, "paragraph", para))
            else:
                # Split large paragraphs into sentences
                sentences = re.split(r"(?<=[.!?])\s+", para)
                sent_pos = pos

                for sent in sentences:
                    sent = sent.strip()
                    if sent:
                        sent_len = len(sent)
                        units.append((sent_pos, sent_pos + sent_len, "sentence", sent))
                        sent_pos += sent_len + 1

            pos += para_len + 2  # +2 for paragraph breaks

        return units

    def chunk(self, text: str, doc_id: str = "") -> list[Chunk]:
        """Chunk text into semantic objects."""
        _emit_records_execution_trace(
            f"chunk_semantic_{doc_id}",
            LayerSegment.L2_EXECUTION,
            "SemanticObjectChunker.chunk",
        )

        units = self._split_into_units(text)
        chunks = []
        chunk_idx = 0

        current_units = []
        current_size = 0
        chunk_start = units[0][0] if units else 0

        target_chars = self.target_tokens * self.approx_chars_per_token
        max_chars = self.max_tokens * self.approx_chars_per_token

        for start, end, unit_type, content in tqdm(units, desc="Processing", unit="item"):
            unit_size = end - start

            # Check if adding this unit exceeds max
            if current_size + unit_size > max_chars and current_units:
                # Finalize current chunk
                chunk_text = " ".join(u[3] for u in current_units)
                chunk_end = current_units[-1][1]

                chunks.append(
                    Chunk(
                        id=f"{doc_id}_semantic_{chunk_idx}",
                        content=chunk_text,
                        start_pos=chunk_start,
                        end_pos=chunk_end,
                        chunk_type="semantic_object",
                        metadata={
                            "unit_count": len(current_units),
                            "unit_types": [u[2] for u in current_units],
                            "strategy": "semantic_object",
                        },
                    )
                )
                chunk_idx += 1

                # Start new chunk
                current_units = [(start, end, unit_type, content)]
                current_size = unit_size
                chunk_start = start
            else:
                current_units.append((start, end, unit_type, content))
                current_size += unit_size

            # Check if we've hit target size
            if current_size >= target_chars:
                chunk_text = " ".join(u[3] for u in current_units)
                chunk_end = current_units[-1][1]

                chunks.append(
                    Chunk(
                        id=f"{doc_id}_semantic_{chunk_idx}",
                        content=chunk_text,
                        start_pos=chunk_start,
                        end_pos=chunk_end,
                        chunk_type="semantic_object",
                        metadata={
                            "unit_count": len(current_units),
                            "unit_types": [u[2] for u in current_units],
                            "strategy": "semantic_object",
                        },
                    )
                )
                chunk_idx += 1

                current_units = []
                current_size = 0
                chunk_start = end

        # Add remaining units
        if current_units:
            chunk_text = " ".join(u[3] for u in current_units)
            chunk_end = current_units[-1][1]

            chunks.append(
                Chunk(
                    id=f"{doc_id}_semantic_{chunk_idx}",
                    content=chunk_text,
                    start_pos=chunk_start,
                    end_pos=chunk_end,
                    chunk_type="semantic_object",
                    metadata={
                        "unit_count": len(current_units),
                        "unit_types": [u[2] for u in current_units],
                        "strategy": "semantic_object",
                    },
                )
            )

        return chunks


class ChunkingEngine:
    """Unified chunking engine with strategy selection.

    Automatically selects appropriate chunking strategy based on document type.
    """

    STRATEGIES = {
        "fixed_token": FixedTokenChunker,
        "overlap_window": OverlapWindowChunker,
        "section_aware": SectionAwareChunker,
        "semantic_object": SemanticObjectChunker,
    }

    def __init__(self, default_strategy: str = "semantic_object"):
        """Initialize chunking engine.

        Args:
            default_strategy: Default chunking strategy
        """
        self.default_strategy = default_strategy
        self._chunkers: dict[str, ChunkingStrategy] = {}

    def get_chunker(self, strategy: str | None = None) -> ChunkingStrategy:
        """Get chunker for strategy.

        Args:
            strategy: Strategy name (defaults to default_strategy)

        Returns:
            ChunkingStrategy instance
        """
        strategy = strategy or self.default_strategy

        if strategy not in self._chunkers:
            if strategy in self.STRATEGIES:
                self._chunkers[strategy] = self.STRATEGIES[strategy]()
            else:
                self._chunkers[strategy] = SemanticObjectChunker()

        return self._chunkers[strategy]

    def chunk(
        self,
        text: str,
        doc_id: str = "",
        strategy: str | None = None,
    ) -> list[Chunk]:
        """Chunk text using specified strategy.

        Args:
            text: Text to chunk
            doc_id: Document identifier
            strategy: Chunking strategy (auto-selected if None)

        Returns:
            List of chunks
        """
        # Auto-select strategy based on content
        if strategy is None:
            strategy = self._auto_select_strategy(text)

        chunker = self.get_chunker(strategy)
        return chunker.chunk(text, doc_id)

    def _auto_select_strategy(self, text: str) -> str:
        """Auto-select best strategy for text.

        Args:
            text: Text to analyze

        Returns:
            Strategy name
        """
        # Check for headings
        heading_pattern = r"^(#{1,6}\s+|.+[=-]+|\d+\.\s+)"
        if re.search(heading_pattern, text, re.MULTILINE):
            return "section_aware"

        # Check for code blocks (semantic chunking better)
        if "```" in text or text.count("\n    ") > 10:
            return "semantic_object"

        # Default
        return self.default_strategy

    def chunk_batch(
        self,
        documents: list[tuple[str, str]],  # (doc_id, text) pairs
        strategy: str | None = None,
    ) -> dict[str, list[Chunk]]:
        """Chunk multiple documents.

        Args:
            documents: List of (doc_id, text) tuples
            strategy: Chunking strategy

        Returns:
            Dict mapping doc_id to chunks
        """
        results = {}
        for doc_id, text in documents:
            results[doc_id] = self.chunk(text, doc_id, strategy)
        return results


# Global instance
_global_chunking_engine: ChunkingEngine | None = None


def get_global_chunking_engine() -> ChunkingEngine:
    """Get or create global chunking engine."""
    global _global_chunking_engine
    if _global_chunking_engine is None:
        _global_chunking_engine = ChunkingEngine()
    return _global_chunking_engine


def chunk_document(
    text: str,
    doc_id: str = "",
    strategy: str = "semantic_object",
) -> list[Chunk]:
    """Convenience function to chunk a document."""
    return get_global_chunking_engine().chunk(text, doc_id, strategy)
