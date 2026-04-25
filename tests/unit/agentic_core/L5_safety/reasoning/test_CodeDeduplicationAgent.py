"""Smoke tests for CodeDeduplicationAgent — wave 28."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.reasoning.CodeDeduplicationAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_CodeDeduplicationAgent_class_present():
    assert hasattr(mod, "CodeDeduplicationAgent")
    assert isinstance(mod.CodeDeduplicationAgent, type)
