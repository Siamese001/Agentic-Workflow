# Outreach LLM caller for L2 execution engines
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class OutreachLLMCaller:
    """LLM caller specialized for outreach operations"""
    provider: str = "anthropic"
    model: str = "claude-haiku-4-5-20251001"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    routing_policy: Optional[Any] = None
    sandbox: Optional[Any] = None
    archetype: Optional[Any] = None
    budget_manager: Optional[Any] = None

    def call(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Make an LLM call with the given prompt"""
        # Stub implementation - simulate LLM response
        return {
            "text": f"Mock response for: {prompt[:50]}...",
            "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": 50},
            "model": self.model,
            "provider": self.provider
    }

    def set_model(self, provider: str, model: str) -> None:
        """Update the provider and model"""
        self.provider = provider
        self.model = model
