"""Resume Generation Orchestration Configuration.

Extracted from legacy Job_Workflow v1.9.2, v54.00, and v61.27.9.
Provides quality controls, validation gates, and orchestration patterns
for agentic resume generation workflow.

Integrated with: apps_rg/L3_orchestration/kx_nodes_resume.py
"""

from dataclasses import dataclass, field
from enum import Enum

from runtime.shared.routing import RoutingTier


class RAGType(str, Enum):
    """RAG execution type."""
    INTERNAL = "Internal"  # No external RAG, use only provided context
    HYBRID = "Hybrid"  # Mix of internal context and external retrieval
    AGENTIC = "Agentic"  # Full multi-hop agentic RAG with planning


class ClaimVerificationMode(str, Enum):
    """Claim verification strictness."""
    PERMISSIVE = "permissive"  # Allow unverified claims
    BALANCED = "balanced"  # Verify critical claims only
    STRICT = "strict"  # Verify all factual claims


class ValidationSeverity(str, Enum):
    """Validation gate Severity."""
    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"


@dataclass
class WordCountConstraint:
    """Word count constraint for a section."""
    min: int | None = None
    max: int | None = None
    scope: str = "total"  # "total", "per_bullet", "per_segment", "per_competency", "per_paragraph"
    unit: str = "words"

    def validate(self, count: int) -> bool:
        """Validate word count against constraints."""
        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True


@dataclass
class CharCountConstraint:
    """Character count constraint for a section."""
    min: int | None = None
    max: int | None = None

    def validate(self, count: int) -> bool:
        """Validate character count against constraints."""
        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True


@dataclass
class ReasoningConfig:
    """Reasoning configuration for K-node execution."""
    temperature: float = 0.7
    RagType: RAGType = RAGType.HYBRID
    rag_total_calls: int = 5
    rag_hops: int = 2
    ClaimVerificationMode: ClaimVerificationMode = ClaimVerificationMode.BALANCED
    hybrid_cot_tot: bool = True
    cot_min_paths: int | None = 1
    tot_branches: int | None = 3
    min_tot_depth: int | None = 2
    self_consistency: int = 3
    reflexion: bool = True
    routing_tier: RoutingTier | None = None  # Auto-determined if None


@dataclass
class ProvenanceRule:
    """Provenance rule for bullet generation."""
    verbatim: int  # Number of verbatim bullets from master resume
    transformed: int  # Number of transformed bullets
    synthetic: int  # Number of synthetic bullets

    @property
    def total(self) -> int:
        """Total bullet count."""
        return self.verbatim + self.transformed + self.synthetic

    @property
    def pattern(self) -> str:
        """Provenance pattern string."""
        return f"{self.verbatim}V-{self.transformed}T-{self.synthetic}S"


@dataclass
class ValidationGate:
    """Validation gate configuration."""
    gate_id: str
    execution_point: str
    blocking: bool
    Severity: ValidationSeverity
    checks: list[str] = field(default_factory=list)
    on_fail: str = "HALT"
    halt_message: str | None = None


# Global Enforcement Specification (from v1.9.2)
GLOBAL_WORD_COUNTS = {
    "K.1_executive_summary": WordCountConstraint(min=118, max=135, scope="total"),
    "K.4_headline": WordCountConstraint(max=4, scope="per_segment"),
    "K.5A_unify_bullets": WordCountConstraint(min=28, max=33, scope="per_bullet"),
    "K.5B_unify_overview": WordCountConstraint(min=28, max=34, scope="total"),
    "K.6A_ibm_bullets": WordCountConstraint(min=24, max=30, scope="per_bullet"),
    "K.6B_ibm_overview": WordCountConstraint(min=25, max=30, scope="total"),
    "K.8_competencies": WordCountConstraint(min=24, max=30, scope="per_competency"),
    "K.9_cover_letter": WordCountConstraint(min=85, max=100, scope="per_paragraph"),
}

GLOBAL_CHAR_COUNTS = {
    "K.4_headline": CharCountConstraint(min=60, max=90),
}

# Bullet Count Requirements
BULLET_COUNTS = {
    "K.5A": 7,  # Unify bullets
    "K.6A": 6,  # IBM bullets
}

# Provenance Rules (from v1.9.2)
PROVENANCE_RULES = {
    "K.5A": ProvenanceRule(verbatim=3, transformed=3, synthetic=1),
    "K.6A": ProvenanceRule(verbatim=2, transformed=3, synthetic=1),
}

