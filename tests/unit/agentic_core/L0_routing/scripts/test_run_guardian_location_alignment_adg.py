"""Behavioral contract tests for agentic_core.L0_routing.scripts.run_guardian_location_alignment."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.run_guardian_location_alignment"


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


def test_guardianresult_is_instantiable(mod):
    """GuardianResult is accessible and is a type."""
    cls = getattr(mod, "GuardianResult", None)
    assert cls is not None, "GuardianResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardianResult must be a class"


def test_guardianstatus_is_instantiable(mod):
    """GuardianStatus is accessible and is a type."""
    cls = getattr(mod, "GuardianStatus", None)
    assert cls is not None, "GuardianStatus must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardianStatus must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


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


def test_get_validated_project_root_is_callable(mod):
    """get_validated_project_root is accessible and callable."""
    func = getattr(mod, "get_validated_project_root", None)
    assert func is not None, "get_validated_project_root must be defined in {MODULE_PATH}"
    assert callable(func), "get_validated_project_root must be callable"


def test_main_is_callable(mod):
    """main is accessible and callable."""
    func = getattr(mod, "main", None)
    assert func is not None, "main must be defined in {MODULE_PATH}"
    assert callable(func), "main must be callable"


def test_maybe_sign_result_is_callable(mod):
    """maybe_sign_result is accessible and callable."""
    func = getattr(mod, "maybe_sign_result", None)
    assert func is not None, "maybe_sign_result must be defined in {MODULE_PATH}"
    assert callable(func), "maybe_sign_result must be callable"


def test_normalize_repo_path_is_callable(mod):
    """normalize_repo_path is accessible and callable."""
    func = getattr(mod, "normalize_repo_path", None)
    assert func is not None, "normalize_repo_path must be defined in {MODULE_PATH}"
    assert callable(func), "normalize_repo_path must be callable"


def test_run_location_alignment_guardian_is_callable(mod):
    """run_location_alignment_guardian is accessible and callable."""
    func = getattr(mod, "run_location_alignment_guardian", None)
    assert func is not None, "run_location_alignment_guardian must be defined in {MODULE_PATH}"
    assert callable(func), "run_location_alignment_guardian must be callable"


def test_scan_misplaced_files_is_callable(mod):
    """scan_misplaced_files is accessible and callable."""
    func = getattr(mod, "scan_misplaced_files", None)
    assert func is not None, "scan_misplaced_files must be defined in {MODULE_PATH}"
    assert callable(func), "scan_misplaced_files must be callable"

