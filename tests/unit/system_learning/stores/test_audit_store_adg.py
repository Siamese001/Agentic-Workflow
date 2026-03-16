"""ADG-driven tests for system_learning/stores/audit_store.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_audit_store_adg")
_emit_applies_guardrail("p0", "test_audit_store_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_audit_store_adg", "policy_binding")
_emit_snapshots_state("p0", "test_audit_store_adg", "state_snapshot")
emit_replay_key("p0", "test_audit_store_adg")
emit_determinism_digest("p0", "test_audit_store_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from system_learning.stores.audit_store import FileBackedAuditStore


class TestFileBackedAuditStore:
    def test_creates(self, tmp_path):
        store = FileBackedAuditStore(reports_dir=tmp_path)
        assert store is not None

    def test_empty_dir_returns_empty_array(self, tmp_path):
        store = FileBackedAuditStore(reports_dir=tmp_path)
        result = store.read_audit_slice(0, 9999999999)
        assert result == b"[]"

    def test_nonexistent_dir_returns_empty_array(self, tmp_path):
        store = FileBackedAuditStore(reports_dir=tmp_path / "nonexistent")
        result = store.read_audit_slice(0, 9999999999)
        assert result == b"[]"

    def test_returns_bytes(self, tmp_path):
        store = FileBackedAuditStore(reports_dir=tmp_path)
        result = store.read_audit_slice(0, 9999999999)
        assert isinstance(result, bytes)

    def test_has_read_audit_slice(self):
        assert hasattr(FileBackedAuditStore, "read_audit_slice")
