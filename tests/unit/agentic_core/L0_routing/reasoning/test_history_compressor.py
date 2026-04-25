"""History compressor tests — eviction policy + determinism."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.reasoning.history_compressor import (
    BudgetExhausted,
    CompressionResult,
    HistoryBuffer,
    HistoryItem,
    HistoryItemKind,
    compress_history,
)


def _ev(kind: HistoryItemKind, tokens: int, rank: float = 0.0, seq: int = 0) -> HistoryItem:
    return HistoryItem(
        kind=kind,
        content="x" * (tokens * 4),
        token_estimate=tokens,
        rank=rank,
        sequence_number=seq,
        item_id=f"{kind.value}-{seq}",
    )


class TestEvictionPriority:
    def test_evidence_dropped_before_convo_turns(self):
        items = [
            _ev(HistoryItemKind.EVIDENCE, 50, rank=0.1, seq=0),
            _ev(HistoryItemKind.CONVO_TURN, 50, seq=1),
        ]
        result = compress_history(items, available_tokens=60)
        kept_kinds = {i.kind for i in result.kept_items}
        dropped_kinds = {i.kind for i in result.dropped_items}
        assert HistoryItemKind.EVIDENCE in dropped_kinds
        assert HistoryItemKind.CONVO_TURN in kept_kinds

    def test_must_use_never_dropped(self):
        items = [
            _ev(HistoryItemKind.MUST_USE, 100, seq=0),
            _ev(HistoryItemKind.EVIDENCE, 50, seq=1),
            _ev(HistoryItemKind.SUPPORTING, 50, seq=2),
        ]
        result = compress_history(items, available_tokens=110)
        kept_kinds = {i.kind for i in result.kept_items}
        assert HistoryItemKind.MUST_USE in kept_kinds
        assert result.fits_budget

    def test_low_rank_evidence_dropped_first(self):
        items = [
            _ev(HistoryItemKind.EVIDENCE, 30, rank=0.9, seq=0),  # high rank → keep
            _ev(HistoryItemKind.EVIDENCE, 30, rank=0.1, seq=1),  # low rank → drop
            _ev(HistoryItemKind.EVIDENCE, 30, rank=0.5, seq=2),
        ]
        result = compress_history(items, available_tokens=60)
        kept_ids = {i.item_id for i in result.kept_items}
        # Lowest rank (0.1, seq=1) should drop first
        assert "evidence-1" not in kept_ids

    def test_fifo_within_convo_turns(self):
        items = [
            _ev(HistoryItemKind.CONVO_TURN, 30, seq=0),  # oldest → drops first
            _ev(HistoryItemKind.CONVO_TURN, 30, seq=1),
            _ev(HistoryItemKind.CONVO_TURN, 30, seq=2),
        ]
        result = compress_history(items, available_tokens=60)
        kept_ids = {i.item_id for i in result.kept_items}
        assert "convo_turn-0" not in kept_ids


class TestQuickPath:
    def test_already_fits_returns_unchanged(self):
        items = [_ev(HistoryItemKind.EVIDENCE, 10, seq=0)]
        result = compress_history(items, available_tokens=100)
        assert result.fits_budget
        assert result.dropped_items == ()
        assert result.tokens_dropped == 0

    def test_empty_input_returns_empty_kept(self):
        result = compress_history([], available_tokens=100)
        assert result.kept_items == ()
        assert result.fits_budget


class TestMustUseOverflow:
    def test_must_use_exceeds_budget_no_raise_returns_must_use_only(self):
        items = [
            _ev(HistoryItemKind.MUST_USE, 100, seq=0),
            _ev(HistoryItemKind.EVIDENCE, 20, seq=1),
        ]
        result = compress_history(items, available_tokens=50)
        assert not result.fits_budget
        assert all(i.kind == HistoryItemKind.MUST_USE for i in result.kept_items)
        assert result.items_must_use_count == 1

    def test_must_use_exceeds_budget_raise_raises(self):
        items = [_ev(HistoryItemKind.MUST_USE, 100, seq=0)]
        with pytest.raises(BudgetExhausted):
            compress_history(items, available_tokens=50, raise_on_overflow=True)


class TestDeterminism:
    def test_two_runs_produce_identical_output(self):
        items = [
            _ev(HistoryItemKind.EVIDENCE, 30, rank=0.5, seq=0),
            _ev(HistoryItemKind.SUPPORTING, 30, seq=1),
            _ev(HistoryItemKind.CONVO_TURN, 30, seq=2),
        ]
        a = compress_history(items, available_tokens=60)
        b = compress_history(items, available_tokens=60)
        assert tuple(i.item_id for i in a.kept_items) == tuple(i.item_id for i in b.kept_items)
        assert tuple(i.item_id for i in a.dropped_items) == tuple(i.item_id for i in b.dropped_items)

    def test_kept_items_in_original_order(self):
        items = [
            _ev(HistoryItemKind.SUPPORTING, 20, seq=2),
            _ev(HistoryItemKind.EVIDENCE, 20, seq=0),
            _ev(HistoryItemKind.CONVO_TURN, 20, seq=1),
        ]
        result = compress_history(items, available_tokens=200)
        seqs = [i.sequence_number for i in result.kept_items]
        assert seqs == [2, 0, 1]  # preserves input order, not drop order


class TestHistoryBuffer:
    def test_append_assigns_sequence_numbers(self):
        buf = HistoryBuffer()
        a = buf.append(HistoryItemKind.EVIDENCE, "foo", token_estimate=10)
        b = buf.append(HistoryItemKind.EVIDENCE, "bar", token_estimate=10)
        assert a.sequence_number == 0
        assert b.sequence_number == 1

    def test_total_tokens_sums_estimates(self):
        buf = HistoryBuffer()
        buf.append(HistoryItemKind.EVIDENCE, "x", token_estimate=5)
        buf.append(HistoryItemKind.SUPPORTING, "y", token_estimate=15)
        assert buf.total_tokens() == 20

    def test_compress_does_not_mutate_buffer(self):
        buf = HistoryBuffer()
        buf.append(HistoryItemKind.EVIDENCE, "x", token_estimate=100)
        before_count = len(buf.items)
        buf.compress_to(50)
        assert len(buf.items) == before_count

    def test_apply_compression_replaces_items(self):
        buf = HistoryBuffer()
        buf.append(HistoryItemKind.EVIDENCE, "x", token_estimate=100)
        buf.append(HistoryItemKind.MUST_USE, "y", token_estimate=10)
        result = buf.compress_to(50)
        buf.apply_compression(result)
        assert all(i.kind == HistoryItemKind.MUST_USE for i in buf.items)


class TestResultShape:
    def test_token_accounting(self):
        items = [
            _ev(HistoryItemKind.EVIDENCE, 40, seq=0),
            _ev(HistoryItemKind.EVIDENCE, 40, seq=1),
            _ev(HistoryItemKind.MUST_USE, 20, seq=2),
        ]
        result = compress_history(items, available_tokens=50)
        assert result.tokens_before == 100
        assert result.tokens_after == result.tokens_before - result.tokens_dropped
        assert result.tokens_after <= 100
        assert isinstance(result, CompressionResult)
