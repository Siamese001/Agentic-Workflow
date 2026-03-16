from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "graph_memory_bridge")
emit_determinism_digest("p0", "graph_memory_bridge")

_emit_dispatches_healing_run("p1", "graph_memory_bridge", "L4")
_emit_routes_through("p1", "graph_memory_bridge", "L4")
_emit_escalates_to_human("p1", "graph_memory_bridge", "L4")
_emit_reads_policy_state("p1", "graph_memory_bridge", "L4")
_emit_authorize_and_execute("p2", "graph_memory_bridge", "execution_auth")
_emit_validates_capability("p2", "graph_memory_bridge", "capability_check")
_emit_routes_to_capability("p2", "graph_memory_bridge", "capability_route")
_emit_writes_via_uwg("p2", "graph_memory_bridge", "uwg_write")
_emit_blocks_direct_write("p2", "graph_memory_bridge", "direct_write_block")
_emit_records_tool_invocation("p2", "graph_memory_bridge", "tool_invocation")
_emit_captures_execution_output("p2", "graph_memory_bridge", "exec_output")
_emit_dispatches_agent("p3", "graph_memory_bridge", "agent_dispatch")
_emit_coordinates_agents("p3", "graph_memory_bridge", "agent_coordination")
_emit_records_workflow_lineage("p3", "graph_memory_bridge", "workflow_lineage")
_emit_records_healing_outcome("p3", "graph_memory_bridge", "healing_outcome")
_emit_escalates_failure("p3", "graph_memory_bridge", "failure_escalation")
_emit_orchestrates_workflow("p3", "graph_memory_bridge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "graph_memory_bridge", "healing_dispatch")
_emit_invokes_evaluation("p3", "graph_memory_bridge", "evaluation_signal")
_emit_records_telemetry_event("p4", "graph_memory_bridge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "graph_memory_bridge", "eval_metric")
_emit_stores_embedding("p4", "graph_memory_bridge", "embedding_store")
_emit_updates_meta_learning_state("p4", "graph_memory_bridge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "graph_memory_bridge", "exec_snapshot_link")

"\n[PHASE 21] Graph Memory Bridge - Interface to Memory MCP Knowledge Graph.\n\nProvides a programmatic interface to the Memory MCP server for:\n- Entity creation (agents, tasks, protocols)\n- Relation creation (MASTERED_TASK, INTERACTS_WITH, etc.)\n- Observation storage\n- Graph queries\n\nThis bridge uses the live Windsurf Memory MCP tools:\n- mcp11_create_entities: Create entities in the knowledge graph\n- mcp11_create_relations: Create relations between entities\n- mcp11_add_observations: Add observations to entities\n- mcp11_search_nodes: Search for nodes in the graph\n- mcp11_open_nodes: Open specific nodes by name\n- mcp11_read_graph: Read the full graph\n\nResilient Mode: If MCP is unavailable, operations are logged but don't crash.\n\n[SSOT] This is the canonical interface for Memory MCP operations.\n"
import hashlib
import logging
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

try:
    from agentic_core.adg.client.mcp_client import ADGMCPClient as _MCPFallbackClient

    _FALLBACK_AVAILABLE = True
except ImportError:
    _FALLBACK_AVAILABLE = False

try:
    from tools.memory.sqlite_memory_store import SqliteMemoryStore as _SqliteMemoryStore

    _SQLITE_STORE_AVAILABLE = True
except ImportError:
    _SqliteMemoryStore = None  # type: ignore[assignment,misc]
    _SQLITE_STORE_AVAILABLE = False
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_writes_through,
)

Logger = logging.getLogger(__name__)


@dataclass
class EntityDefinition:
    """Definition for creating an entity in the Knowledge Graph."""

    name: str
    entity_type: str
    observations: list[str] = field(default_factory=list)


@dataclass
class RelationDefinition:
    """Definition for creating a relation in the Knowledge Graph."""

    from_entity: str
    to_entity: str
    relation_type: str


class GraphMemoryBridge:
    """
    [PHASE 21] Bridge to Memory MCP Knowledge Graph.

    Provides a high-level interface for:
    1. Entity creation (agents register themselves on init)
    2. Relation creation (MASTERED_TASK when memory promoted)
    3. Observation storage (synthesized truths)
    4. Graph queries (search for related entities)

    Resilient Mode: If MCP is unavailable, logs warning but doesn't crash.
    All operations are thread-safe.

    Usage:
        bridge = GraphMemoryBridge.get_instance()
        bridge.create_agent_entity("GovernorAgent")
        bridge.create_mastered_task_relation("GovernorAgent", "task_hash_123")
    """

    _instance: GraphMemoryBridge | None = None
    _instance_lock = threading.RLock()
    RELATION_MASTERED_TASK = "MASTERED_TASK"
    RELATION_FAILED_TASK = "FAILED_TASK"
    RELATION_INTERACTS_WITH = "INTERACTS_WITH"
    RELATION_DEPENDS_ON = "DEPENDS_ON"
    RELATION_INHERITS_FROM = "INHERITS_FROM"

    @classmethod
    def get_instance(cls) -> GraphMemoryBridge:
        """Get the singleton instance of GraphMemoryBridge."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "GraphMemoryBridge.get_instance", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "GraphMemoryBridge.get_instance", "p0_governance")
        _emit_writes_through(str(uuid.uuid4()), "GraphMemoryBridge.get_instance", "L4_STATE")
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing only)."""
        with cls._instance_lock:
            cls._instance = None

    def __init__(self):
        """Initialize the Graph Memory Bridge."""
        self._lock = threading.RLock()
        self._mcp_available = False
        self._sqlite_store: Any = None
        self._create_entities_fn: Callable | None = None
        self._create_relations_fn: Callable | None = None
        self._add_observations_fn: Callable | None = None
        self._search_nodes_fn: Callable | None = None
        self.stats = {
            "entities_created": 0,
            "relations_created": 0,
            "observations_added": 0,
            "searches_performed": 0,
            "mcp_errors": 0,
            "operations_skipped": 0,
        }
        self._registered_entities: set[str] = set()
        self._init_mcp()

    def _init_mcp(self) -> None:
        """
        Detect live Memory MCP availability.

        Attempts to import the mcp11 module exposed by the Windsurf Memory MCP
        server.  Falls back to in-process ADGMCPClient stub when unavailable
        (CI / offline environments).
        """
        try:
            import importlib

            _mod = importlib.import_module("mcp11")
            self._mcp_module = _mod
            self._mcp_available = True
            Logger.info("[GraphMemoryBridge] Initialized (live mcp11 MCP mode)")
        except ImportError:
            self._mcp_module = None
            # mcp11 unavailable (CLI context) — wire SQLite store as persistent fallback
            if _SQLITE_STORE_AVAILABLE:
                import os
                from pathlib import Path as _Path

                _db_path = _Path(os.environ.get("MEMORY_DB", "artifacts/memory/knowledge_graph.sqlite"))
                try:
                    self._sqlite_store = _SqliteMemoryStore(_db_path)
                    self._mcp_available = True
                    Logger.info("[GraphMemoryBridge] Initialized (SQLite fallback mode) db=%s", _db_path)
                except Exception as _e:
                    self._sqlite_store = None
                    self._mcp_available = False
                    Logger.warning("[GraphMemoryBridge] SQLite store init failed: %s — no-op mode", _e)
            else:
                self._sqlite_store = None
                self._mcp_available = False
                Logger.info("[GraphMemoryBridge] mcp11 not importable, SQLite unavailable — no-op mode")

    def _call_mcp_create_entities(self, entities: list[dict]) -> Any:
        """Call mcp11_create_entities; falls back to injected fn, SQLite store, or in-memory stub."""
        if self._create_entities_fn is not None:
            return self._create_entities_fn(entities=entities)
        if self._mcp_module is not None:
            return self._mcp_module.create_entities(entities=entities)
        if self._sqlite_store is not None:
            return self._sqlite_store.create_entities(entities)
        if _FALLBACK_AVAILABLE:
            store = _MCPFallbackClient()
            for e in entities:
                store.upsert_entity(e["name"], e.get("entityType", "Entity"), e.get("observations"))
            return {"status": "ok", "source": "in-memory-stub"}
        return None

    def _call_mcp_create_relations(self, relations: list[dict]) -> Any:
        """Call mcp11_create_relations; falls back to injected fn, SQLite store, or None."""
        if self._create_relations_fn is not None:
            return self._create_relations_fn(relations=relations)
        if self._mcp_module is not None:
            return self._mcp_module.create_relations(relations=relations)
        if self._sqlite_store is not None:
            return self._sqlite_store.create_relations(relations)
        return None

    def _call_mcp_add_observations(self, observations: list[dict]) -> Any:
        """Call mcp11_add_observations; falls back to injected fn, SQLite store, or None."""
        if self._add_observations_fn is not None:
            return self._add_observations_fn(observations=observations)
        if self._mcp_module is not None:
            return self._mcp_module.add_observations(observations=observations)
        if self._sqlite_store is not None:
            return self._sqlite_store.add_observations(observations)
        return None

    def _call_mcp_search_nodes(self, query: str) -> Any:
        """Call mcp11_search_nodes; falls back to injected fn, SQLite store, or empty list."""
        if self._search_nodes_fn is not None:
            return self._search_nodes_fn(query=query)
        if self._mcp_module is not None:
            return self._mcp_module.search_nodes(query=query)
        if self._sqlite_store is not None:
            return self._sqlite_store.search_nodes(query)
        return []

    def set_mcp_functions(
        self,
        create_entities: Callable | None = None,
        create_relations: Callable | None = None,
        add_observations: Callable | None = None,
        search_nodes: Callable | None = None,
    ) -> None:
        """
        Inject MCP tool functions (for testing or custom implementations).

        Args:
            create_entities: Function matching mcp7_create_entities signature
            create_relations: Function matching mcp7_create_relations signature
            add_observations: Function matching mcp7_add_observations signature
            search_nodes: Function matching mcp7_search_nodes signature
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "GraphMemoryBridge.set_mcp_functions"
        )
        self._create_entities_fn = create_entities
        self._create_relations_fn = create_relations
        self._add_observations_fn = add_observations
        self._search_nodes_fn = search_nodes
        self._mcp_available = any([create_entities, create_relations, add_observations, search_nodes])
        Logger.debug("[GraphMemoryBridge] MCP functions injected")

    @property
    def is_available(self) -> bool:
        """Check if the Graph Memory Bridge is available."""
        return self._mcp_available

    def _safe_call(self, operation: str, fn: Callable | None, *args, **kwargs) -> Any | None:
        """
        Safely execute an MCP operation with error handling.

        Args:
            operation: Name of the operation for logging
            fn: The function to call
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Result of the operation or None if failed/unavailable
        """
        if not self._mcp_available:
            Logger.debug(f"[GraphMemoryBridge] Skipping {operation}: MCP unavailable")
            with self._lock:
                self.stats["operations_skipped"] += 1
            return None
        if fn is None:
            Logger.debug(f"[GraphMemoryBridge] Skipping {operation}: No function provided")
            with self._lock:
                self.stats["operations_skipped"] += 1
            return None
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            with self._lock:
                self.stats["mcp_errors"] += 1
            Logger.warning(f"[GraphMemoryBridge] {operation} failed: {e}")
            return None

    def create_agent_entity(
        self, agent_name: str, agent_type: str = "Agent", observations: list[str] | None = None
    ) -> bool:
        """
        Create an agent entity in the Knowledge Graph.

        Called automatically when an agent with MetaLearningMixin is instantiated.
        Idempotent: Will not create duplicate entities.

        Args:
            agent_name: Name of the agent (typically class name)
            agent_type: Type of entity (default: "Agent")
            observations: Initial observations about the agent

        Returns:
            True if created (or already exists), False if failed
        """
        if agent_name in self._registered_entities:
            Logger.debug(f"[GraphMemoryBridge] Entity already registered: {agent_name}")
            return True
        entities = [
            {
                "name": agent_name,
                "entityType": agent_type,
                "observations": observations or [f"Agent {agent_name} registered in Knowledge Graph"],
            }
        ]
        result = self._call_mcp_create_entities(entities)
        if result is not None or (self._create_entities_fn is None and self._mcp_module is None):
            self._registered_entities.add(agent_name)
            with self._lock:
                self.stats["entities_created"] += 1
            Logger.debug(f"[GraphMemoryBridge] Entity created: {agent_name}")
            return True
        return False

    def create_mastered_task_relation(
        self, agent_name: str, task_description: str, feedback_score: float
    ) -> bool:
        """
        Create a MASTERED_TASK relation when memory is promoted to Long-Term DNA.

        This is called when a memory's feedback_score >= 0.8 (promotion threshold).

        Args:
            agent_name: Name of the agent that mastered the task
            task_description: Description of the task (will be hashed)
            feedback_score: The feedback score that triggered promotion

        Returns:
            True if relation created, False if failed
        """
        task_hash = hashlib.sha256(task_description.encode()).hexdigest()[:16]
        task_entity_name = f"Task_{task_hash}"
        task_entities = [
            {
                "name": task_entity_name,
                "entityType": "Task",
                "observations": [
                    f"Task mastered by {agent_name} with score {feedback_score:.2f}",
                    f"Description hash: {task_hash}",
                ],
            }
        ]
        self._call_mcp_create_entities(task_entities)
        relations = [
            {"from": agent_name, "to": task_entity_name, "relationType": self.RELATION_MASTERED_TASK}
        ]
        result = self._call_mcp_create_relations(relations)
        if result is not None or (self._create_relations_fn is None and self._mcp_module is None):
            with self._lock:
                self.stats["relations_created"] += 1
            Logger.info(
                f"[GraphMemoryBridge] MASTERED_TASK relation created: {agent_name} -> {task_entity_name}"
            )
            return True
        return False

    def create_relation(self, from_entity: str, to_entity: str, relation_type: str) -> bool:
        """
        Create a generic relation between two entities.

        Args:
            from_entity: Source entity name
            to_entity: Target entity name
            relation_type: Type of relation

        Returns:
            True if created, False if failed
        """
        relations = [{"from": from_entity, "to": to_entity, "relationType": relation_type}]
        result = self._call_mcp_create_relations(relations)
        if result is not None or (self._create_relations_fn is None and self._mcp_module is None):
            with self._lock:
                self.stats["relations_created"] += 1
            return True
        return False

    def add_observation(self, entity_name: str, observation: str) -> bool:
        """
        Add an observation to an existing entity.

        Enforces 4KB limit on observation size to prevent graph bloat.

        Args:
            entity_name: Name of the entity
            observation: The observation to add

        Returns:
            True if added, False if failed
        """
        if len(observation) > 4096:
            observation = observation[:4093] + "..."
        observations = [{"entityName": entity_name, "contents": [observation]}]
        result = self._call_mcp_add_observations(observations)
        if result is not None or (self._add_observations_fn is None and self._mcp_module is None):
            with self._lock:
                self.stats["observations_added"] += 1
            return True
        return False

    def search_entities(self, query: str) -> list[dict[str, Any]]:
        """
        Search for entities in the Knowledge Graph.

        Args:
            query: Search query string

        Returns:
            List of matching entities (empty if failed or unavailable)
        """
        result = self._call_mcp_search_nodes(query)
        with self._lock:
            self.stats["searches_performed"] += 1
        if result is not None:
            return result if isinstance(result, list) else []
        return []

    def get_statistics(self) -> dict[str, Any]:
        """Get bridge statistics."""
        with self._lock:
            return {
                **self.stats,
                "mcp_available": self._mcp_available,
                "registered_entities": len(self._registered_entities),
            }
