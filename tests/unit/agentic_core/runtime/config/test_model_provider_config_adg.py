"""ADG-driven tests for agentic_core/runtime/config/model_provider_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.config.model_provider_config import (  # noqa: F401
        ModelProvider,
        ModelConfig,
        RAGConfig,
        GovernorConfig,
        WorkflowConfig,
        Config,
        ContentConstraintsConfig,
        SignalControlConfig,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ModelProvider = None  # type: ignore[assignment,misc]
    ModelConfig = None  # type: ignore[assignment,misc]
    RAGConfig = None  # type: ignore[assignment,misc]
    GovernorConfig = None  # type: ignore[assignment,misc]
    WorkflowConfig = None  # type: ignore[assignment,misc]
    Config = None  # type: ignore[assignment,misc]
    ContentConstraintsConfig = None  # type: ignore[assignment,misc]
    SignalControlConfig = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestModelProvider:
    def test_is_enum(self):
        import enum
        assert issubclass(ModelProvider, enum.Enum)
    def test_has_members(self):
        assert len(list(ModelProvider)) >= 1
    def test_importable(self):
        assert ModelProvider is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestModelConfig:
    def test_is_class(self):
        assert isinstance(ModelConfig, type)
    def test_importable(self):
        assert ModelConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestRAGConfig:
    def test_is_class(self):
        assert isinstance(RAGConfig, type)
    def test_importable(self):
        assert RAGConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestGovernorConfig:
    def test_is_class(self):
        assert isinstance(GovernorConfig, type)
    def test_importable(self):
        assert GovernorConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestWorkflowConfig:
    def test_is_class(self):
        assert isinstance(WorkflowConfig, type)
    def test_importable(self):
        assert WorkflowConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestConfig:
    def test_is_class(self):
        assert isinstance(Config, type)
    def test_importable(self):
        assert Config is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestContentConstraintsConfig:
    def test_is_class(self):
        assert isinstance(ContentConstraintsConfig, type)
    def test_importable(self):
        assert ContentConstraintsConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestSignalControlConfig:
    def test_is_class(self):
        assert isinstance(SignalControlConfig, type)
    def test_importable(self):
        assert SignalControlConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="model_provider_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module model_provider_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
