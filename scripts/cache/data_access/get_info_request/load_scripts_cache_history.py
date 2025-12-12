"""Scripts Cache History Loader - Loads and manages scripts cache history.

This module provides cache history loading and management capabilities for scripts operations,
including cache tracking, state persistence, and performance analysis.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheOperation(Enum):
    """Types of cache operations."""
    READ = "read"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    CLEAR = "clear"
    EVICT = "evict"


class CacheStatus(Enum):
    """Status of cache operations."""
    HIT = "hit"
    MISS = "miss"
    ERROR = "error"
    EXPIRED = "expired"


@dataclass
class CacheHistoryEntry:
    """Individual cache history entry."""
    id: str
    operation: CacheOperation
    status: CacheStatus
    key: str
    timestamp: datetime
    size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    access_time_ms: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheHistoryQuery:
    """Query configuration for cache history."""
    operations: List[CacheOperation] = field(default_factory=list)
    status: Optional[CacheStatus] = None
    key_pattern: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


@dataclass
class CacheHistoryResult:
    """Result of cache history query."""
    entries: List[CacheHistoryEntry] = field(default_factory=list)
    total_count: int = 0
    query: CacheHistoryQuery = field(default_factory=CacheHistoryQuery)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheStatistics:
    """Cache performance statistics."""
    total_operations: int = 0
    hits: int = 0
    misses: int = 0
    errors: int = 0
    hit_rate: float = 0.0
    average_access_time_ms: float = 0.0
    total_size_bytes: int = 0
    operation_counts: Dict[str, int] = field(default_factory=dict)
    key_access_counts: Dict[str, int] = field(default_factory=dict)


@dataclass
class CacheHistoryConfig:
    """Configuration for cache history management."""
    storage_path: str = "data/scripts_cache_history.json"
    max_entries: int = 50000
    retention_days: int = 7
    auto_cleanup: bool = True
    compression: bool = False
    enable_statistics: bool = True


class ScriptsCacheHistoryLoader:
    """Main class for loading and managing scripts cache history."""

    def __init__(self, config: Optional[CacheHistoryConfig] = None):
        self.config = config or CacheHistoryConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._history_cache = []
        self._statistics = CacheStatistics()
        self._load_history()

    def load_history(self, query: CacheHistoryQuery) -> CacheHistoryResult:
        """Load cache history based on query parameters.
        
        Args:
            query: Cache history query configuration
            
        Returns:
            CacheHistoryResult: Query results with entries and metadata
        """
        self.logger.info(f"Loading cache history with filters: operations={len(query.operations)}, status={query.status}")
        
        try:
            # Apply filters
            filtered_entries = self._apply_filters(query)
            
            # Sort by timestamp (descending)
            filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply pagination
            total_count = len(filtered_entries)
            paginated_entries = filtered_entries[query.offset:query.offset + query.limit]
            
            result = CacheHistoryResult(
                entries=paginated_entries,
                total_count=total_count,
                query=query,
                metadata={
                    "loaded_at": datetime.utcnow().isoformat(),
                    "storage_path": self.config.storage_path,
                    "loader": "ScriptsCacheHistoryLoader"
                }
            )
            
            self.logger.info(
                f"Cache history loaded: {len(paginated_entries)} entries (total: {total_count})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to load cache history: {str(e)}")
            return CacheHistoryResult(
                entries=[],
                total_count=0,
                query=query,
                metadata={"error": str(e)}
            )

    def add_entry(self, entry: CacheHistoryEntry) -> bool:
        """Add a new cache history entry.
        
        Args:
            entry: Cache history entry to add
            
        Returns:
            bool: True if entry was added successfully
        """
        try:
            # Add to cache
            self._history_cache.append(entry)
            
            # Update statistics
            self._update_statistics(entry)
            
            # Persist to storage
            self._save_history()
            
            # Cleanup if needed
            if self.config.auto_cleanup:
                self._cleanup_old_entries()
            
            self.logger.debug(f"Added cache history entry: {entry.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add cache history entry: {str(e)}")
            return False

    def get_statistics(self) -> CacheStatistics:
        """Get cache performance statistics.
        
        Returns:
            CacheStatistics: Current cache statistics
        """
        # Recalculate statistics if needed
        if not self._statistics.total_operations or len(self._history_cache) != self._statistics.total_operations:
            self._calculate_statistics()
        
        return self._statistics

    def get_key_history(self, key: str, limit: int = 50) -> List[CacheHistoryEntry]:
        """Get history for a specific cache key.
        
        Args:
            key: Cache key to lookup
            limit: Maximum number of entries to return
            
        Returns:
            List[CacheHistoryEntry]: History for the key
        """
        key_entries = [e for e in self._history_cache if e.key == key]
        key_entries.sort(key=lambda x: x.timestamp, reverse=True)
        return key_entries[:limit]

    def get_hot_keys(self, top_k: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently accessed cache keys.
        
        Args:
            top_k: Number of top keys to return
            
        Returns:
            List of (key, access_count) tuples
        """
        key_counts = {}
        for entry in self._history_cache:
            if entry.operation in [CacheOperation.READ, CacheOperation.UPDATE]:
                key_counts[entry.key] = key_counts.get(entry.key, 0) + 1
        
        # Sort by access count
        hot_keys = sorted(key_counts.items(), key=lambda x: x[1], reverse=True)
        return hot_keys[:top_k]

    def clear_history(self, older_than_days: Optional[int] = None) -> int:
        """Clear cache history entries.
        
        Args:
            older_than_days: Only clear entries older than this many days
            
        Returns:
            int: Number of entries cleared
        """
        if older_than_days is None:
            # Clear all entries
            count = len(self._history_cache)
            self._history_cache.clear()
            self._statistics = CacheStatistics()
        else:
            # Clear old entries
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            original_count = len(self._history_cache)
            self._history_cache = [e for e in self._history_cache if e.timestamp >= cutoff_date]
            count = original_count - len(self._history_cache)
        
        self._save_history()
        self.logger.info(f"Cleared {count} cache history entries")
        return count

    def export_history(self, format_type: str = "json", file_path: Optional[str] = None) -> bool:
        """Export cache history to file.
        
        Args:
            format_type: Export format (json, csv)
            file_path: Optional file path
            
        Returns:
            bool: True if export was successful
        """
        try:
            if file_path is None:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                file_path = f"cache_history_export_{timestamp}.{format_type}"
            
            if format_type.lower() == "json":
                self._export_json(file_path)
            elif format_type.lower() == "csv":
                self._export_csv(file_path)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            
            self.logger.info(f"Cache history exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export cache history: {str(e)}")
            return False

    def _load_history(self) -> None:
        """Load history from storage."""
        try:
            storage_file = Path(self.config.storage_path)
            
            if storage_file.exists():
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert JSON data to CacheHistoryEntry objects
                self._history_cache = []
                for entry_data in data.get("entries", []):
                    entry = CacheHistoryEntry(
                        id=entry_data["id"],
                        operation=CacheOperation(entry_data["operation"]),
                        status=CacheStatus(entry_data["status"]),
                        key=entry_data["key"],
                        timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                        size_bytes=entry_data.get("size_bytes", 0),
                        ttl_seconds=entry_data.get("ttl_seconds"),
                        access_time_ms=entry_data.get("access_time_ms", 0.0),
                        error_message=entry_data.get("error_message"),
                        metadata=entry_data.get("metadata", {})
                    )
                    self._history_cache.append(entry)
                
                # Load statistics
                stats_data = data.get("statistics", {})
                self._statistics = CacheStatistics(
                    total_operations=stats_data.get("total_operations", 0),
                    hits=stats_data.get("hits", 0),
                    misses=stats_data.get("misses", 0),
                    errors=stats_data.get("errors", 0),
                    hit_rate=stats_data.get("hit_rate", 0.0),
                    average_access_time_ms=stats_data.get("average_access_time_ms", 0.0),
                    total_size_bytes=stats_data.get("total_size_bytes", 0),
                    operation_counts=stats_data.get("operation_counts", {}),
                    key_access_counts=stats_data.get("key_access_counts", {})
                )
                
                self.logger.info(f"Loaded {len(self._history_cache)} cache history entries")
            else:
                self._history_cache = []
                self._statistics = CacheStatistics()
                self.logger.info("No existing cache history file found, starting fresh")
                
        except Exception as e:
            self.logger.error(f"Failed to load cache history: {str(e)}")
            self._history_cache = []
            self._statistics = CacheStatistics()

    def _save_history(self) -> None:
        """Save history to storage."""
        try:
            storage_file = Path(self.config.storage_path)
            storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to JSON-serializable format
            data = {
                "entries": [
                    {
                        "id": entry.id,
                        "operation": entry.operation.value,
                        "status": entry.status.value,
                        "key": entry.key,
                        "timestamp": entry.timestamp.isoformat(),
                        "size_bytes": entry.size_bytes,
                        "ttl_seconds": entry.ttl_seconds,
                        "access_time_ms": entry.access_time_ms,
                        "error_message": entry.error_message,
                        "metadata": entry.metadata
                    }
                    for entry in self._history_cache
                ],
                "statistics": {
                    "total_operations": self._statistics.total_operations,
                    "hits": self._statistics.hits,
                    "misses": self._statistics.misses,
                    "errors": self._statistics.errors,
                    "hit_rate": self._statistics.hit_rate,
                    "average_access_time_ms": self._statistics.average_access_time_ms,
                    "total_size_bytes": self._statistics.total_size_bytes,
                    "operation_counts": self._statistics.operation_counts,
                    "key_access_counts": self._statistics.key_access_counts
                },
                "saved_at": datetime.utcnow().isoformat()
            }
            
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved {len(self._history_cache)} cache history entries")
            
        except Exception as e:
            self.logger.error(f"Failed to save cache history: {str(e)}")

    def _apply_filters(self, query: CacheHistoryQuery) -> List[CacheHistoryEntry]:
        """Apply filters to cache history entries."""
        filtered = self._history_cache.copy()
        
        # Filter by operations
        if query.operations:
            filtered = [e for e in filtered if e.operation in query.operations]
        
        # Filter by status
        if query.status:
            filtered = [e for e in filtered if e.status == query.status]
        
        # Filter by key pattern
        if query.key_pattern:
            import re
            pattern = re.compile(query.key_pattern, re.IGNORECASE)
            filtered = [e for e in filtered if pattern.search(e.key)]
        
        # Filter by date range
        if query.date_from:
            filtered = [e for e in filtered if e.timestamp >= query.date_from]
        
        if query.date_to:
            filtered = [e for e in filtered if e.timestamp <= query.date_to]
        
        return filtered

    def _update_statistics(self, entry: CacheHistoryEntry) -> None:
        """Update statistics with new entry."""
        if not self.config.enable_statistics:
            return
        
        self._statistics.total_operations += 1
        
        # Update status counts
        if entry.status == CacheStatus.HIT:
            self._statistics.hits += 1
        elif entry.status == CacheStatus.MISS:
            self._statistics.misses += 1
        elif entry.status == CacheStatus.ERROR:
            self._statistics.errors += 1
        
        # Update hit rate
        if self._statistics.total_operations > 0:
            self._statistics.hit_rate = self._statistics.hits / self._statistics.total_operations
        
        # Update operation counts
        op_name = entry.operation.value
        self._statistics.operation_counts[op_name] = self._statistics.operation_counts.get(op_name, 0) + 1
        
        # Update key access counts
        if entry.operation in [CacheOperation.READ, CacheOperation.UPDATE]:
            self._statistics.key_access_counts[entry.key] = self._statistics.key_access_counts.get(entry.key, 0) + 1
        
        # Update size
        self._statistics.total_size_bytes += entry.size_bytes
        
        # Update average access time
        if entry.access_time_ms > 0:
            total_time = self._statistics.average_access_time_ms * (self._statistics.total_operations - 1) + entry.access_time_ms
            self._statistics.average_access_time_ms = total_time / self._statistics.total_operations

    def _calculate_statistics(self) -> None:
        """Recalculate statistics from history."""
        self._statistics = CacheStatistics()
        
        for entry in self._history_cache:
            self._update_statistics(entry)

    def _cleanup_old_entries(self) -> None:
        """Clean up old entries based on retention policy."""
        if not self.config.retention_days:
            return
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
        original_count = len(self._history_cache)
        
        # Remove old entries
        self._history_cache = [e for e in self._history_cache if e.timestamp >= cutoff_date]
        
        # Limit total entries
        if len(self._history_cache) > self.config.max_entries:
            # Keep newest entries
            self._history_cache.sort(key=lambda x: x.timestamp, reverse=True)
            self._history_cache = self._history_cache[:self.config.max_entries]
        
        cleaned_count = original_count - len(self._history_cache)
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old cache history entries")
            self._calculate_statistics()

    def _export_json(self, file_path: str) -> None:
        """Export history as JSON."""
        data = {
            "entries": [
                {
                    "id": e.id,
                    "operation": e.operation.value,
                    "status": e.status.value,
                    "key": e.key,
                    "timestamp": e.timestamp.isoformat(),
                    "size_bytes": e.size_bytes,
                    "access_time_ms": e.access_time_ms
                }
                for e in self._history_cache
            ],
            "statistics": {
                "total_operations": self._statistics.total_operations,
                "hit_rate": self._statistics.hit_rate,
                "average_access_time_ms": self._statistics.average_access_time_ms
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_csv(self, file_path: str) -> None:
        """Export history as CSV."""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'operation', 'status', 'key', 'timestamp', 'size_bytes', 'access_time_ms'])
            
            for e in self._history_cache:
                writer.writerow([
                    e.id,
                    e.operation.value,
                    e.status.value,
                    e.key,
                    e.timestamp.isoformat(),
                    e.size_bytes,
                    e.access_time_ms
                ])


