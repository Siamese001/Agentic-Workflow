"""ADG-driven tests for L2_execution/tools/time_utils_impl.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_time_utils_impl_adg")
_emit_applies_guardrail("p0", "test_time_utils_impl_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_time_utils_impl_adg", "policy_binding")
_emit_snapshots_state("p0", "test_time_utils_impl_adg", "state_snapshot")
emit_replay_key("p0", "test_time_utils_impl_adg")
emit_determinism_digest("p0", "test_time_utils_impl_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.tools.time_utils_impl import TimeTools


class TestTimeTools:
    def test_creates(self):
        t = TimeTools()
        assert t is not None

    def test_has_fallback_method(self):
        assert callable(getattr(TimeTools, "_get_current_time_fallback", None))
