"""Behavioral contract tests for agentic_core.L0_routing.types.determinism_contracts_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.types.determinism_contracts_types"


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


def test_boundarysnapshotartifact_is_instantiable(mod):
    """BoundarySnapshotArtifact is accessible and is a type."""
    cls = getattr(mod, "BoundarySnapshotArtifact", None)
    assert cls is not None, "BoundarySnapshotArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BoundarySnapshotArtifact must be a class"


def test_canonicalastresult_is_instantiable(mod):
    """CanonicalASTResult is accessible and is a type."""
    cls = getattr(mod, "CanonicalASTResult", None)
    assert cls is not None, "CanonicalASTResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CanonicalASTResult must be a class"


def test_episodicmemorynotqueried_is_instantiable(mod):
    """EpisodicMemoryNotQueried is accessible and is a type."""
    cls = getattr(mod, "EpisodicMemoryNotQueried", None)
    assert cls is not None, "EpisodicMemoryNotQueried must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "EpisodicMemoryNotQueried must be a class"


def test_forbiddeninputerror_is_instantiable(mod):
    """ForbiddenInputError is accessible and is a type."""
    cls = getattr(mod, "ForbiddenInputError", None)
    assert cls is not None, "ForbiddenInputError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ForbiddenInputError must be a class"


def test_rollbackhashmismatch_is_instantiable(mod):
    """RollbackHashMismatch is accessible and is a type."""
    cls = getattr(mod, "RollbackHashMismatch", None)
    assert cls is not None, "RollbackHashMismatch must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RollbackHashMismatch must be a class"


def test_semanticclock_is_instantiable(mod):
    """SemanticClock is accessible and is a type."""
    cls = getattr(mod, "SemanticClock", None)
    assert cls is not None, "SemanticClock must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SemanticClock must be a class"


def test_surgicalmanifest_is_instantiable(mod):
    """SurgicalManifest is accessible and is a type."""
    cls = getattr(mod, "SurgicalManifest", None)
    assert cls is not None, "SurgicalManifest must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SurgicalManifest must be a class"


def test_ast_scan_wall_clock_is_callable(mod):
    """ast_scan_wall_clock is accessible and callable."""
    func = getattr(mod, "ast_scan_wall_clock", None)
    assert func is not None, "ast_scan_wall_clock must be defined in {MODULE_PATH}"
    assert callable(func), "ast_scan_wall_clock must be callable"


def test_canonical_ast_serialize_is_callable(mod):
    """canonical_ast_serialize is accessible and callable."""
    func = getattr(mod, "canonical_ast_serialize", None)
    assert func is not None, "canonical_ast_serialize must be defined in {MODULE_PATH}"
    assert callable(func), "canonical_ast_serialize must be callable"


def test_check_forbidden_input_type_is_callable(mod):
    """check_forbidden_input_type is accessible and callable."""
    func = getattr(mod, "check_forbidden_input_type", None)
    assert func is not None, "check_forbidden_input_type must be defined in {MODULE_PATH}"
    assert callable(func), "check_forbidden_input_type must be callable"


def test_check_velocity_threshold_is_callable(mod):
    """check_velocity_threshold is accessible and callable."""
    func = getattr(mod, "check_velocity_threshold", None)
    assert func is not None, "check_velocity_threshold must be defined in {MODULE_PATH}"
    assert callable(func), "check_velocity_threshold must be callable"


def test_create_boundary_snapshot_is_callable(mod):
    """create_boundary_snapshot is accessible and callable."""
    func = getattr(mod, "create_boundary_snapshot", None)
    assert func is not None, "create_boundary_snapshot must be defined in {MODULE_PATH}"
    assert callable(func), "create_boundary_snapshot must be callable"


def test_dedupe_check_is_callable(mod):
    """dedupe_check is accessible and callable."""
    func = getattr(mod, "dedupe_check", None)
    assert func is not None, "dedupe_check must be defined in {MODULE_PATH}"
    assert callable(func), "dedupe_check must be callable"


def test_dedupe_sha256_is_callable(mod):
    """dedupe_sha256 is accessible and callable."""
    func = getattr(mod, "dedupe_sha256", None)
    assert func is not None, "dedupe_sha256 must be defined in {MODULE_PATH}"
    assert callable(func), "dedupe_sha256 must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"

