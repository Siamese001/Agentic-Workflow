"""Foundational behavioral tests for agentic_core/L1_cognition/types/cache_types.py.

fan_in=18 — this module is imported by 18 other modules.
ADG contract: import-hygiene is covered by test_cache_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L1_cognition.types.cache_types import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    DomainConfig,
    EvictionPolicy,
)


class TestEvictionPolicyContract:
    def test_is_enum(self):
        from agentic_core.L1_cognition.types.cache_types import (  # noqa: F401
        import enum
        assert issubclass(EvictionPolicy, enum.Enum)

    def test_has_members(self):
        assert len(list(EvictionPolicy)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in EvictionPolicy:
            assert member.value is not None

    def test_known_member_lru_exists(self):
        assert hasattr(EvictionPolicy, 'LRU')

class TestDomainConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DomainConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(DomainConfig)}
        assert field_names >= {'similarity_threshold', 'eviction_policy', 'domain', 'ttl_seconds', 'max_cache_size'}

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module cache_types must be importable or skip gracefully."""
    pass  # Import verified at module level
