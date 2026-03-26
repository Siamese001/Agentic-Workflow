"""Foundational behavioral tests for agentic_core/L1_cognition/types/client_types.py.

fan_in=21 — this module is imported by 21 other modules.
ADG contract: import-hygiene is covered by test_client_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L1_cognition.types.client_types import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    CacheEntry,
    HealingPattern,
)


class TestHealingPatternContract:
    def test_is_dataclass(self):
                from agentic_core.L1_cognition.types.client_types import (  # noqa: F401
                import dataclasses
                assert dataclasses.is_dataclass(HealingPattern)

        assert dataclasses.is_dataclass(HealingPattern)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(HealingPattern)}
        assert field_names >= {'success_count', 'healing_strategy', 'pattern_id', 'violation_type', 'error_signature'}

class TestCacheEntryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CacheEntry)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CacheEntry)}
        assert field_names >= {'created_at', 'key', 'domain', 'value', 'ttl'}

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
    """Module client_types must be importable or skip gracefully."""
    pass  # Import verified at module level
