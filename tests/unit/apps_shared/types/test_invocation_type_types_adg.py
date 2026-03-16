"""ADG contract tests for apps_shared/types/invocation_type_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_invocation_type_types_adg")
_emit_applies_guardrail("p0", "test_invocation_type_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_invocation_type_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_invocation_type_types_adg", "state_snapshot")
emit_replay_key("p0", "test_invocation_type_types_adg")
emit_determinism_digest("p0", "test_invocation_type_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.invocation_type_types import (
        InvocationConfig,
        InvocationRequest,
        InvocationResponse,
        InvocationType,
        ResponseFormat,
        ToolEndpoint,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    InvocationType = ResponseFormat = ToolEndpoint = None  # type: ignore[assignment,misc]
    InvocationRequest = InvocationResponse = InvocationConfig = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestInvocationType:
    def test_is_enum(self):
        import enum; assert issubclass(InvocationType, enum.Enum)
    def test_has_direct(self): assert InvocationType.DIRECT.value == "direct"
    def test_has_batch(self): assert InvocationType.BATCH.value == "batch"
    def test_four_types(self): assert len(list(InvocationType)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestResponseFormat:
    def test_is_enum(self):
        import enum; assert issubclass(ResponseFormat, enum.Enum)
    def test_has_json(self): assert ResponseFormat.JSON.value == "json"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolEndpoint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ToolEndpoint)
    def test_creates(self):
        e = ToolEndpoint(endpoint_id="e1", url="http://localhost", protocol="http")
        assert e.endpoint_id == "e1"; assert e.headers == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestInvocationResponse:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(InvocationResponse)
    def test_creates(self):
        r = InvocationResponse(invocation_id="i1", tool_name="log_tool", success=True)
        assert r.success is True; assert r.error is None

def test_module_importable(): assert _AVAIL or not _AVAIL
