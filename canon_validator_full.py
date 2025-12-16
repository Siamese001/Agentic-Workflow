"""
Canon Validator - The Core Gatekeeper of Agentic Architecture

Implements a 5-Stage Validation Loop:
1. Embedding Generation
2. L1 Semantic Cache (Redis)
3. L2 Canon Retrieval (Pinecone)
4. Consensus Validation (LLM)
5. Meta-Learning (Write-Back)

Integrates ConnectionManager, LLMClient, and schemas_connectivity modules.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

# Import required modules
from connection_manager import ConnectionFactory, ConnectionManager
from llm_client import LLMClient
from schemas_connectivity import CanonEntry, CanonMetadata, generate_ast_structure

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CanonValidator")

# Try to import redisvl
try:
    from redisvl.query import VectorQuery
    REDISVL_AVAILABLE = True
except ImportError:
    REDISVL_AVAILABLE = False
    logger.warning("redisvl not installed - L1 cache will be disabled")


class CanonValidator:
    """
    The Full Canon Validator with 5-Stage Validation Loop.

    Integrates semantic cache (Redis), long-term memory (Pinecone),
    and consensus engine (LLMClient) into a unified self-improving loop.
    """

    # Cache the embedding model to avoid repeated loading
    _embedding_function = None

    def __init__(self):
        """Initialize the Canon Validator with all components."""
        logger.info("🚀 Initializing Canon Validator...")

        # Initialize core components
        self.connection_manager = ConnectionManager()
        self.llm_client = LLMClient()

        # Initialize connections
        self.redis_index = None
        self.pinecone_index = None

        try:
            self.redis_index = self.connection_manager.get_redis_index()
            logger.info("✅ L1 Semantic Cache (Redis) ready")
        except Exception as e:
            logger.warning(f"⚠️ L1 Cache initialization failed: {e}")

        try:
            self.pinecone_index = self.connection_manager.get_pinecone_index()
            logger.info("✅ L2 Canon Memory (Pinecone) ready")
        except Exception as e:
            logger.warning(f"⚠️ L2 Memory initialization failed: {e}")

        # Configuration
        self.semantic_threshold = float(
            os.getenv("SEMANTIC_THRESHOLD", "0.05"))
        self.max_retrieval_rules = int(os.getenv("MAX_RETRIEVAL_RULES", "3"))
        # 24 hours default
        self.cache_ttl = int(os.getenv("CACHE_TTL", "86400"))
        self.write_back_rate_limit = int(
            os.getenv("WRITE_BACK_RATE_LIMIT", "10"))  # per minute
        self._last_write_back = []  # Track write-backs for rate limiting

        logger.info("🎯 Canon Validator initialization complete")

    def validate(self, content: str, source: str = "user") -> Dict[str, Any]:
        """
        Main validation method implementing the 5-Stage Loop.

        Args:
            content: The content to validate
            source: Source identifier for tracking

        Returns:
            Validation result with metadata
        """
        start_time = time.time()
        logger.info(f"🔍 Starting validation for content from {source}")

        # Initialize result structure
        result = {
            "content": content,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "is_valid": False,
            "confidence": 0.0,
            "stages": {},
            "latency_ms": 0,
            "metadata": {}
        }

        try:
            # Stage 1: Embedding Generation
            embedding, stage1_time = self._stage1_generate_embedding(content)
            result["stages"]["embedding"] = {
                "status": "success",
                "latency_ms": stage1_time * 1000,
                "embedding_dim": len(embedding)
            }

            # Stage 2: L1 Semantic Cache Check
            cache_result, stage2_time = self._stage2_check_l1_cache(embedding)
            result["stages"]["l1_cache"] = {
                "status": "hit" if cache_result else "miss",
                "latency_ms": stage2_time * 1000
            }

            if cache_result:
                # L1 Hit - return cached result immediately
                result.update({
                    "is_valid": cache_result["is_valid"],
                    "confidence": cache_result["confidence"],
                    "reason": cache_result["reason"],
                    "source": "l1_cache"
                })
                result["latency_ms"] = (time.time() - start_time) * 1000
                logger.info(
                    f"⚡ L1 Cache hit - validation complete in {result['latency_ms']:.2f}ms")
                return result

            # Stage 3: L2 Canon Retrieval
            canon_rules, stage3_time = self._stage3_retrieve_canon_rules(
                embedding)
            result["stages"]["l2_retrieval"] = {
                "status": "success" if canon_rules else "no_rules",
                "latency_ms": stage3_time * 1000,
                "rules_found": len(canon_rules)
            }

            # Stage 4: Consensus Validation
            validation_result, stage4_time = self._stage4_consensus_validation(
                content, canon_rules)
            result["stages"]["consensus"] = {
                "status": "success",
                "latency_ms": stage4_time * 1000,
                "model_mode": "consensus_high"
            }

            result.update(validation_result)

            # Stage 5: Meta-Learning Write-Back
            if result["is_valid"]:
                writeback_success, stage5_time = self._stage5_write_back(
                    content, embedding, result)
                result["stages"]["write_back"] = {
                    "status": "success" if writeback_success else "failed",
                    "latency_ms": stage5_time * 1000
                }
            else:
                result["stages"]["write_back"] = {
                    "status": "skipped", "latency_ms": 0}

            # Final metrics
            result["latency_ms"] = (time.time() - start_time) * 1000
            logger.info(
                f"✅ Validation complete in {result['latency_ms']:.2f}ms - Valid: {result['is_valid']}")

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            result["error"] = str(e)
            result["latency_ms"] = (time.time() - start_time) * 1000

        return result

    def _stage1_generate_embedding(self, content: str) -> Tuple[List[float], float]:
        """Stage 1: Generate embedding for the content."""
        start = time.time()

        # Use cached embedding function to avoid model reload
        if self._embedding_function is None:
            self._embedding_function = self.connection_manager.get_embedding()
            logger.info("📦 Embedding model cached for reuse")

        embedding = self._embedding_function(content)
        elapsed = time.time() - start
        logger.debug(
            f"🎯 Embedding generated ({len(embedding)}D) in {elapsed*1000:.2f}ms")
        return embedding, elapsed

    def _stage2_check_l1_cache(self, embedding: List[float]) -> Tuple[Optional[Dict[str, Any]], float]:
        """Stage 2: Check L1 semantic cache in Redis."""
        start = time.time()

        if not self.redis_index or not REDISVL_AVAILABLE:
            logger.debug("⚠️ L1 cache not available")
            return None, time.time() - start

        try:
            # Create vector query for semantic similarity (fixed API)
            query = VectorQuery(
                vector=embedding,
                vector_field_name="embedding",
                return_fields=["content", "is_valid",
                               "confidence", "reason", "timestamp"],
                num_results=1
            )

            # Execute query
            results = self.redis_index.query(query)

            if results:
                # Found cached result - check distance threshold manually
                cached = results[0]
                if cached.distance <= self.semantic_threshold:
                    logger.debug(
                        f"⚡ L1 Cache hit (distance: {cached.distance:.4f})")
                    return {
                        "is_valid": cached.is_valid == "True",
                        "confidence": float(cached.confidence),
                        "reason": cached.reason,
                        "timestamp": cached.timestamp
                    }, time.time() - start
                else:
                    logger.debug(
                        f"🔍 L1 Cache miss (distance: {cached.distance:.4f} > {self.semantic_threshold})")

        except Exception as e:
            logger.warning(f"⚠️ L1 cache query failed: {e}")

        logger.debug("🔍 L1 Cache miss")
        return None, time.time() - start

    def _stage3_retrieve_canon_rules(self, embedding: List[float]) -> Tuple[List[Dict[str, Any]], float]:
        """Stage 3: Retrieve relevant canon rules from Pinecone."""
        start = time.time()

        if not self.pinecone_index:
            logger.debug("⚠️ L2 memory not available")
            return [], time.time() - start

        try:
            # Query Pinecone for similar rules
            results = self.pinecone_index.query(
                vector=embedding,
                top_k=self.max_retrieval_rules,
                include_metadata=True
            )

            rules = []
            for match in results.get("matches", []):
                if match["score"] > 0.7:  # Similarity threshold
                    rules.append({
                        "id": match["id"],
                        "content": match["metadata"].get("content", ""),
                        "score": match["score"],
                        "metadata": match["metadata"]
                    })

            logger.debug(f"📚 Retrieved {len(rules)} canon rules from L2")
            return rules, time.time() - start

        except Exception as e:
            logger.warning(f"⚠️ L2 retrieval failed: {e}")
            return [], time.time() - start

    def _stage4_consensus_validation(self, content: str, canon_rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
        """Stage 4: Consensus validation using LLMClient in high mode."""
        start = time.time()

        # Build system prompt
        system_prompt = self._build_validation_system_prompt(canon_rules)

        # Build user prompt
        user_prompt = f"""
