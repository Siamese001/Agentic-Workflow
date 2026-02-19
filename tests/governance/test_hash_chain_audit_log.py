"""H2 governance tests: Hash-chained immutable audit log.

Validates:
- Genesis rule (entry_index=0, previous_hash="GENESIS")
- Hash chain integrity verification
- Chain break detection (tampered entry)
- Seal prevents further appends
- Entry immutability (frozen dataclass)
- Deterministic hash computation
"""

import pytest

from agentic_core.L2_execution.audit.hash_chain_audit_log import (
    GENESIS_HASH,
    AuditEntry,
    HashChainAuditLog,
)

pytestmark = pytest.mark.governance


class TestGenesisRule:
    """First entry must follow genesis convention."""

    def test_first_entry_has_genesis_previous_hash(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="init")
        assert entry.previous_hash == GENESIS_HASH

    def test_first_entry_has_index_zero(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="init")
        assert entry.entry_index == 0

    def test_genesis_hash_is_literal_string(self):
        assert GENESIS_HASH == "GENESIS"


class TestChainIntegrity:
    """Hash chain must be verifiable from genesis."""

    def test_single_entry_verifies(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        assert log.verify_chain_integrity() is True

    def test_multi_entry_chain_verifies(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        log.append(tier="L2", action="persist", payload={"k": "v"})
        log.append(tier="L5", action="approve")
        assert log.verify_chain_integrity() is True

    def test_chain_links_previous_hash(self):
        log = HashChainAuditLog()
        e0 = log.append(tier="L2", action="init")
        e1 = log.append(tier="L2", action="persist")
        assert e1.previous_hash == e0.entry_hash

    def test_empty_log_verifies(self):
        log = HashChainAuditLog()
        assert log.verify_chain_integrity() is True

    def test_each_entry_hash_is_sha256(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="test")
        assert len(entry.entry_hash) == 64
        assert all(c in "0123456789abcdef" for c in entry.entry_hash)


class TestChainBreakDetection:
    """Tampered entries must be detected."""

    def test_tampered_hash_detected(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        log.append(tier="L2", action="persist")

        tampered = AuditEntry(
            entry_index=log.entries[1].entry_index,
            previous_hash=log.entries[1].previous_hash,
            entry_hash="0" * 64,
            timestamp=log.entries[1].timestamp,
            tier=log.entries[1].tier,
            action=log.entries[1].action,
            payload=log.entries[1].payload,
        )
        log._entries[1] = tampered
        assert log.verify_chain_integrity() is False


class TestSeal:
    """Sealed log must reject further appends."""

    def test_seal_returns_root_hash(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        root = log.seal()
        assert root == log.chain_root

    def test_append_after_seal_raises(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        log.seal()
        with pytest.raises(RuntimeError, match="sealed"):
            log.append(tier="L2", action="rejected")

    def test_seal_empty_log_raises(self):
        log = HashChainAuditLog()
        with pytest.raises(RuntimeError, match="empty"):
            log.seal()


class TestEntryImmutability:
    """AuditEntry must be frozen."""

    def test_cannot_mutate_entry_field(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="init")
        with pytest.raises(AttributeError):
            entry.action = "tampered"  # type: ignore[misc]


class TestHashDeterminism:
    """Same inputs must produce same hash."""

    def test_entry_hash_is_deterministic(self):
        entry = AuditEntry(
            entry_index=0,
            previous_hash=GENESIS_HASH,
            entry_hash="placeholder",
            timestamp="2026-01-01T00:00:00.000000+00:00",
            tier="L2",
            action="init",
            payload={},
        )
        assert entry.verify_hash() is False

    def test_verify_passes_on_correct_hash(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="init")
        assert entry.verify_hash() is True


class TestLogProperties:
    """Log properties must reflect state."""

    def test_length_tracks_entries(self):
        log = HashChainAuditLog()
        assert log.length == 0
        log.append(tier="L2", action="init")
        assert log.length == 1
        log.append(tier="L2", action="persist")
        assert log.length == 2

    def test_chain_root_none_when_empty(self):
        log = HashChainAuditLog()
        assert log.chain_root is None

    def test_entries_returns_tuple(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        assert isinstance(log.entries, tuple)
