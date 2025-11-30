from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

@dataclass
class EpisodicMemory:
    """Robust episodic memory implementation for resume processing."""
    memory_id: str
    content: Dict[str, Any]
    timestamp: datetime
    episode_type: str = "generic"
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.content:
            self.content = {}

    def process(self, *args, **kwargs) -> Any:
        """Process episodic memory with content validation."""
        return {
            "memory_id": self.memory_id,
            "episode_type": self.episode_type,
            "content_size": len(str(self.content)),
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "processed": True,
            "confidence": self.confidence
        }

    def add_tag(self, tag: str) -> None:
        """Add a tag to this memory."""
        if tag not in self.tags:
            self.tags.append(tag)

    def matches_tag(self, tag: str) -> bool:
        """Check if memory has a specific tag."""
        return tag in self.tags

@dataclass
class TemporalContext:
    """Enhanced temporal context with state tracking."""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    context_type: str = "generic"
    parent_context: Optional[str] = None
    children_contexts: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.data is None:
            self.data = {}

    def update_data(self, key: str, value: Any) -> None:
        """Update data and refresh timestamp."""
        self.data[key] = value
        self.updated_at = datetime.now()

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data value with default."""
        return self.data.get(key, default)

class ResumeStateManager:
    """Robust state manager for resume processing workflows."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memories: Dict[str, EpisodicMemory] = {}
        self.contexts: Dict[str, TemporalContext] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.state_history: List[Dict[str, Any]] = []
        self.event_handlers: Dict[str, List[Callable]] = {}

    async def store_memory(self, memory_id: str, content: Dict[str, Any],
                          episode_type: str = "generic",
                          tags: List[str] = None,
                          confidence: float = 1.0) -> Dict[str, Any]:
        """Store episodic memory with validation."""
        if tags is None:
            tags = []

        memory = EpisodicMemory(
            memory_id=memory_id,
            content=content,
            timestamp=datetime.now(),
            episode_type=episode_type,
            tags=tags,
            confidence=confidence
        )

        self.memories[memory_id] = memory

        # Record state change
        self._record_state_change("memory_stored", {"memory_id": memory_id})

        # Trigger event handlers
        await self._trigger_event("memory_stored", memory)

        self.logger.info(f"Stored episodic memory: {memory_id}")
        return {"id": memory_id, "status": "stored"}

    async def retrieve_memories(self, query: str = "", tags: List[str] = None,
                               episode_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve memories with filtering."""
        if tags is None:
            tags = []

        results = []
        for memory in self.memories.values():
            # Filter by tags
            if tags and not all(memory.matches_tag(tag) for tag in tags):
                continue

            # Filter by episode type
            if episode_type and memory.episode_type != episode_type:
                continue

            # Filter by content query (simple text search)
            if query:
                content_text = str(memory.content).lower()
                if query.lower() not in content_text:
                    continue

            results.append(memory.process())

            if len(results) >= limit:
                break

        return results

    async def create_context(self, context_id: str, name: str,
                           context_type: str = "generic",
                           parent_context: str = None,
                           initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new temporal context."""
        context = TemporalContext(
            name=name,
            data=initial_data or {},
            context_type=context_type,
            parent_context=parent_context
        )

        self.contexts[context_id] = context

        # Update parent context if provided
        if parent_context and parent_context in self.contexts:
            self.contexts[parent_context].children_contexts.append(context_id)

        self._record_state_change("context_created", {"context_id": context_id})

        self.logger.info(f"Created temporal context: {context_id}")
        return {"id": context_id, "status": "created"}

    async def update_context(self, context_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing temporal context."""
        if context_id not in self.contexts:
            raise ValueError(f"Context {context_id} not found")

        context = self.contexts[context_id]
        for key, value in updates.items():
            context.update_data(key, value)

        self._record_state_change("context_updated", {"context_id": context_id})

        return {"id": context_id, "status": "updated", "updated_keys": list(updates.keys())}

    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get temporal context by ID."""
        if context_id in self.contexts:
            context = self.contexts[context_id]
            return {
                "id": context_id,
                "name": context.name,
                "data": context.data,
                "type": context.context_type,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
                "parent": context.parent_context,
                "children": context.children_contexts
            }
        return None

    async def create_session(self, session_id: str, initial_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new processing session."""
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "state": initial_state or {},
            "status": "active",
            "memory_ids": [],
            "context_ids": []
        }

        self.active_sessions[session_id] = session_data
        self._record_state_change("session_created", {"session_id": session_id})

        return {"session_id": session_id, "status": "created"}

    async def update_session(self, session_id: str, state_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update session state."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session["state"].update(state_updates)
        session["updated_at"] = datetime.now().isoformat()

        self._record_state_change("session_updated", {"session_id": session_id})

        return {"session_id": session_id, "status": "updated"}

    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add event handler for specific event types."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def _trigger_event(self, event_type: str, data: Any) -> None:
        """Trigger event handlers for specific event type."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    self.logger.error(f"Event handler failed: {e}")

    def _record_state_change(self, change_type: str, details: Dict[str, Any]) -> None:
        """Record state change for audit trail."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "change_type": change_type,
            "details": details
        }
        self.state_history.append(record)

        # Keep history size manageable
        if len(self.state_history) > 1000:
            self.state_history = self.state_history[-500:]

    def get_state_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get state change history."""
        return self.state_history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get state manager statistics."""
        return {
            "total_memories": len(self.memories),
            "total_contexts": len(self.contexts),
            "active_sessions": len(self.active_sessions),
            "history_entries": len(self.state_history),
            "event_handlers": len(self.event_handlers)
        }
