"""Chunking Modes - Pipeline B Step 2

Implements spec-compliant chunking modes from Agentic Retrieval Models v9:
- FixedToken: Fixed-size token chunks
- OverlapWindow: Sliding window with overlap
- SectionAware: Section/heading-based chunking
- SemanticObject: Semantic unit chunking

Provides multiple chunking strategies for different document types.
"""

from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)
from tqdm import tqdm

EmbedderFn = Callable[[list[str]], list[list[float]]]
BreakpointType = Literal["percentile", "stdev", "iqr", "gradient"]


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


def _cosine_distance(a: list[float], b: list[float]) -> float:
    """Cosine distance = 1 - cosine similarity.

    Returns 1.0 (max distance) for zero-norm inputs — safe for empty/degenerate
    embeddings without raising.
    """
    if not a or not b or len(a) != len(b):
        return 1.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 1.0
    sim = dot / (na * nb)
    # Clamp against floating-point drift that can push sim slightly outside [-1, 1].
    sim = max(-1.0, min(1.0, sim))
    return 1.0 - sim


def _percentile(values: list[float], pct: float) -> float:
    """Compute percentile (0-100) using linear interpolation.

    Pure-Python to avoid numpy import cost in a hot chunking path.
    """
    if not values:
        return 0.0
    pct = max(0.0, min(100.0, pct))
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (pct / 100.0)
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return s[lo]
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


