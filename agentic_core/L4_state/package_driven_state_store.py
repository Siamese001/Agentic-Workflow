"""W11 — Package-Driven L4 State Store

L4 durable state storage.
Only accepts writes from UWG.
Rejects all direct writes from L2, Exit, L6, tools, apps.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

from agentic_core.UWG import (
    StateCommitReceipt,
    BlockedWriteReceipt,
    BlockReason,
)


@dataclass(frozen=True)
class L4StateRecord:
    """A single record in L4 state."""
    record_id: str
    namespace: str
    record_type: str
    
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Provenance
    uwg_commit_receipt_ref: str = ""
    write_policy_hash: str = ""
    
    # Audit
    audit_entry_refs: List[str] = field(default_factory=list)


class PackageDrivenStateStore:
    """L4 state store that only accepts UWG-mediated writes.
    
    Hard rule: All writes must come through UWG.
    Direct writes are rejected.
    """
    
    def __init__(self):
        """Initialize state store."""
        self._namespaces: Dict[str, Dict[str, L4StateRecord]] = {}
        self._write_log: List[Dict[str, Any]] = []
    
    def write_from_uwg(
        self,
        commit_receipt: StateCommitReceipt,
        data: Dict[str, Any]
    ) -> Optional[L4StateRecord]:
        """Write to L4 from UWG commit receipt.
        
        Args:
            commit_receipt: Valid UWG commit receipt
            data: Data to store
            
        Returns:
            Created L4StateRecord or None on error
        """
        # Verify receipt is from UWG
        if not self._is_valid_uwg_receipt(commit_receipt):
            raise DirectWriteAttemptError(
                "L4 only accepts writes from UWG. Direct write rejected."
            )
        
        namespace = commit_receipt.l4_namespace
        record_id = f"{namespace}/{commit_receipt.run_id}"
        
        record = L4StateRecord(
            record_id=record_id,
            namespace=namespace,
            record_type="research_substrate",
            data=data,
            uwg_commit_receipt_ref=commit_receipt.receipt_id,
            write_policy_hash=commit_receipt.evidence_digest,
            audit_entry_refs=[commit_receipt.audit_ledger_ref],
        )
        
        # Store in namespace
        if namespace not in self._namespaces:
            self._namespaces[namespace] = {}
        
        self._namespaces[namespace][record_id] = record
        
        # Log write
        self._write_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "write",
            "record_id": record_id,
            "namespace": namespace,
            "commit_receipt_id": commit_receipt.receipt_id,
        })
        
        return record
    
    def read(self, namespace: str, record_id: str) -> Optional[L4StateRecord]:
        """Read record from L4.
        
        Args:
            namespace: L4 namespace
            record_id: Record ID
            
        Returns:
            L4StateRecord or None
        """
        if namespace not in self._namespaces:
            return None
        
        return self._namespaces[namespace].get(record_id)
    
    def query_namespace(
        self,
        namespace: str,
        record_type: Optional[str] = None
    ) -> List[L4StateRecord]:
        """Query records in namespace.
        
        Args:
            namespace: L4 namespace
            record_type: Optional type filter
            
        Returns:
            List of matching records
        """
        if namespace not in self._namespaces:
            return []
        
        records = list(self._namespaces[namespace].values())
        
        if record_type:
            records = [r for r in records if r.record_type == record_type]
        
        return records
    
    def _is_valid_uwg_receipt(self, receipt: StateCommitReceipt) -> bool:
        """Check if receipt is a valid UWG commit receipt."""
        # Verify receipt has required UWG fields
        if not receipt.receipt_id.startswith("receipt-"):
            return False
        
        if not receipt.audit_ledger_ref.startswith("audit://"):
            return False
        
        if not receipt.rollback_ref:
            return False
        
        return True
    
    def get_namespaces(self) -> List[str]:
        """Get list of all namespaces."""
        return list(self._namespaces.keys())
    
    def get_write_log(self) -> List[Dict[str, Any]]:
        """Get write operation log."""
        return list(self._write_log)


class DirectWriteAttemptError(Exception):
    """Raised when direct write to L4 is attempted."""
    pass


class L4WriteGate:
    """Gate that blocks all non-UWG writes to L4.
    
    Acts as a firewall between layers and L4.
    """
    
    ALLOWED_SOURCES = {"UWG", "agentic_core.UWG"}
    
    def check_write_permission(self, source: str) -> bool:
        """Check if source is allowed to write to L4.
        
        Args:
            source: Source identifier attempting write
            
        Returns:
            True if allowed, False otherwise
        """
        return source in self.ALLOWED_SOURCES
    
    def block_direct_write(
        self,
        source: str,
        attempted_operation: str
    ) -> BlockedWriteReceipt:
        """Block a direct write attempt.
        
        Args:
            source: Source that attempted direct write
            attempted_operation: What operation was attempted
            
        Returns:
            BlockedWriteReceipt
        """
        return BlockedWriteReceipt(
            receipt_id=f"blocked-direct-{source}",
            commit_request_id="none",
            run_id="none",
            block_reasons=(BlockReason.DIRECT_WRITE_ATTEMPT_BLOCKED,),
            block_details=[
                f"Direct write from {source} to L4 blocked.",
                f"Attempted operation: {attempted_operation}",
                "All L4 writes must go through UWG.",
            ],
        )


# Global state store instance
default_state_store = PackageDrivenStateStore()
default_l4_gate = L4WriteGate()
