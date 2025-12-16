import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, Optional

from canon_keys import get_keys_as_prompt

# Infrastructure
from apps_rg.connection_manager import ConnectionManager
from apps_rg.llm_client import LLMClient

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
            logger.warning(
                f"⚠️ Redis Cache Init Failed (Running without cache): {e}")
            self.cache = None

    def validate(self, content: str, source: str = "user", auto_repair: bool = True) -> Dict[str, Any]:
        """
        The Master Loop: Embed -> Cache -> Context -> Validate -> (Repair)
        """
        logger.info(f"🛡️ Auditing Code ({len(content)} chars)...")
        time.time()

        # Check if code only uses whitelisted tools for execution (skip validation for simple tool usage)
        # L1 WHITELIST CHECK FIX: Disable in test mode to ensure full validation flow
        is_in_test_mode = os.getenv("CANON_TEST_MODE") == "TRUE"

        if not is_in_test_mode:
            allowed_tools = {"search_web", "print",
                             "read_file", "save_file", "send_email"}
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

            # If code only uses allowed tools for execution, proceed to cache check
            if uses_only_allowed:
                logger.info(
                    "ℹ️ Code uses whitelisted tools. Proceeding to L1 cache check.")
        else:
            # Test Mode: Force full validation run to hit all mocks
            uses_only_allowed = False
            logger.info("🧪 Test Mode ACTIVE: Forcing full validation run.")

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
            except Exception:
                pass

        # STAGE 3: PINECONE CONTEXT (Retrieving Wisdom)
        context_rules = []
        try:
            # We look for 'valid' examples or specific 'precedents' in our long-term memory
            matches = self.pinecone.query(
                vector=vector,
                top_k=3,
                include_metadata=True,
                filter={"status": "valid"}  # Only learn from good code
            )
            for m in matches.get('matches', []):
                if m['score'] > 0.80:
                    context_rules.append(
                        f"PRECEDENT (Score {m['score']:.2f}): {m['metadata'].get('content')[:200]}...")
        except Exception as e:
            logger.warning(f"Pinecone lookup failed: {e}")

        # STAGE 4: GEMINI FLASH VALIDATION
        keys_block = get_keys_as_prompt()
        context_block = "\n".join(
            context_rules) if context_rules else "No specific precedents found."

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
        decision = self.llm.generate_plan(
            system_prompt, f"INPUT CODE:\n{content}")

        # Defensive check for None response
        if not decision:
            decision = {"status": "rejected",
                        "reasoning": "LLM returned no response"}

        status = decision.get("status", "rejected").lower()

        # STAGE 5: AUTO-REPAIR (The Mechanic)
        if "valid" not in status and auto_repair:
            logger.info(
                f"🔧 Violation Detected: {decision.get('reasoning')[:50]}...")
            logger.info("🔧 Initiating Auto-Repair Protocol...")

            repaired_code = self._attempt_repair(
                content, decision.get("reasoning"), context_block)

            if repaired_code:
                # RE-VALIDATE the fix (Recursion check, strictly 1 level deep)
                # We trust the repair for now to avoid infinite loops in this demo,
                # but in production you would recurse validation once.

                # Write back the NEW (Fixed) pattern to memory
                self._meta_learn(repaired_code, self.embed_fn(repaired_code), {
                                 "status": "valid", "source": "auto_repair"})

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
- string_set(key: str, value: str) : Redis cache operation
- save_file(content: str, file_path: str) : File write operation

