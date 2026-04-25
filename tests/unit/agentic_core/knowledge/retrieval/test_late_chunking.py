"""Unit tests for agentic_core.knowledge.retrieval.late_chunking.

These tests exercise the Late Chunking algorithm (Jina 2024) without loading
BGE-M3 weights or torch — the tokenizer and encoder are mocked so the test
suite runs in <1s on CPU-only runners.

Test coverage:
    * ChunkSpan dataclass validation
    * _plan_windows: single-window, multi-window stride, overlap, edge cases
    * _assign_chunk_to_window: best-fit selection, null overlap, special tokens
    * _mean_pool_and_normalize: arithmetic + L2 norm invariant
    * LateChunkingEmbedder.embed_chunks_from_doc: happy path + fallback path
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make repo root importable when this test runs standalone.
_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.knowledge.retrieval import late_chunking as lc_module
from agentic_core.knowledge.retrieval.late_chunking import (
    ChunkSpan,
    LateChunkingConfig,
    LateChunkingEmbedder,
    _assign_chunk_to_window,
    _mean_pool_and_normalize,
    _plan_windows,
    reset_backends_for_testing,
)


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Clear module singletons between tests so mocks don't leak."""
    reset_backends_for_testing()
    yield
    reset_backends_for_testing()


# ---------------------------------------------------------------------------
# ChunkSpan
# ---------------------------------------------------------------------------


def test_chunk_span_accepts_valid_range():
    span = ChunkSpan(chunk_id="c1", start=0, end=100)
    assert span.chunk_id == "c1"
    assert span.end > span.start


def test_chunk_span_rejects_inverted_range():
    with pytest.raises(ValueError, match="start < end"):
        ChunkSpan(chunk_id="c1", start=50, end=10)


def test_chunk_span_rejects_empty_range():
    with pytest.raises(ValueError, match="start < end"):
        ChunkSpan(chunk_id="c1", start=10, end=10)


def test_chunk_span_rejects_negative_start():
    with pytest.raises(ValueError, match="start < end"):
        ChunkSpan(chunk_id="c1", start=-1, end=10)


# ---------------------------------------------------------------------------
# _plan_windows
# ---------------------------------------------------------------------------


def test_plan_windows_empty_input_returns_empty():
    assert _plan_windows(0, window_size=100, overlap=10) == []


def test_plan_windows_single_window_when_tokens_fit():
    """Doc shorter than window: exactly one window covering the whole doc."""
    assert _plan_windows(500, window_size=8000, overlap=256) == [(0, 500)]


def test_plan_windows_exact_fit_single_window():
    """Edge case: n_tokens == window_size. Must stay one window, not two."""
    assert _plan_windows(100, window_size=100, overlap=10) == [(0, 100)]


def test_plan_windows_multi_window_stride():
    """n_tokens > window_size: overlap-strided windows, each <= window_size."""
    windows = _plan_windows(1000, window_size=400, overlap=50)
    # stride = 400 - 50 = 350. Windows: [0,400), [350,750), [700,1000)
    assert windows == [(0, 400), (350, 750), (700, 1000)]


def test_plan_windows_every_token_covered():
    """Invariant: every token index in [0, n_tokens) is in at least one window."""
    n = 1000
    windows = _plan_windows(n, window_size=300, overlap=50)
    covered = set()
    for start, end in windows:
        covered.update(range(start, end))
    assert covered == set(range(n))


def test_plan_windows_rejects_overlap_ge_window_size():
    """Infinite-loop guard: overlap must be strictly less than window_size."""
    with pytest.raises(ValueError, match="overlap.*must be strictly less"):
        _plan_windows(1000, window_size=100, overlap=100)
    with pytest.raises(ValueError, match="overlap.*must be strictly less"):
        _plan_windows(1000, window_size=100, overlap=150)


# ---------------------------------------------------------------------------
# _assign_chunk_to_window
# ---------------------------------------------------------------------------


def _synthetic_token_offsets(n: int, stride: int = 5) -> list[tuple[int, int]]:
    """Return n tokens of width `stride` laid out contiguously from char 0."""
    return [(i * stride, (i + 1) * stride) for i in range(n)]


def test_assign_chunk_picks_window_with_most_token_overlap():
    """Chunk span maps to whichever window covers the most of its characters."""
    # 200 tokens each of 5 chars → doc spans char 0..1000.
    offsets = _synthetic_token_offsets(200, stride=5)
    # Two windows, [0,100) tokens = char 0..500 and [100,200) tokens = char 500..1000.
    windows = [(0, 100), (100, 200)]
    # Chunk at char 600..700 is entirely inside window 1.
    result = _assign_chunk_to_window((600, 700), offsets, windows)
    assert result is not None
    w_idx, local_indices = result
    assert w_idx == 1
    # Tokens 120..140 (global) → local 20..40 inside window 1.
    assert local_indices == list(range(20, 40))


