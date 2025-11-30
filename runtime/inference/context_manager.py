"""
Context management system for the agentic runtime.

Provides context storage, retrieval, and management for task execution,
conversation history, and user session state with persistence and caching.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, UTC
import logging
import time
import uuid
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ContextEntry:
    """Single context entry with metadata and content."""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    content_type: str = "text"  # text, json, binary, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    size_bytes: int = 0

    def __post_init__(self):
        """Calculate size after initialization."""
        if self.size_bytes == 0:
            self.size_bytes = len(self.content.encode('utf-8'))

    def is_expired(self) -> bool:
        """Check if context entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at


@dataclass
class ConversationContext:
    """Context for a conversation or session."""
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    entries: List[ContextEntry] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    max_entries: int = 1000
    max_size_bytes: int = 10 * 1024 * 1024  # 10MB

    def add_entry(self, entry: ContextEntry) -> bool:
        """Add an entry to the conversation context."""
        # Check size limits
        if len(self.entries) >= self.max_entries:
            self._evict_oldest()
        
        current_size = sum(e.size_bytes for e in self.entries)
        if current_size + entry.size_bytes > self.max_size_bytes:
            self._evict_until_space(entry.size_bytes)
        
        self.entries.append(entry)
        self.last_accessed = datetime.now(UTC)
        return True

    def get_recent_entries(self, limit: Optional[int] = None) -> List[ContextEntry]:
        """Get most recent entries from the context."""
        if limit:
            return self.entries[-limit:]
        return self.entries.copy()

    def get_entries_by_tag(self, tag: str) -> List[ContextEntry]:
        """Get entries filtered by tag."""
        return [entry for entry in self.entries if tag in entry.tags]

    def _evict_oldest(self) -> None:
        """Remove the oldest entry to make space."""
        if self.entries:
            self.entries.pop(0)

    def _evict_until_space(self, needed_bytes: int) -> None:
        """Remove entries until enough space is available."""
        current_size = sum(e.size_bytes for e in self.entries)
        while current_size + needed_bytes > self.max_size_bytes and self.entries:
            removed = self.entries.pop(0)
            current_size -= removed.size_bytes


