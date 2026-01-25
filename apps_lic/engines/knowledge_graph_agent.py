"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""

# LEGACY CODE BELOW - COMMENTED OUT
# """Knowledge Graph Integration for Agentic Architectures.

# This module provides Neo4j integration patterns for augmenting agent capabilities
# with graph-based reasoning, context retrieval, and state management.
# """

# from __future__ import annotations
# from dataclasses import dataclass, field
# from typing import Any
# import json
# import logging

# logger = logging.getLogger(__name__)


# @dataclass
# class GraphContext:
#     """Context retrieved from knowledge graph."""

#     entities: list[dict[str, Any]] = field(default_factory=list)
#     relationships: list[dict[str, Any]] = field(default_factory=list)
#     paths: list[list[dict[str, Any]]] = field(default_factory=list)
#     confidence: float = field(default=0.0, metadata={"ge": 0.0, "le": 1.0)


# class KnowledgeGraphAgent:
#     """Neo4j-powered knowledge graph agent for agentic architectures."""

#     def __init__(self}, uri: str, user: str, password: str, similarity_threshold: float = 0.9):
#         """Initialize the knowledge graph agent.

#         Args:
#             uri: Neo4j database URI
#             user: Database username
#             password: Database password
#             similarity_threshold: Threshold for entity similarity matching
#         """
#         self.driver = GraphDatabase.driver(uri, auth=(user, password))
#         self.similarity_threshold = similarity_threshold

#         # Initialize indexes if needed
#         self._setup_indexes()
#         self._ensure_graph_projection()

#         logger.info("Initialized KnowledgeGraphAgent")

#     def query_context(self, entity: str, hops: int = 2, limit: int = 10) -> GraphContext:
#         """Query context around an entity using GraphRAG pattern.

#         Args:
#             entity: Central entity to query
#             hops: Number of relationship hops to explore
#             limit: Maximum number of results

#         Returns:
#             GraphContext with entities, relationships, and paths
#         """
#         try:
#             # Use community-weighted context for better results
#             return self.query_community_context(entity, limit)
#         except Exception as e:
#             logger.error(f"Error querying context: {str(e)}")
#             return GraphContext()

#     def query_community_context(self, entity: str, limit: int = 10) -> GraphContext:
#         """Query context using PageRank-weighted community detection.

#         Args:
#             entity: Central entity to query
#             limit: Maximum number of results

#         Returns:
#             GraphContext with community-weighted entities
#         """
#         try:
#             with self.driver.session() as session:
#                 # Use PageRank to prioritize influential neighbors
#                 cypher = """
#                 MATCH (start:Entity {name: $entity})
#                 CALL gds.pageRank.stream('agentGraph', {
#                     sourceNodes: [start],
#                     maxIterations: 20,
#                     dampingFactor: 0.85
#                 })
#                 YIELD nodeId, score
#                 WITH gds.util.asNode(nodeId) AS related, score
#                 WHERE related <> start
#                 RETURN
#                     related.name as entity_name,
#                     score as influence_score,
#                     labels(related) as labels,
#                     properties(related) as properties,
#                     [(related)-[r]-(start) | type(r)] as relations
#                 ORDER BY score DESC
#                 LIMIT $limit
#                 """

#                 result = session.run(cypher, entity=entity, limit=limit)

#                 entities = []
#                 relationships = []

#                 for record in result:
#                     entities.append(
#                         {
#                             "name": record["entity_name"],
#                             "influence_score": record["score"],
#                             "labels": record["labels"],
#                             "properties": record["properties"],
#                             "relations": record["relations"],
#                         }
#                     )

#                     # Extract relationships
#                     for rel_type in set(record["relations"]):
#                         relationships.append(
#                             {
#                                 "type": rel_type,
#                                 "source": entity,
#                                 "target": record["entity_name"],
#                                 "weight": record["score"],
#                             }
#                         )

#                 return GraphContext(
#                     entities=entities,
#                     relationships=relationships,
#                     paths=[],
#                     confidence=entities[0]["influence_score"] if entities else 0.0,
#                 )

#         except Exception as e:
#             logger.error(f"Error querying community context: {str(e)}")
#             # Fallback to simple hop query if GDS not available
#             return self._query_context_fallback(entity, limit)

#     def _query_context_fallback(self, entity: str, limit: int = 10) -> GraphContext:
#         """Fallback context query without GDS dependencies.

