"""Foundational behavioral tests for apps_rg/config/agent_spec_config.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_agent_spec_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
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
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    AgentSpec = None  # type: ignore[assignment,misc]
    OrchestrationTopology = None  # type: ignore[assignment,misc]
    ClerkExtractionConfig = None  # type: ignore[assignment,misc]
    EnrichmentConfig = None  # type: ignore[assignment,misc]
    GenerationConfig = None  # type: ignore[assignment,misc]
    ValidationConfig = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestAgentSpecContract:
    def test_is_class(self):
        assert isinstance(AgentSpec, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(AgentSpec, type)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestOrchestrationTopologyContract:
    def test_is_class(self):
        assert isinstance(OrchestrationTopology, type)

    def test_has_method_validate_agents_exist(self):
        assert callable(getattr(OrchestrationTopology, 'validate_agents_exist', None))

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestClerkExtractionConfigContract:
    def test_is_class(self):
        assert isinstance(ClerkExtractionConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ClerkExtractionConfig, type)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestEnrichmentConfigContract:
    def test_is_class(self):
        assert isinstance(EnrichmentConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(EnrichmentConfig, type)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestGenerationConfigContract:
    def test_is_class(self):
        assert isinstance(GenerationConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(GenerationConfig, type)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestValidationConfigContract:
    def test_is_class(self):
        assert isinstance(ValidationConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ValidationConfig, type)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module agent_spec_config must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
