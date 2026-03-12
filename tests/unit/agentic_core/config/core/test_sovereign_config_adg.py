"""ADG-driven tests for agentic_core/config/core/sovereign_config.py — fan_in=5.

Singleton config manager contract tests: importability, singleton semantics,
env-var accessors, typed defaults, and reset for test isolation.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.config.core.sovereign_config import (
    SovereignConfigManager,
    get_sovereign_config,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    SovereignConfigManager.reset_instance()
    yield
    SovereignConfigManager.reset_instance()


class TestSovereignConfigManagerImport:
    def test_class_importable(self):
        assert callable(SovereignConfigManager)

    def test_get_sovereign_config_callable(self):
        assert callable(get_sovereign_config)


class TestSovereignConfigManagerSingleton:
    def test_same_instance_returned(self):
        a = SovereignConfigManager()
        b = SovereignConfigManager()
        assert a is b

    def test_get_sovereign_config_returns_instance(self):
        cfg = get_sovereign_config()
        assert isinstance(cfg, SovereignConfigManager)

    def test_reset_creates_new_instance(self):
        a = SovereignConfigManager()
        SovereignConfigManager.reset_instance()
        b = SovereignConfigManager()
        assert a is not b


class TestSovereignConfigManagerDefaults:
    def test_default_openai_model(self):
        cfg = SovereignConfigManager()
        assert cfg.DEFAULT_OPENAI_MODEL == "gpt-4o"

    def test_default_anthropic_model(self):
        cfg = SovereignConfigManager()
        assert "claude" in cfg.DEFAULT_ANTHROPIC_MODEL

    def test_default_embedding_model(self):
        cfg = SovereignConfigManager()
        assert cfg.DEFAULT_EMBEDDING_MODEL == "BAAI/bge-m3"

    def test_default_max_audit_log_size(self):
        cfg = SovereignConfigManager()
        assert cfg.DEFAULT_MAX_AUDIT_LOG_SIZE == 1000

    def test_default_max_healing_attempts(self):
        cfg = SovereignConfigManager()
        assert cfg.DEFAULT_MAX_HEALING_ATTEMPTS == 3

    def test_embedding_dim_bge(self):
        cfg = SovereignConfigManager()
        assert cfg.EMBEDDING_DIM_BGE == 1024


class TestSovereignConfigManagerEnvAccessors:
    def test_get_str_returns_default_when_unset(self):
        cfg = SovereignConfigManager()
        result = cfg.get_str("__NONEXISTENT_KEY_XYZ__", "fallback")
        assert result == "fallback"

    def test_get_int_returns_default_when_unset(self):
        cfg = SovereignConfigManager()
        result = cfg.get_int("__NONEXISTENT_KEY_XYZ__", 42)
        assert result == 42

    def test_get_bool_returns_default_when_unset(self):
        cfg = SovereignConfigManager()
        result = cfg.get_bool("__NONEXISTENT_KEY_XYZ__", False)
        assert result is False

    def test_get_str_reads_env(self, monkeypatch):
        monkeypatch.setenv("__ADG_TEST_STR__", "hello")
        cfg = SovereignConfigManager()
        assert cfg.get_str("__ADG_TEST_STR__") == "hello"

    def test_get_int_reads_env(self, monkeypatch):
        monkeypatch.setenv("__ADG_TEST_INT__", "99")
        cfg = SovereignConfigManager()
        assert cfg.get_int("__ADG_TEST_INT__") == 99

    def test_get_bool_true_values(self, monkeypatch):
        cfg = SovereignConfigManager()
        for truthy in ("true", "1", "yes", "on", "True", "YES"):
            monkeypatch.setenv("__ADG_TEST_BOOL__", truthy)
            assert cfg.get_bool("__ADG_TEST_BOOL__") is True

    def test_get_bool_false_values(self, monkeypatch):
        cfg = SovereignConfigManager()
        for falsy in ("false", "0", "no", "off"):
            monkeypatch.setenv("__ADG_TEST_BOOL__", falsy)
            assert cfg.get_bool("__ADG_TEST_BOOL__") is False

    def test_get_int_invalid_value_returns_default(self, monkeypatch):
        monkeypatch.setenv("__ADG_TEST_INT_BAD__", "notanint")
        cfg = SovereignConfigManager()
        assert cfg.get_int("__ADG_TEST_INT_BAD__", 7) == 7


class TestSovereignConfigTypedProperties:
    def test_openai_model_property(self):
        cfg = SovereignConfigManager()
        assert isinstance(cfg.openai_model, str)
        assert len(cfg.openai_model) > 0

    def test_redis_mcp_enabled_default_false(self):
        cfg = SovereignConfigManager()
        assert cfg.redis_mcp_enabled is False

    def test_redis_url_default(self):
        cfg = SovereignConfigManager()
        assert "redis" in cfg.redis_url

    def test_max_audit_log_size_property(self):
        cfg = SovereignConfigManager()
        assert isinstance(cfg.max_audit_log_size, int)
        assert cfg.max_audit_log_size > 0
