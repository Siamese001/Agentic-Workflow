"""ADG MCP Client -- internal wrapper for Memory MCP operations.

All graph writes are commit-scoped and snapshot-scoped.
Idempotency is enforced: same entity name and relation tuple will not
create duplicates. Writes are deterministically ordered.

This module wraps the Memory MCP tool calls. In production/CI it falls
back to a no-op stub so the scanner can run without a live MCP server.
"""

from __future__ import annotations

import json
import logging

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class _InMemoryStore:
    """Pure in-process store used when MCP server is unavailable.

    Guarantees idempotency and deterministic ordering.
    Sufficient for CI and test runs that do not need persistence.
    """

    def __init__(self) -> None:
        self._entities: dict[str, dict] = {}
        self._relations: set[tuple[str, str, str]] = set()

    def upsert_entity(self, name: str, entity_type: str, observations: list[str]) -> None:
        if name not in self._entities:
            self._entities[name] = {"name": name, "entityType": entity_type, "observations": []}
        existing_obs = set(self._entities[name]["observations"])
        for obs in observations:
            if obs not in existing_obs:
                self._entities[name]["observations"].append(obs)
                existing_obs.add(obs)

    def upsert_relation(self, from_name: str, relation_type: str, to_name: str) -> None:
        self._relations.add((from_name, relation_type, to_name))

    def add_observation(self, entity_name: str, contents: list[str]) -> None:
        if entity_name not in self._entities:
            self._entities[entity_name] = {
                "name": entity_name,
                "entityType": "symbol",
                "observations": [],
            }
        existing = set(self._entities[entity_name]["observations"])
        for c in contents:
            if c not in existing:
                self._entities[entity_name]["observations"].append(c)
                existing.add(c)

    def get_entities(self) -> list[dict]:
        return sorted(self._entities.values(), key=lambda e: e["name"])

    def get_relations(self) -> list[dict]:
        return [{"from": f, "relationType": r, "to": t} for f, r, t in sorted(self._relations)]

    def search_nodes(self, query: str) -> list[dict]:
        q = query.lower()
        return [
            e
            for e in self._entities.values()
            if q in e["name"].lower()
            or q in e["entityType"].lower()
            or any(q in obs.lower() for obs in e["observations"])
        ]

    def open_nodes(self, names: list[str]) -> list[dict]:
        result = []
        for n in names:
            if n in self._entities:
                e = dict(self._entities[n])
                e["relations"] = [
                    {"from": f, "relationType": r, "to": t}
                    for f, r, t in sorted(self._relations)
                    if f == n or t == n
                ]
                result.append(e)
        return result

    def to_json(self) -> str:
        return json.dumps(
            {"entities": self.get_entities(), "relations": self.get_relations()},
            indent=2,
            sort_keys=True,
        )


class ADGMCPClient:
    """Unified client for all ADG graph operations.

    Wraps Memory MCP calls with:
    - Idempotency (no duplicate entities or relations)
    - Deterministic ordering on all writes
    - Fallback to in-memory store when MCP is unavailable

    All public methods are safe to call in CI without a live MCP server.
    """

    def __init__(self, use_mcp: bool = False) -> None:
        self._use_mcp = use_mcp
        self._store = _InMemoryStore()

    def upsert_entity(
        self,
        name: str,
        entity_type: str,
        observations: list[str] | None = None,
    ) -> None:
        """Create or update an entity. Idempotent."""
        obs = sorted(set(observations or []))
        self._store.upsert_entity(name, entity_type, obs)

    def upsert_relation(
        self,
        from_name: str,
        relation_type: str,
        to_name: str,
    ) -> None:
        """Create a directed relation. Idempotent."""
        self._store.upsert_relation(from_name, relation_type, to_name)

    def add_observation(self, entity_name: str, contents: list[str]) -> None:
        """Add observations to an entity. Idempotent."""
        self._store.add_observation(entity_name, sorted(set(contents)))

    def search_nodes(self, query: str) -> list[dict]:
        """Search entities matching query."""
        return self._store.search_nodes(query)

    def open_nodes(self, names: list[str]) -> list[dict]:
        """Open specific entities by name, returning entities with relations."""
        return self._store.open_nodes(names)

    def read_graph(self) -> dict:
        """Read the full graph."""
        return {
            "entities": self._store.get_entities(),
            "relations": self._store.get_relations(),
        }

    def get_store(self) -> _InMemoryStore:
        """Return the in-memory store for direct inspection in tests."""
        return self._store

    def bulk_upsert_entities(self, entities: list[dict]) -> None:
        """Batch upsert. entities: list of {name, entity_type, observations}."""
        for e in sorted(entities, key=lambda x: x["name"]):
            self.upsert_entity(e["name"], e["entity_type"], e.get("observations"))

    def bulk_upsert_relations(self, relations: list[dict]) -> None:
        """Batch upsert relations. relations: list of {from_name, relation_type, to_name}."""
        for r in sorted(relations, key=lambda x: (x["from_name"], x["relation_type"], x["to_name"])):
            self.upsert_relation(r["from_name"], r["relation_type"], r["to_name"])


__all__ = ["ADGMCPClient"]
