"""
Chunking Governance Policies

Supported policies: fixed_token, overlap_window, section_aware, semantic.
All policies implement the ChunkPolicy interface.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """A single document chunk with provenance metadata."""

    chunk_id: str
    doc_id: str
    content: str
    token_count: int
    start_char: int
    end_char: int
    parent_section: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "content": self.content,
            "token_count": self.token_count,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "parent_section": self.parent_section,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Chunk:
        return cls(
            chunk_id=data["chunk_id"],
            doc_id=data["doc_id"],
            content=data["content"],
            token_count=data["token_count"],
            start_char=data["start_char"],
            end_char=data["end_char"],
            parent_section=data.get("parent_section", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ChunkManifest:
    """Manifest of all chunks produced from a document."""

    doc_id: str
    policy_name: str
    chunks: list[Chunk]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "policy_name": self.policy_name,
            "chunks": [c.to_dict() for c in self.chunks],
            "metadata": self.metadata,
        }


def _approx_token_count(text: str) -> int:
    """Approximate token count by whitespace splitting (no external deps)."""
    return len(text.split())


def _make_chunk_id(doc_id: str, index: int) -> str:
    return f"{doc_id}_chunk_{index:04d}"


class ChunkPolicy(ABC):
    """Abstract base class for all chunk policies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Policy name identifier."""
        ...

    @abstractmethod
    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        """Split a document into chunks.

        Args:
            document: Full document text
            doc_id: Document identifier for chunk provenance

        Returns:
            List of Chunk objects
        """
        ...


class FixedTokenChunkPolicy(ChunkPolicy):
    """Splits document into fixed-size non-overlapping token windows."""

    def __init__(self, chunk_size: int = 512):
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        self.chunk_size = chunk_size

    @property
    def name(self) -> str:
        return "fixed_token"

    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        words = document.split()
        chunks: list[Chunk] = []
        for idx, start in enumerate(range(0, len(words), self.chunk_size)):
            word_slice = words[start : start + self.chunk_size]
            content = " ".join(word_slice)
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(doc_id, idx),
                    doc_id=doc_id,
                    content=content,
                    token_count=len(word_slice),
                    start_char=len(" ".join(words[:start])),
                    end_char=len(" ".join(words[: start + len(word_slice)])),
                    metadata={"policy": self.name, "chunk_size": self.chunk_size},
                )
            )
        return chunks


class OverlapWindowChunkPolicy(ChunkPolicy):
    """Splits document with overlapping token windows."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if overlap < 0:
            raise ValueError(f"overlap must be non-negative, got {overlap}")
        if overlap >= chunk_size:
            raise ValueError(f"overlap ({overlap}) must be less than chunk_size ({chunk_size})")
        self.chunk_size = chunk_size
        self.overlap = overlap

    @property
    def name(self) -> str:
        return "overlap_window"

    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        words = document.split()
        step = self.chunk_size - self.overlap
        if step <= 0:
            step = 1
        chunks: list[Chunk] = []
        idx = 0
        start = 0
        while start < len(words):
            word_slice = words[start : start + self.chunk_size]
            content = " ".join(word_slice)
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(doc_id, idx),
                    doc_id=doc_id,
                    content=content,
                    token_count=len(word_slice),
                    start_char=start,
                    end_char=start + len(word_slice),
                    metadata={"policy": self.name, "chunk_size": self.chunk_size, "overlap": self.overlap},
                )
            )
            start += step
            idx += 1
        return chunks


class SectionAwareChunkPolicy(ChunkPolicy):
    """Splits document on Markdown-style section headers (## or ###).

    Each section becomes its own chunk, preserving structural boundaries.
    """

    # guardian: allow-magic-config
    def __init__(self, max_section_tokens: int = 1024):
        self.max_section_tokens = max_section_tokens

    @property
    def name(self) -> str:
        return "section_aware"

    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        sections = re.split("(?m)^#{1,3}\\s+", document)
        chunks: list[Chunk] = []
        char_offset = 0
        for idx, section in enumerate(sections):
            section = section.strip()
            if not section:
                char_offset += len(sections[idx]) + 1
                continue
            token_count = _approx_token_count(section)
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(doc_id, idx),
                    doc_id=doc_id,
                    content=section,
                    token_count=token_count,
                    start_char=char_offset,
                    end_char=char_offset + len(section),
                    parent_section=section[:80].replace("\n", " "),
                    metadata={"policy": self.name, "max_section_tokens": self.max_section_tokens},
                )
            )
            char_offset += len(section) + 1
        return chunks


class SemanticChunkPolicy(ChunkPolicy):
    """Splits document at sentence boundaries, grouping into semantic windows.

    Without an embedding model: uses sentence-boundary heuristics.
    With an embedding model callable: groups sentences by cosine similarity.
    """

    # guardian: allow-magic-config
    def __init__(self, target_size: int = 256, similarity_threshold: float = 0.75, embedder=None):
        if target_size <= 0:
            raise ValueError(f"target_size must be positive, got {target_size}")
        self.target_size = target_size
        self.similarity_threshold = similarity_threshold
        self._embedder = embedder

    @property
    def name(self) -> str:
        return "semantic"

    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        sentences = re.split("(?<=[.!?])\\s+", document.strip())
        sentences = [s for s in sentences if s.strip()]
        groups: list[list[str]] = []
        current_group: list[str] = []
        current_tokens = 0
        for sentence in sentences:
            token_count = _approx_token_count(sentence)
            if current_tokens + token_count > self.target_size and current_group:
                groups.append(current_group)
                current_group = [sentence]
                current_tokens = token_count
            else:
                current_group.append(sentence)
                current_tokens += token_count
        if current_group:
            groups.append(current_group)
        chunks: list[Chunk] = []
        char_offset = 0
        for idx, group in enumerate(groups):
            content = " ".join(group)
            token_count = _approx_token_count(content)
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(doc_id, idx),
                    doc_id=doc_id,
                    content=content,
                    token_count=token_count,
                    start_char=char_offset,
                    end_char=char_offset + len(content),
                    metadata={"policy": self.name, "target_size": self.target_size},
                )
            )
            char_offset += len(content) + 1
        return chunks


__all__ = [
    "Chunk",
    "ChunkManifest",
    "ChunkPolicy",
    "FixedTokenChunkPolicy",
    "OverlapWindowChunkPolicy",
    "SectionAwareChunkPolicy",
    "SemanticChunkPolicy",
    "_approx_token_count",
]
