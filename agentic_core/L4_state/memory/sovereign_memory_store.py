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

"""L4 State: Sovereign MCP Memory — Eternal Knowledge Graph

Ultra-hardened persistent memory with entities, relations, observations.

Delegates all operations through GraphMemoryBridge which routes to the
live mcp11_* Memory MCP tools (or falls back gracefully in CI).

"""

import logging
from typing import Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

# [SSOT IMPORT] Structure blueprint is the single source of truth


Logger: Any = logging.getLogger(__name__)

max_observation_length: Any = 2000

max_entity_name_length: Any = 100


class SovereignMemoryMcp:
    """Ultra-hardened knowledge graph MCP — delegates to GraphMemoryBridge."""

    def __init__(self, mission_id: str, engine=None):
        self.mission_id = mission_id
        self.engine = engine
        self._bridge = GraphMemoryBridge.get_instance()

    async def create_entities(self, entities: list[dict]) -> dict:
        """Create sovereign entities — delegated to GraphMemoryBridge → mcp11."""
        created: Any = []

        try:
            for entity in entities[:20]:
                name: Any = entity.get("name", "")
                if not name or len(name) > max_entity_name_length:
                    continue
                self._bridge.create_agent_entity(
                    agent_name=name,
                    agent_type=entity.get("entityType", "Entity"),
                    observations=entity.get("observations"),
                )
                created.append(name)

            return {"status": "success", "created": created}

        except Exception as e:
            Logger.error(f"[SovereignMemoryMcp] Entity creation failure: {e}")
            return {"status": "error", "msg": str(e)}

    async def add_observations(self, observations: list[dict]) -> dict:
        """Add atomic facts to the graph with size-shielding — delegated to GraphMemoryBridge."""
        added: Any = {}

        try:
            for obs in observations:
                name: Any = obs.get("entityName", "")
                for content in obs.get("contents", []):
                    if len(content) > max_observation_length:
                        content = content[: max_observation_length - 3] + "..."
                    self._bridge.add_observation(name, content)
                    added.setdefault(name, []).append(content)

            return {"status": "success", "added_count": len(added)}

        except Exception as e:
            Logger.error(f"[SovereignMemoryMcp] Observation failure: {e}")
            return {"status": "error", "msg": str(e)}

    async def search_nodes(self, query: str) -> list[dict]:
        """Semantic search across eternal memory — delegated to GraphMemoryBridge."""
        try:
            return self._bridge.search_entities(query)
        except Exception:
            return []
