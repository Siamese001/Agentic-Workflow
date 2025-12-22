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
from typing import Any, Dict, Optional

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
    
    def __init__(self, gemini_client: Optional[Any] = None):
        """
        Initialize SubAtomicEngine.
        
        Args:
            gemini_client: Optional Gemini client (creates new if None)
        """
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
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Failed to parse fission output: {e}")
        
        return {}
    
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
        
        # Build prompt
        if fission_active:
            prompt = f"ATOMIC FISSION: Split {file_path} into 3 sub-modules. Return ONLY a JSON map.\n\nCODE:\n{code}"
        else:
            prompt = f"HEAL: Fix violations in {file_path}.\n\nTASK: {task}\n\nCODE:\n{code}"
        
        config = self.get_safe_config(is_fission=fission_active)
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
            # Truncation guard
            if not fission_active and "..." in output and len(output) < (len(code) * 0.8):
                logger.warning("   [X] TRUNCATION DETECTED. Rejecting mutation.")
                return code
            return output
        
        logger.warning("   [!] Malformed response from Gemini")
        return code
