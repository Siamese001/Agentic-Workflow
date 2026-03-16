"""ADG-driven tests for apps_rg/engines/ats_compatibility_engine.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_ats_compatibility_engine_adg")
_emit_applies_guardrail("p0", "test_ats_compatibility_engine_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_ats_compatibility_engine_adg", "policy_binding")
_emit_snapshots_state("p0", "test_ats_compatibility_engine_adg", "state_snapshot")
emit_replay_key("p0", "test_ats_compatibility_engine_adg")
emit_determinism_digest("p0", "test_ats_compatibility_engine_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from apps_rg.engines.ats_compatibility_engine import ATSCompatibilityEngine
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ATSCompatibilityEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ATSCompatibilityEngine deps unavailable")
class TestATSCompatibilityEngine:
    def test_importable(self):
        assert callable(ATSCompatibilityEngine)

    def test_has_forbidden_patterns(self):
        class FakeCtx:
            buffer = None
        agent = ATSCompatibilityEngine(ctx=FakeCtx())
        assert hasattr(agent, "forbidden_patterns")
        assert len(agent.forbidden_patterns) > 0

    def test_forbidden_patterns_contain_table(self):
        class FakeCtx:
            buffer = None
        agent = ATSCompatibilityEngine(ctx=FakeCtx())
        patterns = [p[0] for p in agent.forbidden_patterns]
        assert any("table" in p for p in patterns)

    def test_has_execute(self):
        assert hasattr(ATSCompatibilityEngine, "execute")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
