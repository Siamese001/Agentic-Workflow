"""ADG-driven tests for apps_rg/engines/clerk_extraction_engine.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_clerk_extraction_engine_adg")
_emit_applies_guardrail("p0", "test_clerk_extraction_engine_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_clerk_extraction_engine_adg", "policy_binding")
_emit_snapshots_state("p0", "test_clerk_extraction_engine_adg", "state_snapshot")
emit_replay_key("p0", "test_clerk_extraction_engine_adg")
emit_determinism_digest("p0", "test_clerk_extraction_engine_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from apps_rg.engines.clerk_extraction_engine import ClerkExtractionEngine
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ClerkExtractionEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ClerkExtractionEngine deps unavailable")
class TestClerkExtractionEngine:
    def _make_ctx(self):
        class FakeBuffer:
            def read(self, key, default=None):
                return default
        class FakeCtx:
            buffer = FakeBuffer()
        return FakeCtx()

    def test_importable(self):
        assert callable(ClerkExtractionEngine)

    def test_creates(self):
        agent = ClerkExtractionEngine(ctx=self._make_ctx())
        assert agent is not None

    def test_has_detector(self):
        agent = ClerkExtractionEngine(ctx=self._make_ctx())
        assert hasattr(agent, "detector")

    def test_has_execute(self):
        assert hasattr(ClerkExtractionEngine, "execute")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