# Factory function for easy instantiation
def create_scripts_cache_history_loader(
    storage_path: str = "data/scripts_cache_history.json",
    max_entries: int = 50000,
    retention_days: int = 7,
    **kwargs: Dict[str, object]) -> ScriptsCacheHistoryLoader:
    """Create a configured scripts cache history loader."""
    config = CacheHistoryConfig(
        storage_path=storage_path,
        max_entries=max_entries,
        retention_days=retention_days,
        **kwargs
    )
    return ScriptsCacheHistoryLoader(config)


# Convenience function for direct usage
def load_scripts_cache_history(
    operations: List[str] = None,
    status: Optional[str] = None,
    key_pattern: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Load scripts cache history.
    
    Args:
        operations: List of operations to filter by
        status: Status to filter by
        key_pattern: Key pattern to filter by
        limit: Maximum number of entries to return
        offset: Number of entries to skip
        config: Optional loader configuration
        
    Returns:
        Dict: Cache history results
    """
    # Create loader and load history
    loader_config = CacheHistoryConfig(**config or {})
    loader = ScriptsCacheHistoryLoader(loader_config)
    
    query = CacheHistoryQuery(
        operations=[CacheOperation(op) for op in (operations or [])],
        status=CacheStatus(status) if status else None,
        key_pattern=key_pattern,
        limit=limit,
        offset=offset
    )
    
    result = loader.load_history(query)
    
    # Convert result to dict for JSON serialization
    return {
        "entries": [
            {
                "id": e.id,
                "operation": e.operation.value,
                "status": e.status.value,
                "key": e.key,
                "timestamp": e.timestamp.isoformat(),
                "size_bytes": e.size_bytes,
                "ttl_seconds": e.ttl_seconds,
                "access_time_ms": e.access_time_ms,
                "error_message": e.error_message,
                "metadata": e.metadata
            }
            for e in result.entries
        ],
        "total_count": result.total_count,
        "query": {
            "operations": [op.value for op in result.query.operations],
            "status": result.query.status.value if result.query.status else None,
            "key_pattern": result.query.key_pattern,
            "limit": result.query.limit,
            "offset": result.query.offset
        },
        "metadata": result.metadata
    }
