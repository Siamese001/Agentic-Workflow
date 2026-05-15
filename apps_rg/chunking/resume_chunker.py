"""apps_rg resume chunker — split structured resume into prompt-sized chunks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Optional

__all__ = [
    "ResumeChunk",
    "ResumeChunker",
    "ChunkerConfig",
    "DEFAULT_CHUNKER_CONFIG",
]


@dataclass(frozen=True)
class ResumeChunk:
    """A single chunk of resume content for prompt assembly."""

    chunk_id: str
    section_id: str
    content: str
    token_estimate: int = 0
    chunk_index: int = 0
    total_chunks_in_section: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_last_chunk(self) -> bool:
        return self.chunk_index == self.total_chunks_in_section - 1


@dataclass(frozen=True)
class ChunkerConfig:
    """Configuration for the ResumeChunker."""

    max_tokens_per_chunk: int = 800
    overlap_tokens: int = 50
    min_chunk_tokens: int = 20
    chars_per_token_estimate: float = 4.0

    def estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text) / self.chars_per_token_estimate))


DEFAULT_CHUNKER_CONFIG = ChunkerConfig()


class ResumeChunker:
    """Split a structured resume into prompt-sized chunks.

    Parameters
    ----------
    config:
        Chunker configuration; defaults to DEFAULT_CHUNKER_CONFIG.
    """

    def __init__(self, config: Optional[ChunkerConfig] = None) -> None:
        self.config = config or DEFAULT_CHUNKER_CONFIG

    def chunk_section(
        self,
        section_id: str,
        content: str,
    ) -> list[ResumeChunk]:
        """Split a section's content into ResumeChunks."""
        if not content.strip():
            return [
                ResumeChunk(
                    chunk_id=f"{section_id}_0",
                    section_id=section_id,
                    content="",
                    token_estimate=0,
                    chunk_index=0,
                    total_chunks_in_section=1,
                )
            ]

        max_chars = int(
            self.config.max_tokens_per_chunk * self.config.chars_per_token_estimate
        )
        overlap = int(self.config.overlap_tokens * self.config.chars_per_token_estimate)

        chunks: list[str] = []
        start = 0
        while start < len(content):
            end = min(start + max_chars, len(content))
            chunks.append(content[start:end])
            if end >= len(content):
                break
            start = end - overlap

        total = len(chunks)
        return [
            ResumeChunk(
                chunk_id=f"{section_id}_{i}",
                section_id=section_id,
                content=chunk_text,
                token_estimate=self.config.estimate_tokens(chunk_text),
                chunk_index=i,
                total_chunks_in_section=total,
            )
            for i, chunk_text in enumerate(chunks)
        ]

    def chunk_resume(
        self,
        sections: dict[str, str],
    ) -> dict[str, list[ResumeChunk]]:
        """Chunk all sections of a resume.

        Parameters
        ----------
        sections:
            Mapping of section_id → content string.

        Returns
        -------
        dict[str, list[ResumeChunk]]
            Mapping of section_id → list of chunks.
        """
        return {
            section_id: self.chunk_section(section_id, content)
            for section_id, content in sections.items()
        }

    def iter_all_chunks(
        self,
        sections: dict[str, str],
    ) -> Iterator[ResumeChunk]:
        """Yield all chunks across all sections in order."""
        for section_id, content in sections.items():
            yield from self.chunk_section(section_id, content)
