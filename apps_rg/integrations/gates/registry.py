"""apps_rg Gate Registry — Adapter to RuntimeGateEngine.

Registers the apps_rg resume-generation gate pack with the agentic_core
RuntimeGateEngine. apps_rg owns domain gate definitions and callables;
agentic_core owns execution authority and write admission.

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W0.P5)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_core.runtime_gates import (
    GateDefinition,
    GateEnforcement,
    GatePlacement,
    RuntimeGateEngine,
)

if TYPE_CHECKING:
    from agentic_core.runtime_gates import GateCallable


# ----------------------------------------------------------------------------
# Gate definitions for apps_rg resume generation
# ----------------------------------------------------------------------------

RESUME_GATE_DEFINITIONS: list[GateDefinition] = [
    # P0 Critical gates — non-bypassable, FAIL_CLOSED
    GateDefinition(
        gate_id="candidate_acceptance_guard",
        placement=GatePlacement.POST_ENS,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Ensures rejected candidates are never written to resume_data",
    ),
    GateDefinition(
        gate_id="length_parity_strict",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Word count within ±15% of base section length",
        default_tolerance=0.15,
    ),
    
    # P1 Anti-fabrication gates — non-bypassable
    GateDefinition(
        gate_id="provenance_required",
        placement=GatePlacement.POST_ENS,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Quantified claims must have provenance sources",
    ),
    GateDefinition(
        gate_id="figure_citation_verification",
        placement=GatePlacement.POST_ENS,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Numeric claims must appear in master_resume",
    ),
    GateDefinition(
        gate_id="tenure_accuracy",
        placement=GatePlacement.POST_ENS,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Prose-stated years must match computed years ±1",
    ),
    GateDefinition(
        gate_id="degree_certification_unchanged",
        placement=GatePlacement.PRE_EXPORT,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Education/certs must be byte-identical to master_resume",
    ),
    
    # P2 ATS Outcomes — quality gates, CONFIGURABLE
    GateDefinition(
        gate_id="quantified_outcome_count",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Exec summary must contain ≥2 numeric claims",
    ),
    GateDefinition(
        gate_id="target_company_name_absence",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Prose must NOT contain target_company string",
    ),
    
    # P3 Voice & Polish — quality gates, CONFIGURABLE
    GateDefinition(
        gate_id="forbidden_filler_strict",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Reject candidates with banned buzzwords",
    ),
    GateDefinition(
        gate_id="forbidden_first_person_pronoun",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Reject first-person pronouns (I/my/me)",
    ),
    GateDefinition(
        gate_id="sentence_max_length",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="No sentence >40 words",
        default_tolerance=40.0,
    ),
    GateDefinition(
        gate_id="archetype_lead",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Sentence 1 must contain archetype string",
    ),
    # W1: Structural and provenance gates for exec_summary
    GateDefinition(
        gate_id="structural_slot_coverage",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Exec summary must contain 4 required structural slots (archetype, quantified_outcomes, engagement_model, value_thesis)",
    ),
    GateDefinition(
        gate_id="unsupported_appended_claim",
        placement=GatePlacement.PER_CAND,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Repaired candidates must have provenance for appended content",
    ),
    
    # P4 Coherence — quality gates, CONFIGURABLE
    GateDefinition(
        gate_id="jd_keyword_coverage_min",
        placement=GatePlacement.POST_NARR,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="JD must-have keywords ≥80% present",
    ),
    GateDefinition(
        gate_id="claim_uniqueness",
        placement=GatePlacement.POST_NARR,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Same outcome cited at most once across sections",
    ),
    GateDefinition(
        gate_id="cross_section_consistency",
        placement=GatePlacement.POST_NARR,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Archetype/tenure/outcomes consistent across sections",
    ),
    GateDefinition(
        gate_id="bullet_count_per_role",
        placement=GatePlacement.POST_NARR,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Each role has 3-5 bullets",
    ),
    GateDefinition(
        gate_id="role_chronology",
        placement=GatePlacement.POST_NARR,
        enforcement=GateEnforcement.CONFIGURABLE,
        bypassable=True,
        description="Roles strictly date-descending, no unexplained gaps >12mo",
    ),
    
    # P5 Observability — non-bypassable
    GateDefinition(
        gate_id="prompt_assembly_sha",
        placement=GatePlacement.PRE_LLM,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Hash of assembled prompt logged for replay",
    ),
    GateDefinition(
        gate_id="master_resume_sha_pinned",
        placement=GatePlacement.PRE_LLM,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Pin master_resume.json sha256, abort if changed",
    ),
    
    # PRE-EXPORT — non-bypassable
    GateDefinition(
        gate_id="docx_render_no_orphan",
        placement=GatePlacement.PRE_EXPORT,
        enforcement=GateEnforcement.FAIL_CLOSED,
        bypassable=False,
        description="Final DOCX has no empty sections or placeholders",
    ),
]


def build_resume_gate_callables() -> dict[str, "GateCallable"]:
    """Build the callable mapping for apps_rg resume gates.
    
    Returns a dict of gate_id -> callable that produces GateVerdict.
    Note: Many gates are placeholders for W1-W7 implementation.
    """
    # Placeholder callables — will be replaced with real implementations in W1-W7
    callables: dict[str, "GateCallable"] = {}
    
    # Import and wire real gate implementations as they become available
    try:
        from apps_rg.integrations.gates.per_cand_resume_gates import (
            length_parity_strict_gate,
            quantified_outcome_count_gate,
            target_company_name_absence_gate,
            forbidden_filler_strict_gate,
            sentence_max_length_gate,
            archetype_lead_gate,
            structural_slot_coverage_gate,  # W1
            unsupported_appended_claim_gate,  # W1
            first_person_lead_ban_gate,  # W4
        )
        callables["length_parity_strict"] = length_parity_strict_gate
        callables["quantified_outcome_count"] = quantified_outcome_count_gate
        callables["target_company_name_absence"] = target_company_name_absence_gate
        callables["forbidden_filler_strict"] = forbidden_filler_strict_gate
        callables["sentence_max_length"] = sentence_max_length_gate
        callables["archetype_lead"] = archetype_lead_gate
        callables["structural_slot_coverage"] = structural_slot_coverage_gate  # W1
        callables["unsupported_appended_claim"] = unsupported_appended_claim_gate  # W1
        callables["first_person_lead_ban"] = first_person_lead_ban_gate  # W4
    except ImportError:
        # Gates not yet implemented — will be empty until W5
        pass
    
    try:
        from apps_rg.integrations.gates.post_ens_resume_gates import (
            candidate_acceptance_guard_callable,
            provenance_required_gate,
            figure_citation_verification_gate,
            tenure_accuracy_gate,
        )
        callables["candidate_acceptance_guard"] = candidate_acceptance_guard_callable
        callables["provenance_required"] = provenance_required_gate
        callables["figure_citation_verification"] = figure_citation_verification_gate
        callables["tenure_accuracy"] = tenure_accuracy_gate
    except ImportError:
        pass
    
    try:
        from apps_rg.integrations.gates.post_narr_resume_gates import (
            jd_keyword_coverage_min_gate,
            claim_uniqueness_gate,
            cross_section_consistency_gate,
            bullet_count_per_role_gate,
            role_chronology_gate,
        )
        callables["jd_keyword_coverage_min"] = jd_keyword_coverage_min_gate
        callables["claim_uniqueness"] = claim_uniqueness_gate
        callables["cross_section_consistency"] = cross_section_consistency_gate
        callables["bullet_count_per_role"] = bullet_count_per_role_gate
        callables["role_chronology"] = role_chronology_gate
    except ImportError:
        pass
    
    try:
        from apps_rg.integrations.gates.pre_export_resume_gates import (
            degree_certification_unchanged_gate,
            docx_render_no_orphan_gate,
        )
        callables["degree_certification_unchanged"] = degree_certification_unchanged_gate
        callables["docx_render_no_orphan"] = docx_render_no_orphan_gate
    except ImportError:
        pass
    
    try:
        from apps_rg.integrations.gates.pre_llm_gates import (
            prompt_assembly_sha_gate,
            master_resume_sha_pinned_gate,
        )
        callables["prompt_assembly_sha"] = prompt_assembly_sha_gate
        callables["master_resume_sha_pinned"] = master_resume_sha_pinned_gate
    except ImportError:
        pass
    
    return callables


def register_apps_rg_gate_pack(engine: RuntimeGateEngine) -> None:
    """Register the apps_rg resume-generation gate pack with the RuntimeGateEngine.
    
    This is the entrypoint called during apps_rg initialization to wire its
gates into the core runtime authority.
    
    Args:
        engine: The RuntimeGateEngine to register with
    """
    callables = build_resume_gate_callables()
    engine.register_gate_pack(
        app_id="apps_rg",
        definitions=RESUME_GATE_DEFINITIONS,
        callables=callables,
    )


__all__ = [
    "RESUME_GATE_DEFINITIONS",
    "build_resume_gate_callables",
    "register_apps_rg_gate_pack",
]
