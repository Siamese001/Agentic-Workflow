"""Smoke tests for ssot_relocator_types — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.types.ssot_relocator_types")


def test_module_imports_clean():
    assert mod is not None


def test_ArchivalGatekeeper_present():
    assert hasattr(mod, "ArchivalGatekeeper")


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