#         Args:
#             entity: Entity to query
#             limit: Result limit

#         Returns:
#             Basic GraphContext
#         """
#         try:
#             with self.driver.session() as session:
#                 cypher = """
#                 MATCH (start:Entity {name: $entity})
#                 MATCH (start)-[r*1..2]-(related)
#                 WITH related, count(*) as connection_count
#                 RETURN
#                     related.name as entity_name,
#                     connection_count as influence_score,
#                     labels(related) as labels,
#                     properties(related) as properties
#                 ORDER BY connection_count DESC
#                 LIMIT $limit
#                 """

#                 result = session.run(cypher, entity=entity, limit=limit)

#                 entities = []
#                 for record in result:
#                     entities.append(
#                         {
#                             "name": record["entity_name"],
#                             "influence_score": record["influence_score"],
#                             "labels": record["labels"],
#                             "properties": record["properties"],
#                         }
#                     )

#                 return GraphContext(entities=entities, relationships=[], paths=[], confidence=1.0)

#         except Exception as e:
#             logger.error(f"Error in fallback context query: {str(e)}")
#             return GraphContext()

#     def store_relationship(
#         self,
#         subject: str,
#         relation: str,
#         object: str,
#         confidence: float = 1.0,
#         source: str = "agent",
#     ) -> bool:
#         """Store a new relationship in the knowledge graph.

#         Args:
#             subject: Subject entity
#             relation: Relationship type
#             object: Object entity
#             confidence: Confidence score
#             source: Source identifier

#         Returns:
#             True if successful
#         """
#         try:
#             # Use safe version with entity disambiguation
#             return self.store_relationship_safe(subject, relation, object, confidence, source)
#         except Exception as e:
#             logger.error(f"Error storing relationship: {str(e)}")
#             return False

#     def store_relationship_safe(
#         self,
#         subject: str,
#         relation: str,
#         object: str,
#         confidence: float = 1.0,
#         source: str = "agent",
#     ) -> bool:
#         """Store relationship with entity disambiguation to prevent duplicates.

#         Args:
#             subject: Subject entity
#             relation: Relationship type
#             object: Object entity
#             confidence: Confidence score
#             source: Source identifier

#         Returns:
#             True if successful
#         """
#         try:
#             # Generate embeddings for entities (simplified - in production use proper embedding model)
#             sub_embedding = self._get_embedding(subject)
#             obj_embedding = self._get_embedding(object)

#             # Find semantic matches to avoid duplicates
#             existing_subject = self.find_semantic_match(subject, sub_embedding)
#             final_subject = existing_subject if existing_subject else subject

#             existing_object = self.find_semantic_match(object, obj_embedding)
#             final_object = existing_object if existing_object else object

#             with self.driver.session() as session:
#                 cypher = """
#                 MERGE (s:Entity {name: $final_subject})
#                 ON CREATE SET s.embedding = $sub_embedding, s.created_at = timestamp()
#                 ON MATCH SET s.embedding = $sub_embedding, s.last_seen = timestamp()
#                 MERGE (o:Entity {name: $final_object})
#                 ON CREATE SET o.embedding = $obj_embedding, o.created_at = timestamp()
#                 ON MATCH SET o.embedding = $obj_embedding, o.last_seen = timestamp()
#                 MERGE (s)-[r:RELATION {type: $relation}]->(o)
#                 SET r.confidence = $confidence,
#                     r.last_verified = timestamp(),
#                     r.weight = coalesce(r.weight, 0) + 1,
#                     r.source = $source
#                 RETURN r
#                 """

#                 session.run(
#                     cypher,
#                     final_subject=final_subject,
#                     final_object=final_object,
#                     relation=relation,
#                     sub_embedding=sub_embedding,
#                     obj_embedding=obj_embedding,
#                     confidence=confidence,
#                     source=source,
#                 )

#                 logger.debug(f"Stored relationship: {final_subject}-{relation}->{final_object}")
#                 return True

#         except Exception as e:
#             logger.error(f"Error storing safe relationship: {str(e)}")
#             return False

#     def get_neighborhood(self, node_id: str, hops: int = 2) -> GraphContext:
#         """Get the neighborhood of a specific node.

#         Args:
#             node_id: Node identifier
#             hops: Number of hops to explore

