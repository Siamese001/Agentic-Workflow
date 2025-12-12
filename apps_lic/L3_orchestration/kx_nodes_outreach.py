"""Outreach Engine K.X Nodes - Knowledge Extraction for LinkedIn Outreach.

K.X nodes define the DAG structure for LinkedIn message generation workflow.
Each node represents a specific message component with its generation strategy.

Integrated with: apps_lic/L3_orchestration/
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OutreachKNodeType(str, Enum):
    """Outreach K.X node type classification."""
    ROUTING = "routing"
    ANALYSIS = "analysis"
    CONTENT = "content"
    CTA = "cta"
    ASSEMBLY = "assembly"


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


# Outreach Engine K.X Node DAG
OUTREACH_KX_DAG = {
    # Routing Node (K.1) - No dependencies
    "K.1_Message_Type_Routing": OutreachKNode(
        node_id="K.1",
        element="Message Type - channel classification and grounding with enhanced RAG",
        node_type=OutreachKNodeType.ROUTING,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.1, top_p=0.85, top_k=30),
        tot_branches=7,
        self_consistency_runs=8,
        validation_rules=["message_type_confirmation"],
        dependencies=[],
        metadata={
            "message_types": ["C_LEVEL", "EXECUTIVE", "SENIOR_TA", "RECRUITER"],
            "routing_decision": True,
            "priority": 1,
        },
    ),
    
    # Analysis Node (K.2) - Depends on routing
    "K.2_Recipient_Analysis": OutreachKNode(
        node_id="K.2",
        element="Recipient Analysis - persona and context extraction",
        node_type=OutreachKNodeType.ANALYSIS,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.1, top_p=0.85),
        tot_branches=5,
        self_consistency_runs=5,
        validation_rules=["persona_extraction", "context_grounding"],
        dependencies=["K.1_Message_Type_Routing"],
        metadata={"requires_linkedin_input": True, "priority": 2},
    ),
    
    # Content Nodes (K.3-K.4) - Depend on analysis
    "K.3_Message_Body": OutreachKNode(
        node_id="K.3",
        element="Message Body - personalized content generation",
        node_type=OutreachKNodeType.CONTENT,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.15, top_p=0.88, top_k=40),
        tot_branches=6,
        self_consistency_runs=6,
        max_chars=800,
        structure_template="greeting + personalized opener + value proposition + transition",
        validation_rules=["resume_fact_verification", "temporal_accuracy", "synthesis_phase_check"],
        dependencies=["K.2_Recipient_Analysis"],
        metadata={"regeneration_supported": True, "priority": 3},
    ),
    
    "K.4_Value_Proposition": OutreachKNode(
        node_id="K.4",
        element="Value Proposition - compelling offer articulation",
        node_type=OutreachKNodeType.CONTENT,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=5, hops=2),
        decoding_params=DecodingParams(temperature=0.2, top_p=0.9),
        tot_branches=5,
        self_consistency_runs=4,
        max_words=100,
        validation_rules=["value_clarity", "grounding_check"],
        dependencies=["K.2_Recipient_Analysis"],
        metadata={"regeneration_supported": True, "priority": 3},
    ),
    
    # CTA Node (K.5) - Depends on content
    "K.5_CTA_Generation": OutreachKNode(
        node_id="K.5",
        element="CTA Generation - call-to-action with temporal framing",
        node_type=OutreachKNodeType.CTA,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=3, hops=1),
        decoding_params=DecodingParams(temperature=0.25, top_p=0.88, top_k=30),
        self_consistency_runs=3,
        max_words=30,
        validation_rules=["date_specific_cta_rules", "temporal_framing"],
        dependencies=["K.3_Message_Body"],
        metadata={"lexicon_ref": "cta_temporal_lexicon", "priority": 4},
    ),
    
    # Signature Node (K.6) - Can run in parallel with CTA
    "K.6_Salutation_Signature": OutreachKNode(
        node_id="K.6",
        element="Salutation and Signature - professional formatting",
        node_type=OutreachKNodeType.CONTENT,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        decoding_params=DecodingParams(temperature=0.1, top_p=0.8),
        max_chars=100,
        validation_rules=["requires_sender_profile", "salutation_format"],
        dependencies=["K.1_Message_Type_Routing"],
        metadata={"persona_catalog_ref": "professional_signatures", "priority": 4},
    ),
    
    # Assembly Node (K.7) - Depends on all content nodes
    "K.7_Final_Assembly": OutreachKNode(
        node_id="K.7",
        element="Final Assembly - message composition and validation",
        node_type=OutreachKNodeType.ASSEMBLY,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        decoding_params=DecodingParams(temperature=0.05, top_p=0.75),
        validation_rules=["final_checks", "character_limit", "professional_tone", "no_hallucinations"],
        dependencies=["K.3_Message_Body", "K.5_CTA_Generation", "K.6_Salutation_Signature"],
        metadata={"assembly_phase": True, "blocking_validation": True, "priority": 5},
    ),
}


# Connection Request Variants (override K.3 and K.5 for connection requests)
CONNECTION_REQUEST_VARIANTS = {
    "CONNECTION_REQ_K.3_COMPRESSED": OutreachKNode(
        node_id="K.3",
        element="Message Body (CONNECTION_REQ compressed mode)",
        node_type=OutreachKNodeType.CONTENT,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        decoding_params=DecodingParams(temperature=0.25, top_p=0.9, top_k=40, min_p=0.04, repetition_penalty=1.1),
        self_consistency_runs=1,
        max_chars=280,
        structure_template="greeting + 1-2 sentence personalized opener + transition to CTA",
        validation_rules=["character_limit_strict"],
        dependencies=["K.2_Recipient_Analysis"],
        metadata={"mode": "compressed", "anti_pattern": "RAG disabled due to 330 char space constraint", "priority": 3},
    ),
    
    "CONNECTION_REQ_K.5_MICRO": OutreachKNode(
        node_id="K.5",
        element="CTA (CONNECTION_REQ micro mode)",
        node_type=OutreachKNodeType.CTA,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        decoding_params=DecodingParams(temperature=0.2, top_p=0.88, top_k=30, min_p=0.03, repetition_penalty=1.05),
        self_consistency_runs=1,
        max_words=5,
        max_chars=30,
        validation_rules=["micro_cta_format"],
        dependencies=["CONNECTION_REQ_K.3_COMPRESSED"],
        metadata={"mode": "micro", "examples": ["Let's connect", "Connect?", "Happy to chat"], "priority": 4},
    ),
}


def get_outreach_kx_dag(connection_request: bool = False) -> Dict[str, OutreachKNode]:
    """Get the complete outreach K.X node DAG.
    
    Args:
        connection_request: Use connection request variants if True
        
    Returns:
        Dictionary of outreach K.X nodes with dependencies
    """
    dag = OUTREACH_KX_DAG.copy()
    
    if connection_request:
        # Replace K.3 and K.5 with connection request variants
        dag["K.3_Message_Body"] = CONNECTION_REQUEST_VARIANTS["CONNECTION_REQ_K.3_COMPRESSED"]
        dag["K.5_CTA_Generation"] = CONNECTION_REQUEST_VARIANTS["CONNECTION_REQ_K.5_MICRO"]
    
    return dag


def get_outreach_execution_order(connection_request: bool = False) -> List[str]:
    """Get topological execution order for outreach K.X nodes.
    
    Args:
        connection_request: Use connection request variants if True
        
    Returns:
        List of node keys in execution order
    """
    dag = get_outreach_kx_dag(connection_request)
    
    # Build dependency graph
    in_degree = {node_key: 0 for node_key in dag}
    adjacency = {node_key: [] for node_key in dag}
    
    for node_key, node in dag.items():
        for dep in node.dependencies:
            if dep in dag:
                adjacency[dep].append(node_key)
                in_degree[node_key] += 1
    
    # Kahn's algorithm for topological sort
    queue = [node for node, degree in in_degree.items() if degree == 0]
    order = []
    
    while queue:
        # Sort by priority for deterministic execution
        queue.sort(key=lambda k: dag[k].metadata.get("priority", 999))
        node = queue.pop(0)
        order.append(node)
        
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(order) != len(dag):
        raise ValueError("Outreach K.X DAG contains cycles")
    
    return order


def get_outreach_kx_node(node_key: str, connection_request: bool = False) -> Optional[OutreachKNode]:
    """Get outreach K.X node by key.
    
    Args:
        node_key: Node key (e.g., "K.3_Message_Body")
        connection_request: Use connection request variant if True
        
    Returns:
        OutreachKNode or None if not found
    """
    dag = get_outreach_kx_dag(connection_request)
    return dag.get(node_key)
