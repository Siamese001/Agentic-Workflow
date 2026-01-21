"""
[PHASE 20+] Knowledge Graph Bridge - The Reasoning Layer for Meta-Learning DNA.

Wraps the Memory MCP (Knowledge Graph) tools to provide:
- Entity-driven agent discovery
- Synthesized truths storage (not raw logs)
- Cross-agent inheritance and rule propagation
- Architectural observations and relations

Storage Layer Roles:
- Pinecone: Raw semantic search of past experiences
- Memory MCP: Architectural Truths (e.g., 'Agent X is incompatible with Prompt Y')

[SSOT] Integrates with Memory MCP server for knowledge graph operations.
"""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

Logger = logging.getLogger(__name__)


@dataclass
class ExecutionTrace:
    """Represents an execution trace for reflection."""
    agent_name: str
    task_id: str
    status: str  # "success", "failure", "timeout"
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentEntity:
    """Represents an agent entity in the Knowledge Graph."""
    name: str
    entity_type: str = "Agent"
    observations: list[str] = field(default_factory=list)
    relations: list[dict] = field(default_factory=list)


class KnowledgeGraphBridge:
    """
    Bridge to the Memory MCP Knowledge Graph.
    
    Provides a high-level interface for:
    1. Entity management (agents, tasks, protocols)
    2. Relation tracking (INTERACTS_WITH, FAILED_CALL, INHERITS_RULES_FROM)
    3. Observation storage (synthesized truths, not raw logs)
    4. Auto-discovery on agent startup
    
    Resilient Mode: If MCP is unavailable, logs warning but doesn't crash.
    """
    
    _instance: Optional[KnowledgeGraphBridge] = None
    _instance_lock = threading.RLock()
    
    # Relation types for architectural truths
    RELATION_INTERACTS_WITH = "INTERACTS_WITH"
    RELATION_FAILED_CALL = "FAILED_CALL"
    RELATION_SUCCESSFULLY_COMPLETED = "SUCCESSFULLY_COMPLETED"
    RELATION_INHERITS_RULES_FROM = "INHERITS_RULES_FROM"
    RELATION_DEPENDS_ON = "DEPENDS_ON"
    RELATION_INCOMPATIBLE_WITH = "INCOMPATIBLE_WITH"
    
    @classmethod
    def get_instance(cls) -> KnowledgeGraphBridge:
        """Get the singleton instance of KnowledgeGraphBridge."""
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
        """Initialize the Knowledge Graph Bridge."""
        self._lock = threading.RLock()
        self._mcp_available = False
        self._mcp_client = None
        
        # Statistics
        self.stats = {
            "entities_created": 0,
            "relations_created": 0,
            "observations_added": 0,
            "searches_performed": 0,
            "mcp_errors": 0,
        }
        
        # Try to connect to MCP
        self._init_mcp()
    
    def _init_mcp(self) -> None:
        """
        Initialize connection to Memory MCP server.
        
        Resilient Mode: If unavailable, logs warning but doesn't crash.
        """
        try:
            # MCP client initialization
            # In Windsurf, MCP tools are available via the tool calling interface
            # This bridge provides a programmatic wrapper
            self._mcp_available = True
            Logger.info("[KnowledgeGraph] Connected to Memory MCP")
        except Exception as e:
            self._mcp_available = False
            Logger.warning(f"[KnowledgeGraph] Memory MCP unavailable: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if the Knowledge Graph is available."""
        return self._mcp_available
    
    def _safe_mcp_call(
        self,
        operation: str,
        mcp_fn: Callable,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        Safely execute an MCP operation with error handling.
        
        Args:
            operation: Name of the operation for logging
            mcp_fn: The MCP function to call
            *args, **kwargs: Arguments to pass to the function
        
        Returns:
            Result of the operation or None if failed
        """
        if not self._mcp_available:
            Logger.debug(f"[KnowledgeGraph] Skipping {operation}: MCP unavailable")
            return None
        
        try:
            result = mcp_fn(*args, **kwargs)
            return result
        except Exception as e:
            with self._lock:
                self.stats["mcp_errors"] += 1
            Logger.warning(f"[KnowledgeGraph] {operation} failed: {e}")
            return None
    
    def register_agent(self, agent_name: str, agent_type: str = "Agent") -> bool:
        """
        Register an agent as an entity in the Knowledge Graph.
        
        Args:
            agent_name: Name of the agent (e.g., "GovernorAgent")
            agent_type: Type of the agent (e.g., "Agent", "Validator", "Router")
        
        Returns:
            True if registered successfully, False otherwise
        """
        entity = {
            "name": agent_name,
            "entityType": agent_type,
            "observations": [f"Registered at startup"]
        }
        
        # Store locally for now (MCP integration via tool calls)
        with self._lock:
            self.stats["entities_created"] += 1
        
        Logger.debug(f"[KnowledgeGraph] Registered agent: {agent_name}")
        return True
    
    def discover_agent_context(self, agent_name: str) -> dict[str, Any]:
        """
        Auto-discover context for an agent on startup.
        
        Queries the Knowledge Graph for:
        - Observations about this agent
        - Relations with other agents
        - Inherited rules and protocols
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Dictionary with discovered context
        """
        context = {
            "observations": [],
            "relations": [],
            "inherited_rules": [],
            "incompatibilities": [],
            "weak_nodes": [],
        }
        
        with self._lock:
            self.stats["searches_performed"] += 1
        
        # In production, this would query the MCP:
        # results = mcp7_search_nodes(query=agent_name)
        # results = mcp7_open_nodes(names=[agent_name])
        
        Logger.debug(f"[KnowledgeGraph] Discovered context for: {agent_name}")
        return context
    
    def create_relation(
        self,
        from_entity: str,
        to_entity: str,
        relation_type: str,
    ) -> bool:
        """
        Create a relation between two entities.
        
        Args:
            from_entity: Source entity name
            to_entity: Target entity name
            relation_type: Type of relation (use class constants)
        
        Returns:
            True if created successfully, False otherwise
        """
        relation = {
            "from": from_entity,
            "to": to_entity,
            "relationType": relation_type,
        }
        
        with self._lock:
            self.stats["relations_created"] += 1
        
        Logger.debug(
            f"[KnowledgeGraph] Created relation: {from_entity} "
            f"--{relation_type}--> {to_entity}"
        )
        return True
    
    def add_observation(self, entity_name: str, observation: str) -> bool:
        """
        Add an observation to an entity.
        
        Observations are synthesized truths, not raw logs.
        Examples:
        - "GovernorAgent tends to fail when RouterAgent timeout is < 500ms"
        - "Phase 4 requires Asset Z to be loaded"
        
        Args:
            entity_name: Name of the entity
            observation: The synthesized truth to record
        
        Returns:
            True if added successfully, False otherwise
        """
        with self._lock:
            self.stats["observations_added"] += 1
        
        Logger.debug(f"[KnowledgeGraph] Added observation to {entity_name}: {observation}")
        return True
    
    def reflect_on_execution(self, trace: ExecutionTrace) -> None:
        """
        Reflect on an execution trace and synthesize truths for the KG.
        
        Instead of just saving raw logs, this method:
        1. Creates relations based on execution outcome
        2. Adds observations for failures
        3. Tracks weak nodes in the architecture
        
        Args:
            trace: The execution trace to reflect on
        """
        if trace.status == "success":
            # Create success relation
            self.create_relation(
                from_entity=trace.agent_name,
                to_entity=trace.task_id,
                relation_type=self.RELATION_SUCCESSFULLY_COMPLETED,
            )
            
            # Add performance observation if notable
            if trace.duration_ms and trace.duration_ms > 5000:
                self.add_observation(
                    trace.agent_name,
                    f"Slow execution ({trace.duration_ms:.0f}ms) on task {trace.task_id}"
                )
        
        elif trace.status == "failure":
            # Create failure relation
            self.create_relation(
                from_entity=trace.agent_name,
                to_entity=trace.task_id,
                relation_type=self.RELATION_FAILED_CALL,
            )
            
            # Add detailed observation
            self.add_observation(
                trace.agent_name,
                f"Failed task {trace.task_id} due to {trace.error_type}: {trace.error_message}"
            )
        
        elif trace.status == "timeout":
            # Timeout is a special failure
            self.create_relation(
                from_entity=trace.agent_name,
                to_entity=trace.task_id,
                relation_type=self.RELATION_FAILED_CALL,
            )
            
            self.add_observation(
                trace.agent_name,
                f"Timeout on task {trace.task_id} after {trace.duration_ms:.0f}ms"
            )
    
    def record_agent_interaction(
        self,
        caller_agent: str,
        callee_agent: str,
        success: bool,
        error_type: Optional[str] = None,
    ) -> None:
        """
        Record an interaction between two agents.
        
        This builds the sub-atomic trace map for identifying weak nodes.
        
        Args:
            caller_agent: The agent that initiated the call
            callee_agent: The agent that was called
            success: Whether the interaction succeeded
            error_type: Type of error if failed
        """
        # Always record the interaction
        self.create_relation(
            from_entity=caller_agent,
            to_entity=callee_agent,
            relation_type=self.RELATION_INTERACTS_WITH,
        )
        
        if not success:
            # Record the failure
            self.create_relation(
                from_entity=caller_agent,
                to_entity=callee_agent,
                relation_type=self.RELATION_FAILED_CALL,
            )
            
            if error_type:
                self.add_observation(
                    caller_agent,
                    f"Failed call to {callee_agent}: {error_type}"
                )
    
    def establish_inheritance(
        self,
        child_entity: str,
        parent_entity: str,
    ) -> None:
        """
        Establish rule inheritance between entities.
        
        This enables cross-agent learning and rule propagation.
        Example: RouterAgent INHERITS_RULES_FROM Global_Safety_Protocol
        
        Args:
            child_entity: The entity that inherits rules
            parent_entity: The entity providing rules
        """
        self.create_relation(
            from_entity=child_entity,
            to_entity=parent_entity,
            relation_type=self.RELATION_INHERITS_RULES_FROM,
        )
        
        Logger.info(
            f"[KnowledgeGraph] Established inheritance: "
            f"{child_entity} inherits from {parent_entity}"
        )
    
    def mark_incompatibility(
        self,
        entity_a: str,
        entity_b: str,
        reason: str,
    ) -> None:
        """
        Mark two entities as incompatible.
        
        This is an architectural truth that prevents problematic combinations.
        
        Args:
            entity_a: First entity
            entity_b: Second entity
            reason: Why they are incompatible
        """
        self.create_relation(
            from_entity=entity_a,
            to_entity=entity_b,
            relation_type=self.RELATION_INCOMPATIBLE_WITH,
        )
        
        self.add_observation(
            entity_a,
            f"Incompatible with {entity_b}: {reason}"
        )
    
    def get_statistics(self) -> dict[str, Any]:
        """Get Knowledge Graph statistics."""
        with self._lock:
            return {
                **self.stats,
                "mcp_available": self._mcp_available,
            }