class EmbeddingSemanticChunker(ChunkingStrategy):
    """Embedding-cosine semantic chunking.

    Implements the canonical LangChain / LlamaIndex pattern:

      1. Split text into sentences.
      2. Group sentences with a ``buffer_size`` window (each group = the
         sentence plus ``buffer_size`` neighbours on each side) to smooth out
         one-sentence topic noise.
      3. Embed every group via the injected ``embedder``.
      4. Compute cosine distance between adjacent group embeddings.
      5. Detect breakpoints where distance crosses a threshold determined by
         ``breakpoint_type`` (percentile / stdev / iqr / gradient).
      6. Emit chunks between breakpoints, clamped by ``min_chunk_chars`` /
         ``max_chunk_chars``.

    This complements — it does not replace — the existing regex-based
    ``SemanticObjectChunker`` (structural) and ``late_chunking.py`` (post-hoc
    pooling of long-context embeddings). For documents < 8k tokens with high
    semantic density, prefer ``late_chunking``. For documents where sentence-
    level topic shifts matter (tech docs, support transcripts, FAQ), this
    chunker gives LangChain ``SemanticChunker`` / LlamaIndex
    ``SemanticSplitterNodeParser`` parity.

    Args:
        embedder: Callable mapping ``list[str] -> list[list[float]]``. Injected
            so tests can pass a deterministic stub and production can wire the
            canonical BGE-m3 embedder without this class knowing about models.
        breakpoint_type: Thresholding mode for cosine distances.
        breakpoint_threshold: Threshold parameter whose meaning depends on
            ``breakpoint_type``:
              - ``percentile``: cut above this percentile (default 95.0)
              - ``stdev``: cut above mean + N*stdev (default 3.0)
              - ``iqr``: cut above Q3 + N*IQR (default 1.5)
              - ``gradient``: cut above Nth percentile of distance gradients
                (default 95.0)
        buffer_size: Sentence-window radius when building groups. 1 means
            "this sentence + 1 on each side". 0 means "bare sentences".
        min_chunk_chars: Chunks smaller than this are merged forward.
        max_chunk_chars: Hard cap; chunks larger than this are split at the
            next sentence boundary regardless of similarity.
    """

    def __init__(
        self,
        embedder: EmbedderFn,
        breakpoint_type: BreakpointType = "percentile",
        breakpoint_threshold: float | None = None,
        buffer_size: int = 1,
        min_chunk_chars: int = 100,
        max_chunk_chars: int = 2000,
    ):
        if embedder is None:
            raise ValueError("EmbeddingSemanticChunker requires a non-None embedder")
        if buffer_size < 0:
            raise ValueError("buffer_size must be >= 0")
        if min_chunk_chars < 0 or max_chunk_chars <= 0:
            raise ValueError("chunk char bounds must be positive")
        if min_chunk_chars >= max_chunk_chars:
            raise ValueError("min_chunk_chars must be < max_chunk_chars")

        self.embedder = embedder
        self.breakpoint_type: BreakpointType = breakpoint_type
        # Sensible defaults per breakpoint type (match LangChain SemanticChunker).
        if breakpoint_threshold is None:
            defaults: dict[str, float] = {
                "percentile": 95.0,
                "stdev": 3.0,
                "iqr": 1.5,
                "gradient": 95.0,
            }
            breakpoint_threshold = defaults[breakpoint_type]
        self.breakpoint_threshold = breakpoint_threshold
        self.buffer_size = buffer_size
        self.min_chunk_chars = min_chunk_chars
        self.max_chunk_chars = max_chunk_chars

    # ------------------------------------------------------------------
    # Sentence splitting — reuses the SemanticObjectChunker regex so both
    # chunkers agree on sentence boundaries.
    # ------------------------------------------------------------------
    _SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

    def _split_sentences(self, text: str) -> list[tuple[int, int, str]]:
        """Return ``[(start, end, sentence)]`` tuples."""
        out: list[tuple[int, int, str]] = []
        pos = 0
        # Split on paragraph boundaries first to preserve structure, then
        # sentence-split within each paragraph.
        for para in re.split(r"\n\n+", text):
            if not para.strip():
                pos += len(para) + 2
                continue
            sentences = self._SENTENCE_RE.split(para)
            local = pos
            for sent in sentences:
                if not sent.strip():
                    local += len(sent) + 1
                    continue
                start = local
                end = local + len(sent)
                out.append((start, end, sent.strip()))
                local = end + 1  # +1 for the separator
            pos += len(para) + 2
        return out

    def _group_sentences(
        self, sentences: list[tuple[int, int, str]]
    ) -> list[str]:
        """Merge each sentence with ``buffer_size`` neighbours on each side."""
        n = len(sentences)
        groups: list[str] = []
        for i in range(n):
            lo = max(0, i - self.buffer_size)
            hi = min(n, i + self.buffer_size + 1)
            groups.append(" ".join(s[2] for s in sentences[lo:hi]))
        return groups

    # ------------------------------------------------------------------
    # Breakpoint detection
    # ------------------------------------------------------------------
    def _compute_breakpoints(self, distances: list[float]) -> list[int]:
        """Return indices *after which* a chunk boundary should be placed."""
        if not distances:
            return []

        if self.breakpoint_type == "percentile":
            cutoff = _percentile(distances, self.breakpoint_threshold)
            return [i for i, d in enumerate(distances) if d > cutoff]

        if self.breakpoint_type == "stdev":
            mean = sum(distances) / len(distances)
            var = sum((d - mean) ** 2 for d in distances) / max(1, len(distances))
            sd = math.sqrt(var)
            cutoff = mean + self.breakpoint_threshold * sd
            return [i for i, d in enumerate(distances) if d > cutoff]

        if self.breakpoint_type == "iqr":
            q1 = _percentile(distances, 25.0)
            q3 = _percentile(distances, 75.0)
            iqr = q3 - q1
            cutoff = q3 + self.breakpoint_threshold * iqr
            return [i for i, d in enumerate(distances) if d > cutoff]

        if self.breakpoint_type == "gradient":
            # Second-derivative-style: look at change in distance between
            # consecutive gaps, cut above the Nth percentile of the gradient.
            if len(distances) < 2:
                return []
            gradients = [
                abs(distances[i + 1] - distances[i]) for i in range(len(distances) - 1)
            ]
            cutoff = _percentile(gradients, self.breakpoint_threshold)
            return [i for i, g in enumerate(gradients) if g > cutoff]

        # Unreachable under Literal typing; defensive fallback.
        return []

    # ------------------------------------------------------------------
    # Chunk assembly
    # ------------------------------------------------------------------
    def _assemble_chunks(
        self,
        sentences: list[tuple[int, int, str]],
        breakpoints: list[int],
        doc_id: str,
    ) -> list[Chunk]:
        """Emit ``Chunk`` objects from sentence runs delimited by breakpoints."""
        if not sentences:
            return []

        # Convert breakpoint indices (distance-array indices, one less than
        # sentence count) into sentence-end indices.
        cut_after = sorted(set(breakpoints))
        runs: list[list[tuple[int, int, str]]] = []
        current: list[tuple[int, int, str]] = []
        for i, sent in enumerate(sentences):
            current.append(sent)
            if i in cut_after:
                runs.append(current)
                current = []
        if current:
            runs.append(current)

        # Merge runs below min_chunk_chars into the next run; split runs
        # above max_chunk_chars at sentence boundaries.
        merged: list[list[tuple[int, int, str]]] = []
        carry: list[tuple[int, int, str]] = []
        for run in runs:
            combined = carry + run
            text_len = sum(len(s[2]) + 1 for s in combined)
            if text_len < self.min_chunk_chars:
                carry = combined
                continue
            carry = []
            merged.append(combined)
        if carry:
            if merged:
                merged[-1].extend(carry)
            else:
                merged.append(carry)

        # Apply max_chunk_chars split.
        final_runs: list[list[tuple[int, int, str]]] = []
        for run in merged:
            acc: list[tuple[int, int, str]] = []
            acc_len = 0
            for sent in run:
                s_len = len(sent[2]) + 1
                if acc and acc_len + s_len > self.max_chunk_chars:
                    final_runs.append(acc)
                    acc = [sent]
                    acc_len = s_len
                else:
                    acc.append(sent)
                    acc_len += s_len
            if acc:
                final_runs.append(acc)

        chunks: list[Chunk] = []
        for idx, run in enumerate(final_runs):
            content = " ".join(s[2] for s in run)
            start = run[0][0]
            end = run[-1][1]
            chunks.append(
                Chunk(
                    id=f"{doc_id}_embsem_{idx}",
                    content=content,
                    start_pos=start,
                    end_pos=end,
                    chunk_type="embedding_semantic",
                    metadata={
                        "strategy": "embedding_semantic",
                        "breakpoint_type": self.breakpoint_type,
                        "breakpoint_threshold": self.breakpoint_threshold,
                        "buffer_size": self.buffer_size,
                        "sentence_count": len(run),
                    },
                )
            )
        return chunks

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def chunk(self, text: str, doc_id: str = "") -> list[Chunk]:
        """Chunk text using embedding-cosine semantic boundary detection."""
        _emit_records_execution_trace(
            f"chunk_embedding_semantic_{doc_id}",
            LayerSegment.L2_EXECUTION,
            "EmbeddingSemanticChunker.chunk",
        )

        if not text or not text.strip():
            return []

        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            # Degenerate: single sentence → single chunk.
            return self._assemble_chunks(sentences, [], doc_id)

        groups = self._group_sentences(sentences)
        embeddings = self.embedder(groups)
        if len(embeddings) != len(groups):
            raise ValueError(
                f"embedder returned {len(embeddings)} vectors for {len(groups)} groups"
            )

        distances = [
            _cosine_distance(embeddings[i], embeddings[i + 1])
            for i in range(len(embeddings) - 1)
        ]
        breakpoints = self._compute_breakpoints(distances)
        return self._assemble_chunks(sentences, breakpoints, doc_id)