# Competency and Skill Counts
COMPETENCY_COUNT = 6
SKILL_COUNT_RANGE = {"min": 12, "max": 12}

# Authenticity Ratios (from v1.9.2)
AUTHENTICITY_RATIOS = {
    "executive": {"positioning": 0.8, "authenticity": 0.2},
    "bullets": {"positioning": 0.5, "authenticity": 0.5},
    "skills": {"positioning": 0.8, "authenticity": 0.2},
}

# Differentiator Distribution (from v1.9.2)
DIFFERENTIATOR_DISTRIBUTION = {
    "K.1": 2,
    "K.4": 1,
    "K.5A": 5,
    "K.5B": 2,
    "K.6A": 3,
    "K.6B": 1,
    "K.8": 2,
    "K.9": 3,
    "TOTAL": 20,
}

# Similarity Thresholds (from v1.9.2)
SIMILARITY_THRESHOLDS = {
    "overview_to_master_natural": 0.75,
    "overview_to_master_synthetic": 0.65,
    "overview_to_bullet": 0.65,
    "inter_bullet": 0.7,
    "headline_to_summary": 0.6,
    "inter_competency": 0.65,
}

# Reasoning Configurations per K-Node (from v54.00)
K_NODE_REASONING_CONFIGS = {
    "K.1": ReasoningConfig(
        temperature=0.1,
        RagType=RAGType.HYBRID,
        rag_total_calls=3,
        rag_hops=2,
        ClaimVerificationMode=ClaimVerificationMode.STRICT,
        hybrid_cot_tot=True,
        cot_min_paths=1,
        tot_branches=1,
        min_tot_depth=1,
        self_consistency=2,
        reflexion=True,
        routing_tier=RoutingTier.REASONING,
    ),
    "K.2": ReasoningConfig(
        temperature=0.2,
        RagType=RAGType.HYBRID,
        rag_total_calls=2,
        rag_hops=2,
        ClaimVerificationMode=ClaimVerificationMode.BALANCED,
        hybrid_cot_tot=False,
        self_consistency=2,
        reflexion=False,
    ),
    "K.2.5": ReasoningConfig(  # Competitive Positioning
        temperature=0.3,
        RagType=RAGType.AGENTIC,
        rag_total_calls=24,
        rag_hops=3,
        ClaimVerificationMode=ClaimVerificationMode.STRICT,
        hybrid_cot_tot=True,
        cot_min_paths=2,
        tot_branches=5,
        min_tot_depth=4,
        self_consistency=6,
        reflexion=True,
        routing_tier=RoutingTier.REASONING,
    ),
    "K.3": ReasoningConfig(  # Primary Job Role Mapping
        temperature=0.2,
        RagType=RAGType.INTERNAL,
        rag_total_calls=0,
        rag_hops=1,
        ClaimVerificationMode=ClaimVerificationMode.BALANCED,
        hybrid_cot_tot=False,
        self_consistency=2,
        reflexion=False,
    ),
    "K.4": ReasoningConfig(  # Professional Headline
        temperature=0.6,
        RagType=RAGType.HYBRID,
        rag_total_calls=17,
        rag_hops=3,
        ClaimVerificationMode=ClaimVerificationMode.BALANCED,
        hybrid_cot_tot=True,
        cot_min_paths=1,
        tot_branches=3,
        min_tot_depth=2,
        self_consistency=4,
        reflexion=True,
        routing_tier=RoutingTier.BALANCED,
    ),
    "K.5": ReasoningConfig(  # Executive Summary
        temperature=0.7,
        RagType=RAGType.HYBRID,
        rag_total_calls=5,
        rag_hops=2,
        ClaimVerificationMode=ClaimVerificationMode.STRICT,
        hybrid_cot_tot=True,
        cot_min_paths=2,
        tot_branches=2,
        min_tot_depth=2,
        self_consistency=5,
        reflexion=True,
        routing_tier=RoutingTier.REASONING,
    ),
    "K.6": ReasoningConfig(  # Most Recent Experience
        temperature=0.5,
        RagType=RAGType.HYBRID,
        rag_total_calls=21,
        rag_hops=3,
        ClaimVerificationMode=ClaimVerificationMode.BALANCED,
        hybrid_cot_tot=True,
        cot_min_paths=2,
        tot_branches=2,
        min_tot_depth=2,
        self_consistency=3,
        reflexion=True,
    ),
    "K.7": ReasoningConfig(  # Prior Experience
        temperature=0.5,
        RagType=RAGType.HYBRID,
        rag_total_calls=21,
        rag_hops=3,
        ClaimVerificationMode=ClaimVerificationMode.BALANCED,
        hybrid_cot_tot=True,
        cot_min_paths=2,
        tot_branches=2,
        min_tot_depth=2,
        self_consistency=3,
        reflexion=True,
    ),
    "K.8": ReasoningConfig(  # Prior Career Foundation
        temperature=0.7,
        RagType=RAGType.INTERNAL,
        rag_total_calls=0,
        rag_hops=1,
        ClaimVerificationMode=ClaimVerificationMode.PERMISSIVE,
        hybrid_cot_tot=False,
        self_consistency=1,
        reflexion=False,
    ),
    "K.9": ReasoningConfig(  # Leadership Competencies
        temperature=0.6,
        RagType=RAGType.AGENTIC,
        rag_total_calls=20,
        rag_hops=3,
        ClaimVerificationMode=ClaimVerificationMode.STRICT,
        hybrid_cot_tot=True,
        cot_min_paths=2,
        tot_branches=2,
        min_tot_depth=1,
        self_consistency=2,
        reflexion=True,
        routing_tier=RoutingTier.REASONING,
    ),
    "K.10": ReasoningConfig(  # Cover Letter
        temperature=0.4,
        RagType=RAGType.AGENTIC,
        rag_total_calls=25,
        rag_hops=4,
        ClaimVerificationMode=ClaimVerificationMode.STRICT,
        hybrid_cot_tot=True,
        cot_min_paths=2,
        tot_branches=3,
        min_tot_depth=1,
        self_consistency=3,
        reflexion=True,
        routing_tier=RoutingTier.BALANCED,
    ),
    "K.11": ReasoningConfig(  # Optimized Skills
        temperature=0.2,
        RagType=RAGType.INTERNAL,
        rag_total_calls=0,
        rag_hops=1,
        ClaimVerificationMode=ClaimVerificationMode.PERMISSIVE,
        hybrid_cot_tot=True,
        cot_min_paths=2,
        self_consistency=3,
        reflexion=True,
    ),
    "K.12": ReasoningConfig(  # App Tracker Transform
        temperature=0.1,
        RagType=RAGType.INTERNAL,
        rag_total_calls=0,
        rag_hops=1,
        ClaimVerificationMode=ClaimVerificationMode.PERMISSIVE,
        hybrid_cot_tot=False,
        self_consistency=1,
        reflexion=False,
    ),
}

