import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np

# Import our hardened schemas and connection manager
from schemas_connectivity import CanonEntry
from connection_manager import ConnectionManager
from redisvl.query import VectorQuery
from redisvl.query.filter import Tag, FilterExpression

logger = logging.getLogger(__name__)

class CanonValidator:
    """
    The Gatekeeper logic that enforces the 'Subatomic' canon.
    Uses a 2-stage cache (L1 Redis Hot, L2 Pinecone Cold) to validate incoming patterns.
    """
    
    def __init__(self, similarity_threshold: float = 0.75): # Lowered to catch code vs comment similarities
        self.cm = ConnectionManager()
        self.similarity_threshold = similarity_threshold
        
        # Initialize connections immediately
        self.redis_index = self.cm.get_redis_index()
        self.pinecone_index = self.cm.get_pinecone_index()
        self.embedding_fn = self.cm.get_embedding

    def process_entry(self, entry: CanonEntry) -> Dict[str, Any]:
        """
        Main entry point.
        1. Checks L1 (Redis) for exact AST match.
        2. Checks L2 (Pinecone) for semantic similarity.
        3. Decides whether to Ingest, Reject, or Flag.
        """
        start_time = time.time()
        
        # 1. Generate Embedding if missing
        if not entry.embedding:
            try:
                entry.embedding = self.embedding_fn(entry.content)
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                return {"status": "error", "message": str(e)}

        # 2. Check L1: Exact AST/Hash Match (Hot Memory)
        l1_match = self._check_l1_cache(entry)
        if l1_match:
            return self._format_result(l1_match, "l1_exact_match", start_time)

        # 3. Check L2: Semantic Similarity (Cold Memory)
        l2_match = self._check_l2_cache(entry)
        if l2_match:
            return self._format_result(l2_match, "l2_semantic_match", start_time)

        # 4. No Match Found -> Ingest as New Canon
        return self._ingest_new_entry(entry, start_time)
    
    def check_and_learn(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Compatibility method for simulation script.
        Accepts raw string input and converts to CanonEntry.
        """
        from schemas_connectivity import CanonEntry, CanonMetadata
        
        # Generate embedding first to meet validation requirements
        try:
            embedding = self.embedding_fn(code)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return {"status": "error", "message": str(e)}
        
        # Create CanonEntry from string input
        entry = CanonEntry(
            code_snippet=code,
            ast_structure={"type": "module"},  # Simple AST structure
            embedding=embedding,  # Now has valid embedding
            metadata=CanonMetadata(
                project_context=context.get("project_context", "default") if context else "default",
                canon_rule_id=context.get("type", "unknown") if context else "unknown"
            )
        )
        
        # Delegate to process_entry
        result = self.process_entry(entry)
        
        # Convert status to expected format for simulation
        if result.get("status") == "duplicate":
            result["source"] = "l1_match"
        elif result.get("status") == "similar":
            result["source"] = "l2_match"
        elif result.get("status") == "ingested":
            result["source"] = "no_match"
            result["is_valid"] = True
            
        return result

    def _check_l1_cache(self, entry: CanonEntry) -> Optional[Dict[str, Any]]:
        """
        Queries Redis for an exact match on the AST hash or Content Hash.
        """
        try:
            # We use the Tag filter for exact matching on the 'ast_hash' field
            # Note: Ensure schema definitions in redisvl match this field name
            t = Tag("ast_hash") == entry.ast_hash
            
            # Construct a VectorQuery but with a filter that creates a strict candidate set
            # We set num_results=1 because we only care if it exists
            query = VectorQuery(
                vector=entry.embedding,
                vector_field_name="embedding",  # Match schema field name
                return_fields=["id", "content", "ast_hash", "metadata"],
                filter_expression=t,
                num_results=1
            )
            
            results = self.redis_index.query(query)
            
            if results and len(results) > 0:
                match = results[0]
                # RedisVL returns a dict. We parse the JSON metadata string back to dict if needed
                meta = match.get("metadata")
                if isinstance(meta, str):
                    meta = json.loads(meta)
                    
                return {
                    "id": match.get("id"),
                    "content": match.get("content"),
                    "similarity": 1.0, # Exact tag match implies 100% logic match
                    "metadata": meta
                }
                
        except Exception as e:
            # Log specific query error but don't crash
            logger.error(f"Redis query failed: {e}")
            
        return None

    def _check_l2_cache(self, entry: CanonEntry) -> Optional[Dict[str, Any]]:
        """
        Queries Pinecone for semantic similarity.
        """
        try:
            # query() expects a list of floats
            logger.info(f"Querying Pinecone with embedding dimension: {len(entry.embedding)}")
            results = self.pinecone_index.query(
                vector=entry.embedding,
                top_k=1,
                include_metadata=True
            )
            
            logger.info(f"Pinecone raw response: {results}")
            
            if results and results['matches']:
                best_match = results['matches'][0]
                score = best_match['score']
                logger.info(f"Best match: ID={best_match['id']}, score={score}")
                
                if score >= self.similarity_threshold:
                    # FIX: Access metadata safely
                    metadata = best_match.get('metadata', {})
                    
                    return {
                        "id": best_match['id'],
                        "content": metadata.get('content', 'Content not in metadata'),
                        "similarity": score,
                        "metadata": metadata
                    }
                    
        except Exception as e:
            logger.error(f"Pinecone query failed: {e}")
            
        return None

    def _ingest_new_entry(self, entry: CanonEntry, start_time: float) -> Dict[str, Any]:
        """
        Writes the new unique entry to both L1 (Redis) and L2 (Pinecone).
        """
        try:
            # 1. Write to Redis (Hot)
            redis_data = entry.to_redis_dict()
            self.redis_index.load([redis_data])
            logger.info(f"✅ Stored new pattern in Redis: {entry.id}")
            
            # 2. Write to Pinecone (Cold)
            pinecone_record = entry.to_pinecone_record()
            self.pinecone_index.upsert(vectors=[pinecone_record])
            logger.info(f"✅ Stored new pattern in Pinecone: {entry.id}")
            
            return {
                "status": "ingested",
                "is_valid": True,
                "confidence": 1.0,
                "source": "no_match",
                "matched_pattern": None,
                "ast_match": False,
                "recommendation": "New code pattern - stored in Canon",
                "pattern_id": entry.id,
                "query_time_ms": (time.time() - start_time) * 1000
            }
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return {
                "status": "error", 
                "message": f"Ingestion failed: {str(e)}",
                "query_time_ms": (time.time() - start_time) * 1000
            }

    def _format_result(self, match: Dict, source: str, start_time: float) -> Dict[str, Any]:
        """
        Helper to format a 'Duplicate Found' response.
        """
        status = "duplicate" if source == "l1_exact_match" else "similar"
        
        return {
            "status": status, # Crucial for the simulator to detect 'duplicate'
            "is_valid": True, # It is valid logic, just redundant
            "confidence": match['similarity'],
            "source": source,
            "matched_pattern": match['id'],
            "ast_match": (source == "l1_exact_match"),
            "recommendation": "Use existing pattern",
            "metadata": match.get('metadata'),
            "query_time_ms": (time.time() - start_time) * 1000
        }
