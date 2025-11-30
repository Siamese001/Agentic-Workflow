"""
LLM Profile Configuration Module

Minimal LLM profile configuration for compatibility.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class LLMProvider(str, Enum):
    """LLM provider types."""
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

@dataclass
class LLMProfile:
    """LLM configuration profile."""
    name: str
    provider: LLMProvider
    model: str
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout_seconds: int = 30
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def get_config(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            "name": self.name,
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata
        }

__all__ = [
    "LLMProvider",
    "LLMProfile",
]
