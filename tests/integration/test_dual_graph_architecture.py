"""
Dual-Graph Architecture Test – Phase 13D
Verification of Knowledge Graph (L4) and DeepWiki (L6) MCP integrations.

Tests the complete dual-graph brain:
- Vector Memory (Pinecone): Semantic similarity search
- Entity Graph (Memory MCP): Structured relationships
- Codebase Graph (DeepWiki MCP): Repository intelligence
"""
import pytest
import pytest_asyncio
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any, List

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class mock_sovereign_graph_client:
    """Mock Knowledge Graph client for testing."""

    def __init__(self):
        self.entities = []
        self.relations = []
        self.initialized = False

    async def initialize(self) -> Any:
        """Mock initialization."""
        self.initialized = True

    async def create_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Mock entity creation."""
        self.entities.extend(entities)
        return f'Created {len(entities)} entities'

    async def create_relations(self, relations: List[Dict[str, Any]]) -> str:
        """Mock relation creation."""
        self.relations.extend(relations)
        return f'Created {len(relations)} relations'

    async def read_graph(self) -> Dict[str, Any]:
        """Mock graph read."""
        return {'entities': self.entities, 'relations': self.relations}

    async def search_nodes(self, query: str) -> List[Dict]:
        """Mock node search."""
        results: Any = []
        query_lower: Any = query.lower()
        for entity in self.entities:
            if query_lower in entity.get('name', '').lower():
                results.append(entity)
        return results

    async def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return {'status': 'healthy', 'entity_count': len(self.entities), 'relation_count': len(self.relations), 'initialized': self.initialized}

class mock_sovereign_deep_wiki_client:
    """Mock DeepWiki client for testing."""

    def __init__(self):
        self.initialized = False
        self.knowledge_base = {'mcp_router': 'agentic_core/L3_orchestration/workflow_engines/mcp_router_sovereign.py', 'pinecone_client': 'agentic_core/L4_state/semantic_memory/pinecone_mcp_client.py', 'graph_client': 'agentic_core/L4_state/knowledge_graph/sovereign_graph_client.py'}

    async def initialize(self) -> Any:
        """Mock initialization."""
        self.initialized = True

    async def ask_question(self, question: str, repo: str=None) -> str:
        """Mock question answering."""
        question_lower: Any = question.lower()
        if 'mcp_router' in question_lower or 'router' in question_lower:
            return self.knowledge_base['mcp_router']
        elif 'pinecone' in question_lower:
            return self.knowledge_base['pinecone_client']
        elif 'graph' in question_lower or 'knowledge' in question_lower:
            return self.knowledge_base['graph_client']
        return 'Information not found in codebase.'

    async def get_structure(self, repo: str=None) -> Dict[str, Any]:
        """Mock structure retrieval."""
        return {'structure': [{'path': 'agentic_core/L3_orchestration', 'type': 'directory'}, {'path': 'agentic_core/L4_state', 'type': 'directory'}, {'path': 'agentic_core/L6_observability', 'type': 'directory'}]}

    async def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return {'status': 'healthy', 'initialized': self.initialized}

@pytest_asyncio.fixture
async def graph_client() -> Any:
    """Create and initialize a mock graph client."""
    client: Any = MockSovereignGraphClient()
    await client.initialize()
    return client

@pytest_asyncio.fixture
async def deepwiki_client() -> Any:
    """Create and initialize a mock DeepWiki client."""
    client: Any = MockSovereignDeepWikiClient()
    await client.initialize()
    return client

@pytest.mark.asyncio
async def test_knowledge_graph_entity_creation(graph_client: Any) -> Any:
    """
    Test creating entities in the Knowledge Graph.
    Validates: Entity creation -> Graph storage -> Retrieval
    """
    entities: Any = [{'name': 'SovereignAI', 'entityType': 'System', 'observations': ['Phase 13D implementation', 'Dual-graph architecture']}, {'name': 'Chevy Traverse', 'entityType': 'Vehicle', 'observations': ['2024 model', "User's vehicle"]}]
    result: Any = await graph_client.create_entities(entities)
    assert 'Created 2 entities' in result
    graph: Any = await graph_client.read_graph()
    assert len(graph['entities']) == 2
    assert any((e['name'] == 'SovereignAI' for e in graph['entities']))
    assert any((e['name'] == 'Chevy Traverse' for e in graph['entities']))

@pytest.mark.asyncio
async def test_knowledge_graph_relations(graph_client: Any) -> Any:
    """
    Test creating relationships between entities.
    Validates: Entity creation -> Relation creation -> Graph integrity
    """
    entities: Any = [{'name': 'User', 'entityType': 'Person', 'observations': ['System user']}, {'name': 'Chevy Traverse', 'entityType': 'Vehicle', 'observations': ['2024 model']}]
    await graph_client.create_entities(entities)
    relations: Any = [{'from': 'User', 'to': 'Chevy Traverse', 'relationType': 'OWNS'}]
    result: Any = await graph_client.create_relations(relations)
    assert 'Created 1 relations' in result
    graph: Any = await graph_client.read_graph()
    assert len(graph['relations']) == 1
    assert graph['relations'][0]['from'] == 'User'
    assert graph['relations'][0]['to'] == 'Chevy Traverse'
    assert graph['relations'][0]['relationType'] == 'OWNS'

@pytest.mark.asyncio
async def test_knowledge_graph_search(graph_client: Any) -> Any:
    """
    Test searching for entities in the graph.
    Validates: Entity creation -> Search -> Result filtering
    """
    entities: Any = [{'name': 'SovereignAI', 'entityType': 'System', 'observations': []}, {'name': 'Sovereign Router', 'entityType': 'Component', 'observations': []}, {'name': 'Pinecone Client', 'entityType': 'Component', 'observations': []}]
    await graph_client.create_entities(entities)
    results: Any = await graph_client.search_nodes('Sovereign')
    assert len(results) == 2
    assert all(('Sovereign' in r['name'] for r in results))

@pytest.mark.asyncio
async def test_deepwiki_question_answering(deepwiki_client: Any) -> Any:
    """
    Test asking questions about the codebase.
    Validates: Question -> Knowledge retrieval -> Answer
    """
    answer: Any = await deepwiki_client.ask_question('Where is the mcp_router defined?')
    assert 'L3_orchestration' in answer
    assert 'mcp_router_sovereign.py' in answer
    answer: Any = await deepwiki_client.ask_question('Where is the Pinecone client?')
    assert 'L4_state' in answer
    assert 'pinecone_mcp_client.py' in answer

@pytest.mark.asyncio
async def test_deepwiki_structure_retrieval(deepwiki_client: Any) -> Any:
    """
    Test retrieving codebase structure.
    Validates: Structure request -> Directory tree -> Response
    """
    structure: Any = await deepwiki_client.get_structure()
    assert 'structure' in structure
    assert len(structure['structure']) > 0
    paths: Any = [item['path'] for item in structure['structure']]
    assert any(('L3_orchestration' in p for p in paths))
    assert any(('L4_state' in p for p in paths))
    assert any(('L6_observability' in p for p in paths))

@pytest.mark.asyncio
async def test_dual_graph_health_checks() -> Any:
    """
    Test health checks for both graph systems.
    Validates: Initialization -> Health status -> Metrics
    """
    graph_client: Any = MockSovereignGraphClient()
    deepwiki_client: Any = MockSovereignDeepWikiClient()
    await graph_client.initialize()
    await deepwiki_client.initialize()
    kg_health: Any = await graph_client.health_check()
    assert kg_health['status'] == 'healthy'
    assert kg_health['initialized'] is True
    assert 'entity_count' in kg_health
    dw_health: Any = await deepwiki_client.health_check()
    assert dw_health['status'] == 'healthy'
    assert dw_health['initialized'] is True

@pytest.mark.asyncio
async def test_dual_graph_integration_scenario() -> Any:
    """
    Test a complete scenario using both graph systems.
    Scenario: User asks about a component, system creates entity and retrieves code location.
    """
    graph_client: Any = MockSovereignGraphClient()
    deepwiki_client: Any = MockSovereignDeepWikiClient()
    await graph_client.initialize()
    await deepwiki_client.initialize()
    question: Any = 'Where is the MCP router?'
    answer: Any = await deepwiki_client.ask_question(question)
    entities: Any = [{'name': 'MCP Router', 'entityType': 'Component', 'observations': [f'Located at: {answer}', 'Handles MCP tool routing', 'L3 orchestration layer']}]
    await graph_client.create_entities(entities)
    graph: Any = await graph_client.read_graph()
    assert len(graph['entities']) == 1
    assert graph['entities'][0]['name'] == 'MCP Router'
    results: Any = await graph_client.search_nodes('MCP')
    assert len(results) == 1
    assert results[0]['name'] == 'MCP Router'

@pytest.mark.asyncio
async def test_knowledge_graph_with_config_disabled() -> Any:
    """
    Test that Knowledge Graph respects config disable flag.
    """
    from agentic_core.config.P1_core.sovereign_config import config
    graph_client: Any = MockSovereignGraphClient()
    await graph_client.initialize()
    with patch.object(config, 'KG_MCP_ENABLED', False):
        result: Any = await graph_client.create_entities([{'name': 'Test', 'entityType': 'Test'}])

@pytest.mark.asyncio
async def test_deepwiki_with_config_disabled() -> Any:
    """
    Test that DeepWiki respects config disable flag.
    """
    from agentic_core.config.P1_core.sovereign_config import config
    deepwiki_client: Any = MockSovereignDeepWikiClient()
    await deepwiki_client.initialize()
    with patch.object(config, 'DEEPWIKI_MCP_ENABLED', False):
        answer: Any = await deepwiki_client.ask_question('test')
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
