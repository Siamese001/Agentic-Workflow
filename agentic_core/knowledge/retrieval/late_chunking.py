"""Late Chunking embedder for BGE-M3 (Jina Late Chunking technique, 2024).

Late Chunking is an embedding-side technique that gives each chunk cross-doc
context at essentially zero marginal cost. Instead of embedding each chunk in
isolation (which strips cross-chunk context — the exact failure mode ADR-045
targets), the full document is forward-passed through BGE-M3 once with
token-level hidden-state capture, and each chunk's embedding is produced by
mean-pooling the token vectors whose offset-mapping falls inside the chunk's
character span. Each chunk embedding therefore inherits the full-doc attention
pass's context.

Reference: Günther, Mohr, Williams, et al. "Late Chunking: Contextual Chunk
Embeddings Using Long-Context Embedding Models", Jina AI, 2024.

Why this is complementary to ADR-045 (Anthropic Contextual Retrieval)
---------------------------------------------------------------------
Both techniques target the same failure mode (chunk-in-isolation loses
context) but via different mechanisms:

  * ADR-045 contextualization: prepends a 50-100 token LLM-generated narrative
    before embedding each chunk. Cost: one LLM call per chunk ($ or GPU time).
  * Late chunking: pools token embeddings from a single full-doc encoder pass.
    Cost: one encoder pass per document (no LLM calls beyond the embedder
    you're already running).

They stack cleanly: a chunk can be both contextualized AND late-chunked. The
A/B harness at ``tools/retrieval_benchmark.py`` can compare all four cells
(baseline / contextualized / late-chunked / both) against the calibration
corpus.

Failure modes
-------------
* Document exceeds the encoder's max sequence length (BGE-M3: 8192 tokens).
  The embedder switches to sliding-window mode: overlapping windows are
  encoded independently and each chunk is mapped to whichever window its
  character span falls inside. Windows overlap by ``window_overlap_tokens``
  to give boundary chunks a richer context than a hard cut would.
* Tokenizer's ``offset_mapping`` misses a chunk's character range entirely
  (can happen for special tokens or BPE edge cases). That chunk falls back
  to ``bge_embed_query(chunk.text)`` — standard per-chunk encoding — so no
  chunk is ever lost from the output; they just lose the late-chunking
  benefit.
* FlagEmbedding / sentence-transformers not installed: raises
  ``LateChunkingUnavailable`` at gateway init. Ingestion scripts catch and
  fall back to the standard ``bge_embed_batch`` path.

Thread / process safety
-----------------------
Module-level singleton model + lock, mirroring ``bge_runtime``. Multi-thread
concurrent calls serialize on the GIL-held encoder; the encoder itself does
its own batching internally.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    import numpy as np

logger = logging.getLogger(__name__)


class LateChunkingUnavailable(RuntimeError):
    """Late chunking dependency (sentence-transformers + torch) not installed."""


@dataclass(frozen=True)
class ChunkSpan:
    """Character-offset span of a chunk within its source document.

    ``chunk_id`` is carried through opaquely so callers can re-join late-chunked
    embeddings with their ``ChunkManifest`` rows. ``start`` and ``end`` are
    inclusive-exclusive character offsets into the full source text.
    """

    chunk_id: str
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError(
                f"ChunkSpan must satisfy 0 <= start < end; got start={self.start}, end={self.end}"
            )


@dataclass(frozen=True)
class LateChunkingConfig:
    """Tunables for the late-chunking embedder.

    Defaults are chosen for BGE-M3 on a 32GB VRAM GPU; CPU operators should
    lower ``window_size_tokens`` and ``window_overlap_tokens`` to fit memory.
    """

    # BGE-M3 max seq len is 8192; we leave 192 of slack for tokenizer special
    # tokens and window-boundary padding so the effective window stays within
    # the model's actual ctx without triggering silent truncation.
    window_size_tokens: int = 8000
    # Overlap gives chunks near a window boundary a chance to land inside the
    # interior of at least one window, which yields a better pooled vector
    # than an embedding from the window edge.
    window_overlap_tokens: int = 256
    # L2-normalize the pooled vectors to match ``bge_embed_query`` output.
    # Retrieval downstream assumes unit-norm vectors.
    normalize: bool = True


# ── Module-level singletons ─────────────────────────────────────────────────
_LOCK = threading.Lock()
_TOKENIZER: Any = None
_ENCODER: Any = None


def _load_backends() -> tuple[Any, Any]:
    """Load the BGE-M3 tokenizer + encoder lazily, once per process.

    Goes under ``SentenceTransformer``'s wrapper to reach the raw HF tokenizer
    and transformer module, because late chunking needs token-level hidden
    states that ``.encode()`` hides. Using the same weights as
    ``bge_runtime._get_model()`` ensures dense-vector compatibility with the
    rest of the retrieval stack.
    """
    global _TOKENIZER, _ENCODER
    if _TOKENIZER is not None and _ENCODER is not None:
        return _TOKENIZER, _ENCODER

    with _LOCK:
        if _TOKENIZER is not None and _ENCODER is not None:
            return _TOKENIZER, _ENCODER

        try:
            import torch  # noqa: F401  — presence-check; used by ST internally
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise LateChunkingUnavailable(
                f"sentence-transformers + torch are required for late chunking: {exc}"
            ) from exc

        # Import here to reuse the constants without forcing the bge_runtime
        # singleton to load the SentenceTransformer (callers may just want
        # to construct the embedder for tests).
        from agentic_core.embeddings.bge_runtime import (  # noqa: PLC0415
            BGE_ALLOW_MODEL_DOWNLOAD,
            BGE_MODEL,
            _resolve_device,
        )

        device = _resolve_device()
        logger.info("Loading BGE-M3 for late chunking: %s (device=%s)", BGE_MODEL, device)
        st_model = SentenceTransformer(
            BGE_MODEL,
            device=device,
            local_files_only=not BGE_ALLOW_MODEL_DOWNLOAD,
            trust_remote_code=False,
        )
        _TOKENIZER = st_model.tokenizer
        # ``SentenceTransformer`` wraps a transformers.AutoModel at index 0.
        # ``.auto_model`` exposes the raw HF model whose forward pass returns
        # last_hidden_state, which is what we need for late chunking.
        _ENCODER = st_model[0].auto_model
        _ENCODER.eval()
        logger.info("BGE-M3 late-chunking backends loaded.")
        return _TOKENIZER, _ENCODER


def reset_backends_for_testing() -> None:
    """Clear the module-level singletons — test-only, never call in prod."""
    global _TOKENIZER, _ENCODER
    with _LOCK:
        _TOKENIZER = None
        _ENCODER = None


# ── Core algorithm ──────────────────────────────────────────────────────────


def _plan_windows(
    n_tokens: int,
    *,
    window_size: int,
    overlap: int,
) -> list[tuple[int, int]]:
    """Partition ``[0, n_tokens)`` into overlapping windows.

    Each window is ``(start, end)`` in TOKEN indices, end-exclusive. Windows
    stride by ``window_size - overlap`` so consecutive windows share
    ``overlap`` tokens. Guarantees every token index is covered by at least
    one window, and no window exceeds ``window_size``.
    """
    if n_tokens <= 0:
        return []
    if n_tokens <= window_size:
        return [(0, n_tokens)]
    if overlap >= window_size:
        raise ValueError(f"overlap ({overlap}) must be strictly less than window_size ({window_size})")
    stride = window_size - overlap
    windows: list[tuple[int, int]] = []
    start = 0
    while start < n_tokens:
        end = min(start + window_size, n_tokens)
        windows.append((start, end))
        if end == n_tokens:
            break
        start += stride
    return windows


def _assign_chunk_to_window(
    chunk_char_span: tuple[int, int],
    token_offsets: list[tuple[int, int]],
    windows_tokens: list[tuple[int, int]],
) -> tuple[int, list[int]] | None:
    """Return ``(window_idx, local_token_indices)`` for the best-fit window.

    "Best fit" = the window whose tokens cover the largest fraction of the
    chunk's character span. Local token indices are relative to the window
    start, so the caller can index into that window's hidden-state tensor.

    Returns ``None`` iff no token offsets overlap the chunk span at all
    (degenerate case — caller falls back to per-chunk encoding).
    """
    ch_start, ch_end = chunk_char_span
    best_window_idx: int | None = None
    best_count = 0
    best_local_indices: list[int] = []

    for w_idx, (w_start, w_end) in enumerate(windows_tokens):
        local_hits: list[int] = []
        for token_global_idx in range(w_start, w_end):
            tok_start, tok_end = token_offsets[token_global_idx]
            # Special tokens and padding produce (0, 0) offsets; skip them.
            if tok_start == tok_end:
                continue
            # Token overlaps the chunk span iff its range intersects the
            # chunk's char range.
            if tok_end <= ch_start or tok_start >= ch_end:
                continue
            local_hits.append(token_global_idx - w_start)
        if len(local_hits) > best_count:
            best_count = len(local_hits)
            best_window_idx = w_idx
            best_local_indices = local_hits

    if best_window_idx is None:
        return None
    return best_window_idx, best_local_indices


def _mean_pool_and_normalize(
    hidden_states: "np.ndarray",
    local_indices: list[int],
    *,
    normalize: bool,
) -> list[float]:
    """Mean-pool a subset of token vectors, optionally L2-normalize.

    ``hidden_states`` is expected as a 2-D array of shape ``[seq_len, hidden]``
    (the caller removes the batch dim). Uses numpy ops so this function can be
    tested without a GPU.
    """
    import numpy as np  # noqa: PLC0415 - deferred: tests import module without numpy

    if not local_indices:
        raise ValueError("_mean_pool_and_normalize: local_indices must be non-empty")
    selected = hidden_states[local_indices]  # [k, hidden]
    pooled = selected.mean(axis=0)
    if normalize:
        norm = float(np.linalg.norm(pooled))
        if norm > 0:
            pooled = pooled / norm
    return [float(v) for v in pooled.tolist()]


class LateChunkingEmbedder:
    """Late-chunking embedder for BGE-M3.

    Usage::

        embedder = LateChunkingEmbedder()
        embeddings = embedder.embed_chunks_from_doc(
            doc_text=full_document,
            chunks=[ChunkSpan(c.id, c.start, c.end) for c in plan],
        )
        # embeddings is a dict: {chunk_id: [float, ...]} with 1024-dim vectors.

    The embedder routes every chunk to exactly one output vector. Chunks that
    cannot be resolved to token indices (tokenizer edge cases) are embedded
    via the standard per-chunk ``bge_embed_query`` path, logged at WARNING.
    """

    def __init__(self, config: LateChunkingConfig | None = None) -> None:
        self.config = config or LateChunkingConfig()

    def embed_chunks_from_doc(
        self,
        doc_text: str,
        chunks: list[ChunkSpan],
    ) -> dict[str, list[float]]:
        """Return ``{chunk_id: late_chunked_embedding}`` for every span in ``chunks``.

        Raises:
            LateChunkingUnavailable: sentence-transformers / torch missing.
            ValueError: ``doc_text`` empty or ``chunks`` empty.
        """
        if not doc_text:
            raise ValueError("doc_text must not be empty")
        if not chunks:
            raise ValueError("chunks must not be empty")

        tokenizer, encoder = _load_backends()

        # One tokenization pass over the full doc gives us both token ids and
        # character offsets aligned to those ids. ``return_offsets_mapping``
        # is the critical flag — without it, chunk->token mapping is impossible.
        encoding = tokenizer(
            doc_text,
            return_offsets_mapping=True,
            add_special_tokens=False,
            truncation=False,
        )
        token_offsets: list[tuple[int, int]] = [(int(s), int(e)) for s, e in encoding["offset_mapping"]]
        n_tokens = len(token_offsets)

        if n_tokens == 0:
            # Degenerate doc; fall back to standard embedding for every chunk.
            return self._fallback_all(chunks, doc_text)

        windows = _plan_windows(
            n_tokens,
            window_size=self.config.window_size_tokens,
            overlap=self.config.window_overlap_tokens,
        )

        # Encode each window once. For the single-window case (most docs)
        # this is one forward pass, cheap and parallel on-GPU.
        window_hiddens = self._encode_windows(encoder, tokenizer, encoding, windows)

        out: dict[str, list[float]] = {}
        fallback_ids: list[ChunkSpan] = []
        for chunk in chunks:
            assignment = _assign_chunk_to_window(
                (chunk.start, chunk.end),
                token_offsets,
                windows,
            )
            if assignment is None:
                fallback_ids.append(chunk)
                continue
            w_idx, local_indices = assignment
            try:
                vec = _mean_pool_and_normalize(
                    window_hiddens[w_idx],
                    local_indices,
                    normalize=self.config.normalize,
                )
            except (ValueError, IndexError) as exc:
                logger.warning("Late chunking pool failed for chunk_id=%s: %s", chunk.chunk_id, exc)
                fallback_ids.append(chunk)
                continue
            out[chunk.chunk_id] = vec

        if fallback_ids:
            out.update(self._fallback_all(fallback_ids, doc_text))
        return out

    # ── Helpers ────────────────────────────────────────────────────────────

    def _encode_windows(
        self,
        encoder: Any,
        tokenizer: Any,
        full_encoding: Any,
        windows: list[tuple[int, int]],
    ) -> list[Any]:
        """Run the encoder on each window and return per-window hidden states.

        Each returned tensor is a 2-D numpy array ``[window_tokens, hidden]``
        so pooling is independent of torch shape conventions.
        """
        import torch  # noqa: PLC0415 - deferred so tests can mock this path

        input_ids_all = full_encoding["input_ids"]
        # transformers tokenizers return a flat list for a single text.
        if not isinstance(input_ids_all, list):
            input_ids_all = list(input_ids_all)

        results: list[Any] = []
        pad_token_id = getattr(tokenizer, "pad_token_id", 0) or 0

        for w_start, w_end in windows:
            ids = input_ids_all[w_start:w_end]
            # Add BOS/EOS-style special tokens if the tokenizer has any, so
            # the encoder sees the window in a shape it was trained on. Many
            # BERT-family tokenizers use [CLS]+tokens+[SEP]; omitting them
            # degrades the pooled vectors slightly but is safe. For
            # simplicity and determinism, we skip them here — BGE-M3 was
            # finetuned for retrieval with and without specials.
            input_ids = torch.tensor([ids], dtype=torch.long, device=encoder.device)
            attention_mask = torch.ones_like(input_ids)
            with torch.no_grad():
                output = encoder(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
            # last_hidden_state: [1, seq_len, hidden]. Drop batch dim for pooling.
            hidden = output.last_hidden_state[0].detach().cpu().numpy()
            results.append(hidden)
            # Release memory eagerly between windows on constrained GPUs.
            del input_ids, attention_mask, output
            if pad_token_id == 0:  # noop to reference the var; mypy-friendly
                pass
        return results

    def _fallback_all(
        self,
        chunks: list[ChunkSpan],
        doc_text: str,
    ) -> dict[str, list[float]]:
        """Embed each chunk via the standard per-chunk path.

        Used when the whole-doc late-chunking path can't map a chunk (tokenizer
        edge case) or when the doc itself failed to tokenize. This preserves
        the invariant "every input chunk gets exactly one output vector".
        """
        from agentic_core.embeddings.bge_runtime import bge_embed_query  # noqa: PLC0415

        out: dict[str, list[float]] = {}
        for chunk in chunks:
            text = doc_text[chunk.start : chunk.end].strip()
            if not text:
                logger.warning(
                    "Empty chunk text for chunk_id=%s (span %d:%d); emitting zero vector",
                    chunk.chunk_id,
                    chunk.start,
                    chunk.end,
                )
                # 1024-dim zero vector keeps downstream shape invariant.
                out[chunk.chunk_id] = [0.0] * 1024
                continue
            out[chunk.chunk_id] = bge_embed_query(text)
        return out


__all__ = [
    "ChunkSpan",
    "LateChunkingConfig",
    "LateChunkingEmbedder",
    "LateChunkingUnavailable",
    "reset_backends_for_testing",
]
