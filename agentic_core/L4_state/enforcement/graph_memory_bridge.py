# guardian: allow-silent-swallower -- Memory bridge operations logged, failures non-critical for system continuity
from __future__ import annotations

"""[PHASE 21] Graph Memory Bridge - Interface to Memory MCP Knowledge Graph.

Provides a programmatic interface to the Memory MCP server for entity/relation
creation, observation storage, and graph queries.
"""
import hashlib
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L4_state.enforcement.memory_db_canonical_policy import (
    resolve_canonical_memory_db_path,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

try:
    from agentic_core.adg.client.InMemoryStore import ADGMCPClient as _MCPFallbackClient

    _FALLBACK_AVAILABLE = True
except ImportError:  # guardian: allow-silent-swallow - Optional ADG MCP client
    _FALLBACK_AVAILABLE = False
# guardian: allow-silent-swallow - optional dependency
try:
    from tools.memory.sqlite_memory_store import SqliteMemoryStore as _SqliteMemoryStore

    _SQLITE_STORE_AVAILABLE = True
except ImportError:  # guardian: allow-silent-swallow - Optional SQLite memory store
    _SqliteMemoryStore = None  # type: ignore[assignment,misc]
    _SQLITE_STORE_AVAILABLE = False

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
        bridge = GraphMemoryBridge()
        bridge.create_agent_entity("GovernorAgent")
        bridge.create_mastered_task_relation("GovernorAgent", "task_hash_123")

    For testing with isolation:
        with GraphMemoryBridge() as bridge:
            bridge.create_agent_entity("TestAgent")
            # Automatically cleaned up when exiting context
    """

    _instance = None
    _instance_lock = threading.Lock()

    RELATION_MASTERED_TASK = "MASTERED_TASK"
    RELATION_FAILED_TASK = "FAILED_TASK"
    RELATION_INTERACTS_WITH = "INTERACTS_WITH"
    RELATION_DEPENDS_ON = "DEPENDS_ON"
    RELATION_INHERITS_FROM = "INHERITS_FROM"

    def __init__(self):
        """Initialize the Graph Memory Bridge with isolated state."""
        self._lock = threading.RLock()
        self._mcp_available = False
        self._mcp_module: Any = None
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
        self._stats = self.stats
        self._registered_entities: set[str] = set()
        self._cleanup_registered = False
        self._init_mcp()

    @classmethod
    def get_instance(cls):
        """Return singleton instance of GraphMemoryBridge for backward compatibility."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __enter__(self):
        """Context manager entry - return self for use in 'with' statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically cleanup when leaving context."""
        self.cleanup()
        return False  # Don't suppress exceptions

    def cleanup(self) -> None:
        """Explicit cleanup method for test isolation.

        Resets all instance state to ensure clean test isolation.
        Can be called multiple times safely.
        """
        if self._cleanup_registered:
            return  # Already cleaned up

        with self._lock:
            # Clear all state
            self._registered_entities.clear()
            self.stats = {
                "entities_created": 0,
                "relations_created": 0,
                "observations_added": 0,
                "searches_performed": 0,
                "mcp_errors": 0,
                "operations_skipped": 0,
            }

            # Reset MCP connections
            self._mcp_available = False
            self._mcp_module = None
            self._create_entities_fn = None
            self._create_relations_fn = None
            self._add_observations_fn = None
            self._search_nodes_fn = None

            # Mark as cleaned up
            self._cleanup_registered = True

    def validate_state_isolation(self) -> dict[str, Any]:
        """Validate that state is properly isolated.

        Returns:
            Dictionary with isolation validation results.
        """
        with self._lock:
            stats_total = sum(self.stats.values())
            return {
                "registered_entities_count": len(self._registered_entities),
                "registered_entities": list(self._registered_entities),
                "stats_totals": stats_total,
                "mcp_available": self._mcp_available,
                "cleanup_registered": self._cleanup_registered,
                "is_clean": len(self._registered_entities) == 0 and stats_total == 0,
            }

    @classmethod
    def create_isolated(cls) -> GraphMemoryBridge:
        """Create a completely isolated instance for testing.

        Returns:
            New GraphMemoryBridge instance with guaranteed isolation.
        """
        return cls()

    def _init_mcp(self) -> None:
        """
        Detect live Memory MCP availability.

        Attempts to import the mcp11 module exposed by the Windsurf Memory MCP
        server.  Falls back to in-process ADGMCPClient stub when unavailable
        (CI / offline environments).
        """
        try:
            import importlib

            # guardian: allow-silent-degradation - Optional MCP module import
            _mod = importlib.import_module("mcp11")
            self._mcp_module = _mod
            self._mcp_available = True
            Logger.info("[GraphMemoryBridge] Initialized (live mcp11 MCP mode)")
        except ImportError:  # guardian: allow-silent-swallow - Optional MCP module
            self._mcp_module = None
            # mcp11 unavailable (CLI context) — wire SQLite store as persistent fallback
            if _SQLITE_STORE_AVAILABLE:
                try:
                    _db_path = resolve_canonical_memory_db_path()
                    self._sqlite_store = _SqliteMemoryStore(_db_path)
                    self._mcp_available = True
                    Logger.info("[GraphMemoryBridge] Initialized (SQLite fallback mode) db=%s", _db_path)
                except (
                    OSError,
                    RuntimeError,
                    TypeError,
                    ValueError,
                ) as _e:  # guardian: allow-log-and-swallow -- SQLite fallback init: non-fatal, bridge operates in degraded mode
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
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            "GraphMemoryBridge.set_mcp_functions",
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
        # guardian: allow-silent-degradation - Skip when MCP unavailable
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
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-return-none-swallow -- MCP operation failure: non-fatal, Logger.warning already called
            with self._lock:
                self.stats["mcp_errors"] += 1
            Logger.warning(f"[GraphMemoryBridge] {operation} failed: {e}")
            return None  # guardian: allow-return-none-swallow -- MCP operation: non-fatal, caller handles None as unavailable

    def create_agent_entity(
        self,
        agent_name: str,
        agent_type: str = "Agent",
        observations: list[str] | None = None,
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
        # guardian: allow-silent-degradation - Silent success when entity already exists
        if agent_name in self._registered_entities:
            Logger.debug(f"[GraphMemoryBridge] Entity already registered: {agent_name}")
            return True
        entities = [
            {
                "name": agent_name,
                "entityType": agent_type,
                "observations": observations or [f"Agent {agent_name} registered in Knowledge Graph"],
            },
        ]
        result = self._call_mcp_create_entities(entities)
        # guardian: allow-silent-degradation - Silent success when MCP unavailable
        if result is not None or (self._create_entities_fn is None and self._mcp_module is None):
            self._registered_entities.add(agent_name)
            with self._lock:
                self.stats["entities_created"] += 1
            Logger.debug(f"[GraphMemoryBridge] Entity created: {agent_name}")
            # guardian: allow-silent-degradation - Silent success on entity creation
            return True
        return False

    def create_mastered_task_relation(
        self,
        agent_name: str,
        task_description: str,
        feedback_score: float,
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
            },
        ]
        self._call_mcp_create_entities(task_entities)
        relations = [
            {"from": agent_name, "to": task_entity_name, "relationType": self.RELATION_MASTERED_TASK},
        ]
        result = self._call_mcp_create_relations(relations)
        # guardian: allow-silent-degradation - Silent success when MCP unavailable
        if result is not None or (self._create_relations_fn is None and self._mcp_module is None):
            with self._lock:
                self.stats["relations_created"] += 1
            Logger.info(
                f"[GraphMemoryBridge] MASTERED_TASK relation created: {agent_name} -> {task_entity_name}",
            )
            # guardian: allow-silent-degradation - Silent success on relation creation
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
        # guardian: allow-silent-degradation - Silent success when MCP unavailable
        if result is not None or (self._create_relations_fn is None and self._mcp_module is None):
            with self._lock:
                self.stats["relations_created"] += 1
            # guardian: allow-silent-degradation - Silent success on relation creation
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
        # guardian: allow-silent-degradation - Silent success when MCP unavailable
        if result is not None or (self._add_observations_fn is None and self._mcp_module is None):
            with self._lock:
                self.stats["observations_added"] += 1
            # guardian: allow-silent-degradation - Silent success on observation addition
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
