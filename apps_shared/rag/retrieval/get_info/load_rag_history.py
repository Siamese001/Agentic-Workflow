"""RAG History Loader - Loads and manages RAG operation history.

This module provides functionality to load, store, and retrieve
RAG operation history for analysis and optimization.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
import json
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class HistoryType(Enum):
    """Types of RAG history data."""
    QUERY_HISTORY = "query_history"
    RETRIEVAL_HISTORY = "retrieval_history"
    GENERATION_HISTORY = "generation_history"
    FEEDBACK_HISTORY = "feedback_history"
    PERFORMANCE_HISTORY = "performance_history"


class HistoryFilter(Enum):
    """Filters for history queries."""
    TIME_RANGE = "time_range"
    USER_ID = "user_id"
    SESSION_ID = "session_id"
    QUERY_TYPE = "query_type"
    PERFORMANCE_THRESHOLD = "performance_threshold"


@dataclass
class HistoryEntry:
    """Single entry in RAG history."""
    id: str
    timestamp: datetime
    history_type: HistoryType
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class HistoryQuery:
    """Query for RAG history."""
    history_type: Optional[HistoryType] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 100
    offset: int = 0
    sort_by: str = "timestamp"
    sort_order: str = "desc"


@dataclass
class HistoryResult:
    """Result of history query."""
    entries: List[HistoryEntry]
    total_count: int
    query: HistoryQuery
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGHistoryConfig:
    """Configuration for RAG history operations."""
    storage_backend: str = "file"  # file, database, memory
    storage_path: str = "data/rag_history"
    max_entries_per_query: int = 1000
    retention_days: int = 30
    enable_compression: bool = True
    cache_enabled: bool = True
    cache_size: int = 1000
    log_level: str = "INFO"


class RAGHistoryLoader:
    """Main class for loading and managing RAG history."""

    def __init__(self, config: Optional[RAGHistoryConfig] = None):
        self.config = config or RAGHistoryConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._cache = {}
        self._storage = None

    def load_history(self, query: HistoryQuery) -> HistoryResult:
        """Load RAG history based on query.
        
        Args:
            query: History query with filters and parameters
            
        Returns:
            HistoryResult: Matching history entries
        """
        self.logger.info(f"Loading RAG history: {query.history_type}")
        
        try:
            # Validate query
            self._validate_query(query)
            
            # Check cache first
            cache_key = self._get_cache_key(query)
            if self.config.cache_enabled and cache_key in self._cache:
                self.logger.debug("Returning cached history result")
                return self._cache[cache_key]
            
            # Load from storage
            entries = self._load_from_storage(query)
            
            # Apply filters
            filtered_entries = self._apply_filters(entries, query.filters)
            
            # Sort results
            sorted_entries = self._sort_entries(filtered_entries, query.sort_by, query.sort_order)
            
            # Apply pagination
            total_count = len(sorted_entries)
            paginated_entries = sorted_entries[query.offset:query.offset + query.limit]
            
            result = HistoryResult(
                entries=paginated_entries,
                total_count=total_count,
                query=query,
                metadata={
                    "loaded_at": datetime.utcnow().isoformat(),
                    "loader": "RAGHistoryLoader"
                }
            )
            
            # Cache result
            if self.config.cache_enabled:
                self._cache[cache_key] = result
                self._manage_cache_size()
            
            self.logger.info(f"Loaded {len(paginated_entries)} history entries")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to load RAG history: {str(e)}")
            return HistoryResult(
                entries=[],
                total_count=0,
                query=query,
                metadata={"error": str(e)}
            )

    def save_entry(self, entry: HistoryEntry) -> bool:
        """Save a history entry.
        
        Args:
            entry: History entry to save
            
        Returns:
            bool: True if saved successfully
        """
        try:
            self.logger.info(f"Saving history entry: {entry.id}")
            
            # Validate entry
            self._validate_entry(entry)
            
            # Save to storage
            success = self._save_to_storage(entry)
            
            if success:
                # Clear cache
                self._cache.clear()
                self.logger.info(f"Successfully saved entry: {entry.id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to save history entry: {str(e)}")
            return False

    def get_statistics(self, history_type: Optional[HistoryType] = None) -> Dict[str, Any]:
        """Get statistics about RAG history.
        
        Args:
            history_type: Optional type filter
            
        Returns:
            Dict: Statistics summary
        """
        try:
            # Query all entries
            query = HistoryQuery(history_type=history_type, limit=self.config.max_entries_per_query)
            result = self.load_history(query)
            
            # Calculate statistics
            stats = {
                "total_entries": result.total_count,
                "entries_by_type": {},
                "entries_by_date": {},
                "unique_users": set(),
                "unique_sessions": set(),
                "average_performance": 0,
                "oldest_entry": None,
                "newest_entry": None
            }
            
            performance_scores = []
            
            for entry in result.entries:
                # Count by type
                entry_type = entry.history_type.value
                stats["entries_by_type"][entry_type] = stats["entries_by_type"].get(entry_type, 0) + 1
                
                # Count by date
                date_str = entry.timestamp.strftime("%Y-%m-%d")
                stats["entries_by_date"][date_str] = stats["entries_by_date"].get(date_str, 0) + 1
                
                # Track unique users and sessions
                if entry.user_id:
                    stats["unique_users"].add(entry.user_id)
                if entry.session_id:
                    stats["unique_sessions"].add(entry.session_id)
                
                # Track performance
                if "performance_score" in entry.data:
                    performance_scores.append(entry.data["performance_score"])
                
                # Track oldest/newest
                if not stats["oldest_entry"] or entry.timestamp < stats["oldest_entry"]:
                    stats["oldest_entry"] = entry.timestamp
                if not stats["newest_entry"] or entry.timestamp > stats["newest_entry"]:
                    stats["newest_entry"] = entry.timestamp
            
            # Convert sets to counts
            stats["unique_users"] = len(stats["unique_users"])
            stats["unique_sessions"] = len(stats["unique_sessions"])
            
            # Calculate average performance
            if performance_scores:
                stats["average_performance"] = sum(performance_scores) / len(performance_scores)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {str(e)}")
            return {"error": str(e)}

    def cleanup_old_entries(self, days: Optional[int] = None) -> int:
        """Clean up old history entries.
        
        Args:
            days: Number of days to retain (overrides config)
            
        Returns:
            int: Number of entries removed
        """
        retention_days = days or self.config.retention_days
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        self.logger.info(f"Cleaning up entries older than {cutoff_date}")
        
        try:
            # Query old entries
            query = HistoryQuery(
                filters={"end_date": cutoff_date.isoformat()},
                limit=self.config.max_entries_per_query
            )
            result = self.load_history(query)
            
            # Delete old entries
            deleted_count = 0
            for entry in result.entries:
                if self._delete_entry(entry.id):
                    deleted_count += 1
            
            # Clear cache
            self._cache.clear()
            
            self.logger.info(f"Cleaned up {deleted_count} old entries")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old entries: {str(e)}")
            return 0

    def _validate_query(self, query: HistoryQuery) -> None:
        """Validate history query."""
        if query.limit > self.config.max_entries_per_query:
            raise ValueError(
                f"Limit ({query.limit}) exceeds maximum ({self.config.max_entries_per_query})"
            )
        
        if query.limit <= 0:
            raise ValueError("Limit must be positive")
        
        if query.offset < 0:
            raise ValueError("Offset cannot be negative")

    def _validate_entry(self, entry: HistoryEntry) -> None:
        """Validate history entry."""
        if not entry.id:
            raise ValueError("Entry ID cannot be empty")
        
        if not entry.history_type:
            raise ValueError("History type is required")

    def _get_cache_key(self, query: HistoryQuery) -> str:
        """Generate cache key for query."""
        return f"{query.history_type}_{hash(str(query.filters))}_{query.limit}_{query.offset}"

    def _load_from_storage(self, query: HistoryQuery) -> List[HistoryEntry]:
        """Load entries from storage."""
        # Simulate loading from storage
        entries = []
        
        # Mock data generation
        for i in range(min(query.limit * 2, 100)):
            entry = HistoryEntry(
                id=f"entry_{i}",
                timestamp=datetime.utcnow() - timedelta(hours=i),
                history_type=query.history_type or HistoryType.QUERY_HISTORY,
                data={"query": f"Sample query {i}", "results": 5},
                metadata={"source": "mock_storage"},
                user_id=f"user_{i % 10}",
                session_id=f"session_{i % 5}"
            )
            entries.append(entry)
        
        return entries

    def _apply_filters(self, entries: List[HistoryEntry], filters: Dict[str, Any]) -> List[HistoryEntry]:
        """Apply filters to entries."""
        filtered = entries
        
        # Time range filter
        if "start_date" in filters or "end_date" in filters:
            start_date = datetime.fromisoformat(filters["start_date"]) if "start_date" in filters else None
            end_date = datetime.fromisoformat(filters["end_date"]) if "end_date" in filters else None
            
            filtered = [
                e for e in filtered
                if (not start_date or e.timestamp >= start_date) and
                   (not end_date or e.timestamp <= end_date)
            ]
        
        # User filter
        if "user_id" in filters:
            user_ids = filters["user_id"] if isinstance(filters["user_id"], list) else [filters["user_id"]]
            filtered = [e for e in filtered if e.user_id in user_ids]
        
        # Session filter
        if "session_id" in filters:
            session_ids = filters["session_id"] if isinstance(filters["session_id"], list) else [filters["session_id"]]
            filtered = [e for e in filtered if e.session_id in session_ids]
        
        return filtered

    def _sort_entries(self, entries: List[HistoryEntry], sort_by: str, sort_order: str) -> List[HistoryEntry]:
        """Sort entries by specified field."""
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "timestamp":
            entries.sort(key=lambda x: x.timestamp, reverse=reverse)
        elif sort_by == "id":
            entries.sort(key=lambda x: x.id, reverse=reverse)
        elif sort_by == "user_id":
            entries.sort(key=lambda x: x.user_id or "", reverse=reverse)
        
        return entries

    def _save_to_storage(self, entry: HistoryEntry) -> bool:
        """Save entry to storage."""
        # Simulate saving to storage
        return True

    def _delete_entry(self, entry_id: str) -> bool:
        """Delete entry from storage."""
        # Simulate deletion
        return True

    def _manage_cache_size(self) -> None:
        """Manage cache size to prevent memory issues."""
        if len(self._cache) > self.config.cache_size:
            # Remove oldest entries
            items = list(self._cache.items())
            self._cache = dict(items[-self.config.cache_size:])


# Factory function for easy instantiation
def create_rag_history_loader(
    storage_backend: str = "file",
    storage_path: str = "data/rag_history",
    retention_days: int = 30,
    **kwargs
) -> RAGHistoryLoader:
    """Create a configured RAG history loader."""
    config = RAGHistoryConfig(
        storage_backend=storage_backend,
        storage_path=storage_path,
        retention_days=retention_days,
        **kwargs
    )
    return RAGHistoryLoader(config)


# Convenience function for direct usage
def load_rag_history(
    history_type: str = "query_history",
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Load RAG history with simple parameters.
    
    Args:
        history_type: Type of history to load
        limit: Maximum number of entries
        filters: Optional filters to apply
        config: Optional loader configuration overrides
        
    Returns:
        Dict: History entries with metadata
    """
    # Build query
    query = HistoryQuery(
        history_type=HistoryType(history_type),
        filters=filters or {},
        limit=limit
    )
    
    # Create loader and execute
    loader_config = RAGHistoryConfig(**config) if config else None
    loader = RAGHistoryLoader(loader_config)
    result = loader.load_history(query)
    
    # Convert result to dict for JSON serialization
    return {
        "entries": [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "history_type": e.history_type.value,
                "data": e.data,
                "metadata": e.metadata,
                "user_id": e.user_id,
                "session_id": e.session_id
            }
            for e in result.entries
        ],
        "total_count": result.total_count,
        "query": {
            "history_type": result.query.history_type.value if result.query.history_type else None,
            "limit": result.query.limit,
            "offset": result.query.offset
        },
        "metadata": result.metadata
    }
