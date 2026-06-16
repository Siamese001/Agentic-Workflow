"""Deterministic message-intelligence packet for apps_lic outreach.

This module reuses the legacy rich outreach engines as governed data producers.
It does not call providers, retrieve new data, write state, or promote evidence
into instructions.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from apps_lic.engines.asymmetric_insight_engine import (
    AsymmetricInsight,
    AsymmetricInsightEngine,
    InsightRequirement,
)
from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY,
    NAMESPACE_COMPANY_TRIGGER,
    NAMESPACE_JD,
    NAMESPACE_PRIOR_THREAD,
    NAMESPACE_REFERRAL,
    NAMESPACE_RELATIONSHIP,
    NAMESPACE_ROLE_OWNERSHIP,
    OpportunityFactDocument,
)
from apps_lic.engines.narrative_arc_engine import (
    NarrativeArc,
    build_narrative_arc_context,
    should_block_draft_due_to_arc_breaks,
)
from apps_lic.engines.recipient_trigger_engine import (
    TRIGGER_TYPE_APPLICATION,
    TRIGGER_TYPE_COMPANY_STRATEGY,
    TRIGGER_TYPE_HIRING_PRIORITY,
    TRIGGER_TYPE_RELATIONSHIP,
    TRIGGER_TYPE_ROLE_CONTEXT,
    RecipientTrigger,
    RecipientTriggerEngine,
    TriggerEvaluationResult,
)
from apps_lic.engines.scope_calibrated_ask_engine import (
    AskCalibration,
    ScopeCalibratedAskEngine,
)
from apps_lic.engines.sender_proof_graph import SenderProofGraphPacket


SCHEMA_VERSION = "apps_lic.message_intelligence_packet.v1"

REASON_RECIPIENT_TRIGGER_FAIL_CLOSED = "recipient_trigger_fail_closed"
REASON_ASYMMETRIC_INSIGHT_FAIL_CLOSED = "asymmetric_insight_fail_closed"
REASON_NARRATIVE_ARC_BLOCK = "narrative_arc_block"
REASON_ASK_CALIBRATION_BOUND_FAIL = "ask_calibration_bound_fail"


@dataclass(frozen=True)
class MessageIntelligencePacket:
    """Replayable data packet used by PA/L2 for high-signal outreach."""

    packet_id: str
    ready: bool
    recipient_class: str
    message_type: str
    channel: str
    outreach_mode: str
    company_insight: str
    role_context: str
    value_proposition: str
    selected_triggers: tuple[RecipientTrigger, ...]
    trigger_evaluation: TriggerEvaluationResult
    asymmetric_insights: tuple[AsymmetricInsight, ...]
    asymmetric_insight_requirement: InsightRequirement
    narrative_arc: NarrativeArc
    ask_calibration: AskCalibration
    blocking_reasons: tuple[str, ...]
    source_refs: tuple[str, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "packet_id": self.packet_id,
            "ready": self.ready,
            "recipient_class": self.recipient_class,
            "message_type": self.message_type,
            "channel": self.channel,
            "outreach_mode": self.outreach_mode,
            "company_insight": self.company_insight,
            "role_context": self.role_context,
            "value_proposition": self.value_proposition,
            "selected_triggers": [_trigger_to_packet(item) for item in self.selected_triggers],
            "trigger_evaluation": _trigger_evaluation_to_packet(self.trigger_evaluation),
            "asymmetric_insights": [
                _asymmetric_insight_to_packet(item) for item in self.asymmetric_insights
            ],
            "asymmetric_insight_requirement": _insight_requirement_to_packet(
                self.asymmetric_insight_requirement
            ),
            "narrative_arc": _narrative_arc_to_packet(self.narrative_arc),
            "ask_calibration": _ask_calibration_to_packet(self.ask_calibration),
            "blocking_reasons": list(self.blocking_reasons),
            "source_refs": list(self.source_refs),
            "warnings": list(self.warnings),
        }


def build_message_intelligence_packet(
    *,
    recipient_class: str,
    message_type: str,
    channel: str,
    outreach_mode: str,
    opportunity_documents: Iterable[OpportunityFactDocument],
    target_context: Mapping[str, str],
    jd_fields: Mapping[str, str],
    proof_packet: SenderProofGraphPacket,
    campaign_objective: str = "",
    desired_next_step: str = "",
) -> MessageIntelligencePacket:
    """Build the governed rich-routing packet from already-ingested facts."""
    documents = tuple(opportunity_documents)
    company_insight, company_ref = _company_insight(documents, target_context)
    role_context, role_ref = _role_context(documents, jd_fields, target_context)
    source_refs = _source_refs(documents, company_ref, role_ref)
    triggers = _recipient_triggers(documents, jd_fields, target_context)
    trigger_evaluation = RecipientTriggerEngine().evaluate(
        triggers=list(triggers),
        recipient_class=recipient_class,
        outreach_mode=outreach_mode,
        omission_policy="omit_unsupported",
    )
    selected_triggers = tuple(
        decision.trigger
        for decision in trigger_evaluation.trigger_decisions
        if decision.verdict == "use"
    )

    insights = _asymmetric_insights(company_insight, company_ref, role_context, role_ref)
    insight_requirement = AsymmetricInsightEngine().evaluate(
        recipient_class=recipient_class,
        outreach_mode=outreach_mode,
        insight_provided=bool(insights),
        omission_policy="omit_unsupported",
        insights=insights,
    )
    ask_calibration = ScopeCalibratedAskEngine().calibrate(
        recipient_class=recipient_class,
        outreach_mode=outreach_mode,
        channel=_ask_channel(channel),
        relationship_distance=_relationship_distance(outreach_mode, documents),
        hiring_posture=_hiring_posture(documents, message_type),
    )
    value_proposition = _value_proposition(
        recipient_class=recipient_class,
        proof_packet=proof_packet,
        company_insight=company_insight,
        role_context=role_context,
    )
    proof_claims = tuple(
        _clean(point.claim_text)
        for point in proof_packet.selected_proof_points
        if _clean(point.claim_text)
    )
    narrative_arc = build_narrative_arc_context(
        recipient_class=recipient_class,
        company_name=_clean(target_context.get("company")),
        role_context=role_context,
        sender_credibility_claims=list(proof_claims[:2]),
        problem_insight=company_insight or campaign_objective,
        ask_output=ask_calibration.recommended_cta or desired_next_step,
        is_recruiter_followup=outreach_mode == "followup"
        and recipient_class in {"RECRUITER", "SENIOR_TA"},
    )
    arc_blocked, arc_reason = should_block_draft_due_to_arc_breaks(
        narrative_arc,
        recipient_class,
    )

    blocking: list[str] = []
    if trigger_evaluation.is_fail_closed:
        blocking.append(REASON_RECIPIENT_TRIGGER_FAIL_CLOSED)
    if insight_requirement.is_fail_closed:
        blocking.append(REASON_ASYMMETRIC_INSIGHT_FAIL_CLOSED)
    if arc_blocked:
        blocking.append(f"{REASON_NARRATIVE_ARC_BLOCK}:{arc_reason}")
    if ask_calibration.is_bound_fail:
        blocking.append(REASON_ASK_CALIBRATION_BOUND_FAIL)

    warnings = tuple(
        dict.fromkeys(
            (
                *trigger_evaluation.warnings,
                *insight_requirement.warnings,
                *ask_calibration.warnings,
                *narrative_arc.arc_breaks,
            )
        )
    )
    payload_seed = {
        "recipient_class": recipient_class,
        "message_type": message_type,
        "channel": channel,
        "outreach_mode": outreach_mode,
        "company_insight": company_insight,
        "role_context": role_context,
        "value_proposition": value_proposition,
        "selected_triggers": [_trigger_to_packet(item) for item in selected_triggers],
        "asymmetric_insights": [
            _asymmetric_insight_to_packet(item) for item in insights
        ],
        "ask_calibration": _ask_calibration_to_packet(ask_calibration),
        "source_refs": source_refs,
        "blocking_reasons": blocking,
    }
    return MessageIntelligencePacket(
        packet_id=_sha256_canonical(payload_seed),
        ready=not blocking,
        recipient_class=recipient_class,
        message_type=message_type,
        channel=channel,
        outreach_mode=outreach_mode,
        company_insight=company_insight,
        role_context=role_context,
        value_proposition=value_proposition,
        selected_triggers=selected_triggers,
        trigger_evaluation=trigger_evaluation,
        asymmetric_insights=insights,
        asymmetric_insight_requirement=insight_requirement,
        narrative_arc=narrative_arc,
        ask_calibration=ask_calibration,
        blocking_reasons=tuple(dict.fromkeys(blocking)),
        source_refs=source_refs,
        warnings=warnings,
    )


def _sha256_canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _short(value: Any, *, max_chars: int = 260) -> str:
    cleaned = _clean(value)
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rsplit(" ", 1)[0].rstrip(" ,;:") + "."


def _source_ref(document: OpportunityFactDocument) -> str:
    metadata = dict(document.metadata)
    return _clean(
        metadata.get("source_ref")
        or metadata.get("url")
        or document.source_snapshot_id
    )


def _source_refs(
    documents: tuple[OpportunityFactDocument, ...],
    *extra_refs: str,
) -> tuple[str, ...]:
    refs = [_source_ref(document) for document in documents]
    refs.extend(_clean(item) for item in extra_refs)
    return tuple(dict.fromkeys(ref for ref in refs if ref))


def _company_insight(
    documents: tuple[OpportunityFactDocument, ...],
    target_context: Mapping[str, str],
) -> tuple[str, str]:
    for namespace in (NAMESPACE_COMPANY_TRIGGER, NAMESPACE_COMPANY):
        for document in documents:
            if document.namespace != namespace:
                continue
            metadata = dict(document.metadata)
            text = _clean(metadata.get("trigger_text") or document.fact_text)
            if text:
                return _short(text), _source_ref(document)
    return _short(target_context.get("company_context")), ""


def _role_context(
    documents: tuple[OpportunityFactDocument, ...],
    jd_fields: Mapping[str, str],
    target_context: Mapping[str, str],
) -> tuple[str, str]:
    position = _clean(jd_fields.get("position_name") or jd_fields.get("job_title"))
    req = _clean(jd_fields.get("requisition_number"))
    if position:
        label = f"{position} ({req})" if req else position
        return label, _document_ref(documents, NAMESPACE_JD)
    ownership = _clean(target_context.get("role_ownership_signal"))
    if ownership:
        return _short(ownership), _document_ref(documents, NAMESPACE_ROLE_OWNERSHIP)
    return _clean(target_context.get("title")), ""


def _document_ref(
    documents: tuple[OpportunityFactDocument, ...],
    namespace: str,
) -> str:
    for document in documents:
        if document.namespace == namespace:
            return _source_ref(document)
    return ""


def _recipient_triggers(
    documents: tuple[OpportunityFactDocument, ...],
    jd_fields: Mapping[str, str],
    target_context: Mapping[str, str],
) -> tuple[RecipientTrigger, ...]:
    triggers: list[RecipientTrigger] = []
    for document in documents:
        metadata = dict(document.metadata)
        text = _clean(metadata.get("trigger_text") or metadata.get("ownership_signal") or document.fact_text)
        if not text:
            continue
        trigger_type = ""
        if document.namespace == NAMESPACE_COMPANY_TRIGGER:
            trigger_type = TRIGGER_TYPE_COMPANY_STRATEGY
        elif document.namespace == NAMESPACE_COMPANY:
            trigger_type = TRIGGER_TYPE_COMPANY_STRATEGY
        elif document.namespace == NAMESPACE_JD:
            trigger_type = TRIGGER_TYPE_ROLE_CONTEXT
        elif document.namespace == NAMESPACE_ROLE_OWNERSHIP:
            trigger_type = TRIGGER_TYPE_HIRING_PRIORITY
        elif document.namespace in {NAMESPACE_RELATIONSHIP, NAMESPACE_REFERRAL}:
            trigger_type = TRIGGER_TYPE_RELATIONSHIP
        elif document.namespace == NAMESPACE_PRIOR_THREAD:
            trigger_type = TRIGGER_TYPE_APPLICATION
        if not trigger_type:
            continue
        triggers.append(
            RecipientTrigger(
                trigger_type=trigger_type,
                description=_short(text, max_chars=180),
                source_ref=_source_ref(document),
                confidence=float(document.confidence or 0.0),
            )
        )
    if not triggers and _clean(jd_fields.get("position_name") or target_context.get("title")):
        triggers.append(
            RecipientTrigger(
                trigger_type=TRIGGER_TYPE_ROLE_CONTEXT,
                description=_short(jd_fields.get("position_name") or target_context.get("title")),
                source_ref=_clean(jd_fields.get("source_ref")) or "jd_fields",
                confidence=0.75,
            )
        )
    return tuple(triggers)


def _asymmetric_insights(
    company_insight: str,
    company_ref: str,
    role_context: str,
    role_ref: str,
) -> tuple[AsymmetricInsight, ...]:
    if company_insight and company_ref:
        return (
            AsymmetricInsight(
                insight_text=company_insight,
                source_ref=company_ref,
                insight_type="company_strategy",
                confidence=0.85,
            ),
        )
    if role_context and role_ref:
        return (
            AsymmetricInsight(
                insight_text=role_context,
                source_ref=role_ref,
                insight_type="role_context",
                confidence=0.75,
            ),
        )
    return ()


def _ask_channel(channel: str) -> str:
    lowered = str(channel or "").strip().lower()
    if "linkedin" in lowered:
        return "linkedin"
    return lowered or "linkedin"


def _relationship_distance(
    outreach_mode: str,
    documents: tuple[OpportunityFactDocument, ...],
) -> str:
    mode = str(outreach_mode or "").strip().lower()
    if mode == "referral" or any(document.namespace == NAMESPACE_REFERRAL for document in documents):
        return "referral"
    if mode in {"warm", "followup"} or any(
        document.namespace in {NAMESPACE_RELATIONSHIP, NAMESPACE_PRIOR_THREAD}
        for document in documents
    ):
        return "warm"
    return "cold"


def _hiring_posture(
    documents: tuple[OpportunityFactDocument, ...],
    message_type: str,
) -> str:
    if any(document.namespace == NAMESPACE_JD for document in documents):
        return "actively_hiring"
    if message_type == "role_specific":
        return "warm"
    return "unknown"


def _value_proposition(
    *,
    recipient_class: str,
    proof_packet: SenderProofGraphPacket,
    company_insight: str,
    role_context: str,
) -> str:
    proof_ids = set(proof_packet.proof_ids)
    rc = str(recipient_class or "").strip().upper()
    if rc in {"CEO", "C_LEVEL", "CTO", "EXECUTIVE", "VP_ENG"}:
        if "sp_platform_commercialization" in proof_ids:
            return (
                "governed agentic AI platform reuse with traceable controls, "
                "operating adoption, and executive-scale accountability"
            )
        return (
            "governed agentic AI execution that connects policy gates, "
            "validation controls, and regulated workflow adoption"
        )
    if rc in {"RECRUITER", "SENIOR_TA"}:
        return (
            "screenable senior AI platform fit across governed agent workflows, "
            "runtime controls, and role-specific delivery"
        )
    if role_context or company_insight:
        return (
            "hands-on governed AI platform delivery aligned to the role context "
            "and company operating signal"
        )
    return "governed AI platform delivery with evidence-backed operating judgment"


def _trigger_to_packet(trigger: RecipientTrigger) -> dict[str, Any]:
    return {
        "trigger_type": trigger.trigger_type,
        "description": trigger.description,
        "source_ref": trigger.source_ref,
        "confidence": trigger.confidence,
    }


def _trigger_evaluation_to_packet(result: TriggerEvaluationResult) -> dict[str, Any]:
    return {
        "is_satisfied": result.is_satisfied,
        "recommended_personalization_mode": result.recommended_personalization_mode,
        "hitl_required": result.hitl_required,
        "is_fail_closed": result.is_fail_closed,
        "trigger_decisions": [
            {
                "trigger": _trigger_to_packet(decision.trigger),
                "verdict": decision.verdict,
                "reason": decision.reason,
            }
            for decision in result.trigger_decisions
        ],
        "evidence_ref": result.evidence_ref,
        "warnings": list(result.warnings),
    }


def _asymmetric_insight_to_packet(insight: AsymmetricInsight) -> dict[str, Any]:
    return {
        "insight_text": insight.insight_text,
        "source_ref": insight.source_ref,
        "insight_type": insight.insight_type,
        "confidence": insight.confidence,
    }


def _insight_requirement_to_packet(requirement: InsightRequirement) -> dict[str, Any]:
    return {
        "verdict": requirement.verdict,
        "is_satisfied": requirement.is_satisfied,
        "is_fail_closed": requirement.is_fail_closed,
        "hitl_required": requirement.hitl_required,
        "rationale": requirement.rationale,
        "evidence_ref": requirement.evidence_ref,
        "warnings": list(requirement.warnings),
    }


def _narrative_arc_to_packet(arc: NarrativeArc) -> dict[str, Any]:
    return {
        "sections": [
            {
                "section_id": section.section_id,
                "required_input": section.required_input,
                "forbidden_inputs": list(section.forbidden_inputs),
                "transition_marker": section.transition_marker,
            }
            for section in arc.sections
        ],
        "arc_coherence_score": arc.arc_coherence_score,
        "arc_breaks": list(arc.arc_breaks),
        "recommended_order": list(arc.recommended_order),
        "context_ref": arc.context_ref,
        "source_refs": list(arc.source_refs),
    }


def _ask_calibration_to_packet(calibration: AskCalibration) -> dict[str, Any]:
    return {
        "ask_friction_score": calibration.ask_friction_score,
        "cta_style": calibration.cta_style,
        "is_bound_fail": calibration.is_bound_fail,
        "recommended_cta": calibration.recommended_cta,
        "reciprocity_first": calibration.reciprocity_first,
        "override_configured": calibration.override_configured,
        "evidence_ref": calibration.evidence_ref,
        "warnings": list(calibration.warnings),
    }


__all__ = [
    "MessageIntelligencePacket",
    "REASON_ASK_CALIBRATION_BOUND_FAIL",
    "REASON_ASYMMETRIC_INSIGHT_FAIL_CLOSED",
    "REASON_NARRATIVE_ARC_BLOCK",
    "REASON_RECIPIENT_TRIGGER_FAIL_CLOSED",
    "SCHEMA_VERSION",
    "build_message_intelligence_packet",
]
