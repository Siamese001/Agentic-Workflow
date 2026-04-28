"""Tests for UWGCommitter - Universal Write Gateway commit logic."""
import pytest
from unittest.mock import Mock
from agentic_core.L4_state.enforcement.uwg_committer import UWGCommitter


class TestUWGCommitter:
    def test_init(self):
        c = UWGCommitter()
        assert c is not None

    def test_commit_transaction(self):
        c = UWGCommitter()
        backend = Mock()
        c.set_backend(backend)
        result = c.commit({"key": "value"})
        assert result is not None

    def test_commit_calls_backend(self):
        c = UWGCommitter()
        backend = Mock()
        c.set_backend(backend)
        c.commit({"k": "v"})
        backend.write.assert_called()

    def test_commit_failure_rollback(self):
        c = UWGCommitter()
        backend = Mock()
        backend.write.side_effect = IOError
        c.set_backend(backend)
        with pytest.raises(IOError):
            c.commit({"k": "v"})
        backend.rollback.assert_called()

    def test_batch_commit(self):
        c = UWGCommitter()
        backend = Mock()
        c.set_backend(backend)
        c.batch_commit([{"k1": "v1"}, {"k2": "v2"}])
        assert backend.write.call_count >= 1

    def test_get_commit_history(self):
        c = UWGCommitter()
        backend = Mock()
        c.set_backend(backend)
        c.commit({"k": "v"})
        history = c.get_history()
        assert len(history) >= 1
