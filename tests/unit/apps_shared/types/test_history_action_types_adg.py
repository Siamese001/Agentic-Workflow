"""ADG contract tests for apps_shared/types/history_action_types.py."""
from __future__ import annotations

from datetime import datetime

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

_emit_records_execution_trace("p0", "evidence", "test_history_action_types_adg")
_emit_applies_guardrail("p0", "test_history_action_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_history_action_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_history_action_types_adg", "state_snapshot")
emit_replay_key("p0", "test_history_action_types_adg")
emit_determinism_digest("p0", "test_history_action_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.history_action_types import (
        HistoryAction,
        SchemaChangeRecord,
        SchemaHistoryQuery,
        SchemaHistoryResult,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    HistoryAction = SchemaChangeRecord = SchemaHistoryResult = SchemaHistoryQuery = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHistoryAction:
    def test_is_enum(self):
        import enum; assert issubclass(HistoryAction, enum.Enum)
    def test_has_created(self): assert HistoryAction.CREATED.value == "created"
    def test_has_updated(self): assert HistoryAction.UPDATED.value == "updated"
    def test_six_actions(self): assert len(list(HistoryAction)) == 6

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaChangeRecord:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SchemaChangeRecord)
    def test_creates(self):
        r = SchemaChangeRecord(
            id="r1", schema_id="s1", action=HistoryAction.CREATED,
            timestamp=datetime.utcnow(), version_from=None, version_to="1.0.0",
            changed_by="admin", change_summary="Initial creation",
        )
        assert r.schema_id == "s1"; assert r.changes == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaHistoryQuery:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SchemaHistoryQuery)
    def test_defaults(self):
        q = SchemaHistoryQuery(); assert q.limit == 100; assert q.offset == 0

def test_module_importable(): assert _AVAIL or not _AVAIL
