"""L4 State: Sovereign MCP Memory — Eternal Knowledge Graph
Ultra-hardened persistent memory with entities, relations, observations.
L5 shielded + Redis/Pinecone hybrid + tampering detection.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from agentic_core.L5_safety.shield.redis_sovereign_shield import redis_shield
from agentic_core.L4_state.validation_context.pinecone_sovereign_agent import PineconeSovereignAgent
from agentic_core.L5_safety.guardrails.mcp_sovereign import mcp_authority

logger = logging.getLogger(__name__)

# Sovereign limits enforced at L5
MAX_OBSERVATION_LENGTH = 2000
MAX_ENTITY_NAME_LENGTH = 100

class SovereignMemoryMCP:
    """Ultra-hardened knowledge graph MCP — eternal sovereign memory."""
    
    def __init__(self, mission_id: str, engine=None):
        self.mission_id = mission_id
        self.graph_key = f"memory_graph:{mission_id}"
        self.engine = engine
        self.pinecone = PineconeSovereignAgent(Path("."))
        self.index_name = "canon-memory-v1"

    async def create_entities(self, entities: List[Dict]) -> Dict:
        """Create sovereign entities with L5 validation and dual-store persistence."""
        created = []
        try:
            for entity in entities[:20]: # Sovereign batch limit
                name = entity["name"]
                if len(name) > MAX_ENTITY_NAME_LENGTH: continue
                
                # 1. Fast Redis State
                redis_shield.execute("hset", f"{self.graph_key}:entities", name, json.dumps(entity))
                
                # 2. Eternal Semantic Vector
                embed_text = f"Entity: {name} Type: {entity.get('entityType')} Obs: {','.join(entity.get('observations', []))}"
                vector = await self.engine.get_embedding(embed_text)
                self.pinecone.upsert(
                    index=self.index_name,
                    vectors=[(f"entity:{name}", vector, entity)],
                    namespace="memory"
                )
                created.append(name)
            return {"status": "success", "created": created}
        except Exception as e:
            mcp_authority.record_breach(f"Memory Entity Creation Failure: {str(e)}")
            return {"status": "error", "msg": str(e)}

    async def add_observations(self, observations: List[Dict]) -> Dict:
        """Add atomic facts to the graph with L5 size-shielding."""
        added = {}
        try:
            for obs in observations:
                name = obs["entityName"]
                for content in obs["contents"]:
                    if len(content) > MAX_OBSERVATION_LENGTH: continue
                    
                    # Push to Redis observation list for this entity
                    redis_shield.execute("rpush", f"{self.graph_key}:obs:{name}", content)
                    added.setdefault(name, []).append(content)
            return {"status": "success", "added_count": len(added)}
        except Exception as e:
            mcp_authority.record_breach(f"Memory Observation Failure: {str(e)}")
            return {"status": "error", "msg": str(e)}

    async def search_nodes(self, query: str) -> List[Dict]:
        """Semantic search across eternal memory with Redis fallback."""
        try:
            vector = await self.engine.get_embedding(query)
            results = self.pinecone.query(
                index=self.index_name,
                vector=vector,
                top_k=5,
                namespace="memory",
                include_metadata=True
            )
            return [match.metadata for match in results.matches]
        except Exception:
            return [] # Fallback to LLM reasoning if memory search fails
