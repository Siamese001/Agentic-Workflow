"""
L5 Agentic Core - L4 Memory Layer - Working Memory
Implements L4 Memory Layer for short-term working memory operations
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid
import time
from collections import OrderedDict

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    WORKING = "working"
    CONTEXT = "context"
    TEMPORARY = "temporary"
    SESSION = "session"

class MemoryStatus(Enum):
    """L5 Memory status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    CORRUPTED = "corrupted"

@dataclass
class MemoryConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_memory_size: int = 10000  # 10KB
    max_entries: int = 100
    max_entry_age: float = 3600.0  # 1 hour
    require_encryption: bool = False
    safety_level: str = "strict"

@dataclass
class MemoryEntry:
    """L5 Memory entry structure with full type safety"""
    entry_id: str
    key: str
    value: Any
    memory_type: MemoryType
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    last_accessed: str = ""
    access_count: int = 0
    size: int = 0
    safety_validated: bool = False

@dataclass
class MemoryOperation:
    """L5 Memory operation structure"""
    operation_id: str
    operation_type: str  # "store", "retrieve", "update", "delete", "clear"
    entry_id: Optional[str] = None
    key: Optional[str] = None
    value: Any = None
    result: Any = None
    error_message: str = ""
    timestamp: str = ""

@dataclass
class MemoryState:
    """L5 Memory state structure"""
    state_id: str
    entries: Dict[str, MemoryEntry] = field(default_factory=dict)
    total_size: int = 0
    entry_count: int = 0
    last_cleanup: str = ""
    safety_validated: bool = False
    timestamp: str = ""

