"""ADG-driven tests for L5_safety/validators/context_validator.py — fan_in=1."""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.validators.context_validator import CacheEntry


class TestCacheEntry:
    def test_creates(self):
        entry = CacheEntry(
            key="test:key",
            value={"result": True},
            timestamp=time.time(),
            ttl=60,
            agent="TestAgent",
        )
        assert entry.key == "test:key"

    def test_not_expired_fresh(self):
        entry = CacheEntry(
            key="k",
            value="v",
            timestamp=time.time(),
            ttl=60,
            agent="A",
        )
        assert entry.is_expired() is False

    def test_expired_old_timestamp(self):
        entry = CacheEntry(
            key="k",
            value="v",
            timestamp=time.time() - 200,
            ttl=60,
            agent="A",
        )
        assert entry.is_expired() is True

    def test_value_preserved(self):
        entry = CacheEntry(
            key="k",
            value={"data": [1, 2, 3]},
            timestamp=time.time(),
            ttl=30,
            agent="B",
        )
        assert entry.value == {"data": [1, 2, 3]}
