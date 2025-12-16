import json
import logging
import time
from datetime import datetime
from typing import Any, Dict

from canon_keys import get_keys_as_prompt

# Infrastructure
from connection_manager import ConnectionManager
from llm_client_flash import LLMClient

# Try to import redisvl SemanticCache
try:
    from redisvl.extensions.llmcache import SemanticCache
    REDISVL_AVAILABLE = True
except ImportError:
    REDISVL_AVAILABLE = False
    logging.warning("redisvl SemanticCache not available")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CanonValidator")


class CanonValidator:
    def __init__(self):
        self.cm = ConnectionManager()
        self.llm = LLMClient()
        self.pinecone = self.cm.get_pinecone_index()
        self.embed_fn = self.cm.get_embedding

        # 1. L1 SPEED LAYER (Redis)
        if REDISVL_AVAILABLE:
            try:
                self.cache = SemanticCache(
                    name="canon_validator_cache",
                    redis_url="redis://localhost:6379",
                    distance_threshold=0.05,
                    ttl=86400,
                    vector_schema={
                        "content": {"type": "text"},
                        # Match embedding dimensions
                        "vector": {"type": "vector", "dims": 384},
                        "metadata": {"type": "text"}
                    }
                )
                logger.info("✅ L1 Semantic Cache initialized (384 dims)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize SemanticCache: {e}")
                self.cache = None
        else:
            self.cache = None

    def validate(self, content: str, source: str = "user", auto_repair: bool = False, max_repair_attempts: int = 1) -> Dict[str, Any]:
        """
        4-Stage Validation Loop (Powered by Gemini Flash)

        Args:
            content: Code content to validate
            source: Source identifier
            auto_repair: If True, attempts to fix rejected code
            max_repair_attempts: Maximum attempts to repair code
        """
        logger.info(f"🛡️ Validating: '{content[:50]}...'")

        # STAGE 1: EMBEDDING
        try:
            vector = self.embed_fn(content)
        except Exception as e:
            return {"status": "error", "message": f"Embedding failed: {e}"}

        # STAGE 2: L1 CACHE HIT
        if self.cache and self.cache.check(vector=vector):
            logger.info("⚡ L1 Cache Hit! (Redis)")
            return {"status": "valid", "source": "l1_redis_cache"}

        # STAGE 3: L2 CONTEXT RETRIEVAL
        context_rules = []
        try:
            matches = self.pinecone.query(
                vector=vector, top_k=3, include_metadata=True)
            for m in matches.get('matches', []):
                if m['score'] > 0.80:
                    context_rules.append(f"- {m['metadata'].get('content')}")
        except Exception:
            logger.debug("L2 retrieval failed or no matches")

        # STAGE 4: GEMINI FLASH VALIDATION
        keys_block = get_keys_as_prompt()
        context_block = "\n".join(
            context_rules) if context_rules else "No specific precedents."

        system_prompt = f"""
You are the Subatomic Gatekeeper.
STRICTLY ENFORCE THESE 50 KEYS:
{keys_block}

RELEVANT PRECEDENTS:
{context_block}

TASK:
Audit the input below.
If it violates ANY key, return {{ "status": "rejected", "reasoning": "..." }}
If it is valid, return {{ "status": "valid", "reasoning": "..." }}
"""
        # Call Gemini 1.5 Flash
        decision = self.llm.generate_plan(system_prompt, f"INPUT: {content}")

        # WRITE-BACK (Meta-Learning)
        if "valid" in decision.get("status", "").lower():
            self._meta_learn(content, vector, decision)
            return {"status": "valid", "source": "gemini_flash", "metrics": decision.get("metrics")}
        else:
            # REJECTED: Check if auto-repair is requested
            if auto_repair:
                logger.info("🔧 ATTEMPTING REPAIR...")
                repair_result = self._attempt_repair(
                    content, decision.get("reasoning", ""))

                if repair_result.get("success"):
                    logger.info("✅ REPAIR SUCCESSFUL")
                    return {
                        "status": "repaired",
                        "source": "gemini_flash",
                        "original_reasoning": decision.get("reasoning"),
                        "fixed_code": repair_result.get("fixed_code")
                    }
                else:
                    logger.error(
                        f"❌ REPAIR FAILED: {repair_result.get('error')}")
                    return {
                        "status": "repair_failed",
                        "source": "gemini_flash",
                        "original_reasoning": decision.get("reasoning"),
                        "repair_error": repair_result.get("error")
                    }
            else:
                return {"status": "rejected", "source": "gemini_flash", "reasoning": decision.get("reasoning")}

    def _attempt_repair(self, bad_code: str, violation_reason: str) -> Dict[str, Any]:
        """
        Attempts to fix code violations using LLM.

        Args:
            bad_code: The original violating code
            violation_reason: Why the code was rejected

        Returns:
            Dict with 'success' bool and 'fixed_code' or 'error' string
        """
        repair_prompt = f"""You are the Repair Agent. The following code was rejected for these reasons:

VIOLATION REASON:
{violation_reason}

ORIGINAL CODE:

{bad_code}


TASK:
Rewrite the code to be fully compliant with the Subatomic Canon rules.
Follow these guidelines:
1. Fix all violations mentioned in the reason
2. Preserve the original functionality
3. Use dependency injection for global dependencies like logging
4. Add proper error handling
5. Include type hints
6. Make functions pure where possible

Return your response as JSON with this format:
{{"code": "the fixed python code here"}}
"""

        try:
            # Call LLM to repair the code - provide proper system_context and user_goal
            system_context = "You are an expert Python code repair assistant. Always return valid JSON."
            repair_response = self.llm.generate_plan(
                system_context, repair_prompt)

            # Extract the code from the JSON response
            if "code" in repair_response:
                fixed_code = repair_response["code"].strip()
            elif "plan" in repair_response:
                plan = repair_response["plan"]
                # Handle case where plan is a dict (error case)
                if isinstance(plan, dict):
                    logger.error(f"LLM returned error dict: {plan}")
                    return {"success": False, "error": "LLM returned error response"}
                fixed_code = str(plan).strip()
            else:
                # Fallback: try to get any text response
                fixed_code = str(repair_response).strip()

            # Validate the fixed code
            if not fixed_code or fixed_code == bad_code or fixed_code == "{}":
                return {"success": False, "error": "LLM did not provide a valid fix"}

            # Quick validation: ensure it's not obviously broken
            if "def " not in fixed_code and "import " not in fixed_code and "class " not in fixed_code:
                return {"success": False, "error": "Fixed code appears invalid"}

            return {"success": True, "fixed_code": fixed_code}

        except Exception as e:
            logger.error(f"Repair attempt failed: {e}")
            return {"success": False, "error": str(e)}

    def _meta_learn(self, content, vector, decision):
        """Updates Redis and Pinecone."""
        timestamp = datetime.utcnow().isoformat()
        try:
            # Update Pinecone (Permanent)
            self.pinecone.upsert(vectors=[(f"canon_{int(time.time())}", vector, {
                "content": content, "source": "validator", "timestamp": timestamp
            })])
            # Update Redis (Hot)
            if self.cache:
                self.cache.store(prompt=content, response=json.dumps(
                    decision), vector=vector)
            logger.info("✅ Learned new pattern.")
        except Exception as e:
            logger.error(f"Write-back failed: {e}")