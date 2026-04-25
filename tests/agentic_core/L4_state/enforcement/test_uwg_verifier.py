"""Tests for UWGVerifier - UWG transaction verification."""
import pytest
from unittest.mock import Mock
from agentic_core.L4_state.enforcement.uwg_verifier import UWGVerifier


class TestUWGVerifier:
    def test_init(self):
        v = UWGVerifier()
        assert v is not None

    def test_verify_valid_transaction(self):
        v = UWGVerifier()
        tx = {"id": "t1", "writes": [{"key": "x", "value": "y"}], "checksum": "abc"}
        assert v.verify(tx) is True

    def test_verify_invalid_checksum(self):
        v = UWGVerifier()
        tx = {"id": "t1", "writes": [{"key": "x", "value": "y"}], "checksum": "wrong"}
        assert v.verify(tx) is False

    def test_verify_missing_fields(self):
        v = UWGVerifier()
        tx = {"id": "t1"}
        assert v.verify(tx) is False

    def test_compute_checksum(self):
        v = UWGVerifier()
        cs = v.compute_checksum({"key": "x", "value": "y"})
        assert isinstance(cs, str)

    def test_batch_verify(self):
        v = UWGVerifier()
        txs = [{"id": "1", "writes": [], "checksum": "a"}]
        results = v.batch_verify(txs)
        assert len(results) == 1
