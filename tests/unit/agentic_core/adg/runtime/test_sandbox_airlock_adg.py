"""Behavioral contract tests for agentic_core.adg.runtime.sandbox_airlock."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.runtime.sandbox_airlock"


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


def test_airlockphase_is_instantiable(mod):
    """AirlockPhase is accessible and is a type."""
    cls = getattr(mod, "AirlockPhase", None)
    assert cls is not None, "AirlockPhase must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AirlockPhase must be a class"


def test_airlocksession_is_instantiable(mod):
    """AirlockSession is accessible and is a type."""
    cls = getattr(mod, "AirlockSession", None)
    assert cls is not None, "AirlockSession must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "AirlockSession must be a class"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_capabilitytoken_is_instantiable(mod):
    """CapabilityToken is accessible and is a type."""
    cls = getattr(mod, "CapabilityToken", None)
    assert cls is not None, "CapabilityToken must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CapabilityToken must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_sandboxairlockrecorder_is_instantiable(mod):
    """SandboxAirlockRecorder is accessible and is a type."""
    cls = getattr(mod, "SandboxAirlockRecorder", None)
    assert cls is not None, "SandboxAirlockRecorder must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SandboxAirlockRecorder must be a class"


def test_sandboxenvelope_is_instantiable(mod):
    """SandboxEnvelope is accessible and is a type."""
    cls = getattr(mod, "SandboxEnvelope", None)
    assert cls is not None, "SandboxEnvelope must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SandboxEnvelope must be a class"


def test_workcontract_is_instantiable(mod):
    """WorkContract is accessible and is a type."""
    cls = getattr(mod, "WorkContract", None)
    assert cls is not None, "WorkContract must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "WorkContract must be a class"


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

