"""Schema History Fetcher - Fetches and manages schema history.

This module provides schema history fetching and management capabilities,
including version tracking, change history, and evolution analysis.
Follows the functional component pattern with proper logging.
"""

import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HistoryAction(Enum):
    """Types of history actions."""

    CREATED = "created"
    UPDATED = "updated"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    RESTORED = "restored"
    CLONED = "cloned"


@dataclass
class SchemaChangeRecord:
    """Record of a schema change."""

    id: str
    schema_id: str
    action: HistoryAction
    timestamp: datetime
    version_from: str | None
    version_to: str | None
    changed_by: str | None
    change_summary: str | None
    changes: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaHistoryQuery:
    """Query configuration for schema history."""

    schema_id: str | None = None
    actions: list[HistoryAction] = field(default_factory=list)
    changed_by: str | None = None
    version_from: str | None = None
    version_to: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    include_changes: bool = True
    limit: int = 100
    offset: int = 0


@dataclass
class SchemaHistoryResult:
    """Result of schema history query."""

    records: list[SchemaChangeRecord]
    total_count: int
    query: SchemaHistoryQuery
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaEvolutionSummary:
    """Summary of schema evolution."""

    schema_id: str
    total_versions: int
    first_version: str
    latest_version: str
    creation_date: datetime
    last_modified: datetime
    modification_count: int
    contributors: list[str]
    major_changes: list[str] = field(default_factory=list)


@dataclass
class SchemaHistoryConfig:
    """Configuration for schema history management."""

    storage_path: str = "data/schema_history"
    max_records_per_schema: int = 1000
    retention_days: int = 365
    enable_diff_tracking: bool = True
    backup_enabled: bool = True


