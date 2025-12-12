"""Resume Engine K.X Nodes - Knowledge Extraction for Resume Generation.

K.X nodes define the DAG structure for resume generation workflow.
Each node represents a specific resume section with its generation strategy.

Integrated with: apps_rg/L3_orchestration/orchestrate_workflow.py
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResumeKNodeType(str, Enum):
    """Resume K.X node type classification."""
    HEADER = "header"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    COMPETENCIES = "competencies"
    SKILLS = "skills"
    COVER_LETTER = "cover_letter"


class ReasoningStrategy(str, Enum):
    """Reasoning strategy for K.X node execution."""
    COT = "chain_of_thought"
    TOT = "tree_of_thought"
    HYBRID_COT_TOT = "hybrid_cot_tot"
    SELF_CONSISTENCY = "self_consistency"


@dataclass
class RAGConfig:
    """RAG configuration for K.X node."""
    enabled: bool = True
    min_retrievers: int = 3
    max_retrievers: int = 6
    hops: int = 2
    source_weighting: Dict[str, float] = field(default_factory=dict)


@dataclass
class DecodingParams:
    """Decoding parameters for LLM generation."""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    min_p: float = 0.04
    repetition_penalty: float = 1.1


@dataclass
class ResumeKNode:
    """Resume K.X node configuration for DAG execution."""
    node_id: str
    element: str
    node_type: ResumeKNodeType
    reasoning_strategy: ReasoningStrategy = ReasoningStrategy.COT
    rag_config: Optional[RAGConfig] = None
    decoding_params: Optional[DecodingParams] = None
    tot_branches: int = 3
    tot_depth: int = 2
    self_consistency_runs: int = 1
    max_chars: Optional[int] = None
    max_words: Optional[int] = None
    structure_template: Optional[str] = None
    validation_rules: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# Resume Engine K.X Node DAG
RESUME_KX_DAG = {
    # Header Nodes (K.0) - No dependencies
    "K.0_Name": ResumeKNode(
        node_id="K.0",
        element="Name",
        node_type=ResumeKNodeType.HEADER,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        max_chars=100,
        validation_rules=["non_empty", "proper_case"],
        dependencies=[],
        metadata={"section": "header", "required": True, "priority": 1},
    ),
    
    "K.0_Headline": ResumeKNode(
        node_id="K.0",
        element="Headline",
        node_type=ResumeKNodeType.HEADER,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        max_chars=120,
        validation_rules=["non_empty", "professional_tone"],
        dependencies=[],
        metadata={"section": "header", "required": True, "priority": 1},
    ),
    
    "K.0_Contact": ResumeKNode(
        node_id="K.0",
        element="Contact",
        node_type=ResumeKNodeType.HEADER,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        validation_rules=["valid_email", "valid_phone"],
        dependencies=[],
        metadata={"section": "header", "required": True, "priority": 1},
    ),
    
    # Summary Node (K.1) - Depends on header
    "K.1_Executive_Summary": ResumeKNode(
        node_id="K.1",
        element="Executive Summary",
        node_type=ResumeKNodeType.SUMMARY,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=4, hops=2),
        decoding_params=DecodingParams(temperature=0.3, top_p=0.85),
        tot_branches=5,
        tot_depth=3,
        self_consistency_runs=3,
        max_words=150,
        structure_template="3-4 sentences highlighting key achievements and value proposition",
        validation_rules=["grounding_check", "hallucination_check", "voice_tense_check"],
        dependencies=["K.0_Name", "K.0_Headline"],
        metadata={"section": "summary", "required": True, "priority": 2},
    ),
    
    # Experience Nodes (K.2-K.6) - Depend on summary
    "K.2_Unify_Overview": ResumeKNode(
        node_id="K.2",
        element="Unify Overview",
        node_type=ResumeKNodeType.EXPERIENCE,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=5, hops=3),
        decoding_params=DecodingParams(temperature=0.25, top_p=0.8),
        tot_branches=4,
        self_consistency_runs=2,
        max_words=100,
        validation_rules=["grounding_check", "factual_accuracy"],
        dependencies=["K.1_Executive_Summary"],
        metadata={"section": "experience", "company": "Unify", "priority": 3},
    ),
    
    "K.2_Unify_Bullets": ResumeKNode(
        node_id="K.2",
        element="Unify Bullets",
        node_type=ResumeKNodeType.EXPERIENCE,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.2, top_p=0.75),
        tot_branches=6,
        self_consistency_runs=4,
        structure_template="3-5 achievement bullets with metrics",
        validation_rules=["bullet_provenance_check", "hallucination_check", "redundancy_check"],
        dependencies=["K.2_Unify_Overview"],
        metadata={"section": "experience", "company": "Unify", "min_bullets": 3, "priority": 3},
    ),
    
    "K.3_IBM_Overview": ResumeKNode(
        node_id="K.3",
        element="IBM Overview",
        node_type=ResumeKNodeType.EXPERIENCE,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=5, hops=3),
        decoding_params=DecodingParams(temperature=0.25, top_p=0.8),
        max_words=100,
        validation_rules=["grounding_check", "factual_accuracy"],
        dependencies=["K.1_Executive_Summary"],
        metadata={"section": "experience", "company": "IBM", "priority": 3},
    ),
    
    "K.3_IBM_Bullets": ResumeKNode(
        node_id="K.3",
        element="IBM Bullets",
        node_type=ResumeKNodeType.EXPERIENCE,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.2, top_p=0.75),
        structure_template="3-5 achievement bullets with metrics",
        validation_rules=["bullet_provenance_check", "hallucination_check"],
        dependencies=["K.3_IBM_Overview"],
        metadata={"section": "experience", "company": "IBM", "min_bullets": 3, "priority": 3},
    ),
    
    "K.4_TraderSense_Narrative": ResumeKNode(
        node_id="K.4",
        element="TraderSense Narrative",
        node_type=ResumeKNodeType.EXPERIENCE,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=4, hops=2),
        max_words=120,
        validation_rules=["grounding_check"],
        dependencies=["K.1_Executive_Summary"],
        metadata={"section": "experience", "company": "TraderSense", "priority": 4},
    ),
    
    "K.5_EY_Narrative": ResumeKNode(
        node_id="K.5",
        element="EY Narrative",
        node_type=ResumeKNodeType.EXPERIENCE,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=4, hops=2),
        max_words=120,
        validation_rules=["grounding_check"],
        dependencies=["K.1_Executive_Summary"],
        metadata={"section": "experience", "company": "EY", "priority": 4},
    ),
    
    "K.6_Early_Career_Narrative": ResumeKNode(
        node_id="K.6",
        element="Early Career Narrative",
        node_type=ResumeKNodeType.EXPERIENCE,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=3, hops=1),
        max_words=100,
        validation_rules=["grounding_check"],
        dependencies=["K.1_Executive_Summary"],
        metadata={"section": "experience", "early_career": True, "priority": 5},
    ),
    
    # Education & Credentials (K.7-K.8) - Can run in parallel with experience
    "K.7_Education": ResumeKNode(
        node_id="K.7",
        element="Education",
        node_type=ResumeKNodeType.EDUCATION,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        validation_rules=["factual_accuracy", "date_format"],
        dependencies=["K.0_Name"],
        metadata={"section": "education", "required": True, "priority": 2},
    ),
    
    "K.8_Certifications": ResumeKNode(
        node_id="K.8",
        element="Certifications",
        node_type=ResumeKNodeType.CERTIFICATIONS,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        validation_rules=["factual_accuracy"],
        dependencies=["K.0_Name"],
        metadata={"section": "certifications", "priority": 2},
    ),
    
    # Skills & Competencies (K.9-K.10) - Depend on all experience sections
    "K.9_Competencies": ResumeKNode(
        node_id="K.9",
        element="Leadership Competencies",
        node_type=ResumeKNodeType.COMPETENCIES,
        reasoning_strategy=ReasoningStrategy.SELF_CONSISTENCY,
        rag_config=RAGConfig(enabled=True, min_retrievers=20, hops=3),
        decoding_params=DecodingParams(temperature=0.6, top_p=0.85),
        self_consistency_runs=2,
        tot_branches=2,
        max_words=30,
        structure_template="6 competency items, each with Title and Description (24-30 words)",
        validation_rules=[
            "competency_word_count_balance",
            "gap_coverage_min_85_percent",
            "dedup_check_vs_k5",
            "dedup_check_vs_k6_k7",
            "plausibility_check_min_2_authentic",
            "keyword_density_check",
            "variance_check_max_3_words",
        ],
        dependencies=["K.2_Unify_Bullets", "K.3_IBM_Bullets", "K.1_Executive_Summary"],
        metadata={
            "section": "competencies",
            "priority": 6,
            "count": 6,
            "gap_target": 0.85,
            "tier_1_enhancement": True,
            "scoring_weight": 0.35,
            "primary_objective": "Achieve ≥85% coverage of JD keywords NOT in K.4/K.5/K.6/K.7",
            "secondary_objective": "Incorporate authentic phrasing patterns from LinkedIn/Industry RAG",
            "execution_mode": "GVD",
            "regeneration_max_attempts": 2,
            "required_inputs": [
                "JD_Keyword_Gap",
                "Authentic_Phrasing",
                "Base_Competency_Pool",
                "K4_Headline",
                "K5_Summary",
                "K6_K7_Bullets",
            ],
        },
    ),
    
    "K.10_Skills": ResumeKNode(
        node_id="K.10",
        element="Skills",
        node_type=ResumeKNodeType.SKILLS,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        validation_rules=["controlled_vocabulary"],
        dependencies=["K.9_Competencies"],
        metadata={"section": "skills", "priority": 7},
    ),
    
    # Cover Letter (K.11) - Depends on everything
    "K.11_Cover_Letter": ResumeKNode(
        node_id="K.11",
        element="Cover Letter",
        node_type=ResumeKNodeType.COVER_LETTER,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=5, hops=3),
        decoding_params=DecodingParams(temperature=0.4, top_p=0.9),
        tot_branches=5,
        self_consistency_runs=2,
        max_words=400,
        validation_rules=["grounding_check", "voice_tense_check"],
        dependencies=["K.1_Executive_Summary", "K.2_Unify_Bullets", "K.7_Education"],
        metadata={"section": "cover_letter", "optional": True, "priority": 8},
    ),
}


def get_resume_kx_dag() -> Dict[str, ResumeKNode]:
    """Get the complete resume K.X node DAG.
    
    Returns:
        Dictionary of resume K.X nodes with dependencies
    """
    return RESUME_KX_DAG.copy()


def get_resume_execution_order() -> List[str]:
    """Get topological execution order for resume K.X nodes.
    
    Returns:
        List of node keys in execution order
    """
    # Build dependency graph
    in_degree = {node_key: 0 for node_key in RESUME_KX_DAG}
    adjacency = {node_key: [] for node_key in RESUME_KX_DAG}
    
    for node_key, node in RESUME_KX_DAG.items():
        for dep in node.dependencies:
            if dep in RESUME_KX_DAG:
                adjacency[dep].append(node_key)
                in_degree[node_key] += 1
    
    # Kahn's algorithm for topological sort
    queue = [node for node, degree in in_degree.items() if degree == 0]
    order = []
    
    while queue:
        # Sort by priority for deterministic execution
        queue.sort(key=lambda k: RESUME_KX_DAG[k].metadata.get("priority", 999))
        node = queue.pop(0)
        order.append(node)
        
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(order) != len(RESUME_KX_DAG):
        raise ValueError("Resume K.X DAG contains cycles")
    
    return order


def get_resume_kx_node(node_key: str) -> Optional[ResumeKNode]:
    """Get resume K.X node by key.
    
    Args:
        node_key: Node key (e.g., "K.1_Executive_Summary")
        
    Returns:
        ResumeKNode or None if not found
    """
    return RESUME_KX_DAG.get(node_key)
