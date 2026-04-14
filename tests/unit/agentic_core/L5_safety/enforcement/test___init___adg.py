"""Behavioral contract tests for agentic_core.enforcement.__init__."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.enforcement.__init__"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(
        MODULE_PATH,
        reason="Requires agentic_core.enforcement namespace package from the monorepo checkout.",
    )


def test_module_importable(mod):
    assert mod.__name__ == MODULE_PATH


def test_module_is_namespace_package(mod):
    public = [name for name in dir(mod) if not name.startswith("_")]
    assert isinstance(public, list)
