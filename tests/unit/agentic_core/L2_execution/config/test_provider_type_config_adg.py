"""ADG-driven tests for L2_execution/config/provider_type_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.config.provider_type_config import (
    DEFAULT_PROVIDER_CLASSES,
    DEFAULT_PROVIDER_MODULES,
    ProviderType,
)


class TestProviderType:
    def test_is_enum(self):
        import enum
        assert issubclass(ProviderType, enum.Enum)

    def test_stub_value(self):
        assert ProviderType.STUB.value == "stub"

    def test_redis_value(self):
        assert ProviderType.REDIS.value == "redis"

    def test_all_values_are_strings(self):
        for pt in ProviderType:
            assert isinstance(pt.value, str)


class TestDefaultProviderMappings:
    def test_modules_is_dict(self):
        assert isinstance(DEFAULT_PROVIDER_MODULES, dict)

    def test_classes_is_dict(self):
        assert isinstance(DEFAULT_PROVIDER_CLASSES, dict)

    def test_stub_in_modules(self):
        assert "stub" in DEFAULT_PROVIDER_MODULES

    def test_stub_in_classes(self):
        assert "stub" in DEFAULT_PROVIDER_CLASSES
