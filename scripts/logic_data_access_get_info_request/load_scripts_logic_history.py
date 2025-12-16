"""Scripts Logic History Loader - Loads and manages scripts logic operation history.

This module provides history loading and management capabilities for scripts logic operations,
including operation tracking, state persistence, and historical analysis.
Follows the functional component pattern with proper logging.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

LOGGER = logging.getLogger(__name__)


class HistoryFilter(Enum):
    """Filters for history queries."""
    ALL = "all"
    SUCCESS = "success"
    FAILURE = "failure"
    BY_OPERATION = "by_operation"
    BY_DATE = "by_date"
    BY_USER = "by_user"


class HistorySort(Enum):
    """Sorting options for history."""
    TIMESTAMP_ASC = "timestamp_asc"
    TIMESTAMP_DESC = "timestamp_desc"
    OPERATION_ASC = "operation_asc"
    OPERATION_DESC = "operation_desc"


@dataclass
class HistoryEntry:
    """Individual history entry."""
    id: str
    operation: str
    status: str
    timestamp: datetime
    duration_ms: float
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HistoryQuery:
    """Query configuration for history retrieval."""
    filter_type: HistoryFilter = HistoryFilter.ALL
    filter_value: Optional[str] = None
    sort_by: HistorySort = HistorySort.TIMESTAMP_DESC
    limit: int = 100
    offset: int = 0
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@dataclass
class HistoryResult:
    """Result of history query."""
    entries: List[HistoryEntry] = field(default_factory=list)
    total_count: int = 0
    query: HistoryQuery = field(default_factory=HistoryQuery)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HistoryConfig:
    """Configuration for history management."""
    storage_path: str = "data/scripts_logic_history.json"
    max_entries: int = 10000
    retention_days: int = 30
    auto_cleanup: bool = True
    compression: bool = False


class ScriptsLogicHistoryLoader:
    """Main class for loading and managing scripts logic history."""

    def __init__(self, config: Optional[HistoryConfig] = None):
        self.config = config or HistoryConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._history_cache = []
        self._load_history()

    def load_history(self, query: HistoryQuery) -> HistoryResult:
        """Load history based on query parameters.

        Args:
            query: History query configuration

        Returns:
            HistoryResult: Query results with entries and metadata
        """
        self.logger.info(
            f"Loading history with filter: {query.filter_type.value}")

        try:
            # Apply filters
            filtered_entries = self._apply_filters(query)

            # Apply sorting
            sorted_entries = self._apply_sorting(
                filtered_entries, query.sort_by)

            # Apply pagination
            total_count = len(sorted_entries)
            paginated_entries = sorted_entries[query.offset:query.offset + query.limit]

            result = HistoryResult(
                entries=paginated_entries,
                total_count=total_count,
                query=query,
                metadata={
                    "loaded_at": datetime.utcnow().isoformat(),
                    "storage_path": self.config.storage_path,
                    "loader": "ScriptsLogicHistoryLoader"
                }
            )

            self.logger.info(
                f"History loaded: {len(paginated_entries)} entries (total: {total_count})"
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to load history: {str(e)}")
            return HistoryResult(
                entries=[],
                total_count=0,
                query=query,
                metadata={"error": str(e)}
            )

    def add_entry(self, entry: HistoryEntry) -> bool:
        """Add a new history entry.

        Args:
            entry: History entry to add

        Returns:
            bool: True if entry was added successfully
        """
        try:
            # Add to cache
            self._history_cache.append(entry)

            # Persist to storage
            self._save_history()

            # Cleanup if needed
            if self.config.auto_cleanup:
                self._cleanup_old_entries()

            self.logger.debug(f"Added history entry: {entry.id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add history entry: {str(e)}")
            return False

    def get_entry(self, entry_id: str) -> Optional[HistoryEntry]:
        """Get a specific history entry by ID.

        Args:
            entry_id: ID of entry to retrieve

        Returns:
            HistoryEntry: Entry if found, None otherwise
        """
        for entry in self._history_cache:
            if entry.id == entry_id:
                return entry
        return None

    def delete_entry(self, entry_id: str) -> bool:
        """# SQL removed: Delete a history entry.

        Args:
            entry_id: ID of entry to delete

        Returns:
            bool: True if entry was deleted
        """
        original_length = len(self._history_cache)
        self._history_cache = [
            e for e in self._history_cache if e.id != entry_id]

        if len(self._history_cache) < original_length:
            self._save_history()
            self.logger.debug("Deleted history entry.")
            return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics.

        Returns:
            Dict: Statistics about the history
        """
        if not self._history_cache:
            return {"total_entries": 0}

        # Calculate statistics
        total_entries=len(self._history_cache)
        successful_entries=len(
            [e for e in self._history_cache if e.status == "success"])
        failed_entries=len(
            [e for e in self._history_cache if e.status == "failure"])

        # Operation counts
        operation_counts={}
        for entry in self._history_cache:
            operation_counts[entry.operation]=operation_counts.get(
                entry.operation, 0) + 1

        # Time range
        timestamps=[e.timestamp for e in self._history_cache]
        oldest_entry=min(timestamps)
        newest_entry=max(timestamps)

        # Average duration
        durations=[
            e.duration_ms for e in self._history_cache if e.duration_ms > 0]
        avg_duration=sum(durations) / len(durations) if durations else 0

        return {
            "total_entries": total_entries,
            "successful_entries": successful_entries,
            "failed_entries": failed_entries,
            "success_rate": successful_entries / total_entries if total_entries > 0 else 0,
            "operation_counts": operation_counts,
            "oldest_entry": oldest_entry.isoformat(),
            "newest_entry": newest_entry.isoformat(),
            "average_duration_ms": avg_duration,
            "retention_days": self.config.retention_days,
            "max_entries": self.config.max_entries
        }

    def clear_history(self, older_than_days: Optional[int]=None) -> int:
        """Clear history entries.

        Args:
            older_than_days: Only clear entries older than this many days

        Returns:
            int: Number of entries cleared
        """
        if older_than_days is None:
            # Clear all entries
            count=len(self._history_cache)
            self._history_cache.clear()
        else:
            # Clear old entries
            cutoff_date=datetime.utcnow() - timedelta(days=older_than_days)
            original_count=len(self._history_cache)
            self._history_cache=[
                e for e in self._history_cache if e.timestamp >= cutoff_date]
            count=original_count - len(self._history_cache)

        self._save_history()
        self.logger.info(f"Cleared {count} history entries")
        return count

    def _load_history(self) -> None:
        """Load history from storage."""
        try:
            storage_file=Path(self.config.storage_path)

            if storage_file.exists():
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data=json.load(f)

                # Convert JSON data to HistoryEntry objects
                self._history_cache=[]
                for entry_data in data.get("entries", []):
                    entry=HistoryEntry(
                        id=entry_data["id"],
                        operation=entry_data["operation"],
                        status=entry_data["status"],
                        timestamp=datetime.fromisoformat(
                            entry_data["timestamp"]),
                        duration_ms=entry_data["duration_ms"],
                        input_data=entry_data.get("input_data", {}),
                        output_data=entry_data.get("output_data", {}),
                        error_message=entry_data.get("error_message"),
                        user_id=entry_data.get("user_id"),
                        metadata=entry_data.get("metadata", {})
                    )
                    self._history_cache.append(entry)

                self.logger.info(
                    f"Loaded {len(self._history_cache)} history entries")
            else:
                self._history_cache=[]
                self.logger.info(
                    "No existing history file found, starting fresh")

        except Exception as e:
            self.logger.error(f"Failed to load history: {str(e)}")
            self._history_cache=[]

    def _save_history(self) -> None:
        """Save history to storage."""
        try:
            storage_file=Path(self.config.storage_path)
            storage_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert to JSON-serializable format
            data={
                "entries": [
                    {
                        "id": entry.id,
                        "operation": entry.operation,
                        "status": entry.status,
                        "timestamp": entry.timestamp.isoformat(),
                        "duration_ms": entry.duration_ms,
                        "input_data": entry.input_data,
                        "output_data": entry.output_data,
                        "error_message": entry.error_message,
                        "user_id": entry.user_id,
                        "metadata": entry.metadata
                    }
                    for entry in self._history_cache
                ],
                "saved_at": datetime.utcnow().isoformat()
            }

            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.debug(
                f"Saved {len(self._history_cache)} history entries")

        except Exception as e:
            self.logger.error(f"Failed to save history: {str(e)}")

    def _apply_filters(self, query: HistoryQuery) -> List[HistoryEntry]:
        """Apply filters to history entries."""
        filtered=self._history_cache.copy()

        # Apply date range filter
        if query.date_from:
            filtered=[e for e in filtered if e.timestamp >= query.date_from]

        if query.date_to:
            filtered=[e for e in filtered if e.timestamp <= query.date_to]

        # Apply specific filters
        if query.filter_type == HistoryFilter.SUCCESS:
            filtered=[e for e in filtered if e.status == "success"]
        elif query.filter_type == HistoryFilter.FAILURE:
            filtered=[e for e in filtered if e.status == "failure"]
        elif query.filter_type == HistoryFilter.BY_OPERATION and query.filter_value:
            filtered=[e for e in filtered if e.operation == query.filter_value]
        elif query.filter_type == HistoryFilter.BY_USER and query.filter_value:
            filtered=[e for e in filtered if e.user_id == query.filter_value]

        return filtered

    def _apply_sorting(self,
        entries: List[HistoryEntry],
        sort_by: HistorySort) -> List[HistoryEntry]:
        """Apply sorting to history entries."""
        if sort_by == HistorySort.TIMESTAMP_ASC:
            return sorted(entries, key=lambda x: x.timestamp)
        elif sort_by == HistorySort.TIMESTAMP_DESC:
            return sorted(entries, key=lambda x: x.timestamp, reverse=True)
        elif sort_by == HistorySort.OPERATION_ASC:
            return sorted(entries, key=lambda x: x.operation)
        elif sort_by == HistorySort.OPERATION_DESC:
            return sorted(entries, key=lambda x: x.operation, reverse=True)
        else:
            return entries

    def _cleanup_old_entries(self) -> None:
        """Clean up old entries based on retention policy."""
        if not self.config.retention_days:
            return

        cutoff_date=datetime.utcnow() - timedelta(days=self.config.retention_days)
        original_count=len(self._history_cache)

        # Remove old entries
        self._history_cache=[
            e for e in self._history_cache if e.timestamp >= cutoff_date]

        # Limit total entries
        if len(self._history_cache) > self.config.max_entries:
            # Keep newest entries
            self._history_cache.sort(key=lambda x: x.timestamp, reverse=True)
            self._history_cache=self._history_cache[:self.config.max_entries]

        cleaned_count=original_count - len(self._history_cache)
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old history entries")

