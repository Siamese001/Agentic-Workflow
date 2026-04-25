"""Smoke tests for telemetry_sanitizer_util — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.utils.telemetry_sanitizer_util")


def test_module_imports_clean():
    assert mod is not None


def test_sanitize_tool_output_callable():
    assert callable(mod.sanitize_tool_output)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
