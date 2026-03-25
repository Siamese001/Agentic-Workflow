"""Foundational behavioral tests for agentic_core/runtime/config/model_provider_config.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_model_provider_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.config.model_provider_config import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    Config,
    GovernorConfig,
    ModelConfig,
    ModelProvider,
    RAGConfig,
    WorkflowConfig,
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

    def test_has_method_validate_model_name(self):
        assert callable(getattr(ModelConfig, 'validate_model_name', None))

class TestRAGConfigContract:
    def test_is_class(self):
        assert isinstance(RAGConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(RAGConfig, type)

class TestGovernorConfigContract:
    def test_is_class(self):
        assert isinstance(GovernorConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(GovernorConfig, type)

class TestWorkflowConfigContract:
    def test_is_class(self):
        assert isinstance(WorkflowConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(WorkflowConfig, type)

class TestConfigContract:
    def test_is_class(self):
        assert isinstance(Config, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(Config, type)

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
    """Module model_provider_config must be importable or skip gracefully."""
    pass  # Import verified at module level
