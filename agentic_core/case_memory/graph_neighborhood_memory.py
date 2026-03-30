"""GraphNeighborhoodMemory — Card upsert and deduplication for memory."""

from __future__ import annotations

from typing import Any, Protocol

from agentic_core.case_memory.memory_card import MemoryCard


class BridgeProtocol(Protocol):
    """Protocol for bridge implementations."""

    def get(self, key: str) -> Any | None:
        """Get value by key."""
        ...

    def put(self, key: str, value: Any) -> bool:
        """Store value by key."""
        ...

    def commit(self) -> None:
        """Commit pending changes."""
        ...


class GraphNeighborhoodMemory:
    """Memory store for graph neighborhood with card upsert and dedup."""

    def __init__(self, bridge: BridgeProtocol):
        self._bridge = bridge
        self._cache: dict[str, MemoryCard] = {}

    def upsert(self, card: MemoryCard) -> bool:
        """Upsert a memory card (no-op if unchanged)."""
        if not card.adg_entity_name:
            return False

        key = f"memory:{card.adg_entity_name}"
        existing = self._cache.get(card.adg_entity_name)

        # No-op if unchanged
        if existing and not card.has_changed_from(existing):
            return True

        # Store new or changed card
        self._cache[card.adg_entity_name] = card
        self._bridge.put(key, card.to_dict())
        self._bridge.commit()
        return True

    def record_healer_success(self, entity_name: str, healer_name: str) -> bool:
        """Record a successful healing for an entity."""
        if not entity_name:
            return False

        key = f"memory:{entity_name}"
        existing = self._cache.get(entity_name)

        if existing:
            # Create new card with updated history
            new_history = list(existing.healer_history) + [healer_name]
            new_card = MemoryCard(
                adg_entity_name=existing.adg_entity_name,
                layer=existing.layer,
                last_updated_utc=existing.last_updated_utc,
                healer_history=new_history,
                policy_touchpoints=list(existing.policy_touchpoints),
                embedding_snapshot=existing.embedding_snapshot,
            )
            self._cache[entity_name] = new_card
            self._bridge.put(key, new_card.to_dict())
            self._bridge.commit()

        return True

    def record_policy_touchpoint(self, entity_name: str, policy_ref: str) -> bool:
        """Record a policy touchpoint for an entity."""
        if not entity_name:
            return False

        key = f"memory:{entity_name}"
        existing = self._cache.get(entity_name)

        if existing:
            # Create new card with updated touchpoints
            new_touchpoints = list(existing.policy_touchpoints) + [policy_ref]
            new_card = MemoryCard(
                adg_entity_name=existing.adg_entity_name,
                layer=existing.layer,
                last_updated_utc=existing.last_updated_utc,
                healer_history=list(existing.healer_history),
                policy_touchpoints=new_touchpoints,
                embedding_snapshot=existing.embedding_snapshot,
            )
            self._cache[entity_name] = new_card
            self._bridge.put(key, new_card.to_dict())
            self._bridge.commit()

        return True

    def get(self, entity_name: str) -> MemoryCard | None:
        """Retrieve a memory card by entity name."""
        return self._cache.get(entity_name)
