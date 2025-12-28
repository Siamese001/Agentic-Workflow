#!/usr/bin/env python3
"""
L5 Safety: SubAtomicEngine
Hardens LLM interaction with token budgets and retry logic.
"""
import asyncio
import json
import logging
import os
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

import numpy as np

try:
    from google import genai
    from google.api_core.exceptions import (
        DeadlineExceeded,
        InternalServerError,
        ResourceExhausted,
    )
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Pinecone for hybrid routing
try:
    from agentic_core.L4_state.validation_context.pinecone_sovereign_agent import (
        PineconeSovereignAgent,
    )
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

logger = logging.getLogger(__name__)


class SubAtomicEngine:
    """Hardens the LLM interaction with the 24,576 token budget."""
    
    def __init__(self, gemini_client: Optional[Any] = None, redis_client: Optional[Any] = None, pinecone_index: Optional[Any] = None):
        """
        Initialize SubAtomicEngine with Meta-Learning storage.
        
        Args:
            gemini_client: Optional Gemini client (creates new if None)
            redis_client: Optional Redis client for L3 Failure Tracking
            pinecone_index: Optional Pinecone index for L2 Long-term Memory
        """
        self.redis_client = redis_client
        self.pinecone_index = pinecone_index
        if not GENAI_AVAILABLE:
            raise RuntimeError("Gemini SDK not available. Install with: pip install google-generativeai")
        
        if gemini_client:
            self._client = gemini_client
        else:
            # L5 SAFETY: Suppress redundant API key warnings
            # Check GOOGLE_API_KEY first (canonical), then GEMINI_API_KEY (legacy)
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    logger.warning("[L5] Using legacy GEMINI_API_KEY. Please migrate to GOOGLE_API_KEY.")
            
            if not api_key:
                raise RuntimeError("No Gemini API key found. Set GOOGLE_API_KEY in your .env file.")
            
            self._client = genai.Client(api_key=api_key)
        
        self.chat_sessions: Dict[str, Any] = {}
        
        # [L6 HARDENING] Defer PineconeSovereignAgent instantiation
        # Rationale: Early instantiation in __init__ triggers circular import:
        #    SubAtomicEngine → PineconeSovereignAgent → SubAtomicEngine
        # This causes PineconeSovereignAgent to receive partially-initialized SubAtomicEngine
        # → hybrid routing always offline → no semantic cache → degraded healing.
        # Fix: Instantiate lazily inside methods that need it (route_mission, resilient_mutation).
        self.pinecone = None
        print("   [OK] SubAtomicEngine: Hybrid routing deferred (lazy init)")
    
    @staticmethod
    def get_safe_config(is_fission: bool = False) -> Any:
        """
        Get safe Gemini configuration with hardened thinking budget.
        
        Args:
            is_fission: Whether this is for fission mode (uses max budget)
            
        Returns:
            GenerateContentConfig with safe thinking budget
        """
        if not GENAI_AVAILABLE:
            raise RuntimeError("Gemini SDK not available")
        
        # 🛑 HARDENED: Fixed at 24,576 to prevent 400 INVALID_ARGUMENT
        safe_budget = 24576 if is_fission else 16000
        return types.GenerateContentConfig(
            temperature=0.1,
            thinking_config=types.ThinkingConfig(thinking_budget=safe_budget)
        )
    
    @staticmethod
    def parse_fission_output(output: str) -> Dict[str, str]:
        """
        Extracts JSON file map from AI response.
        
        Args:
            output: Raw output from Gemini
            
        Returns:
            Dictionary mapping file paths to content
        """
        try:
            if not output or len(output.strip()) < 20:
                return {}
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                # [L5 HARDENING] Ensure dict structure for Fission
                return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.warning(f"Failed to parse fission output: {e}")
        
        return {}
    
    async def get_embedding(self, text: str) -> List[float]:
        """Generates semantic embeddings for code/tasks using Gemini 2025."""
        try:
            # [KEY 49] High-density 768-dim model for structural pattern matching
            result = await asyncio.to_thread(
                self._client.models.embed_content,
                model="text-embedding-004", 
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"   [MEMORY ERROR] Embedding failed: {e}")
            return [0.0] * 768  # Return null vector to prevent mission crash
    
    async def resilient_mutation(self, *args, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Hardened LLM Gateway: Universal signature with legacy system_prompt support.
        Scrubs unknown kwargs to prevent Gemini API errors.
        """
        # Extract prompt from multiple possible legacy signatures
        if len(args) >= 2:  # Handle (code, task)
            code, task = args[0], args[1]
            prompt = f"### TASK\n{task}\n\n### CODE\n{code}"
        elif len(args) == 1: # Handle (prompt)
            prompt = args[0]
        else:
            prompt = kwargs.get("prompt", "")

        # Handle system_prompt shim - prioritize parameter over keyword
        if not system_prompt:
            system_prompt = kwargs.pop("system_prompt", None)
        if system_prompt:
            prompt = f"[SYSTEM_INSTRUCTION]\n{system_prompt}\n\n[USER_INPUT]\n{prompt}"

        # Extract other parameters if provided in new style
        file_path = kwargs.get("file_path", "unknown_file")
        code = kwargs.get("code", "")
        task = kwargs.get("task", prompt)
        round_num = kwargs.get("round_num", 1)
        fission_active = kwargs.get("fission_active", False)
        
        # [HARDENING] Scrub unknown kwargs that cause Gemini API to choke
        # This prevents 'unexpected keyword' errors from third-party callables
        scrubbed_kwargs = {k: v for k, v in kwargs.items() if k not in ['stop_sequences', 'top_p', 'response_format']}
        
        # Call the original implementation with extracted parameters
        return await self._resilient_mutation_impl(
            file_path=file_path,
            code=code or prompt,
            task=task,
            round_num=round_num,
            fission_active=fission_active,
            system_prompt=system_prompt,
            **scrubbed_kwargs
        )

    async def _resilient_mutation_impl(
        self,
        file_path: str,
        code: str,
        task: str,
        round_num: int = 1,
        fission_active: bool = False,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Execute resilient mutation with exponential backoff retry.
        
        Args:
            file_path: Path to the file being mutated
            code: Code content to mutate
            task: Task description
            round_num: Current round number
            fission_active: Whether fission mode is active
            system_prompt: Optional system prompt override
            **kwargs: Additional arguments (ignored for compatibility)
        """
        # [L6 LAZY INIT] Instantiate Pinecone gateway only when needed
        if self.pinecone is None and PINECONE_AVAILABLE:
            try:
                from agentic_core.L4_state.validation_context.pinecone_sovereign_agent import PineconeSovereignAgent
                self.pinecone = PineconeSovereignAgent(Path("."))  # project_root will be resolved inside
                print("   [OK] SubAtomicEngine: Hybrid routing activated (lazy)")
            except Exception as e:
                print(f"   [!] Hybrid routing failed (will use fallback): {e}")
                self.pinecone = None
        if not self._client:
            raise RuntimeError("Gemini client not initialized")
        
        start_time = time.time()
        # [L3 STATE] Redis Adaptive Logic: Check for repeat failure patterns
        temp_override = 0.1
        if self.redis_client:
            fail_key = f"fail_count:{file_path}"
            current_fails = self.redis_client.get(fail_key)
            if current_fails and int(current_fails) >= 2:
                logger.warning(f"   [ADAPTIVE] Repeat failure ({current_fails}) detected for {file_path}. Bumping temperature.")
                temp_override = 0.8  # Increase randomness to break loop
        
        # Build prompt with improved system prompt handling
        if system_prompt:
            # Use cleaner INSTRUCTION/CONTEXT format for better clarity
            prompt = f"[INSTRUCTION]\n{system_prompt}\n\n[CONTEXT]\nFILE: {file_path}\n\nTASK: {task}\n\nCODE:\n{code}"
        elif fission_active:
            prompt = f"ATOMIC FISSION: Split {file_path} into 3 sub-modules. Return ONLY a JSON map.\n\nCODE:\n{code}"
        else:
            prompt = f"HEAL: Fix violations in {file_path}.\n\nTASK: {task}\n\nCODE:\n{code}"
        
        config = self.get_safe_config(is_fission=fission_active)
        config.temperature = temp_override
        chat_key = f"chat_{file_path}"
        
        if chat_key not in self.chat_sessions:
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            self.chat_sessions[chat_key] = self._client.chats.create(model=model_name, config=config)
            logger.info(f"   [NEW] Created chat session for {os.path.basename(file_path)}")
        
        # === RETRY WITH EXPONENTIAL BACKOFF (Max 3 attempts) ===
        max_retries = 3
        response = None
        
        for attempt in range(1, max_retries + 1):
            try:
                response = await asyncio.to_thread(self.chat_sessions[chat_key].send_message, prompt)
                break  # Success
            except (ResourceExhausted, InternalServerError, DeadlineExceeded) as e:
                if attempt == max_retries:
                    logger.error(f"   [X] Gemini Error (Final): {e}")
                    return code
                wait = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"   [!] Gemini Transient Error ({attempt}/{max_retries}): {e}. Retrying in {wait:.1f}s")
                await asyncio.sleep(wait)
            except Exception as e:
                logger.error(f"   [X] Gemini Fatal Error: {e}")
                return code

        # Extract response
        if response and response.candidates and response.candidates[0].content.parts:
            output = response.candidates[0].content.parts[0].text.strip()
            
            # [L5 HARDENING] Zero-Latency Hallucination Guard
            duration = time.time() - start_time
            if duration < 0.1 and (not output or len(output) < 50):
                logger.error(f"   [X] HALLUCINATION REJECTED (Latency: {duration:.3f}s).")
                return code

            # Truncation guard
            if not fission_active and "..." in output and len(output) < (len(code) * 0.8):
                logger.warning("   [X] TRUNCATION DETECTED. Rejecting mutation.")
                # Track safety failure in Redis
                if self.redis_client:
                    self.redis_client.incr(f"fail_count:{file_path}")
                return code
            
            # [L2 MEMORY] Store Successful Pattern in Pinecone
            if self.pinecone and hasattr(self.pinecone, 'index'):
                try:
                    vector = await self.get_embedding(task)
                    self.pinecone.index.upsert(vectors=[{
                        "id": f"succ:{os.path.basename(file_path)}",
                        "values": vector,
                        "metadata": {"task": task[:200], "round": round_num, "type": "healing_pattern"}
                    }])
                    print(f"   [MEMORY] Stored healing pattern for {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"   [!] Failed to store pattern in Pinecone: {e}")
            
            # Clear failures on success
            if self.redis_client:
                self.redis_client.delete(f"fail_count:{file_path}")
                
            return output
        
        logger.warning("   [!] Malformed response from Gemini")
        return code

    def route_mission(self, mission: str) -> Dict:
        """
        Eternal sub-atomic routing: Vector + Keyword precision.
        """
        # [L6 LAZY INIT] Ensure pinecone gateway is ready
        if self.pinecone is None and PINECONE_AVAILABLE:
            try:
                from agentic_core.L4_state.validation_context.pinecone_sovereign_agent import PineconeSovereignAgent
                self.pinecone = PineconeSovereignAgent(Path("."))
            except Exception as e:
                print(f"   [!] Routing failed to initialize Pinecone: {e}")
                self.pinecone = None

        if not self.pinecone:
            return {"route": "fallback", "reason": "Hybrid routing offline", "confidence": 0.0}

        # Extract keywords from canon signals
        from agentic_core.config.blueprint_sovereign.structure_blueprint import CANON_SIGNALS
        keywords = [w for w in CANON_SIGNALS if w.lower() in mission.lower()]

        # [L6 HARDENING] Defensive hybrid search with fallback
        if hasattr(self.pinecone, 'hybrid_search'):
            try:
                results = self.pinecone.hybrid_search(query=mission, top_k=8)
            except Exception as e:
                print(f"   [!] Hybrid search failed: {e}")
                results = None
        else:
            results = None

        if not results or not results.get('matches'):
            return {"route": "unknown", "reason": "No high-confidence matches", "confidence": 0.0}

        # Analyze results to find the sovereign path
        territories = {}
        agents = set()
        
        for match in results.get('matches', []):
            meta = match.get('metadata', {})
            territory = meta.get('territory', 'unknown')
            score = match.get('score', 0)
            path = meta.get('path', '')

            # Weight by score
            territories[territory] = territories.get(territory, 0) + score

            # Extract agent names from path (Naming Law: *_agent.py)
            if 'agent' in path.lower():
                file_stem = Path(path).stem
                if file_stem.endswith("_agent"):
                    agents.add(file_stem.replace("_", " ").title().replace(" ", ""))

        # Determine primary territory and normalize confidence
        if not territories:
            return {"route": "unknown", "reason": "No territory data found", "confidence": 0.0}
            
        best_territory = max(territories, key=territories.get)
        confidence = territories[best_territory] / sum(territories.values())

        routing_plan = {
            "primary_territory": best_territory,
            "confidence": round(confidence, 3),
            "relevant_agents": list(agents)[:3],
            "top_matches": [
                {"path": m['metadata'].get('path'), "score": round(m['score'], 3)} 
                for m in results.get('matches', [])[:3]
            ],
            "recommended_action": f"Deploy {list(agents)[0] if agents else 'Agent'} to {best_territory}"
        }

        print(f"   [ROUTING] Mission routed to '{best_territory}' ({confidence:.1%})")
        return routing_plan
