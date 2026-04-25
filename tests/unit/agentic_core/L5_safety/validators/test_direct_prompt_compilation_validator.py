"""Smoke tests for direct_prompt_compilation_validator — wave 19."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.direct_prompt_compilation_validator")


def test_module_imports_clean():
    assert mod is not None


def test_AntiPatternCategory_present():
    assert hasattr(mod, "AntiPatternCategory")


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
