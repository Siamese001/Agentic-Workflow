"""Behavioral tests for cache_types."""

from __future__ import annotations

from agentic_core.cache_types import CacheScope


def test_cache_scope_enum_contains_expected_values():
    assert {scope.value for scope in CacheScope} == {"request", "session", "persisted"}
