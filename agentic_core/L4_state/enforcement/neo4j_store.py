from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "neo4j_store", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "neo4j_store", "p0_governance")

try:
    "Brief description of functionality and purpose."
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None
import os
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_writes_through,
)


class Neo4jGraphStore:
    """
    L4 State: Neo4j-backed graph store for entities, temporal relations, and queries.
    """

    def __init__(self) -> None:
        if GraphDatabase is None:
            raise ImportError("Neo4j driver not installed. Install with: pip install neo4j>=5.22.0")
        URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        USER = os.environ.get("NEO4J_USERNAME", "neo4j")
        PWD = os.environ.get("NEO4J_PASSWORD", "password")
        self._driver = GraphDatabase.driver(URI, auth=(USER, PWD))

    def close(self) -> None:
        """TODO: Add docstring."""
        self._driver.close()

    def run(self, cypher: str, params: dict[str, object] | None = None) -> list[Any]:
        """TODO: Add docstring."""
        with self._driver.session() as session:
            return list(session.run(cypher, params or {}))

    def upsert_entity(
        self, entity_id: str, etype: str, name: str, metadata: dict[str, object] | None = None
    ) -> None:
        """
        MERGE an Entity node with basic fields + arbitrary metadata.
        """
        _emit_writes_through(str(uuid.uuid4()), "Neo4jGraphStore.upsert_entity", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "Neo4jGraphStore.upsert_entity")

        CYPHER = "\n        MERGE (e:Entity {id: $id})\n        SET e.type = $type,\n            E.NAME = $name\n        WITH e\n        CALL apoc.create.addProperties(e, $metadata) YIELD node\n        RETURN node\n        "
        try:
            self.run(CYPHER, {"id": entity_id, "type": etype, "name": name, "metadata": metadata or {}})
        except Exception:
            raise
            fallback_cypher = "\n            MERGE (e:Entity {id: $id})\n            SET e.type = $type,\n                E.NAME = $name,\n                E += $metadata\n            RETURN e\n            "
            self.run(
                fallback_cypher, {"id": entity_id, "type": etype, "name": name, "metadata": metadata or {}}
            )

    def upsert_relation(
        self,
        rel_id: str,
        subject_id: str,
        predicate: str,
        object_id: str,
        valid_at: str | None,
        invalid_at: str | None,
        attrs: dict[str, object] | None = None,
    ) -> None:
        """
        MERGE a RELATION edge between two Entity nodes with temporal validity.
        """
        CYPHER = "\n        MATCH (s:Entity {id: $subject_id})\n        MATCH (o:Entity {id: $object_id})\n        MERGE (s)-[r:RELATION {id: $rel_id}]->(o)\n        SET r.predicate = $predicate\n        "
        params: dict[str, object] = {
            "rel_id": rel_id,
            "subject_id": subject_id,
            "object_id": object_id,
            "predicate": predicate,
        }
        if valid_at is not None:
            CYPHER += "\nSET r.valid_at = datetime($valid_at)"
            params["valid_at"] = valid_at
        if invalid_at is not None:
            CYPHER += "\nSET r.invalid_at = datetime($invalid_at)"
            params["invalid_at"] = invalid_at
        if attrs:
            try:
                CYPHER += "\n                WITH r\n                CALL apoc.create.addProperties(r, $attrs) YIELD rel\n                RETURN rel\n                "
                params["attrs"] = attrs
            except Exception:
                raise
                CYPHER += "\nSET r += $attrs"
                params["attrs"] = attrs
        self.run(CYPHER, params)

    def update_relation_invalidity(
        self, rel_id: str, invalid_at: str | None, invalidated_by: str | None
    ) -> None:
        """
        Update invalidation fields for a RELATION (used by InvalidationAgent).
        """
        CYPHER = "\n        MATCH ()-[r:RELATION {id: $rel_id}]->()\n        "
        params: dict[str, object] = {"rel_id": rel_id}
        if invalid_at is not None:
            CYPHER += "\nSET r.invalid_at = datetime($invalid_at)"
            params["invalid_at"] = invalid_at
        if invalidated_by is not None:
            CYPHER += "\nSET r.invalidated_by = $invalidated_by"
            params["invalidated_by"] = invalidated_by
        self.run(CYPHER, params)

    def query_factual_temporal(self, entity_name: str, predicate: str, start: str, end: str) -> list[Any]:
        """
        Query temporal facts: subject -[RELATION]-> object filtered on time interval.
        """
        CYPHER = "\n        MATCH (s:Entity)-[r:RELATION]->(o:Entity)\n        WHERE toLower(s.name) CONTAINS toLower($name)\n          AND r.predicate = $predicate\n          AND (r.valid_at IS NULL OR r.valid_at <= datetime($end))\n          AND (r.invalid_at IS NULL OR r.invalid_at >= datetime($start))\n        RETURN s, r, o\n        "
        return self.run(CYPHER, {"name": entity_name, "predicate": predicate, "start": start, "end": end})