def test_assign_chunk_skips_special_tokens_with_zero_offsets():
    """Tokenizer emits (0,0) offsets for special tokens; assignment must skip them."""
    offsets = [(0, 0), (0, 0), *_synthetic_token_offsets(10, stride=5), (0, 0)]
    windows = [(0, len(offsets))]
    # Chunk at char 10..30 covers synthetic tokens index 2..6 (offsets start
    # after the two special tokens at the front).
    result = _assign_chunk_to_window((10, 30), offsets, windows)
    assert result is not None
    _, local_indices = result
    # Tokens with offsets (10,15),(15,20),(20,25),(25,30) overlap char 10..30.
    # Global indices: 4, 5, 6, 7 → local (same as global here, window starts at 0).
    assert local_indices == [4, 5, 6, 7]


def test_assign_chunk_returns_none_when_no_overlap():
    """Chunk outside any token's char range → None, caller falls back."""
    offsets = _synthetic_token_offsets(10, stride=5)  # chars 0..50
    windows = [(0, 10)]
    assert _assign_chunk_to_window((1000, 2000), offsets, windows) is None


# ---------------------------------------------------------------------------
# _mean_pool_and_normalize
# ---------------------------------------------------------------------------


def test_mean_pool_produces_arithmetic_mean_when_not_normalized():
    np = pytest.importorskip("numpy")
    hidden = np.array(
        [
            [1.0, 2.0, 3.0],
            [3.0, 4.0, 5.0],
            [5.0, 6.0, 7.0],
        ]
    )
    # Pool tokens [0, 2] → rows 0 and 2 → mean = [3.0, 4.0, 5.0]
    result = _mean_pool_and_normalize(hidden, [0, 2], normalize=False)
    assert result == [3.0, 4.0, 5.0]


def test_mean_pool_normalizes_to_unit_length():
    np = pytest.importorskip("numpy")
    hidden = np.array([[3.0, 4.0]])  # norm=5
    result = _mean_pool_and_normalize(hidden, [0], normalize=True)
    # After L2-normalize: [3/5, 4/5]
    assert result == pytest.approx([0.6, 0.8])
    # Sanity: result is unit-norm
    norm = sum(v * v for v in result) ** 0.5
    assert norm == pytest.approx(1.0)


def test_mean_pool_handles_zero_vector_without_division_error():
    np = pytest.importorskip("numpy")
    # All zeros: normalization must not divide-by-zero; returns zeros unchanged.
    hidden = np.zeros((2, 3))
    result = _mean_pool_and_normalize(hidden, [0, 1], normalize=True)
    assert result == [0.0, 0.0, 0.0]


def test_mean_pool_raises_on_empty_indices():
    np = pytest.importorskip("numpy")
    hidden = np.ones((3, 4))
    with pytest.raises(ValueError, match="local_indices must be non-empty"):
        _mean_pool_and_normalize(hidden, [], normalize=False)


# ---------------------------------------------------------------------------
# LateChunkingEmbedder.embed_chunks_from_doc
# ---------------------------------------------------------------------------


@dataclass
class _FakeEncoding:
    """Duck-types the transformers BatchEncoding we consume."""

    input_ids: list[int]
    offset_mapping: list[tuple[int, int]]

    def __getitem__(self, key):
        return getattr(self, key)


def _install_fake_backends(
    token_offsets: list[tuple[int, int]],
    hidden_dim: int = 4,
) -> tuple[MagicMock, MagicMock]:
    """Install fake tokenizer + encoder into the module singletons.

    Encoder returns deterministic hidden states: row i = [i+1, 0, 0, 0] so
    each test can check the pooled output is the expected mean.
    """
    pytest.importorskip("numpy")
    import numpy as np

    fake_tokenizer = MagicMock()
    fake_tokenizer.pad_token_id = 0
    fake_tokenizer.return_value = _FakeEncoding(
        input_ids=list(range(1, len(token_offsets) + 1)),
        offset_mapping=token_offsets,
    )

    fake_encoder = MagicMock()
    fake_encoder.device = "cpu"

    def _forward(input_ids, attention_mask):
        seq = input_ids.shape[1]
        hidden = np.zeros((1, seq, hidden_dim), dtype=np.float32)
        # Row i gets value i+1 in position 0 so mean-pool is easy to reason about.
        for i in range(seq):
            hidden[0, i, 0] = float(i + 1)
        output = MagicMock()

        class _T:
            def __init__(self, arr):
                self.arr = arr

            def __getitem__(self, idx):
                return _T(self.arr[idx])

            def detach(self):
                return self

            def cpu(self):
                return self

            def numpy(self):
                return self.arr

        output.last_hidden_state = _T(hidden)
        return output

    fake_encoder.side_effect = _forward
    # ``encoder(input_ids=..., attention_mask=...)`` must return _forward's output.
    fake_encoder.__call__ = _forward  # type: ignore[method-assign]

    lc_module._TOKENIZER = fake_tokenizer
    lc_module._ENCODER = fake_encoder
    return fake_tokenizer, fake_encoder


def test_embed_rejects_empty_doc_text():
    embedder = LateChunkingEmbedder()
    with pytest.raises(ValueError, match="doc_text must not be empty"):
        embedder.embed_chunks_from_doc("", [ChunkSpan("c1", 0, 10)])


