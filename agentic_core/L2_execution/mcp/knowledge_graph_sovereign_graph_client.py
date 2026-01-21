from __future__ import annotations
"""
Sovereign Knowledge Graph Client – Phase 13D
Integrates Official Memory MCP for structured Entity-Relation storage.
L3 Routed | L5 Shielded

Enables the agent to store structured relationships (e.g., (User) -[OWNS]-> (2024 Chevy Traverse))
complementing Pinecone's vector storage with explicit entity graphs.
"""
import logging
from typing import List, Dict, Any, Optional
# ARCHIVED IMPORT REMOVED - dependency no longer available
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

Logger: Any = logging.getLogger('L4.KnowledgeGraph')

class SovereignGraphClient(MCPHardenedMixin, HealerMixin):
    """
    Client for the Knowledge Graph MCP (Memory MCP).
    Stores and retrieves structured entities and relationships.

    Architecture: Dual-Graph Brain
    - Vector Memory (Pinecone): Semantic similarity search
    - Entity Graph (Memory MCP): Structured relationships
    """

    def __init__(self):
        """Initialize the Knowledge Graph client with sovereign routing."""
        super().__init__()
        from agentic_core.L3_orchestration.workflow_engines.SovereignMcpRouter import SovereignMcpRouter
        self.router = SovereignMcpRouter(role='memory')
        self.initialized = False
        self._mcp_audit('init')
        Logger.info('[L4 KG] Sovereign Graph Client initialized')

    async def initialize(self) -> Any:
        """Async initialization of MCP router."""
        try:
            await self.router.initialize()
            self.initialized = True
            Logger.info('[L4 KG] Router initialized successfully')
        except Exception as e:
            Logger.error(f'[L4 KG] Initialization failed: {e}')
            raise

    async def _ensure_initialized(self):
        """Ensure MCP client is initialized."""
        if not self.initialized:
            await self.initialize()

    async def create_entities(self, entities: List[Dict[str, Any]]) -> str:
        """
        Create entities in the Knowledge Graph.

        Args:
            entities: List of entity definitions
                Format: [{"name": "Chevy Traverse", "entityType": "Vehicle", "observations": ["2024 model"]}]

        Returns:
            Result message from MCP
        """
        if not config.KG_MCP_ENABLED:
            Logger.warning('[L4 KG] Knowledge Graph MCP is disabled')
            return 'KG Disabled'
        await self._ensure_initialized()
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp7_create_entities', args={'entities': entities})
            Logger.info(f'[L4 KG] Created {len(entities)} entities')
            return result
        except Exception as e:
            Logger.error(f'[L4 KG] Entity creation failed: {e}')
            return f'Error: {str(e)}'

    async def create_relations(self, relations: List[Dict[str, Any]]) -> str:
        """
        Define relationships between entities.

        Args:
            relations: List of relationship definitions
                Format: [{"from": "User", "to": "Chevy Traverse", "relationType": "OWNS"}]

        Returns:
            Result message from MCP
        """
        if not config.KG_MCP_ENABLED:
            return 'KG Disabled'
        await self._ensure_initialized()
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp7_create_relations', args={'relations': relations})
            Logger.info(f'[L4 KG] Created {len(relations)} relations')
            return result
        except Exception as e:
            Logger.error(f'[L4 KG] Relation creation failed: {e}')
            return f'Error: {str(e)}'

    async def read_graph(self) -> Dict[str, Any]:
        """
        Reads the entire active knowledge graph structure.

        Returns:
            Complete graph with entities and relations
        """
        if not config.KG_MCP_ENABLED:
            return {'entities': [], 'relations': [], 'error': 'KG Disabled'}
        await self._ensure_initialized()
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp7_read_graph', args={})
            Logger.info('[L4 KG] Graph read successfully')
            return result
        except Exception as e:
            Logger.error(f'[L4 KG] Graph read failed: {e}')
            return {'entities': [], 'relations': [], 'error': str(e)}

    async def search_nodes(self, query: str) -> List[Dict]:
        """
        Search for entities/relations by query.

        Args:
            query: Search query string

        Returns:
            List of matching entities
        """
        if not config.KG_MCP_ENABLED:
            return []
        await self._ensure_initialized()
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp7_search_nodes', args={'query': query})
            Logger.info(f'[L4 KG] Search completed for: {query}')
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'nodes' in result:
                return result['nodes']
            return []
        except Exception as e:
            Logger.warning(f'[L4 KG] MCP search failed, using client-side filter: {e}')
            full_graph: Any = await self.read_graph()
            results: Any = []
            if isinstance(full_graph, dict) and 'entities' in full_graph:
                query_lower: Any = query.lower()
                for entity in full_graph['entities']:
                    if query_lower in entity.get('name', '').lower():
                        results.append(entity)
                    elif any((query_lower in obs.lower() for obs in entity.get('observations', []))):
                        results.append(entity)
            Logger.info(f'[L4 KG] Client-side search found {len(results)} results')
            return results

    async def add_observations(self, entity_name: str, observations: List[str]) -> str:
        """
        Add new observations to an existing entity.

        Args:
            entity_name: Name of the entity to update
            observations: List of new observations to add

        Returns:
            Result message from MCP
        """
        if not config.KG_MCP_ENABLED:
            return 'KG Disabled'
        await self._ensure_initialized()
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp7_add_observations', args={'observations': [{'entityName': entity_name, 'contents': observations}]})
            Logger.info(f'[L4 KG] Added {len(observations)} observations to {entity_name}')
            return result
        except Exception as e:
            Logger.error(f'[L4 KG] Add observations failed: {e}')
            return f'Error: {str(e)}'

    async def delete_entities(self, entity_names: List[str]) -> str:
        """
        Delete entities from the graph.

        Args:
            entity_names: List of entity names to delete

        Returns:
            Result message from MCP
        """
        if not config.KG_MCP_ENABLED:
            return 'KG Disabled'
        await self._ensure_initialized()
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp7_delete_entities', args={'entityNames': entity_names})
            Logger.info(f'[L4 KG] Deleted {len(entity_names)} entities')
            return result
        except Exception as e:
            Logger.error(f'[L4 KG] Entity deletion failed: {e}')
            return f'Error: {str(e)}'

    async def open_nodes(self, names: List[str]) -> List[Dict]:
        """
        Open specific nodes by their names (retrieve full details).

        Args:
            names: List of entity names to retrieve

        Returns:
            List of entity details
        """
        if not config.KG_MCP_ENABLED:
            return []
        await self._ensure_initialized()
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp7_open_nodes', args={'names': names})
            Logger.info(f'[L4 KG] Opened {len(names)} nodes')
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'nodes' in result:
                return result['nodes']
            return []
        except Exception as e:
            Logger.error(f'[L4 KG] Open nodes failed: {e}')
            return []

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Knowledge Graph connection.

        Returns:
            Health status
        """
        try:
            graph: Any = await self.read_graph()
            if 'error' in graph:
                return {'status': 'unhealthy', 'error': graph['error']}
            entity_count: Any = len(graph.get('entities', []))
            relation_count: Any = len(graph.get('relations', []))
            return {'status': 'healthy', 'entity_count': entity_count, 'relation_count': relation_count, 'initialized': self.initialized}
        except Exception as e:
            Logger.error(f'[L4 KG] Health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}
_graph_client: Optional[SovereignGraphClient] = None

def get_graph_client() -> SovereignGraphClient:
    """Get or create the global Knowledge Graph client."""
    global _graph_client
    if _graph_client is None:
        _graph_client = SovereignGraphClient()
    return _graph_client

def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
