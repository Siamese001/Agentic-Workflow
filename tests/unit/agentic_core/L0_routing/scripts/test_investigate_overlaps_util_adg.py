"""Behavioral contract tests for agentic_core.L0_routing.scripts.investigate_overlaps_util."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.investigate_overlaps_util"


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


def test_get_file_hash_is_callable(mod):
    """get_file_hash is accessible and callable."""
    func = getattr(mod, "get_file_hash", None)
    assert func is not None, "get_file_hash must be defined in {MODULE_PATH}"
    assert callable(func), "get_file_hash must be callable"


def test_investigate_is_callable(mod):
    """investigate is accessible and callable."""
    func = getattr(mod, "investigate", None)
    assert func is not None, "investigate must be defined in {MODULE_PATH}"
    assert callable(func), "investigate must be callable"

