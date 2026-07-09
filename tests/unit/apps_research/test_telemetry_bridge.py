"""Tests for the apps_research telemetry bridge shims."""

from __future__ import annotations

import builtins
import importlib
import sys

import pytest


MODULE_NAMES = ("apps_research._telemetry", "apps_research.services.telemetry")


def _reload(module_name: str):
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def _base_bridge():
    return _reload("apps_research._telemetry")


@pytest.mark.parametrize("module_name", MODULE_NAMES)
def test_bridge_exports_are_callable(module_name: str) -> None:
    """The bridge should re-export every declared emitter name."""
    base = _base_bridge()
    module = base if module_name == "apps_research._telemetry" else _reload(module_name)

    assert module.__all__ == base.__all__
    assert module.LayerSegment is not None
    for name in base._EMITTER_NAMES:
        assert callable(getattr(module, name))


@pytest.mark.parametrize("module_name", MODULE_NAMES)
def test_bridge_falls_back_to_noops_when_agentic_core_missing(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
) -> None:
    """When agentic_core is unavailable, the bridge must keep returning no-ops."""
    real_import = builtins.__import__

    def _blocked(name: str, *args, **kwargs):
        if name.startswith("agentic_core"):
            raise ImportError(f"simulated missing: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    base = _base_bridge()
    module = base if module_name == "apps_research._telemetry" else _reload(module_name)

    assert module.__all__ == base.__all__
    assert all(getattr(module, name) is getattr(base, name) for name in base._EMITTER_NAMES)
    assert base._noop("any", kw=1) is None
    assert base.LayerSegment.L0_ROUTING == "L0_ROUTING"
    assert base.LayerSegment.L4_STATE == "L4_STATE"
