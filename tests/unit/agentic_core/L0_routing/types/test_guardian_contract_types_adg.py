"""Behavioral contract tests for agentic_core.L0_routing.types.guardian_contract_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.guardian_contract_types"


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


def test_artifactclass_is_instantiable(mod):
    """ArtifactClass is accessible and is a type."""
    cls = getattr(mod, "ArtifactClass", None)
    assert cls is not None, "ArtifactClass must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ArtifactClass must be a class"


def test_artifacttype_is_instantiable(mod):
    """ArtifactType is accessible and is a type."""
    cls = getattr(mod, "ArtifactType", None)
    assert cls is not None, "ArtifactType must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ArtifactType must be a class"


def test_checkstatus_is_instantiable(mod):
    """CheckStatus is accessible and is a type."""
    cls = getattr(mod, "CheckStatus", None)
    assert cls is not None, "CheckStatus must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CheckStatus must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_guardianartifact_is_instantiable(mod):
    """GuardianArtifact is accessible and is a type."""
    cls = getattr(mod, "GuardianArtifact", None)
    assert cls is not None, "GuardianArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardianArtifact must be a class"


def test_guardiancheck_is_instantiable(mod):
    """GuardianCheck is accessible and is a type."""
    cls = getattr(mod, "GuardianCheck", None)
    assert cls is not None, "GuardianCheck must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardianCheck must be a class"


def test_guardianresult_is_instantiable(mod):
    """GuardianResult is accessible and is a type."""
    cls = getattr(mod, "GuardianResult", None)
    assert cls is not None, "GuardianResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardianResult must be a class"


def test_asdict_is_callable(mod):
    """asdict is accessible and callable."""
    func = getattr(mod, "asdict", None)
    assert func is not None, "asdict must be defined in {MODULE_PATH}"
    assert callable(func), "asdict must be callable"


def test_assert_no_persistent_write_is_callable(mod):
    """assert_no_persistent_write is accessible and callable."""
    func = getattr(mod, "assert_no_persistent_write", None)
    assert func is not None, "assert_no_persistent_write must be defined in {MODULE_PATH}"
    assert callable(func), "assert_no_persistent_write must be callable"


def test_check_schema_compatibility_is_callable(mod):
    """check_schema_compatibility is accessible and callable."""
    func = getattr(mod, "check_schema_compatibility", None)
    assert func is not None, "check_schema_compatibility must be defined in {MODULE_PATH}"
    assert callable(func), "check_schema_compatibility must be callable"


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


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"


def test_get_artifact_filename_is_callable(mod):
    """get_artifact_filename is accessible and callable."""
    func = getattr(mod, "get_artifact_filename", None)
    assert func is not None, "get_artifact_filename must be defined in {MODULE_PATH}"
    assert callable(func), "get_artifact_filename must be callable"

