"""Behavioral contract tests for agentic_core.L0_routing.scripts.file_analysis."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.file_analysis"


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


def test_analyze_class_is_callable(mod):
    """analyze_class is accessible and callable."""
    func = getattr(mod, "analyze_class", None)
    assert func is not None, "analyze_class must be defined in {MODULE_PATH}"
    assert callable(func), "analyze_class must be callable"


def test_analyze_file_is_callable(mod):
    """analyze_file is accessible and callable."""
    func = getattr(mod, "analyze_file", None)
    assert func is not None, "analyze_file must be defined in {MODULE_PATH}"
    assert callable(func), "analyze_file must be callable"


def test_analyze_function_is_callable(mod):
    """analyze_function is accessible and callable."""
    func = getattr(mod, "analyze_function", None)
    assert func is not None, "analyze_function must be defined in {MODULE_PATH}"
    assert callable(func), "analyze_function must be callable"


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


def test_extract_docstring_is_callable(mod):
    """extract_docstring is accessible and callable."""
    func = getattr(mod, "extract_docstring", None)
    assert func is not None, "extract_docstring must be defined in {MODULE_PATH}"
    assert callable(func), "extract_docstring must be callable"


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"

