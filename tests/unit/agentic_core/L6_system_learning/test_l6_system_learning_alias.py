"""Post-W5 canonical path smoke test for agentic_core.L6_system_learning."""
from __future__ import annotations

import importlib

import pytest

SUBPACKAGES_WITH_INIT = (
    "adapters",
    "engines",
    "meta_learning",
    "ports",
    "validators",
)


def test_canonical_package_importable() -> None:
    pkg = importlib.import_module("agentic_core.L6_system_learning")
    assert getattr(pkg, "__layer__", None) == "L6"
    assert getattr(pkg, "__l6_surface__", None) == "active"


@pytest.mark.parametrize("subname", SUBPACKAGES_WITH_INIT)
def test_subpackage_importable(subname: str) -> None:
    mod = importlib.import_module(f"agentic_core.L6_system_learning.{subname}")
    assert getattr(mod, "__layer__", None) == "L6"