#         Returns:
#             GraphContext of neighborhood
#         """
#         try:
#             with self.driver.session() as session:
#                 cypher = """
#                 MATCH (n {id: $node_id})
#                 CALL apoc.path.expandConfig(n, {
#                     relationshipFilter: ">",
#                     minLevel: 1,
#                     maxLevel: $hops
#                 })
#                 YIELD path
#                 UNWIND nodes(path) as node
#                 UNWIND relationships(path) as rel
#                 RETURN DISTINCT
#                     collect(DISTINCT node) as nodes,
#                     collect(DISTINCT rel) as rels
#                 """

#                 result = session.run(cypher, node_id=node_id, hops=hops)
#                 record = result.single()

#                 if record:
#                     entities = [
#                         {"id": node.id, "labels": list(node.labels), "properties": dict(node)}
#                         for node in record["nodes"]
#                     ]

#                     relationships = [
#                         {
#                             "type": rel.type,
#                             "properties": dict(rel),
#                             "start": rel.start_node.id,
#                             "end": rel.end_node.id,
#                         }
#                         for rel in record["rels"]
#                     ]

#                     return GraphContext(
#                         entities=entities, relationships=relationships, paths=[], confidence=1.0
#                     )

#                 return GraphContext()

#         except Exception as e:
#             logger.error(f"Error getting neighborhood: {str(e)}")
#             return GraphContext()

#     def create_reasoning_step(
#         self,
#         agent_id: str,
#         step_id: str,
#         step_data: dict[str, Any],
#         state_embedding: list[float] | None = None,
#     ) -> bool:
#         """Create a reasoning step in the agent's decision chain.

#         Args:
#             agent_id: Agent identifier
#             step_id: Step identifier
#             step_data: Step data
#             state_embedding: Current state embedding for episodic memory

#         Returns:
#             True if successful
#         """
#         try:
#             # Generate state embedding if not provided
#             if state_embedding is None:
#                 state_embedding = self._get_embedding(json.dumps(step_data))

#             with self.driver.session() as session:
#                 cypher = """
#                 // Create new step with embedding
#                 CREATE (s:Step {
#                     id: $step_id,
#                     agent_id: $agent_id,
#                     data: $data,
#                     embedding: $embedding,
#                     timestamp: datetime()
#                 })

#                 // Link to agent and previous step
#                 WITH s
#                 MATCH (a:Agent {id: $agent_id})
#                 OPTIONAL MATCH (a)-[:LAST_STEP]->(prev)

#                 // Update agent's last step
#                 DETACH DELETE (a)-[:LAST_STEP]->()
#                 MERGE (a)-[:LAST_STEP]->(s)

#                 // Link to previous step
#                 FOREACH(_ IN CASE WHEN prev IS NOT NULL THEN [1] ELSE [] END |
#                     MERGE (prev)-[:NEXT]->(s))

#                 RETURN s
#                 """

#                 session.run(
#                     cypher,
#                     agent_id=agent_id,
#                     step_id=step_id,
#                     data=json.dumps(step_data),
#                     embedding=state_embedding,
#                 )

#                 return True

#         except Exception as e:
#             logger.error(f"Error creating reasoning step: {str(e)}")
#             return False

#     def find_similar_decisions(
#         self, current_state_embedding: list[float], limit: int = 3
#     ) -> list[dict[str, Any]]:
#         """Find past decisions made in similar contexts.

#         Args:
#             current_state_embedding: Current state vector
#             limit: Number of similar decisions to return

#         Returns:
#             List of similar decision contexts
#         """
#         try:
#             with self.driver.session() as session:
#                 cypher = """
#                 CALL db.index.vector.queryNodes('reasoningEmbeddings', $limit, $embedding)
#                 YIELD node, score
#                 OPTIONAL MATCH (node)<-[:NEXT*]-(context_chain)
#                 OPTIONAL MATCH (node)-[:NEXT]->(next_steps)
#                 RETURN
#                     node.id as step_id,
#                     node.data as decision_data,
#                     node.timestamp as decision_time,
#                     score as similarity,
#                     collect(context_chain.data) as history,
#                     collect(next_steps.data) as outcomes
#                 ORDER BY score DESC
#                 LIMIT $limit
#                 """

#                 result = session.run(cypher, embedding=current_state_embedding, limit=limit)

