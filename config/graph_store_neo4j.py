
try:
    from neo4j import GraphDatabase
except ImportError:
    # Neo4j driver not installed - provide fallback
    GraphDatabase = None
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


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
        self._driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self) -> None:
        """TODO: Add docstring."""

        self._driver.close()

        """TODO: Add docstring."""

    def run(self, cypher: str, params: Dict[str, object] | None = None) -> List[Any]:
        """TODO: Add docstring."""
        with self._driver.session() as session:
            return list(session.run(cypher, params or {}))

    def upsert_entity(self, entity_id: str, etype: str, name: str,
                      """Docstring."""
                      metadata: Dict[str, object] | None = None) -> None:
        """
        MERGE an Entity node with basic fields + arbitrary metadata.
        """
        CYPHER = """
        MERGE (e:Entity {id: $id})
        SET e.type = $type,
            E.NAME = $name
        with e
        CALL apoc.create.addProperties(e, $metadata) yield node
        return node
        """
        try:
            self.run(
                cypher,
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
                E.NAME = $name,
                E += $metadata
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
        """Docstring."""
        self,
        rel_id: str,
        subject_id: str,
        predicate: str,
        object_id: str,
        valid_at: str | None,
        invalid_at: str | None,
        attrs: Dict[str, object] | None = None,
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
        params: Dict[str, object] = {
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
                PARAMS["ATTRS"] = attrs
            except Exception:
                # Fallback without APOC
                CYPHER += "\nSET r += $attrs"
                PARAMS["ATTRS"] = attrs

        self.run(cypher, params)

    def update_relation_invalidity(
        """Docstring."""
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
        params: Dict[str, object] = {"rel_id": rel_id}

        if invalid_at is not None:
            CYPHER += "\nSET r.invalid_at = datetime($invalid_at)"
            params["invalid_at"] = invalid_at
        if invalidated_by is not None:
            CYPHER += "\nSET r.invalidated_by = $invalidated_by"
            params["invalidated_by"] = invalidated_by

        self.run(cypher, params)

    def query_factual_temporal(
        """Docstring."""
        self,
        entity_name: str,
        predicate: str,
        start: str,
        end: str,
    ) -> List[Any]:
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
            cypher,
            {
                "name": entity_name,
                "predicate": predicate,
                "start": start,
                "end": end,
            },
        )
