#!/usr/bin/env python3
"""
L5 Safety: SubAtomicEngine
Hardens LLM interaction with token budgets and retry logic.
"""
from typing import Any, Optional, Protocol, Dict, List


import asyncio
import json
import logging
import os
import random
import re
import time
import numpy as np
from typing import Any, Dict, Optional, List

# Gemini SDK
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
    
    async def resilient_mutation(
        self,
        file_path: str,
        code: str,
        task: str,
        round_num: int = 1,
        fission_active: bool = False
    ) -> str:
        """Execute resilient mutation with exponential backoff retry."""
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
        
        # Build prompt
        if fission_active:
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
            if self.pinecone_index:
                vector = await self.get_embedding(task)
                self.pinecone_index.upsert(vectors=[{
                    "id": f"succ:{os.path.basename(file_path)}",
                    "values": vector,
                    "metadata": {"task": task[:200], "round": round_num}
                }])
            
            # Clear failures on success
            if self.redis_client:
                self.redis_client.delete(f"fail_count:{file_path}")
                
            return output
        
        logger.warning("   [!] Malformed response from Gemini")
        return code
