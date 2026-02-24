"""Unit tests for HealingOutcomeAggregator — determinism proofs.

Tests:
  - order invariance: shuffled ingest yields identical snapshot
  - window determinism: oldest-drop is deterministic
  - proposal no-op: default build_proposal returns empty/neutral proposal
  - stats rounding: stable round-half-up to 4 decimals
  - type immutability: frozen dataclasses reject mutation
"""

from __future__ import annotations

import random

import pytest

pytestmark = pytest.mark.unit_min_deps

from system_learning.engines.healing_outcome_aggregator import (
    HealingOutcomeAggregator,
)
from system_learning.types.healing_outcome_types import (
    HealingOutcomeEvent,
    HealingOutcomeProposal,
    HealingOutcomeStats,
)


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def _event(
    healer_id: str = "h1",
    tier: str = "LOCAL_AGENT",
    failure_type: str = "syntax_error",
    success: bool = True,
    ts: int = 1000,
    trace_id: str | None = None,
) -> HealingOutcomeEvent:
    return HealingOutcomeEvent(
        healer_id=healer_id,
        tier=tier,
        failure_type=failure_type,
        success=success,
        timestamp_utc=ts,
        trace_id=trace_id,
    )


# -------------------------------------------------------------------------
# Event contract tests
# -------------------------------------------------------------------------


class TestHealingOutcomeEvent:
    """HealingOutcomeEvent validation and immutability."""

    def test_valid_event_creation(self) -> None:
        ev = _event()
        assert ev.healer_id == "h1"
        assert ev.tier == "LOCAL_AGENT"
        assert ev.success is True

    def test_empty_healer_id_rejected(self) -> None:
        with pytest.raises(ValueError, match="healer_id"):
            _event(healer_id="")

    def test_empty_tier_rejected(self) -> None:
        with pytest.raises(ValueError, match="tier"):
            _event(tier="")

    def test_empty_failure_type_rejected(self) -> None:
        with pytest.raises(ValueError, match="failure_type"):
            _event(failure_type="")

    def test_frozen(self) -> None:
        ev = _event()
        with pytest.raises(AttributeError):
            ev.healer_id = "changed"  # type: ignore[misc]


# -------------------------------------------------------------------------
# Stats contract tests
# -------------------------------------------------------------------------


class TestHealingOutcomeStats:
    """HealingOutcomeStats stable rounding."""

    def test_from_counts_basic(self) -> None:
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 3, 1)
        assert stats.total_count == 4
        assert stats.success_count == 3
        assert stats.failure_count == 1
        assert stats.success_rate == 0.75

    def test_from_counts_zero_denominator(self) -> None:
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 0, 0)
        assert stats.success_rate == 0.0

    def test_stable_rounding_half_up(self) -> None:
        # 1/3 = 0.33333... -> round-half-up to 4 decimals = 0.3333
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 1, 2)
        assert stats.success_rate == 0.3333

    def test_stable_rounding_2_of_3(self) -> None:
        # 2/3 = 0.66666... -> round-half-up to 4 decimals = 0.6667
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 2, 1)
        assert stats.success_rate == 0.6667

    def test_frozen(self) -> None:
        stats = HealingOutcomeStats.from_counts("h", "T", "f", 1, 0)
        with pytest.raises(AttributeError):
            stats.success_rate = 0.5  # type: ignore[misc]


# -------------------------------------------------------------------------
# Proposal contract tests
# -------------------------------------------------------------------------


class TestHealingOutcomeProposal:
    """HealingOutcomeProposal — Phase 1 no-op contract."""

    def test_default_proposal_is_empty(self) -> None:
        p = HealingOutcomeProposal()
        assert p.stats == ()
        assert p.recommended_actions == ()

    def test_frozen(self) -> None:
        p = HealingOutcomeProposal()
        with pytest.raises(AttributeError):
            p.recommended_actions = ("x",)  # type: ignore[misc]


# -------------------------------------------------------------------------
# Aggregator tests
# -------------------------------------------------------------------------


