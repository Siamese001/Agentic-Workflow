"""
LLM Client - Thin Wrapper
Delegates to Universal Context Gemini client in agentic_core/infra/context.py

This is a backward compatibility shim. All new code should import directly from:
    from agentic_core.infra.context import context
"""

import logging
from typing import Any, Dict

from agentic_core.infra.context import get_context

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Thin wrapper around Universal Context Gemini client.
    
    Delegates all LLM operations to the singleton Universal Context.
    """
    
    def __init__(self):
        """Initialize wrapper (delegates to singleton)."""
        self._ctx = get_context()
        self.model_id = self._ctx.gemini_config.model
        logger.debug(f"LLMClient wrapper initialized: {self.model_id}")
    
    async def generate_plan(
        self,
        system_context: str,
        user_goal: str,
        complexity: str = "mini"
    ) -> Dict[str, Any]:
        """
        Generate a plan using Gemini.
        
        Args:
            system_context: System context/instruction
            user_goal: User goal/prompt
            complexity: Complexity level (unused, kept for compatibility)
            
        Returns:
            Generated plan as dictionary
        """
        import time
        import json
        
        start_time = time.time()
        
        try:
            prompt = f"{system_context}\n\n{user_goal}"
            
            response_text = await self._ctx.generate_with_thinking(
                prompt=prompt,
                temperature=0.7
            )
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                result = {
                    "status": "success",
                    "reasoning": response_text,
                    "plan": {}
                }
            
            result["metrics"] = {
                "latency": f"{time.time() - start_time:.4f}s",
                "model": self.model_id,
                "cost_tier": "mini"
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            return {
                "status": "error",
                "reasoning": f"API Error: {str(e)}",
                "plan": {}
            }
    
    async def generate_content(
        self,
        prompt: str,
        temperature: float = None
    ) -> str:
        """
        Generate content using Gemini.
        
        Args:
            prompt: Prompt for generation
            temperature: Temperature override
            
        Returns:
            Generated text
        """
        return await self._ctx.generate_with_thinking(
            prompt=prompt,
            temperature=temperature
        )


def create_llm_client() -> LLMClient:
    """
    Factory function for backward compatibility.
    
    Returns:
        LLMClient wrapper
    """
    return LLMClient()
