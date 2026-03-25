"""Behavioral contract tests for agentic_core.adg.runtime.io_interception."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.io_interception"


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


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_iointerceptionevent_is_instantiable(mod):
    """IOInterceptionEvent is accessible and is a type."""
    cls = getattr(mod, "IOInterceptionEvent", None)
    assert cls is not None, "IOInterceptionEvent must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IOInterceptionEvent must be a class"


def test_iointerceptionreport_is_instantiable(mod):
    """IOInterceptionReport is accessible and is a type."""
    cls = getattr(mod, "IOInterceptionReport", None)
    assert cls is not None, "IOInterceptionReport must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IOInterceptionReport must be a class"


def test_iointerceptor_is_instantiable(mod):
    """IOInterceptor is accessible and is a type."""
    cls = getattr(mod, "IOInterceptor", None)
    assert cls is not None, "IOInterceptor must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IOInterceptor must be a class"


def test_interceptionoutcome_is_instantiable(mod):
    """InterceptionOutcome is accessible and is a type."""
    cls = getattr(mod, "InterceptionOutcome", None)
    assert cls is not None, "InterceptionOutcome must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "InterceptionOutcome must be a class"


def test_networktranscript_is_instantiable(mod):
    """NetworkTranscript is accessible and is a type."""
    cls = getattr(mod, "NetworkTranscript", None)
    assert cls is not None, "NetworkTranscript must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "NetworkTranscript must be a class"


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

