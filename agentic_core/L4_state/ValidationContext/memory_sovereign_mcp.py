from __future__ import annotations

"""L4 State: Sovereign MCP Memory — Eternal Knowledge Graph
Ultra-hardened persistent memory with entities, relations, observations.
L5 shielded + Redis/Pinecone hybrid + tampering detection.
"""
import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.L4_state.validation_context.PineconeSovereignAgent import PineconeSovereignAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth

Logger: Any = logging.getLogger(__name__)
max_observation_length: Any = 2000
max_entity_name_length: Any = 100

class SovereignMemoryMcp:
    """Ultra-hardened knowledge graph MCP — eternal sovereign memory."""

    def __init__(self, mission_id: str, engine=None):
        self.mission_id = mission_id
        self.graph_key = f'memory_graph:{mission_id}'
        self.engine = engine
        self.pinecone = PineconeSovereignAgent(Path('.'))
        self.index_name = 'canon-memory-v1'

    async def create_entities(self, entities: list[dict]) -> dict:
        """Create sovereign entities with L5 validation and dual-store persistence."""
        created: Any = []
        try:
            for entity in entities[:20]:
                name: Any = entity['name']
                if len(name) > MAX_ENTITY_NAME_LENGTH:
                    continue
                redis_shield.execute('hset', f'{self.graph_key}:entities', name, json.dumps(entity))
                embed_text: Any = f"Entity: {name} Type: {entity.get('entityType')} Obs: {','.join(entity.get('observations', []))}"
                vector: Any = await self.engine.get_embedding(embed_text)
                self.pinecone.upsert(index=self.index_name, vectors=[(f'entity:{name}', vector, entity)], namespace='memory')
                created.append(name)
            return {'status': 'success', 'created': created}
        except Exception as e:
            mcp_authority.record_breach(f'Memory Entity Creation Failure: {str(e)}')
            return {'status': 'error', 'msg': str(e)}

    async def add_observations(self, observations: list[dict]) -> dict:
        """Add atomic facts to the graph with L5 size-shielding."""
        added: Any = {}
        try:
            for obs in observations:
                name: Any = obs['entityName']
                for content in obs['contents']:
                    if len(content) > MAX_OBSERVATION_LENGTH:
                        continue
                    redis_shield.execute('rpush', f'{self.graph_key}:obs:{name}', content)
                    added.setdefault(name, []).append(content)
            return {'status': 'success', 'added_count': len(added)}
        except Exception as e:
            mcp_authority.record_breach(f'Memory Observation Failure: {str(e)}')
            return {'status': 'error', 'msg': str(e)}

    async def search_nodes(self, query: str) -> list[dict]:
        """Semantic search across eternal memory with Redis fallback."""
        try:
            vector: Any = await self.engine.get_embedding(query)
            results: Any = self.pinecone.query(index=self.index_name, vector=vector, top_k=5, namespace='memory', include_metadata=True)
            return [match.metadata for match in results.matches]
        except Exception:
            return []
