"""
L5 Agentic Core - L4 Memory Layer - Persistent Storage
Implements L4 Memory Layer for long-term persistent storage operations
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid
import time
import json
import os
from pathlib import Path

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    FILE = "file"
    DATABASE = "database"
    CACHE = "cache"
    ARCHIVE = "archive"

class StorageStatus(Enum):
    """L5 Storage status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CORRUPTED = "corrupted"
    LOCKED = "locked"
    ERROR = "error"

@dataclass
class StorageConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_file_size: int = 1000000  # 1MB
    max_records: int = 10000
    require_encryption: bool = False
    allowed_extensions: List[str] = field(default_factory=lambda: [".json", ".txt", ".yaml"])
    blocked_paths: List[str] = field(default_factory=lambda: ["system", "config", "temp"])
    safety_level: str = "strict"

@dataclass
class StorageRecord:
    """L5 Storage record structure with full type safety"""
    record_id: str
    key: str
    value: Any
    storage_type: StorageType
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    last_modified: str = ""
    version: int = 1
    size: int = 0
    checksum: str = ""
    safety_validated: bool = False

@dataclass
class StorageOperation:
    """L5 Storage operation structure"""
    operation_id: str
    operation_type: str  # "save", "load", "delete", "backup", "restore"
    record_id: Optional[str] = None
    key: Optional[str] = None
    file_path: Optional[str] = None
    result: Any = None
    error_message: str = ""
    timestamp: str = ""

@dataclass
class StorageState:
    """L5 Storage state structure"""
    state_id: str
    records: Dict[str, StorageRecord] = field(default_factory=dict)
    total_size: int = 0
    record_count: int = 0
    storage_directory: str = ""
    last_backup: str = ""
    safety_validated: bool = False
    timestamp: str = ""

