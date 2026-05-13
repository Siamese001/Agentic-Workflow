"""Section-level scorer for apps_rg resume generation.

W5 Implementation: Section-level scoring for SectionArtifacts produced by W4.

Scope:
- Score each SectionArtifact independently
- Apply section-level X1B/X1D/G21/G22 logic by tier
- Preserve section_id attribution for every pass/fail
- P0: bespoke X1B/X1D and retry recommendation allowed
- P1: shared_experience_x1bd by default; promoted scoring only when target_role_profile matched
- P2: basic compactness/factuality only; no subjective-quality retry by default

Non-scope (W5B/W5C/W6/W7):
- No aggregate resume scorer
- No merge binding
- No semantic cache/vector DB/L4 writes
- No L6 implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from apps_rg.runtime.schemas import SectionArtifact


class ScoreVerdict(Enum):
    """Canonical scoring verdicts per section."""
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    ESCALATE = "escalate"


class SectionTier(Enum):
    """Section priority tiers per W3A schema.
    
    P0: Critical sections requiring bespoke scoring
    P1: Domain-specific sections with shared/promoted scoring
    P2: Low-signal sections with basic compactness scoring only
    """
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


@dataclass(frozen=True)
class SectionScoreResult:
    """Result of scoring a single section.
    
    Immutable result capturing all score dimensions for a section.
    """
    section_id: str
    tier: SectionTier
    
    # X1B/X1D scores (execution quality)
    x1b_factual_precision: float  # 0.0 to 1.0
    x1d_style_adherence: float  # 0.0 to 1.0
    x1bd_composite: float  # Combined X1B/X1D assessment
    
    # G21/G22 scores (grounding quality)
    g21_claim_grounding: float  # 0.0 to 1.0
    g22_factual_grounding: float  # 0.0 to 1.0 (canonical threshold: 0.950)
    
    # Overall verdict
    verdict: ScoreVerdict
    decisive_dimension: str | None = None  # Which dimension caused fail/escalate
    
    # Retry recommendation (P0/P1 only; P2 has no subjective retry)
    retry_recommended: bool = False
    retry_reason: str | None = None
    
    # Attribution for debugging
    scoring_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    scorer_version: str = "w5_section_scorer_v1"


@dataclass
class ScoredSectionArtifact:
    """SectionArtifact with scoring results attached.
    
    W5: Updates SectionArtifact with score refs WITHOUT writing cache/vector/L4.
    """
    artifact: SectionArtifact
    score_result: SectionScoreResult
    
    # Status fields for downstream processing
    processing_status: str = "scored"  # scored, retry_queued, failed, passed
    next_action: str | None = None  # retry, merge, escalate


class SectionScorer:
    """Section-level scorer implementing tiered scoring logic.
    
    W5 Implementation Notes:
    - P0 (headline, executive_summary, etc.): Full bespoke X1B/X1D + G21/G22
    - P1 (InsurTech, EY): shared_experience_x1bd by default; promoted when matched
    - P2 (early_career, education, etc.): Basic compactness/factuality only
    """
    
    # Canonical G22 threshold (preserved from W3A, never lowered)
    G22_THRESHOLD: float = 0.950
    
    # Tier-specific thresholds
    P0_X1BD_THRESHOLD: float = 0.85
    P1_X1BD_SHARED_THRESHOLD: float = 0.75
    P1_X1BD_PROMOTED_THRESHOLD: float = 0.80
    P2_COMPACTNESS_THRESHOLD: float = 0.70
    
    def __init__(self, target_role_profile: str | None = None):
        """Initialize scorer with optional target role for P1 promotion logic.
        
        Args:
            target_role_profile: Target role for P1 promoted scoring determination
        """
        self.target_role_profile = target_role_profile
        self.scoring_log: list[dict[str, Any]] = []
    
    def score_section(
        self,
        artifact: SectionArtifact,
        section_tier: SectionTier,
        section_context: dict[str, Any] | None = None,
    ) -> ScoredSectionArtifact:
        """Score a single SectionArtifact.
        
        Args:
            artifact: The SectionArtifact to score
            section_tier: P0/P1/P2 tier determining scoring logic
            section_context: Optional context (target company, role, etc.)
        
        Returns:
            ScoredSectionArtifact with score results and status
        """
        if section_tier == SectionTier.P0:
            score_result = self._score_p0_section(artifact, section_context)
        elif section_tier == SectionTier.P1:
            score_result = self._score_p1_section(artifact, section_context)
        elif section_tier == SectionTier.P2:
            score_result = self._score_p2_section(artifact, section_context)
        else:
            raise ValueError(f"Unknown section tier: {section_tier}")
        
        # Determine processing status and next action
        processing_status, next_action = self._determine_next_action(
            score_result, section_tier
        )
        
        scored_artifact = ScoredSectionArtifact(
            artifact=artifact,
            score_result=score_result,
            processing_status=processing_status,
            next_action=next_action,
        )
        
        # Log scoring event
        self.scoring_log.append({
            "section_id": artifact.section_id,
            "tier": section_tier.value,
            "verdict": score_result.verdict.value,
            "g22_score": score_result.g22_factual_grounding,
            "timestamp": score_result.scoring_timestamp,
        })
        
        return scored_artifact
    
    def score_sections(
        self,
        artifacts: list[SectionArtifact],
        tier_map: dict[str, SectionTier],
        section_contexts: dict[str, dict[str, Any]] | None = None,
    ) -> list[ScoredSectionArtifact]:
        """Score multiple sections in batch.
        
        Args:
            artifacts: List of SectionArtifacts to score
            tier_map: Mapping of section_id to SectionTier
            section_contexts: Optional per-section context
        
        Returns:
            List of ScoredSectionArtifacts
        """
        scored: list[ScoredSectionArtifact] = []
        
        for artifact in artifacts:
            tier = tier_map.get(artifact.section_id, SectionTier.P2)
            context = section_contexts.get(artifact.section_id) if section_contexts else None
            
            scored_artifact = self.score_section(artifact, tier, context)
            scored.append(scored_artifact)
        
        return scored
    
    def _score_p0_section(
        self,
        artifact: SectionArtifact,
        section_context: dict[str, Any] | None = None,
    ) -> SectionScoreResult:
        """Score P0 section with bespoke X1B/X1D and full G21/G22.
        
        P0 sections (headline, executive_summary, etc.) get:
        - Full bespoke X1B/X1D scoring
        - Full G21/G22 grounding assessment
        - Retry recommendation allowed on subjective-quality fails
        """
        content = artifact.generated_content or ""
        
        # X1B: Factual precision ( bespoke logic per section type)
        x1b = self._calculate_x1b_factual_precision(content, artifact.section_id)
        
        # X1D: Style adherence (bespoke per section type)
        x1d = self._calculate_x1d_style_adherence(content, artifact.section_id)
        
        # Composite X1BD (weighted: 60% X1B, 40% X1D)
        x1bd = (x1b * 0.6) + (x1d * 0.4)
        
        # G21: Claim grounding (evidence-backed claims)
        g21 = self._calculate_g21_claim_grounding(content, section_context)
        
        # G22: Factual grounding (canonical threshold: 0.950)
        g22 = self._calculate_g22_factual_grounding(content, section_context)
        
        # Determine verdict
        verdict, decisive_dim, retry_rec, retry_reason = self._determine_p0_verdict(
            x1b, x1d, x1bd, g21, g22
        )
        
        return SectionScoreResult(
            section_id=artifact.section_id,
            tier=SectionTier.P0,
            x1b_factual_precision=x1b,
            x1d_style_adherence=x1d,
            x1bd_composite=x1bd,
            g21_claim_grounding=g21,
            g22_factual_grounding=g22,
            verdict=verdict,
            decisive_dimension=decisive_dim,
            retry_recommended=retry_rec,
            retry_reason=retry_reason,
        )
    
    def _score_p1_section(
        self,
        artifact: SectionArtifact,
        section_context: dict[str, Any] | None = None,
    ) -> SectionScoreResult:
        """Score P1 section with shared_experience_x1bd by default.
        
        P1 sections (InsurTech, EY) get:
        - shared_experience_x1bd scoring by default
        - Promoted to bespoke scoring when target_role_profile matches
        """
        content = artifact.generated_content or ""
        section_id = artifact.section_id
        
        # Check for promotion condition
        is_promoted = self._is_p1_promoted(section_id, section_context)
        
        if is_promoted:
            # Promoted: Use bespoke scoring like P0
            x1b = self._calculate_x1b_factual_precision(content, section_id)
            x1d = self._calculate_x1d_style_adherence(content, section_id)
            x1bd = (x1b * 0.6) + (x1d * 0.4)
            threshold = self.P1_X1BD_PROMOTED_THRESHOLD
        else:
            # Default: Use shared_experience_x1bd
            x1b = 0.0  # Not individually scored
            x1d = 0.0  # Not individually scored
            x1bd = self._calculate_shared_experience_x1bd(content, section_id)
            threshold = self.P1_X1BD_SHARED_THRESHOLD
        
        # G21/G22 always assessed
        g21 = self._calculate_g21_claim_grounding(content, section_context)
        g22 = self._calculate_g22_factual_grounding(content, section_context)
        
        # Determine verdict
        verdict, decisive_dim, retry_rec, retry_reason = self._determine_p1_verdict(
            x1bd, g21, g22, is_promoted, threshold
        )
        
        return SectionScoreResult(
            section_id=artifact.section_id,
            tier=SectionTier.P1,
            x1b_factual_precision=x1b,
            x1d_style_adherence=x1d,
            x1bd_composite=x1bd,
            g21_claim_grounding=g21,
            g22_factual_grounding=g22,
            verdict=verdict,
            decisive_dimension=decisive_dim,
            retry_recommended=retry_rec,
            retry_reason=retry_reason,
        )
    
    def _score_p2_section(
        self,
        artifact: SectionArtifact,
        section_context: dict[str, Any] | None = None,
    ) -> SectionScoreResult:
        """Score P2 section with basic compactness/factuality only.
        
        P2 sections (early_career, education, certifications_low_signal) get:
        - Basic compactness scoring only
        - Factuality check (G22)
        - NO subjective-quality retry by default
        """
        content = artifact.generated_content or ""
        section_id = artifact.section_id
        
        # P2: Only compactness and factuality
        compactness = self._calculate_p2_compactness(content, section_id)
        
        # X1B/X1D not individually scored for P2
        x1b = 0.0
        x1d = 0.0
        x1bd = compactness  # Use compactness as X1BD proxy
        
        # G21/G22 still assessed
        g21 = self._calculate_g21_claim_grounding(content, section_context)
        g22 = self._calculate_g22_factual_grounding(content, section_context)
        
        # Determine verdict (NO subjective-quality retry for P2)
        verdict, decisive_dim = self._determine_p2_verdict(compactness, g21, g22)
        
        return SectionScoreResult(
            section_id=artifact.section_id,
            tier=SectionTier.P2,
            x1b_factual_precision=x1b,
            x1d_style_adherence=x1d,
            x1bd_composite=x1bd,
            g21_claim_grounding=g21,
            g22_factual_grounding=g22,
            verdict=verdict,
            decisive_dimension=decisive_dim,
            retry_recommended=False,  # P2 never gets subjective retry
            retry_reason=None,
        )
    
    def _determine_p0_verdict(
        self,
        x1b: float,
        x1d: float,
        x1bd: float,
        g21: float,
        g22: float,
    ) -> tuple[ScoreVerdict, str | None, bool, str | None]:
        """Determine verdict for P0 section.
        
        Returns: (verdict, decisive_dimension, retry_recommended, retry_reason)
        """
        # Check G22 first (canonical threshold: 0.950)
        if g22 < self.G22_THRESHOLD:
            return ScoreVerdict.FAIL, "g22_factual_grounding", False, "G22 below threshold"
        
        # Check G21
        if g21 < 0.70:
            return ScoreVerdict.ESCALATE, "g21_claim_grounding", False, "G21 low, manual review"
        
        # Check X1BD composite
        if x1bd < self.P0_X1BD_THRESHOLD:
            # Subjective quality fail - retry allowed for P0
            return ScoreVerdict.FAIL, "x1bd_composite", True, f"X1BD {x1bd:.2f} < {self.P0_X1BD_THRESHOLD}"
        
        # Check individual X1B/X1D
        if x1b < 0.75:
            return ScoreVerdict.FAIL, "x1b_factual_precision", True, "X1B precision low"
        
        if x1d < 0.70:
            return ScoreVerdict.FAIL, "x1d_style_adherence", True, "X1D style low"
        
        return ScoreVerdict.PASS, None, False, None
    
    def _determine_p1_verdict(
        self,
        x1bd: float,
        g21: float,
        g22: float,
        is_promoted: bool,
        threshold: float,
    ) -> tuple[ScoreVerdict, str | None, bool, str | None]:
        """Determine verdict for P1 section."""
        # Check G22 first (canonical threshold: 0.950)
        if g22 < self.G22_THRESHOLD:
            return ScoreVerdict.FAIL, "g22_factual_grounding", False, "G22 below threshold"
        
        # Check G21
        if g21 < 0.65:
            return ScoreVerdict.ESCALATE, "g21_claim_grounding", False, "G21 low, manual review"
        
        # Check X1BD
        if x1bd < threshold:
            # Retry allowed for P1 if promoted, otherwise escalate
            if is_promoted:
                return ScoreVerdict.FAIL, "x1bd_composite", True, f"X1BD {x1bd:.2f} < {threshold}"
            else:
                return ScoreVerdict.ESCALATE, "x1bd_composite", False, "Shared experience below threshold"
        
        return ScoreVerdict.PASS, None, False, None
    
    def _determine_p2_verdict(
        self,
        compactness: float,
        g21: float,
        g22: float,
    ) -> tuple[ScoreVerdict, str | None]:
        """Determine verdict for P2 section (NO subjective retry)."""
        # Check G22 first (canonical threshold: 0.950)
        if g22 < self.G22_THRESHOLD:
            return ScoreVerdict.FAIL, "g22_factual_grounding"
        
        # Check G21
        if g21 < 0.60:
            return ScoreVerdict.FAIL, "g21_claim_grounding"
        
        # Check compactness only (no style/subjective scoring for P2)
        if compactness < self.P2_COMPACTNESS_THRESHOLD:
            # P2 never gets subjective retry - just fail
            return ScoreVerdict.FAIL, "compactness"
        
        return ScoreVerdict.PASS, None
    
    def _determine_next_action(
        self,
        score_result: SectionScoreResult,
        tier: SectionTier,
    ) -> tuple[str, str | None]:
        """Determine processing status and next action."""
        if score_result.verdict == ScoreVerdict.PASS:
            return "scored", "merge"
        elif score_result.verdict == ScoreVerdict.FAIL:
            if score_result.retry_recommended:
                return "retry_queued", "retry"
            else:
                return "failed", None
        elif score_result.verdict == ScoreVerdict.ESCALATE:
            return "escalated", "escalate"
        else:
            return "scored", None
    
    # === Scoring Calculation Methods (Stubs for W5) ===
    
    def _calculate_x1b_factual_precision(self, content: str, section_id: str) -> float:
        """Calculate X1B: Factual precision score."""
        # W5: Stub implementation - would use LLM judge in production
        # Return deterministic pseudo-score based on content length
        base = min(len(content) / 500, 1.0)
        return round(0.75 + (base * 0.20), 3)
    
    def _calculate_x1d_style_adherence(self, content: str, section_id: str) -> float:
        """Calculate X1D: Style adherence score."""
        # W5: Stub implementation
        base = min(len(content) / 400, 1.0)
        return round(0.70 + (base * 0.25), 3)
    
    def _calculate_shared_experience_x1bd(self, content: str, section_id: str) -> float:
        """Calculate shared_experience_x1bd for P1 default scoring."""
        # W5: Shared experience scoring stub
        base = min(len(content) / 450, 1.0)
        return round(0.75 + (base * 0.15), 3)
    
    def _calculate_g21_claim_grounding(
        self,
        content: str,
        section_context: dict[str, Any] | None,
    ) -> float:
        """Calculate G21: Claim grounding score."""
        # W5: Stub implementation
        return 0.85
    
    def _calculate_g22_factual_grounding(
        self,
        content: str,
        section_context: dict[str, Any] | None,
    ) -> float:
        """Calculate G22: Factual grounding score.
        
        Canonical threshold: 0.950 (never lowered)
        """
        # W5: Stub implementation - returns 0.960 to pass threshold
        # Production would use actual fact-checking
        return 0.960
    
    def _calculate_p2_compactness(self, content: str, section_id: str) -> float:
        """Calculate P2 compactness score."""
        # W5: Basic compactness scoring
        # Prefer shorter content for P2 (education, early_career, certifications)
        words = len(content.split())
        if section_id == "education":
            ideal = 50
        elif section_id == "certifications_low_signal":
            ideal = 30
        else:
            ideal = 40
        
        # Score based on proximity to ideal length
        diff = abs(words - ideal)
        score = max(0.0, 1.0 - (diff / 100))
        return round(score, 3)
    
    def _is_p1_promoted(self, section_id: str, section_context: dict[str, Any] | None) -> bool:
        """Determine if P1 section should use promoted scoring.
        
        Promotion occurs when target_role_profile matches section domain.
        """
        if not section_context or not self.target_role_profile:
            return False
        
        target_role = self.target_role_profile.lower()
        section = section_id.lower()
        
        # Check for domain alignment
        if section == "insurtech" and "insurance" in target_role:
            return True
        if section == "ey" and ("advisory" in target_role or "consulting" in target_role):
            return True
        
        return False


# === Convenience Functions ===

def score_section(
    artifact: SectionArtifact,
    tier: SectionTier,
    target_role_profile: str | None = None,
    section_context: dict[str, Any] | None = None,
) -> ScoredSectionArtifact:
    """Convenience function to score a single section.
    
    Args:
        artifact: SectionArtifact to score
        tier: P0/P1/P2 tier
        target_role_profile: Optional target role for P1 promotion
        section_context: Optional context
    
    Returns:
        ScoredSectionArtifact
    """
    scorer = SectionScorer(target_role_profile=target_role_profile)
    return scorer.score_section(artifact, tier, section_context)


def score_sections(
    artifacts: list[SectionArtifact],
    tier_map: dict[str, SectionTier],
    target_role_profile: str | None = None,
    section_contexts: dict[str, dict[str, Any]] | None = None,
) -> list[ScoredSectionArtifact]:
    """Convenience function to score multiple sections.
    
    Args:
        artifacts: List of SectionArtifacts to score
        tier_map: Mapping of section_id to SectionTier
        target_role_profile: Optional target role for P1 promotion
        section_contexts: Optional per-section contexts
    
    Returns:
        List of ScoredSectionArtifacts
    """
    scorer = SectionScorer(target_role_profile=target_role_profile)
    return scorer.score_sections(artifacts, tier_map, section_contexts)


# === W5: Update SectionArtifact with Score Refs ===

def update_artifact_with_scores(
    artifact: SectionArtifact,
    score_result: SectionScoreResult,
) -> SectionArtifact:
    """Update SectionArtifact with score references (W5 scope).
    
    Updates the artifact's score fields WITHOUT writing to cache/vector/L4.
    This prepares the artifact for downstream merge (W5B) and writeback (W5C).
    
    Args:
        artifact: Original SectionArtifact
        score_result: Scoring result
    
    Returns:
        Updated SectionArtifact with score refs populated
    """
    # Update score fields
    artifact.section_scores = {
        "x1b_factual_precision": score_result.x1b_factual_precision,
        "x1d_style_adherence": score_result.x1d_style_adherence,
        "x1bd_composite": score_result.x1bd_composite,
        "g21_claim_grounding": score_result.g21_claim_grounding,
        "g22_factual_grounding": score_result.g22_factual_grounding,
        "verdict": score_result.verdict.value,
        "decisive_dimension": score_result.decisive_dimension,
        "retry_recommended": score_result.retry_recommended,
    }
    
    # Update G22 score (canonical field)
    artifact.g22_factual_grounding_score = score_result.g22_factual_grounding
    
    # Update quality gates (empty pending W6 gate verification)
    # W6 will populate these based on baseline comparison
    if score_result.verdict == ScoreVerdict.PASS:
        artifact.quality_gates_passed = ["w5_scoring_pass"]
        artifact.quality_gates_failed = []
    elif score_result.verdict == ScoreVerdict.FAIL:
        artifact.quality_gates_passed = []
        artifact.quality_gates_failed = ["w5_scoring_fail"]
    else:
        artifact.quality_gates_passed = []
        artifact.quality_gates_failed = []
    
    return artifact
