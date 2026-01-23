"""schema Store Querier - Queries and retrieves schemas from storage.

This module provides schema querying capabilities for schema operations,
including lookup, filtering, versioning, and metadata retrieval.
Follows the functional component pattern with proper logging.
"""

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SchemaType(Enum):
    """Types of schemas."""

    JSON_SCHEMA = "json_schema"
    AVRO_SCHEMA = "avro_schema"
    PROTOBUF_SCHEMA = "protobuf_schema"
    XML_SCHEMA = "xml_schema"
    CUSTOM = "custom"


class SchemaStatus(Enum):
    """Status of schemas."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class SchemaMetadata:
    """Metadata for a schema."""

    id: str
    name: str
    version: str
    schema_type: SchemaType
    status: SchemaStatus
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    size_bytes: int = 0


@dataclass
class SchemaEntry:
    """Complete schema entry with metadata and content."""

    metadata: SchemaMetadata
    content: dict[str, Any]
    validation_rules: dict[str, Any] | None = None
    examples: list[dict[str, Any]] | None = None


@dataclass
class SchemaQuery:
    """Query configuration for schema retrieval."""

    name_pattern: str | None = None
    schema_type: SchemaType | None = None
    status: SchemaStatus | None = None
    tags: list[str] = field(default_factory=list)
    version_range: str | None = None
    created_by: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    include_content: bool = True
    include_validation: bool = False
    include_examples: bool = False
    limit: int = 100
    offset: int = 0


@dataclass
class SchemaQueryResult:
    """Result of schema query."""

    entries: list[SchemaEntry]
    total_count: int
    query: SchemaQuery
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaStoreConfig:
    """configuration for schema store."""

    storage_path: str = "data/schema_store"
    max_entries_per_query: int = 1000
    enable_versioning: bool = True
    enable_indexing: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24


class SchemaStoreQuerier:
    """Main class for querying schema store."""

    def __init__(self, config: SchemaStoreConfig | None = None):
        self.config = config or SchemaStoreConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._schema_cache: dict[str, SchemaEntry] = {}
        self._name_index: dict[str, list[str]] = {}
        self._type_index: dict[SchemaType, list[str]] = {}
        self._tag_index: dict[str, list[str]] = {}
        self._load_schemas()

    def query_schemas(self, query: SchemaQuery) -> SchemaQueryResult:
        """Query schemas based on criteria.

        Args:
            query: schema query configuration

        Returns:
            SchemaQueryResult: Query results with schemas and metadata
        """
        self.logger.info(
            f"Querying schemas with criteria: type={query.schema_type}, status={query.status}"
        )

        try:
            # Apply filters
            filtered_ids = self._apply_filters(query)

            # Sort by updated date (descending)
            filtered_ids.sort(key=lambda x: self._schema_cache[x].metadata.updated_at, reverse=True)

            # Apply pagination
            total_count = len(filtered_ids)
            paginated_ids = filtered_ids[query.offset : query.offset + query.limit]

            # Build result entries
            entries = []
            for schema_id in paginated_ids:
                entry = self._schema_cache[schema_id]

                # Create filtered entry based on query options
                filtered_entry = SchemaEntry(
                    metadata=entry.metadata,
                    content=entry.content if query.include_content else {},
                    validation_rules=entry.validation_rules if query.include_validation else None,
                    examples=entry.examples if query.include_examples else None,
                )
                entries.append(filtered_entry)

            result = SchemaQueryResult(
                entries=entries,
                total_count=total_count,
                query=query,
                metadata={
                    "queried_at": datetime.utcnow().isoformat(),
                    "storage_path": self.config.storage_path,
                    "total_schemas": len(self._schema_cache),
                    "querier": "SchemaStoreQuerier",
                },
            )

            self.logger.info(
                f"schema query completed: {len(entries)} results (total: {total_count})"
            )

            return result

        except Exception as e:
            self.logger.error(f"schema query failed: {str(e)}")
            return SchemaQueryResult(
                entries=[], total_count=0, query=query, metadata={"error": str(e)}
            )

    def get_schema(self, schema_id: str) -> SchemaEntry | None:
        """Get a specific schema by ID.

        Args:
            schema_id: ID of schema to retrieve

        Returns:
            SchemaEntry: schema if found, None otherwise
        """
        return self._schema_cache.get(schema_id)

    def get_schema_by_name(self, name: str, version: str | None = None) -> SchemaEntry | None:
        """Get schema by name and optionally version.

        Args:
            name: schema name
            version: Optional version (latest if not specified)

        Returns:
            SchemaEntry: schema if found, None otherwise
        """
        if name not in self._name_index:
            return None

        schema_ids = self._name_index[name]

        if version:
            # Find specific version
            for schema_id in schema_ids:
                entry = self._schema_cache[schema_id]
                if entry.metadata.version == version:
                    return entry
        else:
            # Get latest version
            latest_id = max(schema_ids, key=lambda x: self._schema_cache[x].metadata.updated_at)
            return self._schema_cache[latest_id]

        return None

    def get_schema_versions(self, name: str) -> list[SchemaMetadata]:
        """Get all versions of a schema.

        Args:
            name: schema name

        Returns:
            List[SchemaMetadata]: Metadata for all versions
        """
        if name not in self._name_index:
            return []

        schema_ids = self._name_index[name]
        versions = [self._schema_cache[schema_id].metadata for schema_id in schema_ids]

        # Sort by version (descending)
        versions.sort(key=lambda x: x.updated_at, reverse=True)

        return versions

    def add_schema(self, entry: SchemaEntry) -> bool:
        """Add a schema to the store.

        Args:
            entry: schema entry to add

        Returns:
            bool: True if schema was added successfully
        """
        try:
            schema_id = entry.metadata.id

            # Check if already exists
            if schema_id in self._schema_cache:
                self.logger.warning(f"schema {schema_id} already exists, updating")

            # Add to cache
            self._schema_cache[schema_id] = entry

            # Update indexes
            self._update_indexes(schema_id, entry)

            # Save to disk
            self._save_schema(entry)

            self.logger.info(f"Added schema: {schema_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add schema: {str(e)}")
            return False

    def delete_schema(self, schema_id: str) -> bool:
        """Delete a schema from the store.

        Args:
            schema_id: ID of schema to delete

        Returns:
            bool: True if schema was deleted
        """
        if schema_id not in self._schema_cache:
            return False

        try:
            entry = self._schema_cache[schema_id]

            # Remove from cache
            del self._schema_cache[schema_id]

            # Update indexes
            self._remove_from_indexes(schema_id, entry)

            # Delete from disk
            self._delete_schema_file(schema_id)

            self.logger.info(f"Deleted schema: {schema_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete schema: {str(e)}")
            return False

    def get_statistics(self) -> dict[str, Any]:
        """Get schema store statistics.

        Returns:
            Dict: Statistics about the schema store
        """
        # Count by type
        type_counts = {}
        for entry in self._schema_cache.values():
            schema_type = entry.metadata.schema_type.value
            type_counts[schema_type] = type_counts.get(schema_type, 0) + 1

        # Count by status
        status_counts = {}
        for entry in self._schema_cache.values():
            status = entry.metadata.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Find largest schemas
        sorted_by_size = sorted(
            self._schema_cache.values(), key=lambda x: x.metadata.size_bytes, reverse=True
        )[:5]

        # Most recently updated
        recent_schemas = sorted(
            self._schema_cache.values(), key=lambda x: x.metadata.updated_at, reverse=True
        )[:5]

        return {
            "total_schemas": len(self._schema_cache),
            "type_distribution": type_counts,
            "status_distribution": status_counts,
            "largest_schemas": [
                {"id": e.metadata.id, "name": e.metadata.name, "size_bytes": e.metadata.size_bytes}
                for e in sorted_by_size
            ],
            "recently_updated": [
                {
                    "id": e.metadata.id,
                    "name": e.metadata.name,
                    "updated_at": e.metadata.updated_at.isoformat(),
                }
                for e in recent_schemas
            ],
            "index_sizes": {
                "name_index": len(self._name_index),
                "type_index": len(self._type_index),
                "tag_index": len(self._tag_index),
            },
        }

    def _load_schemas(self) -> None:
        """Load all schemas from storage."""
        try:
            storage_path = Path(self.config.storage_path)
            if not storage_path.exists():
                storage_path.mkdir(parents=True, exist_ok=True)
                return

            # Load each schema file
            for schema_file in storage_path.glob("*.json"):
                try:
                    with open(schema_file, encoding="utf-8") as f:
                        data = json.load(f)

                    # Convert to SchemaEntry
                    entry = self._json_to_schema_entry(data)
                    if entry:
                        self._schema_cache[entry.metadata.id] = entry
                        self._update_indexes(entry.metadata.id, entry)

                except Exception as e:
                    self.logger.error(f"Failed to load schema from {schema_file}: {str(e)}")

            self.logger.info(f"Loaded {len(self._schema_cache)} schemas from storage")

        except Exception as e:
            self.logger.error(f"Failed to load schemas: {str(e)}")

    def _apply_filters(self, query: SchemaQuery) -> list[str]:
        """Apply filters to schema IDs."""
        filtered_ids = list(self._schema_cache.keys())

        # Filter by name pattern
        if query.name_pattern:
            import re

            pattern = re.compile(query.name_pattern, re.IGNORECASE)
            filtered_ids = [
                id for id in filtered_ids if pattern.search(self._schema_cache[id].metadata.name)
            ]

        # Filter by type
        if query.schema_type:
            if query.schema_type in self._type_index:
                type_ids = set(self._type_index[query.schema_type])
                filtered_ids = list(set(filtered_ids) & type_ids)
            else:
                filtered_ids = []

        # Filter by status
        filtered_ids = [
            id
            for id in filtered_ids
            if not query.status or self._schema_cache[id].metadata.status == query.status
        ]

        # Filter by tags
        if query.tags:
            matching_ids = set()
            for tag in query.tags:
                if tag in self._tag_index:
                    matching_ids.update(self._tag_index[tag])
            filtered_ids = list(set(filtered_ids) & matching_ids)

        # Filter by creator
        if query.created_by:
            filtered_ids = [
                id
                for id in filtered_ids
                if self._schema_cache[id].metadata.created_by == query.created_by
            ]

        # Filter by date range
        if query.date_from:
            filtered_ids = [
                id
                for id in filtered_ids
                if self._schema_cache[id].metadata.created_at >= query.date_from
            ]

        if query.date_to:
            filtered_ids = [
                id
                for id in filtered_ids
                if self._schema_cache[id].metadata.created_at <= query.date_to
            ]

        return filtered_ids

    def _update_indexes(self, schema_id: str, entry: SchemaEntry) -> None:
        """Update indexes for a schema."""
        # Name index
        name = entry.metadata.name
        if name not in self._name_index:
            self._name_index[name] = []
        if schema_id not in self._name_index[name]:
            self._name_index[name].append(schema_id)

        # Type index
        schema_type = entry.metadata.schema_type
        if schema_type not in self._type_index:
            self._type_index[schema_type] = []
        if schema_id not in self._type_index[schema_type]:
            self._type_index[schema_type].append(schema_id)

        # Tag index
        for tag in entry.metadata.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            if schema_id not in self._tag_index[tag]:
                self._tag_index[tag].append(schema_id)

    def _remove_from_indexes(self, schema_id: str, entry: SchemaEntry) -> None:
        """Remove schema from indexes."""
        # Name index
        name = entry.metadata.name
        if name in self._name_index and schema_id in self._name_index[name]:
            self._name_index[name].remove(schema_id)
            if not self._name_index[name]:
                del self._name_index[name]

        # Type index
        schema_type = entry.metadata.schema_type
        if schema_type in self._type_index and schema_id in self._type_index[schema_type]:
            self._type_index[schema_type].remove(schema_id)
            if not self._type_index[schema_type]:
                del self._type_index[schema_type]

        # Tag index
        for tag in entry.metadata.tags:
            if tag in self._tag_index and schema_id in self._tag_index[tag]:
                self._tag_index[tag].remove(schema_id)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]

    def _save_schema(self, entry: SchemaEntry) -> None:
        """Save schema to disk."""
        try:
            storage_path = Path(self.config.storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)

            schema_file = storage_path / f"{entry.metadata.id}.json"

            # Convert to JSON
            data = self._schema_entry_to_json(entry)

            with open(schema_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save schema: {str(e)}")

    def _delete_schema_file(self, schema_id: str) -> None:
        """Delete schema file from disk."""
        try:
            storage_path = Path(self.config.storage_path)
            schema_file = storage_path / f"{schema_id}.json"

            if schema_file.exists():
                schema_file.unlink()

        except Exception as e:
            self.logger.error(f"Failed to delete schema file: {str(e)}")

    def _schema_entry_to_json(self, entry: SchemaEntry) -> dict[str, Any]:
        """Convert SchemaEntry to JSON-serializable dict."""
        return {
            "metadata": {
                "id": entry.metadata.id,
                "name": entry.metadata.name,
                "version": entry.metadata.version,
                "schema_type": entry.metadata.schema_type.value,
                "status": entry.metadata.status.value,
                "created_at": entry.metadata.created_at.isoformat(),
                "updated_at": entry.metadata.updated_at.isoformat(),
                "created_by": entry.metadata.created_by,
                "description": entry.metadata.description,
                "tags": entry.metadata.tags,
                "dependencies": entry.metadata.dependencies,
                "size_bytes": entry.metadata.size_bytes,
            },
            "content": entry.content,
            "validation_rules": entry.validation_rules,
            "examples": entry.examples,
        }

    def _json_to_schema_entry(self, data: dict[str, Any]) -> SchemaEntry | None:
        """Convert JSON dict to SchemaEntry."""
        try:
            metadata = SchemaMetadata(
                id=data["metadata"]["id"],
                name=data["metadata"]["name"],
                version=data["metadata"]["version"],
                schema_type=SchemaType(data["metadata"]["schema_type"]),
                status=SchemaStatus(data["metadata"]["status"]),
                created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
                updated_at=datetime.fromisoformat(data["metadata"]["updated_at"]),
                created_by=data["metadata"].get("created_by"),
                description=data["metadata"].get("description"),
                tags=data["metadata"].get("tags", []),
                dependencies=data["metadata"].get("dependencies", []),
                size_bytes=data["metadata"].get("size_bytes", 0),
            )

            return SchemaEntry(
                metadata=metadata,
                content=data.get("content", {}),
                validation_rules=data.get("validation_rules"),
                examples=data.get("examples"),
            )

        except Exception as e:
            self.logger.error(f"Failed to convert JSON to SchemaEntry: {str(e)}")
            return None


# Factory function for easy instantiation
def create_schema_store_querier(
    storage_path: str = "data/schema_store",
    max_entries_per_query: int = 1000,
    enable_versioning: bool = True,
    **kwargs: object,
) -> SchemaStoreQuerier:
    """Create a configured schema store querier."""
    config = SchemaStoreConfig(
        storage_path=storage_path,
        max_entries_per_query=max_entries_per_query,
        enable_versioning=enable_versioning,
        **kwargs,
    )
    return SchemaStoreQuerier(config)


# Convenience function for direct usage
def query_schema_store(
    name_pattern: str | None = None,
    schema_type: str | None = None,
    status: str | None = None,
    tags: list[str] = None,
    include_content: bool = True,
    limit: int = 100,
    offset: int = 0,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Query schema store.

    Args:
        name_pattern: Pattern to match schema names
        schema_type: Type of schemas to filter by
        status: Status of schemas to filter by
        tags: Tags to filter by
        include_content: Whether to include schema content
        limit: Maximum number of results
        offset: Number of results to skip
        config: Optional querier configuration

    Returns:
        Dict: Query results
    """
    # Create querier and execute query
    querier_config = SchemaStoreConfig(**config or {})
    querier = SchemaStoreQuerier(querier_config)

    query = SchemaQuery(
        name_pattern=name_pattern,
        schema_type=SchemaType(schema_type) if schema_type else None,
        status=SchemaStatus(status) if status else None,
        tags=tags or [],
        include_content=include_content,
        limit=limit,
        offset=offset,
    )

    result = querier.query_schemas(query)

    # Convert result to dict for JSON serialization
    return {
        "entries": [
            {
                "metadata": {
                    "id": e.metadata.id,
                    "name": e.metadata.name,
                    "version": e.metadata.version,
                    "schema_type": e.metadata.schema_type.value,
                    "status": e.metadata.status.value,
                    "created_at": e.metadata.created_at.isoformat(),
                    "updated_at": e.metadata.updated_at.isoformat(),
                    "created_by": e.metadata.created_by,
                    "description": e.metadata.description,
                    "tags": e.metadata.tags,
                    "dependencies": e.metadata.dependencies,
                    "size_bytes": e.metadata.size_bytes,
                },
                "content": e.content,
                "validation_rules": e.validation_rules,
                "examples": e.examples,
            }
            for e in result.entries
        ],
        "total_count": result.total_count,
        "query": {
            "name_pattern": result.query.name_pattern,
            "schema_type": result.query.schema_type.value if result.query.schema_type else None,
            "status": result.query.status.value if result.query.status else None,
            "tags": result.query.tags,
            "include_content": result.query.include_content,
            "limit": result.query.limit,
            "offset": result.query.offset,
        },
        "metadata": result.metadata,
    }