class SchemaHistoryFetcher:
    """Main class for fetching schema history."""

    def __init__(self, config: SchemaHistoryConfig | None = None):
        self.config = config or SchemaHistoryConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._history_records: dict[str, list[SchemaChangeRecord]] = {}
        self._load_history()

    def fetch_history(self, query: SchemaHistoryQuery) -> SchemaHistoryResult:
        """Fetch schema history based on query.

        Args:
            query: History query configuration

        Returns:
            SchemaHistoryResult: Query results with change records
        """
        self.logger.info(f"Fetching schema history: schema_id={query.schema_id}")

        try:
            # Get relevant records
            all_records = []

            if query.schema_id:
                # Get history for specific schema
                if query.schema_id in self._history_records:
                    all_records = self._history_records[query.schema_id].copy()
            else:
                # Get all history
                for records in self._history_records.values():
                    all_records.extend(records)

            # Apply filters
            filtered_records = self._apply_filters(all_records, query)

            # Sort by timestamp (descending)
            filtered_records.sort(key=lambda x: x.timestamp, reverse=True)

            # Apply pagination
            total_count = len(filtered_records)
            paginated_records = filtered_records[query.offset : query.offset + query.limit]

            # Filter changes if not requested
            if not query.include_changes:
                for record in paginated_records:
                    record = record.__class__(
                        id=record.id,
                        schema_id=record.schema_id,
                        action=record.action,
                        timestamp=record.timestamp,
                        version_from=record.version_from,
                        version_to=record.version_to,
                        changed_by=record.changed_by,
                        change_summary=record.change_summary,
                        changes={},
                        metadata=record.metadata,
                    )

            result = SchemaHistoryResult(
                records=paginated_records,
                total_count=total_count,
                query=query,
                metadata={
                    "fetched_at": datetime.utcnow().isoformat(),
                    "storage_path": self.config.storage_path,
                    "total_schemas": len(self._history_records),
                    "fetcher": "SchemaHistoryFetcher",
                },
            )

            self.logger.info(
                f"Schema history fetched: {len(paginated_records)} records (total: {total_count})"
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to fetch schema history: {str(e)}")
            return SchemaHistoryResult(
                records=[], total_count=0, query=query, metadata={"error": str(e)}
            )

    def add_change_record(self, record: SchemaChangeRecord) -> bool:
        """Add a change record to history.

        Args:
            record: Change record to add

        Returns:
            bool: True if record was added successfully
        """
        try:
            # Initialize schema history if needed
            if record.schema_id not in self._history_records:
                self._history_records[record.schema_id] = []

            # Add record
            self._history_records[record.schema_id].append(record)

            # Limit records per schema
            if len(self._history_records[record.schema_id]) > self.config.max_records_per_schema:
                # Remove oldest records
                self._history_records[record.schema_id].sort(key=lambda x: x.timestamp)
                excess = (
                    len(self._history_records[record.schema_id])
                    - self.config.max_records_per_schema
                )
                self._history_records[record.schema_id] = self._history_records[record.schema_id][
                    excess:
                ]

            # Save to disk
            self._save_schema_history(record.schema_id)

            self.logger.debug(f"Added change record for schema: {record.schema_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add change record: {str(e)}")
            return False

    def get_evolution_summary(self, schema_id: str) -> SchemaEvolutionSummary | None:
        """Get evolution summary for a schema.

        Args:
            schema_id: ID of schema

        Returns:
            SchemaEvolutionSummary: Evolution summary if found
        """
        if schema_id not in self._history_records:
            return None

        records = self._history_records[schema_id]
        if not records:
            return None

        # Sort by timestamp
        records.sort(key=lambda x: x.timestamp)

        # Extract information
        contributors = list(set(r.changed_by for r in records if r.changed_by))

        # Find major changes
        major_changes = []
        for record in records:
            if record.action in [HistoryAction.CREATED, HistoryAction.UPDATED]:
                if record.change_summary:
                    major_changes.append(f"{record.action.value}: {record.change_summary}")

        # Find first and latest versions
        first_record = records[0]
        latest_record = records[-1]

        return SchemaEvolutionSummary(
            schema_id=schema_id,
            total_versions=len(set(r.version_to for r in records if r.version_to)),
            first_version=first_record.version_from or "1.0.0",
            latest_version=latest_record.version_to or "1.0.0",
            creation_date=first_record.timestamp,
            last_modified=latest_record.timestamp,
            modification_count=len([r for r in records if r.action == HistoryAction.UPDATED]),
            contributors=contributors,
            major_changes=major_changes[:10],  # Limit to 10 major changes
        )

    def get_version_timeline(self, schema_id: str) -> list[tuple[str, datetime, str]]:
        """Get timeline of versions for a schema.

        Args:
            schema_id: ID of schema

        Returns:
            List of (version, timestamp, action) tuples
        """
        if schema_id not in self._history_records:
            return []

        records = self._history_records[schema_id]
        timeline = []

        for record in records:
            if record.version_to:
                timeline.append((record.version_to, record.timestamp, record.action.value))

        # Sort by timestamp
        timeline.sort(key=lambda x: x[1])

        return timeline

    def get_contributor_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all contributors.

        Returns:
            Dict: Contributor statistics
        """
        stats = {}

        for schema_id, records in self._history_records.items():
            for record in records:
                if record.changed_by:
                    contributor = record.changed_by

                    if contributor not in stats:
                        stats[contributor] = {
                            "total_changes": 0,
                            "schemas_modified": set(),
                            "actions": {},
                        }

                    stats[contributor]["total_changes"] += 1
                    stats[contributor]["schemas_modified"].add(schema_id)

                    action = record.action.value
                    stats[contributor]["actions"][action] = (
                        stats[contributor]["actions"].get(action, 0) + 1
                    )

        # Convert sets to counts
        for contributor in stats:
            stats[contributor]["schemas_modified"] = len(stats[contributor]["schemas_modified"])

        return stats

    def cleanup_old_records(self) -> int:
        """Clean up old records based on retention policy.

        Returns:
            int: Number of records cleaned up
        """
        if not self.config.retention_days:
            return 0

        cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
        cleaned_count = 0

        for schema_id in list(self._history_records.keys()):
            records = self._history_records[schema_id]
            original_count = len(records)

            # Filter old records
            self._history_records[schema_id] = [r for r in records if r.timestamp >= cutoff_date]

            cleaned_count += original_count - len(self._history_records[schema_id])

            # Remove empty histories
            if not self._history_records[schema_id]:
                del self._history_records[schema_id]

        if cleaned_count > 0:
            self._save_all_histories()
            self.logger.info(f"Cleaned up {cleaned_count} old history records")

        return cleaned_count

    def _load_history(self) -> None:
        """Load history from storage."""
        try:
            storage_path = Path(self.config.storage_path)
            if not storage_path.exists():
                storage_path.mkdir(parents=True, exist_ok=True)
                return

            # Load each schema history file
            for history_file in storage_path.glob("*.json"):
                try:
                    schema_id = history_file.stem

                    with open(history_file, encoding="utf-8") as f:
                        data = json.load(f)

                    # Convert to change records
                    records = []
                    for record_data in data.get("records", []):
                        record = SchemaChangeRecord(
                            id=record_data["id"],
                            schema_id=record_data["schema_id"],
                            action=HistoryAction(record_data["action"]),
                            timestamp=datetime.fromisoformat(record_data["timestamp"]),
                            version_from=record_data.get("version_from"),
                            version_to=record_data.get("version_to"),
                            changed_by=record_data.get("changed_by"),
                            change_summary=record_data.get("change_summary"),
                            changes=record_data.get("changes", {}),
                            metadata=record_data.get("metadata", {}),
                        )
                        records.append(record)

                    self._history_records[schema_id] = records

                except Exception as e:
                    self.logger.error(f"Failed to load history from {history_file}: {str(e)}")

            total_records = sum(len(records) for records in self._history_records.values())
            self.logger.info(
                f"Loaded {total_records} history records for {len(self._history_records)} schemas"
            )

        except Exception as e:
            self.logger.error(f"Failed to load schema history: {str(e)}")

    def _apply_filters(
        self, records: list[SchemaChangeRecord], query: SchemaHistoryQuery
    ) -> list[SchemaChangeRecord]:
        """Apply filters to history records."""
        filtered = records.copy()

        # Filter by actions
        if query.actions:
            filtered = [r for r in filtered if r.action in query.actions]

        # Filter by contributor
        if query.changed_by:
            filtered = [r for r in filtered if r.changed_by == query.changed_by]

        # Filter by version range
        if query.version_from:
            filtered = [r for r in filtered if r.version_from == query.version_from]

        if query.version_to:
            filtered = [r for r in filtered if r.version_to == query.version_to]

        # Filter by date range
        if query.date_from:
            filtered = [r for r in filtered if r.timestamp >= query.date_from]

        if query.date_to:
            filtered = [r for r in filtered if r.timestamp <= query.date_to]

        return filtered

    def _save_schema_history(self, schema_id: str) -> None:
        """Save history for a specific schema."""
        try:
            storage_path = Path(self.config.storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)

            history_file = storage_path / f"{schema_id}.json"

            # Convert to JSON
            data = {
                "schema_id": schema_id,
                "records": [
                    {
                        "id": r.id,
                        "schema_id": r.schema_id,
                        "action": r.action.value,
                        "timestamp": r.timestamp.isoformat(),
                        "version_from": r.version_from,
                        "version_to": r.version_to,
                        "changed_by": r.changed_by,
                        "change_summary": r.change_summary,
                        "changes": r.changes,
                        "metadata": r.metadata,
                    }
                    for r in self._history_records[schema_id]
                ],
                "saved_at": datetime.utcnow().isoformat(),
            }

            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save schema history: {str(e)}")

    def _save_all_histories(self) -> None:
        """Save all schema histories."""
        for schema_id in self._history_records:
            self._save_schema_history(schema_id)


# Factory function for easy instantiation
def create_schema_history_fetcher(
    storage_path: str = "data/schema_history",
    max_records_per_schema: int = 1000,
    retention_days: int = 365,
    **kwargs: object,
) -> SchemaHistoryFetcher:
    """Create a configured schema history fetcher."""
    config = SchemaHistoryConfig(
        storage_path=storage_path,
        max_records_per_schema=max_records_per_schema,
        retention_days=retention_days,
        **kwargs,
    )
    return SchemaHistoryFetcher(config)


# Convenience function for direct usage
def fetch_schema_history(
    schema_id: str | None = None,
    actions: list[str] = None,
    changed_by: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    include_changes: bool = True,
    limit: int = 100,
    offset: int = 0,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fetch schema history.

    Args:
        schema_id: ID of schema to fetch history for
        actions: List of actions to filter by
        changed_by: Contributor to filter by
        date_from: Start date for history
        date_to: End date for history
        include_changes: Whether to include detailed changes
        limit: Maximum number of records
        offset: Number of records to skip
        config: Optional fetcher configuration

    Returns:
        Dict: History results
    """
    # Create fetcher and fetch history
    fetcher_config = SchemaHistoryConfig(**config or {})
    fetcher = SchemaHistoryFetcher(fetcher_config)

    query = SchemaHistoryQuery(
        schema_id=schema_id,
        actions=[HistoryAction(action) for action in (actions or [])],
        changed_by=changed_by,
        date_from=date_from,
        date_to=date_to,
        include_changes=include_changes,
        limit=limit,
        offset=offset,
    )

    result = fetcher.fetch_history(query)

    # Convert result to dict for JSON serialization
    return {
        "records": [
            {
                "id": r.id,
                "schema_id": r.schema_id,
                "action": r.action.value,
                "timestamp": r.timestamp.isoformat(),
                "version_from": r.version_from,
                "version_to": r.version_to,
                "changed_by": r.changed_by,
                "change_summary": r.change_summary,
                "changes": r.changes,
                "metadata": r.metadata,
            }
            for r in result.records
        ],
        "total_count": result.total_count,
        "query": {
            "schema_id": result.query.schema_id,
            "actions": [a.value for a in result.query.actions],
            "changed_by": result.query.changed_by,
            "include_changes": result.query.include_changes,
            "limit": result.query.limit,
            "offset": result.query.offset,
        },
        "metadata": result.metadata,
    }
