"""Tests for ReadonlyRetrievalScope - read-only retrieval enforcement."""
import pytest
from agentic_core.L4_state.enforcement.readonly_retrieval_scope import ReadonlyRetrievalScope


class TestReadonlyRetrievalScope:
    def test_init(self):
        s = ReadonlyRetrievalScope()
        assert s is not None

    def test_read_allowed(self):
        s = ReadonlyRetrievalScope()
        s.read("key")  # no raise

    def test_write_blocked(self):
        s = ReadonlyRetrievalScope()
        with pytest.raises(PermissionError):
            s.write("key", "value")

    def test_delete_blocked(self):
        s = ReadonlyRetrievalScope()
        with pytest.raises(PermissionError):
            s.delete("key")

    def test_scope_name(self):
        s = ReadonlyRetrievalScope(name="reader")
        assert s.name == "reader"

    def test_check_readonly(self):
        s = ReadonlyRetrievalScope()
        assert s.is_readonly() is True

    def test_audit_read_access(self):
        s = ReadonlyRetrievalScope()
        s.read("key")
        log = s.get_access_log()
        assert len(log) >= 1
