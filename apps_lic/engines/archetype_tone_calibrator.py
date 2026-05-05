"""apps_lic.engines.archetype_tone_calibrator — P2b Archetype Tone Calibrator.

Plan: .windsurf/plans/apps-lic-signal-enhancements-p2p3-spine-aligned.md W2

Calibrates tone and register based on recipient archetype detection.
Returns an immutable ArchetypeToneCalibration for Prompt Assembly.

P2b Invariants
--------------
- No durable writes.
- No provider API calls.
- No subprocess calls.
- No direct apps_research calls.
- Tone affects phrasing constraints only, never factual claims.
- Context-only: feeds Prompt Assembly, not direct draft composition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ArchetypeToneCalibration:
    """Result of archetype tone calibration.

    Fields
    ------
    archetype_id        : detected archetype (TECHNICAL_BUILDER, BUSINESS_EXECUTIVE, etc.)
    confidence          : detection confidence 0.0-1.0
    detection_signals   : signals that led to archetype detection
    vocabulary_boosted  : vocabulary to emphasize
    vocabulary_suppressed : vocabulary to avoid
    sentence_structure_hint : structural guidance
    register            : tone register (formal, casual, technical, etc.)
    context_ref         : reference for Prompt Assembly
    """

    archetype_id: str
    confidence: float
    detection_signals: list[str] = field(default_factory=list)
    vocabulary_boosted: list[str] = field(default_factory=list)
    vocabulary_suppressed: list[str] = field(default_factory=list)
    sentence_structure_hint: str = ""
    register: str = ""
    context_ref: str = "archetype_tone_calibration"


# Archetype definitions with tone policies
_ARCHETYPE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "TECHNICAL_BUILDER": {
        "detection_signals": [
            "github_repo_mentions",
            "technical_blog_posts",
            "oss_contributions",
            "architecture_discussions",
            "engineering_leadership",
        ],
        "vocabulary_boosted": [
            "architecture", "performance", "scalability", "reliability",
            "system design", "trade-offs", "implementation",
        ],
        "vocabulary_suppressed": [
            "synergy", "leverage", "paradigm", "strategic alignment",
            "value proposition", "stakeholder buy-in", "vertical integration",
        ],
        "sentence_structure_hint": "specific over abstract; mechanism over outcome",
        "register": "technical_precise",
    },
    "BUSINESS_EXECUTIVE": {
        "detection_signals": [
            "c_suite_title",
            "p_l_ownership",
            "business_strategy_focus",
            "market_expansion",
            "revenue_growth",
        ],
        "vocabulary_boosted": [
            "outcome", "impact", "growth", "efficiency", "roi",
            "time-to-value", "competitive advantage", "market position",
        ],
        "vocabulary_suppressed": [
            "implementation details", "code structure", "database schema",
            "api endpoints", "dependency injection", "refactoring",
        ],
        "sentence_structure_hint": "outcome over mechanism; business value over technical detail",
        "register": "business_outcome",
    },
    "RESEARCH_ACADEMIC": {
        "detection_signals": [
            "phd_credentials",
            "research_publications",
            "conference_presentations",
            "lab_leadership",
            "novel_methodology",
        ],
        "vocabulary_boosted": [
            "evidence", "methodology", "findings", "analysis", "validation",
            "peer review", "empirical", "hypothesis", "experiment",
        ],
        "vocabulary_suppressed": [
            "revolutionary", "game-changing", "disruptive", "world-class",
            "cutting-edge", "thought leader", "visionary",
        ],
        "sentence_structure_hint": "evidence over assertion; method over hype",
        "register": "evidence_based",
    },
    "TALENT_SCOUT": {
        "detection_signals": [
            "recruiter_title",
            "talent_acquisition",
            "candidate_experience",
            "culture_fit",
            "hiring_velocity",
        ],
        "vocabulary_boosted": [
            "fit", "opportunity", "potential", "growth trajectory",
            "impact", "team alignment", "mission match",
        ],
        "vocabulary_suppressed": [
            "aggressive", "dominate", "crush", "kill it",
            "rockstar", "ninja", "guru", "10x",
        ],
        "sentence_structure_hint": "fit signal over hype; opportunity over pressure",
        "register": "opportunity_focussed",
    },
    "UNKNOWN": {
        "detection_signals": [],
        "vocabulary_boosted": [],
        "vocabulary_suppressed": [],
        "sentence_structure_hint": "concise professional",
        "register": "concise_professional",
    },
}


def _detect_archetype_from_signals(
    recipient_class: str,
    recipient_seniority: str | None = None,
    recipient_trigger_vector: list[str] | None = None,
    company_briefing: dict[str, Any] | None = None,
) -> tuple[str, float, list[str]]:
    """Detect archetype from available signals.

    Returns (archetype_id, confidence, detection_signals).
    """
    signals: list[str] = []
    archetype_scores: dict[str, float] = {k: 0.0 for k in _ARCHETYPE_DEFINITIONS}
    
    # Score from recipient class
    rc = recipient_class.upper()
    if rc in {"CTO", "VP_ENG", "ENGINEERING_MANAGER", "TECHNICAL_LEAD"}:
        archetype_scores["TECHNICAL_BUILDER"] += 0.4
        signals.append(f"recipient_class:{rc}")
    elif rc in {"CEO", "CFO", "COO", "C_LEVEL", "EXECUTIVE"}:
        archetype_scores["BUSINESS_EXECUTIVE"] += 0.5
        signals.append(f"recipient_class:{rc}")
    elif rc in {"RECRUITER", "SENIOR_TA", "TALENT_ACQUISITION"}:
        archetype_scores["TALENT_SCOUT"] += 0.6
        signals.append(f"recipient_class:{rc}")
    elif rc in {"RESEARCH_SCIENTIST", "PRINCIPAL_SCIENTIST", "PHD"}:
        archetype_scores["RESEARCH_ACADEMIC"] += 0.5
        signals.append(f"recipient_class:{rc}")
    
    # Score from seniority
    if recipient_seniority:
        rs = recipient_seniority.upper()
        if "TECHNICAL" in rs or "ENGINEERING" in rs:
            archetype_scores["TECHNICAL_BUILDER"] += 0.2
            signals.append(f"seniority:{rs}")
        elif "EXECUTIVE" in rs or "C_LEVEL" in rs:
            archetype_scores["BUSINESS_EXECUTIVE"] += 0.3
            signals.append(f"seniority:{rs}")
    
    # Score from trigger vector
    if recipient_trigger_vector:
        for trigger in recipient_trigger_vector:
            trigger_lower = trigger.lower()
            if any(t in trigger_lower for t in ["github", "repo", "code", "architecture", "system"]):
                archetype_scores["TECHNICAL_BUILDER"] += 0.15
                signals.append(f"trigger:technical:{trigger}")
            elif any(t in trigger_lower for t in ["revenue", "growth", "strategy", "business", "market"]):
                archetype_scores["BUSINESS_EXECUTIVE"] += 0.15
                signals.append(f"trigger:business:{trigger}")
            elif any(t in trigger_lower for t in ["research", "phd", "paper", "study", "academic"]):
                archetype_scores["RESEARCH_ACADEMIC"] += 0.15
                signals.append(f"trigger:research:{trigger}")
            elif any(t in trigger_lower for t in ["hiring", "talent", "culture", "team"]):
                archetype_scores["TALENT_SCOUT"] += 0.15
                signals.append(f"trigger:talent:{trigger}")
    
    # Score from company briefing
    if company_briefing:
        briefing_str = str(company_briefing).lower()
        if any(t in briefing_str for t in ["technical", "engineering", "product", "platform"]):
            archetype_scores["TECHNICAL_BUILDER"] += 0.1
            signals.append("briefing:technical_language")
        if any(t in briefing_str for t in ["research", "innovation", "patent", "study"]):
            archetype_scores["RESEARCH_ACADEMIC"] += 0.1
            signals.append("briefing:research_language")
    
    # Find best match
    best_archetype = max(archetype_scores, key=archetype_scores.get)
    best_score = archetype_scores[best_archetype]
    
    # Confidence calculation
    # If score is very low, fall back to UNKNOWN
    if best_score < 0.15:
        return "UNKNOWN", 0.3, signals
    
    # Cap confidence at 0.95 (never 100% certain)
    confidence = min(0.95, best_score + 0.2)
    
    return best_archetype, confidence, signals


def calibrate_archetype_tone(
    *,
    recipient_class: str,
    recipient_seniority: str | None = None,
    recipient_trigger_vector: list[str] | None = None,
    company_briefing: dict[str, Any] | None = None,
) -> ArchetypeToneCalibration:
    """Calibrate tone based on detected recipient archetype.

    Parameters
    ----------
    recipient_class        : e.g. "EXECUTIVE", "RECRUITER"
    recipient_seniority    : e.g. "VP", "Director", "Staff Engineer"
    recipient_trigger_vector : list of trigger words/phrases from research
    company_briefing       : company briefing dict if available

    Returns
    -------
    ArchetypeToneCalibration with vocabulary and register guidance.
    """
    # Detect archetype
    archetype_id, confidence, detection_signals = _detect_archetype_from_signals(
        recipient_class=recipient_class,
        recipient_seniority=recipient_seniority,
        recipient_trigger_vector=recipient_trigger_vector,
        company_briefing=company_briefing,
    )
    
    # Get archetype definition
    archetype_def = _ARCHETYPE_DEFINITIONS.get(archetype_id, _ARCHETYPE_DEFINITIONS["UNKNOWN"])
    
    # If confidence is low, use recipient_class fallback
    if confidence < 0.4:
        # Fallback based on recipient_class
        rc = recipient_class.upper()
        if rc in {"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"}:
            archetype_id = "BUSINESS_EXECUTIVE"
            archetype_def = _ARCHETYPE_DEFINITIONS["BUSINESS_EXECUTIVE"]
        elif rc in {"RECRUITER", "SENIOR_TA"}:
            archetype_id = "TALENT_SCOUT"
            archetype_def = _ARCHETYPE_DEFINITIONS["TALENT_SCOUT"]
        else:
            archetype_id = "UNKNOWN"
            archetype_def = _ARCHETYPE_DEFINITIONS["UNKNOWN"]
    
    return ArchetypeToneCalibration(
        archetype_id=archetype_id,
        confidence=confidence,
        detection_signals=detection_signals,
        vocabulary_boosted=list(archetype_def["vocabulary_boosted"]),
        vocabulary_suppressed=list(archetype_def["vocabulary_suppressed"]),
        sentence_structure_hint=archetype_def["sentence_structure_hint"],
        register=archetype_def["register"],
        context_ref="archetype_tone_calibration",
    )


def check_tone_violations(
    message_text: str,
    calibration: ArchetypeToneCalibration,
) -> list[str]:
    """Check if message violates tone calibration constraints.

    Returns list of violation descriptions.
    """
    violations: list[str] = []
    text_lower = message_text.lower()
    
    # Check for suppressed vocabulary
    for suppressed in calibration.vocabulary_suppressed:
        if suppressed.lower() in text_lower:
            violations.append(f"suppressed_vocabulary:{suppressed}")
    
    # Special checks per archetype
    if calibration.archetype_id == "TECHNICAL_BUILDER":
        # Count business jargon instances
        business_jargon = [
            "synergy", "leverage", "paradigm", "strategic alignment",
            "value proposition", "stakeholder buy-in",
        ]
        jargon_count = sum(1 for j in business_jargon if j in text_lower)
        if jargon_count >= 2:
            violations.append(f"technical_builder_excessive_business_jargon:{jargon_count}")
    
    elif calibration.archetype_id == "BUSINESS_EXECUTIVE":
        # Check for excessive implementation detail
        detail_indicators = [
            "database schema", "api endpoint", "function calls",
            "class hierarchy", "dependency injection", "unit tests",
        ]
        detail_count = sum(1 for d in detail_indicators if d in text_lower)
        if detail_count >= 3:
            violations.append(f"business_executive_excessive_detail:{detail_count}")
    
    return violations


__all__ = [
    "ArchetypeToneCalibration",
    "calibrate_archetype_tone",
    "check_tone_violations",
]
