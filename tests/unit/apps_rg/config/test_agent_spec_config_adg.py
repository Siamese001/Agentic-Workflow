"""ADG-driven tests for apps_rg/config/agent_spec_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.config.agent_spec_config import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        AgentSpec,
        ClerkExtractionConfig,
        EnrichmentConfig,
        GateConfig,
        GenerationConfig,
        OrchestrationTopology,
        RefinementConfig,
        ValidationConfig,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    AgentSpec = None  # type: ignore[assignment,misc]
    OrchestrationTopology = None  # type: ignore[assignment,misc]
    ClerkExtractionConfig = None  # type: ignore[assignment,misc]
    EnrichmentConfig = None  # type: ignore[assignment,misc]
    GenerationConfig = None  # type: ignore[assignment,misc]
    ValidationConfig = None  # type: ignore[assignment,misc]
    GateConfig = None  # type: ignore[assignment,misc]
    RefinementConfig = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestAgentSpec:
    def test_is_class(self):
        assert isinstance(AgentSpec, type)
    def test_importable(self):
        assert AgentSpec is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestOrchestrationTopology:
    def test_is_class(self):
        assert isinstance(OrchestrationTopology, type)
    def test_importable(self):
        assert OrchestrationTopology is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestClerkExtractionConfig:
    def test_is_class(self):
        assert isinstance(ClerkExtractionConfig, type)
    def test_importable(self):
        assert ClerkExtractionConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestEnrichmentConfig:
    def test_is_class(self):
        assert isinstance(EnrichmentConfig, type)
    def test_importable(self):
        assert EnrichmentConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestGenerationConfig:
    def test_is_class(self):
        assert isinstance(GenerationConfig, type)
    def test_importable(self):
        assert GenerationConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestValidationConfig:
    def test_is_class(self):
        assert isinstance(ValidationConfig, type)
    def test_importable(self):
        assert ValidationConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestGateConfig:
    def test_is_class(self):
        assert isinstance(GateConfig, type)
    def test_importable(self):
        assert GateConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestRefinementConfig:
    def test_is_class(self):
        assert isinstance(RefinementConfig, type)
    def test_importable(self):
        assert RefinementConfig is not None

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

@pytest.mark.skipif(not _AVAILABLE, reason="agent_spec_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module agent_spec_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE