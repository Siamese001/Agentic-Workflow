"""ADG-driven tests for L2_execution/types/mcp_error_types.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_mcp_error_types_adg")
_emit_applies_guardrail("p0", "test_mcp_error_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_mcp_error_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_mcp_error_types_adg", "state_snapshot")
emit_replay_key("p0", "test_mcp_error_types_adg")
emit_determinism_digest("p0", "test_mcp_error_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.mcp_error_types import (
    MCPClientInitializationError,
    MCPClientNotFoundError,
    MCPError,
)


class TestMCPError:
    def test_is_exception(self):
        assert issubclass(MCPError, Exception)


class TestMCPClientInitializationError:
    def test_is_mcp_error(self):
        assert issubclass(MCPClientInitializationError, MCPError)

    def test_creates(self):
        err = MCPClientInitializationError("init failed", client_name="fs", Provider="mcp8")
        assert err.client_name == "fs"
        assert err.Provider == "mcp8"
        assert "init failed" in str(err)


class TestMCPClientNotFoundError:
    def test_is_mcp_error(self):
        assert issubclass(MCPClientNotFoundError, MCPError)

    def test_creates(self):
        err = MCPClientNotFoundError("not found", client_name="unknown")
        assert err.client_name == "unknown"
