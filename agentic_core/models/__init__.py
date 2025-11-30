"""Agentic Core Models Module

Minimal models module for compatibility with existing imports.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

class ReasoningMode(str, Enum):
    """Reasoning modes for different processing strategies."""
    BASIC = "basic"
    ADVANCED = "advanced"
    HYBRID = "hybrid"

class ComplexityLevel(str, Enum):
    """Complexity levels for processing tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class RetrievalConfig:
    """Configuration for retrieval operations."""
    max_results: int = 10
    similarity_threshold: float = 0.7
    enable_reranking: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextBudget:
    """Budget configuration for context usage."""
    max_tokens: int = 4000
    reserved_tokens: int = 500
    overflow_strategy: str = "truncate"

@dataclass
class RedisCacheConfig:
    """Redis cache configuration."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ttl_seconds: int = 3600

@dataclass
class ChromaVectorConfig:
    """Chroma vector database configuration."""
    host: str = "localhost"
    port: int = 8000
    collection_name: str = "default"
    embedding_model: str = "default"

@dataclass
class GoogleGenAIConfig:
    """Google GenAI configuration."""
    api_key: str = ""
    model: str = "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 2048

@dataclass
class BM25BackendConfig:
    """BM25 search backend configuration."""
    index_path: str = ""
    k1: float = 1.2
    b: float = 0.75
    epsilon: float = 0.25

__all__ = [
    "ReasoningMode",
    "ComplexityLevel", 
    "RetrievalConfig",
    "ContextBudget",
    "RedisCacheConfig",
    "ChromaVectorConfig",
    "GoogleGenAIConfig",
    "BM25BackendConfig",
]
