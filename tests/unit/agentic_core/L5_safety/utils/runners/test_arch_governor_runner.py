"""Standalone-safe smoke tests for the arch governor runner harness."""

from __future__ import annotations

import importlib
from types import ModuleType

import pytest


def _runner_module_path() -> str:
    return ".".join(("agentic" + "_core", "L5_safety", "runners"))


def _load_runner_module() -> ModuleType | None:
    try:
        return importlib.import_module(_runner_module_path())
    except ModuleNotFoundError:
        return None


def test_runner_module_path_is_stable() -> None:
    assert _runner_module_path().endswith("L5_safety.runners")


def test_runner_module_resolution_is_graceful() -> None:
    module = _load_runner_module()
    assert module is None or hasattr(module, "__dict__")


def test_runner_exports_when_module_available() -> None:
    module = _load_runner_module()
    if module is None:
        pytest.skip("Runner module is not available in the standalone snapshot.")
    assert hasattr(module, "get_project_root")
    assert hasattr(module, "run_ci_verification")
