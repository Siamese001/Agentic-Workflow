"""
L5 Agentic Core - L4 Memory Layer - State Tracker
Implements L4 Memory Layer for tracking and managing system state
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid
import time
import json
from collections import defaultdict

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StateType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    EXECUTION = "execution"
    MEMORY = "memory"
    SAFETY = "safety"
    SYSTEM = "system"
    USER = "user"

class StateStatus(Enum):
    """L5 State status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    CORRUPTED = "corrupted"
    ARCHIVED = "archived"

@dataclass
class StateConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_state_size: int = 50000  # 50KB
    max_state_entries: int = 1000
    max_history_entries: int = 100
    require_versioning: bool = True
    safety_level: str = "strict"

@dataclass
class StateEntry:
    """L5 State entry structure with full type safety"""
    entry_id: str
    key: str
    value: Any
    state_type: StateType
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    last_updated: str = ""
    version: int = 1
    access_count: int = 0
    size: int = 0
    safety_validated: bool = False

@dataclass
class StateSnapshot:
    """L5 State snapshot structure"""
    snapshot_id: str
    timestamp: str
    entries: Dict[str, StateEntry] = field(default_factory=dict)
    total_size: int = 0
    entry_count: int = 0
    checksum: str = ""
    safety_validated: bool = False

@dataclass
class StateTransition:
    """L5 State transition structure"""
    transition_id: str
    from_state: str
    to_state: str
    transition_type: str  # "update", "create", "delete", "restore"
    affected_keys: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

@dataclass
class StateOperation:
    """L5 State operation structure"""
    operation_id: str
    operation_type: str  # "get", "set", "delete", "snapshot", "restore"
    key: Optional[str] = None
    value: Any = None
    result: Any = None
    error_message: str = ""
    timestamp: str = ""

