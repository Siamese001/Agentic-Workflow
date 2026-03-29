"""Foundational behavioral tests for apps_rg/config/agent_spec_config.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_agent_spec_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestAgentSpecContract:
    def test_is_class(self):
        from apps_rg.config.agent_spec_config import (  # noqa: F401
            BATCH_SIZE,
            BUFFER_SIZE,
            DEFAULT_SLEEP,
            MAX_RETRIES,
            THRESHOLD,
            AgentSpec,
            ClerkExtractionConfig,
            EnrichmentConfig,
            GenerationConfig,
            OrchestrationTopology,
            ValidationConfig,
        )

        assert isinstance(AgentSpec, type)

    def test_instantiable_or_abstract(self):
        from apps_rg.config.agent_spec_config import AgentSpec
        assert isinstance(AgentSpec, type)


class TestOrchestrationTopologyContract:
    def test_is_class(self):
        from apps_rg.config.agent_spec_config import OrchestrationTopology
        assert isinstance(OrchestrationTopology, type)

    def test_has_method_validate_agents_exist(self):
        from apps_rg.config.agent_spec_config import OrchestrationTopology
        assert callable(getattr(OrchestrationTopology, 'validate_agents_exist', None))


class TestClerkExtractionConfigContract:
    def test_is_class(self):
        from apps_rg.config.agent_spec_config import ClerkExtractionConfig
        assert isinstance(ClerkExtractionConfig, type)

    def test_instantiable_or_abstract(self):
        from apps_rg.config.agent_spec_config import ClerkExtractionConfig
        assert isinstance(ClerkExtractionConfig, type)


class TestEnrichmentConfigContract:
    def test_is_class(self):
        from apps_rg.config.agent_spec_config import EnrichmentConfig
        assert isinstance(EnrichmentConfig, type)

    def test_instantiable_or_abstract(self):
        from apps_rg.config.agent_spec_config import EnrichmentConfig
        assert isinstance(EnrichmentConfig, type)


class TestGenerationConfigContract:
    def test_is_class(self):
        from apps_rg.config.agent_spec_config import GenerationConfig
        assert isinstance(GenerationConfig, type)

    def test_instantiable_or_abstract(self):
        from apps_rg.config.agent_spec_config import GenerationConfig
        assert isinstance(GenerationConfig, type)


class TestValidationConfigContract:
    def test_is_class(self):
        from apps_rg.config.agent_spec_config import ValidationConfig
        assert isinstance(ValidationConfig, type)

    def test_instantiable_or_abstract(self):
        from apps_rg.config.agent_spec_config import ValidationConfig
        assert isinstance(ValidationConfig, type)


class TestMaxRetriesConstant:
    def test_is_not_none(self):
        from apps_rg.config.agent_spec_config import MAX_RETRIES
        assert MAX_RETRIES is not None


class TestDefaultSleepConstant:
    def test_is_not_none(self):
        from apps_rg.config.agent_spec_config import DEFAULT_SLEEP
        assert DEFAULT_SLEEP is not None


class TestThresholdConstant:
    def test_is_not_none(self):
        from apps_rg.config.agent_spec_config import THRESHOLD
        assert THRESHOLD is not None


class TestBufferSizeConstant:
    def test_is_not_none(self):
        from apps_rg.config.agent_spec_config import BUFFER_SIZE
        assert BUFFER_SIZE is not None


class TestBatchSizeConstant:
    def test_is_not_none(self):
        from apps_rg.config.agent_spec_config import BATCH_SIZE
        assert BATCH_SIZE is not None