# K.8/K.9 Competencies Specific Constraints
K8_COMPETENCIES_CONFIG = {
    "count": 6,
    "word_count_per_description": {"min": 24, "max": 30},
    "variance_max_std_dev": 3,
    "gap_coverage_minimum": 0.85,
    "gap_coverage_warning": 0.70,
    "plausibility_minimum_authentic": 2,
    "title_keyword_density": {"min": 2, "max": 3},
    "dedup_similarity_thresholds": {
        "vs_k5_summary": 0.50,
        "vs_k6_k7_bullets": 0.60,
    },
    "regeneration_max_attempts": 2,
    "execution_mode": "GVD",
    "tier_1_enhancement": True,
    "scoring_weight": 0.35,
}

# Validation Gates (from v61.27.9)
VALIDATION_GATES = [
    ValidationGate(
        gate_id="VG_CLERK_SCAFFOLD_INTEGRITY",
        execution_point="POST_CLERK_EXTRACTION_PRE_ARTIST_PHASE",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "master_resume_file_present",
            "file_parse_validation",
            "critical_fields_extracted",
            "bullet_pool_adequate",
            "overview_baselines_extracted",
        ],
        on_fail="HALT_AND_GENERATE_SCAFFOLD_FAILURE_REPORT",
    ),
    ValidationGate(
        gate_id="VG_K8_COMPETENCY_WORD_COUNT_COMPLIANCE",
        execution_point="POST_K8_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "all_6_descriptions_24_30_words",
            "variance_max_3_words_std_dev",
        ],
        on_fail="REGENERATE",
        halt_message="K.8 competency word count Violation. All 6 descriptions must be 24-30 words with max 3-word std dev.",
    ),
    ValidationGate(
        gate_id="VG_K8_GAP_COVERAGE_CHECK",
        execution_point="POST_K8_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "gap_coverage_min_85_percent",
        ],
        on_fail="HALT_IF_BELOW_70_WARN_IF_70_TO_84",
        halt_message="K.8 gap coverage <70%. CRITICAL: Cannot proceed. Gap coverage: {coverage}%",
    ),
    ValidationGate(
        gate_id="VG_K8_REDUNDANCY_CHECK",
        execution_point="POST_K8_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "dedup_vs_k5_max_50_percent",
            "dedup_vs_k6_k7_max_60_percent",
        ],
        on_fail="REGENERATE",
        halt_message="K.8 competencies too similar to K.5 (>50%) or K.6/K.7 (>60%). Regenerating entire K.8 output.",
    ),
    ValidationGate(
        gate_id="VG_K8_PLAUSIBILITY_CHECK",
        execution_point="POST_K8_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "min_2_authentic_from_base_pool",
        ],
        on_fail="REGENERATE",
        halt_message="K.8 must have ≥2 competencies verbatim/near-verbatim from Base_Competency_Pool.",
    ),
    ValidationGate(
        gate_id="VG_PRODUCTION_READY_PROOF",
        execution_point="PRE_FILE_WRITE",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "tag_sanitization",
            "overview_customization",
            "round_numbers",
            "synthetic_plausibility",
        ],
        on_fail="HALT",
    ),
    ValidationGate(
        gate_id="VG_SUMMARY_GROUNDING_CHECK",
        execution_point="POST_K1_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "all_claims_grounded_in_source",
            "no_hallucinated_facts",
            "word_count_compliance",
        ],
        on_fail="REGENERATE",
    ),
    ValidationGate(
        gate_id="VG_BULLET_HALLUCINATION_CHECK",
        execution_point="POST_BULLET_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "bullet_provenance_verified",
            "no_synthetic_facts",
            "metrics_grounded",
        ],
        on_fail="REGENERATE",
    ),
    ValidationGate(
        gate_id="VG_HEADLINE_CHARACTER_COMPLIANCE",
        execution_point="POST_K4_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "char_count_60_90",
            "segment_word_count_max_4",
        ],
        on_fail="REGENERATE",
    ),
    ValidationGate(
        gate_id="VG_K2_5_DEEP_RESEARCH_INTEGRITY",
        execution_point="POST_K2_5_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "no_unbound_metrics",
            "no_fluff_language",
            "no_orphaned_claims",
            "minimum_3_citations",
            "depth_score_min_0_7",
        ],
        on_fail="REGENERATE",
        halt_message="K.2.5 deep research failed integrity gate. All metrics must have citations, no fluff language, all claims linked to tech/executives, min 3 citations, depth score ≥0.7.",
    ),
    ValidationGate(
        gate_id="VG_K2_5_FINANCIAL_LAYER_COMPLETENESS",
        execution_point="POST_K2_5_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "min_2_financial_metrics",
            "all_metrics_have_citations",
            "metrics_have_specific_values",
            "yoy_comparisons_present",
        ],
        on_fail="REGENERATE",
        halt_message="K.2.5 financial layer incomplete. Requires ≥2 metrics with citations, specific values, and YoY comparisons.",
    ),
    ValidationGate(
        gate_id="VG_K2_5_TECHNICAL_LAYER_SPECIFICITY",
        execution_point="POST_K2_5_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "min_2_specific_technologies",
            "implementation_details_present",
            "performance_gains_quantified",
            "no_generic_tech_descriptions",
        ],
        on_fail="REGENERATE",
        halt_message="K.2.5 technical layer lacks specificity. Requires ≥2 specific technologies with implementation details and quantified performance gains.",
    ),
    ValidationGate(
        gate_id="VG_K2_5_LEADERSHIP_MAPPING",
        execution_point="POST_K2_5_GENERATION",
        blocking=True,
        Severity=ValidationSeverity.CRITICAL,
        checks=[
            "min_2_executives_identified",
            "executives_have_domain_ownership",
            "initiatives_mapped_to_leaders",
        ],
        on_fail="REGENERATE",
        halt_message="K.2.5 leadership mapping incomplete. Requires ≥2 executives with domain ownership and initiatives mapped to responsible leaders.",
    ),
]

