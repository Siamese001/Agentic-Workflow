"""ADG-driven tests for agentic_core/runtime/config/model_tier_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.config.path_constants import (
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
    )
    from agentic_core.runtime.config.model_tier_config import (
        ModelConfig,
        ModelTier,
        RoutingDecision,
        TaskComplexity,
    )
except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallow
    ModelTier = None  # type: ignore[assignment,misc]
    TaskComplexity = None  # type: ignore[assignment,misc]
    ModelConfig = None  # type: ignore[assignment,misc]
    RoutingDecision = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


class TestModelTier:
    def test_is_enum(self):
        """Test ModelTier is an enum."""
        from enum import Enum
        assert isinstance(ModelTier, type) and issubclass(ModelTier, Enum)

    def test_has_members(self):
        """Test ModelTier has expected members."""
        assert hasattr(ModelTier, 'LOW')
        assert hasattr(ModelTier, 'MEDIUM')
        assert hasattr(ModelTier, 'HIGH')

    def test_is_not_none(self):
        """Test ModelTier is not None."""
        assert ModelTier is not None


class TestTaskComplexity:
    def test_is_enum(self):
        """Test TaskComplexity is an enum."""
        from enum import Enum
        assert isinstance(TaskComplexity, type) and issubclass(TaskComplexity, Enum)

    def test_is_not_none(self):
        """Test TaskComplexity is not None."""
        assert TaskComplexity is not None


class TestModelConfig:
    def test_is_class(self):
        """Test ModelConfig is a class."""
        assert isinstance(ModelConfig, type)

    def test_is_not_none(self):
        """Test ModelConfig is not None."""
        assert ModelConfig is not None


class TestRoutingDecision:
    def test_is_class(self):
        """Test RoutingDecision is a class."""
        assert isinstance(RoutingDecision, type)

    def test_is_not_none(self):
        """Test RoutingDecision is not None."""
        assert RoutingDecision is not None


class TestConstants:
    def test_batch_size_is_int(self):
        """Test BATCH_SIZE is an integer."""
        assert isinstance(BATCH_SIZE, int)

    def test_buffer_size_is_int(self):
        """Test BUFFER_SIZE is an integer."""
        assert isinstance(BUFFER_SIZE, int)

    def test_max_retries_is_int(self):
        """Test MAX_RETRIES is an integer."""
        assert isinstance(MAX_RETRIES, int)
