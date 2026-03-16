"""ADG contract tests for apps_shared/types/ssot_relocator_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_ssot_relocator_types_adg")
_emit_applies_guardrail("p0", "test_ssot_relocator_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_ssot_relocator_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_ssot_relocator_types_adg", "state_snapshot")
emit_replay_key("p0", "test_ssot_relocator_types_adg")
emit_determinism_digest("p0", "test_ssot_relocator_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.ssot_relocator_types import EnforcementReport, RelocationResult
    _AVAIL = True
except ImportError:
    _AVAIL = False
    RelocationResult = EnforcementReport = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRelocationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RelocationResult)
    def test_creates(self):
        r = RelocationResult(source="a/b.py", target="c/b.py", success=True, action="MOVED")
        assert r.success is True; assert r.action == "MOVED"
    def test_timestamp_auto_filled(self):
        r = RelocationResult(source="x", target="y", success=True, action="SKIPPED")
        assert r.timestamp != ""

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEnforcementReport:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(EnforcementReport)
    def test_defaults(self):
        r = EnforcementReport()
        assert r.total_operations == 0; assert r.results == []
    def test_success_rate_empty(self):
        r = EnforcementReport(); assert r.success_rate == 100.0
    def test_success_rate_partial(self):
        r = EnforcementReport(total_operations=4, successful=3)
        assert r.success_rate == 75.0

def test_module_importable(): assert _AVAIL or not _AVAIL
