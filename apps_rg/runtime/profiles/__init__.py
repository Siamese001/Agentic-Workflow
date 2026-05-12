"""W3A Profile Definitions for apps_rg Golden State.

This module contains profile definitions for section-level and aggregate scoring.
These are DESIGN-TIME profile specs only - no runtime implementation in W3A.

profiles:
    - AggregateResumeScorer: Whole-resume X1B/X1D scoring after section merge
    - AggregateBenchmarkSet: Full-resume coherence benchmarks
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class AggregateResumeScorer:
    """Whole-resume X1B/X1D scoring after section merge.
    
    W3A: Profile spec only - no runtime implementation.
    
    Section-level pass does not imply aggregate pass.
    Aggregate pass does not erase section failures.
    """
    scorer_id: str = "aggregate_resume_scorer_v1"
    
    # Scoring dimensions (X1B/X1D equivalents)
    dimensions: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "overall_quality": {
            "weight": 0.25,
            "threshold": 0.80,
            "target": 0.90,
        },
        "section_coherence": {
            "weight": 0.20,
            "threshold": 0.75,
            "target": 0.85,
        },
        "narrative_consistency": {
            "weight": 0.20,
            "threshold": 0.75,
            "target": 0.85,
        },
        "claims_verifiability": {
            "weight": 0.20,
            "threshold": 0.80,
            "target": 0.90,
        },
        "g22_factual_grounding": {  # G22 invariant at aggregate level
            "weight": 0.15,
            "threshold": 0.950,  # G22 = 0.950 invariant
            "target": 0.980,
        },
    })
    
    # Aggregate score calculation
    min_aggregate_score: float = 0.75
    target_aggregate_score: float = 0.90
    
    # Gate requirements (G24/G28 remain whole-run invariants)
    require_g24_compliance: bool = True
    require_g28_safety: bool = True
    
    # Section attribution preservation
    include_section_breakdown: bool = True
    preserve_section_failures: bool = True  # Aggregate pass does not erase section failures


@dataclass
class AggregateBenchmarkSet:
    """Full-resume coherence benchmarks.
    
    W3A: Profile spec only - no runtime implementation.
    """
    benchmark_id: str = "aggregate_benchmark_set_v1"
    
    # Coherence benchmarks (cross-section validation)
    coherence_checks: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "check_id": "header_summary_alignment",
            "description": "Header role matches executive summary positioning",
            "weight": 0.20,
        },
        {
            "check_id": "summary_experience_consistency",
            "description": "Executive summary claims supported by experience bullets",
            "weight": 0.25,
        },
        {
            "check_id": "experience_competencies_match",
            "description": "Experience demonstrates claimed competencies",
            "weight": 0.25,
        },
        {
            "check_id": "timeline_coherence",
            "description": "No gaps or contradictions in employment timeline",
            "weight": 0.15,
        },
        {
            "check_id": "achievement_claims_verifiable",
            "description": "All major achievements have supporting evidence",
            "weight": 0.15,
        },
    ])
    
    # Quality thresholds
    min_coherence_score: float = 0.70
    target_coherence_score: float = 0.90
    
    # Failure modes to detect
    failure_modes: List[str] = field(default_factory=lambda: [
        "contradiction_between_sections",
        "unsupported_claim_in_summary",
        "timeline_gap",
        "missing_competency_evidence",
        "overstated_achievement",
    ])


@dataclass
class SectionGenerationPolicy:
    """Policy configuration for section-level generation.
    
    W3A: Profile spec only - no runtime implementation.
    
    Tiered section-priority model per plan addendum.
    """
    policy_id: str = "section_generation_policy_v1"
    
    # Section priority tiers (per plan addendum: not all sections receive bespoke rubrics)
    priority_tiers: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "T1_CRITICAL": {
            "sections": ["executive_summary", "experience"],
            "rubric_complexity": "full",
            "retry_attempts": 3,
            "requires_bespoke_benchmarks": True,
        },
        "T2_HIGH": {
            "sections": ["competencies", "achievements"],
            "rubric_complexity": "standard",
            "retry_attempts": 2,
            "requires_bespoke_benchmarks": True,
        },
        "T3_STANDARD": {
            "sections": ["education", "certifications"],
            "rubric_complexity": "basic",
            "retry_attempts": 1,
            "requires_bespoke_benchmarks": False,
        },
        "T4_MINIMAL": {
            "sections": ["header", "contact"],
            "rubric_complexity": "minimal",
            "retry_attempts": 0,
            "requires_bespoke_benchmarks": False,
        },
    })
    
    # No Direct Writeback Rule enforcement
    enforce_no_direct_writeback: bool = True
    writeback_requires_exit_approval: bool = True
    writeback_requires_uwg_approval: bool = True
    
    # L6 learning policy
    l6_future_run_only: bool = True  # L6 learning is future-run only
    l6_proposals_require_gauntlet: bool = True


@dataclass
class NoDirectWritebackRule:
    """Explicit rule specification for No Direct Writeback.
    
    W3A: Profile spec only - no runtime implementation.
    
    All writeback candidates inert until Exit/UWG/L4.
    """
    rule_id: str = "no_direct_writeback_rule_v1"
    rule_description: str = (
        "All writeback candidates (SectionWritebackCandidate, "
        "AggregateWritebackCandidate) remain inert until explicitly "
        "approved by Exit gate, UWG, or L4. No section or aggregate "
        "may write to cache, index, or storage without proper gating."
    )
    
    # Enforcement points
    enforcement_points: List[str] = field(default_factory=lambda: [
        "exit_finalize_apps_rg",  # Exit gate approval
        "uwg_review",              # UWG review approval
        "l4_promote",             # L4 promotion approval
    ])
    
    # Bypass prevention
    allow_section_direct_write: bool = False
    allow_merge_direct_write: bool = False
    allow_unapproved_cache: bool = False
    
    # Audit requirements
    require_approval_audit: bool = True
    require_writeback_receipt: bool = True


@dataclass
class L6FutureRunOnlyPolicy:
    """L6 learning is future-run only - no current-run rescue.
    
    W3A: Profile spec only - no runtime implementation.
    
    Proposals route through gauntlet/UWG; never auto-applied.
    """
    policy_id: str = "l6_future_run_only_policy_v1"
    policy_description: str = (
        "L6 learning proposals (SectionCompletedEvalRecord, "
        "AggregateCompletedEvalRecord) are shadow records only. "
        "They apply to FUTURE runs, never the current run. "
        "All improvement proposals must route through gauntlet/UWG."
    )
    
    # Future-run only enforcement
    applicable_to_current_run: bool = False  # Explicitly never
    applicable_to_future_runs: bool = True
    
    # Proposal routing
    proposals_require_gauntlet_review: bool = True
    proposals_require_uwg_approval: bool = True
    auto_apply_proposals: bool = False  # Never auto-apply
    
    # Learning record retention
    retention_period_days: int = 90
    require_fingerprint_matching: bool = True


# Export all profile classes
__all__ = [
    "AggregateResumeScorer",
    "AggregateBenchmarkSet",
    "SectionGenerationPolicy",
    "NoDirectWritebackRule",
    "L6FutureRunOnlyPolicy",
]
