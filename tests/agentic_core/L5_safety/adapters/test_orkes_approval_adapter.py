"""ADG-hotspot scaffold tests for `agentic_core.L5_safety.adapters.orkes_approval_adapter` (fanin=2).

Auto-generated speculative scaffold. Module is high fan-in per ADG snapshot
04252026_0843. Verify class/function names against actual module before
extending these scaffolds with behavioral assertions.
"""
from __future__ import annotations

import pathlib
import sys

import pytest


MODULE_PATH = "agentic_core.L5_safety.adapters.orkes_approval_adapter"

_REPO_ROOT = pathlib.Path(__file__).parents[4]

_SHADOW_PREFIXES = (
    "agentic_core.L5_safety.adapters",
    "agentic_core.L5_safety",
    "agentic_core.L3_orchestration",
    "agentic_core",
)


def _evict_shadow_modules() -> None:
    """Remove tests/agentic_core shadow entries so production package wins."""
    to_remove = []
    for key, mod in sys.modules.items():
        if not key.startswith(_SHADOW_PREFIXES):
            continue
        file = getattr(mod, "__file__", "") or ""
        if "tests" in file.replace("\\", "/"):
            to_remove.append(key)
    for key in to_remove:
        del sys.modules[key]


def _load_module():
    """Load module directly from filesystem to avoid tests/agentic_core shadow namespace."""
    _evict_shadow_modules()
    if MODULE_PATH in sys.modules:
        return sys.modules[MODULE_PATH]
    str_root = str(_REPO_ROOT)
    if str_root not in sys.path:
        sys.path.insert(0, str_root)
    import importlib
    return importlib.import_module(MODULE_PATH)


def test_module_imports():
    mod = _load_module()
    assert mod is not None


def test_module_has_public_surface():
    mod = _load_module()
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    _load_module()
    _load_module()


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    mod = _load_module()
    has_callable = any(
        callable(getattr(mod, n))
        for n in dir(mod)
        if not n.startswith("_")
    )
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    mod = _load_module()
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), (
        f"{MODULE_PATH} not under agentic_core: {file}"
    )
