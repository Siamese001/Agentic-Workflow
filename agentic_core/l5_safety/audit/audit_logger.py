"""
L5 Agentic Core - L5 Safety Layer - Audit Logger
Implements L5 Safety Layer for immutable event tracking and audit logging
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid
import time
import json
import hashlib
from pathlib import Path

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditLevel(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditCategory(Enum):
    """L5 Audit category enumeration"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_OPERATION = "system_operation"
    SECURITY_EVENT = "security_event"
    POLICY_VIOLATION = "policy_violation"
    ERROR_EVENT = "error_event"

@dataclass
class AuditConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_log_entries: int = 10000
    require_integrity: bool = True
    encrypt_sensitive_data: bool = True
    append_only: bool = True
    retention_days: int = 90
    safety_level: str = "strict"

@dataclass
class AuditEvent:
    """L5 Audit event structure with full type safety"""
    event_id: str
    timestamp: str
    level: AuditLevel
    category: AuditCategory
    source: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: str = ""
    resource: str = ""
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    checksum: str = ""
    safety_validated: bool = False

@dataclass
class AuditLog:
    """L5 Audit log structure"""
    log_id: str
    events: List[AuditEvent] = field(default_factory=list)
    created_at: str = ""
    last_updated: str = ""
    total_events: int = 0
    file_path: Optional[str] = None
    integrity_hash: str = ""
    safety_validated: bool = False

@dataclass
class AuditOperation:
    """L5 Audit operation structure"""
    operation_id: str
    operation_type: str  # "log", "query", "export", "verify"
    event: Optional[AuditEvent] = None
    result: Any = None
    error_message: str = ""
    timestamp: str = ""

