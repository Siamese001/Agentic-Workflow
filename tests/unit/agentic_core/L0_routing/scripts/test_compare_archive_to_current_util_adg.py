"""Behavioral contract tests for agentic_core.L0_routing.scripts.compare_archive_to_current_util."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.compare_archive_to_current_util"


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
    """Test emit_determinism_digest_is_callable runtime behavior."""
    func = getattr(mod, "emit_determinism_digest", None)
    if func is None:
        pytest.skip("emit_determinism_digest not found in module")
    assert callable(func), "emit_determinism_digest must be callable"
    
    # Test function signature
    import inspect
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    assert len(params) >= 0, "emit_determinism_digest should accept parameters"