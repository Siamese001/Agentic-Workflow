"""ADG Core Models — Pydantic models for type-safe ADG entities."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ADGNode(BaseModel):
    """Canonical node representation from SQLite."""

    id: str
    adg_name: str
    entity_type: str
    layer: str | None = None
    # resolved_path is the authoritative path field from the nodes schema.
    # file_path does not exist as a column — removed to prevent misleading null output.
    resolved_path: str | None = None

    class Config:
        extra = "allow"  # Allow additional fields from SQLite


class ADGEdge(BaseModel):
    """Canonical edge representation from SQLite."""

    id: str
    src_id: str
    dst_id: str
    relation_type: str
    edge_kind: str
    source_file: str | None = None
    line_no: int | None = None
    symbol: str | None = None

    class Config:
        extra = "allow"


QueryResultState = Literal[
    "COMPLETE",
    "EMPTY",
    "UNAVAILABLE",
    "STALE",
    "TRUNCATED",
    "UNKNOWN",
]


class QueryMeta(BaseModel):
    """Provenance and evaluation state for an ADG query result."""

    result_state: QueryResultState = "UNKNOWN"
    selected_artifact_digest: str | None = None
    source_artifact_digest: str | None = None
    schema_version: str = "unknown"
    metric_id: str | None = None
    metric_version: str | None = None
    requested_limit: int | None = None
    returned_count: int | None = None
    has_more: bool | None = None
    truncation_reason: str | None = None
    reason_code: str | None = None
    reason: str | None = None


class ADGResponse(BaseModel):
    """Unified response shape regardless of backend."""

    status: str = "ok"
    data: dict[str, Any]
    backend_used: Literal["redis", "sqlite", "projection"] = Field(
        ...,
        description="redis|sqlite|projection",
    )
    cache_meta: dict[str, Any] = Field(default_factory=dict)
    query_meta: QueryMeta = Field(default_factory=QueryMeta)


class HealthStatus(BaseModel):
    """Certification-aware ADG health response."""

    mode: str
    sqlite: str
    redis: str
    cache_hit_capable: bool
    schema_version: str
    adg_snapshot_id: str
    views_materialized_at: str | None = None
    overall_status: Literal[
        "healthy",
        "degraded",
        "critical",
        "unknown",
    ] = "unknown"
    reasons: list[str] = Field(default_factory=list)
    snapshot_selection: str = "unknown"
    certified: bool = False
    certification_status: str = "unknown"
    artifact_status: str = "unknown"
    pointer_path: str | None = None
    digest_verified: bool = False
    materialization_status: str = "UNKNOWN"
    materialization_counts: dict[str, int] = Field(default_factory=dict)