# Factory function for easy instantiation
def create_scripts_logic_history_loader(
    storage_path: str="data/scripts_logic_history.json",
    max_entries: int=10000,
    retention_days: int=30,
    **kwargs: Dict[str, object]) -> ScriptsLogicHistoryLoader:
    """Create a configured scripts logic history loader."""
    config=HistoryConfig(
        storage_path=storage_path,
        max_entries=max_entries,
        retention_days=retention_days,
        **kwargs
    )
    return ScriptsLogicHistoryLoader(config)

# Convenience function for direct usage
def load_scripts_logic_history(
    filter_type: str="all",
    filter_value: Optional[str]=None,
    sort_by: str="timestamp_desc",
    limit: int=100,
    offset: int=0,
    config: Optional[Dict[str, Any]]=None
) -> Dict[str, Any]:
    """Load scripts logic history.

    Args:
        filter_type: Type of filter to apply
        filter_value: Value for the filter
        sort_by: How to sort the results
        limit: Maximum number of entries to return
        offset: Number of entries to skip
        config: Optional loader configuration

    Returns:
        Dict: History results
    """
    # Create loader and load history
    loader_config=HistoryConfig(**config or {})
    loader=ScriptsLogicHistoryLoader(loader_config)

    query=HistoryQuery(
        filter_type=HistoryFilter(filter_type),
        filter_value=filter_value,
        sort_by=HistorySort(sort_by),
        limit=limit,
        offset=offset
    )

    result=loader.load_history(query)

    # Convert result to dict for JSON serialization
    return {
        "entries": [
            {
                "id": e.id,
                "operation": e.operation,
                "status": e.status,
                "timestamp": e.timestamp.isoformat(),
                "duration_ms": e.duration_ms,
                "input_data": e.input_data,
                "output_data": e.output_data,
                "error_message": e.error_message,
                "user_id": e.user_id,
                "metadata": e.metadata
            }
            for e in result.entries
        ],
        "total_count": result.total_count,
        "query": {
            "filter_type": result.query.filter_type.value,
            "filter_value": result.query.filter_value,
            "sort_by": result.query.sort_by.value,
            "limit": result.query.limit,
            "offset": result.query.offset
        },
        "metadata": result.metadata
    }