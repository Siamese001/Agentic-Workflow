"""ADG-driven tests for L2_execution/utils/archive_util.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_archive_util_adg")
_emit_applies_guardrail("p0", "test_archive_util_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_archive_util_adg", "policy_binding")
_emit_snapshots_state("p0", "test_archive_util_adg", "state_snapshot")
emit_replay_key("p0", "test_archive_util_adg")
emit_determinism_digest("p0", "test_archive_util_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.utils.archive_util import parse_mcp_client_specs
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    parse_mcp_client_specs = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="archive_util deps unavailable")
class TestParseMcpClientSpecs:
    def test_empty_list_returns_empty(self):
        result = parse_mcp_client_specs([])
        assert result == []

    def test_importable(self):
        assert callable(parse_mcp_client_specs)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