# Feedback Loop Configuration (from v1.9.2 HOP-3)
FEEDBACK_LOOP_CONFIG = {
    "max_attempts": 5,
    "checkpoint_saving": True,
    "reversion_capability": True,
    "reversion_policy": "If attempt N fails worse than attempt N-1, can revert to N-1",
    "exhaustion_policy": "After 5 attempts, HALT_WORKFLOW with detailed failure report",
}

# Industry Adjacency Map (from v1.9.2)
INDUSTRY_ADJACENCY_MAP = {
    "LegalTech": ["FinTech", "RegTech", "Compliance", "Enterprise SaaS", "Financial Services"],
    "FinTech": ["LegalTech", "RegTech", "Banking", "Insurance", "Payments", "Enterprise SaaS"],
    "HealthTech": ["Biotech", "MedTech", "Insurance", "Healthcare", "Wellness"],
    "EdTech": ["Enterprise SaaS", "HR Tech", "Training", "Learning Management"],
    "MarTech": ["AdTech", "SaaS", "Analytics", "CRM", "Sales Tech"],
    "DevOps": ["Cloud", "Infrastructure", "Security", "SaaS", "Enterprise Software"],
}

INDUSTRY_CONFIDENCE_THRESHOLDS = {
    "high": 0.9,
    "moderate": 0.7,
    "low": 0.5,
}

