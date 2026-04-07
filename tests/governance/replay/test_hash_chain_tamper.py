"""REQ-158/303: Hash chain tamper detection.

Inject reorder into HashChainAuditLog; assert detection raises.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class HashChainTamperError(RuntimeError):
    """Raised when hash chain tampering is detected."""

    pass


@dataclass
class AuditEntry:
    """Single entry in audit log."""

    sequence_number: int
    timestamp: str  # Using string instead of datetime for determinism
    operation: str
    data_hash: str
    previous_hash: str
    signature: str | None = None


@dataclass
class HashChainAuditLog:
    """Hash chain audit log with tamper detection."""

    entries: list[AuditEntry] = field(default_factory=list)

    def add_entry(self, operation: str, data: Any) -> AuditEntry:
        """Add new entry to audit log."""
        # Compute hash of data
        data_json = json.dumps(data, sort_keys=True, separators=(",", ":"))
        data_hash = hashlib.sha256(data_json.encode("utf-8")).hexdigest()

        # Get previous hash
        previous_hash = "0" * 64  # Genesis hash
        if self.entries:
            previous_hash = self.entries[-1].data_hash

        # Create entry
        entry = AuditEntry(
            sequence_number=len(self.entries),
            timestamp="2023-01-01T00:00:00Z",  # Fixed timestamp for determinism
            operation=operation,
            data_hash=data_hash,
            previous_hash=previous_hash,
        )

        self.entries.append(entry)
        return entry

    def verify_chain_integrity(self) -> bool:
        """Verify hash chain integrity."""
        if not self.entries:
            return True

        # Check each entry's previous hash
        for i, entry in enumerate(self.entries):
            if i == 0:
                # First entry should have genesis hash
                if entry.previous_hash != "0" * 64:
                    return False
            else:
                # Previous hash should match actual previous entry
                expected_previous = self.entries[i - 1].data_hash
                if entry.previous_hash != expected_previous:
                    return False

        # Check sequence numbers are consecutive
        for i, entry in enumerate(self.entries):
            if entry.sequence_number != i:
                return False

        return True

    def detect_reorder(self) -> list[str]:
        """Detect if entries have been reordered."""
        issues = []

        # Check sequence numbers
        for i, entry in enumerate(self.entries):
            if entry.sequence_number != i:
                issues.append(f"Entry {i} has sequence number {entry.sequence_number}")

        # Check hash chain continuity
        for i in range(1, len(self.entries)):
            entry = self.entries[i]
            expected_previous = self.entries[i - 1].data_hash
            if entry.previous_hash != expected_previous:
                issues.append(
                    f"Hash break at entry {i}: expected {expected_previous[:16]}, got {entry.previous_hash[:16]}",
                )

        return issues

    def assert_integrity(self) -> None:
        """Assert chain integrity, raise if tampered."""
        if not self.verify_chain_integrity():
            issues = self.detect_reorder()
            raise HashChainTamperError(f"Hash chain tampering detected: {issues}")


@pytest.mark.governance
def test_req158_hash_chain_integrity():
    """REQ-158: Hash chain maintains integrity."""
    audit_log = HashChainAuditLog()

    # Add entries
    entry1 = audit_log.add_entry("operation1", {"data": "value1"})
    entry2 = audit_log.add_entry("operation2", {"data": "value2"})
    entry3 = audit_log.add_entry("operation3", {"data": "value3"})

    # Verify integrity
    assert audit_log.verify_chain_integrity()

    # Check sequence numbers
    assert entry1.sequence_number == 0
    assert entry2.sequence_number == 1
    assert entry3.sequence_number == 2

    # Check hash chain
    assert entry1.previous_hash == "0" * 64
    assert entry2.previous_hash == entry1.data_hash
    assert entry3.previous_hash == entry2.data_hash


@pytest.mark.governance
def test_req158_reorder_detection():
    """REQ-158: Reordered entries are detected."""
    audit_log = HashChainAuditLog()

    # Add entries normally
    audit_log.add_entry("op1", {"data": "1"})
    audit_log.add_entry("op2", {"data": "2"})
    audit_log.add_entry("op3", {"data": "3"})

    # Verify normal integrity
    assert audit_log.verify_chain_integrity()

    # Manually reorder entries (simulate tampering)
    entry1, entry2, entry3 = audit_log.entries
    audit_log.entries = [entry1, entry3, entry2]  # Swap 2 and 3

    # Should detect tampering
    assert not audit_log.verify_chain_integrity()

    issues = audit_log.detect_reorder()
    assert len(issues) > 0
    assert any("sequence number" in issue or "Hash break" in issue for issue in issues)


@pytest.mark.governance
def test_req303_tamper_raises_exception():
    """REQ-303: Tamper detection raises exception."""
    audit_log = HashChainAuditLog()

    # Add entries
    audit_log.add_entry("op1", {"data": "1"})
    audit_log.add_entry("op2", {"data": "2"})

    # Should not raise for intact chain
    audit_log.assert_integrity()  # Should not raise

    # Tamper with chain
    entry1, entry2 = audit_log.entries
    tampered_entry = AuditEntry(
        sequence_number=1,
        timestamp="2023-01-01T00:00:00Z",
        operation="op2",
        data_hash="tampered" + "0" * 56,  # Invalid hash
        previous_hash="invalid" + "0" * 56,
    )

    audit_log.entries = [entry1, tampered_entry]

    # Should raise exception
    with pytest.raises(HashChainTamperError, match="Hash chain tampering detected"):
        audit_log.assert_integrity()


@pytest.mark.governance
def test_req158_missing_entry_detection():
    """REQ-158: Missing entries are detected."""
    audit_log = HashChainAuditLog()

    # Add entries
    audit_log.add_entry("op1", {"data": "1"})
    audit_log.add_entry("op2", {"data": "2"})
    audit_log.add_entry("op3", {"data": "3"})

    # Remove middle entry (simulate tampering)
    entry1, entry2, entry3 = audit_log.entries
    audit_log.entries = [entry1, entry3]

    # Should detect tampering
    assert not audit_log.verify_chain_integrity()

    # Check specific issues are detected
    issues = audit_log.detect_reorder()
    assert len(issues) > 0


@pytest.mark.governance
def test_req303_duplicate_entry_detection():
    """REQ-303: Duplicate entries are detected."""
    audit_log = HashChainAuditLog()

    # Add entry
    entry1 = audit_log.add_entry("op1", {"data": "1"})

    # Duplicate the entry (simulate tampering)
    audit_log.entries.append(entry1)

    # Should detect tampering due to sequence number conflict
    assert not audit_log.verify_chain_integrity()

    issues = audit_log.detect_reorder()
    assert any("sequence number" in issue for issue in issues)


@pytest.mark.governance
def test_req158_hash_chain_persistence():
    """REQ-158: Hash chain can be serialized and restored."""
    # Create audit log
    audit_log1 = HashChainAuditLog()
    audit_log1.add_entry("op1", {"data": "1"})
    audit_log1.add_entry("op2", {"data": "2"})

    # Serialize to JSON
    entries_data = [
        {
            "sequence_number": e.sequence_number,
            "timestamp": e.timestamp,
            "operation": e.operation,
            "data_hash": e.data_hash,
            "previous_hash": e.previous_hash,
        }
        for e in audit_log1.entries
    ]

    # Restore from JSON
    restored_entries = [AuditEntry(**data) for data in entries_data]

    audit_log2 = HashChainAuditLog(entries=restored_entries)

    # Should have same integrity
    assert audit_log2.verify_chain_integrity()
    assert len(audit_log2.entries) == 2
    assert audit_log2.entries[0].data_hash == audit_log1.entries[0].data_hash


@pytest.mark.governance
def test_req303_comprehensive_tamper_scenarios():
    """REQ-303: Comprehensive tampering scenarios are detected."""
    scenarios = [
        # Scenario 1: Reorder entries
        lambda log: setattr(log, "entries", [log.entries[0], log.entries[2], log.entries[1]]),
        # Scenario 2: Modify data hash
        lambda log: setattr(log.entries[1], "data_hash", "modified" + "0" * 56),
        # Scenario 3: Break hash chain
        lambda log: setattr(log.entries[1], "previous_hash", "broken" + "0" * 56),
        # Scenario 4: Wrong sequence numbers
        lambda log: setattr(log.entries[0], "sequence_number", 5),
    ]

    for i, tamper_func in enumerate(scenarios):
        # Create fresh audit log
        audit_log = HashChainAuditLog()
        audit_log.add_entry("op1", {"data": "1"})
        audit_log.add_entry("op2", {"data": "2"})
        audit_log.add_entry("op3", {"data": "3"})

        # Apply tampering
        tamper_func(audit_log)

        # Should detect tampering
        assert not audit_log.verify_chain_integrity(), f"Scenario {i + 1} should detect tampering"

        # Should raise exception
        with pytest.raises(HashChainTamperError):
            audit_log.assert_integrity()
