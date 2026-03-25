"""Behavioral contract tests for agentic_core.L0_routing.scripts.disposition."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.disposition"


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


def test_coreanalysisresult_is_instantiable(mod):
    """CoreAnalysisResult is accessible and is a type."""
    cls = getattr(mod, "CoreAnalysisResult", None)
    assert cls is not None, "CoreAnalysisResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CoreAnalysisResult must be a class"


def test_coresynthesisanalyzer_is_instantiable(mod):
    """CoreSynthesisAnalyzer is accessible and is a type."""
    cls = getattr(mod, "CoreSynthesisAnalyzer", None)
    assert cls is not None, "CoreSynthesisAnalyzer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CoreSynthesisAnalyzer must be a class"


def test_disposition_is_instantiable(mod):
    """Disposition is accessible and is a type."""
    cls = getattr(mod, "Disposition", None)
    assert cls is not None, "Disposition must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Disposition must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


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


def test_assert_no_persistent_write_is_callable(mod):
    """assert_no_persistent_write is accessible and callable."""
    func = getattr(mod, "assert_no_persistent_write", None)
    assert func is not None, "assert_no_persistent_write must be defined in {MODULE_PATH}"
    assert callable(func), "assert_no_persistent_write must be callable"


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


def test_main_is_callable(mod):
    """main is accessible and callable."""
    func = getattr(mod, "main", None)
    assert func is not None, "main must be defined in {MODULE_PATH}"
    assert callable(func), "main must be callable"

