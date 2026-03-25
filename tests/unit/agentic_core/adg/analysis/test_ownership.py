"""Behavioral contract tests for agentic_core.adg.analysis.ModuleOwnership."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.analysis.ModuleOwnership"


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


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_moduleownership_is_instantiable(mod):
    """ModuleOwnership is accessible and is a type."""
    cls = getattr(mod, "ModuleOwnership", None)
    assert cls is not None, "ModuleOwnership must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ModuleOwnership must be a class"


def test_ownershipregistry_is_instantiable(mod):
    """OwnershipRegistry is accessible and is a type."""
    cls = getattr(mod, "OwnershipRegistry", None)
    assert cls is not None, "OwnershipRegistry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "OwnershipRegistry must be a class"


def test_criticality_is_callable(mod):
    """Criticality is accessible and callable."""
    func = getattr(mod, "Criticality", None)
    assert func is not None, "Criticality must be defined in {MODULE_PATH}"
    assert callable(func), "Criticality must be callable"


def test_literal_is_callable(mod):
    """Literal is accessible and callable."""
    func = getattr(mod, "Literal", None)
    assert func is not None, "Literal must be defined in {MODULE_PATH}"
    assert callable(func), "Literal must be callable"


def test_owner_is_callable(mod):
    """Owner is accessible and callable."""
    func = getattr(mod, "Owner", None)
    assert func is not None, "Owner must be defined in {MODULE_PATH}"
    assert callable(func), "Owner must be callable"


def test_runtimesurface_is_callable(mod):
    """RuntimeSurface is accessible and callable."""
    func = getattr(mod, "RuntimeSurface", None)
    assert func is not None, "RuntimeSurface must be defined in {MODULE_PATH}"
    assert callable(func), "RuntimeSurface must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


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

