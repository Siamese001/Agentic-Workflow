"""Smoke tests for docs_structure_guard — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.governance.docs_structure_guard")


def test_module_imports_clean():
    assert mod is not None


def test_is_valid_extension_callable():
    assert callable(mod.is_valid_extension)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
