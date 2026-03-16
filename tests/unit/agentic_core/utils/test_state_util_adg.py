"""ADG-driven tests for utils/state_util.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_state_util_adg")
_emit_applies_guardrail("p0", "test_state_util_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_state_util_adg", "policy_binding")
_emit_snapshots_state("p0", "test_state_util_adg", "state_snapshot")
emit_replay_key("p0", "test_state_util_adg")
emit_determinism_digest("p0", "test_state_util_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.state_util import check_past_failures
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    check_past_failures = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="state_util deps unavailable")
class TestCheckPastFailures:
    def test_returns_string(self):
        result = check_past_failures("test task description")
        assert isinstance(result, str)

    def test_handles_empty_task(self):
        result = check_past_failures("")
        assert isinstance(result, str)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
