"""Tests for DurableWriteWrapper - durable write operations with retries."""
import pytest
from unittest.mock import Mock, patch
from agentic_core.L2_execution.enforcement.durable_write_wrapper import DurableWriteWrapper


class TestDurableWriteWrapper:
    def test_init(self):
        w = DurableWriteWrapper(max_retries=3)
        assert w.max_retries == 3

    def test_write_success(self):
        w = DurableWriteWrapper(max_retries=3)
        backend = Mock()
        backend.write.return_value = True
        w.set_backend(backend)
        assert w.write("key", "value") is True

    def test_write_retry_on_failure(self):
        w = DurableWriteWrapper(max_retries=3)
        backend = Mock()
        backend.write.side_effect = [IOError, IOError, True]
        w.set_backend(backend)
        assert w.write("key", "value") is True
        assert backend.write.call_count == 3

    def test_write_exhausts_retries(self):
        w = DurableWriteWrapper(max_retries=2)
        backend = Mock()
        backend.write.side_effect = IOError("fail")
        w.set_backend(backend)
        with pytest.raises(IOError):
            w.write("key", "value")

    def test_write_with_checksum(self):
        w = DurableWriteWrapper(max_retries=1, verify_checksum=True)
        backend = Mock()
        backend.write.return_value = True
        backend.checksum.return_value = "abc"
        w.set_backend(backend)
        w.write("key", "value")
        backend.checksum.assert_called()

    def test_write_atomic_rollback(self):
        w = DurableWriteWrapper(max_retries=1)
        backend = Mock()
        backend.write.side_effect = IOError
        w.set_backend(backend)
        with pytest.raises(IOError):
            w.write("key", "value")
        backend.rollback.assert_called()

    def test_get_stats(self):
        w = DurableWriteWrapper(max_retries=3)
        stats = w.get_stats()
        assert "writes" in stats or "max_retries" in stats