class PersistentStorage(ABC):
    """L5 Abstract base - ensures L4 memory behavior"""
    
    @abstractmethod
    def save(self, key: str, value: Any, storage_type: StorageType, constraints: StorageConstraints) -> StorageOperation:
        """Save value to persistent storage with L5 safety constraints"""
        pass
    
    @abstractmethod
    def load(self, key: str, constraints: StorageConstraints) -> StorageOperation:
        """Load value from persistent storage with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, key: str, value: Any, file_path: Optional[str] = None) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class PersistentStorageImpl(PersistentStorage):
    """
    L5 Implementation - L4 Memory Layer
    Pure persistent storage execution with comprehensive safety
    """
    
    def __init__(self, storage_directory: str, constraints: Optional[StorageConstraints] = None):
        self.storage_directory = Path(storage_directory)
        self.constraints = constraints or StorageConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure storage directory exists
        self.storage_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage state
        self.storage_state = StorageState(
            state_id=self._generate_state_id(),
            storage_directory=str(self.storage_directory),
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        # Load existing records
        self._load_existing_records()
        
        self.operations: List[StorageOperation] = []
    
    def save(self, key: str, value: Any, storage_type: StorageType, constraints: Optional[StorageConstraints] = None) -> StorageOperation:
        """Save value to persistent storage following L5 architecture principles"""
        storage_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Saving value to persistent storage: {key}")
        
        # L5 Input validation
        self._validate_save_input(key, value, storage_type)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(key, value):
            raise SecurityError("Storage save operation failed L5 safety validation")
        
        try:
            # Generate file path
            file_path = self._generate_file_path(key, storage_type, storage_constraints)
            
            # Check storage constraints
            if not self._check_save_constraints(key, value, file_path, storage_constraints):
                return StorageOperation(
                    operation_id=operation_id,
                    operation_type="save",
                    key=key,
                    file_path=file_path,
                    error_message="Storage constraints violated",
                    timestamp=self._get_timestamp()
                )
            
            # Serialize value
            serialized_value = self._serialize_value(value)
            
            # Calculate checksum
            checksum = self._calculate_checksum(serialized_value)
            
            # Create storage record
            record_id = self._generate_record_id()
            record = StorageRecord(
                record_id=record_id,
                key=key,
                value=value,
                storage_type=storage_type,
                file_path=file_path,
                created_at=self._get_timestamp(),
                last_modified=self._get_timestamp(),
                size=len(serialized_value),
                checksum=checksum,
                safety_validated=True
            )
            
            # Write to file
            self._write_to_file(file_path, serialized_value)
            
            # Update storage state
            self.storage_state.records[record_id] = record
            self.storage_state.total_size += record.size
            self.storage_state.record_count += 1
            self.storage_state.timestamp = self._get_timestamp()
            
            # Create operation result
            operation = StorageOperation(
                operation_id=operation_id,
                operation_type="save",
                record_id=record_id,
                key=key,
                file_path=file_path,
                result={"record_id": record_id, "file_path": file_path, "size": record.size},
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Value saved successfully: {key} -> {file_path}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Storage save error: {e}")
            return StorageOperation(
                operation_id=operation_id,
                operation_type="save",
                key=key,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def load(self, key: str, constraints: Optional[StorageConstraints] = None) -> StorageOperation:
        """Load value from persistent storage following L5 architecture principles"""
        storage_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Loading value from persistent storage: {key}")
        
        # L5 Input validation
        self._validate_load_input(key)
        
        try:
            # Find record by key
            record = self._find_record_by_key(key)
            
            if not record:
                return StorageOperation(
                    operation_id=operation_id,
                    operation_type="load",
                    key=key,
                    error_message="Key not found",
                    timestamp=self._get_timestamp()
                )
            
            # Check file exists
            if not os.path.exists(record.file_path):
                return StorageOperation(
                    operation_id=operation_id,
                    operation_type="load",
                    key=key,
                    file_path=record.file_path,
                    error_message="File not found",
                    timestamp=self._get_timestamp()
                )
            
            # Read from file
            serialized_value = self._read_from_file(record.file_path)
            
            # Verify checksum
            current_checksum = self._calculate_checksum(serialized_value)
            if current_checksum != record.checksum:
                return StorageOperation(
                    operation_id=operation_id,
                    operation_type="load",
                    key=key,
                    file_path=record.file_path,
                    error_message="File corrupted (checksum mismatch)",
                    timestamp=self._get_timestamp()
                )
            
            # Deserialize value
            value = self._deserialize_value(serialized_value)
            
            # Update access information
            record.last_modified = self._get_timestamp()
            
            # Create operation result
            operation = StorageOperation(
                operation_id=operation_id,
                operation_type="load",
                record_id=record.record_id,
                key=key,
                file_path=record.file_path,
                result=value,
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Value loaded successfully: {key}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Storage load error: {e}")
            return StorageOperation(
                operation_id=operation_id,
                operation_type="load",
                key=key,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def delete(self, key: str, constraints: Optional[StorageConstraints] = None) -> StorageOperation:
        """Delete value from persistent storage"""
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Deleting value from persistent storage: {key}")
        
        # L5 Input validation
        self._validate_load_input(key)
        
        try:
            # Find record by key
            record = self._find_record_by_key(key)
            
            if not record:
                return StorageOperation(
                    operation_id=operation_id,
                    operation_type="delete",
                    key=key,
                    error_message="Key not found",
                    timestamp=self._get_timestamp()
                )
            
            # Delete file
            if os.path.exists(record.file_path):
                os.remove(record.file_path)
            
            # Remove from storage state
            del self.storage_state.records[record.record_id]
            self.storage_state.total_size -= record.size
            self.storage_state.record_count -= 1
            self.storage_state.timestamp = self._get_timestamp()
            
            # Create operation result
            operation = StorageOperation(
                operation_id=operation_id,
                operation_type="delete",
                record_id=record.record_id,
                key=key,
                file_path=record.file_path,
                result={"deleted": True},
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Value deleted successfully: {key}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Storage delete error: {e}")
            return StorageOperation(
                operation_id=operation_id,
                operation_type="delete",
                key=key,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def backup(self, backup_path: str) -> StorageOperation:
        """Create backup of storage"""
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Creating backup: {backup_path}")
        
        try:
            # Validate backup path
            if not self._validate_path_safety(backup_path):
                return StorageOperation(
                    operation_id=operation_id,
                    operation_type="backup",
                    error_message="Invalid backup path",
                    timestamp=self._get_timestamp()
                )
            
            # Create backup directory
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all files
            backup_count = 0
            for record in self.storage_state.records.values():
                if record.file_path and os.path.exists(record.file_path):
                    backup_file = backup_dir / os.path.basename(record.file_path)
                    import shutil
                    shutil.copy2(record.file_path, backup_file)
                    backup_count += 1
            
            # Update storage state
            self.storage_state.last_backup = self._get_timestamp()
            
            # Create operation result
            operation = StorageOperation(
                operation_id=operation_id,
                operation_type="backup",
                result={"backup_path": backup_path, "backup_count": backup_count},
                timestamp=self._get_timestamp()
            )
            
            # Store operation
            self.operations.append(operation)
            
            self.logger.info(f"Backup created successfully: {backup_count} files")
            return operation
            
        except Exception as e:
            self.logger.error(f"Storage backup error: {e}")
            return StorageOperation(
                operation_id=operation_id,
                operation_type="backup",
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def _load_existing_records(self) -> None:
        """Load existing records from storage directory"""
        try:
            for file_path in self.storage_directory.rglob("*"):
                if file_path.is_file():
                    # Extract key from filename
                    key = file_path.stem
                    
                    try:
                        # Read and deserialize
                        serialized_value = self._read_from_file(str(file_path))
                        value = self._deserialize_value(serialized_value)
                        
                        # Create record
                        record = StorageRecord(
                            record_id=self._generate_record_id(),
                            key=key,
                            value=value,
                            storage_type=StorageType.FILE,
                            file_path=str(file_path),
                            created_at=self._get_timestamp(),
                            last_modified=self._get_timestamp(),
                            size=len(serialized_value),
                            checksum=self._calculate_checksum(serialized_value),
                            safety_validated=True
                        )
                        
                        self.storage_state.records[record.record_id] = record
                        self.storage_state.total_size += record.size
                        self.storage_state.record_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to load record from {file_path}: {e}")
            
            self.logger.info(f"Loaded {self.storage_state.record_count} existing records")
            
        except Exception as e:
            self.logger.error(f"Failed to load existing records: {e}")
    
    def _find_record_by_key(self, key: str) -> Optional[StorageRecord]:
        """Find record by key"""
        for record in self.storage_state.records.values():
            if record.key == key:
                return record
        return None
    
    def _generate_file_path(self, key: str, storage_type: StorageType, constraints: StorageConstraints) -> str:
        """Generate file path for storage"""
        # Sanitize key
        safe_key = "".join(c for c in key if c.isalnum() or c in ('_', '-'))
        
        # Determine extension
        if storage_type == StorageType.FILE:
            extension = constraints.allowed_extensions[0] if constraints.allowed_extensions else ".json"
        else:
            extension = ".json"
        
        # Generate unique filename
        filename = f"{safe_key}_{uuid.uuid4().hex[:8]}{extension}"
        
        return str(self.storage_directory / filename)
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value to string"""
        return json.dumps(value, default=str, ensure_ascii=False)
    
    def _deserialize_value(self, serialized_value: str) -> Any:
        """Deserialize value from string"""
        return json.loads(serialized_value)
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate checksum for data integrity"""
        import hashlib
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def _write_to_file(self, file_path: str, data: str) -> None:
        """Write data to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)
    
    def _read_from_file(self, file_path: str) -> str:
        """Read data from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _check_save_constraints(self, key: str, value: Any, file_path: str, constraints: StorageConstraints) -> bool:
        """Check if save operation violates constraints"""
        # Check record count
        if self.storage_state.record_count >= constraints.max_records:
            return False
        
        # Check file size
        serialized_value = self._serialize_value(value)
        if len(serialized_value) > constraints.max_file_size:
            return False
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in constraints.allowed_extensions:
            return False
        
        return True
    
    def validate_safety(self, key: str, value: Any, file_path: Optional[str] = None) -> bool:
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
            
            # Validate file path safety
            if file_path and not self._validate_path_safety(file_path):
                self.logger.error("File path contains unsafe content")
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
        
        elif isinstance(value, dict):
            for k, v in value.items():
                if not self._validate_key_safety(str(k)) or not self._validate_value_safety(v):
                    return False
        
        elif isinstance(value, list):
            for item in value:
                if not self._validate_value_safety(item):
                    return False
        
        return True
    
    def _validate_path_safety(self, file_path: str) -> bool:
        """Validate file path safety"""
        # Check for blocked paths
        path_lower = file_path.lower()
        for blocked_path in self.constraints.blocked_paths:
            if blocked_path in path_lower:
                return False
        
        # Check for path traversal
        if ".." in file_path:
            return False
        
        # Check for suspicious characters
        if any(char in file_path for char in ['<', '>', '|', '"', '\0']):
            return False
        
        return True
    
    def _validate_save_input(self, key: str, value: Any, storage_type: StorageType) -> None:
        """L5 Save input validation"""
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        
        if not isinstance(storage_type, StorageType):
            raise ValueError("Storage type must be a StorageType enum")
        
        if not key.strip():
            raise ValueError("Key cannot be empty")
    
    def _validate_load_input(self, key: str) -> None:
        """L5 Load input validation"""
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        
        if not key.strip():
            raise ValueError("Key cannot be empty")
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        return f"storage_op_{uuid.uuid4().hex[:8]}"
    
    def _generate_record_id(self) -> str:
        """Generate unique record ID"""
        return f"storage_rec_{uuid.uuid4().hex[:8]}"
    
    def _generate_state_id(self) -> str:
        """Generate unique state ID"""
        return f"storage_state_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class PersistentStorageInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, storage: PersistentStorage):
        self._storage = storage
    
    def save(self, key: str, value: Any, storage_type: str = "file", max_file_size: int = 1000000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            st_type = StorageType(storage_type)
            constraints = StorageConstraints(max_file_size=max_file_size)
            
            operation = self._storage.save(key, value, st_type, constraints)
            
            return {
                "success": operation.error_message == "",
                "operation_id": operation.operation_id,
                "operation_type": operation.operation_type,
                "record_id": operation.record_id,
                "key": operation.key,
                "file_path": operation.file_path,
                "result": operation.result,
                "error_message": operation.error_message,
                "timestamp": operation.timestamp
            }
        except Exception as e:
            self.logger.error(f"Storage save failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }
    
    def load(self, key: str) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            constraints = StorageConstraints()
            operation = self._storage.load(key, constraints)
            
            return {
                "success": operation.error_message == "",
                "operation_id": operation.operation_id,
                "operation_type": operation.operation_type,
                "record_id": operation.record_id,
                "key": operation.key,
                "result": operation.result,
                "error_message": operation.error_message,
                "timestamp": operation.timestamp
            }
        except Exception as e:
            self.logger.error(f"Storage load failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class PersistentStorageFactory:
    """L5 Factory for creating persistent storage instances"""
    
    @staticmethod
    def create_storage(storage_directory: str, constraints: Optional[StorageConstraints] = None) -> PersistentStorage:
        return PersistentStorageImpl(storage_directory, constraints)
    
    @staticmethod
    def create_interface(storage_directory: str, constraints: Optional[StorageConstraints] = None) -> PersistentStorageInterface:
        storage = PersistentStorageFactory.create_storage(storage_directory, constraints)
        return PersistentStorageInterface(storage)

# L5 Export for module usage
__all__ = [
    "StorageType",
    "StorageStatus",
    "StorageConstraints",
    "StorageRecord",
    "StorageOperation",
    "StorageState",
    "PersistentStorage",
    "PersistentStorageImpl",
    "PersistentStorageInterface",
    "PersistentStorageFactory",
    "SecurityError"
]
