"""Types and models for kx_nodes_resume."""

import logging

_logger = logging.getLogger(__name__)


# NAMING FIXED: ResumeKNodeType → ResumeKNodeType
class ResumeKNodeType(str, Enum):
    """Resume K.X node type classification."""


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
    _source_weighting: dict[str, float] = field(default_factory=dict)


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
# NAMING FIXED: ResumeKNode → ResumeKNode
class ResumeKNode:
    """Resume K.X node configuration for DAG execution."""

    _node_id: str
    _element: str
    _node_type: ResumeKNodeType
    _reasoning_strategy: ReasoningStrategy = ReasoningStrategy.COT
    _rag_config: RAGConfig | None = None
    _decoding_params: DecodingParams | None = None
    _tot_branches: int = 3
    _tot_depth: int = 2
    _self_consistency_runs: int = 1
    _max_chars: int | None = None
    _max_words: int | None = None
    _structure_template: str | None = None
    _validation_rules: list[str] = field(default_factory=list)
    _dependencies: list[str] = field(default_factory=list)
    _metadata: dict[str, Any] = field(default_factory=dict)
