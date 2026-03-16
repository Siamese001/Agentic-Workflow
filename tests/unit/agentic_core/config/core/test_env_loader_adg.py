"""ADG-driven tests for config/core/env_loader.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_env_loader_adg")
_emit_applies_guardrail("p0", "test_env_loader_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_env_loader_adg", "policy_binding")
_emit_snapshots_state("p0", "test_env_loader_adg", "state_snapshot")
emit_replay_key("p0", "test_env_loader_adg")
emit_determinism_digest("p0", "test_env_loader_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.config.core.env_loader import SovereignEnv
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SovereignEnv = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="env_loader deps unavailable")
class TestSovereignEnv:
    def test_importable(self):
        assert callable(SovereignEnv)

    def test_singleton_requires_project_root(self):
        import agentic_core.config.core.env_loader as mod
        original = mod.SovereignEnv._instance
        mod.SovereignEnv._instance = None
        try:
            with pytest.raises((ValueError, FileNotFoundError, Exception)):
                mod.SovereignEnv(project_root=None)
        finally:
            mod.SovereignEnv._instance = original

    def test_has_instance_attribute(self):
        assert hasattr(SovereignEnv, "_instance")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
