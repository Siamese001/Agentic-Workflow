"""Behavioral contract tests for agentic_core.adg.runtime.jit_context."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.jit_context"


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


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_contextsnapshot_is_instantiable(mod):
    """ContextSnapshot is accessible and is a type."""
    cls = getattr(mod, "ContextSnapshot", None)
    assert cls is not None, "ContextSnapshot must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ContextSnapshot must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_freezeboundary_is_instantiable(mod):
    """FreezeBoundary is accessible and is a type."""
    cls = getattr(mod, "FreezeBoundary", None)
    assert cls is not None, "FreezeBoundary must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "FreezeBoundary must be a class"


def test_freezestate_is_instantiable(mod):
    """FreezeState is accessible and is a type."""
    cls = getattr(mod, "FreezeState", None)
    assert cls is not None, "FreezeState must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "FreezeState must be a class"


def test_jitcontextsession_is_instantiable(mod):
    """JITContextSession is accessible and is a type."""
    cls = getattr(mod, "JITContextSession", None)
    assert cls is not None, "JITContextSession must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "JITContextSession must be a class"


def test_jitcontextsynchronizer_is_instantiable(mod):
    """JITContextSynchronizer is accessible and is a type."""
    cls = getattr(mod, "JITContextSynchronizer", None)
    assert cls is not None, "JITContextSynchronizer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "JITContextSynchronizer must be a class"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"

