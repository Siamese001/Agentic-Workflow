"""Types and models for kx_nodes_resume.

Local Runtime DTOs (Allowed) - App-specific K-node configuration models.
Phase 7: Underscore fields eliminated for SSOT alignment.
"""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
from enum import Enum, auto

import logging
from typing import Any, Dict, List, Optional

Logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


class ResumeKNodeType(str, Enum):
    """Resume K.X node type classification."""


class ReasoningStrategy(str, Enum):
    """Reasoning strategy for K.X node execution."""


@dataclass
class RAGConfig:  # Local Runtime DTO (Allowed)
    """RAG configuration for K.X node."""
    enabled: bool = True
    min_retrievers: int = 3
    max_retrievers: int = 6
    hops: int = 2
    source_weighting: Dict[str, float] = field(default_factory=dict)


@dataclass
class DecodingParams:  # Local Runtime DTO (Allowed)
    """Decoding parameters for LLM generation."""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    min_p: float = 0.04
    repetition_penalty: float = 1.1


@dataclass
class ResumeKNode:  # Local Runtime DTO (Allowed)
    """Resume K.X node configuration for DAG execution."""
    node_id: str
    element: str
    node_type: ResumeKNodeType
    ReasoningStrategy: ReasoningStrategy = ReasoningStrategy.COT
    RagConfig: Optional[RAGConfig] = None
    DecodingParams: Optional[DecodingParams] = None
    tot_branches: int = 3
    tot_depth: int = 2
    self_consistency_runs: int = 1
    max_chars: Optional[int] = None
    max_words: Optional[int] = None
    structure_template: Optional[str] = None
    validation_rules: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

