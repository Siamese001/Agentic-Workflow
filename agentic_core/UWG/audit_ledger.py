"""W11 — Audit Ledger (UWG)

Immutable audit trail for all write attempts.
Every UWG operation is logged for compliance.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class AuditEntry:
    """Single audit ledger entry."""
    entry_id: str
    timestamp: str
    operation: str  # "commit_attempt", "commit_success", "commit_blocked", etc.
    
    run_id: str
    commit_request_id: str
    l4_namespace: str
    
    # Operation details
    status: str  # "success", "blocked", "error"
    reason_codes: List[str] = field(default_factory=list)
    
    # Evidence
    evidence_digest: str = ""
    merkle_hash: str = ""
    
    # Chain of custody
    previous_entry_hash: str = ""
    entry_sequence: int = 0


class AuditLedger:
    """Immutable audit ledger for UWG operations.
    
    Maintains complete chain of custody for all write operations.
    """
    
    def __init__(self):
        """Initialize audit ledger."""
        self._entries: List[AuditEntry] = []
        self._merkle_root: str = ""
    
    def append_entry(
        self,
        operation: str,
        run_id: str,
        commit_request_id: str,
        l4_namespace: str,
        status: str,
        reason_codes: Optional[List[str]] = None,
        evidence_digest: str = ""
    ) -> AuditEntry:
        """Append entry to audit ledger.
        
        Args:
            operation: Type of operation
            run_id: Associated run
            commit_request_id: Commit request ID
            l4_namespace: Target L4 namespace
            status: Operation status
            reason_codes: Reason codes for status
            evidence_digest: Evidence digest
            
        Returns:
            Created AuditEntry
        """
        sequence = len(self._entries)
        previous_hash = self._merkle_root if self._entries else "0" * 64
        
        # Generate entry hash
        entry_content = f"{sequence}:{previous_hash}:{operation}:{run_id}:{commit_request_id}"
        import hashlib
        entry_hash = hashlib.sha256(entry_content.encode()).hexdigest()
        
        entry = AuditEntry(
            entry_id=f"audit-{commit_request_id}-{sequence}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=operation,
            run_id=run_id,
            commit_request_id=commit_request_id,
            l4_namespace=l4_namespace,
            status=status,
            reason_codes=reason_codes or [],
            evidence_digest=evidence_digest,
            merkle_hash=entry_hash,
            previous_entry_hash=previous_hash,
            entry_sequence=sequence,
        )
        
        self._entries.append(entry)
        self._merkle_root = entry_hash
        
        return entry
    
    def get_entries(
        self,
        run_id: Optional[str] = None,
        operation: Optional[str] = None
    ) -> List[AuditEntry]:
        """Get ledger entries with optional filters."""
        entries = self._entries
        
        if run_id:
            entries = [e for e in entries if e.run_id == run_id]
        
        if operation:
            entries = [e for e in entries if e.operation == operation]
        
        return entries
    
    def get_merkle_root(self) -> str:
        """Get current Merkle root hash."""
        return self._merkle_root
    
    def verify_chain(self) -> bool:
        """Verify integrity of audit chain."""
        if not self._entries:
            return True
        
        expected_hash = "0" * 64
        
        for i, entry in enumerate(self._entries):
            # Check sequence
            if entry.entry_sequence != i:
                return False
            
            # Check previous hash
            if entry.previous_entry_hash != expected_hash:
                return False
            
            # Verify entry hash
            entry_content = f"{i}:{expected_hash}:{entry.operation}:{entry.run_id}:{entry.commit_request_id}"
            import hashlib
            expected_hash = hashlib.sha256(entry_content.encode()).hexdigest()
            
            if entry.merkle_hash != expected_hash:
                return False
        
        return True


# Global ledger instance
default_ledger = AuditLedger()
