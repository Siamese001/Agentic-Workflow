"""Smoke tests for mcp_sovereign_authority_enforcer — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_MCPSovereignAuthority_class_present():
    assert hasattr(mod, "MCPSovereignAuthority")
    assert isinstance(mod.MCPSovereignAuthority, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)


def test_emit_replay_key_callable():
    assert callable(mod.emit_replay_key)
