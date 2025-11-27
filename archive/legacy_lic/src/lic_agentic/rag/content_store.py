"""Content-addressable store with TTL tracking."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class ContentMetadata:
    """Metadata persisted with cached retrieval artifacts."""

    tool: str
    ts: float
    extra: Dict[str, Any]


def make_key(**components: Any) -> str:
    """Return a stable cache key for retrieval artifacts."""

    normalized = json.dumps(components, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class ContentStore:
    """In-memory cache with TTL-based freshness checks."""

    def __init__(self) -> None:
        self._db: Dict[str, Tuple[Any, ContentMetadata]] = {}

    def put(self, key: str, blob: Any, meta: Dict[str, Any]) -> None:
        metadata = ContentMetadata(tool=str(meta.get("tool", "unknown")), ts=time.time(), extra=dict(meta))
        self._db[key] = (blob, metadata)

    def get(self, key: str, ttl_s: int) -> Optional[Tuple[Any, ContentMetadata, bool]]:
        record = self._db.get(key)
        if not record:
            return None
        blob, metadata = record
        fresh = (time.time() - metadata.ts) <= ttl_s
        return blob, metadata, fresh

    def clear(self) -> None:
        self._db.clear()