class WorkingMemory(ABC):
    """L5 Abstract base - ensures L4 memory behavior"""
    
    @abstractmethod
    def store(self, key: str, value: Any, memory_type: MemoryType, constraints: MemoryConstraints) -> MemoryOperation:
        """Store value in working memory with L5 safety constraints"""
        pass
    
    @abstractmethod
    def retrieve(self, key: str, constraints: MemoryConstraints) -> MemoryOperation:
        """Retrieve value from working memory with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, key: str, value: Any) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class WorkingMemoryImpl(WorkingMemory):
    """
    L5 Implementation - L4 Memory Layer
    Pure working memory execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[MemoryConstraints] = None):
        self.constraints = constraints or MemoryConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory_state = MemoryState(
            state_id=self._generate_state_id(),
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        self.operations: List[MemoryOperation] = []
    
    def store(self, key: str, value: Any, memory_type: MemoryType, constraints: Optional[MemoryConstraints] = None) -> MemoryOperation:
        """Store value in working memory following L5 architecture principles"""
        memory_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Storing value in working memory: {key}")
        
        # L5 Input validation
        self._validate_store_input(key, value, memory_type)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(key, value):
            raise SecurityError("Memory store operation failed L5 safety validation")
        
        try:
            # Check memory constraints
            if not self._check_store_constraints(key, value, memory_constraints):
                return MemoryOperation(
                    operation_id=operation_id,
                    operation_type="store",
                    key=key,
                    value=value,
                    error_message="Memory constraints violated",
                    timestamp=self._get_timestamp()
                )
            
            # Create memory entry
            entry_id = self._generate_entry_id()
            entry_size = self._calculate_size(value)
            
            entry = MemoryEntry(
                entry_id=entry_id,
                key=key,
                value=value,
                memory_type=memory_type,
                created_at=self._get_timestamp(),
                last_accessed=self._get_timestamp(),
                access_count=0,
                size=entry_size,
                safety_validated=True
            )
            
            # Store in memory state
            self.memory_state.entries[entry_id] = entry
            self.memory_state.total_size += entry_size
            self.memory_state.entry_count += 1
            
            # Update memory state
            self.memory_state.timestamp = self._get_timestamp()
            
            # Create operation result
            operation = MemoryOperation(
                operation_id=operation_id,
                operation_type="store",
                entry_id=entry_id,
                key=key,
                value=value,
                result={"entry_id": entry_id, "size": entry_size},
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Value stored successfully: {key} (size: {entry_size})")
            return operation
            
        except Exception as e:
            self.logger.error(f"Memory store error: {e}")
            return MemoryOperation(
                operation_id=operation_id,
                operation_type="store",
                key=key,
                value=value,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def retrieve(self, key: str, constraints: Optional[MemoryConstraints] = None) -> MemoryOperation:
        """Retrieve value from working memory following L5 architecture principles"""
        memory_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Retrieving value from working memory: {key}")
        
        # L5 Input validation
        self._validate_retrieve_input(key)
        
        try:
            # Find entry by key
            entry = self._find_entry_by_key(key)
            
            if not entry:
                return MemoryOperation(
                    operation_id=operation_id,
                    operation_type="retrieve",
                    key=key,
                    error_message="Key not found",
                    timestamp=self._get_timestamp()
                )
            
            # Check if entry has expired
            if self._is_entry_expired(entry, memory_constraints):
                return MemoryOperation(
                    operation_id=operation_id,
                    operation_type="retrieve",
                    key=key,
                    error_message="Entry has expired",
                    timestamp=self._get_timestamp()
                )
            
            # Update access information
            entry.last_accessed = self._get_timestamp()
            entry.access_count += 1
            
            # Create operation result
            operation = MemoryOperation(
                operation_id=operation_id,
                operation_type="retrieve",
                entry_id=entry.entry_id,
                key=key,
                result=entry.value,
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Value retrieved successfully: {key}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Memory retrieve error: {e}")
            return MemoryOperation(
                operation_id=operation_id,
                operation_type="retrieve",
                key=key,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def update(self, key: str, value: Any, constraints: Optional[MemoryConstraints] = None) -> MemoryOperation:
        """Update value in working memory"""
        memory_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Updating value in working memory: {key}")
        
        # L5 Input validation
        self._validate_store_input(key, value, MemoryType.WORKING)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(key, value):
            raise SecurityError("Memory update operation failed L5 safety validation")
        
        try:
            # Find existing entry
            entry = self._find_entry_by_key(key)
            
            if not entry:
                return MemoryOperation(
                    operation_id=operation_id,
                    operation_type="update",
                    key=key,
                    value=value,
                    error_message="Key not found",
                    timestamp=self._get_timestamp()
                )
            
            # Calculate size difference
            old_size = entry.size
            new_size = self._calculate_size(value)
            size_diff = new_size - old_size
            
            # Check memory constraints
            if self.memory_state.total_size + size_diff > memory_constraints.max_memory_size:
                return MemoryOperation(
                    operation_id=operation_id,
                    operation_type="update",
                    key=key,
                    value=value,
                    error_message="Memory size limit exceeded",
                    timestamp=self._get_timestamp()
                )
            
            # Update entry
            entry.value = value
            entry.size = new_size
            entry.last_accessed = self._get_timestamp()
            
            # Update memory state
            self.memory_state.total_size += size_diff
            self.memory_state.timestamp = self._get_timestamp()
            
            # Create operation result
            operation = MemoryOperation(
                operation_id=operation_id,
                operation_type="update",
                entry_id=entry.entry_id,
                key=key,
                value=value,
                result={"entry_id": entry.entry_id, "size": new_size},
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Value updated successfully: {key}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Memory update error: {e}")
            return MemoryOperation(
                operation_id=operation_id,
                operation_type="update",
                key=key,
                value=value,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def delete(self, key: str, constraints: Optional[MemoryConstraints] = None) -> MemoryOperation:
        """Delete value from working memory"""
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Deleting value from working memory: {key}")
        
        # L5 Input validation
        self._validate_retrieve_input(key)
        
        try:
            # Find entry by key
            entry = self._find_entry_by_key(key)
            
            if not entry:
                return MemoryOperation(
                    operation_id=operation_id,
                    operation_type="delete",
                    key=key,
                    error_message="Key not found",
                    timestamp=self._get_timestamp()
                )
            
            # Remove from memory state
            del self.memory_state.entries[entry.entry_id]
            self.memory_state.total_size -= entry.size
            self.memory_state.entry_count -= 1
            self.memory_state.timestamp = self._get_timestamp()
            
            # Create operation result
            operation = MemoryOperation(
                operation_id=operation_id,
                operation_type="delete",
                entry_id=entry.entry_id,
                key=key,
                result={"entry_id": entry.entry_id, "deleted": True},
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Value deleted successfully: {key}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Memory delete error: {e}")
            return MemoryOperation(
                operation_id=operation_id,
                operation_type="delete",
                key=key,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def clear(self, memory_type: Optional[MemoryType] = None) -> MemoryOperation:
        """Clear working memory"""
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Clearing working memory: {memory_type.value if memory_type else 'all'}")
        
        try:
            if memory_type:
                # Clear specific type
                entries_to_delete = [entry for entry in self.memory_state.entries.values() 
                                   if entry.memory_type == memory_type]
                
                for entry in entries_to_delete:
                    del self.memory_state.entries[entry.entry_id]
                    self.memory_state.total_size -= entry.size
                    self.memory_state.entry_count -= 1
                
                cleared_count = len(entries_to_delete)
            else:
                # Clear all
                cleared_count = self.memory_state.entry_count
                self.memory_state.entries.clear()
                self.memory_state.total_size = 0
                self.memory_state.entry_count = 0
            
            self.memory_state.timestamp = self._get_timestamp()
            
            # Create operation result
            operation = MemoryOperation(
                operation_id=operation_id,
                operation_type="clear",
                result={"cleared_count": cleared_count},
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Memory cleared successfully: {cleared_count} entries")
            return operation
            
        except Exception as e:
            self.logger.error(f"Memory clear error: {e}")
            return MemoryOperation(
                operation_id=operation_id,
                operation_type="clear",
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def cleanup_expired(self, constraints: Optional[MemoryConstraints] = None) -> MemoryOperation:
        """Clean up expired entries"""
        memory_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info("Cleaning up expired memory entries")
        
        try:
            current_time = time.time()
            entries_to_delete = []
            
            for entry in self.memory_state.entries.values():
                created_time = time.mktime(time.strptime(entry.created_at, "%Y-%m-%dT%H:%M:%S.%f"))
                if current_time - created_time > memory_constraints.max_entry_age:
                    entries_to_delete.append(entry)
            
            # Delete expired entries
            for entry in entries_to_delete:
                del self.memory_state.entries[entry.entry_id]
                self.memory_state.total_size -= entry.size
                self.memory_state.entry_count -= 1
            
            self.memory_state.last_cleanup = self._get_timestamp()
            self.memory_state.timestamp = self._get_timestamp()
            
            # Create operation result
            operation = MemoryOperation(
                operation_id=operation_id,
                operation_type="cleanup",
                result={"cleaned_count": len(entries_to_delete)},
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Cleanup completed: {len(entries_to_delete)} entries removed")
            return operation
            
        except Exception as e:
            self.logger.error(f"Memory cleanup error: {e}")
            return MemoryOperation(
                operation_id=operation_id,
                operation_type="cleanup",
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def _find_entry_by_key(self, key: str) -> Optional[MemoryEntry]:
        """Find entry by key"""
        for entry in self.memory_state.entries.values():
            if entry.key == key:
                return entry
        return None
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate size of value in bytes"""
        if isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, (int, float)):
            return 8  # Approximate size
        elif isinstance(value, dict):
            return len(str(value).encode('utf-8'))
        elif isinstance(value, list):
            return sum(self._calculate_size(item) for item in value)
        else:
            return len(str(value).encode('utf-8'))
    
    def _check_store_constraints(self, key: str, value: Any, constraints: MemoryConstraints) -> bool:
        """Check if store operation violates constraints"""
        # Check entry count
        if self.memory_state.entry_count >= constraints.max_entries:
            return False
        
        # Check memory size
        value_size = self._calculate_size(value)
        if self.memory_state.total_size + value_size > constraints.max_memory_size:
            return False
        
        # Check key length
        if len(key) > 100:
            return False
        
        return True
    
    def _is_entry_expired(self, entry: MemoryEntry, constraints: MemoryConstraints) -> bool:
        """Check if entry has expired"""
        current_time = time.time()
        created_time = time.mktime(time.strptime(entry.created_at, "%Y-%m-%dT%H:%M:%S.%f"))
        return current_time - created_time > constraints.max_entry_age
    
    def validate_safety(self, key: str, value: Any) -> bool:
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
            
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_key_safety(self, key: str) -> bool:
        """Validate key safety"""
        # Check for dangerous patterns
        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
        key_lower = key.lower()
        
        for pattern in dangerous_patterns:
            if pattern in key_lower:
                return False
        
        # Check key length
        if len(key) > 100:
            return False
        
        # Check for suspicious characters
        if any(char in key for char in ['\0', '\r', '\n', '\t']):
            return False
        
        return True
    
    def _validate_value_safety(self, value: Any) -> bool:
        """Validate value safety"""
        if isinstance(value, str):
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            value_lower = value.lower()
            
            for pattern in dangerous_patterns:
                if pattern in value_lower:
                    return False
            
            # Check value length
            if len(value) > self.constraints.max_memory_size:
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
    
    def _validate_store_input(self, key: str, value: Any, memory_type: MemoryType) -> None:
        """L5 Store input validation"""
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        
        if not isinstance(memory_type, MemoryType):
            raise ValueError("Memory type must be a MemoryType enum")
        
        if not key.strip():
            raise ValueError("Key cannot be empty")
    
    def _validate_retrieve_input(self, key: str) -> None:
        """L5 Retrieve input validation"""
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        
        if not key.strip():
            raise ValueError("Key cannot be empty")
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        return f"mem_op_{uuid.uuid4().hex[:8]}"
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        return f"mem_entry_{uuid.uuid4().hex[:8]}"
    
    def _generate_state_id(self) -> str:
        """Generate unique state ID"""
        return f"mem_state_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class WorkingMemoryInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, memory: WorkingMemory):
        self._memory = memory
    
    def store(self, key: str, value: Any, memory_type: str = "working", max_size: int = 10000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            mem_type = MemoryType(memory_type)
            constraints = MemoryConstraints(max_memory_size=max_size)
            
            operation = self._memory.store(key, value, mem_type, constraints)
            
            return {
                "success": operation.error_message == "",
                "operation_id": operation.operation_id,
                "operation_type": operation.operation_type,
                "entry_id": operation.entry_id,
                "key": operation.key,
                "result": operation.result,
                "error_message": operation.error_message,
                "timestamp": operation.timestamp
            }
        except Exception as e:
            self.logger.error(f"Memory store failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def retrieve(self, key: str) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            constraints = MemoryConstraints()
            operation = self._memory.retrieve(key, constraints)
            
            return {
                "success": operation.error_message == "",
                "operation_id": operation.operation_id,
                "operation_type": operation.operation_type,
                "entry_id": operation.entry_id,
                "key": operation.key,
                "result": operation.result,
                "error_message": operation.error_message,
                "timestamp": operation.timestamp
            }
        except Exception as e:
            self.logger.error(f"Memory retrieve failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class WorkingMemoryFactory:
    """L5 Factory for creating working memory instances"""
    
    @staticmethod
    def create_memory(constraints: Optional[MemoryConstraints] = None) -> WorkingMemory:
        return WorkingMemoryImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[MemoryConstraints] = None) -> WorkingMemoryInterface:
        memory = WorkingMemoryFactory.create_memory(constraints)
        return WorkingMemoryInterface(memory)

# L5 Export for module usage
__all__ = [
    "MemoryType",
    "MemoryStatus",
    "MemoryConstraints",
    "MemoryEntry",
    "MemoryOperation",
    "MemoryState",
    "WorkingMemory",
    "WorkingMemoryImpl",
    "WorkingMemoryInterface",
    "WorkingMemoryFactory",
    "SecurityError"
]
