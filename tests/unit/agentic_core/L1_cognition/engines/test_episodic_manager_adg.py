"""ADG-driven tests for L1_cognition/engines/episodic_manager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.episodic_manager import Episode, EpisodicMemory


class TestEpisode:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Episode)

    def test_creates(self):
        ep = Episode(episode_id="ep-001", summary="ran task", mission_type="task", outcome="success")
        assert ep.episode_id == "ep-001"
        assert ep.outcome == "success"
        assert ep.steps == []
        assert ep.duration_ms == 0.0

    def test_reward_default(self):
        ep = Episode(episode_id="ep-002", summary="x", mission_type="healing", outcome="partial")
        assert ep.reward == 0.0


class TestEpisodicMemory:
    def test_creates_with_defaults(self):
        mem = EpisodicMemory()
        assert mem is not None
        assert mem.capacity == 200
        assert mem.episodes == []
        assert mem.total_stored == 0

    def test_creates_with_custom_capacity(self):
        mem = EpisodicMemory(capacity=50)
        assert mem.capacity == 50
