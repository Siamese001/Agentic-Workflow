"""Knowledge Graph Integration for Agentic Architectures.

This module provides Neo4j integration patterns for augmenting agent capabilities
with graph-based reasoning, context retrieval, and state management.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
import json


logger = logging.getLogger(__name__)


class GraphContext(BaseModel):
    """Context retrieved from knowledge graph."""
    
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    paths: List[List[Dict[str, Any]]] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class KnowledgeGraphAgent:
    """Neo4j-powered knowledge graph agent for agentic architectures."""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize the knowledge graph agent.
        
        Args:
            uri: Neo4j database URI
            user: Database username
            password: Database password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Initialize indexes if needed
        self._setup_indexes()
        
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
            with self.driver.session() as session:
                # Hybrid semantic + graph query
                cypher = """
                // Find matching entities
                CALL db.index.fulltext.queryNodes('entityNames', $entity) 
                YIELD node, score
                WITH node, score
                // Explore neighborhood
                MATCH (node)-[r*1..$hops]-(related)
                RETURN DISTINCT 
                    node as central_entity,
                    related,
                    relationships(r) as rels,
                    score
                LIMIT $limit
                """
                
                result = session.run(cypher, entity=entity, hops=hops, limit=limit)
                
                entities = []
                relationships = []
                paths = []
                
                for record in result:
                    entities.append({
                        "id": record["central_entity"].id,
                        "labels": list(record["central_entity"].labels),
                        "properties": dict(record["central_entity"]),
                        "score": record["score"]
                    })
                    
                    if record["related"]:
                        entities.append({
                            "id": record["related"].id,
                            "labels": list(record["related"].labels),
                            "properties": dict(record["related"])
                        })
                    
                    # Process relationships
                    for rel in record["rels"] or []:
                        relationships.append({
                            "type": rel.type,
                            "properties": dict(rel),
                            "start": rel.start_node.id,
                            "end": rel.end_node.id
                        })
                
                return GraphContext(
                    entities=entities,
                    relationships=relationships,
                    paths=paths,
                    confidence=min(1.0, len(entities) / limit)
                )
                
        except Exception as e:
            logger.error(f"Error querying context: {str(e)}")
            return GraphContext()
    
    def store_relationship(
        self,
        subject: str,
        relation: str,
        object: str,
        confidence: float = 1.0,
        source: str = "agent"
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
            with self.driver.session() as session:
                cypher = """
                MERGE (s:Entity {name: $subject})
                MERGE (o:Entity {name: $object})
                MERGE (s)-[r:RELATION {type: $relation}]->(o)
                SET r.confidence = $confidence, 
                    r.source = $source,
                    r.timestamp = datetime(),
                    r.updated = datetime()
                RETURN r
                """
                
                session.run(cypher, 
                    subject=subject, 
                    object=object, 
                    relation=relation,
                    confidence=confidence,
                    source=source
                )
                
                logger.debug(f"Stored relationship: {subject}-{relation}->{object}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing relationship: {str(e)}")
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
                cypher = """
                MATCH (n {id: $node_id})
                CALL apoc.path.expandConfig(n, {
                    relationshipFilter: ">", 
                    minLevel: 1, 
                    maxLevel: $hops
                })
                YIELD path
                UNWIND nodes(path) as node
                UNWIND relationships(path) as rel
                RETURN DISTINCT 
                    collect(DISTINCT node) as nodes,
                    collect(DISTINCT rel) as rels
                """
                
                result = session.run(cypher, node_id=node_id, hops=hops)
                record = result.single()
                
                if record:
                    entities = [
                        {
                            "id": node.id,
                            "labels": list(node.labels),
                            "properties": dict(node)
                        }
                        for node in record["nodes"]
                    ]
                    
                    relationships = [
                        {
                            "type": rel.type,
                            "properties": dict(rel),
                            "start": rel.start_node.id,
                            "end": rel.end_node.id
                        }
                        for rel in record["rels"]
                    ]
                    
                    return GraphContext(
                        entities=entities,
                        relationships=relationships,
                        paths=[],
                        confidence=1.0
                    )
                
                return GraphContext()
                
        except Exception as e:
            logger.error(f"Error getting neighborhood: {str(e)}")
            return GraphContext()
    
    def create_reasoning_step(
        self,
        agent_id: str,
        step_id: str,
        step_data: Dict[str, Any]
    ) -> bool:
        """Create a reasoning step in the agent's decision chain.
        
        Args:
            agent_id: Agent identifier
            step_id: Step identifier
            step_data: Step data
            
        Returns:
            True if successful
        """
        try:
            with self.driver.session() as session:
                cypher = """
                // Create new step
                CREATE (s:Step {
                    id: $step_id,
                    agent_id: $agent_id,
                    data: $data,
                    timestamp: datetime()
                })
                
                // Link to agent and previous step
                WITH s
                MATCH (a:Agent {id: $agent_id})
                OPTIONAL MATCH (a)-[:LAST_STEP]->(prev)
                
                // Update agent's last step
                DETACH DELETE (a)-[:LAST_STEP]->()
                MERGE (a)-[:LAST_STEP]->(s)
                
                // Link to previous step
                FOREACH(_ IN CASE WHEN prev IS NOT NULL THEN [1] ELSE [] END |
                    MERGE (prev)-[:NEXT]->(s))
                
                RETURN s
                """
                
                session.run(cypher,
                    agent_id=agent_id,
                    step_id=step_id,
                    data=json.dumps(step_data)
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Error creating reasoning step: {str(e)}")
            return False
    
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
                cypher = """
                CALL db.index.vector.queryNodes('entityEmbeddings', $top_k, $embedding)
                YIELD node, score
                
                // Get additional context
                OPTIONAL MATCH (node)-[r]-(related)
                RETURN node, score, collect(DISTINCT related)[0..3] as related
                
                LIMIT $top_k
                """
                
                result = session.run(cypher,
                    embedding=query_embedding,
                    top_k=top_k
                )
                
                entities = []
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
                    entities=entities,
                    relationships=[],
                    paths=[],
                    confidence=entities[0]["score"] if entities else 0.0
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
                CREATE FULLTEXT INDEX entityNames IF NOT EXISTS 
                FOR (e:Entity) 
                ON EACH [e.name, e.type, e.description]
                """)
                
                # Vector index for embeddings (Neo4j 5.11+)
                session.run("""
                CREATE VECTOR INDEX entityEmbeddings IF NOT EXISTS 
                FOR (e:Entity) 
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 1536,
                    `vector.similarity_function`: 'cosine'
                }}
                ON e.embedding
                """)
                
                # Unique constraints
                session.run("""
                CREATE CONSTRAINT entity_id_unique IF NOT EXISTS 
                FOR (e:Entity) 
                REQUIRE e.id IS UNIQUE
                """)
                
                logger.info("Indexes and constraints setup complete")
                
        except Exception as e:
            logger.warning(f"Error setting up indexes: {str(e)}")
    
    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()


# Factory function
def create_knowledge_graph_agent(
    uri: str,
    user: str,
    password: str
) -> KnowledgeGraphAgent:
    """Create a KnowledgeGraphAgent instance.
    
    Args:
        uri: Neo4j URI
        user: Username
        password: Password
        
    Returns:
        Configured KnowledgeGraphAgent
    """
    return KnowledgeGraphAgent(uri, user, password)
