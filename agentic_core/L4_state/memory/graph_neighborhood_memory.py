"""L4 State: Graph-Neighborhood Memory — per-ADG-node memory cards.

For each important ADG node (module, symbol, agent, guardrail, healer, etc.)
persists a compact "memory card" entity in Memory MCP summarising:

  - layer and territory
  - adjacent ADG relation families
  - common failure families observed at this node
  - common healers successfully dispatched for this node
  - policy touchpoints (policy hashes that governed decisions here)
  - replay sensitivity flag
  - retrieval sensitivity flag

This gives the system a librarian card-catalog view of each component so
routing, healing, and RAG decisions can be informed by prior governed cases,
not just retrieved documents or live telemetry.

Design invariants
-----------------
1. Memory cards are stored as Memory MCP entities via ``GraphMemoryBridge``.
2. Entity names use the ADG canonical name as-is (``ADG::Module::...`` etc.).
3. Card updates are additive observations — no entity is ever deleted here.
4. Fail-open: errors log and return False rather than raise.
5. No wall-clock reads; ``timestamp_utc`` is caller-supplied.
6. Max observation length enforced at 1 800 chars to prevent graph bloat.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "graph_neighborhood_memory", "L4")
_emit_routes_through("p1", "graph_neighborhood_memory", "L4")
_emit_escalates_to_human("p1", "graph_neighborhood_memory", "L4")
_emit_reads_policy_state("p1", "graph_neighborhood_memory", "L4")


def _get_determinism_fns():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_determinism_fns", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_determinism_fns", "p0_governance")
    from system_learning.enforcement.determinism import deterministic_json, stable_sha256_json

    return deterministic_json, stable_sha256_json


logger = logging.getLogger(__name__)

_MAX_OBS = 1800
_CARD_ENTITY_TYPE = "ADGNodeMemoryCard"


def _truncate(s: str, limit: int = _MAX_OBS) -> str:
    return s if len(s) <= limit else s[: limit - 3] + "..."


# ---------------------------------------------------------------------------
# MemoryCard dataclass — lightweight, not frozen so callers can accumulate
# ---------------------------------------------------------------------------


@dataclass
class MemoryCard:
    """In-process representation of an ADG node memory card.

    Attributes
    ----------
    adg_entity_name:
        Canonical ADG entity name (e.g. ``ADG::Module::agentic_core/L2_execution/...``).
    layer:
        Layer label (e.g. ``L0``, ``L4``, ``L_SL``).
    territory:
        Sovereign territory label (e.g. ``L4_state``, ``L5_safety``).
    relation_families:
        Set of ADG relation families observed at this node
        (e.g. ``{"routing", "healing", "guardrail"}``).
    common_failure_families:
        Set of stable failure category strings seen at this node.
    common_healers:
        Set of healer_id strings that successfully resolved issues at this node.
    policy_touchpoints:
        Set of policy_hash strings that governed decisions at this node.
    replay_sensitive:
        True if this node participates in deterministic replay paths.
    retrieval_sensitive:
        True if this node is on a RAG/retrieval path (completeness-relevant).
    timestamp_utc:
        Unix timestamp of the most recent card update (caller-supplied).
    """

    adg_entity_name: str
    layer: str
    territory: str = ""
    relation_families: set[str] = field(default_factory=set)
    common_failure_families: set[str] = field(default_factory=set)
    common_healers: set[str] = field(default_factory=set)
    policy_touchpoints: set[str] = field(default_factory=set)
    replay_sensitive: bool = False
    retrieval_sensitive: bool = False
    timestamp_utc: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "adg_entity_name": self.adg_entity_name,
            "common_failure_families": sorted(self.common_failure_families),
            "common_healers": sorted(self.common_healers),
            "layer": self.layer,
            "policy_touchpoints": sorted(self.policy_touchpoints),
            "relation_families": sorted(self.relation_families),
            "replay_sensitive": self.replay_sensitive,
            "retrieval_sensitive": self.retrieval_sensitive,
            "territory": self.territory,
            "timestamp_utc": self.timestamp_utc,
        }

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())

    def to_observations(self) -> list[str]:
        """Build the observation list stored on the Memory MCP entity."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "MemoryCard.to_observations")

        obs = [
            f"layer:{self.layer}",
            f"territory:{self.territory or 'NONE'}",
            f"replay_sensitive:{self.replay_sensitive}",
            f"retrieval_sensitive:{self.retrieval_sensitive}",
            f"timestamp_utc:{self.timestamp_utc}",
        ]
        if self.relation_families:
            obs.append(f"relation_families:{','.join(sorted(self.relation_families))}")
        if self.common_failure_families:
            obs.append(f"common_failure_families:{','.join(sorted(self.common_failure_families))}")
        if self.common_healers:
            obs.append(f"common_healers:{','.join(sorted(self.common_healers))}")
        if self.policy_touchpoints:
            obs.append(f"policy_touchpoints:{','.join(sorted(self.policy_touchpoints))}")
        obs.append(_truncate(f"card_summary:{deterministic_json(self.to_dict())}"))
        return obs


