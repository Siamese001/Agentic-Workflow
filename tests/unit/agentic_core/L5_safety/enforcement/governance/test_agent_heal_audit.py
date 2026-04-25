"""Smoke tests for agent_heal_audit — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.governance.agent_heal_audit")


def test_module_imports_clean():
    assert mod is not None


def test_main_callable():
    assert callable(mod.main)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