#                 decisions = []
#                 for record in result:
#                     decisions.append(
#                         {
#                             "step_id": record["step_id"],
#                             "decision": json.loads(record["decision_data"]),
#                             "timestamp": record["decision_time"],
#                             "similarity": record["score"],
#                             "history": [json.loads(d) for d in record["history"]],
#                             "outcomes": [json.loads(d) for d in record["outcomes"]],
#                         }
#                     )

#                 return decisions

#         except Exception as e:
#             logger.error(f"Error finding similar decisions: {str(e)}")
#             return []

#     def semantic_search(self, query_embedding: list[float], top_k: int = 5) -> GraphContext:
#         """Perform semantic search using Neo4j vector index.

#         Args:
#             query_embedding: Query vector embedding
#             top_k: Number of results to return

#         Returns:
#             GraphContext with similar entities
#         """
#         try:
#             with self.driver.session() as session:
#                 cypher = """
#                 CALL db.index.vector.queryNodes('entityEmbeddings', $top_k, $embedding)
#                 YIELD node, score

#                 // Get additional context
#                 OPTIONAL MATCH (node)-[r]-(related)
#                 RETURN node, score, collect(DISTINCT related)[0..3] as related

#                 LIMIT $top_k
#                 """

#                 result = session.run(cypher, embedding=query_embedding, top_k=top_k)

#                 entities = []
#                 for record in result:
#                     entities.append(
#                         {
#                             "id": record["node"].id,
#                             "labels": list(record["node"].labels),
#                             "properties": dict(record["node"]),
#                             "score": record["score"],
#                             "related": [
#                                 {"id": rel.id, "labels": list(rel.labels), "properties": dict(rel)}
#                                 for rel in record["related"] or []
#                             ],
#                         }
#                     )

#                 return GraphContext(
#                     entities=entities,
#                     relationships=[],
#                     paths=[],
#                     confidence=entities[0]["score"] if entities else 0.0,
#                 )

#         except Exception as e:
#             logger.error(f"Error in semantic search: {str(e)}")
#             return GraphContext()

#     def _setup_indexes(self):
#         """Setup necessary indexes and constraints."""
#         try:
#             with self.driver.session() as session:
#                 # Entity name full-text index
#                 session.run("""
#                 CREATE FULLTEXT INDEX entityNames IF NOT EXISTS
#                 FOR (e:Entity)
#                 ON EACH [e.name, e.type, e.description]
#                 """)

#                 # Vector index for embeddings (Neo4j 5.11+)
#                 session.run("""
#                 CREATE VECTOR INDEX entityEmbeddings IF NOT EXISTS
#                 FOR (e:Entity)
#                 OPTIONS {indexConfig: {
#                     `vector.dimensions`: 1536,
#                     `vector.similarity_function`: 'cosine'
#                 }}
#                 ON e.embedding
#                 """)

#                 # Vector index for reasoning embeddings
#                 session.run("""
#                 CREATE VECTOR INDEX reasoningEmbeddings IF NOT EXISTS
#                 FOR (s:Step)
#                 OPTIONS {indexConfig: {
#                     `vector.dimensions`: 1536,
#                     `vector.similarity_function`: 'cosine'
#                 }}
#                 ON s.embedding
#                 """)

#                 # Unique constraints
#                 session.run("""
#                 CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
#                 FOR (e:Entity)
#                 REQUIRE e.id IS UNIQUE
#                 """)

#                 session.run("""
#                 CREATE CONSTRAINT step_id_unique IF NOT EXISTS
#                 FOR (s:Step)
#                 REQUIRE s.id IS UNIQUE
#                 """)

#                 logger.info("Indexes and constraints setup complete")

#         except Exception as e:
#             logger.warning(f"Error setting up indexes: {str(e)}")

#     def _ensure_graph_projection(self):
#         """Ensure GDS graph projection exists for community detection."""
#         try:
#             with self.driver.session() as session:
#                 # Check if projection exists
#                 result = session.run("""
#                 CALL gds.graph.exists('agentGraph') YIELD exists
#                 RETURN exists
#                 """)

#                 if not result.single()["exists"]:
#                     # Create graph projection
#                     session.run("""
#                     CALL gds.graph.project(
#                         'agentGraph',
#                         'Entity',
#                         {
#                             RELATION: {
#                                 orientation: 'UNDIRECTED'
#                             }
#                         },
#                         {
#                             nodeProperties: ['embedding'],
#                             relationshipProperties: ['weight', 'confidence']
#                         }
#                     )
#                     YIELD graphName
#                     """)
#                     logger.info("Created GDS graph projection 'agentGraph'")

