from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
[PHASE 21] Graph Memory Bridge - Interface to Memory MCP Knowledge Graph.

Provides a programmatic interface to the Memory MCP server for:
- Entity creation (agents, tasks, protocols)
- Relation creation (MASTERED_TASK, INTERACTS_WITH, etc.)
- Observation storage
- Graph queries

This bridge uses the MCP tools:
- mcp7_create_entities: Create entities in the knowledge graph
- mcp7_create_relations: Create relations between entities
- mcp7_add_observations: Add observations to entities
- mcp7_search_nodes: Search for nodes in the graph

Resilient Mode: If MCP is unavailable, operations are logged but don't crash.

[SSOT] This is the canonical interface for Memory MCP operations.
"""


import hashlib
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

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

    # Relation types for DNA mapping
    RELATION_MASTERED_TASK = "MASTERED_TASK"
    RELATION_FAILED_TASK = "FAILED_TASK"
    RELATION_INTERACTS_WITH = "INTERACTS_WITH"
    RELATION_DEPENDS_ON = "DEPENDS_ON"
    RELATION_INHERITS_FROM = "INHERITS_FROM"

    @classmethod
    def get_instance(cls) -> GraphMemoryBridge:
        """Get the singleton instance of GraphMemoryBridge."""
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

        # MCP tool functions (injected or mocked)
        self._create_entities_fn: Callable | None = None
        self._create_relations_fn: Callable | None = None
        self._add_observations_fn: Callable | None = None
        self._search_nodes_fn: Callable | None = None

        # Statistics
        self.stats = {
            "entities_created": 0,
            "relations_created": 0,
            "observations_added": 0,
            "searches_performed": 0,
            "mcp_errors": 0,
            "operations_skipped": 0,
        }

        # Registered entities cache (to avoid duplicate registrations)
        self._registered_entities: set[str] = set()

        # Try to initialize MCP connection
        self._init_mcp()

    def _init_mcp(self) -> None:
        """
        Initialize connection to Memory MCP server.

        In production, this would connect to the actual MCP server.
        For testing, mock functions can be injected via set_mcp_functions().
        """
        try:
            # Check if MCP tools are available
            # In Windsurf/Cascade, MCP tools are available via the tool calling interface
            # This bridge provides a programmatic wrapper for agent code

            # Default: assume MCP is available (will fail gracefully if not)
            self._mcp_available = True
            Logger.info("[GraphMemoryBridge] Initialized (MCP mode)")
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self._mcp_available = False
            Logger.warning(f"[GraphMemoryBridge] MCP unavailable: {e}")

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
        self._create_entities_fn = create_entities
        self._create_relations_fn = create_relations
        self._add_observations_fn = add_observations
        self._search_nodes_fn = search_nodes

        # Mark as available if any function is provided
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
        # Check if already registered (idempotent)
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

        result = self._safe_call(
            "create_entities",
            self._create_entities_fn,
            entities=entities,
        )

        if result is not None or self._create_entities_fn is None:
            # Mark as registered even if MCP unavailable (to prevent repeated attempts)
            self._registered_entities.add(agent_name)
            with self._lock:
                self.stats["entities_created"] += 1
            Logger.debug(f"[GraphMemoryBridge] Entity created: {agent_name}")
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
        # Hash the task description for the entity name
        task_hash = hashlib.sha256(task_description.encode()).hexdigest()[:16]
        task_entity_name = f"Task_{task_hash}"

        # First, ensure the task entity exists
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

        self._safe_call(
            "create_task_entity",
            self._create_entities_fn,
            entities=task_entities,
        )

        # Create the MASTERED_TASK relation
        relations = [
            {
                "from": agent_name,
                "to": task_entity_name,
                "relationType": self.RELATION_MASTERED_TASK,
            },
        ]

        result = self._safe_call(
            "create_relations",
            self._create_relations_fn,
            relations=relations,
        )

        if result is not None or self._create_relations_fn is None:
            with self._lock:
                self.stats["relations_created"] += 1
            Logger.info(
                f"[GraphMemoryBridge] MASTERED_TASK relation created: {agent_name} -> {task_entity_name}",
            )
            return True

        return False

    def create_relation(
        self,
        from_entity: str,
        to_entity: str,
        relation_type: str,
    ) -> bool:
        """
        Create a generic relation between two entities.

        Args:
            from_entity: Source entity name
            to_entity: Target entity name
            relation_type: Type of relation

        Returns:
            True if created, False if failed
        """
        relations = [
            {
                "from": from_entity,
                "to": to_entity,
                "relationType": relation_type,
            },
        ]

        result = self._safe_call(
            "create_relations",
            self._create_relations_fn,
            relations=relations,
        )

        if result is not None or self._create_relations_fn is None:
            with self._lock:
                self.stats["relations_created"] += 1
            return True

        return False

    def add_observation(
        self,
        entity_name: str,
        observation: str,
    ) -> bool:
        """
        Add an observation to an existing entity.

        Enforces 4KB limit on observation size to prevent graph bloat.

        Args:
            entity_name: Name of the entity
            observation: The observation to add

        Returns:
            True if added, False if failed
        """
        # Truncate observation if too large (4KB safety limit)
        if len(observation) > 4096:
            observation = observation[:4093] + "..."

        observations = [
            {
                "entityName": entity_name,
                "contents": [observation],
            },
        ]

        result = self._safe_call(
            "add_observations",
            self._add_observations_fn,
            observations=observations,
        )

        if result is not None or self._add_observations_fn is None:
            with self._lock:
                self.stats["observations_added"] += 1
            return True

        return False

    def search_entities(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search for entities in the Knowledge Graph.

        Args:
            query: Search query string

        Returns:
            List of matching entities (empty if failed or unavailable)
        """
        result = self._safe_call(
            "search_nodes",
            self._search_nodes_fn,
            query=query,
        )

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