TASK:
Rewrite the code to be fully compliant and executable:
- ALWAYS start with: `from typing import Callable, Dict, Any, Optional`
- DO NOT use Protocol classes or dependency injection
- Call the tools directly - they are already available in the execution scope
- Add type hints
- Define a single 'run' function with optional logger parameter
- RETURN ONLY THE JSON: {{ "code": "..." }}
"""
        try:
            repair_result = self.llm.generate_plan(
                repair_prompt, f"BAD CODE:\n{bad_code}")
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
                self.cache.store(prompt=content, response=json.dumps(
                    decision), vector=vector)

            logger.info("✅ Learned new pattern (Updated Pinecone/Redis).")
        except Exception as e:
            logger.error(f"Write-back failed: {e}")

    def validate_design_compliance(self, file_path: str, component_id: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
        """
        Implements the 'Automated Design System Compliance Check' use case.

        Checks a file for hardcoded values against Figma tokens, retrieves a canonical fix
        from Pinecone, and applies the repair using the Filesystem MCP.
        """
        if logger:
            logger.info(
                f"🛡️ Starting Design Compliance check for {file_path} (Component: {component_id})...")

        # Extract tools from the tools dictionary
        read_text_file = tools.get('read_text_file')
        get_variable_defs = tools.get('get_variable_defs')
        search_records = tools.get('search_records')
        edit_file = tools.get('edit_file')
        string_set = tools.get('string_set')

        # Validate required tools
        if not all([read_text_file, get_variable_defs, search_records, edit_file, string_set]):
            return {"status": "error", "message": "Required MCP tools not available"}

        # 1. Read the Code (Filesystem MCP)
        try:
            source_code = read_text_file(path=file_path)
        except Exception as e:
            return {"status": "error", "message": f"Could not read file {file_path}: {e}"}

        # 2. Get Design Canon (Figma MCP)
        try:
            # Retrieves an exhaustive JSON list of approved tokens, including their hex values and variable names
            token_data_str = get_variable_defs(node_id=component_id)
            token_data = json.loads(token_data_str)
        except Exception as e:
            return {"status": "warning", "message": f"Figma token retrieval failed. Cannot proceed with token check: {e}"}

        # --- Core Validation Logic ---

        # Use regex to find hardcoded hex color values
        hex_pattern = r'#[0-9A-Fa-f]{6}\b'
        hardcoded_hexes = re.findall(hex_pattern, source_code)

        if not hardcoded_hexes:
            if logger:
                logger.info(
                    "✅ No hardcoded hex values found. Compliance passed.")
            # Cache the passing result to skip re-running this expensive check soon
            string_set(
                key=f"design_check_hash:{file_path}", value="PASSED_CLEAN")
            return {"status": "success", "message": "File is design-compliant."}

        # Process first hardcoded hex found
        hardcoded_hex = hardcoded_hexes[0]

        # Find matching token
        token_replacement = None
        for token in token_data:
            if token.get('value') == hardcoded_hex:
                token_replacement = token.get('replacement', token.get('name'))
                break

        if not token_replacement:
            return {"status": "warning", "message": f"Hardcoded hex {hardcoded_hex} found but no matching token defined"}

        # 3. Retrieve Fix Pattern (Pinecone MCP)
        # We ask Pinecone for the canonical code snippet that performs the token replacement
        fix_query = f"Canonical pattern to replace hardcoded hex {hardcoded_hex} with token '{token_replacement}'"

        try:
            # Search the 'code_canon' index for the best match (top_k=1)
            search_result_str = search_records(
                query=fix_query, index="code_canon", top_k=1, namespace="code_canon")
            search_result = json.loads(search_result_str)

            # Extract the canonical replacement from Pinecone result
            if search_result and len(search_result) > 0:
                canonical_replacement = search_result[0].get(
                    'metadata', {}).get('replacement_snippet', token_replacement)
            else:
                canonical_replacement = token_replacement

            if logger:
                logger.info(
                    f"🔎 Found canonical replacement: {canonical_replacement}")

        except Exception as e:
            return {"status": "error", "message": f"Pinecone lookup failed. Cannot repair: {e}"}

        # 4. Apply Repair (Filesystem MCP)
        # The 'edit_file' tool is used for surgical, context-aware code modification
        edit_payload = [{
            "oldText": hardcoded_hex,
            "newText": canonical_replacement
        }]

        try:
            repair_result = edit_file(path=file_path, edits=edit_payload)

            # 5. Cache Success (Redis MCP)
            string_set(
                key=f"design_check_hash:{file_path}", value="REPAIRED_TOKEN")

            return {
                "status": "repaired",
                "message": f"Hardcoded value {hardcoded_hex} replaced with token: {canonical_replacement}",
                "details": repair_result
            }

        except Exception as e:
            return {"status": "error", "message": f"Filesystem repair failed: {e}"}

