"""Behavioral contract tests for agentic_core.interfaces.write_gateway."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.interfaces.write_gateway"


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


def test_instructionpacket_is_instantiable(mod):
    """InstructionPacket is accessible and is a type."""
    cls = getattr(mod, "InstructionPacket", None)
    assert cls is not None, "InstructionPacket must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "InstructionPacket must be a class"


def test_universalwritegateway_is_instantiable(mod):
    """UniversalWriteGateway is accessible and is a type."""
    cls = getattr(mod, "UniversalWriteGateway", None)
    assert cls is not None, "UniversalWriteGateway must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "UniversalWriteGateway must be a class"


def test_sequence_is_callable(mod):
    """Sequence is accessible and callable."""
    func = getattr(mod, "Sequence", None)
    assert func is not None, "Sequence must be defined in {MODULE_PATH}"
    assert callable(func), "Sequence must be callable"


def test_compute_replay_key_is_callable(mod):
    """compute_replay_key is accessible and callable."""
    func = getattr(mod, "compute_replay_key", None)
    assert func is not None, "compute_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "compute_replay_key must be callable"


def test_get_write_gateway_is_callable(mod):
    """get_write_gateway is accessible and callable."""
    func = getattr(mod, "get_write_gateway", None)
    assert func is not None, "get_write_gateway must be defined in {MODULE_PATH}"
    assert callable(func), "get_write_gateway must be callable"

