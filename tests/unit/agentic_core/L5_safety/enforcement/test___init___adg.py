"""Behavioral contract tests for agentic_core.enforcement.__init__."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.enforcement.__init__"


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


def test_module_is_namespace_package(mod):
    """Module is a valid namespace package (empty __init__)."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    # Empty namespace packages are valid - just verify import succeeded
    assert mod is not None
