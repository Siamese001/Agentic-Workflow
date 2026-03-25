"""Behavioral contract tests for agentic_core.adg.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.__init__"


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


def test_edgekind_is_callable(mod):
    """EdgeKind is accessible and callable."""
    func = getattr(mod, "EdgeKind", None)
    assert func is not None, "EdgeKind must be defined in {MODULE_PATH}"
    assert callable(func), "EdgeKind must be callable"


def test_entitytype_is_callable(mod):
    """EntityType is accessible and callable."""
    func = getattr(mod, "EntityType", None)
    assert func is not None, "EntityType must be defined in {MODULE_PATH}"
    assert callable(func), "EntityType must be callable"


def test_relationtype_is_callable(mod):
    """RelationType is accessible and callable."""
    func = getattr(mod, "RelationType", None)
    assert func is not None, "RelationType must be defined in {MODULE_PATH}"
    assert callable(func), "RelationType must be callable"


def test_canonical_name_is_callable(mod):
    """canonical_name is accessible and callable."""
    func = getattr(mod, "canonical_name", None)
    assert func is not None, "canonical_name must be defined in {MODULE_PATH}"
    assert callable(func), "canonical_name must be callable"