Please validate the following content against the retrieved Canon Rules:

CONTENT TO VALIDATE:
{content}

RETRIEVED CANON RULES:
{json.dumps(canon_rules, indent=2) if canon_rules else "No rules found - evaluate based on general quality principles"}

Respond with a JSON object containing:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "reason": "Detailed explanation of validation decision",
    "applied_rules": ["list of rule IDs that applied"],
    "suggestions": ["list of improvements if invalid"]
}}
"""

        try:
            # Use LLMClient in high complexity mode for consensus
            try:
                response = self.llm_client.generate_plan(
                    system_context=system_prompt,
                    user_goal=user_prompt,
                    complexity="high"
                )
            except Exception as llm_error:
                logger.warning(f"⚠️ High complexity LLM failed: {llm_error}")
                # Fallback to mini mode
                logger.info("🔄 Falling back to mini mode validation")
                response = self.llm_client.generate_plan(
                    system_context=system_prompt,
                    user_goal=user_prompt,
                    complexity="mini"
                )

            # Extract validation results
            validation_result = {
                "is_valid": response.get("is_valid", False),
                "confidence": float(response.get("confidence", 0.0)),
                "reason": response.get("reason", "No reason provided"),
                "applied_rules": response.get("applied_rules", []),
                "suggestions": response.get("suggestions", []),
                "source": "consensus_validation"
            }

            logger.debug(
                f"⚖️ Consensus validation completed - Valid: {validation_result['is_valid']}")
            return validation_result, time.time() - start

        except Exception as e:
            logger.error(f"❌ Consensus validation failed: {e}")
            # Fallback to basic validation
            return {
                "is_valid": False,
                "confidence": 0.0,
                "reason": f"Validation error: {str(e)}",
                "source": "validation_error"
            }, time.time() - start

    def _stage5_write_back(self, content: str, embedding: List[float], validation_result: Dict[str, Any]) -> Tuple[bool, float]:
        """Stage 5: Write back valid patterns to both Redis and Pinecone."""
        start = time.time()
        success = True

        # Rate limiting check
        now = time.time()
        self._last_write_back = [
            t for t in self._last_write_back if now - t < 60]  # Keep last minute
        if len(self._last_write_back) >= self.write_back_rate_limit:
            logger.warning(
                f"⚠️ Write-back rate limit exceeded ({self.write_back_rate_limit}/min)")
            return False, time.time() - start

        self._last_write_back.append(now)

        try:
            # Create CanonEntry for storage
            # For non-code content, use a simple valid AST structure
            if self._is_code(content):
                ast_structure = generate_ast_structure(content)
            else:
                # Use a minimal valid AST structure for text content
                ast_structure = {
                    "type": "Module",
                    "body": "text_content",
                    "valid": True
                }

            canon_entry = CanonEntry(
                code_snippet=content,
                ast_structure=ast_structure,
                embedding=embedding,
                metadata=CanonMetadata(
                    success_count=1,
                    failure_count=0,
                    project_context=os.getenv("PROJECT_CONTEXT", "default"),
                    canon_rule_id=f"rule_{uuid4().hex[:8]}"
                )
            )

            # Write to Redis (L1)
            if self.redis_index:
                try:
                    redis_data = canon_entry.to_redis_fields()
                    redis_data.update({
                        "is_valid": str(validation_result["is_valid"]),
                        "confidence": str(validation_result["confidence"]),
                        # Truncate for Redis
                        "reason": validation_result["reason"][:500],
                        "validation_timestamp": str(int(time.time()))
                    })

                    # Store in Redis using the index key
                    key = f"canon:{canon_entry.id}"
                    redis_conn = ConnectionFactory.get_redis_connection()
                    redis_data["ttl"] = str(self.cache_ttl)  # Add TTL
                    redis_conn.hset(key, mapping=redis_data)
                    # Set expiration
                    redis_conn.expire(key, self.cache_ttl)
                    logger.debug("💾 Written to L1 Cache")

                except Exception as e:
                    logger.warning(f"⚠️ L1 write-back failed: {e}")
                    success = False

            # Write to Pinecone (L2)
            if self.pinecone_index:
                try:
                    pinecone_data = canon_entry.to_pinecone_vector()
                    pinecone_data["metadata"].update({
                        "is_valid": validation_result["is_valid"],
                        "confidence": validation_result["confidence"],
                        "validation_reason": validation_result["reason"][:1000]
                    })

                    self.pinecone_index.upsert([pinecone_data])
                    logger.debug("💾 Written to L2 Memory")

                except Exception as e:
                    logger.warning(f"⚠️ L2 write-back failed: {e}")
                    success = False

            logger.info(
                f"✅ Meta-learning complete - pattern stored for future use")

        except Exception as e:
            logger.error(f"❌ Write-back failed: {e}")
            success = False

        return success, time.time() - start

    def _build_validation_system_prompt(self, canon_rules: List[Dict[str, Any]]) -> str:
        """Build system prompt for validation."""
        base_prompt = """
