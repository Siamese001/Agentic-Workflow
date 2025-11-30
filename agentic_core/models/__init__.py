"""Agentic Core Models Module

Minimal models module for compatibility with existing imports.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

class ReasoningMode(str, Enum):
    """Reasoning modes for different processing strategies."""
    BASIC = "basic"
    ADVANCED = "advanced"
    HYBRID = "hybrid"
    COT = "cot"  # Chain of Thought
    REACT = "react"  # ReAct

class ComplexityLevel(str, Enum):
    """Complexity levels for processing tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class RetrievalConfig:
    """Configuration for retrieval operations."""
    strategy: str = "hybrid"
    use_rrf: bool = True
    max_hits: int = 50
    bm25_k1: float = 1.2
    bm25_b: float = 0.75
    bm25_backend: Optional['BM25BackendConfig'] = None
    rrf_weights: Optional[Dict[str, float]] = None
    allow_hyde: bool = False
    qa_council_size: int = 1
    qa_council_mode: str = "simple"
    redis_cache: Optional['RedisCacheConfig'] = None
    chroma: Optional['ChromaVectorConfig'] = None
    google_genai: Optional['GoogleGenAIConfig'] = None
    enable_reranking: bool = True
    max_results: int = 10
    similarity_threshold: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextBudget:
    """Budget configuration for context usage."""
    max_tokens: int = 4000
    total_tokens: int = 2000
    planning_tokens: int = 300
    rag_tokens: int = 1000
    drafting_tokens: int = 600
    qa_tokens: int = 256
    safety_tokens: int = 256
    reserved_tokens: int = 500
    overflow_strategy: str = "truncate"

@dataclass
class RedisCacheConfig:
    """Redis cache configuration."""
    enabled: bool = True
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ttl_seconds: int = 3600

@dataclass
class ChromaVectorConfig:
    """Chroma vector database configuration."""
    enabled: bool = True
    host: str = "localhost"
    port: int = 8000
    collection_name: str = "default"
    embedding_model: str = "default"

@dataclass
class GoogleGenAIConfig:
    """Google GenAI configuration."""
    enabled: bool = True
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
