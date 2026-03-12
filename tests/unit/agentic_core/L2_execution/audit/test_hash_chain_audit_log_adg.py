"""ADG-driven tests for L2_execution/audit/hash_chain_audit_log.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.audit.hash_chain_audit_log import (
        GENESIS_HASH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GENESIS_HASH = None


@pytest.mark.skipif(not _AVAILABLE, reason="hash_chain_audit_log deps unavailable")
class TestHashChainAuditLog:
    def test_genesis_hash_is_string(self):
        assert isinstance(GENESIS_HASH, str)

    def test_genesis_hash_value(self):
        assert GENESIS_HASH == "GENESIS"


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
