"""Smoke tests for logs_guard — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.governance.logs_guard")


def test_module_imports_clean():
    assert mod is not None


def test_is_log_or_output_file_callable():
    assert callable(mod.is_log_or_output_file)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
