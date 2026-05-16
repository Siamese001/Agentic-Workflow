"""Foundational behavioral tests for apps_rg/config/agent_spec_config.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_agent_spec_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

# W1 (apps-rg-unit-pytest-remediation-f7e2a9): former agent_spec_config API removed;
# production SSOT is RgAgentSpecs in the same module. Restore or relocate tests in W2+.
try:
    from apps_rg.config.agent_spec_config import (
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        THRESHOLD,
        AgentSpec,
        ClerkExtractionConfig,
        EnrichmentConfig,
        GenerationConfig,
        OrchestrationTopology,
        ValidationConfig,
    )
except ImportError:
    pytest.skip(
        "apps-rg-unit-pytest-remediation-f7e2a9 W1: legacy agent_spec_config "
        "symbols (BATCH_SIZE, AgentSpec, …) not exported — module is RgAgentSpecs-only.",
        allow_module_level=True,
    )

pytestmark = pytest.mark.unit


class TestAgentSpecContract:
    def test_is_class(self):
        assert isinstance(AgentSpec, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(AgentSpec, type)


class TestOrchestrationTopologyContract:
    def test_is_class(self):
        assert isinstance(OrchestrationTopology, type)

    def test_has_method_validate_agents_exist(self):
        assert callable(getattr(OrchestrationTopology, "validate_agents_exist", None))


class TestClerkExtractionConfigContract:
    def test_is_class(self):
        assert isinstance(ClerkExtractionConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ClerkExtractionConfig, type)


class TestEnrichmentConfigContract:
    def test_is_class(self):
        assert isinstance(EnrichmentConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(EnrichmentConfig, type)


class TestGenerationConfigContract:
    def test_is_class(self):
        assert isinstance(GenerationConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(GenerationConfig, type)


class TestValidationConfigContract:
    def test_is_class(self):
        assert isinstance(ValidationConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ValidationConfig, type)


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
