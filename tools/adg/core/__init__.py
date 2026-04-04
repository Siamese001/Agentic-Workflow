"""ADG Core Models — Pydantic models for type-safe ADG entities."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ADGNode(BaseModel):
    """Canonical node representation from SQLite."""
    id: str
    adg_name: str
    entity_type: str
    layer: Optional[str] = None
    file_path: Optional[str] = None
    resolved_path: Optional[str] = None

    class Config:
        extra = "allow"  # Allow additional fields from SQLite


class ADGEdge(BaseModel):
    """Canonical edge representation from SQLite."""
    id: str
    src_id: str
    dst_id: str
    relation_type: str
    edge_kind: str
    source_file: Optional[str] = None
    line_no: Optional[int] = None
    symbol: Optional[str] = None

    class Config:
        extra = "allow"


class ADGResponse(BaseModel):
    """Unified response shape regardless of backend."""
    status: str = "ok"
    data: Dict[str, Any]
    backend_used: str = Field(..., description="redis|sqlite")
    cache_meta: Dict[str, Any] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    """Health check response."""
    mode: str  # "sqlite_only" | "full"
    sqlite: str  # "healthy" | "degraded" | "unavailable"
    redis: str   # "healthy" | "degraded" | "unavailable"
    cache_hit_capable: bool
    schema_version: str
    adg_snapshot_id: str
