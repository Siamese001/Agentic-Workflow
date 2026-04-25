"""Smoke tests for fix_inherited_invocation_util — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.fix_inherited_invocation_util")


def test_module_imports_clean():
    assert mod is not None


def test_load_inherited_agents_callable():
    assert callable(mod.load_inherited_agents)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
