"""ADG-driven tests for L4_state/utils/telemetry_sanitizer_util.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_telemetry_sanitizer_util_adg")
_emit_applies_guardrail("p0", "test_telemetry_sanitizer_util_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_telemetry_sanitizer_util_adg", "policy_binding")
_emit_snapshots_state("p0", "test_telemetry_sanitizer_util_adg", "state_snapshot")
emit_replay_key("p0", "test_telemetry_sanitizer_util_adg")
emit_determinism_digest("p0", "test_telemetry_sanitizer_util_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L4_state.utils.telemetry_sanitizer_util import sanitize_tool_output


class TestTelemetrySanitizerUtil:
    def test_importable(self):
        assert callable(sanitize_tool_output)

    def test_returns_string(self):
        result = sanitize_tool_output("some output text")
        assert isinstance(result, str)

    def test_passes_clean_text_unchanged(self):
        result = sanitize_tool_output("clean output")
        assert "clean output" in result

    def test_handles_empty_string(self):
        result = sanitize_tool_output("")
        assert isinstance(result, str)

    def test_handles_none_gracefully(self):
        result = sanitize_tool_output(None)
        assert result is None or isinstance(result, str)