def test_embed_rejects_empty_chunks():
    embedder = LateChunkingEmbedder()
    with pytest.raises(ValueError, match="chunks must not be empty"):
        embedder.embed_chunks_from_doc("nonempty doc", [])


def test_embed_full_doc_single_window_happy_path():
    """Single-window doc: one encoder call, every chunk gets a 4-dim vector.

    This verifies the end-to-end path works with deterministic fake backends:
    tokenizer → encoder → offset-based chunk assignment → mean pool.
    """
    pytest.importorskip("numpy")
    pytest.importorskip("torch")

    # Doc = 50 chars, 10 tokens of width 5.
    token_offsets = [(i * 5, (i + 1) * 5) for i in range(10)]
    doc = "x" * 50

    with patch.object(lc_module, "_load_backends") as load:
        tok, enc = _install_fake_backends(token_offsets)
        load.return_value = (tok, enc)

        embedder = LateChunkingEmbedder(
            LateChunkingConfig(window_size_tokens=20, window_overlap_tokens=5, normalize=False)
        )
        chunks = [
            ChunkSpan("c1", 0, 25),  # tokens 0..5
            ChunkSpan("c2", 25, 50),  # tokens 5..10
        ]
        result = embedder.embed_chunks_from_doc(doc, chunks)

    assert set(result) == {"c1", "c2"}
    assert len(result["c1"]) == 4
    assert len(result["c2"]) == 4
    # c1 pools rows 0..4 → mean of [1,2,3,4,5] = 3.0 in position 0.
    assert result["c1"][0] == pytest.approx(3.0)
    # c2 pools rows 5..9 → mean of [6,7,8,9,10] = 8.0 in position 0.
    assert result["c2"][0] == pytest.approx(8.0)


def test_embed_normalizes_output_when_config_says_so():
    """With normalize=True each output vector has unit L2 norm (<= 1024-dim in real BGE;
    here we use a 4-dim fake encoder so we can check the math easily)."""
    pytest.importorskip("numpy")
    pytest.importorskip("torch")

    token_offsets = [(i * 5, (i + 1) * 5) for i in range(4)]
    doc = "x" * 20

    with patch.object(lc_module, "_load_backends") as load:
        tok, enc = _install_fake_backends(token_offsets)
        load.return_value = (tok, enc)

        embedder = LateChunkingEmbedder(
            LateChunkingConfig(window_size_tokens=10, window_overlap_tokens=2, normalize=True)
        )
        result = embedder.embed_chunks_from_doc(doc, [ChunkSpan("c1", 0, 20)])

    vec = result["c1"]
    norm = sum(v * v for v in vec) ** 0.5
    assert norm == pytest.approx(1.0, rel=1e-5)


def test_embed_falls_back_when_chunk_has_no_token_overlap(monkeypatch):
    """Chunk outside the doc's tokenized range must still get a vector, via
    the ``bge_embed_query`` fallback path. This preserves the
    every-chunk-gets-one-vector invariant."""
    pytest.importorskip("numpy")
    pytest.importorskip("torch")

    token_offsets = [(i * 5, (i + 1) * 5) for i in range(4)]  # chars 0..20
    doc = "x" * 1000  # long doc but tokenizer only reports 4 tokens

    fallback_calls: list[str] = []

    def _fake_bge_embed_query(text: str) -> list[float]:
        fallback_calls.append(text)
        return [0.1] * 1024

    # Patch the fallback symbol before the method imports it at call-time.
    import agentic_core.embeddings.bge_runtime as bge_rt

    monkeypatch.setattr(bge_rt, "bge_embed_query", _fake_bge_embed_query)

    with patch.object(lc_module, "_load_backends") as load:
        tok, enc = _install_fake_backends(token_offsets)
        load.return_value = (tok, enc)

        embedder = LateChunkingEmbedder(
            LateChunkingConfig(window_size_tokens=10, window_overlap_tokens=2, normalize=False)
        )
        # c_far is at char 900..950 where there are no token offsets.
        chunks = [ChunkSpan("c_in", 0, 20), ChunkSpan("c_far", 900, 950)]
        result = embedder.embed_chunks_from_doc(doc, chunks)

    assert set(result) == {"c_in", "c_far"}
    # c_far must have come from the fallback (1024-dim).
    assert len(result["c_far"]) == 1024
    # And exactly one fallback call happened, for c_far's substring.
    assert fallback_calls == ["x" * 50]


def test_fallback_emits_zero_vector_for_whitespace_only_chunk():
    """An empty or whitespace-only substring from the fallback path yields a
    1024-dim zero vector rather than an exception. Keeps ingestion resilient
    to chunking bugs that produce empty spans."""
    pytest.importorskip("numpy")
    embedder = LateChunkingEmbedder()
    # Doc is whitespace in the span we'll ask for. Route directly to the
    # internal fallback to avoid needing tokenizer mocks.
    result = embedder._fallback_all(
        [ChunkSpan("empty", 0, 3)],
        doc_text="   rest of doc",
    )
    assert result["empty"] == [0.0] * 1024
