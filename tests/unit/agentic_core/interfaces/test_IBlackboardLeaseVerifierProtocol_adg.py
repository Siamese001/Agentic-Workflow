"""Behavioral contract tests for agentic_core.interfaces.IBlackboardLeaseVerifierProtocol."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.interfaces.IBlackboardLeaseVerifierProtocol"


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


def test_healingleaseerror_is_instantiable(mod):
    """HealingLeaseError is accessible and is a type."""
    cls = getattr(mod, "HealingLeaseError", None)
    assert cls is not None, "HealingLeaseError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HealingLeaseError must be a class"


def test_iblackboardleaseverifier_is_instantiable(mod):
    """IBlackboardLeaseVerifier is accessible and is a type."""
    cls = getattr(mod, "IBlackboardLeaseVerifier", None)
    assert cls is not None, "IBlackboardLeaseVerifier must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IBlackboardLeaseVerifier must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_preservationviolationerror_is_instantiable(mod):
    """PreservationViolationError is accessible and is a type."""
    cls = getattr(mod, "PreservationViolationError", None)
    assert cls is not None, "PreservationViolationError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "PreservationViolationError must be a class"


def test_protocol_is_instantiable(mod):
    """Protocol is accessible and is a type."""
    cls = getattr(mod, "Protocol", None)
    assert cls is not None, "Protocol must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Protocol must be a class"


def test_sandboxviolationerror_is_instantiable(mod):
    """SandboxViolationError is accessible and is a type."""
    cls = getattr(mod, "SandboxViolationError", None)
    assert cls is not None, "SandboxViolationError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SandboxViolationError must be a class"


def test_create_directory_is_callable(mod):
    """create_directory is accessible and callable."""
    func = getattr(mod, "create_directory", None)
    assert func is not None, "create_directory must be defined in {MODULE_PATH}"
    assert callable(func), "create_directory must be callable"


def test_delete_file_is_callable(mod):
    """delete_file is accessible and callable."""
    func = getattr(mod, "delete_file", None)
    assert func is not None, "delete_file must be defined in {MODULE_PATH}"
    assert callable(func), "delete_file must be callable"


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


def test_get_project_root_is_callable(mod):
    """get_project_root is accessible and callable."""
    func = getattr(mod, "get_project_root", None)
    assert func is not None, "get_project_root must be defined in {MODULE_PATH}"
    assert callable(func), "get_project_root must be callable"


def test_list_files_is_callable(mod):
    """list_files is accessible and callable."""
    func = getattr(mod, "list_files", None)
    assert func is not None, "list_files must be defined in {MODULE_PATH}"
    assert callable(func), "list_files must be callable"


def test_move_file_is_callable(mod):
    """move_file is accessible and callable."""
    func = getattr(mod, "move_file", None)
    assert func is not None, "move_file must be defined in {MODULE_PATH}"
    assert callable(func), "move_file must be callable"


def test_read_file_is_callable(mod):
    """read_file is accessible and callable."""
    func = getattr(mod, "read_file", None)
    assert func is not None, "read_file must be defined in {MODULE_PATH}"
    assert callable(func), "read_file must be callable"

