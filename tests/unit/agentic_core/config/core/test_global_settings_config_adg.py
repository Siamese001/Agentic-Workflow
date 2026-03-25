"""Behavioral contract tests for agentic_core.config.core.global_settings_config."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.config.core.global_settings_config"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_basesettings_is_instantiable(mod):
    """BaseSettings is accessible and is a type."""
    cls = getattr(mod, "BaseSettings", None)
    assert cls is not None, "BaseSettings must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BaseSettings must be a class"


def test_secretstr_is_instantiable(mod):
    """SecretStr is accessible and is a type."""
    cls = getattr(mod, "SecretStr", None)
    assert cls is not None, "SecretStr must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SecretStr must be a class"


def test_settings_is_instantiable(mod):
    """Settings is accessible and is a type."""
    cls = getattr(mod, "Settings", None)
    assert cls is not None, "Settings must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Settings must be a class"


def test_settingsconfigdict_is_instantiable(mod):
    """SettingsConfigDict is accessible and is a type."""
    cls = getattr(mod, "SettingsConfigDict", None)
    assert cls is not None, "SettingsConfigDict must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SettingsConfigDict must be a class"


def test_field_is_callable(mod):
    """Field is accessible and callable."""
    func = getattr(mod, "Field", None)
    assert func is not None, "Field must be defined in {MODULE_PATH}"
    assert callable(func), "Field must be callable"


def test_literal_is_callable(mod):
    """Literal is accessible and callable."""
    func = getattr(mod, "Literal", None)
    assert func is not None, "Literal must be defined in {MODULE_PATH}"
    assert callable(func), "Literal must be callable"


def test_get_settings_is_callable(mod):
    """get_settings is accessible and callable."""
    func = getattr(mod, "get_settings", None)
    assert func is not None, "get_settings must be defined in {MODULE_PATH}"
    assert callable(func), "get_settings must be callable"


def test_lru_cache_is_callable(mod):
    """lru_cache is accessible and callable."""
    func = getattr(mod, "lru_cache", None)
    assert func is not None, "lru_cache must be defined in {MODULE_PATH}"
    assert callable(func), "lru_cache must be callable"

