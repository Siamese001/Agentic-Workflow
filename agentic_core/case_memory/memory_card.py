"""MemoryCard — Individual memory entry for graph neighborhood memory."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MemoryCard:
    """Frozen memory card for deterministic serialization."""

    adg_entity_name: str = ""
    layer: str = ""
    last_updated_utc: int = 0
    healer_history: list[str] = field(default_factory=list)
    policy_touchpoints: list[str] = field(default_factory=list)
    embedding_snapshot: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to sorted dictionary for deterministic serialization."""
        return {
            "adg_entity_name": self.adg_entity_name,
            "embedding_snapshot": self.embedding_snapshot,
            "healer_history": list(self.healer_history),
            "last_updated_utc": self.last_updated_utc,
            "layer": self.layer,
            "policy_touchpoints": list(self.policy_touchpoints),
        }

    def stable_hash(self) -> str:
        """Compute stable hash for deduplication."""
        content = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode()).hexdigest()

    def has_changed_from(self, other: MemoryCard | None) -> bool:
        """Check if this card differs from another."""
        if other is None:
            return True
        return self.stable_hash() != other.stable_hash()
