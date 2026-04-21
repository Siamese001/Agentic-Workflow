"""Shared smoke-test helpers for optional agentic_core imports."""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Any

import pytest


def import_module_or_skip(module_path: str) -> ModuleType:
    """Import a module or skip the test when agentic_core is unavailable."""
    pytest.importorskip(
        "agentic_core",
        reason="agentic_core runtime package is not available in this standalone test bundle",
    )
    try:
        return importlib.import_module(module_path)
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised in standalone bundles
        if exc.name and exc.name.startswith("agentic_core"):
            pytest.skip(f"Missing optional runtime dependency: {exc.name}")
        raise


def import_attr_or_skip(module_path: str, attr_name: str) -> Any:
    """Import an attribute from a module, skipping cleanly on missing runtime deps."""
    module = import_module_or_skip(module_path)
    return getattr(module, attr_name)  # guardian: allow-hallucinated-tool-name -- getattr is a Python stdlib builtin, not a hallucinated tool; detector false positive
