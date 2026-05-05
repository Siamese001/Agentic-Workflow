"""apps_lic.engines.narrative_arc_engine — P2a Narrative Arc Engine.

Plan: .windsurf/plans/apps-lic-signal-enhancements-p2p3-spine-aligned.md W1

Builds narrative arc context for outreach drafts. Returns an immutable NarrativeArc
with sections, coherence scoring, and arc break detection.

P2a Invariants
--------------
- No durable writes.
- No provider API calls.
- No subprocess calls.
- No direct apps_research calls.
- Context-only: feeds Prompt Assembly, not direct draft composition.

Narrative Arc Sections (canonical order)
----------------------------------------
  opener    — recipient/company/role context (not sender biography for execs)
  hook      — problem or insight that connects to recipient's context
  proof     — sender credibility or repo evidence claim
  ask       — logical next step following from proof

Arc coherence requires hook→proof connection and proof→ask logical flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MessageSection:
    """A section within a narrative arc.

    Fields
    ------
    section_id       : canonical identifier (opener, hook, proof, ask)
    required_input   : input key required for this section
    forbidden_inputs : input keys that must not appear in this section
    transition_marker : phrase/concept linking to next section
    """

    section_id: str
    required_input: str
    forbidden_inputs: list[str] = field(default_factory=list)
    transition_marker: str = ""


@dataclass(frozen=True)
class NarrativeArc:
    """Result of narrative arc building.

    Fields
    ------
    sections         : ordered list of message sections
    arc_coherence_score : 0.0-1.0 score of arc logical consistency
    arc_breaks       : list of detected logical breaks
    recommended_order : suggested section ordering
    context_ref      : reference to this arc context for Prompt Assembly
    source_refs      : source references for any factual claims
    """

    sections: list[MessageSection]
    arc_coherence_score: float
    arc_breaks: list[str] = field(default_factory=list)
    recommended_order: list[str] = field(default_factory=list)
    context_ref: str = "narrative_arc_context"
    source_refs: list[str] = field(default_factory=list)


def _detect_recipient_bucket(recipient_class: str) -> str:
    """Map recipient class to bucket for arc policy."""
    rc = recipient_class.upper()
    exec_classes = {"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG", "HIRING_MANAGER"}
    recruiter_classes = {"RECRUITER", "SENIOR_TA"}
    if rc in exec_classes:
        return "exec"
    if rc in recruiter_classes:
        return "recruiter"
    return "default"


def _score_arc_coherence(
    sections: list[MessageSection],
    recipient_bucket: str,
    has_company_briefing: bool,
    has_sender_credibility: bool,
) -> tuple[float, list[str]]:
    """Score narrative arc coherence and detect breaks.

    Returns (score, arc_breaks).
    """
    arc_breaks: list[str] = []
    score = 1.0

    # Check section presence
    section_ids = {s.section_id for s in sections}
    required = {"opener", "hook", "proof", "ask"}
    missing = required - section_ids
    if missing:
        arc_breaks.append(f"missing_sections:{','.join(missing)}")
        score -= 0.3 * len(missing)

    # Check hook→proof connection
    hook_section = next((s for s in sections if s.section_id == "hook"), None)
    proof_section = next((s for s in sections if s.section_id == "proof"), None)
    if hook_section and proof_section:
        if not hook_section.transition_marker:
            arc_breaks.append("hook_to_proof_disconnect")
            score -= 0.2
    elif hook_section and not proof_section:
        arc_breaks.append("hook_without_proof")
        score -= 0.25

    # Check proof→ask connection
    ask_section = next((s for s in sections if s.section_id == "ask"), None)
    if proof_section and ask_section:
        if not proof_section.transition_marker:
            arc_breaks.append("proof_to_ask_disconnect")
            score -= 0.15
    elif ask_section and not proof_section:
        arc_breaks.append("ask_without_proof")
        score -= 0.25

    # Executive policy: opener must not lead with sender biography
    if recipient_bucket == "exec":
        opener = next((s for s in sections if s.section_id == "opener"), None)
        if opener and "sender_bio" in opener.required_input.lower():
            arc_breaks.append("exec_opener_leads_with_sender_bio")
            score -= 0.3

    # Penalty for missing evidence
    if not has_sender_credibility:
        arc_breaks.append("missing_sender_credibility")
        score -= 0.15

    # Clamp score
    score = max(0.0, min(1.0, score))
    return score, arc_breaks


def build_narrative_arc_context(
    *,
    recipient_class: str,
    company_name: str | None = None,
    role_context: str | None = None,
    sender_credibility_claims: list[str] | None = None,
    problem_insight: str | None = None,
    ask_output: str | None = None,
    is_recruiter_followup: bool = False,
) -> NarrativeArc:
    """Build narrative arc context for Prompt Assembly.

    Parameters
    ----------
    recipient_class        : e.g. "EXECUTIVE", "RECRUITER"
    company_name           : recipient's company (optional)
    role_context           : recipient's role/title (optional)
    sender_credibility_claims : list of credibility claims for proof section
    problem_insight        : problem or insight for hook section
    ask_output             : the ask/call-to-action
    is_recruiter_followup  : if True, use compact recruiter-friendly arc

    Returns
    -------
    NarrativeArc with sections, coherence score, and any arc breaks.
    """
    recipient_bucket = _detect_recipient_bucket(recipient_class)
    has_company_briefing = company_name is not None
    has_sender_credibility = bool(sender_credibility_claims)

    sections: list[MessageSection] = []

    # Build opener section
    if recipient_bucket == "exec":
        # Executive policy: lead with recipient/company/role context
        opener_input = f"recipient_context:{company_name or ''}:{role_context or ''}"
        opener_forbidden = ["sender_bio", "sender_background"]
    else:
        opener_input = f"recipient_context:{company_name or ''}:{role_context or ''}"
        opener_forbidden = []

    sections.append(
        MessageSection(
            section_id="opener",
            required_input=opener_input,
            forbidden_inputs=opener_forbidden,
            transition_marker="problem_or_insight",
        )
    )

    # Build hook section
    if is_recruiter_followup:
        # Compact arc for recruiter follow-up
        hook_input = problem_insight or "prior_engagement_context"
        hook_transition = "fit_signal"
    else:
        hook_input = problem_insight or "recipient_context_problem"
        # Hook must connect to same problem as proof
        hook_transition = "solution_or_credibility"

    sections.append(
        MessageSection(
            section_id="hook",
            required_input=hook_input,
            forbidden_inputs=[],
            transition_marker=hook_transition,
        )
    )

    # Build proof section
    if sender_credibility_claims:
        proof_input = "credibility_claims:" + "|".join(sender_credibility_claims)
    else:
        proof_input = "sender_evidence_required"

    sections.append(
        MessageSection(
            section_id="proof",
            required_input=proof_input,
            forbidden_inputs=[],
            transition_marker="logical_next_step",
        )
    )

    # Build ask section
    sections.append(
        MessageSection(
            section_id="ask",
            required_input=ask_output or "call_to_action",
            forbidden_inputs=[],
            transition_marker="",
        )
    )

    # Score coherence
    coherence_score, arc_breaks = _score_arc_coherence(
        sections=sections,
        recipient_bucket=recipient_bucket,
        has_company_briefing=has_company_briefing,
        has_sender_credibility=has_sender_credibility,
    )

    # Determine recommended order
    if is_recruiter_followup and recipient_bucket == "recruiter":
        # Compact order: opener (brief), fit signal, ask
        recommended_order = ["opener", "hook", "ask"]
        # Remove proof for compact recruiter arc if desired
        if coherence_score < 0.7:
            sections = [s for s in sections if s.section_id != "proof"]
            recommended_order = ["opener", "hook", "ask"]
    else:
        recommended_order = ["opener", "hook", "proof", "ask"]

    return NarrativeArc(
        sections=sections,
        arc_coherence_score=coherence_score,
        arc_breaks=arc_breaks,
        recommended_order=recommended_order,
        context_ref="narrative_arc_context",
        source_refs=["recipient_class_analysis", "sender_credibility_assessment"],
    )


def should_block_draft_due_to_arc_breaks(
    arc: NarrativeArc,
    recipient_class: str,
) -> tuple[bool, str]:
    """Determine if arc breaks should block draft production.

    Returns (should_block, reason).
    """
    exec_classes = {"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG", "HIRING_MANAGER"}

    # Fail-closed policy for executives
    if recipient_class.upper() in exec_classes:
        if arc.arc_coherence_score < 0.6:
            return True, f"arc_coherence_score {arc.arc_coherence_score:.2f} < 0.6 for exec"
        if "exec_opener_leads_with_sender_bio" in arc.arc_breaks:
            return True, "exec opener leads with sender biography"

    # Contextual/soft for recruiters
    if arc.arc_coherence_score < 0.4:
        return True, f"arc_coherence_score {arc.arc_coherence_score:.2f} critically low"

    return False, ""


__all__ = [
    "MessageSection",
    "NarrativeArc",
    "build_narrative_arc_context",
    "should_block_draft_due_to_arc_breaks",
]