@dataclass
class ContextQuery:
    """Query for searching context entries."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    content_type: Optional[str] = None
    tags: Optional[Set[str]] = None
    date_range: Optional[tuple[datetime, datetime]] = None
    limit: Optional[int] = None


class ContextManager:
    """
    Central context management system for the agentic runtime.
    
    Handles storage, retrieval, and lifecycle management of context data
    including conversations, user sessions, and task execution state.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize context manager with optional storage path."""
        self.storage_path = Path(storage_path) if storage_path else Path("runtime/cache/contexts")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.contexts: Dict[str, ConversationContext] = {}
        self.global_context: ConversationContext = ConversationContext(
            context_id="global",
            max_entries=10000,
            max_size_bytes=100 * 1024 * 1024  # 100MB
        )
        
        self._load_contexts()

    def create_context(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new conversation context.

        Args:
            user_id: User identifier
            session_id: Session identifier
            metadata: Additional context metadata

        Returns:
            Context ID for the newly created context
        """
        context = ConversationContext(
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {}
        )
        
        self.contexts[context.context_id] = context
        self._save_context(context)
        
        logger.info(f"Created context: {context.context_id} for user: {user_id}")
        return context.context_id

    def get_context(self, context_id: str) -> Optional[ConversationContext]:
        """Get a conversation context by ID."""
        context = self.contexts.get(context_id)
        if context:
            context.last_accessed = datetime.now(UTC)
        return context

    def add_context_entry(
        self,
        context_id: str,
        content: str,
        content_type: str = "text",
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """
        Add an entry to a conversation context.

        Args:
            context_id: Target context ID
            content: Entry content
            content_type: Type of content
            tags: Content tags for categorization
            metadata: Entry metadata
            expires_at: Expiration time for the entry

        Returns:
            True if entry was added successfully
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return False

        entry = ContextEntry(
            content=content,
            content_type=content_type,
            tags=tags or set(),
            metadata=metadata or {},
            expires_at=expires_at
        )

        success = context.add_entry(entry)
        if success:
            self._save_context(context)
            logger.debug(f"Added entry to context: {context_id}")

        return success

    def get_context_entries(
        self,
        context_id: str,
        limit: Optional[int] = None,
        tags: Optional[Set[str]] = None
    ) -> List[ContextEntry]:
        """
        Get entries from a conversation context.

        Args:
            context_id: Context ID
            limit: Maximum number of entries to return
            tags: Filter by tags

        Returns:
            List of context entries
        """
        context = self.get_context(context_id)
        if not context:
            return []

        entries = context.get_recent_entries(limit)
        
        if tags:
            entries = [entry for entry in entries if tags.intersection(entry.tags)]

        # Filter out expired entries
        entries = [entry for entry in entries if not entry.is_expired()]

        return entries

    def search_contexts(self, query: ContextQuery) -> List[ConversationContext]:
        """
        Search for contexts matching the query criteria.

        Args:
            query: Search query with filters

        Returns:
            List of matching conversation contexts
        """
        results = []
        
        for context in self.contexts.values():
            # Apply filters
            if query.user_id and context.user_id != query.user_id:
                continue
            if query.session_id and context.session_id != query.session_id:
                continue
            
            results.append(context)
        
        # Sort by last accessed (most recent first)
        results.sort(key=lambda c: c.last_accessed, reverse=True)
        
        if query.limit:
            results = results[:query.limit]
        
        return results

    def delete_context(self, context_id: str) -> bool:
        """Delete a conversation context."""
        if context_id in self.contexts:
            del self.contexts[context_id]
            
            # Remove from storage
            storage_file = self.storage_path / f"{context_id}.json"
            if storage_file.exists():
                storage_file.unlink()
            
            logger.info(f"Deleted context: {context_id}")
            return True
        return False

    def cleanup_expired_entries(self) -> int:
        """Remove expired entries from all contexts and return count of removed entries."""
        total_removed = 0
        
        for context in list(self.contexts.values()):
            original_count = len(context.entries)
            context.entries = [entry for entry in context.entries if not entry.is_expired()]
            removed = original_count - len(context.entries)
            total_removed += removed
            
            if removed > 0:
                self._save_context(context)
        
        logger.info(f"Cleaned up {total_removed} expired entries")
        return total_removed

    def get_context_stats(self) -> Dict[str, Any]:
        """Get comprehensive context statistics."""
        total_contexts = len(self.contexts)
        total_entries = sum(len(ctx.entries) for ctx in self.contexts.values())
        total_size = sum(sum(e.size_bytes for e in ctx.entries) for ctx in self.contexts.values())
        
        return {
            "total_contexts": total_contexts,
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "average_entries_per_context": total_entries / total_contexts if total_contexts > 0 else 0,
            "storage_path": str(self.storage_path)
        }

    def _save_context(self, context: ConversationContext) -> None:
        """Save context to persistent storage."""
        try:
            storage_file = self.storage_path / f"{context.context_id}.json"
            
            # Convert to serializable format
            data = {
                "context_id": context.context_id,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "metadata": context.metadata,
                "created_at": context.created_at.isoformat(),
                "last_accessed": context.last_accessed.isoformat(),
                "max_entries": context.max_entries,
                "max_size_bytes": context.max_size_bytes,
                "entries": [
                    {
                        "entry_id": entry.entry_id,
                        "content": entry.content,
                        "content_type": entry.content_type,
                        "metadata": entry.metadata,
                        "timestamp": entry.timestamp.isoformat(),
                        "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                        "tags": list(entry.tags),
                        "size_bytes": entry.size_bytes
                    }
                    for entry in context.entries
                ]
            }
            
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save context {context.context_id}: {e}")

    def _load_contexts(self) -> None:
        """Load contexts from persistent storage."""
        if not self.storage_path.exists():
            return
        
        loaded_count = 0
        
        for storage_file in self.storage_path.glob("*.json"):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Reconstruct context
                context = ConversationContext(
                    context_id=data["context_id"],
                    user_id=data.get("user_id"),
                    session_id=data.get("session_id"),
                    metadata=data.get("metadata", {}),
                    max_entries=data.get("max_entries", 1000),
                    max_size_bytes=data.get("max_size_bytes", 10 * 1024 * 1024)
                )
                
                context.created_at = datetime.fromisoformat(data["created_at"])
                context.last_accessed = datetime.fromisoformat(data["last_accessed"])
                
                # Reconstruct entries
                for entry_data in data.get("entries", []):
                    entry = ContextEntry(
                        entry_id=entry_data["entry_id"],
                        content=entry_data["content"],
                        content_type=entry_data["content_type"],
                        metadata=entry_data.get("metadata", {}),
                        timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                        expires_at=datetime.fromisoformat(entry_data["expires_at"]) if entry_data.get("expires_at") else None,
                        tags=set(entry_data.get("tags", [])),
                        size_bytes=entry_data.get("size_bytes", 0)
                    )
                    context.entries.append(entry)
                
                self.contexts[context.context_id] = context
                loaded_count += 1
                
            except Exception as e:
                logger.error(f"Failed to load context from {storage_file}: {e}")
        
        logger.info(f"Loaded {loaded_count} contexts from storage")


# Global context manager instance
_context_manager = ContextManager()


def get_context_manager() -> ContextManager:
    """Get the global context manager instance."""
    return _context_manager


def create_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new conversation context using the global manager."""
    return _context_manager.create_context(user_id, session_id, metadata)


def add_context_entry(
    context_id: str,
    content: str,
    content_type: str = "text",
    tags: Optional[Set[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Add an entry to a conversation context using the global manager."""
    return _context_manager.add_context_entry(context_id, content, content_type, tags, metadata)


def get_context_entries(
    context_id: str,
    limit: Optional[int] = None,
    tags: Optional[Set[str]] = None
) -> List[ContextEntry]:
    """Get entries from a conversation context using the global manager."""
    return _context_manager.get_context_entries(context_id, limit, tags)


__all__ = [
    "ContextEntry",
    "ConversationContext",
    "ContextQuery",
    "ContextManager",
    "get_context_manager",
    "create_context",
    "add_context_entry",
    "get_context_entries"
]
