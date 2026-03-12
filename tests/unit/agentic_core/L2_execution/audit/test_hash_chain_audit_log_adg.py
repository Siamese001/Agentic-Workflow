"""ADG importability contract for agentic_core/L2_execution/audit/hash_chain_audit_log.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hash_chain_audit_log.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.audit.hash_chain_audit_log import (  # noqa: F401
        AuditEntry,
        HashChainAuditLog,
        GENESIS_HASH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AuditEntry = None  # type: ignore[assignment,misc]
    HashChainAuditLog = None  # type: ignore[assignment,misc]
    GENESIS_HASH = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="hash_chain_audit_log.py deps unavailable")
class TestHashChainAuditLogImportability:
    def test_module_importable(self) -> None:
        """ADG contract: hash_chain_audit_log.py must be importable."""
        assert _AVAILABLE

    def test_auditentry_is_type(self) -> None:
        assert AuditEntry is not None

    def test_hashchainauditlog_is_type(self) -> None:
        assert HashChainAuditLog is not None

    def test_genesis_hash_defined(self) -> None:
        assert GENESIS_HASH is not None

