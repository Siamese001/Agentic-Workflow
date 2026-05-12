"""W3A Schema Definitions for apps_rg Golden State.

This module contains dataclass schemas for section-level resume generation.
These are DESIGN-TIME schemas only - no runtime implementation in W3A.

schemas:
    - SectionSpec: Resume section specification
    - SectionBenchmarkSet: Per-section quality benchmarks
    - SectionSeedSet: Deterministic seed management
    - SectionArtifact: Per-section output container
    - MergedResumeArtifact: Whole-resume output container
    - SectionWritebackCandidate: Inert cache candidate
    - AggregateWritebackCandidate: Full-resume cache candidate
    - SectionCompletedEvalRecord: L6 learning record per section
    - AggregateCompletedEvalRecord: L6 learning record for full resume
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class SectionSpec:
    """Resume section specification for Golden State section-level generation.
    
    W3A: Schema only - no runtime implementation.
    """
    section_id: str  # e.g., "header", "executive_summary", "experience", "competencies"
    section_name: str  # Human-readable name
    priority_tier: str  # "T1_CRITICAL", "T2_HIGH", "T3_STANDARD", "T4_MINIMAL"
    prompt_profile_ref: str  # Reference to prompt profile
    scorer_profile_ref: str  # Reference to scorer profile
    benchmark_set_ref: Optional[str] = None  # Reference to SectionBenchmarkSet
    seed_set_ref: Optional[str] = None  # Reference to SectionSeedSet
    max_tokens: int = 500
    requires_fact_check: bool = True
    g22_factual_grounding_threshold: float = 0.950  # G22 invariant
    
    # Constraints
    min_content_length: int = 50
    max_content_length: int = 2000
    required_elements: List[str] = field(default_factory=list)
    forbidden_patterns: List[str] = field(default_factory=list)


@dataclass
class SectionBenchmarkSet:
    """Per-section positive/negative examples and quality thresholds.
    
    W3A: Schema only - no runtime implementation.
    """
    benchmark_id: str
    section_id: str  # Links to SectionSpec.section_id
    
    # Positive examples (what good looks like)
    positive_examples: List[Dict[str, Any]] = field(default_factory=list)
    
    # Negative examples (what to avoid)
    negative_examples: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality thresholds
    min_quality_score: float = 0.75
    target_quality_score: float = 0.90
    
    # G22 factual grounding requirements per section
    g22_factual_grounding_min: float = 0.950  # G22 invariant


@dataclass 
class SectionSeedSet:
    """Deterministic seed management for generation, retry, replay.
    
    W3A: Schema only - no runtime implementation.
    """
    seed_set_id: str
    section_id: str  # Links to SectionSpec.section_id
    
    # Base seeds for deterministic generation
    base_seeds: List[int] = field(default_factory=list)
    
    # Retry escalation seeds
    retry_seeds: Dict[int, int] = field(default_factory=dict)  # retry_attempt -> seed
    
    # Replay checkpoint seeds
    checkpoint_seeds: Dict[str, int] = field(default_factory=dict)  # checkpoint_name -> seed


@dataclass
class SectionArtifact:
    """Per-section output with provenance, scores, writeback candidates.
    
    W3A: Schema only - no runtime implementation.
    SectionArtifact is inert until Exit/UWG/L4 per No Direct Writeback Rule.
    """
    artifact_id: str
    section_id: str  # Links to SectionSpec.section_id
    
    # Content
    generated_content: str = ""
    generation_timestamp: Optional[datetime] = None
    
    # Provenance
    generation_seed: Optional[int] = None
    prompt_version: Optional[str] = None
    model_ref: Optional[str] = None
    
    # Scores (X1B/X1D equivalents at section level)
    section_scores: Dict[str, float] = field(default_factory=dict)
    g22_factual_grounding_score: float = 0.0  # G22 invariant tracking
    
    # Quality gates passed
    quality_gates_passed: List[str] = field(default_factory=list)
    quality_gates_failed: List[str] = field(default_factory=list)
    
    # Writeback candidate (inert until Exit/UWG/L4)
    writeback_candidate: Optional['SectionWritebackCandidate'] = None
    
    # Attribution for learning
    source_resume_digest: Optional[str] = None
    prompt_compilation_hash: Optional[str] = None


@dataclass
class MergedResumeArtifact:
    """Whole-resume output after section merge.
    
    W3A: Schema only - no runtime implementation.
    MergedResumeArtifact requires aggregate review after section merge.
    """
    artifact_id: str
    run_id: str
    
    # Merged content
    merged_content: str = ""
    merge_timestamp: Optional[datetime] = None
    
    # Source sections (attribution preserved)
    source_section_artifacts: List[str] = field(default_factory=list)  # artifact_ids
    
    # Aggregate scores (X1B/X1D at whole-resume level)
    aggregate_scores: Dict[str, float] = field(default_factory=dict)
    g22_factual_grounding_score: float = 0.0  # G22 invariant at aggregate level
    
    # Whole-run gates (G24/G28 remain whole-run invariants)
    g24_compliance_passed: bool = False
    g28_safety_passed: bool = False
    
    # Writeback candidate (inert until Exit/UWG/L4)
    writeback_candidate: Optional['AggregateWritebackCandidate'] = None
    
    # Provenance
    merge_binding_version: Optional[str] = None
    disposition_digest: Optional[str] = None


@dataclass
class SectionWritebackCandidate:
    """Inert cache/index candidate until Exit/UWG/L4.
    
    W3A: Schema only - no runtime implementation.
    No Direct Writeback Rule: All writeback candidates inert until proper gating.
    """
    candidate_id: str
    section_artifact_id: str
    
    # Target writeback locations
    cache_namespace: Optional[str] = None
    index_path: Optional[str] = None
    
    # Content to write
    content_hash: Optional[str] = None
    content_summary: Optional[str] = None
    
    # Gating status
    approved_for_writeback: bool = False  # Set by Exit/UWG/L4 only
    approved_by: Optional[str] = None  # e.g., "ExitGate", "UWG", "L4"
    approved_timestamp: Optional[datetime] = None
    
    # TTL and metadata
    ttl_seconds: int = 86400  # 24 hours default
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregateWritebackCandidate:
    """Full-resume cache/index candidate until Exit/UWG/L4.
    
    W3A: Schema only - no runtime implementation.
    No Direct Writeback Rule: All writeback candidates inert until proper gating.
    """
    candidate_id: str
    merged_resume_artifact_id: str
    
    # Target writeback locations
    cache_namespace: Optional[str] = None
    index_path: Optional[str] = None
    run_directory: Optional[str] = None
    
    # Content to write
    content_hash: Optional[str] = None
    content_summary: Optional[str] = None
    
    # Gating status
    approved_for_writeback: bool = False  # Set by Exit/UWG/L4 only
    approved_by: Optional[str] = None  # e.g., "ExitGate", "UWG", "L4"
    approved_timestamp: Optional[datetime] = None
    
    # TTL and metadata
    ttl_seconds: int = 86400  # 24 hours default
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SectionCompletedEvalRecord:
    """L6 shadow learning record per section.
    
    W3A: Schema only - no runtime implementation.
    L6 learning is future-run only - no current-run rescue.
    """
    record_id: str
    section_id: str
    run_id: str
    
    # What happened
    section_artifact_id: Optional[str] = None
    generation_outcome: str = ""  # "success", "retry", "fallback", "failure"
    
    # Scores achieved
    final_scores: Dict[str, float] = field(default_factory=dict)
    g22_factual_grounding_achieved: float = 0.0
    
    # Proposals for future improvement (routed through gauntlet/UWG, not auto-applied)
    improvement_proposals: List[Dict[str, Any]] = field(default_factory=list)
    
    # Attribution for learning
    timestamp: Optional[datetime] = None
    resume_fingerprint: Optional[str] = None
    job_fingerprint: Optional[str] = None
    
    # Future-run only flag
    applicable_to_future_runs: bool = True  # Never applied to current run


@dataclass
class AggregateCompletedEvalRecord:
    """L6 shadow learning record for full resume.
    
    W3A: Schema only - no runtime implementation.
    L6 learning is future-run only - no current-run rescue.
    """
    record_id: str
    run_id: str
    
    # What happened
    merged_resume_artifact_id: Optional[str] = None
    aggregate_outcome: str = ""  # "success", "partial", "failure"
    
    # Aggregate scores
    final_aggregate_scores: Dict[str, float] = field(default_factory=dict)
    g22_factual_grounding_achieved: float = 0.0
    
    # Section-level attribution preserved
    section_records: List[str] = field(default_factory=list)  # SectionCompletedEvalRecord IDs
    
    # Proposals for future improvement (routed through gauntlet/UWG, not auto-applied)
    improvement_proposals: List[Dict[str, Any]] = field(default_factory=list)
    
    # Attribution for learning
    timestamp: Optional[datetime] = None
    resume_fingerprint: Optional[str] = None
    job_fingerprint: Optional[str] = None
    
    # Future-run only flag
    applicable_to_future_runs: bool = True  # Never applied to current run


# Export all schema classes
__all__ = [
    "SectionSpec",
    "SectionBenchmarkSet",
    "SectionSeedSet",
    "SectionArtifact",
    "MergedResumeArtifact",
    "SectionWritebackCandidate",
    "AggregateWritebackCandidate",
    "SectionCompletedEvalRecord",
    "AggregateCompletedEvalRecord",
]
