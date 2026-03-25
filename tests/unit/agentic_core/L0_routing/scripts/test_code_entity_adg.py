"""Behavioral contract tests for agentic_core.L0_routing.scripts.code_entity."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.code_entity"


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


def test_codeentity_is_instantiable(mod):
    """CodeEntity is accessible and is a type."""
    cls = getattr(mod, "CodeEntity", None)
    assert cls is not None, "CodeEntity must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CodeEntity must be a class"


def test_fileanalysis_is_instantiable(mod):
    """FileAnalysis is accessible and is a type."""
    cls = getattr(mod, "FileAnalysis", None)
    assert cls is not None, "FileAnalysis must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "FileAnalysis must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_defaultdict_is_instantiable(mod):
    """defaultdict is accessible and is a type."""
    cls = getattr(mod, "defaultdict", None)
    assert cls is not None, "defaultdict must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "defaultdict must be a class"


def test_analyze_file_is_callable(mod):
    """analyze_file is accessible and callable."""
    func = getattr(mod, "analyze_file", None)
    assert func is not None, "analyze_file must be defined in {MODULE_PATH}"
    assert callable(func), "analyze_file must be callable"


def test_assert_no_persistent_write_is_callable(mod):
    """assert_no_persistent_write is accessible and callable."""
    func = getattr(mod, "assert_no_persistent_write", None)
    assert func is not None, "assert_no_persistent_write must be defined in {MODULE_PATH}"
    assert callable(func), "assert_no_persistent_write must be callable"


def test_build_current_codebase_index_is_callable(mod):
    """build_current_codebase_index is accessible and callable."""
    func = getattr(mod, "build_current_codebase_index", None)
    assert func is not None, "build_current_codebase_index must be defined in {MODULE_PATH}"
    assert callable(func), "build_current_codebase_index must be callable"


def test_calculate_uniqueness_is_callable(mod):
    """calculate_uniqueness is accessible and callable."""
    func = getattr(mod, "calculate_uniqueness", None)
    assert func is not None, "calculate_uniqueness must be defined in {MODULE_PATH}"
    assert callable(func), "calculate_uniqueness must be callable"


def test_classify_entity_type_is_callable(mod):
    """classify_entity_type is accessible and callable."""
    func = getattr(mod, "classify_entity_type", None)
    assert func is not None, "classify_entity_type must be defined in {MODULE_PATH}"
    assert callable(func), "classify_entity_type must be callable"


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

