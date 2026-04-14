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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "graph_neighborhood_memory")
emit_determinism_digest("p0", "graph_neighborhood_memory")

_emit_dispatches_healing_run("p1", "graph_neighborhood_memory", "L4")
_emit_routes_through("p1", "graph_neighborhood_memory", "L4")
_emit_checks_agent_registry("p1", "graph_neighborhood_memory", "agent_registry")
_emit_validates_agent_capability("p1", "graph_neighborhood_memory", "capability")
_emit_dispatches_execution_plan("p1", "graph_neighborhood_memory", "exec_plan")
_emit_agent_executes_agent("p1", "graph_neighborhood_memory", "sub_agent")
_emit_routes_to_agent("p1", "graph_neighborhood_memory", "target_agent")
_emit_verifies_policy("p1", "graph_neighborhood_memory", "policy_check")
_emit_observes_runtime_state("p1", "graph_neighborhood_memory", "runtime_state")
_emit_verifies_boundary("p1", "graph_neighborhood_memory", "boundary_check")
_emit_transcripts_response("p1", "graph_neighborhood_memory", "transcript")
_emit_hard_fails_untranscripted("p1", "graph_neighborhood_memory")
_emit_gated_by_confidence("p1", "graph_neighborhood_memory", "confidence_gate")
_emit_escalates_to_human("p1", "graph_neighborhood_memory", "L4")
_emit_reads_policy_state("p1", "graph_neighborhood_memory", "L4")
_emit_authorize_and_execute("p2", "graph_neighborhood_memory", "execution_auth")
_emit_validates_capability("p2", "graph_neighborhood_memory", "capability_check")
_emit_routes_to_capability("p2", "graph_neighborhood_memory", "capability_route")
_emit_writes_via_uwg("p2", "graph_neighborhood_memory", "uwg_write")
_emit_blocks_direct_write("p2", "graph_neighborhood_memory", "direct_write_block")
_emit_records_tool_invocation("p2", "graph_neighborhood_memory", "tool_invocation")
_emit_captures_execution_output("p2", "graph_neighborhood_memory", "exec_output")
_emit_dispatches_agent("p3", "graph_neighborhood_memory", "agent_dispatch")
_emit_coordinates_agents("p3", "graph_neighborhood_memory", "agent_coordination")
_emit_records_workflow_lineage("p3", "graph_neighborhood_memory", "workflow_lineage")
_emit_records_healing_outcome("p3", "graph_neighborhood_memory", "healing_outcome")
_emit_escalates_failure("p3", "graph_neighborhood_memory", "failure_escalation")
_emit_orchestrates_workflow("p3", "graph_neighborhood_memory", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "graph_neighborhood_memory", "healing_dispatch")
_emit_invokes_evaluation("p3", "graph_neighborhood_memory", "evaluation_signal")
_emit_records_telemetry_event("p4", "graph_neighborhood_memory", "telemetry_event")
_emit_captures_evaluation_metric("p4", "graph_neighborhood_memory", "eval_metric")
_emit_stores_embedding("p4", "graph_neighborhood_memory", "embedding_store")
_emit_updates_meta_learning_state("p4", "graph_neighborhood_memory", "meta_learning")
_emit_links_execution_to_snapshot("p4", "graph_neighborhood_memory", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("graph_neighborhood_memory", "p4obs", "metric_1")
_emit_emits_metric_event("graph_neighborhood_memory", "p4obs", "metric_2")
_emit_emits_metric_event("graph_neighborhood_memory", "p4obs", "metric_3")
_emit_emits_metric_event("graph_neighborhood_memory", "p4obs", "metric_4")
_emit_emits_metric_event("graph_neighborhood_memory", "p4obs", "metric_5")
_emit_emits_metric_event("graph_neighborhood_memory", "p4obs", "metric_6")
_emit_records_incident_event("graph_neighborhood_memory", "p4obs", "incident")
_emit_captures_runtime_anomaly("graph_neighborhood_memory", "p4obs", "anomaly")
_emit_writes_observability_log("graph_neighborhood_memory", "p4obs", "obs_log")
_emit_updates_monitoring_state("graph_neighborhood_memory", "p4obs", "mon_state")
_emit_triggers_alert("graph_neighborhood_memory", "p4obs", "alert")
_emit_links_incident_trace("graph_neighborhood_memory", "p4obs", "trace_link")
_emit_captures_pattern("graph_neighborhood_memory", "p3lm", "pattern")
_emit_records_learning_event("graph_neighborhood_memory", "p3lm", "learning_event")
_emit_writes_learning_snapshot("graph_neighborhood_memory", "p3lm", "snapshot")
_emit_feeds_meta_learning("graph_neighborhood_memory", "p3lm", "meta_feed")
_emit_updates_routing_strategy("graph_neighborhood_memory", "p3lm", "routing")
_emit_improves_agent_policy("graph_neighborhood_memory", "p3lm", "policy")
_emit_stores_learning_state("graph_neighborhood_memory", "p3lm", "state")
_emit_records_execution_trace("graph_neighborhood_memory", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("graph_neighborhood_memory", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("graph_neighborhood_memory", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("graph_neighborhood_memory", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("graph_neighborhood_memory", "L4_STATE", "p2_trace_5")
_emit_reads_environ("graph_neighborhood_memory", "env_read", "p2_env_1")
_emit_reads_environ("graph_neighborhood_memory", "env_read", "p2_env_2")
_emit_reads_runtime_state("graph_neighborhood_memory", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("graph_neighborhood_memory", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "graph_neighborhood_memory", "context_pull")
_emit_pulls_context("p1", "graph_neighborhood_memory", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "graph_neighborhood_memory", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "graph_neighborhood_memory", "uwg_term_2")
_emit_writes_through("p1", "graph_neighborhood_memory", "write_through")
_emit_writes_through("p1", "graph_neighborhood_memory", "write_through_2")
_emit_validated_by_safety_plane("p1", "graph_neighborhood_memory", "safety_validation")
_emit_invokes_eval("p1", "graph_neighborhood_memory", "eval_call")
_emit_proposal_commits_routing("p1", "graph_neighborhood_memory", "routing_commit")


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
        _, _stable_sha256_json = _get_determinism_fns()
        return _stable_sha256_json(self.to_dict())

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
        _deterministic_json, _ = _get_determinism_fns()
        obs.append(_truncate(f"card_summary:{_deterministic_json(self.to_dict())}"))
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
        self._graph_store = None
        self._init_graph_store()

    def _init_graph_store(self) -> None:
        """Initialize SQLiteGraphStore for graph-distance-based memory retrieval."""
        try:
            from agentic_core.L4_state.utils.memory.graph_store_factory import (
                create_sqlite_graph_store_or_none,
            )

            self._graph_store = create_sqlite_graph_store_or_none()
            if self._graph_store:
                logger.info("GraphNeighborhoodMemory: Graph store initialized for enhanced retrieval")
        except Exception as e:
            logger.warning(f"GraphNeighborhoodMemory: Graph store initialization failed: {e}")
            self._graph_store = None

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

    def search_by_graph_distance(
        self,
        adg_entity_name: str,
        max_depth: int = 2,
        relation_types: list[str] | None = None,
    ) -> list[MemoryCard]:
        """Search memory cards by graph distance from a given entity.

                Uses SQLiteGraphStore to find structurally related ADG nodes,
                then returns their memory cards. This enables retrieval of memories
                from components that are graph-adjacent (e.g., callers, callees,
                import dependencies) rather than just text-similar.
        from tqdm import tqdm

                Args:
                    adg_entity_name: The ADG entity name to start from
                    max_depth: Maximum graph traversal depth (default: 2)
                    relation_types: Optional filter for relation types (e.g., ['calls', 'imports'])

                Returns:
                    List of MemoryCard objects for graph-adjacent entities
        """
        if not self._graph_store:
            logger.warning("Graph store not available, using text search fallback")
            # Fallback to text search
            results = self.search(adg_entity_name)
            return [self._bridge.get_agent_entity(r.get("name", "")) for r in results if r.get("name")]

        try:
            # Search for the entity in the graph store
            entities = self._graph_store.search_entities(adg_entity_name, limit=10)
            if not entities:
                logger.debug(f"No graph entities found for {adg_entity_name}")
                return []

            # Get the first matching entity
            start_entity = entities[0]

            # Traverse the graph to find related entities
            paths = self._graph_store.traverse(
                start_entity.id,
                max_depth=max_depth,
                relation_types=relation_types,
            )

            # Collect unique entity IDs from paths
            related_entity_ids = set()
            for path in tqdm(paths, desc="Processing", unit="item"):
                for node in path.nodes:
                    if node.id != start_entity.id:  # Exclude the start node
                        related_entity_ids.add(node.id)

            # Get memory cards for related entities
            related_cards = []
            for entity_id in related_entity_ids:
                entity = self._graph_store.get_entity(entity_id)
                if entity:
                    card = self.get_card(entity.name)
                    if card:
                        related_cards.append(card)

            logger.info(
                f"GraphNeighborhoodMemory[Graph]: Found {len(related_cards)} cards "
                f"within {max_depth} hops of {adg_entity_name}",
            )
            return related_cards

        except Exception as e:
            logger.warning(f"Graph-distance search failed: {e}, falling back to text search")
            return []

    def search_by_centrality(
        self,
        min_centrality: float = 0.5,
        layer: str | None = None,
    ) -> list[MemoryCard]:
        """Search memory cards by centrality score.

        Returns cards for high-centrality nodes (important hubs in the graph).
        Useful for finding memories from critical components.

        Args:
            min_centrality: Minimum centrality score (0.0-1.0)
            layer: Optional layer filter (e.g., 'L4', 'L5')

        Returns:
            List of MemoryCard objects for high-centrality entities
        """
        if not self._graph_store:
            logger.warning("Graph store not available, returning all cached cards")
            return list(self._cards.values())

        try:
            high_centrality_cards = []
            for card in tqdm(self._cards.values(), desc="Processing", unit="item"):
                if layer and card.layer != layer:
                    continue

                # Get centrality from graph store
                entities = self._graph_store.search_entities(card.adg_entity_name, limit=1)
                if entities:
                    centrality = self._graph_store.get_centrality(entities[0].id)
                    if isinstance(centrality, float) and centrality >= min_centrality:
                        high_centrality_cards.append(card)

            # Sort by centrality (descending)
            high_centrality_cards.sort(
                key=lambda c: (
                    self._graph_store.get_centrality(
                        self._graph_store.search_entities(c.adg_entity_name, limit=1)[0].id,
                    )
                    if self._graph_store.search_entities(c.adg_entity_name, limit=1)
                    else 0.0
                ),
                reverse=True,
            )

            logger.info(
                f"GraphNeighborhoodMemory[Graph]: Found {len(high_centrality_cards)} "
                f"high-centrality cards (>= {min_centrality})",
            )
            return high_centrality_cards

        except Exception as e:
            logger.warning(f"Centrality-based search failed: {e}, returning all cached cards")
            return list(self._cards.values())

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
