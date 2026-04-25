"""Smoke tests for phase_acceptance_guardrail — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.phase_acceptance_guardrail")


def test_module_imports_clean():
    assert mod is not None


def test_PhaseAcceptanceGuard_present():
    assert hasattr(mod, "PhaseAcceptanceGuard")
    assert isinstance(mod.PhaseAcceptanceGuard, type)


def test_main_callable():
    assert callable(mod.main)
