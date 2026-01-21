import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from connection_manager import ConnectionFactory
from redisvl.query import VectorQuery
from schemas_connectivity import (
    CanonEntry,
    CanonQuery,
    generate_ast_structure,
    validate_ast_integrity,
)

logger = logging.getLogger(__name__)


class CanonValidator:
    """
    The L5 Meta-Learner for Canon validation.

    Implements the check_and_learn and update_learning methods
    using RedisVL for L1 and Pinecone for L2 storage.
    """

    def __init__(self):
        """Initialize the Canon Validator."""
        # Get connections
        self.redis_conn = ConnectionFactory.get_redis_connection()
        self.pinecone = ConnectionFactory.get_pinecone_index()
        self.embed_func = ConnectionFactory.get_embedding_function()

        # Get indexes
        self.redis_index = ConnectionFactory.create_redis_index(None)
        self.pinecone_index = os.getenv(
            "PINECONE_INDEX_NAME", "canon-memory-l2")

        # Configuration
        self.failure_threshold = int(os.getenv("FAILURE_THRESHOLD", "5"))
        self.success_threshold = int(os.getenv("SUCCESS_THRESHOLD", "3"))

        logger.info("CanonValidator initialized with RedisVL and Pinecone")

    def check_and_learn(self, new_code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check code against the Canon and learn from results.

        Process:
        1. Generate embedding/AST for new_code
        2. Query L1 (Redis) with hybrid filter: failure_count < 5
        3. If miss, query L2 (Pinecone)
        4. If hit, validate AST structure

        Args:
            new_code: Python code to validate
            context: Optional context information

        Returns:
            Dictionary with validation result and metadata
        """
        start_time = datetime.utcnow()

        # Generate embedding and AST
        embedding = self.embed_func(f"Code validation: {new_code[:100]}...")
        ast_structure = generate_ast_structure(new_code)

        # Check if code is syntactically valid
        if not validate_ast_integrity(ast_structure):
            return {
                "is_valid": False,
                "confidence": 0.0,
                "error": "Invalid Python syntax",
                "ast_error": ast_structure.get("error"),
                "source": "syntax_check",
                "matched_pattern": None,
                "recommendation": "Fix syntax errors before validation"
            }

        # Prepare query
        query = CanonQuery(
            text=new_code[:200],  # First 200 chars for context
            filter_failures=True,
            max_results=10,
            threshold=0.7,
            project_context=context.get("project_context") if context else None
        )

        # Query L1 (Redis) first
        l1_results = self._query_redis(embedding, query)

        if l1_results:
            # Found match in L1
            best_match = l1_results[0]
            validation = self._validate_ast_match(
                new_code, ast_structure, best_match.entry)

            result = {
                "is_valid": validation["is_valid"],
                "confidence": best_match.score,
                "source": "L1_Redis",
                "matched_pattern": best_match.entry.id,
                "ast_match": validation["is_match"],
                "recommendation": validation["recommendation"],
                "query_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }

            logger.info(
                f"L1 match found: {best_match.entry.id} with score {best_match.score:.3f}")
            return result

        # Query L2 (Pinecone) if no L1 match
        logger.info("No L1 match found, querying L2...")
        l2_results = self._query_pinecone(embedding, query)

        if l2_results:
            # Found match in L2
            best_match = l2_results[0]
            validation = self._validate_ast_match(
                new_code, ast_structure, best_match.entry)

            # Promote to L1 if valid
            if validation["is_valid"]:
                self._promote_to_l1(best_match.entry)

            result = {
                "is_valid": validation["is_valid"],
                "confidence": best_match.score,
                "source": "L2_Pinecone",
                "matched_pattern": best_match.entry.id,
                "ast_match": validation["is_match"],
                "recommendation": validation["recommendation"],
                "query_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }

            logger.info(
                f"L2 match found: {best_match.entry.id} with score {best_match.score:.3f}")
            return result

        # No matches found - store the new pattern
        import uuid
        pattern_id = str(uuid.uuid4())

        # Store in Redis (L1)
        try:
            redis_data = {
                "id": pattern_id,
                "code_snippet": new_code,
                "embedding": embedding,
                "failure_count": 0,
                "success_count": 0,
                "project_context": context.get("project_context", "default") if context else "default",
                "canon_rule_id": context.get("type", "unknown") if context else "unknown",
                "last_validated": datetime.utcnow().isoformat()
            }

            # Create and load into Redis
            embedding_attrs = {
                "dims": len(embedding),
                "distance_metric": "cosine",
                "algorithm": "hnsw"
            }
            redis_schema = {
                "index": {
                    "name": "canon-index",
                    "prefix": "canon:",
                    "storage_type": "hash"
                },
                "fields": [
                    {"name": "id", "type": "tag"},
                    {"name": "code_snippet", "type": "text"},
                    {"name": "embedding", "type": "vector", "attrs": embedding_attrs},
                    {"name": "failure_count", "type": "numeric"},
                    {"name": "success_count", "type": "numeric"},
                    {"name": "project_context", "type": "tag"},
                    {"name": "canon_rule_id", "type": "tag"},
                    {"name": "last_validated", "type": "numeric"}
                ]
            }

            # Load data using the key format expected by RedisVL
            redis_key = f"canon:{pattern_id}"
            # Convert embedding to string representation that RedisVL can parse
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            self.redis_conn.hset(redis_key, mapping={
                "id": pattern_id,
                "code_snippet": new_code,
                "embedding": embedding_str,  # Store as list string for RedisVL
                "failure_count": "0",
                "success_count": "0",
                "project_context": context.get("project_context", "default") if context else "default",
                "canon_rule_id": context.get("type", "unknown") if context else "unknown",
                "last_validated": str(int(datetime.utcnow().timestamp()))
            })
            logger.info(f"✅ Stored new pattern in Redis: {pattern_id}")

        except Exception as e:
            logger.error(f"Failed to store in Redis: {e}")

        # Store in Pinecone (L2)
        try:
            index = self.pinecone.Index(self.pinecone_index)
            pinecone_data = [{
                "id": pattern_id,
                "values": embedding,
                "metadata": {
                    "code_snippet": new_code[:500],  # First 500 chars
                    "project_context": context.get("project_context", "default") if context else "default",
                    "canon_rule_id": context.get("type", "unknown") if context else "unknown",
                    "failure_count": 0,
                    "success_count": 0
                }
            }]
            index.upsert(pinecone_data)
            logger.info(f"✅ Stored new pattern in Pinecone: {pattern_id}")
        except Exception as e:
            logger.error(f"Failed to store in Pinecone: {e}")

        result = {
            "is_valid": True,  # New code is assumed valid
            "confidence": 1.0,
            "source": "no_match",
            "matched_pattern": None,
            "ast_match": False,
            "recommendation": "New code pattern - stored in Canon",
            "pattern_id": pattern_id,
            "query_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
        }

        logger.info("No matches found in L1 or L2 - stored new pattern")
        return result

    def _query_redis(self, embedding: List[float], query: CanonQuery) -> List[Dict[str, Any]]:
        """Query RedisVL for similar patterns."""
        try:
            # Build vector query
            vector_query = VectorQuery(
                vector=embedding,
                vector_field_name="embedding",
                return_fields=[
                    "id", "code_snippet", "failure_count", "success_count",
                    "project_context", "canon_rule_id", "last_validated"
                ],
                num_results=query.max_results,
                return_score=True
            )

            # Add hybrid filter if requested
            if query.filter_failures:
                vector_query.set_filter(
                    f"failure_count < {self.failure_threshold}")

            if query.project_context:
                project_filter = f"@project_context:{{{query.project_context}}}"
                if vector_query.filter:
                    vector_query.filter += f" {project_filter}"
                else:
                    vector_query.set_filter(project_filter)

            # Execute query
            results = self.redis_index.query(vector_query)

            # Convert to CanonEntry objects
            entries = []
            for result in results:
                if result.score >= query.threshold:
                    # Create partial CanonEntry (without full AST)
                    entry = CanonEntry(
                        id=result["id"],
                        code_snippet=result["code_snippet"],
                        ast_structure={},  # Not loaded from Redis for performance
                        embedding=embedding,  # Use query embedding
                        metadata={
                            "failure_count": result["failure_count"],
                            "success_count": result["success_count"],
                            "project_context": result["project_context"],
                            "canon_rule_id": result["canon_rule_id"]
                        }
                    )
                    entries.append({"entry": entry, "score": result.score})

            return entries

        except Exception as e:
            logger.error(f"Redis query failed: {e}")
            return []

    def _query_pinecone(self, embedding: List[float], query: CanonQuery) -> List[Dict[str, Any]]:
        """Query Pinecone for similar patterns."""
        try:
            # Get Pinecone index
            index = self.pinecone.Index(self.pinecone_index)

            # Build filter
            filter_dict = {}
            if query.filter_failures:
                filter_dict["failure_count"] = {"$lt": self.failure_threshold}
            if query.project_context:
                filter_dict["project_context"] = query.project_context

            # Query Pinecone
            results = index.query(
                vector=embedding,
                top_k=query.max_results,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )

            # Convert to CanonEntry objects
            entries = []
            for match in results["matches"]:
                if match["score"] >= query.threshold:
                    metadata = match["metadata"]

                    entry = CanonEntry(
                        id=match["id"],
                        code_snippet=metadata["code_snippet"],
                        ast_structure=metadata["ast_structure"],
                        embedding=match["values"],
                        metadata={
                            "failure_count": metadata["failure_count"],
                            "success_count": metadata["success_count"],
                            "project_context": metadata["project_context"],
                            "canon_rule_id": metadata["canon_rule_id"]
                        }
                    )
                    entries.append({"entry": entry, "score": match["score"]})

            return entries

        except Exception as e:
            logger.error(f"Pinecone query failed: {e}")
            return []

    def _validate_ast_match(
        self,
        new_code: str,
        new_ast: Dict[str, Any],
        existing_entry: CanonEntry
    ) -> Dict[str, Any]:
        """Validate AST structure match."""
        # Simple AST similarity check
        similarity = self._calculate_ast_similarity(
            new_ast, existing_entry.ast_structure)

        # Check success rate
        success_rate = existing_entry.metadata.success_rate

        # Determine validity
        is_match = similarity > 0.7
        is_valid = is_match and success_rate > 0.5

        return {
            "is_match": is_match,
            "is_valid": is_valid,
            "similarity": similarity,
            "success_rate": success_rate,
            "recommendation": self._generate_recommendation(similarity, success_rate)
        }

    def _calculate_ast_similarity(self, ast1: Dict[str, Any], ast2: Dict[str, Any]) -> float:
        """Calculate AST similarity score."""
        # Simplified similarity calculation
        # In production, this would use more sophisticated algorithms
        try:
            import ast

            # Parse ASTs
            tree1 = ast.parse(ast1.get("body", "{}"))
            tree2 = ast.parse(ast2.get("body", "{}"))

            # Compare node types
            types1 = set(type(node).__name__ for node in ast.walk(tree1))
            types2 = set(type(node).__name__ for node in ast.walk(tree2))

            # Jaccard similarity
            intersection = len(types1.intersection(types2))
            union = len(types1.union(types2))

            return intersection / union if union > 0 else 0.0
        except Exception as e:
            logger.error(f"AST similarity calculation failed: {e}")
            return 0.0

    def _generate_recommendation(self, similarity: float, success_rate: float) -> str:
        """Generate recommendation based on similarity and success rate."""
        if similarity > 0.8 and success_rate > 0.8:
            return "Strong match with successful pattern - proceed"
        elif similarity > 0.7 and success_rate > 0.5:
            return "Pattern matches but has mixed results - review carefully"
        elif similarity > 0.7 and success_rate <= 0.5:
            return "Pattern matches known failure - avoid this approach"
        else:
            return "Low similarity - new pattern, validate thoroughly"

    def _promote_to_l1(self, entry: CanonEntry):
        """Promote a pattern from L2 to L1."""
        try:
            # Convert to Redis fields
            fields = entry.to_redis_fields()

            # Store in Redis
            key = f"canon:{fields['id']}"
            self.redis_conn.client.hset(key, mapping=fields)

            # Add to search index
            self.redis_index.load([{
                "id": fields["id"],
                "embedding": fields["embedding"],
                "failure_count": fields["failure_count"],
                "success_count": fields["success_count"],
                "project_context": fields["project_context"],
                "canon_rule_id": fields["canon_rule_id"],
                "last_validated": fields["last_validated"]
            }])

            logger.info(f"Promoted pattern {entry.id} to L1")

        except Exception as e:
            logger.error(f"Failed to promote pattern to L1: {e}")

    def update_learning(self, entry_id: str, outcome: bool, error_trace: Optional[str] = None):
        """
        Update learning based on execution outcome.

        Args:
            entry_id: ID of the pattern to update
            outcome: True for success, False for failure
            error_trace: Optional error trace for failures
        """
        try:
            # Get entry from Redis first
            key = f"canon:{entry_id}"
            fields = self.redis_conn.client.hgetall(key)

            if not fields:
                # Try Pinecone if not in Redis
                self._update_pinecone_learning(entry_id, outcome, error_trace)
                return

            # Update counts
            if outcome:
                fields["success_count"] = int(
                    fields.get("success_count", 0)) + 1
            else:
                fields["failure_count"] = int(
                    fields.get("failure_count", 0)) + 1

            fields["last_validated"] = datetime.utcnow().isoformat()

            # Update Redis
            self.redis_conn.client.hset(key, mapping=fields)

            # Check for promotion to L2
            if int(fields["success_count"]) >= self.success_threshold:
                self._promote_to_l2(entry_id, fields)

            logger.info(
                f"Updated learning for {entry_id}: {'SUCCESS' if outcome else 'FAILURE'}")

        except Exception as e:
            logger.error(f"Failed to update learning: {e}")

    def _update_pinecone_learning(self, entry_id: str, outcome: bool, error_trace: Optional[str]):
        """Update learning in Pinecone when not in Redis."""
        try:
            index = self.pinecone.Index(self.pinecone_index)

            # Fetch from Pinecone
            results = index.fetch(ids=[entry_id])

            if entry_id in results["vectors"]:
                vector = results["vectors"][entry_id]
                metadata = vector["metadata"]

                # Update counts
                if outcome:
                    metadata["success_count"] += 1
                else:
                    metadata["failure_count"] += 1

                metadata["last_validated"] = datetime.utcnow().isoformat()

                # Update Pinecone
                index.upsert(vectors=[{
                    "id": entry_id,
                    "values": vector["values"],
                    "metadata": metadata
                }])

                logger.info(f"Updated Pinecone learning for {entry_id}")

        except Exception as e:
            logger.error(f"Failed to update Pinecone learning: {e}")

    def _promote_to_l2(self, entry_id: str, fields: Dict[str, Any]):
        """Promote a successful pattern to L2."""
        try:
            # Get full entry from Redis
            entry = CanonEntry.from_redis_fields(fields)

            # Convert to Pinecone format
            vector = entry.to_pinecone_vector()

            # Upsert to Pinecone
            index = self.pinecone.Index(self.pinecone_index)
            index.upsert(vectors=[vector])

            logger.info(f"Promoted pattern {entry_id} to L2")

        except Exception as e:
            logger.error(f"Failed to promote to L2: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get Canon validator statistics."""
        stats = {
            "redis_stats": {},
            "pinecone_stats": {},
            "thresholds": {
                "failure_threshold": self.failure_threshold,
                "success_threshold": self.success_threshold
            }
        }

        # Redis stats
        try:
            redis_info = self.redis_conn.client.info()
            stats["redis_stats"] = {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory": redis_info.get("used_memory_human", "0B"),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")

        # Pinecone stats
        try:
            index = self.pinecone.Index(self.pinecone_index)
            index_stats = index.describe_index_stats()
            stats["pinecone_stats"] = {
                "vector_count": index_stats.get("total_vector_count", 0),
                "dimension": index_stats.get("dimension", 0),
                "index_fullness": index_stats.get("index_fullness", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")

        return stats
