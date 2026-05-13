"""Section Planner for apps_rg Golden State.

W3B: Section Planner Runtime — PLANNER ONLY

This module produces deterministic SectionSpec plans for the target resume run.
It does NOT generate resume sections, call PA/L2, or emit artifacts.

Scope:
- Deterministic SectionSpec list production
- P0/P1/P2 section tier assignment (Golden State frozen model)
- P1 promotion logic using target_role_profile keywords
- Profile/ref field assignment (prompt, scorer, benchmark, seed, etc.)

Anti-scope (deferred to later waves):
- NO PA calls (W4)
- NO L2 calls (W4)
- NO section content generation (W4)
- NO SectionArtifact emission (W4)
- NO section scoring (W5)
- NO merge binding (W5B)

Golden State Canonical Sections (Frozen Model):
P0 (Bespoke X1B/X1D - Section-level retry allowed): headline, executive_summary, unify_narrative, competencies_ats, IBM
P1 (Shared experience scoring, promotes to bespoke): InsurTech, EY
P2 (Basic checks - No subjective-quality retry): early_career, education, certifications_low_signal
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import W3A schemas
from apps_rg.runtime.schemas import SectionSpec, SectionBenchmarkSet, SectionSeedSet


# Golden State Canonical Section Definitions (Frozen Model)
# P0 = Bespoke X1B/X1D profiles, section-level retry/regeneration allowed on X1B/X1D failure
# P1 = Shared experience scoring (shared_experience_x1bd), promotes to bespoke when target_role_profile matches
# P2 = Basic compactness/factuality checks, no subjective-quality retry by default

GOLDEN_STATE_SECTION_ORDER: List[str] = [
    # P0 sections (bespoke X1B/X1D, section-level retry allowed)
    "headline",
    "executive_summary",
    "unify_narrative",
    "competencies_ats",
    "IBM",
    # P1 sections (promotable)
    "InsurTech",
    "EY",
    # P2 sections (low-signal, no subjective retry)
    "early_career",
    "education",
    "certifications_low_signal",
]

# Section metadata mapping
GOLDEN_STATE_SECTIONS: Dict[str, Dict[str, Any]] = {
    # P0 Sections - Bespoke X1B/X1D Profiles, Section-Level Retry Allowed
    "headline": {
        "section_name": "Headline / Role Alignment",
        "p_level": "P0",
        "priority_tier": "P0_CRITICAL",
        "description": "Role title and positioning headline",
        "min_length_chars": 20,
        "max_length_chars": 100,
        "target_length_chars": 60,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "headline_verification_scorer",
        "benchmark_set_ref": "headline_benchmarks",
        "seed_set_ref": "headline_seeds",
    },
    "executive_summary": {
        "section_name": "Executive Summary",
        "p_level": "P0",
        "priority_tier": "P0_CRITICAL",
        "description": "Positioning statement and value proposition",
        "min_length_chars": 200,
        "max_length_chars": 800,
        "target_length_chars": 400,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "executive_positioning_scorer",
        "benchmark_set_ref": "executive_summary_benchmarks",
        "seed_set_ref": "executive_summary_seeds",
    },
    "unify_narrative": {
        "section_name": "Unify Narrative",
        "p_level": "P0",
        "priority_tier": "P0_CRITICAL",
        "description": "Cross-section narrative coherence and story unification",
        "min_length_chars": 100,
        "max_length_chars": 500,
        "target_length_chars": 250,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "narrative_coherence_scorer",
        "benchmark_set_ref": "narrative_benchmarks",
        "seed_set_ref": "narrative_seeds",
    },
    "competencies_ats": {
        "section_name": "Competencies ATS-Optimized",
        "p_level": "P0",
        "priority_tier": "P0_CRITICAL",
        "description": "ATS-optimized skills and capabilities",
        "min_length_chars": 100,
        "max_length_chars": 600,
        "target_length_chars": 300,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "competencies_ats_scorer",
        "benchmark_set_ref": "competencies_ats_benchmarks",
        "seed_set_ref": "competencies_ats_seeds",
    },
    "IBM": {
        "section_name": "IBM Experience",
        "p_level": "P0",
        "priority_tier": "P0_CRITICAL",
        "description": "IBM-specific experience and achievements",
        "min_length_chars": 300,
        "max_length_chars": 1500,
        "target_length_chars": 800,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "IBM_experience_scorer",
        "benchmark_set_ref": "IBM_benchmarks",
        "seed_set_ref": "IBM_seeds",
    },
    # P1 Sections - Promotable Based on Target Role
    "InsurTech": {
        "section_name": "InsurTech Experience",
        "p_level": "P1",
        "priority_tier": "P1_PROMOTABLE",
        "description": "Insurance technology domain experience",
        "min_length_chars": 200,
        "max_length_chars": 1000,
        "target_length_chars": 600,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "InsurTech_scorer",
        "benchmark_set_ref": "InsurTech_benchmarks",
        "seed_set_ref": "InsurTech_seeds",
    },
    "EY": {
        "section_name": "EY Experience",
        "p_level": "P1",
        "priority_tier": "P1_PROMOTABLE",
        "description": "Ernst & Young experience and achievements",
        "min_length_chars": 200,
        "max_length_chars": 1000,
        "target_length_chars": 600,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "EY_experience_scorer",
        "benchmark_set_ref": "EY_benchmarks",
        "seed_set_ref": "EY_seeds",
    },
    # P2 Sections - Low Signal, No Subjective Retry
    "early_career": {
        "section_name": "Early Career",
        "p_level": "P2",
        "priority_tier": "P2_LOW_SIGNAL",
        "description": "Pre-IBM early career experience (low signal)",
        "min_length_chars": 100,
        "max_length_chars": 800,
        "target_length_chars": 400,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "early_career_scorer",
        "benchmark_set_ref": None,
        "seed_set_ref": None,
    },
    "education": {
        "section_name": "Education",
        "p_level": "P2",
        "priority_tier": "P2_LOW_SIGNAL",
        "description": "Academic credentials and degrees",
        "min_length_chars": 50,
        "max_length_chars": 400,
        "target_length_chars": 200,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "education_verification_scorer",
        "benchmark_set_ref": None,
        "seed_set_ref": None,
    },
    "certifications_low_signal": {
        "section_name": "Certifications (Low Signal)",
        "p_level": "P2",
        "priority_tier": "P2_LOW_SIGNAL",
        "description": "Professional certifications (low signal background)",
        "min_length_chars": 50,
        "max_length_chars": 300,
        "target_length_chars": 150,
        "g22_factual_grounding_threshold": 0.950,
        "scorer_profile_ref": "certification_validity_scorer",
        "benchmark_set_ref": None,
        "seed_set_ref": None,
    },
}

# Legacy section name aliases (for migration/reference only)
# header -> headline
# competencies -> competencies_ats
# experience -> mapped to IBM/InsurTech/EY/early_career based on content
# achievements -> represented within IBM/InsurTech/EY sections
LEGACY_SECTION_ALIASES: Dict[str, str] = {
    "header": "headline",
    "competencies": "competencies_ats",
}


@dataclass
class TargetRoleProfile:
    """Target role profile for P1 promotion decisions."""
    target_company: str
    target_role: str
    target_level: str
    industry_keywords: List[str] = field(default_factory=list)
    domain_keywords: List[str] = field(default_factory=list)
    competency_requirements: List[str] = field(default_factory=list)


@dataclass
class RetryPolicy:
    """Retry policy for section generation."""
    max_attempts: int = 3
    p0_strategy: str = "fail_closed"  # P0 = no retry
    p1_strategy: str = "promote"      # P1 = promote to standard
    p2_strategy: str = "full_retry"   # P2 = full retry with escalation
    backoff_seconds: float = 1.0


@dataclass
class WritebackPolicy:
    """Writeback policy for section artifacts (inert until Exit/UWG/L4)."""
    cache_enabled: bool = True
    index_enabled: bool = True
    ttl_seconds: int = 86400
    requires_exit_approval: bool = True
    requires_uwg_approval: bool = True


@dataclass
class ShadowLearningProfile:
    """L6 shadow learning profile (future-run only)."""
    record_section_completions: bool = True
    improvement_proposal_threshold: float = 0.75
    applicable_to_future_runs_only: bool = True


@dataclass
class SectionPlan:
    """Complete plan for a single section."""
    # Core section spec reference
    section_id: str
    section_name: str
    
    # Priority tier (P0/P1/P2)
    priority_tier: str  # "T1_CRITICAL", "T2_HIGH", "T3_STANDARD", "T4_MINIMAL"
    p_level: str  # "P0", "P1", "P2"
    
    # Promotion logic (P1 only)
    is_promoted: bool = False
    promotion_reason: Optional[str] = None
    
    # Profile references
    prompt_profile_id: Optional[str] = None
    scorer_profile_id: Optional[str] = None
    benchmark_set_id: Optional[str] = None
    seed_set_id: Optional[str] = None
    section_output_schema_ref: str = "section_artifact_v1"
    
    # Policies
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    writeback_policy: WritebackPolicy = field(default_factory=WritebackPolicy)
    shadow_learning_profile: ShadowLearningProfile = field(default_factory=ShadowLearningProfile)
    
    # Generation constraints (from SectionSpec)
    min_content_length: int = 50
    max_content_length: int = 2000
    target_content_length: int = 400
    g22_factual_grounding_threshold: float = 0.950  # G22 invariant


@dataclass
class ResumeGenerationPlan:
    """Complete resume generation plan."""
    plan_id: str
    run_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Target context
    target_role_profile: Optional[TargetRoleProfile] = None
    
    # Section plans (deterministic ordering)
    section_plans: List[SectionPlan] = field(default_factory=list)
    
    # Plan metadata
    total_sections: int = 0
    p0_count: int = 0
    p1_count: int = 0
    p2_count: int = 0
    p1_promoted_count: int = 0
    
    # Constraints
    g22_global_threshold: float = 0.950  # G22 invariant


class SectionPlanner:
    """Planner for deterministic SectionSpec production.
    
    W3B: Planner only - no generation, no PA/L2 calls, no artifact emission.
    
    Uses Golden State frozen section model:
    - P0: headline, executive_summary, unify_narrative, competencies_ats, IBM
    - P1: InsurTech, EY (promotable)
    - P2: early_career, education, certifications_low_signal (low signal)
    """
    
    def __init__(self):
        self._canonical_sections = GOLDEN_STATE_SECTIONS
        self._assembly_order = GOLDEN_STATE_SECTION_ORDER
    
    def create_plan(
        self,
        run_id: str,
        target_role_profile: Optional[TargetRoleProfile] = None,
    ) -> ResumeGenerationPlan:
        """Create deterministic resume generation plan.
        
        Args:
            run_id: Unique run identifier
            target_role_profile: Target role context for P1 promotion
            
        Returns:
            ResumeGenerationPlan with all SectionPlans configured
        """
        plan = ResumeGenerationPlan(
            plan_id=f"plan_{run_id}",
            run_id=run_id,
            target_role_profile=target_role_profile,
        )
        
        # Build section plans in deterministic order
        for section_id in self._assembly_order:
            if section_id in self._canonical_sections:
                section_plan = self._create_section_plan(
                    section_id=section_id,
                    target_role_profile=target_role_profile,
                )
                plan.section_plans.append(section_plan)
        
        # Update metadata
        plan.total_sections = len(plan.section_plans)
        plan.p0_count = sum(1 for sp in plan.section_plans if sp.p_level == "P0")
        plan.p1_count = sum(1 for sp in plan.section_plans if sp.p_level == "P1")
        plan.p2_count = sum(1 for sp in plan.section_plans if sp.p_level == "P2")
        plan.p1_promoted_count = sum(1 for sp in plan.section_plans if sp.is_promoted)
        
        return plan
    
    def _create_section_plan(
        self,
        section_id: str,
        target_role_profile: Optional[TargetRoleProfile],
    ) -> SectionPlan:
        """Create a single SectionPlan from section definition."""
        
        # Get section definition from Golden State model
        section_def = self._canonical_sections.get(section_id, {})
        
        # Get P-level from Golden State model
        p_level = self._get_p_level(section_id)
        
        # P1 promotion logic (only for InsurTech and EY)
        is_promoted = False
        promotion_reason = None
        if self._is_p1_promotable(section_id) and target_role_profile:
            is_promoted = self._evaluate_p1_promotion(section_def, target_role_profile)
            if is_promoted:
                promotion_reason = "Domain/keyword match for target role - promoted to bespoke scoring"
                # P1 remains P1, but uses bespoke scoring instead of shared_experience_x1bd
        
        # Build retry policy based on P-level
        retry_policy = self._build_retry_policy(p_level, section_id)
        
        return SectionPlan(
            section_id=section_id,
            section_name=section_def.get("section_name", section_id),
            priority_tier=section_def.get("priority_tier", "T3_STANDARD"),
            p_level=p_level,
            is_promoted=is_promoted,
            promotion_reason=promotion_reason,
            prompt_profile_id=self._get_prompt_profile_id(section_id),
            scorer_profile_id=section_def.get("scorer_profile_ref"),
            benchmark_set_id=section_def.get("benchmark_set_ref"),
            seed_set_id=section_def.get("seed_set_ref"),
            section_output_schema_ref="section_artifact_v1",
            retry_policy=retry_policy,
            writeback_policy=WritebackPolicy(),
            shadow_learning_profile=ShadowLearningProfile(),
            min_content_length=section_def.get("min_length_chars", 50),
            max_content_length=section_def.get("max_length_chars", 2000),
            target_content_length=section_def.get("target_length_chars", 400),
            g22_factual_grounding_threshold=section_def.get("g22_factual_grounding_threshold", 0.95),
        )
    
    def _get_p_level(self, section_id: str) -> str:
        """Get P-level for section from Golden State model.
        
        P0 = Bespoke X1B/X1D (headline, executive_summary, unify_narrative, competencies_ats, IBM)
             Section-level retry/regeneration allowed on X1B or X1D failure
        P1 = Shared experience scoring (InsurTech, EY)
             Remains P1, uses shared_experience_x1bd by default
             Promotes to bespoke scoring when target_role_profile conditions match
        P2 = Basic compactness/factuality (early_career, education, certifications_low_signal)
             No subjective-quality retry by default
        """
        section_def = self._canonical_sections.get(section_id, {})
        return section_def.get("p_level", "P2")
    
    def _is_p1_promotable(self, section_id: str) -> bool:
        """Check if section is P1 promotable.
        
        Only InsurTech and EY are P1 promotable per Golden State model.
        """
        return section_id in ("InsurTech", "EY")
    
    def _evaluate_p1_promotion(
        self,
        section_def: Dict[str, Any],
        target_role_profile: TargetRoleProfile,
    ) -> bool:
        """Evaluate if P1 section should be promoted to bespoke scoring.

        Only InsurTech and EY sections are eligible for P1 promotion.

        Promotion criteria:
        - Target role profile indicates domain relevance
        - Domain keywords match (InsurTech specific or consulting/Big4 for EY)
        """
        if not target_role_profile:
            return False
        
        section_name = section_def.get("section_name", "").lower()
        
        # Match against industry keywords
        for keyword in target_role_profile.industry_keywords:
            keyword_lower = keyword.lower()
            # InsurTech promotion triggers
            if "InsurTech" in section_def.get("section_id", ""):
                if any(term in keyword_lower for term in ["insurance", "insurtech", "fintech", "financial"]):
                    return True
            # EY promotion triggers
            if "EY" in section_def.get("section_id", ""):
                if any(term in keyword_lower for term in ["consulting", "advisory", "professional services", "audit"]):
                    return True
        
        # Match against domain keywords
        for keyword in target_role_profile.domain_keywords:
            keyword_lower = keyword.lower()
            if "insurtech" in keyword_lower and "InsurTech" in section_def.get("section_id", ""):
                return True
            if any(term in keyword_lower for term in ["consulting", "big4", "ey", "ernst"]):
                if "EY" in section_def.get("section_id", ""):
                    return True
        
        return False
    
    def _build_retry_policy(self, p_level: str, section_id: str = "") -> RetryPolicy:
        """Build retry policy based on P-level per Golden State model.
        
        P0: Section-level retry allowed on X1B/X1D failure (bespoke profiles)
        P1: Shared experience scoring by default, bespoke on promotion (remains P1 tier)
        P2: No subjective-quality retry by default (basic compactness/factuality only)
        """
        if p_level == "P0":
            # P0 sections: Bespoke X1B/X1D, section-level retry allowed
            return RetryPolicy(
                max_attempts=3,  # Section-level retry allowed on X1B/X1D failure
                p0_strategy="retry_on_x1b_x1d",
                p1_strategy="none",
                p2_strategy="none",
            )
        elif p_level == "P1":
            # P1 sections: Shared experience scoring by default
            # Promotes to bespoke scoring on target_role_profile match (remains P1 tier)
            return RetryPolicy(
                max_attempts=2,
                p0_strategy="none",
                p1_strategy="shared_experience_x1bd",
                p2_strategy="none",
            )
        else:  # P2
            # P2 sections: Basic compactness/factuality, no subjective-quality retry
            return RetryPolicy(
                max_attempts=1,  # No subjective-quality retry
                p0_strategy="none",
                p1_strategy="none",
                p2_strategy="basic_factuality_only",
            )
    
    def _get_prompt_profile_id(self, section_id: str) -> Optional[str]:
        """Get prompt profile ID for Golden State section.
        
        Maps canonical section_id to prompt profile reference.
        """
        prompt_profile_map = {
            # P0 sections
            "headline": "headline_generation_v1",
            "executive_summary": "executive_summary_generation_v1",
            "unify_narrative": "unify_narrative_generation_v1",
            "competencies_ats": "competencies_ats_generation_v1",
            "IBM": "IBM_generation_v1",
            # P1 sections
            "InsurTech": "InsurTech_generation_v1",
            "EY": "EY_generation_v1",
            # P2 sections
            "early_career": "early_career_generation_v1",
            "education": "education_generation_v1",
            "certifications_low_signal": "certifications_low_signal_generation_v1",
        }
        return prompt_profile_map.get(section_id)
    
    def get_canonical_sections(self) -> List[str]:
        """Return list of canonical section IDs in assembly order."""
        return list(self._assembly_order)
    
    def get_section_metadata(self, section_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a Golden State canonical section."""
        if section_id not in self._canonical_sections:
            return None
        
        section_def = self._canonical_sections[section_id]
        return {
            "section_id": section_id,
            "section_name": section_def.get("section_name"),
            "p_level": section_def.get("p_level"),
            "priority_tier": section_def.get("priority_tier"),
            "scorer_profile_ref": section_def.get("scorer_profile_ref"),
            "benchmark_set_ref": section_def.get("benchmark_set_ref"),
            "seed_set_ref": section_def.get("seed_set_ref"),
        }
    
    def resolve_legacy_section_name(self, legacy_name: str) -> Optional[str]:
        """Resolve legacy section name to Golden State canonical ID.
        
        Aliases:
        - header -> headline
        - competencies -> competencies_ats
        
        Non-canonical sections (experience, achievements) must be mapped
        to domain-specific sections by content analysis in W4.
        """
        return LEGACY_SECTION_ALIASES.get(legacy_name)


def create_target_role_profile(
    target_company: str,
    target_role: str,
    target_level: str,
    industry_keywords: Optional[List[str]] = None,
    domain_keywords: Optional[List[str]] = None,
    competency_requirements: Optional[List[str]] = None,
) -> TargetRoleProfile:
    """Factory function to create TargetRoleProfile."""
    return TargetRoleProfile(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        industry_keywords=industry_keywords or [],
        domain_keywords=domain_keywords or [],
        competency_requirements=competency_requirements or [],
    )


# Export
__all__ = [
    "SectionPlanner",
    "SectionPlan",
    "ResumeGenerationPlan",
    "TargetRoleProfile",
    "RetryPolicy",
    "WritebackPolicy",
    "ShadowLearningProfile",
    "create_target_role_profile",
]
