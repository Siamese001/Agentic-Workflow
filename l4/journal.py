"""
L4 State Management - Journal

Implements a journal for state changes with support for corrections and auditing.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import logging
from enum import Enum

from .types import StateTransition, StateSnapshot, StatePath, StateOperation

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CorrectionType(str, Enum):
    """Types of corrections that can be made to the state."""
    UNDO = "undo"
    REDO = "redo"
    AMEND = "amend"
    COMPENSATE = "compensate"

@dataclass
class JournalEntry(Generic[T]):
    """A single entry in the state journal."""
    entry_id: str
    timestamp: datetime
    transition: StateTransition[T]
    snapshot_before: StateSnapshot[T]
    snapshot_after: StateSnapshot[T]
    correlation_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    corrections: List[Correction] = field(default_factory=list)

@dataclass
class Correction(Generic[T]):
    """Represents a correction to a previous state change."""
    correction_id: str
    entry_id: str
    correction_type: CorrectionType
    timestamp: datetime
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    # The transition that was used to correct the state
    correction_transition: Optional[StateTransition[T]] = None
    # The resulting state after applying the correction
    corrected_snapshot: Optional[StateSnapshot[T]] = None

class StateJournal(Generic[T]):
    """
    Maintains a journal of all state changes with support for corrections.
    
    The journal provides a complete audit trail of all state changes,
    including corrections and their justifications.
    """
    
    def __init__(self):
        self._entries: Dict[str, JournalEntry[T]] = {}
        self._corrections: Dict[str, Correction[T]] = {}
        self._correlation_chain: Dict[str, List[str]] = {}
    
    def record(
        self,
        transition: StateTransition[T],
        snapshot_before: StateSnapshot[T],
        snapshot_after: StateSnapshot[T],
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JournalEntry[T]:
        """Record a new state transition in the journal."""
        entry_id = str(uuid.uuid4())
        correlation_id = correlation_id or str(uuid.uuid4())
        
        entry = JournalEntry[
            T
        ](
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
            transition=transition,
            snapshot_before=snapshot_before,
            snapshot_after=snapshot_after,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        
        self._entries[entry_id] = entry
        
        # Update correlation chain
        if correlation_id not in self._correlation_chain:
            self._correlation_chain[correlation_id] = []
        self._correlation_chain[correlation_id].append(entry_id)
        
        logger.debug(
            f"Recorded journal entry {entry_id} for transition {transition.operation} "
            f"on path {transition.path}"
        )
        
        return entry
    
    def correct(
        self,
        entry_id: str,
        correction_type: CorrectionType,
        reason: str,
        correction_transition: Optional[StateTransition[T]] = None,
        corrected_snapshot: Optional[StateSnapshot[T]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Correction[T]:
        """Record a correction to a previous journal entry."""
        if entry_id not in self._entries:
            raise ValueError(f"Journal entry not found: {entry_id}")
        
        correction_id = str(uuid.uuid4())
        correction = Correction[
            T
        ](
            correction_id=correction_id,
            entry_id=entry_id,
            correction_type=correction_type,
            timestamp=datetime.utcnow(),
            reason=reason,
            metadata=metadata or {},
            correction_transition=correction_transition,
            corrected_snapshot=corrected_snapshot
        )
        
        self._corrections[correction_id] = correction
        self._entries[entry_id].corrections.append(correction)
        
        logger.info(
            f"Recorded {correction_type} correction {correction_id} "
            f"for journal entry {entry_id}: {reason}"
        )
        
        return correction
    
    def get_entry(self, entry_id: str) -> Optional[JournalEntry[T]]:
        """Get a journal entry by ID."""
        return self._entries.get(entry_id)
    
    def get_correction(self, correction_id: str) -> Optional[Correction[T]]:
        """Get a correction by ID."""
        return self._corrections.get(correction_id)
    
    def get_correlation_chain(self, correlation_id: str) -> List[JournalEntry[T]]:
        """Get all journal entries for a given correlation ID."""
        entry_ids = self._correlation_chain.get(correlation_id, [])
        return [self._entries[eid] for eid in entry_ids if eid in self._entries]
    
    def get_entries_since(
        self, 
        timestamp: datetime,
        include_corrections: bool = False
    ) -> List[JournalEntry[T]]:
        """Get all journal entries since the given timestamp."""
        return [
            entry for entry in self._entries.values()
            if entry.timestamp > timestamp and 
               (include_corrections or not entry.corrections)
        ]
    
    def get_entries_for_path(
        self, 
        path: StatePath,
        since: Optional[datetime] = None
    ) -> List[JournalEntry[T]]:
        """Get all journal entries that modified the given path."""
        result = []
        for entry in self._entries.values():
            if since and entry.timestamp <= since:
                continue
                
            # Check if this entry's transition affects the target path
            if self._path_matches(entry.transition.path, path):
                result.append(entry)
                
        return result
    
    def _path_matches(self, path1: StatePath, path2: StatePath) -> bool:
        """Check if two paths match, with support for wildcards."""
        # Exact match
        if path1 == path2:
            return True
            
        # Path1 is a prefix of path2 (e.g., "a.b" matches "a.b.c")
        if len(path1.parts) < len(path2.parts):
            return path1.parts == path2.parts[:len(path1.parts)]
            
        return False
    
    def get_audit_trail(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        include_corrections: bool = True
    ) -> List[Dict[str, Any]]:
        """Generate an audit trail of all state changes."""
        audit = []
        
        for entry in sorted(self._entries.values(), key=lambda e: e.timestamp):
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
                
            entry_dict = {
                "timestamp": entry.timestamp.isoformat(),
                "entry_id": entry.entry_id,
                "correlation_id": entry.correlation_id,
                "operation": entry.transition.operation.value,
                "path": str(entry.transition.path),
                "metadata": entry.metadata,
                "corrections": []
            }
            
            if include_corrections:
                for correction in entry.corrections:
                    entry_dict["corrections"].append({
                        "correction_id": correction.correction_id,
                        "type": correction.correction_type.value,
                        "timestamp": correction.timestamp.isoformat(),
                        "reason": correction.reason,
                        "metadata": correction.metadata
                    })
            
            audit.append(entry_dict)
        
        return audit

# Singleton instance for global access
_journal: Optional[StateJournal] = None

def get_global_journal() -> StateJournal:
    """Get or create the global state journal instance."""
    global _journal
    if _journal is None:
        _journal = StateJournal()
    return _journal

def record_transition(
    transition: StateTransition[T],
    snapshot_before: StateSnapshot[T],
    snapshot_after: StateSnapshot[T],
    correlation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> JournalEntry[T]:
    """Record a state transition in the global journal."""
    return get_global_journal().record(
        transition=transition,
        snapshot_before=snapshot_before,
        snapshot_after=snapshot_after,
        correlation_id=correlation_id,
        metadata=metadata or {}
    )



