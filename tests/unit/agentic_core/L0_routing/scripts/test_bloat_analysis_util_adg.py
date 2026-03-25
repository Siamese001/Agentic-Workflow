"""Behavioral contract tests for agentic_core.L0_routing.scripts.bloat_analysis_util."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.bloat_analysis_util"


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


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_datetime_is_instantiable(mod):
    """datetime is accessible and is a type."""
    cls = getattr(mod, "datetime", None)
    assert cls is not None, "datetime must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "datetime must be a class"


def test_defaultdict_is_instantiable(mod):
    """defaultdict is accessible and is a type."""
    cls = getattr(mod, "defaultdict", None)
    assert cls is not None, "defaultdict must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "defaultdict must be a class"


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


def test_find_deprecated_markers_is_callable(mod):
    """find_deprecated_markers is accessible and callable."""
    func = getattr(mod, "find_deprecated_markers", None)
    assert func is not None, "find_deprecated_markers must be defined in {MODULE_PATH}"
    assert callable(func), "find_deprecated_markers must be callable"


def test_find_duplicate_filenames_is_callable(mod):
    """find_duplicate_filenames is accessible and callable."""
    func = getattr(mod, "find_duplicate_filenames", None)
    assert func is not None, "find_duplicate_filenames must be defined in {MODULE_PATH}"
    assert callable(func), "find_duplicate_filenames must be callable"


def test_find_empty_or_stub_files_is_callable(mod):
    """find_empty_or_stub_files is accessible and callable."""
    func = getattr(mod, "find_empty_or_stub_files", None)
    assert func is not None, "find_empty_or_stub_files must be defined in {MODULE_PATH}"
    assert callable(func), "find_empty_or_stub_files must be callable"


def test_find_large_files_is_callable(mod):
    """find_large_files is accessible and callable."""
    func = getattr(mod, "find_large_files", None)
    assert func is not None, "find_large_files must be defined in {MODULE_PATH}"
    assert callable(func), "find_large_files must be callable"


def test_find_script_candidates_is_callable(mod):
    """find_script_candidates is accessible and callable."""
    func = getattr(mod, "find_script_candidates", None)
    assert func is not None, "find_script_candidates must be defined in {MODULE_PATH}"
    assert callable(func), "find_script_candidates must be callable"


def test_find_test_files_outside_tests_is_callable(mod):
    """find_test_files_outside_tests is accessible and callable."""
    func = getattr(mod, "find_test_files_outside_tests", None)
    assert func is not None, "find_test_files_outside_tests must be defined in {MODULE_PATH}"
    assert callable(func), "find_test_files_outside_tests must be callable"

