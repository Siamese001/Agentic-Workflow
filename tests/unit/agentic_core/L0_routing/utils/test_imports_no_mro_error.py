"""Focused regression guard for historical MRO import failures."""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit

MODULE_CANDIDATES = [
    "agentic_core.L6_observability.engines.SovereignHealthMonitor",
    "agentic_core.L6_observability.reasoning.observability_probe_executor",
]


def test_l6_observability_imports_do_not_raise_mro_errors():
    pytest.importorskip("agentic_core")
    for module_name in MODULE_CANDIDATES:
        try:
            importlib.import_module(module_name)
        except TypeError as exc:
            if "method resolution" in str(exc).lower():
                pytest.fail(f"MRO error importing {module_name}: {exc}")
            raise
        except ModuleNotFoundError:
            pytest.skip(f"{module_name} is not available in this environment")
