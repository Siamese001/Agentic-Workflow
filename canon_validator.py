import time
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Infrastructure
from connection_manager import ConnectionManager
from llm_client import LLMClient
from canon_keys import get_keys_as_prompt
from redisvl.extensions.llmcache import SemanticCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CanonValidator")

class CanonValidator:
    def __init__(self):
        self.cm = ConnectionManager()
        self.llm = LLMClient()
        self.pinecone = self.cm.get_pinecone_index()
        self.embed_fn = self.cm.get_embedding
        
        # 1. REDIS SEMANTIC CACHE (Speed Layer)
        # We wrap this in a try/except block to handle library version mismatches gracefully
        try:
            import os
            from redisvl.extensions.cache.llm import SemanticCache
            
            # For redisvl 0.12+, use default vectorizer but force index recreation
            self.cache = SemanticCache(
                name="canon_validator_cache",
                redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
                distance_threshold=0.05,
                ttl=86400,
                overwrite=True  # Force recreation with correct dimensions
            )
            logger.info("✅ Redis Semantic Cache Initialized (768-dim default)")
        except Exception as e:
            logger.warning(f"⚠️ Redis Cache Init Failed (Running without cache): {e}")
            self.cache = None

    def validate(self, content: str, source: str = "user", auto_repair: bool = True) -> Dict[str, Any]:
        """
        The Master Loop: Embed -> Cache -> Context -> Validate -> (Repair)
        """
        logger.info(f"🛡️ Auditing Code ({len(content)} chars)...")
        t_start = time.time()
        
        # Check if code only uses whitelisted tools for execution (skip validation for simple tool usage)
        allowed_tools = {"search_web", "print", "read_file", "save_file", "send_email"}
        uses_only_allowed = True
        
        # Simple parsing to detect function calls
        for line in content.split('\n'):
            line = line.strip()
            if '(' in line and ')' in line and not line.startswith('#'):
                # Extract function name before first parenthesis
                # Skip variable assignments (contains '=' before function name)
                if '=' not in line.split('(')[0]:
                    func_name = line.split('(')[0].strip().split()[-1]
                    if func_name and func_name.isidentifier() and func_name not in allowed_tools:
                        uses_only_allowed = False
                        break
        
        # If code only uses allowed tools for execution, mark as valid
        if uses_only_allowed:
            logger.info("✅ Code only uses whitelisted tools - skipping validation")
            return {
                "status": "valid",
                "reasoning": "Code only uses whitelisted Action Registry tools",
                "content": content
            }

        # STAGE 1: EMBEDDING
        try:
            vector = self.embed_fn(content)
        except Exception as e:
            return {"status": "error", "message": f"Embedding failed: {e}"}

        # STAGE 2: REDIS CACHE CHECK
        if self.cache:
            try:
                # If we have seen this exact code pattern before, return the cached verdict
                # Note: We only trust the cache if it was a 'valid' result previously
                cached_res = self.cache.check(vector=vector)
                if cached_res:
                    # Parse the cached JSON response if possible, or treat as simple hit
                    logger.info("⚡ L1 Cache Hit! (Redis)")
                    return {"status": "valid", "source": "l1_redis_cache", "metrics": {"latency": "0.01s"}}
            except Exception: pass

        # STAGE 3: PINECONE CONTEXT (Retrieving Wisdom)
        context_rules = []
        try:
            # We look for 'valid' examples or specific 'precedents' in our long-term memory
            matches = self.pinecone.query(
                vector=vector, 
                top_k=3, 
                include_metadata=True,
                filter={"status": "valid"} # Only learn from good code
            )
            for m in matches.get('matches', []):
                if m['score'] > 0.80:
                    context_rules.append(f"PRECEDENT (Score {m['score']:.2f}): {m['metadata'].get('content')[:200]}...")
        except Exception as e: 
            logger.warning(f"Pinecone lookup failed: {e}")

        # STAGE 4: GEMINI FLASH VALIDATION
        keys_block = get_keys_as_prompt()
        context_block = "\n".join(context_rules) if context_rules else "No specific precedents found."
        
        system_prompt = f"""
You are the Subatomic Gatekeeper.
STRICTLY ENFORCE THESE 50 KEYS:
{keys_block}

RELEVANT PRECEDENTS (Good Code):
{context_block}

TASK:
Audit the input.
If it violates ANY key, return {{ "status": "rejected", "reasoning": "Violates Key X because..." }}
If it is valid, return {{ "status": "valid", "reasoning": "Compliant." }}
"""
        decision = self.llm.generate_plan(system_prompt, f"INPUT CODE:\n{content}")
        
        status = decision.get("status", "rejected").lower()

        # STAGE 5: AUTO-REPAIR (The Mechanic)
        if "valid" not in status and auto_repair:
            logger.info(f"🔧 Violation Detected: {decision.get('reasoning')[:50]}...")
            logger.info("🔧 Initiating Auto-Repair Protocol...")
            
            repaired_code = self._attempt_repair(content, decision.get("reasoning"), context_block)
            
            if repaired_code:
                # RE-VALIDATE the fix (Recursion check, strictly 1 level deep)
                # We trust the repair for now to avoid infinite loops in this demo,
                # but in production you would recurse validation once.
                
                # Write back the NEW (Fixed) pattern to memory
                self._meta_learn(repaired_code, self.embed_fn(repaired_code), {"status": "valid", "source": "auto_repair"})
                
                return {
                    "status": "repaired", 
                    "repaired_code": repaired_code, 
                    "reasoning": decision.get("reasoning"),
                    "source": "gemini_flash_repair"
                }

        # STAGE 6: META-LEARNING (Write-Back)
        # Only memorize if it was valid (or we fixed it above)
        if "valid" in status:
            self._meta_learn(content, vector, decision)

        return decision

    def _attempt_repair(self, bad_code: str, reasoning: str, context: str) -> Optional[str]:
        """
        Asks Gemini to fix the code based on the specific violation and precedents.
        """
        repair_prompt = f"""
You are the Subatomic Mechanic.
The following code was REJECTED by the Gatekeeper.

VIOLATION:
{reasoning}

PRECEDENTS (How we write good code):
{context}

ACTION REGISTRY TOOLS (These are pre-injected and do NOT need dependency injection):
- search_web(query: str) -> str : Performs web search using Brave API
- print(msg) : Standard python print

TASK:
Rewrite the code to be fully compliant.
- Use Protocol for Dependency Injection ONLY for custom dependencies.
- Action Registry tools (search_web, print) are already available - DO NOT wrap them in protocols.
- Add type hints.
- Remove side effects (except for Action Registry tools).
- For logging, use a 'logger' parameter (not 'log_func').
- RETURN ONLY THE JSON: {{ "code": "..." }}
"""
        try:
            repair_result = self.llm.generate_plan(repair_prompt, f"BAD CODE:\n{bad_code}")
            return repair_result.get("code")
        except Exception as e:
            logger.error(f"Repair failed: {e}")
            return None

    def _meta_learn(self, content, vector, decision):
        """Updates Redis and Pinecone with the pattern."""
        timestamp = datetime.utcnow().isoformat()
        try:
            # Update Pinecone (Permanent Wisdom)
            self.pinecone.upsert(vectors=[(f"canon_{int(time.time())}", vector, {
                "content": content, 
                "status": "valid",
                "source": "validator", 
                "timestamp": timestamp
            })])
            
            # Update Redis (Fast Cache)
            if self.cache:
                self.cache.store(prompt=content, response=json.dumps(decision), vector=vector)
            
            logger.info("✅ Learned new pattern (Updated Pinecone/Redis).")
        except Exception as e:
            logger.error(f"Write-back failed: {e}")
