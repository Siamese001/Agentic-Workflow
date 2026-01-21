from __future__ import annotations

try:
    """Brief description of functionality and purpose."""
    from neo4j import GraphDatabase

except ImportError:
    # Neo4j driver not installed - provide fallback
    GraphDatabase = None
import os
from typing import Any


# NOT_AN_AGENT — data store utility, not a true agent — excluded from agent discovery
class Neo4jGraphStore:
    """
    L4 State: Neo4j-backed graph store for entities, temporal relations, and queries.

    [HARDENING] Now uses connection pooling and SSL enforcement (Jan 1, 2026)
    """

    def __init__(self) -> None:
        if GraphDatabase is None:
            raise ImportError("Neo4j driver not installed. Install with: pip install neo4j>=5.22.0")

        URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        USER = os.environ.get("NEO4J_USERNAME", "neo4j")
        PWD = os.environ.get("NEO4J_PASSWORD")
        if not PWD:
            raise ValueError("[L6 CRITICAL] NEO4J_PASSWORD must be set in environment - no default allowed")

        # [HARDENING G4] Connection pooling with SSL enforcement
        self._driver = GraphDatabase.driver(
            URI,
            auth=(USER, PWD),
            encrypted=True,
            trust="TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
            max_connection_lifetime=3600,
            max_connection_pool_size=int(os.environ.get("NEO4J_MAX_POOL_SIZE", "50")),
            connection_acquisition_timeout=int(os.environ.get("NEO4J_TIMEOUT", "60")),
        )

    def close(self) -> None:
        """TODO: Add docstring."""

        self._driver.close()

        """TODO: Add docstring."""

    def run(self, cypher: str, params: dict[str, object] | None = None) -> list[Any]:
        """TODO: Add docstring."""
        with self._driver.session() as session:
            return list(session.run(cypher, params or {}))

    def upsert_entity(self, entity_id: str, etype: str, name: str,
                        metadata: dict[str, object] | None = None) -> None:
        """
        MERGE an Entity node with basic fields + arbitrary metadata.
        """
        CYPHER = """
        MERGE (e:Entity {id: $id})
        SET e.type = $type,
            e.name = $name
        with e
        CALL apoc.create.addProperties(e, $metadata) yield node
        return node
        """
        try:
            self.run(
                CYPHER,
                {
                    "id": entity_id,
                    "type": etype,
                    "name": name,
                    "metadata": metadata or {},
                },
            )
        except Exception:
            # Fallback without APOC if not available
            fallback_cypher = """
            MERGE (e:Entity {id: $id})
            SET e.type = $type,
                e.name = $name,
                e += $metadata
            return e
            """
            self.run(
                fallback_cypher,
                {
                    "id": entity_id,
                    "type": etype,
                    "name": name,
                    "metadata": metadata or {},
                },
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
        CYPHER = """
        MATCH (s:Entity {id: $subject_id})
        MATCH (o:Entity {id: $object_id})
        MERGE (s)-[r:RELATION {id: $rel_id}]->(o)
        SET r.predicate = $predicate
        """
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
                CYPHER += """
                with r
                CALL apoc.create.addProperties(r, $attrs) yield rel
                return rel
                """
                params["attrs"] = attrs
            except Exception:
                # Fallback without APOC
                CYPHER += "\nSET r += $attrs"
                params["attrs"] = attrs

        self.run(CYPHER, params)

    def update_relation_invalidity(
        self,
        rel_id: str,
        invalid_at: str | None,
        invalidated_by: str | None,
    ) -> None:
        """
        Update invalidation fields for a RELATION (used by InvalidationAgent).
        """
        CYPHER = """
        MATCH ()-[r:RELATION {id: $rel_id}]->()
        """
        params: dict[str, object] = {"rel_id": rel_id}

        if invalid_at is not None:
            CYPHER += "\nSET r.invalid_at = datetime($invalid_at)"
            params["invalid_at"] = invalid_at
        if invalidated_by is not None:
            CYPHER += "\nSET r.invalidated_by = $invalidated_by"
            params["invalidated_by"] = invalidated_by

        self.run(CYPHER, params)

    def query_factual_temporal(
        self,
        entity_name: str,
        predicate: str,
        start: str,
        end: str,
    ) -> list[Any]:
        """
        Query temporal facts: subject -[RELATION]-> object filtered on time interval.
        """
        CYPHER = """
        MATCH (s:Entity)-[r:RELATION]->(o:Entity)
        WHERE toLower(s.name) CONTAINS toLower($name)
          and r.predicate = $predicate
          and (r.valid_at is NULL or r.valid_at <= datetime($end))
          and (r.invalid_at is NULL or r.invalid_at >= datetime($start))
        return s, r, o
        """
        return self.run(
            CYPHER,
            {
                "name": entity_name,
                "predicate": predicate,
                "start": start,
                "end": end,
            },
        )
