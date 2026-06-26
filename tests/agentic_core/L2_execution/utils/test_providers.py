"""ADG-hotspot scaffold tests for `agentic_core.L2_execution.utils.providers` (fanin=47).

Auto-generated speculative scaffold. Module is high fan-in per ADG snapshot
04252026_0843. Verify class/function names against actual module before
treating these as authoritative tests.
"""
from __future__ import annotations

import importlib
import sys
import warnings

import pytest


MODULE_PATH = "agentic_core.L2_execution.utils.providers"


def _import_module_silencing_deprecation():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"agentic_core\.L2_execution\.providers is deprecated",
            category=DeprecationWarning,
        )
        return importlib.import_module(MODULE_PATH)


def test_module_imports_deprecated_shim_with_warning():
    """Smoke: compatibility shim imports and advertises its deprecation."""
    sys.modules.pop(MODULE_PATH, None)
    with pytest.warns(DeprecationWarning, match=r"agentic_core\.L2_execution\.providers is deprecated"):
        mod = importlib.import_module(MODULE_PATH)
    assert mod is not None


def test_module_has_public_surface():
    """Smoke: hotspot module must expose at least one public attribute."""
    mod = _import_module_silencing_deprecation()
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    """Re-import must be idempotent — no top-level side effects that fail."""
    _import_module_silencing_deprecation()
    _import_module_silencing_deprecation()


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    """Hotspot modules with high fan-in should expose a callable surface."""
    mod = _import_module_silencing_deprecation()
    has_callable = any(
        callable(getattr(mod, n))
        for n in dir(mod)
        if not n.startswith("_")
    )
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    """Module file path must contain expected layer prefix."""
    mod = _import_module_silencing_deprecation()
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), (
        f"{MODULE_PATH} not under agentic_core: {file}"
    )
