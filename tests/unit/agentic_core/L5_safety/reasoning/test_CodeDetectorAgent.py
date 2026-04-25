"""Smoke tests for CodeDetectorAgent — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.CodeDetectorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_CodeDetectorAgent_class_present():
    assert hasattr(mod, "CodeDetectorAgent")
    assert isinstance(mod.CodeDetectorAgent, type)


def test_CodeDetectorAgent_inherits_SovereignBaseAgent():
    bases = [c.__name__ for c in mod.CodeDetectorAgent.__mro__]
    assert "SovereignBaseAgent" in bases


def test_Detection_present():
    assert hasattr(mod, "Detection")
    assert isinstance(mod.Detection, type)
