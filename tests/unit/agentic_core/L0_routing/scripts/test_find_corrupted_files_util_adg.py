"""Behavioral contract tests for agentic_core.L0_routing.scripts.find_corrupted_files_util."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.find_corrupted_files_util"


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


def test_find_corruption_is_callable(mod):
    """find_corruption is accessible and callable."""
    func = getattr(mod, "find_corruption", None)
    assert func is not None, "find_corruption must be defined in {MODULE_PATH}"
    assert callable(func), "find_corruption must be callable"


def test_is_valid_python_is_callable(mod):
    """is_valid_python is accessible and callable."""
    func = getattr(mod, "is_valid_python", None)
    assert func is not None, "is_valid_python must be defined in {MODULE_PATH}"
    assert callable(func), "is_valid_python must be callable"


def test_main_is_callable(mod):
    """main is accessible and callable."""
    func = getattr(mod, "main", None)
    assert func is not None, "main must be defined in {MODULE_PATH}"
    assert callable(func), "main must be callable"


def test_safe_write_text_is_callable(mod):
    """safe_write_text is accessible and callable."""
    func = getattr(mod, "safe_write_text", None)
    assert func is not None, "safe_write_text must be defined in {MODULE_PATH}"
    assert callable(func), "safe_write_text must be callable"

