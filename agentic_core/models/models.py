"""
Models module shim for backward compatibility.

Re-exports all classes from the main models package.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class RetrievalProfile:
    """Configuration for retrieval operations."""
    name: str
    retrieval_method: str = "vector"
    top_k: int = 10
    similarity_threshold: float = 0.7
    metadata: Optional[Dict[str, Any]] = None

from . import (
    ReasoningMode,
    ComplexityLevel,
    RetrievalConfig,
    ContextBudget,
    RedisCacheConfig,
    ChromaVectorConfig,
    GoogleGenAIConfig,
    BM25BackendConfig,
)

__all__ = [
    "ReasoningMode",
    "ComplexityLevel",
    "RetrievalConfig",
    "ContextBudget",
    "RedisCacheConfig",
    "ChromaVectorConfig",
    "GoogleGenAIConfig",
    "BM25BackendConfig",
    "RetrievalProfile",
]
