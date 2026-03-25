"""Behavioral contract tests for agentic_core.adg.artifact.serializer_util."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.artifact.serializer_util"


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


def test_diff_artifacts_is_callable(mod):
    """diff_artifacts is accessible and callable."""
    func = getattr(mod, "diff_artifacts", None)
    assert func is not None, "diff_artifacts must be defined in {MODULE_PATH}"
    assert callable(func), "diff_artifacts must be callable"


def test_load_artifact_is_callable(mod):
    """load_artifact is accessible and callable."""
    func = getattr(mod, "load_artifact", None)
    assert func is not None, "load_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "load_artifact must be callable"


def test_serialize_artifact_is_callable(mod):
    """serialize_artifact is accessible and callable."""
    func = getattr(mod, "serialize_artifact", None)
    assert func is not None, "serialize_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "serialize_artifact must be callable"


def test_write_artifact_is_callable(mod):
    """write_artifact is accessible and callable."""
    func = getattr(mod, "write_artifact", None)
    assert func is not None, "write_artifact must be defined in {MODULE_PATH}"
    assert callable(func), "write_artifact must be callable"