# Executive Summary Structure Rules (from v1.9.2)
EXECUTIVE_SUMMARY_RULES = {
    "sentence_count": 6,
    "style": "narrative_arc",
    "forbidden_content": ["bullet-like", "numbered_list"],
}

# Competency Ranking Rules (from v1.9.2)
COMPETENCY_RANKING_RULES = {
    "pos_1": ["tier_1"],
    "pos_2": ["tier_1", "tier_2"],
    "pos_3": ["tier_1", "tier_2"],
}

# System Parameters (from v1.9.2)
SYSTEM_PARAMETERS = {
    "api_config": {
        "timeout_seconds": 30,
        "retry_attempts": 3,
    },
    "max_regeneration_attempts": 5,
    "hop_execution_timeout_seconds": 60,
    "staging_buffer_immutability": "ENFORCED",
}

# File Complexity Thresholds (from v61.27.9)
FILE_COMPLEXITY_THRESHOLDS = {
    "max_files": 5,
    "max_size_mb": 10,
}

# Round Number Detection (from v61.27.9)
ROUND_NUMBER_CONFIG = {
    "max_total_across_resume": 2,
    "exclusions": ["100%", "24/7", "365"],
    "contextual_exclusions": [
        {
            "pattern": "100%",
            "context": ["uptime", "SLA", "availability", "compliance", "accuracy"],
            "detection_method": "PHRASE_MATCH_WITHIN_10_WORDS",
        },
        {
            "pattern": "50%",
            "context": ["reduction", "improvement", "cost savings", "efficiency"],
            "detection_method": "PHRASE_MATCH_WITHIN_10_WORDS",
        },
    ],
    "variation_range": [-3, 3],
}

# Overview Customization Rules (from v61.27.9)
OVERVIEW_CUSTOMIZATION_RULES = {
    "master_similarity_max": 0.74,
    "similarity_boundary_policy": "STRICT_LESS_THAN",
    "min_edit_distance": 0.25,
    "k0_keywords_min": 2,
    "k2_keywords_min": 1,
    "validation_method": "cosine_similarity + levenshtein_distance + keyword_match",
}


def get_word_count_constraint(k_node: str) -> WordCountConstraint | None:
    """Get word count constraint for a K-node.

    Args:
        k_node: K-node identifier (e.g., "K.1_executive_summary")

    Returns:
        WordCountConstraint or None if not defined
    """
    return GLOBAL_WORD_COUNTS.get(k_node)


def get_char_count_constraint(k_node: str) -> CharCountConstraint | None:
    """Get character count constraint for a K-node.

    Args:
        k_node: K-node identifier (e.g., "K.4_headline")

    Returns:
        CharCountConstraint or None if not defined
    """
    return GLOBAL_CHAR_COUNTS.get(k_node)


def get_reasoning_config(k_node: str) -> ReasoningConfig | None:
    """Get reasoning configuration for a K-node.

    Args:
        k_node: K-node identifier (e.g., "K.1", "K.5")

    Returns:
        ReasoningConfig or None if not defined
    """
    return K_NODE_REASONING_CONFIGS.get(k_node)


def get_validation_gates(execution_point: str) -> list[ValidationGate]:
    """Get validation gates for a specific execution point.

    Args:
        execution_point: Execution point identifier

    Returns:
        List of validation gates
    """
    return [gate for gate in VALIDATION_GATES if gate.execution_point == execution_point]