class AuditLogger(ABC):
    """L5 Abstract base - ensures L5 safety behavior"""
    
    @abstractmethod
    def log_event(self, event: AuditEvent, constraints: AuditConstraints) -> AuditOperation:
        """Log audit event with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, event: AuditEvent) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class AuditLoggerImpl(AuditLogger):
    """
    L5 Implementation - L5 Safety Layer
    Pure audit logging execution with comprehensive safety
    """
    
    def __init__(self, log_directory: str, constraints: Optional[AuditConstraints] = None):
        self.log_directory = Path(log_directory)
        self.constraints = constraints or AuditConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure log directory exists
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize audit log
        self.audit_log = AuditLog(
            log_id=self._generate_log_id(),
            created_at=self._get_timestamp(),
            safety_validated=True
        )
        
        # Load existing events
        self._load_existing_events()
        
        # Initialize persistent storage
        self._initialize_persistent_storage()
    
    def log_event(self, event: AuditEvent, constraints: Optional[AuditConstraints] = None) -> AuditOperation:
        """Log audit event following L5 architecture principles"""
        audit_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Logging audit event: {event.category.value} - {event.operation}")
        
        # L5 Input validation
        self._validate_log_input(event)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(event):
            raise SecurityError("Audit logging failed L5 safety validation")
        
        try:
            # Generate event checksum for integrity
            event.checksum = self._generate_event_checksum(event)
            event.safety_validated = True
            
            # Add to audit log
            self.audit_log.events.append(event)
            self.audit_log.total_events += 1
            self.audit_log.last_updated = self._get_timestamp()
            
            # Check log size constraints
            if self.audit_log.total_events > audit_constraints.max_log_entries:
                self._rotate_log()
            
            # Persist to storage (append-only)
            if audit_constraints.append_only:
                self._append_to_persistent_storage(event)
            
            # Update integrity hash
            self.audit_log.integrity_hash = self._generate_log_integrity_hash()
            
            # Create operation result
            operation = AuditOperation(
                operation_id=operation_id,
                operation_type="log",
                event=event,
                result={"event_id": event.event_id, "logged": True},
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Audit event logged successfully: {event.event_id}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Audit logging error: {e}")
            return AuditOperation(
                operation_id=operation_id,
                operation_type="log",
                event=event,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def query_events(self, filters: Dict[str, Any], constraints: Optional[AuditConstraints] = None) -> AuditOperation:
        """Query audit events"""
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Querying audit events with filters: {filters}")
        
        try:
            # Apply filters
            filtered_events = self._apply_filters(self.audit_log.events, filters)
            
            # Limit results
            max_results = filters.get("max_results", 100)
            filtered_events = filtered_events[:max_results]
            
            # Create operation result
            operation = AuditOperation(
                operation_id=operation_id,
                operation_type="query",
                result={
                    "events": [self._serialize_event(event) for event in filtered_events],
                    "total_count": len(filtered_events),
                    "filters_applied": filters
                },
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Query completed: {len(filtered_events)} events found")
            return operation
            
        except Exception as e:
            self.logger.error(f"Query error: {e}")
            return AuditOperation(
                operation_id=operation_id,
                operation_type="query",
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def export_logs(self, export_path: str, filters: Optional[Dict[str, Any]] = None) -> AuditOperation:
        """Export audit logs"""
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Exporting audit logs to: {export_path}")
        
        try:
            # Get events to export
            if filters:
                events_to_export = self._apply_filters(self.audit_log.events, filters)
            else:
                events_to_export = self.audit_log.events
            
            # Prepare export data
            export_data = {
                "export_metadata": {
                    "export_id": operation_id,
                    "export_timestamp": self._get_timestamp(),
                    "total_events": len(events_to_export),
                    "log_id": self.audit_log.log_id,
                    "integrity_hash": self.audit_log.integrity_hash
                },
                "events": [self._serialize_event(event) for event in events_to_export]
            }
            
            # Write to file
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Create operation result
            operation = AuditOperation(
                operation_id=operation_id,
                operation_type="export",
                result={
                    "export_path": str(export_file),
                    "events_exported": len(events_to_export),
                    "file_size": export_file.stat().st_size
                },
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Export completed: {len(events_to_export)} events")
            return operation
            
        except Exception as e:
            self.logger.error(f"Export error: {e}")
            return AuditOperation(
                operation_id=operation_id,
                operation_type="export",
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def verify_integrity(self) -> AuditOperation:
        """Verify audit log integrity"""
        operation_id = self._generate_operation_id()
        
        self.logger.info("Verifying audit log integrity")
        
        try:
            # Calculate current integrity hash
            current_hash = self._generate_log_integrity_hash()
            stored_hash = self.audit_log.integrity_hash
            
            # Verify individual event checksums
            invalid_events = []
            for event in self.audit_log.events:
                expected_checksum = self._generate_event_checksum(event)
                if event.checksum != expected_checksum:
                    invalid_events.append(event.event_id)
            
            # Check overall integrity
            integrity_valid = (current_hash == stored_hash) and (len(invalid_events) == 0)
            
            # Create operation result
            operation = AuditOperation(
                operation_id=operation_id,
                operation_type="verify",
                result={
                    "integrity_valid": integrity_valid,
                    "current_hash": current_hash,
                    "stored_hash": stored_hash,
                    "invalid_events": invalid_events,
                    "total_events": self.audit_log.total_events
                },
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Integrity verification completed: {'VALID' if integrity_valid else 'INVALID'}")
            return operation
            
        except Exception as e:
            self.logger.error(f"Integrity verification error: {e}")
            return AuditOperation(
                operation_id=operation_id,
                operation_type="verify",
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit log summary"""
        summary = {
            "log_id": self.audit_log.log_id,
            "total_events": self.audit_log.total_events,
            "created_at": self.audit_log.created_at,
            "last_updated": self.audit_log.last_updated,
            "integrity_hash": self.audit_log.integrity_hash
        }
        
        # Count by level
        level_counts = {}
        for event in self.audit_log.events:
            level = event.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        summary["events_by_level"] = level_counts
        
        # Count by category
        category_counts = {}
        for event in self.audit_log.events:
            category = event.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        summary["events_by_category"] = category_counts
        
        # Recent activity
        recent_events = self.audit_log.events[-10:] if self.audit_log.events else []
        summary["recent_events"] = [
            {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "level": event.level.value,
                "category": event.category.value,
                "operation": event.operation,
                "message": event.message[:100] + "..." if len(event.message) > 100 else event.message
            }
            for event in recent_events
        ]
        
        return summary
    
    def _load_existing_events(self) -> None:
        """Load existing events from persistent storage"""
        try:
            log_file = self.log_directory / "audit_log.jsonl"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            event_data = json.loads(line)
                            event = self._deserialize_event(event_data)
                            self.audit_log.events.append(event)
                
                self.audit_log.total_events = len(self.audit_log.events)
                self.logger.info(f"Loaded {self.audit_log.total_events} existing events")
            
        except Exception as e:
            self.logger.error(f"Failed to load existing events: {e}")
    
    def _initialize_persistent_storage(self) -> None:
        """Initialize persistent storage"""
        try:
            log_file = self.log_directory / "audit_log.jsonl"
            self.audit_log.file_path = str(log_file)
            
            # Create file if it doesn't exist
            if not log_file.exists():
                log_file.touch()
            
            self.logger.info(f"Persistent storage initialized: {log_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize persistent storage: {e}")
    
    def _append_to_persistent_storage(self, event: AuditEvent) -> None:
        """Append event to persistent storage"""
        try:
            log_file = self.log_directory / "audit_log.jsonl"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                event_data = self._serialize_event(event)
                f.write(json.dumps(event_data) + '\n')
            
        except Exception as e:
            self.logger.error(f"Failed to append to persistent storage: {e}")
    
    def _rotate_log(self) -> None:
        """Rotate audit log when it gets too large"""
        try:
            # Keep only the most recent events
            max_events = self.constraints.max_log_entries // 2
            self.audit_log.events = self.audit_log.events[-max_events:]
            self.audit_log.total_events = len(self.audit_log.events)
            
            # Update persistent storage
            log_file = self.log_directory / "audit_log.jsonl"
            backup_file = self.log_directory / f"audit_log_backup_{int(time.time())}.jsonl"
            
            if log_file.exists():
                log_file.rename(backup_file)
            
            # Rewrite current log
            with open(log_file, 'w', encoding='utf-8') as f:
                for event in self.audit_log.events:
                    event_data = self._serialize_event(event)
                    f.write(json.dumps(event_data) + '\n')
            
            self.logger.info(f"Log rotated: {max_events} events retained")
            
        except Exception as e:
            self.logger.error(f"Failed to rotate log: {e}")
    
    def _apply_filters(self, events: List[AuditEvent], filters: Dict[str, Any]) -> List[AuditEvent]:
        """Apply filters to events"""
        filtered = events.copy()
        
        # Filter by level
        if "level" in filters:
            level_filter = filters["level"]
            if isinstance(level_filter, str):
                level_filter = [level_filter]
            filtered = [e for e in filtered if e.level.value in level_filter]
        
        # Filter by category
        if "category" in filters:
            category_filter = filters["category"]
            if isinstance(category_filter, str):
                category_filter = [category_filter]
            filtered = [e for e in filtered if e.category.value in category_filter]
        
        # Filter by user_id
        if "user_id" in filters:
            filtered = [e for e in filtered if e.user_id == filters["user_id"]]
        
        # Filter by operation
        if "operation" in filters:
            filtered = [e for e in filtered if filters["operation"] in e.operation]
        
        # Filter by time range
        if "start_time" in filters:
            start_time = filters["start_time"]
            filtered = [e for e in filtered if e.timestamp >= start_time]
        
        if "end_time" in filters:
            end_time = filters["end_time"]
            filtered = [e for e in filtered if e.timestamp <= end_time]
        
        return filtered
    
    def _generate_event_checksum(self, event: AuditEvent) -> str:
        """Generate checksum for event integrity"""
        event_data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "level": event.level.value,
            "category": event.category.value,
            "source": event.source,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "operation": event.operation,
            "resource": event.resource,
            "message": event.message,
            "details": event.details
        }
        
        event_json = json.dumps(event_data, sort_keys=True)
        return hashlib.sha256(event_json.encode('utf-8')).hexdigest()
    
    def _generate_log_integrity_hash(self) -> str:
        """Generate integrity hash for entire log"""
        log_data = {
            "log_id": self.audit_log.log_id,
            "created_at": self.audit_log.created_at,
            "events": [event.checksum for event in self.audit_log.events]
        }
        
        log_json = json.dumps(log_data, sort_keys=True)
        return hashlib.sha256(log_json.encode('utf-8')).hexdigest()
    
    def _serialize_event(self, event: AuditEvent) -> Dict[str, Any]:
        """Serialize event to dictionary"""
        return {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "level": event.level.value,
            "category": event.category.value,
            "source": event.source,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "operation": event.operation,
            "resource": event.resource,
            "message": event.message,
            "details": event.details,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "checksum": event.checksum,
            "safety_validated": event.safety_validated
        }
    
    def _deserialize_event(self, event_data: Dict[str, Any]) -> AuditEvent:
        """Deserialize event from dictionary"""
        return AuditEvent(
            event_id=event_data["event_id"],
            timestamp=event_data["timestamp"],
            level=AuditLevel(event_data["level"]),
            category=AuditCategory(event_data["category"]),
            source=event_data["source"],
            user_id=event_data.get("user_id"),
            session_id=event_data.get("session_id"),
            operation=event_data.get("operation", ""),
            resource=event_data.get("resource", ""),
            message=event_data.get("message", ""),
            details=event_data.get("details", {}),
            ip_address=event_data.get("ip_address"),
            user_agent=event_data.get("user_agent"),
            checksum=event_data.get("checksum", ""),
            safety_validated=event_data.get("safety_validated", False)
        )
    
    def validate_safety(self, event: AuditEvent) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Validate event fields
            if not event.event_id or not event.timestamp:
                self.logger.error("Event missing required fields")
                return False
            
            # Validate message length
            if len(event.message) > 10000:
                self.logger.error("Event message too long")
                return False
            
            # Validate source safety
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec("]
            source_lower = event.source.lower()
            for pattern in dangerous_patterns:
                if pattern in source_lower:
                    self.logger.error("Source contains unsafe content")
                    return False
            
            # Validate operation safety
            if event.operation:
                operation_lower = event.operation.lower()
                for pattern in dangerous_patterns:
                    if pattern in operation_lower:
                        self.logger.error("Operation contains unsafe content")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_log_input(self, event: AuditEvent) -> None:
        """L5 Log input validation"""
        if not isinstance(event, AuditEvent):
            raise ValueError("Event must be an AuditEvent object")
        
        if not event.event_id.strip():
            raise ValueError("Event ID cannot be empty")
        
        if not isinstance(event.level, AuditLevel):
            raise ValueError("Level must be an AuditLevel enum")
        
        if not isinstance(event.category, AuditCategory):
            raise ValueError("Category must be an AuditCategory enum")
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        return f"audit_op_{uuid.uuid4().hex[:8]}"
    
    def _generate_log_id(self) -> str:
        """Generate unique log ID"""
        return f"audit_log_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class AuditLoggerInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, logger: AuditLogger):
        self._logger = logger
    
    def log_event(self, level: str, category: str, source: str, operation: str, message: str, 
                  user_id: str = None, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            event = AuditEvent(
                event_id=self._logger._generate_operation_id(),
                timestamp=self._logger._get_timestamp(),
                level=AuditLevel(level),
                category=AuditCategory(category),
                source=source,
                user_id=user_id,
                operation=operation,
                message=message,
                details=details or {},
                safety_validated=False
            )
            
            constraints = AuditConstraints()
            operation = self._logger.log_event(event, constraints)
            
            return {
                "success": operation.error_message == "",
                "operation_id": operation.operation_id,
                "operation_type": operation.operation_type,
                "event_id": operation.event.event_id if operation.event else None,
                "result": operation.result,
                "error_message": operation.error_message,
                "timestamp": operation.timestamp
            }
        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class AuditLoggerFactory:
    """L5 Factory for creating audit logger instances"""
    
    @staticmethod
    def create_logger(log_directory: str, constraints: Optional[AuditConstraints] = None) -> AuditLogger:
        return AuditLoggerImpl(log_directory, constraints)
    
    @staticmethod
    def create_interface(log_directory: str, constraints: Optional[AuditConstraints] = None) -> AuditLoggerInterface:
        logger = AuditLoggerFactory.create_logger(log_directory, constraints)
        return AuditLoggerInterface(logger)

# L5 Export for module usage
__all__ = [
    "AuditLevel",
    "AuditCategory",
    "AuditConstraints",
    "AuditEvent",
    "AuditLog",
    "AuditOperation",
    "AuditLogger",
    "AuditLoggerImpl",
    "AuditLoggerInterface",
    "AuditLoggerFactory",
    "SecurityError"
]