You are the Canon Validator - the gatekeeper of our agentic architecture.

Your role is to evaluate content against established Canon Rules and principles.
Be rigorous but fair. Consider:
1. Alignment with retrieved canon rules
2. Code quality and best practices (if applicable)
3. Clarity and coherence
4. Potential security or safety issues

If no rules are found, evaluate based on general quality principles.
"""

        if canon_rules:
            base_prompt += f"\n\nThere are {len(canon_rules)} relevant canon rules to consider."

        return base_prompt

    def _is_code(self, content: str) -> bool:
        """Simple heuristic to determine if content is code."""
        # Check for common code patterns (more specific to avoid false positives)
        code_indicators = [
            "def ", "class ", "import ", "from import", "function(", "var ", "let ", "const ",
            "=>", "return ", "if __name__", "#!/usr/bin", "async def", "await "
        ]
        # Avoid false positives from common English words
        if "from " in content and " import " not in content:
            return False
        return any(indicator in content for indicator in code_indicators)

    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics."""
        stats = {
            "validator": "CanonValidator",
            "version": "1.0.0",
            "components": {
                "l1_cache": self.redis_index is not None,
                "l2_memory": self.pinecone_index is not None,
                "llm_client": True,
                "embedding_function": True
            },
            "config": {
                "semantic_threshold": self.semantic_threshold,
                "max_retrieval_rules": self.max_retrieval_rules
            }
        }
        return stats


# Convenience function for quick usage
def validate_content(content: str, source: str = "user") -> Dict[str, Any]:
    """
    Quick validation function.

    Args:
        content: Content to validate
        source: Source identifier

    Returns:
        Validation result
    """
    validator = CanonValidator()
    return validator.validate(content, source)


# Main execution for testing
if __name__ == "__main__":
    # Simple test
    validator = CanonValidator()

    test_content = "The cognitive plane must be separate from the data plane."
    result = validator.validate(test_content, "test")

    # print("\n🎯 Validation Result:")  # [Security Fix]
    # print(json.dumps(result, indent=2))  # [Security Fix]