def _build_sentence_transformer_embedder(model_name: str) -> EmbedderFn:
    """Lazy-load a sentence-transformers model and return an EmbedderFn.

    Imports happen inside the function so the rest of this module stays
    free of the heavy ML dependency. Raises ``RuntimeError`` (not
    ``ImportError``) so production callers get a single, actionable
    message instead of a swallowed import error.
    """
    try:
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers is required for the default "
            "embedding_semantic chunker. Install it with "
            "`pip install sentence-transformers`, or pass a custom "
            "embedder to ChunkingEngine.bootstrap_embedding_semantic()."
        ) from exc

    model = SentenceTransformer(model_name)

    def _embed(texts: list[str]) -> list[list[float]]:
        # ``convert_to_numpy=True`` is the default; ``.tolist()`` materialises
        # the result so the chunker stays numpy-free at the boundary.
        vectors = model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return [list(map(float, v)) for v in vectors]

    return _embed


class ChunkingEngine:
    """Unified chunking engine with strategy selection.

    Automatically selects appropriate chunking strategy based on document type.
    """

    STRATEGIES = {
        "fixed_token": FixedTokenChunker,
        "overlap_window": OverlapWindowChunker,
        "section_aware": SectionAwareChunker,
        "semantic_object": SemanticObjectChunker,
        # "embedding_semantic" requires an embedder and must be registered via
        # register_chunker(); instantiating from a zero-arg factory would fail.
    }

    def __init__(self, default_strategy: str = "semantic_object"):
        """Initialize chunking engine.

        Args:
            default_strategy: Default chunking strategy
        """
        self.default_strategy = default_strategy
        self._chunkers: dict[str, ChunkingStrategy] = {}

    def register_chunker(self, name: str, chunker: ChunkingStrategy) -> None:
        """Register a pre-constructed chunker under ``name``.

        Use this for strategies that require constructor dependencies the
        ``STRATEGIES`` zero-arg factory cannot provide — notably
        :class:`EmbeddingSemanticChunker`, which needs an injected embedder.
        """
        self._chunkers[name] = chunker

    def bootstrap_embedding_semantic(
        self,
        embedder: EmbedderFn | None = None,
        *,
        model_name: str = "BAAI/bge-m3",
        breakpoint_type: BreakpointType = "percentile",
        breakpoint_threshold: float | None = None,
        buffer_size: int = 1,
        min_chunk_chars: int = 100,
        max_chunk_chars: int = 2000,
    ) -> EmbeddingSemanticChunker:
        """Construct and register the ``embedding_semantic`` strategy.

        If ``embedder`` is None, lazy-imports ``sentence_transformers`` and
        wraps the supplied ``model_name`` as the embedder. Raises
        ``RuntimeError`` with an actionable message if sentence-transformers
        is not installed — never silently falls back.

        Returns the registered chunker so callers can poke at thresholds.
        """
        if embedder is None:
            embedder = _build_sentence_transformer_embedder(model_name)
        chunker = EmbeddingSemanticChunker(
            embedder=embedder,
            breakpoint_type=breakpoint_type,
            breakpoint_threshold=breakpoint_threshold,
            buffer_size=buffer_size,
            min_chunk_chars=min_chunk_chars,
            max_chunk_chars=max_chunk_chars,
        )
        self.register_chunker("embedding_semantic", chunker)
        return chunker

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
