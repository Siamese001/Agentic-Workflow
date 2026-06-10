"""PA/L2 whole-message generation contract for apps_lic W6.

W6 creates a provider-free, read-only generation request and candidate artifact
shape. Later runtime wiring can hand the request to a model provider; this
module proves the control knobs, evidence packet, and whole-message boundaries.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY,
    NAMESPACE_COMPANY_TRIGGER,
    NAMESPACE_CONTACT,
    NAMESPACE_JD,
    NAMESPACE_PRIOR_THREAD,
    NAMESPACE_REFERRAL,
    NAMESPACE_RELATIONSHIP,
    NAMESPACE_ROLE_OWNERSHIP,
    OpportunityFactDocument,
    OpportunityFactStore,
)
from apps_lic.engines.message_type_requirement_gate import (
    MESSAGE_FOLLOW_UP,
    MESSAGE_GENERAL_INTRO,
    MESSAGE_REFERRAL_ASK,
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
    MODIFIER_APPLICATION_STATUS_CLAIMED,
    MODIFIER_USES_JD,
    MODIFIER_USES_PRIOR_THREAD,
    MODIFIER_USES_REFERRAL_CONTEXT,
    MODIFIER_USES_SENSITIVE_CONSTRAINTS,
    STATUS_REQUIREMENTS_PASS,
    MessageRequirementGateResult,
)
from apps_lic.engines.recipient_classification import (
    CLASS_CEO,
    CLASS_CTO,
    CLASS_C_LEVEL,
    CLASS_EXECUTIVE,
    CLASS_HIRING_MANAGER,
    CLASS_RECRUITER,
    CLASS_SENIOR_TA,
    CLASS_VP_ENG,
    STATUS_DERIVED as RECIPIENT_STATUS_DERIVED,
    RecipientClassDerivation,
)
from apps_lic.engines.sender_proof_graph import (
    STATUS_PROOF_GRAPH_READY,
    SenderProofGraphPacket,
    validate_l2_sender_claims_against_packet,
)
from apps_lic.types.recipient_archetype_mapping import (
    resolve_recipient_template_policy,
)
from apps_lic.types.linkedin_route_envelope import CHANNEL_LINKEDIN_INMAIL


STATUS_GENERATION_REQUEST_READY = "WHOLE_MESSAGE_GENERATION_REQUEST_READY"
STATUS_GENERATION_REQUEST_BLOCKED = "WHOLE_MESSAGE_GENERATION_REQUEST_BLOCKED"
STATUS_CANDIDATES_READY = "WHOLE_MESSAGE_CANDIDATES_READY"
STATUS_CANDIDATES_BLOCKED = "WHOLE_MESSAGE_CANDIDATES_BLOCKED"
STATUS_CANDIDATE_SHAPE_PASS = "WHOLE_MESSAGE_CANDIDATE_SHAPE_PASS"
STATUS_CANDIDATE_SHAPE_BLOCKED = "WHOLE_MESSAGE_CANDIDATE_SHAPE_BLOCKED"

SC_0 = "SC-0"
SC_1 = "SC-1"
SC_2 = "SC-2"
SC_3 = "SC-3"

R0_MINIMAL = "R0_MINIMAL"
R1_STANDARD = "R1_STANDARD"
R2_DELIBERATE = "R2_DELIBERATE"
R3_STRICT = "R3_STRICT"

GENERATOR_MODEL_ID = "Qwen/Qwen2.5-32B-Instruct-AWQ"
GENERATOR_PROVIDER_ID = "vllm"

NO_DURABLE_WRITE_RECEIPT = "pass:w6_generation_contract_no_durable_write"
NO_SEND_RECEIPT = "pass:draft_only_no_auto_send"
INSTRUCTION_DATA_BOUNDARY_RECEIPT = "pass:c0_c03_payloads_are_data_only"

REASON_RECIPIENT_CLASS_NOT_DERIVED = "recipient_class_not_derived"
REASON_MESSAGE_REQUIREMENTS_NOT_PASSED = "message_requirements_not_passed"
REASON_SENDER_PROOF_NOT_READY = "sender_proof_graph_not_ready"
REASON_SEND_MODE_FORBIDDEN = "send_mode_forbidden"
REASON_CANDIDATE_NOT_WHOLE_MESSAGE = "candidate_not_whole_message"
REASON_CANDIDATE_OVER_LENGTH = "candidate_over_length_budget"
REASON_CANDIDATE_UNAPPROVED_CLAIM = "candidate_uses_claim_not_in_proof_packet"
REASON_CANDIDATE_MISSING_CTA = "candidate_missing_low_friction_cta"
REASON_CANDIDATE_MISSING_SIGNATURE = "candidate_missing_amit_signature"
REASON_CANDIDATE_MISSING_SUBJECT = "candidate_missing_inmail_subject_line"
REASON_CANDIDATE_SUBJECT_TOO_LONG = "candidate_inmail_subject_line_too_long"

_ALLOWED_SEND_MODES = {"draft_only", "review_required"}
_FORBIDDEN_FRAGMENT_MARKERS = (
    "subject:",
    "header:",
    "body:",
    "footer:",
    "opening:",
    "cta:",
    "section:",
)
_SIGNATURE_PATTERN = re.compile(
    r"(?:\r?\n|\A)\s*(?:best|thanks|regards|warmly|cheers)?[,]?\s*Amit(?: Ayer)?\.?\s*\Z",
    flags=re.IGNORECASE,
)
_CTA_PATTERN = re.compile(
    r"\b(would|could|can|open to|worth|reasonable|useful|available)\b"
    r"[^?!.]{0,120}\b(chat|call|screen|review|fit|compare notes|connect|exchange|redirect|conversation)\b",
    flags=re.IGNORECASE,
)

_SC_SETTINGS: dict[str, tuple[str, int, int, float, float]] = {
    SC_0: (R0_MINIMAL, 1, 0, 0.80, 0.90),
    SC_1: (R1_STANDARD, 1, 1, 0.86, 0.94),
    SC_2: (R2_DELIBERATE, 2, 1, 0.92, 0.94),
    SC_3: (R3_STRICT, 3, 2, 0.94, 0.95),
}


@dataclass(frozen=True)
class LengthBudget:
    budget_key: str
    min_words: int
    max_words: int
    min_sentences: int
    max_sentences: int
    hard_cap_chars: int
    channel: str = "linkedin"
    route_family: str = "LINKEDIN_DRAFT"
    subject_required: bool = False
    signature_required: bool = True
    cta_style: str = ""

    def to_packet(self) -> dict[str, Any]:
        return {
            "budget_key": self.budget_key,
            "min_words": self.min_words,
            "max_words": self.max_words,
            "min_sentences": self.min_sentences,
            "max_sentences": self.max_sentences,
            "hard_cap_chars": self.hard_cap_chars,
            "hard_controls": ["max_sentences", "hard_cap_chars"],
            "advisory_controls": ["min_words", "max_words"],
            "channel": self.channel,
            "route_family": self.route_family,
            "subject_required": self.subject_required,
            "signature_required": self.signature_required,
            "cta_style": self.cta_style,
        }


@dataclass(frozen=True)
class ReasoningPolicy:
    sc_level: str
    reasoning_intensity: str
    candidate_count: int
    repair_budget: int
    generator_temperature: float
    top_p: float
    repair_temperature: float
    judge_temperature: float
    x1d_llm_judge_depth: int
    reason_codes: tuple[str, ...]

    def to_packet(self) -> dict[str, Any]:
        return {
            "sc_level": self.sc_level,
            "reasoning_intensity": self.reasoning_intensity,
            "candidate_count": self.candidate_count,
            "repair_budget": self.repair_budget,
            "generator_temperature": self.generator_temperature,
            "top_p": self.top_p,
            "repair_temperature": self.repair_temperature,
            "judge_temperature": self.judge_temperature,
            "x1d_llm_judge_depth": self.x1d_llm_judge_depth,
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True)
class WholeMessageGenerationRequest:
    status: str
    ready: bool
    request_id: str
    trace_root: str
    channel: str
    outreach_mode: str
    send_mode: str
    recipient_class: str
    message_type: str
    modifiers: Mapping[str, bool]
    campaign_objective: str
    desired_next_step: str
    target_context: Mapping[str, str]
    jd_fields: Mapping[str, str]
    proof_packet: SenderProofGraphPacket
    length_budget: LengthBudget
    reasoning_policy: ReasoningPolicy
    prompt_contract_id: str
    component_hash_map: Mapping[str, str]
    blocking_reasons: tuple[str, ...]
    no_send_receipt: str
    no_durable_write_receipt: str
    instruction_data_boundary_receipt: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.whole_message_generation_request.v1",
            "status": self.status,
            "ready": self.ready,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "channel": self.channel,
            "outreach_mode": self.outreach_mode,
            "send_mode": self.send_mode,
            "recipient_class": self.recipient_class,
            "message_type": self.message_type,
            "modifiers": dict(self.modifiers),
            "campaign_objective": self.campaign_objective,
            "desired_next_step": self.desired_next_step,
            "target_context": dict(self.target_context),
            "jd_fields": dict(self.jd_fields),
            "proof_packet_id": self.proof_packet.proof_packet_id,
            "allowed_claim_ids": list(self.proof_packet.proof_ids),
            "length_budget": self.length_budget.to_packet(),
            "reasoning_policy": self.reasoning_policy.to_packet(),
            "prompt_contract_id": self.prompt_contract_id,
            "component_hash_map": dict(self.component_hash_map),
            "blocking_reasons": list(self.blocking_reasons),
            "no_send_receipt": self.no_send_receipt,
            "no_durable_write_receipt": self.no_durable_write_receipt,
            "instruction_data_boundary_receipt": self.instruction_data_boundary_receipt,
        }


@dataclass(frozen=True)
class WholeMessageCandidate:
    candidate_id: str
    draft_text: str
    attempt_seed: str
    model_id: str
    provider_id: str
    temperature: float
    top_p: float
    word_count: int
    sentence_count: int
    char_count: int
    claims_used: tuple[str, ...]
    is_whole_message: bool
    no_durable_write_receipt: str
    generation_receipt: str
    subject_line: str = ""

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.whole_message_candidate.v1",
            "candidate_id": self.candidate_id,
            "subject_line": self.subject_line,
            "draft_text": self.draft_text,
            "attempt_seed": self.attempt_seed,
            "model_id": self.model_id,
            "provider_id": self.provider_id,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "char_count": self.char_count,
            "claims_used": list(self.claims_used),
            "is_whole_message": self.is_whole_message,
            "no_durable_write_receipt": self.no_durable_write_receipt,
            "generation_receipt": self.generation_receipt,
        }


@dataclass(frozen=True)
class WholeMessageCandidateBatch:
    status: str
    request_id: str
    prompt_contract_id: str
    candidates: tuple[WholeMessageCandidate, ...]
    blocking_reasons: tuple[str, ...]

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.whole_message_candidate_batch.v1",
            "status": self.status,
            "request_id": self.request_id,
            "prompt_contract_id": self.prompt_contract_id,
            "candidates": [candidate.to_packet() for candidate in self.candidates],
            "blocking_reasons": list(self.blocking_reasons),
        }


@dataclass(frozen=True)
class WholeMessageCandidateValidation:
    status: str
    candidate_id: str
    issues: tuple[str, ...]
    word_count: int
    sentence_count: int
    char_count: int

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.whole_message_candidate_validation.v1",
            "status": self.status,
            "candidate_id": self.candidate_id,
            "issues": list(self.issues),
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "char_count": self.char_count,
        }


def _sha256_canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _has_terminal_signature(text: str) -> bool:
    return _SIGNATURE_PATTERN.search(str(text or "")) is not None


def _has_low_friction_cta(text: str) -> bool:
    return "?" in str(text or "") or _CTA_PATTERN.search(str(text or "")) is not None


def _with_signature(text: str) -> str:
    return f"{_clean(text)}\n\nAmit"


def _short_trigger_signal(value: str, *, max_words: int = 10) -> str:
    first_clause = re.split(r"[.;]", _clean(value), maxsplit=1)[0].strip()
    words = re.findall(r"\b[\w'-]+\b", first_clause)
    if len(words) <= max_words:
        return first_clause
    return " ".join(words[:max_words])


def _first_name(name: str) -> str:
    cleaned = _clean(name)
    return cleaned.split()[0] if cleaned else "there"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _sentence_count(text: str) -> int:
    text = _SIGNATURE_PATTERN.sub("", str(text or "")).strip()
    return len([part for part in re.split(r"[.!?]+", text) if part.strip()])


def _is_exec_class(recipient_class: str) -> bool:
    return recipient_class in {
        CLASS_EXECUTIVE,
        CLASS_C_LEVEL,
        CLASS_CEO,
        CLASS_CTO,
        CLASS_VP_ENG,
    }


def _resolve_x1d_depth(sc_level: str, recipient_class: str, message_type: str) -> int:
    if recipient_class in {CLASS_CEO, CLASS_C_LEVEL}:
        return 2
    if message_type == MESSAGE_ROLE_SPECIFIC and recipient_class == CLASS_HIRING_MANAGER:
        return 2
    if message_type == MESSAGE_ROLE_SPECIFIC and _is_exec_class(recipient_class):
        return 2
    if sc_level == SC_3 and _is_exec_class(recipient_class):
        return 1
    if message_type == MESSAGE_REFERRAL_ASK:
        return 1
    if message_type == MESSAGE_ROLE_SPECIFIC and recipient_class != CLASS_RECRUITER:
        return 1
    if message_type == MESSAGE_ROLE_SPECIFIC and recipient_class == CLASS_RECRUITER:
        return 1
    return 0


def resolve_reasoning_policy(
    *,
    recipient_class: str,
    message_type: str,
    modifiers: Mapping[str, bool],
    send_mode: str = "draft_only",
) -> ReasoningPolicy:
    """Resolve W6 SC level, candidate count, repair budget, and temperatures."""
    reason_codes: list[str] = []
    sc_level = SC_1
    if message_type == MESSAGE_ROLE_SPECIFIC:
        sc_level = SC_2
        reason_codes.append("role_specific:SC-2")
    elif message_type == MESSAGE_TRIGGER_BASED_INSIGHT:
        sc_level = SC_3 if _is_exec_class(recipient_class) else SC_2
        reason_codes.append(f"trigger_based_insight:{sc_level}")
    elif message_type == MESSAGE_REFERRAL_ASK:
        sc_level = SC_3
        reason_codes.append("referral_ask:SC-3")
    elif message_type == MESSAGE_FOLLOW_UP:
        if _is_exec_class(recipient_class) or modifiers.get(MODIFIER_APPLICATION_STATUS_CLAIMED):
            sc_level = SC_3
            reason_codes.append("follow_up_sensitive_or_exec:SC-3")
        elif recipient_class in {CLASS_SENIOR_TA, CLASS_HIRING_MANAGER}:
            sc_level = SC_2
            reason_codes.append("follow_up_senior_or_hiring:SC-2")
        else:
            reason_codes.append("follow_up_low_claim:SC-1")
    elif message_type == MESSAGE_GENERAL_INTRO:
        if recipient_class in {CLASS_CEO, CLASS_C_LEVEL, CLASS_CTO, CLASS_VP_ENG}:
            sc_level = SC_3
            reason_codes.append("executive_general_intro:SC-3")
        elif recipient_class == CLASS_EXECUTIVE:
            sc_level = SC_2
            reason_codes.append("executive_general_intro:SC-2")
        else:
            reason_codes.append("general_intro_default:SC-1")

    if modifiers.get(MODIFIER_USES_SENSITIVE_CONSTRAINTS):
        sc_level = SC_3
        reason_codes.append("sensitive_constraints:SC-3")
    if modifiers.get(MODIFIER_USES_REFERRAL_CONTEXT):
        sc_level = SC_3
        reason_codes.append("referral_context:SC-3")
    if send_mode not in _ALLOWED_SEND_MODES:
        sc_level = SC_3
        reason_codes.append("forbidden_send_mode:SC-3")

    intensity, candidate_count, repair_budget, temperature, top_p = _SC_SETTINGS[sc_level]
    return ReasoningPolicy(
        sc_level=sc_level,
        reasoning_intensity=intensity,
        candidate_count=candidate_count,
        repair_budget=repair_budget,
        generator_temperature=temperature,
        top_p=top_p,
        repair_temperature=0.30,
        judge_temperature=0.10,
        x1d_llm_judge_depth=_resolve_x1d_depth(sc_level, recipient_class, message_type),
        reason_codes=tuple(dict.fromkeys(reason_codes)),
    )


def resolve_length_budget(
    *,
    recipient_class: str,
    message_type: str,
    modifiers: Mapping[str, bool],
    channel: str = "linkedin",
) -> LengthBudget:
    """Resolve LinkedIn/InMail length budget from the shared recipient template policy.

    Word bands are retained for reporting and prompt guidance only. Hard runtime
    controls are sentence count and character cap because tokenizer splits make
    word counts a weak proxy for model output length.
    """
    policy = resolve_recipient_template_policy(
        recipient_class=recipient_class,
        message_type=message_type,
        channel=channel,
        modifiers=modifiers,
    )
    packet = policy.length_policy.to_length_budget_packet()
    return LengthBudget(
        budget_key=str(packet["budget_key"]),
        min_words=int(packet["min_words"]),
        max_words=int(packet["max_words"]),
        min_sentences=int(packet["min_sentences"]),
        max_sentences=int(packet["max_sentences"]),
        hard_cap_chars=int(packet["hard_cap_chars"]),
        channel=str(packet["channel"]),
        route_family=str(packet["route_family"]),
        subject_required=bool(packet["subject_required"]),
        signature_required=bool(packet["signature_required"]),
        cta_style=str(packet["cta_style"]),
    )


def _docs_from_store(store: OpportunityFactStore) -> tuple[OpportunityFactDocument, ...]:
    documents: list[OpportunityFactDocument] = []
    for namespace in (
        NAMESPACE_CONTACT,
        NAMESPACE_COMPANY,
        NAMESPACE_JD,
        NAMESPACE_COMPANY_TRIGGER,
        NAMESPACE_ROLE_OWNERSHIP,
        NAMESPACE_RELATIONSHIP,
        NAMESPACE_REFERRAL,
        NAMESPACE_PRIOR_THREAD,
    ):
        documents.extend(store.query_namespace(namespace))
    return tuple(documents)


def _extract_context(
    documents: Iterable[OpportunityFactDocument],
) -> tuple[dict[str, str], dict[str, str], tuple[str, ...]]:
    target: dict[str, str] = {}
    jd_fields: dict[str, str] = {}
    source_snapshot_ids: list[str] = []
    for document in documents:
        source_snapshot_ids.append(document.source_snapshot_id)
        metadata = dict(document.metadata)
        if document.namespace == NAMESPACE_CONTACT:
            target.setdefault("name", _clean(metadata.get("name")))
            target.setdefault("title", _clean(metadata.get("title") or metadata.get("headline")))
            target.setdefault("company", _clean(metadata.get("company")))
        elif document.namespace == NAMESPACE_COMPANY:
            target.setdefault("company", _clean(metadata.get("company")))
            target.setdefault("company_context", _clean(document.fact_text))
        elif document.namespace == NAMESPACE_JD:
            for key in (
                "position_name",
                "job_title",
                "requisition_number",
                "company",
                "location",
                "role_family",
                "jd_digest",
            ):
                value = _clean(metadata.get(key))
                if value:
                    jd_fields.setdefault(key, value)
            if "company" in jd_fields:
                target.setdefault("company", jd_fields["company"])
        elif document.namespace == NAMESPACE_COMPANY_TRIGGER:
            target.setdefault("company_trigger", _clean(metadata.get("trigger_text") or document.fact_text))
        elif document.namespace == NAMESPACE_REFERRAL:
            target.setdefault("referrer_name", _clean(metadata.get("referrer_name")))
            target.setdefault("referral_permission", _clean(metadata.get("permission_scope")))
        elif document.namespace == NAMESPACE_RELATIONSHIP:
            target.setdefault("relationship_context", _clean(metadata.get("relationship_context")))
        elif document.namespace == NAMESPACE_PRIOR_THREAD:
            target.setdefault("prior_thread_summary", _clean(metadata.get("thread_summary")))
            target.setdefault("last_touch_date", _clean(metadata.get("last_touch_date")))
        elif document.namespace == NAMESPACE_ROLE_OWNERSHIP:
            target.setdefault("role_ownership_signal", _clean(metadata.get("ownership_signal") or document.fact_text))
    return target, jd_fields, tuple(dict.fromkeys(source_snapshot_ids))


def build_whole_message_generation_request(
    *,
    recipient_derivation: RecipientClassDerivation,
    message_gate_result: MessageRequirementGateResult,
    sender_proof_packet: SenderProofGraphPacket,
    opportunity_documents: Iterable[OpportunityFactDocument] = (),
    request_id: str = "",
    trace_root: str = "",
    channel: str = "linkedin",
    outreach_mode: str = "cold",
    send_mode: str = "draft_only",
    campaign_objective: str = "",
    desired_next_step: str = "",
) -> WholeMessageGenerationRequest:
    """Pack C0/W4/C0.3 into a PA/L2 whole-message generation request."""
    documents = tuple(opportunity_documents)
    target_context, jd_fields, source_snapshot_ids = _extract_context(documents)
    modifiers = dict(message_gate_result.modifiers)
    length_budget = resolve_length_budget(
        recipient_class=message_gate_result.recipient_class,
        message_type=message_gate_result.message_type,
        modifiers=modifiers,
        channel=channel,
    )
    reasoning_policy = resolve_reasoning_policy(
        recipient_class=message_gate_result.recipient_class,
        message_type=message_gate_result.message_type,
        modifiers=modifiers,
        send_mode=send_mode,
    )

    blocking: list[str] = []
    if recipient_derivation.status != RECIPIENT_STATUS_DERIVED:
        blocking.append(REASON_RECIPIENT_CLASS_NOT_DERIVED)
    if message_gate_result.status != STATUS_REQUIREMENTS_PASS:
        blocking.append(REASON_MESSAGE_REQUIREMENTS_NOT_PASSED)
    if sender_proof_packet.status != STATUS_PROOF_GRAPH_READY or not sender_proof_packet.ready:
        blocking.append(REASON_SENDER_PROOF_NOT_READY)
    if send_mode not in _ALLOWED_SEND_MODES:
        blocking.append(REASON_SEND_MODE_FORBIDDEN)

    component_hash_map = {
        "recipient_class_derivation": recipient_derivation.evidence_packet_id,
        "message_requirement_gate": _sha256_canonical(message_gate_result.to_packet()),
        "sender_proof_graph": sender_proof_packet.proof_packet_id,
        "length_budget": _sha256_canonical(length_budget.to_packet()),
        "reasoning_policy": _sha256_canonical(reasoning_policy.to_packet()),
        "source_snapshot_ids": _sha256_canonical(source_snapshot_ids),
    }
    prompt_seed = {
        "request_id": request_id,
        "trace_root": trace_root,
        "recipient_class": message_gate_result.recipient_class,
        "message_type": message_gate_result.message_type,
        "modifiers": modifiers,
        "campaign_objective": campaign_objective,
        "desired_next_step": desired_next_step,
        "target_context": target_context,
        "jd_fields": jd_fields,
        "proof_packet_id": sender_proof_packet.proof_packet_id,
        "allowed_claim_ids": sender_proof_packet.proof_ids,
        "length_budget": length_budget.to_packet(),
        "reasoning_policy": reasoning_policy.to_packet(),
        "component_hash_map": component_hash_map,
    }
    ready = not blocking
    return WholeMessageGenerationRequest(
        status=STATUS_GENERATION_REQUEST_READY if ready else STATUS_GENERATION_REQUEST_BLOCKED,
        ready=ready,
        request_id=request_id,
        trace_root=trace_root,
        channel=channel,
        outreach_mode=outreach_mode,
        send_mode=send_mode,
        recipient_class=message_gate_result.recipient_class,
        message_type=message_gate_result.message_type,
        modifiers=modifiers,
        campaign_objective=campaign_objective,
        desired_next_step=desired_next_step,
        target_context=target_context,
        jd_fields=jd_fields,
        proof_packet=sender_proof_packet,
        length_budget=length_budget,
        reasoning_policy=reasoning_policy,
        prompt_contract_id=_sha256_canonical(prompt_seed),
        component_hash_map=component_hash_map,
        blocking_reasons=tuple(dict.fromkeys(blocking)),
        no_send_receipt=NO_SEND_RECEIPT if send_mode in _ALLOWED_SEND_MODES else "",
        no_durable_write_receipt=NO_DURABLE_WRITE_RECEIPT,
        instruction_data_boundary_receipt=INSTRUCTION_DATA_BOUNDARY_RECEIPT,
    )


def build_whole_message_generation_request_from_store(
    *,
    store: OpportunityFactStore,
    recipient_derivation: RecipientClassDerivation,
    message_gate_result: MessageRequirementGateResult,
    sender_proof_packet: SenderProofGraphPacket,
    request_id: str = "",
    trace_root: str = "",
    channel: str = "linkedin",
    outreach_mode: str = "cold",
    send_mode: str = "draft_only",
    campaign_objective: str = "",
    desired_next_step: str = "",
) -> WholeMessageGenerationRequest:
    """Read W2 facts and build the W6 generation request."""
    return build_whole_message_generation_request(
        recipient_derivation=recipient_derivation,
        message_gate_result=message_gate_result,
        sender_proof_packet=sender_proof_packet,
        opportunity_documents=_docs_from_store(store),
        request_id=request_id,
        trace_root=trace_root,
        channel=channel,
        outreach_mode=outreach_mode,
        send_mode=send_mode,
        campaign_objective=campaign_objective,
        desired_next_step=desired_next_step,
    )


def _proof_claim_fragment(
    request: WholeMessageGenerationRequest,
    *,
    variant_index: int = 0,
) -> tuple[str, tuple[str, ...]]:
    points = request.proof_packet.selected_proof_points
    if not points:
        return "I work on governed AI platforms for regulated enterprise settings", ()
    point = points[variant_index % len(points)]
    claim = _clean(point.claim_text).rstrip(".")
    claim = re.sub(r"^(Designed|Strengthened|Productized|Architected|Brings)\b", lambda m: m.group(0).lower(), claim)
    return f"My background: {claim}", (point.proof_id,)


def _render_candidate_text(
    request: WholeMessageGenerationRequest,
    *,
    variant_index: int,
) -> tuple[str, tuple[str, ...]]:
    target = dict(request.target_context)
    jd = dict(request.jd_fields)
    first = _first_name(target.get("name", ""))
    company = _clean(target.get("company")) or "your team"
    objective = _clean(request.campaign_objective)
    next_step = _clean(request.desired_next_step) or "a quick conversation"
    proof_fragment, claims_used = _proof_claim_fragment(request, variant_index=variant_index)
    position = _clean(jd.get("position_name") or jd.get("job_title"))
    req = _clean(jd.get("requisition_number"))
    trigger = _clean(target.get("company_trigger"))
    referrer = _clean(target.get("referrer_name"))
    prior_thread = _clean(target.get("prior_thread_summary"))

    asks = (
        f"Would {next_step} be reasonable?",
        f"Open to {next_step} if the fit is worth a closer look?",
        f"Would it be useful to compare notes briefly?",
    )
    ask = asks[variant_index % len(asks)]

    if request.message_type == MESSAGE_ROLE_SPECIFIC:
        role_ref = position or "the open role"
        req_ref = f" ({req})" if req else ""
        return (
            _with_signature(
                f"Hi {first}, I noticed {company}'s {role_ref} role{req_ref}. "
                f"{proof_fragment}, which maps to the platform and governance work behind this kind of mandate. "
                f"{ask}"
            ),
            claims_used,
        )
    if request.message_type == MESSAGE_TRIGGER_BASED_INSIGHT:
        trigger_ref = _short_trigger_signal(trigger or f"{company}'s AI platform work").rstrip(".!?")
        return (
            _with_signature(
                f"Hi {first}, I noticed {trigger_ref}. "
                f"{proof_fragment}; the edge is making governance accelerate adoption. "
                f"{ask}"
            ),
            claims_used,
        )
    if request.message_type == MESSAGE_REFERRAL_ASK:
        bridge = f"{referrer} suggested I reach out" if referrer else "A warm intro brought you to mind"
        return (
            _with_signature(
                f"Hi {first}, {bridge}. "
                f"{proof_fragment}. "
                f"{ask}"
            ),
            claims_used,
        )
    if request.message_type == MESSAGE_FOLLOW_UP:
        thread_ref = prior_thread or "our earlier exchange"
        return (
            _with_signature(
                f"Hi {first}, following up on {thread_ref}. "
                f"{proof_fragment}. "
                f"{ask}"
            ),
            claims_used,
        )
    if objective:
        return (
            _with_signature(
                f"Hi {first}, I saw your work at {company} and wanted to connect around {objective}. "
                f"{proof_fragment}. "
                f"{ask}"
            ),
            claims_used,
        )
    return (
        _with_signature(
            f"Hi {first}, I saw your work at {company} and wanted to connect. "
            f"{proof_fragment}. "
            f"{ask}"
        ),
        claims_used,
    )


def _candidate_id(request: WholeMessageGenerationRequest, index: int, draft_text: str) -> str:
    return _sha256_canonical(
        {
            "prompt_contract_id": request.prompt_contract_id,
            "index": index,
            "draft_text": draft_text,
        }
    )


def _subject_for_request(request: WholeMessageGenerationRequest) -> str:
    if str(request.channel or "").strip().lower() != CHANNEL_LINKEDIN_INMAIL:
        return ""
    company = _clean(request.target_context.get("company")) or "AI platform work"
    position = _clean(
        request.jd_fields.get("position_name") or request.jd_fields.get("job_title")
    )
    if position:
        return _clean(f"{position} fit at {company}")[:200]
    if request.message_type == MESSAGE_TRIGGER_BASED_INSIGHT:
        return _clean(f"{company} AI execution note")[:200]
    return _clean(f"{company} AI leadership fit")[:200]


def generate_whole_message_candidates(
    request: WholeMessageGenerationRequest,
) -> WholeMessageCandidateBatch:
    """Generate provider-free whole-message candidate artifacts for W6 tests."""
    if not request.ready:
        return WholeMessageCandidateBatch(
            status=STATUS_CANDIDATES_BLOCKED,
            request_id=request.request_id,
            prompt_contract_id=request.prompt_contract_id,
            candidates=(),
            blocking_reasons=request.blocking_reasons,
        )

    candidates: list[WholeMessageCandidate] = []
    for index in range(request.reasoning_policy.candidate_count):
        draft_text, claims_used = _render_candidate_text(request, variant_index=index)
        subject_line = _subject_for_request(request)
        candidate_id = _candidate_id(request, index, draft_text)
        candidates.append(
            WholeMessageCandidate(
                candidate_id=candidate_id,
                subject_line=subject_line,
                draft_text=draft_text,
                attempt_seed=_sha256_canonical(
                    {
                        "prompt_contract_id": request.prompt_contract_id,
                        "candidate_index": index,
                    }
                ),
                model_id=GENERATOR_MODEL_ID,
                provider_id=GENERATOR_PROVIDER_ID,
                temperature=request.reasoning_policy.generator_temperature,
                top_p=request.reasoning_policy.top_p,
                word_count=_word_count(draft_text),
                sentence_count=_sentence_count(draft_text),
                char_count=len(draft_text),
                claims_used=claims_used,
                is_whole_message=True,
                no_durable_write_receipt=NO_DURABLE_WRITE_RECEIPT,
                generation_receipt="pass:w6_provider_free_candidate_scaffold",
            )
        )
    return WholeMessageCandidateBatch(
        status=STATUS_CANDIDATES_READY,
        request_id=request.request_id,
        prompt_contract_id=request.prompt_contract_id,
        candidates=tuple(candidates),
        blocking_reasons=(),
    )


def validate_whole_message_candidate(
    candidate: WholeMessageCandidate,
    *,
    request: WholeMessageGenerationRequest,
) -> WholeMessageCandidateValidation:
    """Validate W6 whole-message shape and proof-ID containment."""
    issues: list[str] = []
    lowered = candidate.draft_text.lower()
    if not candidate.is_whole_message or any(marker in lowered for marker in _FORBIDDEN_FRAGMENT_MARKERS):
        issues.append(REASON_CANDIDATE_NOT_WHOLE_MESSAGE)
    if str(request.channel or "").strip().lower() == CHANNEL_LINKEDIN_INMAIL:
        subject = _clean(candidate.subject_line)
        if not subject:
            issues.append(REASON_CANDIDATE_MISSING_SUBJECT)
        elif len(subject) > 200:
            issues.append(REASON_CANDIDATE_SUBJECT_TOO_LONG)
    if candidate.char_count > request.length_budget.hard_cap_chars:
        issues.append(REASON_CANDIDATE_OVER_LENGTH)
    if not _has_low_friction_cta(candidate.draft_text):
        issues.append(REASON_CANDIDATE_MISSING_CTA)
    if not _has_terminal_signature(candidate.draft_text):
        issues.append(REASON_CANDIDATE_MISSING_SIGNATURE)
    claim_validation = validate_l2_sender_claims_against_packet(
        candidate.claims_used,
        packet=request.proof_packet,
    )
    if claim_validation.status != "SENDER_PROOF_CLAIMS_PASS":
        issues.append(REASON_CANDIDATE_UNAPPROVED_CLAIM)
    return WholeMessageCandidateValidation(
        status=STATUS_CANDIDATE_SHAPE_BLOCKED if issues else STATUS_CANDIDATE_SHAPE_PASS,
        candidate_id=candidate.candidate_id,
        issues=tuple(issues),
        word_count=candidate.word_count,
        sentence_count=candidate.sentence_count,
        char_count=candidate.char_count,
    )


__all__ = [
    "GENERATOR_MODEL_ID",
    "GENERATOR_PROVIDER_ID",
    "INSTRUCTION_DATA_BOUNDARY_RECEIPT",
    "NO_DURABLE_WRITE_RECEIPT",
    "NO_SEND_RECEIPT",
    "R0_MINIMAL",
    "R1_STANDARD",
    "R2_DELIBERATE",
    "R3_STRICT",
    "REASON_CANDIDATE_NOT_WHOLE_MESSAGE",
    "REASON_CANDIDATE_MISSING_CTA",
    "REASON_CANDIDATE_MISSING_SIGNATURE",
    "REASON_CANDIDATE_MISSING_SUBJECT",
    "REASON_CANDIDATE_OVER_LENGTH",
    "REASON_CANDIDATE_SUBJECT_TOO_LONG",
    "REASON_CANDIDATE_UNAPPROVED_CLAIM",
    "REASON_MESSAGE_REQUIREMENTS_NOT_PASSED",
    "REASON_RECIPIENT_CLASS_NOT_DERIVED",
    "REASON_SEND_MODE_FORBIDDEN",
    "REASON_SENDER_PROOF_NOT_READY",
    "SC_0",
    "SC_1",
    "SC_2",
    "SC_3",
    "STATUS_CANDIDATES_BLOCKED",
    "STATUS_CANDIDATES_READY",
    "STATUS_CANDIDATE_SHAPE_BLOCKED",
    "STATUS_CANDIDATE_SHAPE_PASS",
    "STATUS_GENERATION_REQUEST_BLOCKED",
    "STATUS_GENERATION_REQUEST_READY",
    "LengthBudget",
    "ReasoningPolicy",
    "WholeMessageCandidate",
    "WholeMessageCandidateBatch",
    "WholeMessageCandidateValidation",
    "WholeMessageGenerationRequest",
    "build_whole_message_generation_request",
    "build_whole_message_generation_request_from_store",
    "generate_whole_message_candidates",
    "resolve_length_budget",
    "resolve_reasoning_policy",
    "validate_whole_message_candidate",
]
