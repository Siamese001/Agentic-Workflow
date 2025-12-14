"""Types and models for kx_nodes_outreach."""

from typing import Any, Dict, List, Optional
import logging


class OutreachKNodeType(str, Enum):
    """Outreach K.X node type classification."""

class ReasoningStrategy(str, Enum):
    """Reasoning strategy for K.X node execution."""

@dataclass
class RAGConfig:
    """RAG configuration for K.X node."""
    enabled: bool = True
    min_retrievers: int = 3
    max_retrievers: int = 6
    hops: int = 2

@dataclass
class DecodingParams:
    """Decoding parameters for LLM generation."""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    min_p: float = 0.04
    repetition_penalty: float = 1.1

@dataclass
class OutreachKNode:
    """Outreach K.X node configuration for DAG execution."""
    node_id: str
    element: str
    node_type: OutreachKNodeType
    reasoning_strategy: ReasoningStrategy = ReasoningStrategy.COT
    rag_config: Optional[RAGConfig] = None
    decoding_params: Optional[DecodingParams] = None
    tot_branches: int = 3
    self_consistency_runs: int = 1
    max_chars: Optional[int] = None
    max_words: Optional[int] = None
    structure_template: Optional[str] = None
    validation_rules: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
