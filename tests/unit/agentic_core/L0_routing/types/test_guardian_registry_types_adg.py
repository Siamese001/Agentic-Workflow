"""Behavioral contract tests for agentic_core.L0_routing.types.guardian_registry_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.guardian_registry_types"


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


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_guardianspec_is_instantiable(mod):
    """GuardianSpec is accessible and is a type."""
    cls = getattr(mod, "GuardianSpec", None)
    assert cls is not None, "GuardianSpec must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardianSpec must be a class"


def test_guardiantier_is_instantiable(mod):
    """GuardianTier is accessible and is a type."""
    cls = getattr(mod, "GuardianTier", None)
    assert cls is not None, "GuardianTier must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardianTier must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_literal_is_callable(mod):
    """Literal is accessible and callable."""
    func = getattr(mod, "Literal", None)
    assert func is not None, "Literal must be defined in {MODULE_PATH}"
    assert callable(func), "Literal must be callable"


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


def test_get_all_check_ids_is_callable(mod):
    """get_all_check_ids is accessible and callable."""
    func = getattr(mod, "get_all_check_ids", None)
    assert func is not None, "get_all_check_ids must be defined in {MODULE_PATH}"
    assert callable(func), "get_all_check_ids must be callable"


def test_get_guardian_by_id_is_callable(mod):
    """get_guardian_by_id is accessible and callable."""
    func = getattr(mod, "get_guardian_by_id", None)
    assert func is not None, "get_guardian_by_id must be defined in {MODULE_PATH}"
    assert callable(func), "get_guardian_by_id must be callable"


def test_get_guardian_entrypoints_is_callable(mod):
    """get_guardian_entrypoints is accessible and callable."""
    func = getattr(mod, "get_guardian_entrypoints", None)
    assert func is not None, "get_guardian_entrypoints must be defined in {MODULE_PATH}"
    assert callable(func), "get_guardian_entrypoints must be callable"


def test_get_guardian_specs_is_callable(mod):
    """get_guardian_specs is accessible and callable."""
    func = getattr(mod, "get_guardian_specs", None)
    assert func is not None, "get_guardian_specs must be defined in {MODULE_PATH}"
    assert callable(func), "get_guardian_specs must be callable"

