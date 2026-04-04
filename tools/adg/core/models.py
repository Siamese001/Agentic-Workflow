"""ADG Core Models — Pydantic models for type-safe ADG entities."""
from typing import Any

from pydantic import BaseModel, Field


class ADGNode(BaseModel):
    """Canonical node representation from SQLite."""
    id: str
    adg_name: str
    entity_type: str
    layer: str | None = None
    file_path: str | None = None
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


class ADGResponse(BaseModel):
    """Unified response shape regardless of backend."""
    status: str = "ok"
    data: dict[str, Any]
    backend_used: str = Field(..., description="redis|sqlite")
    cache_meta: dict[str, Any] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    """Health check response."""
    mode: str  # "sqlite_only" | "full"
    sqlite: str  # "healthy" | "degraded" | "unavailable"
    redis: str   # "healthy" | "degraded" | "unavailable"
    cache_hit_capable: bool
    schema_version: str
    adg_snapshot_id: str
