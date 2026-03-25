"""Behavioral contract tests for agentic_core.adg.ci.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.adg.ci.__init__"


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


def test_invariantscanner_is_instantiable(mod):
    """InvariantScanner is accessible and is a type."""
    cls = getattr(mod, "InvariantScanner", None)
    assert cls is not None, "InvariantScanner must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "InvariantScanner must be a class"


def test_violation_is_instantiable(mod):
    """Violation is accessible and is a type."""
    cls = getattr(mod, "Violation", None)
    assert cls is not None, "Violation must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Violation must be a class"

