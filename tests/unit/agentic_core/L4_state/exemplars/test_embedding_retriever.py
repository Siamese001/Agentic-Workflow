"""W7 tests for embedding-based exemplar retrieval."""

from __future__ import annotations

from typing import Sequence

import pytest

from agentic_core.L4_state.exemplars.bank import ExemplarBank, ExemplarRecord
from agentic_core.L4_state.exemplars.embedding_retriever import (
    select_top_k_by_embedding,
    select_with_fallback,
)


class FakeEmbeddingProvider:
    """Deterministic fake. Each input gets a 3-d vector derived from fixed
    tokens so tests are both repeatable and human-meaningful."""

    name = "fake-embedder"

    # Axis-aligned vectors: 'security', 'marketing', 'other'.
    _VOCAB = {
        "security": [1.0, 0.0, 0.0],
        "soc2": [1.0, 0.0, 0.0],
        "audit": [0.9, 0.0, 0.1],
        "marketing": [0.0, 1.0, 0.0],
        "copy": [0.0, 1.0, 0.0],
        "landing": [0.0, 0.9, 0.1],
    }

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for t in texts:
            vec = [0.0, 0.0, 1.0]  # default: pure 'other'
            lowered = t.lower()
            acc = [0.0, 0.0, 0.0]
            matched = 0
            for word, v in self._VOCAB.items():
                if word in lowered:
                    acc = [acc[0] + v[0], acc[1] + v[1], acc[2] + v[2]]
                    matched += 1
            if matched:
                vec = [c / matched for c in acc]
            out.append(vec)
        return out


class NullEmbeddingProvider:
    """Returns zero-length vectors \u2014 used to test the zero-norm guard."""

    name = "null-embedder"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[] for _ in texts]


class BrokenEmbeddingProvider:
    """Returns wrong number of vectors \u2014 should raise."""

    name = "broken-embedder"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0]]  # only one vector regardless of input count


def _populate(bank: ExemplarBank) -> None:
    bank.add(
        ExemplarRecord(
            exemplar_id="ex-sec",
            task_class="draft",
            input_text="security posture for SOC2 audit",
            output_text="result A",
            tags=("security", "soc2"),
        )
    )
    bank.add(
        ExemplarRecord(
            exemplar_id="ex-mkt",
            task_class="draft",
            input_text="marketing landing page copy",
            output_text="result B",
            tags=("marketing", "copy"),
        )
    )
    bank.add(
        ExemplarRecord(
            exemplar_id="ex-aud",
            task_class="draft",
            input_text="audit remediation plan",
            output_text="result C",
            tags=("security", "audit"),
        )
    )


class TestEmbeddingRetrieval:
    def test_selects_most_similar(self) -> None:
        bank = ExemplarBank()
        _populate(bank)
        chosen = select_top_k_by_embedding(
            query="Write a security section for a SOC2 audit",
            task_class="draft",
            bank=bank,
            provider=FakeEmbeddingProvider(),
            k=2,
        )
        ids = [r.exemplar_id for r in chosen]
        assert "ex-sec" in ids
        # Marketing record should NOT be in the top 2 for a security query.
        assert "ex-mkt" not in ids

    def test_k_zero_returns_empty(self) -> None:
        bank = ExemplarBank()
        _populate(bank)
        assert (
            select_top_k_by_embedding(
                query="x",
                task_class="draft",
                bank=bank,
                provider=FakeEmbeddingProvider(),
                k=0,
            )
            == ()
        )

    def test_unknown_class_returns_empty(self) -> None:
        bank = ExemplarBank()
        _populate(bank)
        assert (
            select_top_k_by_embedding(
                query="x",
                task_class="nope",
                bank=bank,
                provider=FakeEmbeddingProvider(),
            )
            == ()
        )

    def test_zero_norm_vectors_score_zero(self) -> None:
        """Null provider \u2014 must not crash on division by zero."""
        bank = ExemplarBank()
        _populate(bank)
        chosen = select_top_k_by_embedding(
            query="anything",
            task_class="draft",
            bank=bank,
            provider=NullEmbeddingProvider(),
            k=3,
        )
        # All scores zero \u2014 order is pure exemplar_id ascending.
        assert [r.exemplar_id for r in chosen] == ["ex-aud", "ex-mkt", "ex-sec"]

    def test_broken_provider_raises(self) -> None:
        bank = ExemplarBank()
        _populate(bank)
        with pytest.raises(ValueError, match="returned 1 vectors"):
            select_top_k_by_embedding(
                query="x",
                task_class="draft",
                bank=bank,
                provider=BrokenEmbeddingProvider(),
            )


class TestFallback:
    def test_fallback_to_static_when_provider_none(self) -> None:
        bank = ExemplarBank()
        _populate(bank)
        chosen = select_with_fallback(
            query="security SOC2 audit",
            task_class="draft",
            bank=bank,
            provider=None,
            k=2,
        )
        # Static Jaccard also prefers the security tagged records.
        ids = [r.exemplar_id for r in chosen]
        assert "ex-sec" in ids
        assert "ex-mkt" not in ids

    def test_fallback_uses_provider_when_given(self) -> None:
        bank = ExemplarBank()
        _populate(bank)
        chosen = select_with_fallback(
            query="security SOC2 audit",
            task_class="draft",
            bank=bank,
            provider=FakeEmbeddingProvider(),
            k=1,
        )
        assert len(chosen) == 1
        assert chosen[0].exemplar_id in ("ex-sec", "ex-aud")
