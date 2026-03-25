"""Behavioral contract tests for agentic_core.adg.analysis.test_gap_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.analysis.test_gap_types"


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


def test_testgapentry_is_instantiable(mod):
    """TestGapEntry is accessible and is a type."""
    cls = getattr(mod, "TestGapEntry", None)
    assert cls is not None, "TestGapEntry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "TestGapEntry must be a class"


def test_testgapreport_is_instantiable(mod):
    """TestGapReport is accessible and is a type."""
    cls = getattr(mod, "TestGapReport", None)
    assert cls is not None, "TestGapReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "TestGapReport must be a class"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_detect_test_gaps_is_callable(mod):
    """detect_test_gaps is accessible and callable."""
    func = getattr(mod, "detect_test_gaps", None)
    assert func is not None, "detect_test_gaps must be defined in {MODULE_PATH}"
    assert callable(func), "detect_test_gaps must be callable"


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


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"


def test_module_path_to_layer_is_callable(mod):
    """module_path_to_layer is accessible and callable."""
    func = getattr(mod, "module_path_to_layer", None)
    assert func is not None, "module_path_to_layer must be defined in {MODULE_PATH}"
    assert callable(func), "module_path_to_layer must be callable"