class TestAggregatorDeterminism:
    """Deterministic behaviour proofs for HealingOutcomeAggregator."""

    def test_window_size_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="window_size"):
            HealingOutcomeAggregator(window_size=0)

    def test_empty_snapshot(self) -> None:
        agg = HealingOutcomeAggregator(window_size=10)
        assert agg.snapshot() == []

    def test_single_event_snapshot(self) -> None:
        agg = HealingOutcomeAggregator(window_size=10)
        agg.ingest(_event(success=True))
        stats = agg.snapshot()
        assert len(stats) == 1
        assert stats[0].success_count == 1
        assert stats[0].failure_count == 0
        assert stats[0].success_rate == 1.0

    def test_order_invariance_shuffled_ingest_yields_identical_snapshot(self) -> None:
        """Shuffled ingest order MUST produce identical snapshot."""
        events = [
            _event(healer_id="h1", tier="LOCAL_AGENT", failure_type="syntax_error", success=True, ts=i)
            for i in range(5)
        ] + [
            _event(healer_id="h1", tier="LOCAL_AGENT", failure_type="syntax_error", success=False, ts=i + 100)
            for i in range(3)
        ] + [
            _event(healer_id="h2", tier="QWEN_VLLM", failure_type="import_cycle", success=True, ts=i + 200)
            for i in range(2)
        ]

        # Canonical order
        agg_canonical = HealingOutcomeAggregator(window_size=100)
        for ev in events:
            agg_canonical.ingest(ev)
        snap_canonical = agg_canonical.snapshot()

        # Shuffled order (fixed seed for reproducibility)
        rng = random.Random(42)
        shuffled = list(events)
        rng.shuffle(shuffled)
        agg_shuffled = HealingOutcomeAggregator(window_size=100)
        for ev in shuffled:
            agg_shuffled.ingest(ev)
        snap_shuffled = agg_shuffled.snapshot()

        assert snap_canonical == snap_shuffled

    def test_window_determinism_oldest_dropped(self) -> None:
        """When window overflows, oldest events are dropped deterministically."""
        agg = HealingOutcomeAggregator(window_size=3)
        agg.ingest(_event(success=True, ts=1))
        agg.ingest(_event(success=True, ts=2))
        agg.ingest(_event(success=True, ts=3))
        # Window full: 3 successes
        assert agg.snapshot()[0].success_count == 3

        # Ingest failure -> drops ts=1 (oldest success)
        agg.ingest(_event(success=False, ts=4))
        stats = agg.snapshot()
        assert len(stats) == 1
        assert stats[0].success_count == 2
        assert stats[0].failure_count == 1
        assert stats[0].total_count == 3

    def test_snapshot_sort_key(self) -> None:
        """Stats MUST be sorted by (healer_id, tier, failure_type)."""
        agg = HealingOutcomeAggregator(window_size=100)
        agg.ingest(_event(healer_id="z_healer", tier="A_tier", failure_type="a_type"))
        agg.ingest(_event(healer_id="a_healer", tier="Z_tier", failure_type="z_type"))
        agg.ingest(_event(healer_id="a_healer", tier="A_tier", failure_type="z_type"))
        stats = agg.snapshot()
        keys = [(s.healer_id, s.tier, s.failure_type) for s in stats]
        assert keys == sorted(keys)

    def test_proposal_noop_carries_snapshot(self) -> None:
        """build_proposal returns no-op proposal with snapshot data."""
        agg = HealingOutcomeAggregator(window_size=100)
        agg.ingest(_event(success=True))
        agg.ingest(_event(success=False))
        proposal = agg.build_proposal()
        assert isinstance(proposal, HealingOutcomeProposal)
        assert len(proposal.stats) == 1
        assert proposal.stats[0].total_count == 2
        assert proposal.recommended_actions == ()

    def test_event_count_property(self) -> None:
        agg = HealingOutcomeAggregator(window_size=5)
        assert agg.event_count == 0
        agg.ingest(_event())
        assert agg.event_count == 1
        for i in range(10):
            agg.ingest(_event(ts=i))
        assert agg.event_count == 5  # capped at window_size

    def test_multiple_keys_in_snapshot(self) -> None:
        """Multiple (healer_id, tier, failure_type) keys tracked independently."""
        agg = HealingOutcomeAggregator(window_size=100)
        agg.ingest(_event(healer_id="h1", tier="LOCAL_AGENT", failure_type="syntax"))
        agg.ingest(_event(healer_id="h1", tier="QWEN_VLLM", failure_type="syntax"))
        agg.ingest(_event(healer_id="h2", tier="LOCAL_AGENT", failure_type="import"))
        stats = agg.snapshot()
        assert len(stats) == 3
