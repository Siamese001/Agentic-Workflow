"""X2/X1D validation and Exit clearance for apps_lic W7.

This module is provider-free and read-only. It enforces deterministic X2 gates,
accepts already-produced X1D judge results as data, and emits the final Exit
proof bundle. It never calls a model provider and never sends a message.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, replace
from typing import Any, Callable, Iterable, Mapping

from apps_lic.engines.message_type_requirement_gate import (
    MESSAGE_FOLLOW_UP,
    MESSAGE_REFERRAL_ASK,
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
    MODIFIER_APPLICATION_STATUS_CLAIMED,
    MODIFIER_USES_COMPANY_TRIGGER,
    MODIFIER_USES_JD,
    MODIFIER_USES_PRIOR_THREAD,
    MODIFIER_USES_REFERRAL_CONTEXT,
)
from apps_lic.engines.recipient_classification import (
    CLASS_CEO,
    CLASS_CTO,
    CLASS_C_LEVEL,
    CLASS_EXECUTIVE,
    CLASS_HIRING_MANAGER,
    CLASS_RECRUITER,
    CLASS_SENIOR_TA,
    CLASS_UNKNOWN,
    CLASS_VP_ENG,
)
from apps_lic.engines.sender_proof_graph import (
    STATUS_CLAIMS_PASS,
    validate_draft_metrics_against_packet,
    validate_l2_sender_claims_against_packet,
)
from apps_lic.engines.whole_message_generation import (
    GENERATOR_MODEL_ID,
    GENERATOR_PROVIDER_ID,
    NO_SEND_RECEIPT,
    SC_2,
    SC_3,
    STATUS_CANDIDATES_READY,
    STATUS_CANDIDATE_SHAPE_PASS,
    STATUS_GENERATION_REQUEST_READY,
    WholeMessageCandidate,
    WholeMessageCandidateBatch,
    WholeMessageGenerationRequest,
    validate_whole_message_candidate,
)
from apps_lic.engines.x1d_judge_policy import (
    ANTHROPIC_MESSAGES_API,
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    INDEPENDENT_JUDGE,
    JUDGE_AVAILABLE,
    JUDGE_CEO_EVIDENCE_RISK,
    JUDGE_CEO_ORIGINALITY,
    JUDGE_EVIDENCE_SUPPORT,
    JUDGE_LINKEDIN_TONE,
    JUDGE_LINKEDIN_TONE_NON_GENERIC,
    JUDGE_UNAVAILABLE,
    LIVE_CLAUDE_API_CALL,
    MODIFIER_PROVIDER_BACKED_GENERATION,
    MODIFIER_SIMILARITY_GATE_FLAGGED,
    NON_INDEPENDENT_JUDGE,
    X1DJudgeProfilePolicy,
    required_x1d_judge_ids_for_context,
    x1d_judge_profile_policy,
)


STATUS_X2_PASS = "X2_VALIDATION_PASS"
STATUS_X2_BLOCKED = "X2_VALIDATION_BLOCKED"
STATUS_X1D_NOT_REQUIRED = "X1D_NOT_REQUIRED"
STATUS_X1D_PASS = "X1D_VALIDATION_PASS"
STATUS_X1D_REVIEW_REQUIRED = "X1D_REVIEW_REQUIRED"
STATUS_X1D_BLOCKED = "X1D_BLOCKED"
STATUS_EXIT_CLEAR_DRAFT = "EXIT_CLEAR_DRAFT"
STATUS_EXIT_REVIEW_REQUIRED = "EXIT_REVIEW_REQUIRED"
STATUS_EXIT_BLOCKED = "EXIT_BLOCKED"
STATUS_EXIT_ABSTAIN = "EXIT_ABSTAIN"

EXIT_CLEAR_DRAFT = "clear_draft"
EXIT_REVIEW_REQUIRED = "review_required"
EXIT_BLOCKED = "blocked"
EXIT_ABSTAIN = "abstain"

GATE_PASS = "pass"
GATE_FAIL = "fail"
GATE_NOT_APPLICABLE = "not_applicable"
SEVERITY_BLOCK = "block"
SEVERITY_REVIEW = "review"

GATE_SCHEMA = "schema_gate"
GATE_NO_SEND = "no_send_gate"
GATE_RECIPIENT_CLASS = "recipient_class_present_and_derived_gate"
GATE_PROMPT_INJECTION = "prompt_injection_neutralization_gate"
GATE_WHOLE_MESSAGE_SHAPE = "whole_message_shape_gate"
GATE_INMAIL_SUBJECT = "inmail_subject_line_gate"
GATE_CHANNEL_LENGTH = "message_type_recipient_length_gate"
GATE_UNSUPPORTED_CLAIM = "unsupported_claim_gate"
GATE_GENERATED_METRIC_GROUNDED = "generated_metric_graph_grounded_gate"
GATE_CANDIDATE_SELECTION = "candidate_selection_gate"
GATE_JD_REQUIRED = "jd_required_gate"
GATE_POSITION_NAME = "position_name_required_gate"
GATE_REQUISITION_NUMBER = "requisition_number_required_gate"
GATE_APPLICATION_STATUS = "application_status_gate"
GATE_REFERRAL_CONTEXT = "referral_context_gate"
GATE_RELATIONSHIP_EVIDENCE = "relationship_evidence_gate"
GATE_PRIOR_THREAD = "prior_thread_gate"
GATE_COMPANY_TRIGGER = "company_trigger_gate"
GATE_ROLE_OWNERSHIP_FIT = "role_ownership_fit_gate"

X1D_DEPTH_NONE = "none"
X1D_DEPTH_ONE = "one"
X1D_DEPTH_TWO = "two"

_X2_UNIVERSAL_GATES = (
    GATE_SCHEMA,
    GATE_NO_SEND,
    GATE_RECIPIENT_CLASS,
    GATE_PROMPT_INJECTION,
    GATE_WHOLE_MESSAGE_SHAPE,
    GATE_INMAIL_SUBJECT,
    GATE_CHANNEL_LENGTH,
    GATE_UNSUPPORTED_CLAIM,
)

_PROMPT_INJECTION_PATTERNS = (
    r"\bignore (all )?(previous|prior) instructions\b",
    r"\bsystem prompt\b",
    r"\bdeveloper message\b",
    r"\breveal (the )?(prompt|instructions)\b",
    r"\bjailbreak\b",
)

_US_JD_LOCATION_HINTS = (
    "new york",
    "ny-new york",
    "charlotte",
    "nc-charlotte",
    "atlanta",
    "ga-atlanta",
)
_NON_US_OWNERSHIP_HINTS = (
    "aig japan",
    "japan",
    "tokyo",
)
@dataclass(frozen=True)
class X2GateResult:
    gate_id: str
    status: str
    severity: str
    reason: str
    evidence_refs: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.status in {GATE_PASS, GATE_NOT_APPLICABLE}

    def to_packet(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "severity": self.severity,
            "reason": self.reason,
            "evidence_refs": list(self.evidence_refs),
            "clearance": "pass" if self.passed else "fail",
        }


@dataclass(frozen=True)
class X2ValidationResult:
    status: str
    passed: bool
    gate_results: tuple[X2GateResult, ...]
    failed_gate_ids: tuple[str, ...]
    selected_candidate_id: str
    reason_codes: tuple[str, ...]

    def gate(self, gate_id: str) -> X2GateResult:
        for gate_result in self.gate_results:
            if gate_result.gate_id == gate_id:
                return gate_result
        raise KeyError(gate_id)

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.x2_validation_result.v1",
            "status": self.status,
            "passed": self.passed,
            "selected_candidate_id": self.selected_candidate_id,
            "failed_gate_ids": list(self.failed_gate_ids),
            "reason_codes": list(self.reason_codes),
            "gate_results": [gate_result.to_packet() for gate_result in self.gate_results],
        }


@dataclass(frozen=True)
class X1DJudgeProfile:
    judge_id: str
    rubric_id: str
    model: str
    provider: str
    threshold: float
    role: str
    required_for_depth: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "judge_id": self.judge_id,
            "rubric_id": self.rubric_id,
            "model": self.model,
            "provider": self.provider,
            "threshold": self.threshold,
            "role": self.role,
            "required_for_depth": self.required_for_depth,
        }


@dataclass(frozen=True)
class X1DJudgeResult:
    judge_id: str
    model: str = DEFAULT_X1D_JUDGE_MODEL
    provider: str = DEFAULT_X1D_JUDGE_PROVIDER
    score: float = 0.0
    threshold: float = 0.0
    passed: bool = False
    availability_status: str = JUDGE_AVAILABLE
    independence_status: str = ""
    transport_provenance: str = ""
    transport_provider: str = ""
    transport_call_id: str = ""
    raw_response_digest: str = ""
    issues: tuple[str, ...] = ()
    required_repairs: tuple[str, ...] = ()

    def to_packet(self) -> dict[str, Any]:
        return {
            "judge_id": self.judge_id,
            "model": self.model,
            "provider": self.provider,
            "score": self.score,
            "threshold": self.threshold,
            "passed": self.passed,
            "availability_status": self.availability_status,
            "independence_status": self.independence_status,
            "transport_provenance": self.transport_provenance,
            "transport_provider": self.transport_provider,
            "transport_call_id": self.transport_call_id,
            "raw_response_digest": self.raw_response_digest,
            "issues": list(self.issues),
            "required_repairs": list(self.required_repairs),
            "clearance": "pass" if self.passed else "fail",
        }


@dataclass(frozen=True)
class X1DValidationResult:
    status: str
    passed: bool
    required_depth: str
    required_profiles: tuple[X1DJudgeProfile, ...]
    judge_results: tuple[X1DJudgeResult, ...]
    missing_judge_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.x1d_validation_result.v1",
            "status": self.status,
            "passed": self.passed,
            "required_depth": self.required_depth,
            "required_profiles": [profile.to_packet() for profile in self.required_profiles],
            "required_judge_ids": [profile.judge_id for profile in self.required_profiles],
            "judge_results": [result.to_packet() for result in self.judge_results],
            "missing_judge_ids": list(self.missing_judge_ids),
            "reason_codes": list(self.reason_codes),
            "clearance": "pass" if self.passed else "fail",
        }


@dataclass(frozen=True)
class ExitProofBundle:
    status: str
    disposition: str
    request_id: str
    trace_root: str
    candidate_id: str
    final_user_visible_draft_id: str
    review_required_reason: str
    exit_reason: str
    no_send_receipt: str
    proof_packet_id: str
    prompt_contract_id: str
    generator_model_id: str
    generator_provider_id: str
    x2_result: X2ValidationResult
    x1d_result: X1DValidationResult

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.exit_proof_bundle.v1",
            "status": self.status,
            "disposition": self.disposition,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "candidate_id": self.candidate_id,
            "final_user_visible_draft_id": self.final_user_visible_draft_id,
            "review_required_reason": self.review_required_reason,
            "exit_reason": self.exit_reason,
            "no_send_receipt": self.no_send_receipt,
            "proof_packet_id": self.proof_packet_id,
            "prompt_contract_id": self.prompt_contract_id,
            "generator_model_id": self.generator_model_id,
            "generator_provider_id": self.generator_provider_id,
            "x2": self.x2_result.to_packet(),
            "x1d": self.x1d_result.to_packet(),
            "clearance": self.disposition,
        }


def _sha256_canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _depth_label(depth: int) -> str:
    if depth <= 0:
        return X1D_DEPTH_NONE
    if depth == 1:
        return X1D_DEPTH_ONE
    return X1D_DEPTH_TWO


def _has_text(mapping: Mapping[str, Any], *keys: str) -> bool:
    return any(_clean(mapping.get(key)) for key in keys)


def _needs_jd(request: WholeMessageGenerationRequest) -> bool:
    return request.message_type == MESSAGE_ROLE_SPECIFIC or bool(
        request.modifiers.get(MODIFIER_USES_JD)
    )


def _needs_requisition_number(request: WholeMessageGenerationRequest) -> bool:
    return request.recipient_class in {CLASS_RECRUITER, CLASS_SENIOR_TA} and _needs_jd(request)


def _role_ownership_fit_passes(request: WholeMessageGenerationRequest) -> tuple[bool, str]:
    if request.message_type != MESSAGE_ROLE_SPECIFIC:
        return True, "not_role_specific"
    if request.recipient_class not in {CLASS_RECRUITER, CLASS_SENIOR_TA}:
        return True, "recipient_class_does_not_require_recruiting_ownership_fit"
    ownership_text = _clean(
        " ".join(
            (
                request.target_context.get("role_ownership_signal", ""),
                request.target_context.get("title", ""),
            )
        )
    ).lower()
    if not ownership_text:
        return True, "no_specific_role_ownership_signal"
    jd_text = _clean(" ".join(str(value) for value in request.jd_fields.values())).lower()
    non_us_signal = any(hint in ownership_text for hint in _NON_US_OWNERSHIP_HINTS)
    us_jd_signal = any(hint in jd_text for hint in _US_JD_LOCATION_HINTS)
    if non_us_signal and us_jd_signal:
        return False, "role_ownership_region_mismatch"
    return True, "role_ownership_fit_not_contradicted"


def _has_prompt_injection_text(*values: Any) -> bool:
    text = " ".join(_clean(value).lower() for value in values if _clean(value))
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in _PROMPT_INJECTION_PATTERNS)


def _gate(
    gate_id: str,
    passed: bool,
    reason: str,
    *,
    evidence_refs: Iterable[str] = (),
    severity: str = SEVERITY_BLOCK,
    applicable: bool = True,
) -> X2GateResult:
    if not applicable:
        status = GATE_NOT_APPLICABLE
    else:
        status = GATE_PASS if passed else GATE_FAIL
    return X2GateResult(
        gate_id=gate_id,
        status=status,
        severity=severity,
        reason=reason,
        evidence_refs=tuple(dict.fromkeys(_clean(ref) for ref in evidence_refs if _clean(ref))),
    )


def _candidate_by_id(
    batch: WholeMessageCandidateBatch,
    candidate_id: str,
) -> WholeMessageCandidate | None:
    for candidate in batch.candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    return None


def _select_candidate(
    request: WholeMessageGenerationRequest,
    batch: WholeMessageCandidateBatch,
    selected_candidate_id: str,
) -> tuple[WholeMessageCandidate | None, str]:
    candidates = tuple(batch.candidates)
    if selected_candidate_id:
        candidate = _candidate_by_id(batch, selected_candidate_id)
        if candidate is None:
            return None, "selected_candidate_id_not_in_batch"
        return candidate, "selected_candidate_id_present"
    if request.reasoning_policy.sc_level in {SC_2, SC_3}:
        return None, "missing_candidate_selection_for_multi_candidate_path"
    if len(candidates) == 1:
        return candidates[0], "auto_selected_single_candidate"
    if candidates:
        return candidates[0], "auto_selected_first_candidate"
    return None, "candidate_batch_empty"


def _length_gate_passes(
    candidate: WholeMessageCandidate,
    request: WholeMessageGenerationRequest,
) -> tuple[bool, str]:
    budget = request.length_budget
    if candidate.char_count > budget.hard_cap_chars:
        return False, "candidate_exceeds_hard_char_cap"
    if candidate.sentence_count > budget.max_sentences:
        return False, "candidate_exceeds_message_type_sentence_budget"
    if candidate.word_count < budget.min_words or candidate.sentence_count < budget.min_sentences:
        return True, "candidate_below_recommended_minimum_but_within_hard_bounds"
    if candidate.word_count > budget.max_words:
        return True, "candidate_above_recommended_word_band_but_within_hard_bounds"
    return True, "candidate_within_message_type_recipient_length_budget"


def _inmail_subject_gate_passes(
    candidate: WholeMessageCandidate | None,
    request: WholeMessageGenerationRequest,
) -> tuple[bool, str, bool]:
    applicable = str(request.channel or "").strip().lower() == "linkedin_inmail"
    if not applicable:
        return True, "subject_line_not_required_for_route", False
    if candidate is None:
        return False, "selected_candidate_missing", True
    subject = _clean(getattr(candidate, "subject_line", ""))
    if not subject:
        return False, "inmail_subject_line_missing", True
    if len(subject) > 200:
        return False, "inmail_subject_line_over_200_chars", True
    return True, "inmail_subject_line_present", True


def _schema_gate_passes(
    request: WholeMessageGenerationRequest,
    batch: WholeMessageCandidateBatch,
) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []
    if request.status != STATUS_GENERATION_REQUEST_READY or not request.ready:
        issues.append("generation_request_not_ready")
    if batch.status != STATUS_CANDIDATES_READY:
        issues.append("candidate_batch_not_ready")
    if batch.request_id != request.request_id:
        issues.append("candidate_batch_request_mismatch")
    if batch.prompt_contract_id != request.prompt_contract_id:
        issues.append("candidate_batch_prompt_contract_mismatch")
    if not request.prompt_contract_id.startswith("sha256:"):
        issues.append("prompt_contract_id_not_hashed")
    if not batch.candidates:
        issues.append("candidate_batch_empty")
    return not issues, tuple(issues)


def run_x2_validation(
    request: WholeMessageGenerationRequest,
    batch: WholeMessageCandidateBatch,
    *,
    selected_candidate_id: str = "",
    application_status: str = "",
) -> X2ValidationResult:
    """Run deterministic X2 gates for the selected apps_lic candidate."""
    gate_results: list[X2GateResult] = []
    source_refs = (
        request.prompt_contract_id,
        request.proof_packet.proof_packet_id,
        request.component_hash_map.get("message_requirement_gate", ""),
        request.component_hash_map.get("sender_proof_graph", ""),
    )
    schema_ok, schema_issues = _schema_gate_passes(request, batch)
    gate_results.append(
        _gate(
            GATE_SCHEMA,
            schema_ok,
            "schema_contract_ready" if schema_ok else ",".join(schema_issues),
            evidence_refs=source_refs,
        )
    )

    no_send_ok = request.send_mode in {"draft_only", "review_required"} and request.no_send_receipt == NO_SEND_RECEIPT
    gate_results.append(
        _gate(
            GATE_NO_SEND,
            no_send_ok,
            "draft_only_no_auto_send" if no_send_ok else "no_send_receipt_or_send_mode_invalid",
            evidence_refs=(request.no_send_receipt, request.send_mode),
        )
    )

    recipient_ok = (
        bool(_clean(request.recipient_class))
        and request.recipient_class != CLASS_UNKNOWN
        and request.proof_packet.recipient_class == request.recipient_class
    )
    gate_results.append(
        _gate(
            GATE_RECIPIENT_CLASS,
            recipient_ok,
            "recipient_class_present_and_matches_proof_packet"
            if recipient_ok
            else "recipient_class_missing_unknown_or_mismatched",
            evidence_refs=(request.recipient_class, request.proof_packet.recipient_class),
        )
    )

    selected_candidate, selection_reason = _select_candidate(request, batch, _clean(selected_candidate_id))
    selection_applicable = request.reasoning_policy.sc_level in {SC_2, SC_3}
    selection_ok = selected_candidate is not None and (
        not selection_applicable or selection_reason == "selected_candidate_id_present"
    )
    gate_results.append(
        _gate(
            GATE_CANDIDATE_SELECTION,
            selection_ok,
            selection_reason,
            evidence_refs=(selected_candidate.candidate_id if selected_candidate else "", request.reasoning_policy.sc_level),
            applicable=selection_applicable,
        )
    )

    context_values = (
        *request.target_context.values(),
        *request.jd_fields.values(),
        selected_candidate.draft_text if selected_candidate else "",
    )
    injection_ok = not _has_prompt_injection_text(*context_values)
    gate_results.append(
        _gate(
            GATE_PROMPT_INJECTION,
            injection_ok,
            "prompt_injection_patterns_absent" if injection_ok else "prompt_injection_pattern_detected",
            evidence_refs=(request.prompt_contract_id,),
        )
    )

    if selected_candidate is None:
        shape_ok = False
        shape_reason = "selected_candidate_missing"
        length_ok = False
        length_reason = "selected_candidate_missing"
        claims_ok = False
        claims_reason = "selected_candidate_missing"
        selected_id = ""
        draft_metric_result = None
    else:
        selected_id = selected_candidate.candidate_id
        shape_validation = validate_whole_message_candidate(selected_candidate, request=request)
        shape_ok = shape_validation.status == STATUS_CANDIDATE_SHAPE_PASS
        shape_reason = "whole_message_shape_pass" if shape_ok else ",".join(shape_validation.issues)
        length_ok, length_reason = _length_gate_passes(selected_candidate, request)
        claim_validation = validate_l2_sender_claims_against_packet(
            selected_candidate.claims_used,
            packet=request.proof_packet,
        )
        claims_ok = claim_validation.status == STATUS_CLAIMS_PASS
        claims_reason = "claims_within_c03_packet" if claims_ok else "unsupported_claim_ids_present"
        draft_metric_result = validate_draft_metrics_against_packet(
            selected_candidate.draft_text,
            packet=request.proof_packet,
        )

    gate_results.append(
        _gate(
            GATE_WHOLE_MESSAGE_SHAPE,
            shape_ok,
            shape_reason,
            evidence_refs=(selected_id,),
        )
    )
    subject_ok, subject_reason, subject_applicable = _inmail_subject_gate_passes(
        selected_candidate,
        request,
    )
    gate_results.append(
        _gate(
            GATE_INMAIL_SUBJECT,
            subject_ok,
            subject_reason,
            evidence_refs=(selected_id, getattr(selected_candidate, "subject_line", "") if selected_candidate else ""),
            applicable=subject_applicable,
        )
    )
    gate_results.append(
        _gate(
            GATE_CHANNEL_LENGTH,
            length_ok,
            length_reason,
            evidence_refs=(selected_id, request.length_budget.budget_key),
        )
    )
    gate_results.append(
        _gate(
            GATE_UNSUPPORTED_CLAIM,
            claims_ok,
            claims_reason,
            evidence_refs=(selected_id, request.proof_packet.proof_packet_id),
        )
    )

    draft_metric_grounded = bool(draft_metric_result and draft_metric_result.grounded)
    draft_metric_applicable = bool(draft_metric_result and draft_metric_result.applicable)
    ungrounded_metric_tokens = (
        draft_metric_result.ungrounded_metric_tokens if draft_metric_result else ()
    )
    gate_results.append(
        _gate(
            GATE_GENERATED_METRIC_GROUNDED,
            draft_metric_grounded,
            "draft_metrics_graph_grounded"
            if draft_metric_grounded
            else "draft_carries_ungrounded_metric:" + ",".join(ungrounded_metric_tokens),
            evidence_refs=(
                selected_id,
                request.proof_packet.proof_packet_id,
                *ungrounded_metric_tokens,
            ),
            applicable=draft_metric_applicable,
        )
    )

    jd_needed = _needs_jd(request)
    gate_results.append(
        _gate(
            GATE_JD_REQUIRED,
            bool(request.jd_fields),
            "jd_fields_present" if request.jd_fields else "jd_fields_missing",
            evidence_refs=(request.component_hash_map.get("source_snapshot_ids", ""),),
            applicable=jd_needed,
        )
    )
    gate_results.append(
        _gate(
            GATE_POSITION_NAME,
            _has_text(request.jd_fields, "position_name", "job_title"),
            "position_name_present" if _has_text(request.jd_fields, "position_name", "job_title") else "position_name_missing",
            evidence_refs=(request.jd_fields.get("position_name", ""), request.jd_fields.get("job_title", "")),
            applicable=jd_needed,
        )
    )
    gate_results.append(
        _gate(
            GATE_REQUISITION_NUMBER,
            _has_text(request.jd_fields, "requisition_number"),
            "requisition_number_present" if _has_text(request.jd_fields, "requisition_number") else "requisition_number_missing",
            evidence_refs=(request.jd_fields.get("requisition_number", ""),),
            applicable=_needs_requisition_number(request),
        )
    )

    app_status_needed = bool(request.modifiers.get(MODIFIER_APPLICATION_STATUS_CLAIMED))
    app_status_ok = _clean(application_status) or _has_text(request.target_context, "application_status", "candidate_status")
    gate_results.append(
        _gate(
            GATE_APPLICATION_STATUS,
            bool(app_status_ok),
            "application_status_present" if app_status_ok else "application_status_missing",
            evidence_refs=(application_status, request.target_context.get("application_status", "")),
            applicable=app_status_needed,
        )
    )

    referral_needed = request.message_type == MESSAGE_REFERRAL_ASK or bool(
        request.modifiers.get(MODIFIER_USES_REFERRAL_CONTEXT)
    )
    gate_results.append(
        _gate(
            GATE_REFERRAL_CONTEXT,
            _has_text(request.target_context, "referrer_name", "referral_permission"),
            "referral_context_present" if _has_text(request.target_context, "referrer_name", "referral_permission") else "referral_context_missing",
            evidence_refs=(request.target_context.get("referrer_name", ""), request.target_context.get("referral_permission", "")),
            applicable=referral_needed,
        )
    )
    gate_results.append(
        _gate(
            GATE_RELATIONSHIP_EVIDENCE,
            _has_text(request.target_context, "relationship_context"),
            "relationship_evidence_present" if _has_text(request.target_context, "relationship_context") else "relationship_evidence_missing",
            evidence_refs=(request.target_context.get("relationship_context", ""),),
            applicable=referral_needed,
        )
    )

    prior_needed = request.message_type == MESSAGE_FOLLOW_UP or bool(
        request.modifiers.get(MODIFIER_USES_PRIOR_THREAD)
    )
    gate_results.append(
        _gate(
            GATE_PRIOR_THREAD,
            _has_text(request.target_context, "prior_thread_summary"),
            "prior_thread_present" if _has_text(request.target_context, "prior_thread_summary") else "prior_thread_missing",
            evidence_refs=(request.target_context.get("prior_thread_summary", ""),),
            applicable=prior_needed,
        )
    )

    trigger_needed = request.message_type == MESSAGE_TRIGGER_BASED_INSIGHT or bool(
        request.modifiers.get(MODIFIER_USES_COMPANY_TRIGGER)
    )
    gate_results.append(
        _gate(
            GATE_COMPANY_TRIGGER,
            _has_text(request.target_context, "company_trigger"),
            "company_trigger_present" if _has_text(request.target_context, "company_trigger") else "company_trigger_missing",
            evidence_refs=(request.target_context.get("company_trigger", ""),),
            applicable=trigger_needed,
        )
    )

    role_fit_ok, role_fit_reason = _role_ownership_fit_passes(request)
    gate_results.append(
        _gate(
            GATE_ROLE_OWNERSHIP_FIT,
            role_fit_ok,
            role_fit_reason,
            evidence_refs=(
                request.target_context.get("role_ownership_signal", ""),
                request.jd_fields.get("location", ""),
            ),
            applicable=request.message_type == MESSAGE_ROLE_SPECIFIC
            and request.recipient_class in {CLASS_RECRUITER, CLASS_SENIOR_TA},
        )
    )

    failed = tuple(
        result.gate_id
        for result in gate_results
        if result.status == GATE_FAIL and result.severity == SEVERITY_BLOCK
    )
    reason_codes = tuple(
        dict.fromkeys(
            f"{result.gate_id}:{result.reason}"
            for result in gate_results
            if result.status == GATE_FAIL
        )
    )
    passed = not failed
    return X2ValidationResult(
        status=STATUS_X2_PASS if passed else STATUS_X2_BLOCKED,
        passed=passed,
        gate_results=tuple(gate_results),
        failed_gate_ids=failed,
        selected_candidate_id=selected_id if passed else selected_id,
        reason_codes=reason_codes,
    )


def _judge_profile_for_id(judge_id: str, *, required_for_depth: str) -> X1DJudgeProfile:
    policy = x1d_judge_profile_policy().get(judge_id)
    if policy is None:
        raise ValueError(f"Unsupported X1D judge profile id: {judge_id!r}")
    return X1DJudgeProfile(
        judge_id=policy.judge_id,
        rubric_id=policy.rubric_id,
        model=DEFAULT_X1D_JUDGE_MODEL,
        provider=DEFAULT_X1D_JUDGE_PROVIDER,
        threshold=policy.threshold,
        role=policy.role,
        required_for_depth=required_for_depth,
    )


def required_x1d_profiles(request: WholeMessageGenerationRequest) -> tuple[X1DJudgeProfile, ...]:
    """Resolve required X1D profiles from the W6 recipient/message risk matrix."""
    modifier_map = dict(request.modifiers)
    modifier_map["x1d_llm_judge_depth"] = request.reasoning_policy.x1d_llm_judge_depth
    proof_packet = getattr(request, "proof_packet", None)
    judge_ids = required_x1d_judge_ids_for_context(
        recipient_class=request.recipient_class,
        message_type=request.message_type,
        modifiers=modifier_map,
        proof_ids=getattr(proof_packet, "proof_ids", ()),
    )
    required_depth = _depth_label(len(judge_ids))
    return tuple(
        _judge_profile_for_id(judge_id, required_for_depth=required_depth)
        for judge_id in judge_ids
    )


def _is_independent_judge(result: X1DJudgeResult) -> bool:
    return result.provider != GENERATOR_PROVIDER_ID and result.model != GENERATOR_MODEL_ID


def _is_live_claude_judge(result: X1DJudgeResult) -> bool:
    return (
        result.provider == DEFAULT_X1D_JUDGE_PROVIDER
        and result.model == DEFAULT_X1D_JUDGE_MODEL
        and result.transport_provenance == LIVE_CLAUDE_API_CALL
        and result.transport_provider == ANTHROPIC_MESSAGES_API
        and bool(_clean(result.transport_call_id))
        and result.raw_response_digest.startswith("sha256:")
    )


def _normalize_judge_result(
    result: X1DJudgeResult,
    profile: X1DJudgeProfile,
) -> X1DJudgeResult:
    threshold = result.threshold if result.threshold > 0 else profile.threshold
    model_ok = result.model == profile.model
    provider_ok = result.provider == profile.provider
    available = result.availability_status == JUDGE_AVAILABLE
    independent = _is_independent_judge(result)
    live_claude = _is_live_claude_judge(result)
    score_passed = result.score >= threshold
    passed = bool(
        result.passed
        and score_passed
        and available
        and independent
        and model_ok
        and provider_ok
        and live_claude
    )
    return replace(
        result,
        threshold=threshold,
        passed=passed,
        independence_status=INDEPENDENT_JUDGE if independent else NON_INDEPENDENT_JUDGE,
    )


def evaluate_x1d(
    request: WholeMessageGenerationRequest,
    *,
    x2_result: X2ValidationResult,
    judge_results: Iterable[X1DJudgeResult] = (),
) -> X1DValidationResult:
    """Evaluate required X1D judge results after X2 passes."""
    profiles = required_x1d_profiles(request)
    required_depth = _depth_label(
        max(request.reasoning_policy.x1d_llm_judge_depth, len(profiles))
    )
    if not x2_result.passed:
        return X1DValidationResult(
            status=STATUS_X1D_BLOCKED,
            passed=False,
            required_depth=required_depth,
            required_profiles=(),
            judge_results=(),
            missing_judge_ids=(),
            reason_codes=("x1d_blocked_until_x2_passes",),
        )

    if not profiles:
        return X1DValidationResult(
            status=STATUS_X1D_NOT_REQUIRED,
            passed=True,
            required_depth=required_depth,
            required_profiles=(),
            judge_results=(),
            missing_judge_ids=(),
            reason_codes=("x2_only_clearance_path",),
        )

    supplied_by_id = {result.judge_id: result for result in judge_results}
    normalized: list[X1DJudgeResult] = []
    missing: list[str] = []
    reasons: list[str] = []

    for profile in profiles:
        supplied = supplied_by_id.get(profile.judge_id)
        if supplied is None:
            missing.append(profile.judge_id)
            reasons.append(f"missing_required_judge:{profile.judge_id}")
            continue
        result = _normalize_judge_result(supplied, profile)
        normalized.append(result)
        if result.availability_status != JUDGE_AVAILABLE:
            reasons.append(f"judge_unavailable:{profile.judge_id}")
        if not _is_live_claude_judge(result):
            reasons.append(f"non_live_claude_judge:{profile.judge_id}")
        if result.independence_status != INDEPENDENT_JUDGE:
            reasons.append(f"non_independent_judge:{profile.judge_id}")
        if result.model != profile.model:
            reasons.append(f"wrong_judge_model:{profile.judge_id}")
        if result.provider != profile.provider:
            reasons.append(f"wrong_judge_provider:{profile.judge_id}")
        if result.score < result.threshold:
            reasons.append(f"judge_below_threshold:{profile.judge_id}")
        if not supplied.passed:
            reasons.append(f"judge_reported_fail:{profile.judge_id}")

    blocking_reason_prefixes = (
        "missing_required_judge:",
        "judge_unavailable:",
        "non_live_claude_judge:",
        "non_independent_judge:",
        "wrong_judge_model:",
        "wrong_judge_provider:",
    )
    blocked = any(
        reason.startswith(blocking_reason_prefixes)
        for reason in reasons
    ) or bool(missing)
    passed = not missing and not reasons and len(normalized) == len(profiles)
    return X1DValidationResult(
        status=STATUS_X1D_PASS if passed else (STATUS_X1D_BLOCKED if blocked else STATUS_X1D_REVIEW_REQUIRED),
        passed=passed,
        required_depth=required_depth,
        required_profiles=profiles,
        judge_results=tuple(normalized),
        missing_judge_ids=tuple(missing),
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


def _exit_status(disposition: str) -> str:
    if disposition == EXIT_CLEAR_DRAFT:
        return STATUS_EXIT_CLEAR_DRAFT
    if disposition == EXIT_REVIEW_REQUIRED:
        return STATUS_EXIT_REVIEW_REQUIRED
    if disposition == EXIT_ABSTAIN:
        return STATUS_EXIT_ABSTAIN
    return STATUS_EXIT_BLOCKED


def decide_exit(
    request: WholeMessageGenerationRequest,
    *,
    x2_result: X2ValidationResult,
    x1d_result: X1DValidationResult,
    selected_candidate: WholeMessageCandidate | None,
) -> ExitProofBundle:
    """Apply final Exit authority after X2 and X1D evaluation."""
    if not x2_result.passed:
        disposition = EXIT_BLOCKED
        exit_reason = "x2_hard_gate_failed"
        review_reason = ""
    elif x1d_result.status == STATUS_X1D_BLOCKED:
        disposition = EXIT_BLOCKED
        exit_reason = "x1d_blocked"
        review_reason = ""
    elif not x1d_result.passed:
        disposition = EXIT_REVIEW_REQUIRED
        exit_reason = "x1d_review_required"
        review_reason = ",".join(x1d_result.reason_codes)
    elif not selected_candidate:
        disposition = EXIT_BLOCKED
        exit_reason = "selected_candidate_missing"
        review_reason = ""
    else:
        disposition = EXIT_CLEAR_DRAFT
        exit_reason = "all_required_gates_and_judges_passed"
        review_reason = ""

    candidate_id = selected_candidate.candidate_id if selected_candidate else x2_result.selected_candidate_id
    visible_draft_id = candidate_id if disposition in {EXIT_CLEAR_DRAFT, EXIT_REVIEW_REQUIRED} else ""
    return ExitProofBundle(
        status=_exit_status(disposition),
        disposition=disposition,
        request_id=request.request_id,
        trace_root=request.trace_root,
        candidate_id=candidate_id,
        final_user_visible_draft_id=visible_draft_id,
        review_required_reason=review_reason,
        exit_reason=exit_reason,
        no_send_receipt=request.no_send_receipt,
        proof_packet_id=request.proof_packet.proof_packet_id,
        prompt_contract_id=request.prompt_contract_id,
        generator_model_id=selected_candidate.model_id if selected_candidate else GENERATOR_MODEL_ID,
        generator_provider_id=selected_candidate.provider_id if selected_candidate else GENERATOR_PROVIDER_ID,
        x2_result=x2_result,
        x1d_result=x1d_result,
    )


def run_validation_exit(
    request: WholeMessageGenerationRequest,
    batch: WholeMessageCandidateBatch,
    *,
    selected_candidate_id: str = "",
    judge_results: Iterable[X1DJudgeResult] = (),
    x1d_judge_runner: Callable[
        [WholeMessageGenerationRequest, WholeMessageCandidate],
        Iterable[X1DJudgeResult],
    ] | None = None,
    application_status: str = "",
) -> ExitProofBundle:
    """Run W7 X2, X1D, and Exit and return the proof bundle."""
    x2_result = run_x2_validation(
        request,
        batch,
        selected_candidate_id=selected_candidate_id,
        application_status=application_status,
    )
    selected_candidate = _candidate_by_id(batch, x2_result.selected_candidate_id) if x2_result.selected_candidate_id else None
    judge_result_tuple = tuple(judge_results)
    if x2_result.passed and selected_candidate is not None and x1d_judge_runner is not None:
        judge_result_tuple = tuple(x1d_judge_runner(request, selected_candidate))
    x1d_result = evaluate_x1d(
        request,
        x2_result=x2_result,
        judge_results=judge_result_tuple,
    )
    return decide_exit(
        request,
        x2_result=x2_result,
        x1d_result=x1d_result,
        selected_candidate=selected_candidate,
    )


__all__ = [
    "DEFAULT_X1D_JUDGE_MODEL",
    "DEFAULT_X1D_JUDGE_PROVIDER",
    "EXIT_ABSTAIN",
    "EXIT_BLOCKED",
    "EXIT_CLEAR_DRAFT",
    "EXIT_REVIEW_REQUIRED",
    "GATE_APPLICATION_STATUS",
    "GATE_CANDIDATE_SELECTION",
    "GATE_CHANNEL_LENGTH",
    "GATE_COMPANY_TRIGGER",
    "GATE_JD_REQUIRED",
    "GATE_NO_SEND",
    "GATE_POSITION_NAME",
    "GATE_PRIOR_THREAD",
    "GATE_PROMPT_INJECTION",
    "GATE_RECIPIENT_CLASS",
    "GATE_REFERRAL_CONTEXT",
    "GATE_RELATIONSHIP_EVIDENCE",
    "GATE_REQUISITION_NUMBER",
    "GATE_ROLE_OWNERSHIP_FIT",
    "GATE_SCHEMA",
    "GATE_UNSUPPORTED_CLAIM",
    "GATE_WHOLE_MESSAGE_SHAPE",
    "INDEPENDENT_JUDGE",
    "JUDGE_AVAILABLE",
    "JUDGE_CEO_EVIDENCE_RISK",
    "JUDGE_CEO_ORIGINALITY",
    "JUDGE_EVIDENCE_SUPPORT",
    "JUDGE_LINKEDIN_TONE",
    "JUDGE_LINKEDIN_TONE_NON_GENERIC",
    "JUDGE_UNAVAILABLE",
    "MODIFIER_PROVIDER_BACKED_GENERATION",
    "MODIFIER_SIMILARITY_GATE_FLAGGED",
    "NON_INDEPENDENT_JUDGE",
    "STATUS_EXIT_ABSTAIN",
    "STATUS_EXIT_BLOCKED",
    "STATUS_EXIT_CLEAR_DRAFT",
    "STATUS_EXIT_REVIEW_REQUIRED",
    "STATUS_X1D_BLOCKED",
    "STATUS_X1D_NOT_REQUIRED",
    "STATUS_X1D_PASS",
    "STATUS_X1D_REVIEW_REQUIRED",
    "STATUS_X2_BLOCKED",
    "STATUS_X2_PASS",
    "X1D_DEPTH_NONE",
    "X1D_DEPTH_ONE",
    "X1D_DEPTH_TWO",
    "X1DJudgeProfilePolicy",
    "X1DJudgeProfile",
    "X1DJudgeResult",
    "X1DValidationResult",
    "X2GateResult",
    "X2ValidationResult",
    "ExitProofBundle",
    "decide_exit",
    "evaluate_x1d",
    "required_x1d_judge_ids_for_context",
    "required_x1d_profiles",
    "run_validation_exit",
    "run_x2_validation",
    "x1d_judge_profile_policy",
]