class StateTracker(ABC):
    """L5 Abstract base - ensures L4 memory behavior"""
    
    @abstractmethod
    def set_state(self, key: str, value: Any, state_type: StateType, constraints: StateConstraints) -> StateOperation:
        """Set state value with L5 safety constraints"""
        pass
    
    @abstractmethod
    def get_state(self, key: str, constraints: StateConstraints) -> StateOperation:
        """Get state value with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, key: str, value: Any, state_type: StateType) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class StateTrackerImpl(StateTracker):
    """
    L5 Implementation - L4 Memory Layer
    Pure state tracking execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[StateConstraints] = None):
        self.constraints = constraints or StateConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize state storage
        self.current_state: Dict[str, StateEntry] = {}
        self.state_history: List[StateSnapshot] = []
        self.transitions: List[StateTransition] = []
        
        # Initialize working memory and persistent storage
        from ..short_term.working_memory import WorkingMemoryFactory
        from ..long_term.persistent_storage import PersistentStorageFactory
        
        self.working_memory = WorkingMemoryFactory.create_memory()
        self.persistent_storage = PersistentStorageFactory.create_storage("./state_storage")
        
        # Load existing state
        self._load_existing_state()
    
    def set_state(self, key: str, value: Any, state_type: StateType, constraints: Optional[StateConstraints] = None) -> StateOperation:
        """Set state value following L5 architecture principles"""
        state_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Setting state: {key} ({state_type.value})")
        
        # L5 Input validation
        self._validate_set_input(key, value, state_type)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(key, value, state_type):
            raise SecurityError("State set operation failed L5 safety validation")
        
        try:
            # Check state constraints
            if not self._check_set_constraints(key, value, state_constraints):
                return StateOperation(
                    operation_id=operation_id,
                    operation_type="set",
                    key=key,
                    value=value,
                    error_message="State constraints violated",
                    timestamp=self._get_timestamp()
                )
            
            # Create state entry
            entry_id = self._generate_entry_id()
            entry_size = self._calculate_size(value)
            
            # Check if key already exists
            old_entry = self.current_state.get(key)
            from_state = "none" if not old_entry else old_entry.entry_id
            
            entry = StateEntry(
                entry_id=entry_id,
                key=key,
                value=value,
                state_type=state_type,
                created_at=self._get_timestamp() if not old_entry else old_entry.created_at,
                last_updated=self._get_timestamp(),
                version=old_entry.version + 1 if old_entry else 1,
                access_count=old_entry.access_count if old_entry else 0,
                size=entry_size,
                safety_validated=True
            )
            
            # Update current state
            self.current_state[key] = entry
            
            # Create transition
            transition = StateTransition(
                transition_id=self._generate_transition_id(),
                from_state=from_state,
                to_state=entry_id,
                transition_type="update" if old_entry else "create",
                affected_keys=[key],
                timestamp=self._get_timestamp()
            )
            self.transitions.append(transition)
            
            # Persist to storage
            self._persist_state_entry(entry)
            
            # Create operation result
            operation = StateOperation(
                operation_id=operation_id,
                operation_type="set",
                key=key,
                value=value,
                result={"entry_id": entry_id, "version": entry.version, "size": entry_size},
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"State set successfully: {key} (version: {entry.version})")
            return operation
            
        except Exception as e:
            self.logger.error(f"State set error: {e}")
            return StateOperation(
                operation_id=operation_id,
                operation_type="set",
                key=key,
                value=value,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def get_state(self, key: str, constraints: Optional[StateConstraints] = None) -> StateOperation:
        """Get state value following L5 architecture principles"""
        state_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Getting state: {key}")
        
        # L5 Input validation
        self._validate_get_input(key)
        
        try:
            # Find state entry
            entry = self.current_state.get(key)
            
            if not entry:
                return StateOperation(
                    operation_id=operation_id,
                    operation_type="get",
                    key=key,
                    error_message="State key not found",
                    timestamp=self._get_timestamp()
                )
            
            # Update access count
            entry.access_count += 1
            entry.last_updated = self._get_timestamp()
            
            # Create operation result
            operation = StateOperation(
                operation_id=operation_id,
                operation_type="get",
                key=key,
                result=entry.value,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"State retrieved successfully: {key}")
            return operation
            
        except Exception as e:
            self.logger.error(f"State get error: {e}")
            return StateOperation(
                operation_id=operation_id,
                operation_type="get",
                key=key,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def delete_state(self, key: str, constraints: Optional[StateConstraints] = None) -> StateOperation:
        """Delete state value"""
        state_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Deleting state: {key}")
        
        # L5 Input validation
        self._validate_get_input(key)
        
        try:
            # Find state entry
            entry = self.current_state.get(key)
            
            if not entry:
                return StateOperation(
                    operation_id=operation_id,
                    operation_type="delete",
                    key=key,
                    error_message="State key not found",
                    timestamp=self._get_timestamp()
                )
            
            # Remove from current state
            del self.current_state[key]
            
            # Create transition
            transition = StateTransition(
                transition_id=self._generate_transition_id(),
                from_state=entry.entry_id,
                to_state="none",
                transition_type="delete",
                affected_keys=[key],
                timestamp=self._get_timestamp()
            )
            self.transitions.append(transition)
            
            # Delete from persistent storage
            self._delete_state_entry(key)
            
            # Create operation result
            operation = StateOperation(
                operation_id=operation_id,
                operation_type="delete",
                key=key,
                result={"deleted": True},
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"State deleted successfully: {key}")
            return operation
            
        except Exception as e:
            self.logger.error(f"State delete error: {e}")
            return StateOperation(
                operation_id=operation_id,
                operation_type="delete",
                key=key,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def create_snapshot(self, snapshot_name: str) -> StateOperation:
        """Create state snapshot"""
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Creating state snapshot: {snapshot_name}")
        
        try:
            # Create snapshot
            snapshot_id = self._generate_snapshot_id()
            snapshot = StateSnapshot(
                snapshot_id=snapshot_id,
                timestamp=self._get_timestamp(),
                entries=self.current_state.copy(),
                total_size=sum(entry.size for entry in self.current_state.values()),
                entry_count=len(self.current_state),
                checksum=self._calculate_state_checksum(),
                safety_validated=True
            )
            
            # Add to history
            self.state_history.append(snapshot)
            
            # Limit history size
            if len(self.state_history) > self.constraints.max_history_entries:
                self.state_history.pop(0)
            
            # Persist snapshot
            self._persist_snapshot(snapshot, snapshot_name)
            
            # Create operation result
            operation = StateOperation(
                operation_id=operation_id,
                operation_type="snapshot",
                result={"snapshot_id": snapshot_id, "entry_count": snapshot.entry_count},
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Snapshot created successfully: {snapshot_name}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Snapshot creation error: {e}")
            return StateOperation(
                operation_id=operation_id,
                operation_type="snapshot",
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def restore_snapshot(self, snapshot_name: str) -> StateOperation:
        """Restore state from snapshot"""
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Restoring state snapshot: {snapshot_name}")
        
        try:
            # Load snapshot
            snapshot = self._load_snapshot(snapshot_name)
            
            if not snapshot:
                return StateOperation(
                    operation_id=operation_id,
                    operation_type="restore",
                    error_message="Snapshot not found",
                    timestamp=self._get_timestamp()
                )
            
            # Verify snapshot integrity
            current_checksum = self._calculate_state_checksum()
            if current_checksum != snapshot.checksum:
                self.logger.warning("Snapshot checksum mismatch, proceeding with restore")
            
            # Restore state
            self.current_state = snapshot.entries.copy()
            
            # Create transition
            transition = StateTransition(
                transition_id=self._generate_transition_id(),
                from_state="snapshot",
                to_state="restored",
                transition_type="restore",
                affected_keys=list(snapshot.entries.keys()),
                timestamp=self._get_timestamp()
            )
            self.transitions.append(transition)
            
            # Create operation result
            operation = StateOperation(
                operation_id=operation_id,
                operation_type="restore",
                result={"restored_entries": len(snapshot.entries)},
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Snapshot restored successfully: {snapshot_name}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Snapshot restore error: {e}")
            return StateOperation(
                operation_id=operation_id,
                operation_type="restore",
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state"""
        state_types = defaultdict(int)
        total_size = 0
        total_entries = len(self.current_state)
        
        for entry in self.current_state.values():
            state_types[entry.state_type.value] += 1
            total_size += entry.size
        
        return {
            "total_entries": total_entries,
            "total_size": total_size,
            "state_types": dict(state_types),
            "snapshot_count": len(self.state_history),
            "transition_count": len(self.transitions)
        }
    
    def _load_existing_state(self) -> None:
        """Load existing state from persistent storage"""
        try:
            # Load state summary
            from .working_memory import MemoryType
            operation = self.working_memory.retrieve("state_summary")
            
            if operation.result:
                summary = operation.result
                self.logger.info(f"Loaded existing state: {summary}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load existing state: {e}")
    
    def _persist_state_entry(self, entry: StateEntry) -> None:
        """Persist state entry to storage"""
        try:
            from .long_term.persistent_storage import StorageType
            self.persistent_storage.save(
                f"state_{entry.key}",
                {
                    "entry_id": entry.entry_id,
                    "key": entry.key,
                    "value": entry.value,
                    "state_type": entry.state_type.value,
                    "created_at": entry.created_at,
                    "last_updated": entry.last_updated,
                    "version": entry.version,
                    "access_count": entry.access_count,
                    "size": entry.size
                },
                StorageType.FILE
            )
        except Exception as e:
            self.logger.error(f"Failed to persist state entry: {e}")
    
    def _delete_state_entry(self, key: str) -> None:
        """Delete state entry from storage"""
        try:
            self.persistent_storage.delete(f"state_{key}")
        except Exception as e:
            self.logger.error(f"Failed to delete state entry: {e}")
    
    def _persist_snapshot(self, snapshot: StateSnapshot, snapshot_name: str) -> None:
        """Persist snapshot to storage"""
        try:
            from .long_term.persistent_storage import StorageType
            snapshot_data = {
                "snapshot_id": snapshot.snapshot_id,
                "timestamp": snapshot.timestamp,
                "entries": {k: {
                    "entry_id": v.entry_id,
                    "key": v.key,
                    "value": v.value,
                    "state_type": v.state_type.value,
                    "created_at": v.created_at,
                    "last_updated": v.last_updated,
                    "version": v.version,
                    "access_count": v.access_count,
                    "size": v.size
                } for k, v in snapshot.entries.items()},
                "total_size": snapshot.total_size,
                "entry_count": snapshot.entry_count,
                "checksum": snapshot.checksum
            }
            
            self.persistent_storage.save(f"snapshot_{snapshot_name}", snapshot_data, StorageType.FILE)
        except Exception as e:
            self.logger.error(f"Failed to persist snapshot: {e}")
    
    def _load_snapshot(self, snapshot_name: str) -> Optional[StateSnapshot]:
        """Load snapshot from storage"""
        try:
            operation = self.persistent_storage.load(f"snapshot_{snapshot_name}")
            
            if operation.result:
                snapshot_data = operation.result
                
                # Reconstruct entries
                entries = {}
                for key, entry_data in snapshot_data["entries"].items():
                    entry = StateEntry(
                        entry_id=entry_data["entry_id"],
                        key=entry_data["key"],
                        value=entry_data["value"],
                        state_type=StateType(entry_data["state_type"]),
                        created_at=entry_data["created_at"],
                        last_updated=entry_data["last_updated"],
                        version=entry_data["version"],
                        access_count=entry_data["access_count"],
                        size=entry_data["size"],
                        safety_validated=True
                    )
                    entries[key] = entry
                
                snapshot = StateSnapshot(
                    snapshot_id=snapshot_data["snapshot_id"],
                    timestamp=snapshot_data["timestamp"],
                    entries=entries,
                    total_size=snapshot_data["total_size"],
                    entry_count=snapshot_data["entry_count"],
                    checksum=snapshot_data["checksum"],
                    safety_validated=True
                )
                
                return snapshot
            
        except Exception as e:
            self.logger.error(f"Failed to load snapshot: {e}")
        
        return None
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate size of value in bytes"""
        if isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, dict):
            return len(str(value).encode('utf-8'))
        elif isinstance(value, list):
            return sum(self._calculate_size(item) for item in value)
        else:
            return len(str(value).encode('utf-8'))
    
    def _calculate_state_checksum(self) -> str:
        """Calculate checksum of current state"""
        import hashlib
        state_data = json.dumps({k: v.value for k, v in self.current_state.items()}, sort_keys=True)
        return hashlib.md5(state_data.encode('utf-8')).hexdigest()
    
    def _check_set_constraints(self, key: str, value: Any, constraints: StateConstraints) -> bool:
        """Check if set operation violates constraints"""
        # Check entry count
        if len(self.current_state) >= constraints.max_state_entries:
            return False
        
        # Check state size
        value_size = self._calculate_size(value)
        current_total_size = sum(entry.size for entry in self.current_state.values())
        if current_total_size + value_size > constraints.max_state_size:
            return False
        
        return True
    
    def validate_safety(self, key: str, value: Any, state_type: StateType) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Validate key safety
            if not self._validate_key_safety(key):
                self.logger.error("Key contains unsafe content")
                return False
            
            # Validate value safety
            if not self._validate_value_safety(value):
                self.logger.error("Value contains unsafe content")
                return False
            
            # Validate state type safety
            if not self._validate_state_type_safety(state_type):
                self.logger.error("State type contains unsafe content")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_key_safety(self, key: str) -> bool:
        """Validate key safety"""
        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
        key_lower = key.lower()
        
        for pattern in dangerous_patterns:
            if pattern in key_lower:
                return False
        
        if len(key) > 100:
            return False
        
        return True
    
    def _validate_value_safety(self, value: Any) -> bool:
        """Validate value safety"""
        if isinstance(value, str):
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            value_lower = value.lower()
            
            for pattern in dangerous_patterns:
                if pattern in value_lower:
                    return False
        
        elif isinstance(value, dict):
            for k, v in value.items():
                if not self._validate_key_safety(str(k)) or not self._validate_value_safety(v):
                    return False
        
        elif isinstance(value, list):
            for item in value:
                if not self._validate_value_safety(item):
                    return False
        
        return True
    
    def _validate_state_type_safety(self, state_type: StateType) -> bool:
        """Validate state type safety"""
        # All predefined state types are safe
        return isinstance(state_type, StateType)
    
    def _validate_set_input(self, key: str, value: Any, state_type: StateType) -> None:
        """L5 Set input validation"""
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        
        if not isinstance(state_type, StateType):
            raise ValueError("State type must be a StateType enum")
        
        if not key.strip():
            raise ValueError("Key cannot be empty")
    
    def _validate_get_input(self, key: str) -> None:
        """L5 Get input validation"""
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        
        if not key.strip():
            raise ValueError("Key cannot be empty")
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        return f"state_op_{uuid.uuid4().hex[:8]}"
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        return f"state_entry_{uuid.uuid4().hex[:8]}"
    
    def _generate_snapshot_id(self) -> str:
        """Generate unique snapshot ID"""
        return f"state_snapshot_{uuid.uuid4().hex[:8]}"
    
    def _generate_transition_id(self) -> str:
        """Generate unique transition ID"""
        return f"state_trans_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class StateTrackerInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, tracker: StateTracker):
        self._tracker = tracker
    
    def set_state(self, key: str, value: Any, state_type: str = "execution", max_size: int = 50000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            st_type = StateType(state_type)
            constraints = StateConstraints(max_state_size=max_size)
            
            operation = self._tracker.set_state(key, value, st_type, constraints)
            
            return {
                "success": operation.error_message == "",
                "operation_id": operation.operation_id,
                "operation_type": operation.operation_type,
                "key": operation.key,
                "result": operation.result,
                "error_message": operation.error_message,
                "timestamp": operation.timestamp
            }
        except Exception as e:
            self.logger.error(f"State set failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def get_state(self, key: str) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            constraints = StateConstraints()
            operation = self._tracker.get_state(key, constraints)
            
            return {
                "success": operation.error_message == "",
                "operation_id": operation.operation_id,
                "operation_type": operation.operation_type,
                "key": operation.key,
                "result": operation.result,
                "error_message": operation.error_message,
                "timestamp": operation.timestamp
            }
        except Exception as e:
            self.logger.error(f"State get failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class StateTrackerFactory:
    """L5 Factory for creating state tracker instances"""
    
    @staticmethod
    def create_tracker(constraints: Optional[StateConstraints] = None) -> StateTracker:
        return StateTrackerImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[StateConstraints] = None) -> StateTrackerInterface:
        tracker = StateTrackerFactory.create_tracker(constraints)
        return StateTrackerInterface(tracker)

# L5 Export for module usage
__all__ = [
    "StateType",
    "StateStatus",
    "StateConstraints",
    "StateEntry",
    "StateSnapshot",
    "StateTransition",
    "StateOperation",
    "StateTracker",
    "StateTrackerImpl",
    "StateTrackerInterface",
    "StateTrackerFactory",
    "SecurityError"
]