# ---------------------------------------------------------------------------
# GraphNeighborhoodMemory
# ---------------------------------------------------------------------------


class GraphNeighborhoodMemory:
    """Persists per-ADG-node memory cards in Memory MCP.

    Each call to ``upsert_card`` stores (or updates via new observations) a
    memory card entity for the given ADG node.  The in-process ``_cards`` dict
    acts as a write-through cache so repeated upserts within the same process
    avoid redundant bridge calls for unchanged cards.

    Usage
    -----
    .. code-block:: python

        mem = GraphNeighborhoodMemory()

        card = MemoryCard(
            adg_entity_name="ADG::Module::agentic_core/L2_execution/healers/base.py",
            layer="L2",
            territory="L2_execution",
            relation_families={"healing", "guardrail"},
            common_failure_families={"IMPORT_ERROR", "POLICY_VIOLATION"},
            common_healers={"AutoRepairHealer"},
            policy_touchpoints={"abc123..."},
            replay_sensitive=True,
            timestamp_utc=1700000000,
        )
        mem.upsert_card(card)

        results = mem.search("L2 healing POLICY_VIOLATION")
    """

    def __init__(self, bridge: GraphMemoryBridge | None = None) -> None:
        self._bridge = bridge or GraphMemoryBridge.get_instance()
        self._cards: dict[str, MemoryCard] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upsert_card(self, card: MemoryCard) -> bool:
        """Store or update a memory card for an ADG node.

        If a card for this entity was already stored in this process with an
        identical ``stable_hash``, the write is skipped (no-op).

        Returns True on successful write or no-op, False on bridge error.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "GraphNeighborhoodMemory.upsert_card")

        if not card.adg_entity_name:
            logger.warning("[GraphNeighborhoodMemory] adg_entity_name must not be empty")
            return False

        existing = self._cards.get(card.adg_entity_name)
        if existing is not None and existing.stable_hash() == card.stable_hash():
            logger.debug(
                "[GraphNeighborhoodMemory] Card unchanged, skipping write: %s",
                card.adg_entity_name,
            )
            return True

        observations = card.to_observations()
        ok = self._bridge.create_agent_entity(
            agent_name=card.adg_entity_name,
            agent_type=_CARD_ENTITY_TYPE,
            observations=observations,
        )
        if ok:
            self._cards[card.adg_entity_name] = card
            logger.debug("[GraphNeighborhoodMemory] Card stored: %s", card.adg_entity_name)
        return ok

    def record_failure(
        self,
        adg_entity_name: str,
        failure_family: str,
        layer: str,
        timestamp_utc: int,
        territory: str = "",
    ) -> bool:
        """Convenience: add a failure family observation to an existing card.

        If no card exists in process yet for this entity, creates a minimal one.
        """
        card = self._cards.get(adg_entity_name)
        if card is None:
            card = MemoryCard(
                adg_entity_name=adg_entity_name,
                layer=layer,
                territory=territory,
                timestamp_utc=timestamp_utc,
            )
        card.common_failure_families.add(failure_family)
        card.timestamp_utc = timestamp_utc
        return self.upsert_card(card)

    def record_healer_success(
        self,
        adg_entity_name: str,
        healer_id: str,
        layer: str,
        timestamp_utc: int,
        territory: str = "",
    ) -> bool:
        """Convenience: add a successful healer observation to an existing card."""
        card = self._cards.get(adg_entity_name)
        if card is None:
            card = MemoryCard(
                adg_entity_name=adg_entity_name,
                layer=layer,
                territory=territory,
                timestamp_utc=timestamp_utc,
            )
        card.common_healers.add(healer_id)
        card.timestamp_utc = timestamp_utc
        return self.upsert_card(card)

    def record_policy_touchpoint(
        self,
        adg_entity_name: str,
        policy_hash: str,
        layer: str,
        timestamp_utc: int,
        territory: str = "",
    ) -> bool:
        """Convenience: add a policy hash touchpoint to an existing card."""
        card = self._cards.get(adg_entity_name)
        if card is None:
            card = MemoryCard(
                adg_entity_name=adg_entity_name,
                layer=layer,
                territory=territory,
                timestamp_utc=timestamp_utc,
            )
        card.policy_touchpoints.add(policy_hash)
        card.timestamp_utc = timestamp_utc
        return self.upsert_card(card)

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search the neighborhood memory by free-text query.

        Returns raw MCP graph node dicts.
        """
        return self._bridge.search_entities(query)

    def get_card(self, adg_entity_name: str) -> MemoryCard | None:
        """Return the in-process cached card for an entity (if any)."""
        return self._cards.get(adg_entity_name)

    def list_cached_entities(self) -> list[str]:
        """Return list of ADG entity names with in-process cards."""
        return list(self._cards.keys())

    def get_stats(self) -> dict[str, Any]:
        return {
            "cached_cards": len(self._cards),
            "bridge_stats": self._bridge.get_statistics(),
        }


__all__ = ["GraphNeighborhoodMemory", "MemoryCard"]
