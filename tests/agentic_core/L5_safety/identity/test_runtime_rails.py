"""ADG-hotspot scaffold tests for `agentic_core.L5_safety.identity.runtime_rails` (fanin=3).

Auto-generated speculative scaffold. Module is high fan-in per ADG snapshot
04252026_0843. Verify class/function names against actual module before
extending these scaffolds with behavioral assertions.
"""
from __future__ import annotations

import importlib

import pytest


MODULE_PATH = "agentic_core.L5_safety.identity.runtime_rails"


def test_module_imports():
    """Smoke: hotspot module must import cleanly (high fan-in regression guard)."""
    mod = importlib.import_module(MODULE_PATH)
    assert mod is not None


def test_module_has_public_surface():
    """Smoke: hotspot module must expose at least one public attribute."""
    mod = importlib.import_module(MODULE_PATH)
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    """Re-import must be idempotent — no top-level side effects that fail."""
    importlib.import_module(MODULE_PATH)
    importlib.import_module(MODULE_PATH)


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    """Hotspot modules with high fan-in should expose a callable surface."""
    mod = importlib.import_module(MODULE_PATH)
    has_callable = any(
        callable(getattr(mod, n))
        for n in dir(mod)
        if not n.startswith("_")
    )
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    """Module file path must contain expected layer prefix."""
    mod = importlib.import_module(MODULE_PATH)
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), (
        f"{MODULE_PATH} not under agentic_core: {file}"
    )
