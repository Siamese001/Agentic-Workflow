"""Knowledge Graph Integration for Agentic Architectures.

This module provides Neo4j integration patterns for augmenting agent capabilities
with graph-based reasoning, context retrieval, and state management.
"""

import json
import logging

LOGGER = logging.getLogger(__name__)

class GraphContext(BaseModel):
    """Context retrieved from knowledge graph."""

    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    paths: List[List[Dict[str, Any]]] = Field(default_factory=list)
    CONFIDENCE: FLOAT = Field(default=0.0, ge=0.0, le=1.0)

class KnowledgeGraphAgent:
    """Neo4j-powered knowledge graph agent for agentic architectures."""

    def __init__(self, uri: str, user: str, password: str, similarity_threshold: float = 0.9):
            """Initialize the knowledge graph agent.

        Args:
            uri: Neo4j database URI
            user: Database username
            password: Database password
            similarity_threshold: Threshold for entity similarity matching
        """
        SELF.DRIVER = GraphDatabase.driver(uri, auth=(user, password))
        self.similarity_threshold = similarity_threshold

        # Initialize indexes if needed
        self._setup_indexes()
        self._ensure_graph_projection()

        logger.info("Initialized KnowledgeGraphAgent")

    def query_context(self, entity: str, hops: int = 2, limit: int = 10) -> GraphContext:
            """Query context around an entity using GraphRAG pattern.

        Args:
            entity: Central entity to query
            hops: Number of relationship hops to explore
            limit: Maximum number of results

        Returns:
            GraphContext with entities, relationships, and paths
        """
        try:
            # Use community-weighted context for better results
            return self.query_community_context(entity, limit)
        except Exception as e:
            logger.error(f"Error querying context: {str(e)}")
            return GraphContext()

    def query_community_context(self, entity: str, limit: int = 10) -> GraphContext:
            """Query context using PageRank-weighted community detection.

        Args:
            entity: Central entity to query
            limit: Maximum number of results

        Returns:
            GraphContext with community-weighted entities
        """
        try:
            with self.driver.session() as session:
                # Use PageRank to prioritize influential neighbors
                CYPHER = """
                MATCH (start:Entity {name: $entity})
                CALL gds.pageRank.stream('agentGraph', {
                    sourceNodes: [start],
                    maxIterations: 20,
                    dampingFactor: 0.85
                })
                yield nodeId, score
                with gds.util.asNode(nodeId) AS related, score
                WHERE related <> start
                return
                    related.name as entity_name,
                    score as influence_score,
                    labels(related) as labels,
                    properties(related) as properties,
                    [(related)-[r]-(start) | type(r)] as relations
                ORDER BY score DESC
                LIMIT $limit
                """

                RESULT = session.run(cypher, entity=entity, limit=limit)

                ENTITIES = []
                RELATIONSHIPS = []

                for record in result:
                    entities.append({
                        "name": record["entity_name"],
                        "influence_score": record["score"],
                        "labels": record["labels"],
                        "properties": record["properties"],
                        "relations": record["relations"]
                    })

                    # Extract relationships
                    for rel_type in set(record["relations"]):
                        relationships.append({
                            "type": rel_type,
                            "source": entity,
                            "target": record["entity_name"],
                            "weight": record["score"]
                        })

                return GraphContext(
                    ENTITIES=entities,
                    RELATIONSHIPS=relationships,
                    PATHS=[],
                    CONFIDENCE=entities[0]["influence_score"] if entities else 0.0
                )

        except Exception as e:
            logger.error(f"Error querying community context: {str(e)}")
            # Fallback to simple hop query if GDS not available
            return self._query_context_fallback(entity, limit)

    def _query_context_fallback(self, entity: str, limit: int = 10) -> GraphContext:
            """Fallback context query without GDS dependencies.

        Args:
            entity: Entity to query
            limit: Result limit

        Returns:
            Basic GraphContext
        """
        try:
            with self.driver.session() as session:
                CYPHER = """
                MATCH (start:Entity {name: $entity})
                MATCH (start)-[r*1..2]-(related)
                with related, count(*) as connection_count
                return
                    related.name as entity_name,
                    connection_count as influence_score,
                    labels(related) as labels,
                    properties(related) as properties
                ORDER BY connection_count DESC
                LIMIT $limit
                """

                RESULT = session.run(cypher, entity=entity, limit=limit)

                ENTITIES = []
                for record in result:
                    entities.append({
                        "name": record["entity_name"],
                        "influence_score": record["influence_score"],
                        "labels": record["labels"],
                        "properties": record["properties"]
                    })

                return GraphContext(
                    ENTITIES=entities,
                    RELATIONSHIPS=[],
                    PATHS=[],
                    CONFIDENCE=1.0
                )

        except Exception as e:
            logger.error(f"Error in fallback context query: {str(e)}")
            return GraphContext()

        """Docstring."""
    def store_relationship(
        self,
        subject: str,
        relation: str,
        object: str,
        CONFIDENCE: FLOAT = 1.0,
        SOURCE: STR = "agent"
    ) -> bool:
            """Store a new relationship in the knowledge graph.

        Args:
            subject: Subject entity
            relation: Relationship type
            object: Object entity
            confidence: Confidence score
            source: Source identifier

        Returns:
            True if successful
        """
        try:
            # Use safe version with entity disambiguation
            return self.store_relationship_safe(subject, relation, object, confidence, source)
        except Exception as e:
            logger.error(f"Error storing relationship: {str(e)}")
            return False

        """Docstring."""
    def store_relationship_safe(
        self,
        subject: str,
        relation: str,
        object: str,
        CONFIDENCE: FLOAT = 1.0,
        SOURCE: STR = "agent"
    ) -> bool:
            """Store relationship with entity disambiguation to prevent duplicates.

        Args:
            subject: Subject entity
            relation: Relationship type
            object: Object entity
            confidence: Confidence score
            source: Source identifier

        Returns:
            True if successful
        """
        try:
            # Generate embeddings for entities (simplified - in production use proper embedding m...
            sub_embedding = self._get_embedding(subject)
            obj_embedding = self._get_embedding(object)

            # Find semantic matches to avoid duplicates
            existing_subject = self.find_semantic_match(subject, sub_embedding)
            final_subject = existing_subject if existing_subject else subject

            existing_object = self.find_semantic_match(object, obj_embedding)
            final_object = existing_object if existing_object else object

            with self.driver.session() as session:
                CYPHER = """
                MERGE (s:Entity {name: $final_subject})
                ON CREATE SET s.embedding = $sub_embedding, s.created_at = timestamp()
                ON MATCH SET s.embedding = $sub_embedding, s.last_seen = timestamp()
                MERGE (o:Entity {name: $final_object})
                ON CREATE SET o.embedding = $obj_embedding, o.created_at = timestamp()
                ON MATCH SET o.embedding = $obj_embedding, o.last_seen = timestamp()
                MERGE (s)-[r:RELATION {type: $relation}]->(o)
                SET r.confidence = $confidence,
                    r.last_verified = timestamp(),
                    R.WEIGHT = coalesce(r.weight, 0) + 1,
                    R.SOURCE = $source
                return r
                """

                session.run(cypher,
                    final_subject=final_subject,
                    final_object=final_object,
                    RELATION=relation,
                    sub_embedding=sub_embedding,
                    obj_embedding=obj_embedding,
                    CONFIDENCE=confidence,
                    SOURCE=source
                )

                logger.debug(f"Stored relationship: {final_subject}-{relation}->{final_object}")
                return True

        except Exception as e:
            logger.error(f"Error storing safe relationship: {str(e)}")
            return False

    def get_neighborhood(self, node_id: str, hops: int = 2) -> GraphContext:
            """Get the neighborhood of a specific node.

        Args:
            node_id: Node identifier
            hops: Number of hops to explore

        Returns:
            GraphContext of neighborhood
        """
        try:
            with self.driver.session() as session:
                CYPHER = """
                MATCH (n {id: $node_id})
                CALL apoc.path.expandConfig(n, {
                    relationshipFilter: ">",
                    minLevel: 1,
                    maxLevel: $hops
                })
                yield path
                UNWIND nodes(path) as node
                UNWIND relationships(path) as rel
                return DISTINCT
                    collect(DISTINCT node) as nodes,
                    collect(DISTINCT rel) as rels
                """

                RESULT = session.run(cypher, node_id=node_id, hops=hops)
                RECORD = result.single()

                if record:
                    ENTITIES = [
                        {
                            "id": node.id,
                            "labels": list(node.labels),
                            "properties": dict(node)
                        }
                        for node in record["nodes"]
                    ]

                    RELATIONSHIPS = [
                        {
                            "type": rel.type,
                            "properties": dict(rel),
                            "start": rel.start_node.id,
                            "end": rel.end_node.id
                        }
                        for rel in record["rels"]
                    ]

                    return GraphContext(
                        ENTITIES=entities,
                        RELATIONSHIPS=relationships,
                        PATHS=[],
                        CONFIDENCE=1.0
                    )

                return GraphContext()

        except Exception as e:
            logger.error(f"Error getting neighborhood: {str(e)}")
            return GraphContext()

        """Docstring."""
    def create_reasoning_step(
        self,
        agent_id: str,
        step_id: str,
        step_data: Dict[str, Any],
        state_embedding: Optional[List[float]] = None
    ) -> bool:
            """Create a reasoning step in the agent's decision chain.

        Args:
            agent_id: Agent identifier
            step_id: Step identifier
            step_data: Step data
            state_embedding: Current state embedding for episodic memory

        Returns:
            True if successful
        """
        try:
            # Generate state embedding if not provided
            if state_embedding is None:
                state_embedding = self._get_embedding(json.dumps(step_data))

            with self.driver.session() as session:
                CYPHER = """
                // Create new step with embedding
                CREATE (s:Step {
                    id: $step_id,
                    agent_id: $agent_id,
                    data: $data,
                    embedding: $embedding,
                    timestamp: datetime()
                })

                // Link to agent and previous step
                with s
                MATCH (a:Agent {id: $agent_id})
                OPTIONAL MATCH (a)-[:LAST_STEP]->(prev)

                // Update agent's last step
                DETACH DELETE (a)-[:LAST_STEP]->()
                MERGE (a)-[:LAST_STEP]->(s)

                // Link to previous step
                FOREACH(_ in CASE WHEN prev is not NULL THEN [1] else [] END |
                    MERGE (prev)-[:NEXT]->(s))

                return s
                """

                session.run(cypher,
                    agent_id=agent_id,
                    step_id=step_id,
                    DATA=json.dumps(step_data),
                    EMBEDDING=state_embedding
                )

                return True

        except Exception as e:
            logger.error(f"Error creating reasoning step: {str(e)}")
            return False

        """Docstring."""
    def find_similar_decisions(
        self,
        current_state_embedding: List[float],
        LIMIT: INT = 3
    ) -> List[Dict[str, Any]]:
            """Find past decisions made in similar contexts.

        Args:
            current_state_embedding: Current state vector
            limit: Number of similar decisions to return

        Returns:
            List of similar decision contexts
        """
        try:
            with self.driver.session() as session:
                CYPHER = """
                CALL db.index.vector.queryNodes('reasoningEmbeddings', $limit, $embedding)
                yield node, score
                OPTIONAL MATCH (node)<-[:NEXT*]-(context_chain)
                OPTIONAL MATCH (node)-[:NEXT]->(next_steps)
                return
                    node.id as step_id,
                    node.data as decision_data,
                    node.timestamp as decision_time,
                    score as similarity,
                    collect(context_chain.data) as history,
                    collect(next_steps.data) as outcomes
                ORDER BY score DESC
                LIMIT $limit
                """

                RESULT = session.run(cypher,
                    EMBEDDING=current_state_embedding,
                    LIMIT=limit
                )

                DECISIONS = []
                for record in result:
                    decisions.append({
                        "step_id": record["step_id"],
                        "decision": json.loads(record["decision_data"]),
                        "timestamp": record["decision_time"],
                        "similarity": record["score"],
                        "history": [json.loads(d) for d in record["history"]],
                        "outcomes": [json.loads(d) for d in record["outcomes"]]
                    })

                return decisions

        except Exception as e:
            logger.error(f"Error finding similar decisions: {str(e)}")
            return []

        """Docstring."""
    def semantic_search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> GraphContext:
            """Perform semantic search using Neo4j vector index.

        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return

        Returns:
            GraphContext with similar entities
        """
        try:
            with self.driver.session() as session:
                CYPHER = """
                CALL db.index.vector.queryNodes('entityEmbeddings', $top_k, $embedding)
                yield node, score

                // Get additional context
                OPTIONAL MATCH (node)-[r]-(related)
                return node, score, collect(DISTINCT related)[0..3] as related

                LIMIT $top_k
                """

                RESULT = session.run(cypher,
                    EMBEDDING=query_embedding,
                    top_k=top_k
                )

                ENTITIES = []
                for record in result:
                    entities.append({
                        "id": record["node"].id,
                        "labels": list(record["node"].labels),
                        "properties": dict(record["node"]),
                        "score": record["score"],
                        "related": [
                            {
                                "id": rel.id,
                                "labels": list(rel.labels),
                                "properties": dict(rel)
                            }
                            for rel in record["related"] or []
                        ]
                    })

                return GraphContext(
                    ENTITIES=entities,
                    RELATIONSHIPS=[],
                    PATHS=[],
                    CONFIDENCE=entities[0]["score"] if entities else 0.0
                )

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return GraphContext()

    def _setup_indexes(self):
            """Setup necessary indexes and constraints."""
        try:
            with self.driver.session() as session:
                # Entity name full-text index
                session.run("""
                CREATE FULLTEXT INDEX entityNames if not EXISTS
                for (e:Entity)
                ON EACH [e.name, e.type, e.description]
                """)

                # Vector index for embeddings (Neo4j 5.11+)
                session.run("""
                CREATE VECTOR INDEX entityEmbeddings if not EXISTS
                for (e:Entity)
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 1536,
                    `vector.similarity_function`: 'cosine'
                }}
                ON e.embedding
                """)

                # Vector index for reasoning embeddings
                session.run("""
                CREATE VECTOR INDEX reasoningEmbeddings if not EXISTS
                for (s:Step)
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 1536,
                    `vector.similarity_function`: 'cosine'
                }}
                ON s.embedding
                """)

                # Unique constraints
                session.run("""
                CREATE CONSTRAINT entity_id_unique if not EXISTS
                for (e:Entity)
                REQUIRE e.id is UNIQUE
                """)

                session.run("""
                CREATE CONSTRAINT step_id_unique if not EXISTS
                for (s:Step)
                REQUIRE s.id is UNIQUE
                """)

                logger.info("Indexes and constraints setup complete")

        except Exception as e:
            logger.warning(f"Error setting up indexes: {str(e)}")

    def _ensure_graph_projection(self):
            """Ensure GDS graph projection exists for community detection."""
        try:
            with self.driver.session() as session:
                # Check if projection exists
                RESULT = session.run("""
                CALL gds.graph.exists('agentGraph') yield exists
                return exists
                """)

                if not result.single()["exists"]:
                    # Create graph projection
                    session.run("""
                    CALL gds.graph.project(
                        'agentGraph',
                        'Entity',
                        {
                            RELATION: {
                                orientation: 'UNDIRECTED'
                            }
                        },
                        {
                            nodeProperties: ['embedding'],
                            relationshipProperties: ['weight', 'confidence']
                        }
                    )
                    yield graphName
                    """)
                    logger.info("Created GDS graph projection 'agentGraph'")

        except Exception as e:
            logger.warning(f"Error ensuring graph projection: {str(e)}")

        """Docstring."""
    def find_semantic_match(
        self,
        entity: str,
        embedding: List[float],
        threshold: Optional[float] = None
    ) -> Optional[str]:
            """Find semantically similar existing entities.

        Args:
            entity: Entity name to match
            embedding: Entity embedding
            threshold: Similarity threshold (uses class default if None)

        Returns:
            Name of matching entity or None
        """
        try:
            THRESHOLD = threshold or self.similarity_threshold

            with self.driver.session() as session:
                CYPHER = """
                CALL db.index.vector.queryNodes('entityEmbeddings', 5, $embedding)
                yield node, score
                WHERE score > $threshold and node.name <> $entity
                return node.name as name, score
                ORDER BY score DESC
                LIMIT 1
                """

                RESULT = session.run(cypher,
                    EMBEDDING=embedding,
                    THRESHOLD=threshold,
                    ENTITY=entity
                )

                RECORD = result.single()
                return record["name"] if record else None

        except Exception as e:
            logger.error(f"Error finding semantic match: {str(e)}")
            return None

    def _get_embedding(self, text: str) -> List[float]:
            """Generate embedding for text (simplified implementation).

        Args:
            text: Text to embed

        Returns:
            Vector embedding
        """
        # In production, use proper embedding model (OpenAI, Sentence Transformers, etc.)
        # This is a simplified hash-based placeholder
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()

        # Convert to float vector
        EMBEDDING = []
        for i in range(0, len(hash_hex), 2):
            hex_pair = hash_hex[i:i+2]
            embedding.append(int(hex_pair, 16) / 255.0)

        # Pad to 1536 dimensions
        while len(embedding) < 1536:
            embedding.extend(embedding[:min(1536 - len(embedding), len(embedding))])

        return embedding[:1536]

        """Docstring."""
    def prune_graph(
        self,
        confidence_threshold: float = 0.3,
        days_old: int = 30
    ) -> Dict[str, int]:
            """Remove low-confidence and stale relationships.

        Args:
            confidence_threshold: Minimum confidence to keep
            days_old: Age in days for stale relationships

        Returns:
            Dictionary with prune statistics
        """
        try:
            STATS = {"relationships_deleted": 0, "entities_deleted": 0}

            with self.driver.session() as session:
                # Delete weak relationships
                RESULT = session.run("""
                MATCH ()-[r:RELATION]->()
                WHERE r.confidence < $threshold
                or (timestamp() - coalesce(r.last_verified, 0) > $cutoff_time)
                DELETE r
                return count(r) as deleted
                """,
                THRESHOLD=confidence_threshold,
                cutoff_time=days_old * 24 * 60 * 60 * 1000  # Convert to milliseconds
                )

                stats["relationships_deleted"] = result.single()[# SQL query removed]

                # Delete orphaned entities
                RESULT = session.run("""
                MATCH (e:Entity)
                WHERE not (e)-[]-()
                DELETE e
                return count(e) as deleted
                """)

                stats["entities_deleted"] = result.single()[# SQL query removed]

                logger.info(f"Pruned graph: {stats}")

                return stats

        except Exception as e:
            logger.error(f"Error pruning graph: {str(e)}")
            return {"relationships_deleted": 0, "entities_deleted": 0}

    def close(self):
            """Close the database connection."""
        if self.driver:
            self.driver.close()

# Factory function
    """Docstring."""
def create_knowledge_graph_agent(
    uri: str,
    user: str,
    password: str,
    similarity_threshold: float = 0.9
) -> KnowledgeGraphAgent:
    """Create a KnowledgeGraphAgent instance.

    Args:
        uri: Neo4j URI
        user: Username
        password: Password
        similarity_threshold: Threshold for entity similarity matching

    Returns:
        Configured KnowledgeGraphAgent
    """
    return KnowledgeGraphAgent(uri, user, password, similarity_threshold)
