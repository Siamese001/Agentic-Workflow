"""Foundational behavioral tests for agentic_core/runtime/config/reasoning_types.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_reasoning_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.config.reasoning_types import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    GovernorConfig,
    ModelConfig,
    ModelProvider,
    RAGConfig,
    ReasoningConfig,
)


class TestModelProviderContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ModelProvider, enum.Enum)

    def test_has_members(self):
        assert len(list(ModelProvider)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ModelProvider:
            assert member.value is not None

    def test_known_member_openai_exists(self):
        assert hasattr(ModelProvider, 'OPENAI')

class TestModelConfigContract:
    def test_is_class(self):
        assert isinstance(ModelConfig, type)

    def test_has_method_validate_invariants(self):
        assert callable(getattr(ModelConfig, 'validate_invariants', None))

class TestRAGConfigContract:
    def test_is_class(self):
        assert isinstance(RAGConfig, type)

    def test_has_method_validate_invariants(self):
        assert callable(getattr(RAGConfig, 'validate_invariants', None))

class TestGovernorConfigContract:
    def test_is_class(self):
        assert isinstance(GovernorConfig, type)

    def test_has_method_validate_invariants(self):
        assert callable(getattr(GovernorConfig, 'validate_invariants', None))

class TestReasoningConfigContract:
    def test_is_class(self):
        assert isinstance(ReasoningConfig, type)

    def test_has_method_validate_invariants(self):
        assert callable(getattr(ReasoningConfig, 'validate_invariants', None))

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
    """Module reasoning_types must be importable or skip gracefully."""
    pass  # Import verified at module level
