# LIC LLM Adapter for L2 execution
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class LLMRequest:
    """LLM request structure"""
    prompt: str = ""
    context: Dict[str, Any] = None
    temperature: float = 0.7
    max_tokens: int = 1000

    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str = ""
    token_usage: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class LICLLMAdapter:
    """LLM adapter for outreach execution"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.model_name = self.config.get("model", "default-model")

    def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM"""
        return LLMResponse(
            content=f"Generated response for: {request.prompt[:50]}...",
            token_usage=len(request.prompt.split()),
            metadata={"model": self.model_name, "temperature": request.temperature}
        )

    def batch_generate(self, requests: List[LLMRequest]) -> List[LLMResponse]:
        """Generate responses for multiple requests"""
        return [self.generate_response(request) for request in requests]

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        return len(text.split()) * 4  # Rough estimation
