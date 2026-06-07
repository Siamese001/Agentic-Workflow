"""apps_lic.engines.competitive_landscape_engine — P2c Competitive Landscape Engine.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-signal-enhancements-p2p3-spine-aligned.md W3

Builds competitive landscape context for outreach drafts.
Returns an immutable CompetitiveLandscapeContext for Prompt Assembly.

P2c Invariants
--------------
- No direct apps_research calls — uses company_briefing from R3 manifest.
- Skipped when no competitive context with source refs in company_briefing.
- Confidence < 0.5 means skip competitive claims, not fabricate.
- Source refs required for any company-specific differentiator claim.
- Maximum one differentiator sentence in final draft.
- Only added after validate_research_and_build_manifest (R3R4 managed).
- Context-only: feeds Prompt Assembly, not direct draft composition.

Fallback Modes
--------------
- When fallback_mode=true: no company-specific differentiator claim allowed.
- When competitive_signals empty or confidence < 0.5: skip entirely.
- When source_refs missing: skip with warning, never fabricate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CompetitiveLandscapeContext:
    """Result of competitive landscape analysis.

    Fields
    ------
    differentiator_claim    : single-sentence differentiator (or empty if skipped)
    competitive_signals     : signals from company briefing
    confidence              : 0.0-1.0 confidence in differentiator
    source_refs             : source references for any claims
    fallback_mode           : if True, no company-specific claims allowed
    skipped                 : if True, context was skipped (see skip_reason)
    skip_reason             : reason for skipping if skipped=True
    context_ref             : reference for Prompt Assembly
    """

    differentiator_claim: str = ""
    competitive_signals: list[str] = field(default_factory=list)
    confidence: float = 0.0
    source_refs: list[str] = field(default_factory=list)
    fallback_mode: bool = False
    skipped: bool = True
    skip_reason: str = ""
    context_ref: str = "competitive_landscape_context"


def _extract_competitive_signals(
    company_briefing: dict[str, Any] | None,
) -> tuple[list[str], list[str], float]:
    """Extract competitive signals and source refs from company briefing.
    
    Returns (signals, source_refs, confidence).
    """
    if not company_briefing:
        return [], [], 0.0
    
    signals: list[str] = []
    source_refs: list[str] = []
    
    # Extract competitive context if present
    competitive_section = company_briefing.get("competitive_landscape", {})
    if not competitive_section:
        competitive_section = company_briefing.get("competitive_context", {})
    
    if competitive_section:
        # Extract signals
        if "market_position" in competitive_section:
            signals.append(f"market_position:{competitive_section['market_position']}")
        if "differentiators" in competitive_section:
            signals.append(f"differentiators:{competitive_section['differentiators']}")
        if "competitive_advantages" in competitive_section:
            signals.append(f"advantages:{competitive_section['competitive_advantages']}")
        if "industry_ranking" in competitive_section:
            signals.append(f"ranking:{competitive_section['industry_ranking']}")
        
        # Extract source refs (REQUIRED for any claim)
        briefing_sources = competitive_section.get("source_refs", [])
        source_refs.extend(briefing_sources)
        
        # Also check top-level briefing sources
        top_sources = company_briefing.get("source_refs", [])
        source_refs.extend(top_sources)
    
    # Calculate confidence based on signal quality and source presence
    confidence = 0.0
    if signals:
        confidence += 0.3  # Base for having any signals
    if source_refs:
        confidence += 0.4  # Strong boost for having sources
    if len(signals) >= 2:
        confidence += 0.2  # Multiple signals
    if len(source_refs) >= 2:
        confidence += 0.1  # Multiple sources
    
    confidence = min(0.95, confidence)  # Cap at 0.95 (never 100% certain)
    
    return signals, list(set(source_refs)), confidence


def _build_differentiator_claim(
    signals: list[str],
    confidence: float,
    source_refs: list[str],
    fallback_mode: bool,
) -> tuple[str, str]:
    """Build single-sentence differentiator claim.
    
    Returns (claim, skip_reason). Empty claim means skip.
    """
    # Skip conditions
    if fallback_mode:
        return "", "fallback_mode_active"
    
    if confidence < 0.5:
        return "", f"confidence_too_low:{confidence:.2f}"
    
    if not source_refs:
        return "", "missing_source_refs"
    
    if not signals:
        return "", "no_competitive_signals"
    
    # Build differentiator from strongest signal
    # NOTE: This is a structured placeholder that Prompt Assembly will expand
    # The actual prose generation happens at draft composition time
    differentiator_types = []
    for signal in signals:
        if signal.startswith("market_position:"):
            differentiator_types.append("market_position")
        elif signal.startswith("differentiators:"):
            differentiator_types.append("differentiator")
        elif signal.startswith("advantages:"):
            differentiator_types.append("advantage")
        elif signal.startswith("ranking:"):
            differentiator_types.append("ranking")
    
    if not differentiator_types:
        return "", "unrecognized_signal_types"
    
    # Return structured claim reference (not prose)
    # Format: type|sources|placeholder
    claim_key = f"competitive_claim:{','.join(differentiator_types)}"
    return claim_key, ""


def build_competitive_landscape_context(
    *,
    company_briefing: dict[str, Any] | None = None,
    fallback_mode: bool = False,
    recipient_class: str = "",
) -> CompetitiveLandscapeContext:
    """Build competitive landscape context for Prompt Assembly.
    
    Parameters
    ----------
    company_briefing        : Company briefing from R3 manifest (if available)
    fallback_mode           : If True, skip all company-specific claims
    recipient_class         : For gating (execs may skip differentiators)
    
    Returns
    -------
    CompetitiveLandscapeContext with differentiator or skip indication.
    """
    # Extract signals from briefing
    signals, source_refs, confidence = _extract_competitive_signals(company_briefing)
    
    # Build differentiator claim
    claim, skip_reason = _build_differentiator_claim(
        signals=signals,
        confidence=confidence,
        source_refs=source_refs,
        fallback_mode=fallback_mode,
    )
    
    # Determine if skipped
    skipped = not claim
    
    return CompetitiveLandscapeContext(
        differentiator_claim=claim,
        competitive_signals=signals,
        confidence=confidence,
        source_refs=source_refs,
        fallback_mode=fallback_mode,
        skipped=skipped,
        skip_reason=skip_reason,
        context_ref="competitive_landscape_context",
    )


def should_include_competitive_context(
    context: CompetitiveLandscapeContext,
    recipient_class: str,
) -> tuple[bool, str]:
    """Determine if competitive context should be included in draft.
    
    Returns (should_include, reason).
    """
    if context.skipped:
        return False, f"skipped:{context.skip_reason}"
    
    if context.fallback_mode:
        return False, "fallback_mode"
    
    if context.confidence < 0.5:
        return False, f"confidence_below_threshold:{context.confidence:.2f}"
    
    if not context.source_refs:
        return False, "no_source_refs"
    
    if not context.differentiator_claim:
        return False, "no_differentiator_claim"
    
    # Executive policy: may skip if confidence borderline
    exec_classes = {"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"}
    if recipient_class.upper() in exec_classes and context.confidence < 0.7:
        return False, "exec_low_confidence"
    
    return True, "confidence_and_sources_sufficient"


def validate_differentiator_for_exit(
    differentiator: str,
    source_refs: list[str],
    max_length: int = 200,
) -> tuple[bool, list[str]]:
    """Validate differentiator claim for exit rubric compliance.
    
    Returns (is_valid, violations).
    """
    violations: list[str] = []
    
    # Must have source refs
    if not source_refs:
        violations.append("missing_source_refs")
    
    # Length check (one sentence max)
    if len(differentiator) > max_length:
        violations.append(f"exceeds_max_length:{len(differentiator)}>{max_length}")
    
    # No fabrication markers
    if "[unverified]" in differentiator.lower() or "[assumed]" in differentiator.lower():
        violations.append("unverified_marker_present")
    
    # Must be structured claim format (not raw prose)
    if differentiator and not differentiator.startswith("competitive_claim:"):
        # Allow empty or structured only
        if differentiator.strip():
            violations.append("not_structured_claim_format")
    
    is_valid = len(violations) == 0
    return is_valid, violations


__all__ = [
    "CompetitiveLandscapeContext",
    "build_competitive_landscape_context",
    "should_include_competitive_context",
    "validate_differentiator_for_exit",
]
