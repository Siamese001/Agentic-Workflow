from __future__ import annotations
"""Types and models for kx_nodes_outreach."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


# NAMING FIXED: OutreachKNodeType → OutreachKNodeType
class OutreachKNodeType(str, Enum):
    """Outreach K.X node type classification."""


# NAMING FIXED: ReasoningStrategy → ReasoningStrategy
class ReasoningStrategy(str, Enum):
    """Reasoning strategy for K.X node execution."""


@dataclass
# NAMING FIXED: RAGConfig → RagConfig
class RagConfig:
    """RAG configuration for K.X node."""

    _enabled: bool = True
    _min_retrievers: int = 3
    _max_retrievers: int = 6
    _hops: int = 2


@dataclass
# NAMING FIXED: DecodingParams → DecodingParams
class DecodingParams:
    """Decoding parameters for LLM generation."""

    _temperature: float = 0.7
    _top_p: float = 0.9
    _top_k: int = 40
    _min_p: float = 0.04
    _repetition_penalty: float = 1.1


@dataclass
# NAMING FIXED: OutreachKNode → OutreachKNode
class OutreachKNode:
    """Outreach K.X node configuration for DAG execution."""

    _node_id: str
    _element: str
    _node_type: OutreachKNodeType
    _reasoning_strategy: ReasoningStrategy = ReasoningStrategy.COT
    _rag_config: Optional[RAGConfig] = None
    _decoding_params: Optional[DecodingParams] = None
    _tot_branches: int = 3
    _self_consistency_runs: int = 1
    _max_chars: Optional[int] = None
    _max_words: Optional[int] = None
    _structure_template: Optional[str] = None
    _validation_rules: List[str] = field(default_factory=list)
    _dependencies: List[str] = field(default_factory=list)
    _metadata: Dict[str, Any] = field(default_factory=dict)