#         except Exception as e:
#             logger.warning(f"Error ensuring graph projection: {str(e)}")

#     def find_semantic_match(
#         self, entity: str, embedding: list[float], threshold: float | None = None
#     ) -> str | None:
#         """Find semantically similar existing entities.

#         Args:
#             entity: Entity name to match
#             embedding: Entity embedding
#             threshold: Similarity threshold (uses class default if None)

#         Returns:
#             Name of matching entity or None
#         """
#         try:
#             threshold = threshold or self.similarity_threshold

#             with self.driver.session() as session:
#                 cypher = """
#                 CALL db.index.vector.queryNodes('entityEmbeddings', 5, $embedding)
#                 YIELD node, score
#                 WHERE score > $threshold AND node.name <> $entity
#                 RETURN node.name as name, score
#                 ORDER BY score DESC
#                 LIMIT 1
#                 """

#                 result = session.run(
#                     cypher, embedding=embedding, threshold=threshold, entity=entity
#                 )

#                 record = result.single()
#                 return record["name"] if record else None

#         except Exception as e:
#             logger.error(f"Error finding semantic match: {str(e)}")
#             return None

#     def _get_embedding(self, text: str) -> list[float]:
#         """Generate embedding for text (simplified implementation).

#         Args:
#             text: Text to embed

#         Returns:
#             Vector embedding
#         """
#         # In production, use proper embedding model (OpenAI, Sentence Transformers, etc.)
#         # This is a simplified hash-based placeholder
#         import hashlib

#         hash_obj = hashlib.md5(text.encode())
#         hash_hex = hash_obj.hexdigest()

#         # Convert to float vector
#         embedding = []
#         for i in range(0, len(hash_hex), 2):
#             hex_pair = hash_hex[i : i + 2]
#             embedding.append(int(hex_pair, 16) / 255.0)

#         # Pad to 1536 dimensions
#         while len(embedding) < 1536:
#             embedding.extend(embedding[: min(1536 - len(embedding), len(embedding))])

#         return embedding[:1536]

#     def prune_graph(self, confidence_threshold: float = 0.3, days_old: int = 30) -> dict[str, int]:
#         """Remove low-confidence and stale relationships.

#         Args:
#             confidence_threshold: Minimum confidence to keep
#             days_old: Age in days for stale relationships

#         Returns:
#             Dictionary with prune statistics
#         """
#         try:
#             stats = {"relationships_deleted": 0, "entities_deleted": 0}

#             with self.driver.session() as session:
#                 # Delete weak relationships
#                 result = session.run(
#                     """
#                 MATCH ()-[r:RELATION]->()
#                 WHERE r.confidence < $threshold
#                 OR (timestamp() - coalesce(r.last_verified, 0) > $cutoff_time)
#                 DELETE r
#                 RETURN count(r) as deleted
#                 """,
#                     threshold=confidence_threshold,
#                     cutoff_time=days_old * 24 * 60 * 60 * 1000,  # Convert to milliseconds
#                 )

#                 stats["relationships_deleted"] = result.single()["deleted"]

#                 # Delete orphaned entities
#                 result = session.run("""
#                 MATCH (e:Entity)
#                 WHERE NOT (e)-[]-()
#                 DELETE e
#                 RETURN count(e) as deleted
#                 """)

#                 stats["entities_deleted"] = result.single()["deleted"]

#                 logger.info(f"Pruned graph: {stats}")

#                 return stats

#         except Exception as e:
#             logger.error(f"Error pruning graph: {str(e)}")
#             return {"relationships_deleted": 0, "entities_deleted": 0}

#     def close(self):
#         """Close the database connection."""
#         if self.driver:
#             self.driver.close()


# Factory function
# def create_knowledge_graph_agent(
#     uri: str, user: str, password: str, similarity_threshold: float = 0.9
# ) -> KnowledgeGraphAgent:
#     """Create a KnowledgeGraphAgent instance.

#     Args:
#         uri: Neo4j URI
#         user: Username
#         password: Password
#         similarity_threshold: Threshold for entity similarity matching

#     Returns:
#         Configured KnowledgeGraphAgent
#     """
#     return KnowledgeGraphAgent(uri, user, password, similarity_threshold)
