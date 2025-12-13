"""Dataclass models for match_schema_context."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .match_schema_context_enums import *

@dataclass
class SchemaContext:
    """Context information for a schema."""
    schema_id: str
    domain: Optional[str] = None
    purpose: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    usage_patterns: List[str] = field(default_factory=list)
    related_schemas: List[str] = field(default_factory=list)
    business_context: Optional[str] = None
    technical_context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextMatchRequest:
    """Request for context-based schema matching."""
    query_context: SchemaContext
    candidate_schemas: List[Tuple[str, Dict[str, Any], SchemaContext]]
    match_types: List[ContextMatchType] = field(default_factory=lambda: list(ContextMatchType))
    min_score: float = 0.5
    top_k: int = 10
    include_explanations: bool = False

@dataclass
class ContextMatchResult:
    """Result of context matching."""
    schema_id: str
    match_score: float
    match_details: Dict[str, float] = field(default_factory=dict)
    explanation: Optional[str] = None
    compatibility_score: float = 0.0

@dataclass
class SchemaContextMatchResult:
    """Complete context match results."""
    query_context: SchemaContext
    matches: List[ContextMatchResult]
    total_candidates: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaContextConfig:
    """Configuration for schema context matching."""
    domain_weight: float = 0.3
    purpose_weight: float = 0.25
    semantic_weight: float = 0.2
    structural_weight: float = 0.15
    usage_weight: float = 0.1
    similarity_threshold: float = 0.5

