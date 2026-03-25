"""Behavioral contract tests for agentic_core.adg.runtime.cache_loader."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.cache_loader"


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


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_invalidate_cache_is_callable(mod):
    """invalidate_cache is accessible and callable."""
    func = getattr(mod, "invalidate_cache", None)
    assert func is not None, "invalidate_cache must be defined in {MODULE_PATH}"
    assert callable(func), "invalidate_cache must be callable"


def test_load_or_scan_is_callable(mod):
    """load_or_scan is accessible and callable."""
    func = getattr(mod, "load_or_scan", None)
    assert func is not None, "load_or_scan must be defined in {MODULE_PATH}"
    assert callable(func), "load_or_scan must be callable"

