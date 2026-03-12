"""ADG-driven tests for system_learning/stores/audit_store.py — fan_in=1."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

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
