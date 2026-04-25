"""Surface coverage for `agentic_core.L5_safety.enforcement.verification_gate`.

Wave 2 of `.windsurf/plans/test-coverage-waves-f8f5a7.md`. Security-surface
L5 gatekeeper — verification gate for hallucination detection.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.enforcement.verification_gate"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_verification_gate_class_present(mod):
    assert hasattr(mod, "VerificationGate")
    assert inspect.isclass(mod.VerificationGate)


def test_verification_gate_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.VerificationGate, SovereignBaseAgent)


def test_verification_gate_mro_includes_hallucination_mixin(mod):
    names = [c.__name__ for c in mod.VerificationGate.__mro__]
    assert any("Hallucination" in n for n in names), f"MRO missing hallucination mixin: {names}"
