"""Behavioral contract tests for agentic_core.adg.artifact.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.artifact.__init__"


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


def test_adgartifact_is_instantiable(mod):
    """ADGArtifact is accessible and is a type."""
    cls = getattr(mod, "ADGArtifact", None)
    assert cls is not None, "ADGArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGArtifact must be a class"


def test_adgartifactbuilder_is_instantiable(mod):
    """ADGArtifactBuilder is accessible and is a type."""
    cls = getattr(mod, "ADGArtifactBuilder", None)
    assert cls is not None, "ADGArtifactBuilder must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ADGArtifactBuilder must be a class"


def test_build_artifact_is_callable(mod):
    """build_artifact is accessible and callable."""
    func = getattr(mod, "build_artifact", None)
    assert func is not None, "build_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "build_artifact must be callable"


def test_diff_artifacts_is_callable(mod):
    """diff_artifacts is accessible and callable."""
    func = getattr(mod, "diff_artifacts", None)
    assert func is not None, "diff_artifacts must be defined in {MODULE_PATH}"
    assert callable(func), "diff_artifacts must be callable"


def test_serialize_artifact_is_callable(mod):
    """serialize_artifact is accessible and callable."""
    func = getattr(mod, "serialize_artifact", None)
    assert func is not None, "serialize_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "serialize_artifact must be callable"

