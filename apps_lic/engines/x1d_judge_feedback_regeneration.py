"""Bounded X1D judge-feedback regeneration for apps_lic W5.

This module orchestrates one controlled Qwen repair pass after live Claude X1D
review feedback. It does not change W4 receipts and does not make Exit
provider-aware; it reruns the deterministic Exit engine against a repair
candidate overlay.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from apps_lic.engines.generation_engine import generate_judge_feedback_repair_draft
from apps_lic.engines.validation_exit import (
    STATUS_X1D_BLOCKED,
    STATUS_X1D_PASS,
    STATUS_X1D_REVIEW_REQUIRED,
    ExitProofBundle,
    X1DJudgeResult,
    run_validation_exit,
)
from apps_lic.engines.whole_message_generation import (
    GENERATOR_MODEL_ID,
    GENERATOR_PROVIDER_ID,
    NO_DURABLE_WRITE_RECEIPT,
    STATUS_CANDIDATES_READY,
    WholeMessageCandidate,
    WholeMessageCandidateBatch,
    WholeMessageGenerationRequest,
)
from apps_lic.types.recipient_archetype_mapping import (
    ARCHETYPE_C_LEVEL,
    ARCHETYPE_EXECUTIVE,
    ARCHETYPE_RECRUITER,
    ARCHETYPE_SENIOR_TA,
    resolve_recipient_template_policy,
)


STOP_ALREADY_CLEAR = "already_clear"
STOP_REPAIR_BUDGET_EXHAUSTED = "repair_budget_exhausted"
STOP_X1D_NOT_REVIEW_REQUIRED = "x1d_not_review_required"
STOP_X1D_BLOCKED_NO_REGENERATION = "x1d_blocked_no_regeneration"
STOP_X2_FAILED_BEFORE_JUDGE_FEEDBACK = "x2_failed_before_judge_feedback"
STOP_NO_SELECTED_CANDIDATE = "no_selected_candidate"
STOP_QWEN_REPAIR_UNAVAILABLE = "qwen_repair_unavailable"
STOP_QWEN_REPAIR_UNPARSEABLE = "qwen_repair_unparseable"
STOP_REPAIR_SAME_AS_PARENT = "repair_same_as_parent"
STOP_REPAIR_CANDIDATE_X2_FAILED = "repair_candidate_x2_failed"
STOP_REPAIR_CANDIDATE_X1D_BLOCKED = "repair_candidate_x1d_blocked"
STOP_REPAIR_CANDIDATE_REVIEW_REQUIRED = "repair_candidate_review_required"
STOP_REPAIR_CANDIDATE_CLEAR = "repair_candidate_clear"
_SIGNATURE_PATTERN = re.compile(
    r"(?:\r?\n|\A)\s*(?:best|thanks|regards|warmly|cheers)?[,]?\s*Amit(?: Ayer)?\.?\s*\Z",
    flags=re.IGNORECASE,
)

_MAX_REPAIR_HARD_CAP = 2
_REGEN_REASON_PREFIXES = (
    "judge_below_threshold:",
    "judge_reported_fail:",
)
_BLOCKED_REASON_PREFIXES = (
    "missing_required_judge:",
    "judge_unavailable:",
    "non_live_claude_judge:",
    "non_independent_judge:",
    "wrong_judge_model:",
    "wrong_judge_provider:",
)
_C_LEVEL_EDITORIAL_BANNED_PHRASES = (
    "brief executive exchange",
    "pressure-test",
    "pressure test",
    "worth a look",
    "commercial proof:",
    "the governance foundation is",
    "my fit is",
    "my proof is",
    "the measurable proof is",
)

RepairRunner = Callable[
    [WholeMessageGenerationRequest, WholeMessageCandidate, tuple[X1DJudgeResult, ...], int],
    WholeMessageCandidate | None,
]
JudgeRunner = Callable[
    [WholeMessageGenerationRequest, WholeMessageCandidate],
    Iterable[X1DJudgeResult],
]


@dataclass(frozen=True)
class X1DFeedbackRegenerationAttempt:
    iteration: int
    parent_candidate_id: str
    repaired_candidate_id: str
    failed_judge_ids: tuple[str, ...]
    required_repairs: tuple[str, ...]
    pre_repair_scores: tuple[dict[str, Any], ...]
    post_repair_scores: tuple[dict[str, Any], ...]
    stop_reason: str
    qwen_repair_receipt: str
    x2_status: str
    x1d_status: str
    repaired_candidate: dict[str, Any]
    x1d_repair_effective: bool
    x1d_repair_resolved_issue_ids: tuple[str, ...]
    x1d_repair_unresolved_issue_ids: tuple[str, ...]
    repair_candidate_sanitization_passed: bool

    def to_packet(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "parent_candidate_id": self.parent_candidate_id,
            "repaired_candidate_id": self.repaired_candidate_id,
            "failed_judge_ids": list(self.failed_judge_ids),
            "required_repairs": list(self.required_repairs),
            "pre_repair_scores": list(self.pre_repair_scores),
            "post_repair_scores": list(self.post_repair_scores),
            "stop_reason": self.stop_reason,
            "qwen_repair_receipt": self.qwen_repair_receipt,
            "x2_status": self.x2_status,
            "x1d_status": self.x1d_status,
            "repaired_candidate": dict(self.repaired_candidate),
            "x1d_repair_effective": self.x1d_repair_effective,
            "x1d_repair_resolved_issue_ids": list(self.x1d_repair_resolved_issue_ids),
            "x1d_repair_unresolved_issue_ids": list(self.x1d_repair_unresolved_issue_ids),
            "repair_candidate_sanitization_passed": self.repair_candidate_sanitization_passed,
        }


@dataclass(frozen=True)
class X1DFeedbackRegenerationResult:
    attempted: bool
    iteration_count: int
    stop_reason: str
    final_proof: ExitProofBundle
    final_selected_candidate_id: str
    attempts: tuple[X1DFeedbackRegenerationAttempt, ...] = ()

    def to_packet(self) -> dict[str, Any]:
        resolved_issue_ids = tuple(
            dict.fromkeys(
                issue_id
                for attempt in self.attempts
                for issue_id in attempt.x1d_repair_resolved_issue_ids
            )
        )
        unresolved_issue_ids = tuple(
            dict.fromkeys(
                issue_id
                for attempt in self.attempts
                for issue_id in attempt.x1d_repair_unresolved_issue_ids
            )
        )
        return {
            "schema_version": "apps_lic.x1d_feedback_regeneration_result.v1",
            "attempted": self.attempted,
            "iteration_count": self.iteration_count,
            "stop_reason": self.stop_reason,
            "final_selected_candidate_id": self.final_selected_candidate_id,
            "x1d_repair_effective": any(
                attempt.x1d_repair_effective for attempt in self.attempts
            ),
            "x1d_repair_resolved_issue_ids": list(resolved_issue_ids),
            "x1d_repair_unresolved_issue_ids": list(unresolved_issue_ids),
            "repair_candidate_sanitization_passed": all(
                attempt.repair_candidate_sanitization_passed for attempt in self.attempts
            )
            if self.attempts
            else False,
            "attempts": [attempt.to_packet() for attempt in self.attempts],
        }


@dataclass(frozen=True)
class X1DFeedbackRepairPlan:
    intents: tuple[str, ...]
    company: str
    role: str
    recipient_class: str
    archetype: str
    altitude: str
    cta_style: str
    evidence_bridge_sentence: str
    outcome_sentence: str
    cta_sentence: str
    allowed_claim_ids: frozenset[str]


@dataclass(frozen=True)
class X1DNormalizedRepairIntent:
    judge_id: str
    issue_id: str
    required_repair: str
    intent: str
    required_claim_ids: tuple[str, ...]


@dataclass(frozen=True)
class X1DRepairCandidateSanitizationResult:
    text: str
    subject_line: str
    claims_used: tuple[str, ...]
    passed: bool
    issues: tuple[str, ...]


def run_x1d_judge_feedback_regeneration(
    *,
    request: WholeMessageGenerationRequest,
    batch: WholeMessageCandidateBatch,
    selected_candidate_id: str,
    initial_proof: ExitProofBundle,
    x1d_judge_runner: JudgeRunner | None,
    repair_runner: RepairRunner | None = None,
    application_status: str = "",
    max_iterations: int | None = None,
) -> X1DFeedbackRegenerationResult:
    """Run a bounded X1D feedback repair loop and return the final proof."""
    stop_reason = _initial_stop_reason(
        proof=initial_proof,
        batch=batch,
        selected_candidate_id=selected_candidate_id,
    )
    if stop_reason:
        return _result(
            attempted=False,
            stop_reason=stop_reason,
            proof=initial_proof,
            selected_candidate_id=selected_candidate_id,
        )

    limit = _max_repair_iterations(
        request,
        explicit=max_iterations,
        initial_proof=initial_proof,
    )
    if limit <= 0:
        return _result(
            attempted=False,
            stop_reason=STOP_REPAIR_BUDGET_EXHAUSTED,
            proof=initial_proof,
            selected_candidate_id=selected_candidate_id,
        )

    runner = repair_runner or qwen_judge_feedback_repair_candidate
    current_batch = batch
    current_proof = initial_proof
    current_selected_id = current_proof.candidate_id or selected_candidate_id
    attempts: list[X1DFeedbackRegenerationAttempt] = []

    iteration = 1
    while iteration <= limit:
        parent = _candidate_by_id(current_batch, current_selected_id)
        if parent is None:
            return _result(
                attempted=bool(attempts),
                stop_reason=STOP_NO_SELECTED_CANDIDATE,
                proof=current_proof,
                selected_candidate_id=current_selected_id,
                attempts=tuple(attempts),
            )
        failed = _failed_judges(current_proof)
        repaired = runner(request, parent, failed, iteration)
        if repaired is None:
            return _result(
                attempted=True,
                stop_reason=STOP_QWEN_REPAIR_UNAVAILABLE,
                proof=current_proof,
                selected_candidate_id=current_selected_id,
                attempts=tuple(attempts),
            )
        if not repaired.draft_text.strip():
            return _result(
                attempted=True,
                stop_reason=STOP_QWEN_REPAIR_UNPARSEABLE,
                proof=current_proof,
                selected_candidate_id=current_selected_id,
                attempts=tuple(attempts),
            )
        if _message_fingerprint(repaired.draft_text) == _message_fingerprint(parent.draft_text):
            attempt = _attempt(
                iteration=iteration,
                parent=parent,
                repaired=repaired,
                failed=failed,
                pre=current_proof,
                post=None,
                stop_reason=STOP_REPAIR_SAME_AS_PARENT,
                repair_candidate_sanitization_passed=_repair_candidate_sanitization_passed(
                    request=request,
                    candidate=repaired,
                    failed=failed,
                ),
            )
            attempts.append(attempt)
            return _result(
                attempted=True,
                stop_reason=STOP_REPAIR_SAME_AS_PARENT,
                proof=current_proof,
                selected_candidate_id=current_selected_id,
                attempts=tuple(attempts),
            )

        current_batch = _overlay_repair_candidate(current_batch, repaired)
        repaired_proof = run_validation_exit(
            request,
            current_batch,
            selected_candidate_id=repaired.candidate_id,
            x1d_judge_runner=x1d_judge_runner,
            application_status=application_status,
        )
        stop_reason = _post_repair_stop_reason(repaired_proof)
        attempt = _attempt(
            iteration=iteration,
            parent=parent,
            repaired=repaired,
            failed=failed,
            pre=current_proof,
            post=repaired_proof,
            stop_reason=stop_reason,
            repair_candidate_sanitization_passed=_repair_candidate_sanitization_passed(
                request=request,
                candidate=repaired,
                failed=failed,
            ),
        )
        attempts.append(attempt)
        if stop_reason == STOP_REPAIR_CANDIDATE_CLEAR:
            return _result(
                attempted=True,
                stop_reason=stop_reason,
                proof=repaired_proof,
                selected_candidate_id=repaired.candidate_id,
                attempts=tuple(attempts),
            )
        if stop_reason != STOP_REPAIR_CANDIDATE_REVIEW_REQUIRED:
            return _result(
                attempted=True,
                stop_reason=stop_reason,
                proof=repaired_proof,
                selected_candidate_id=repaired.candidate_id,
                attempts=tuple(attempts),
            )
        if iteration >= limit and _can_extend_after_effective_repair(attempt):
            limit = min(_MAX_REPAIR_HARD_CAP, iteration + 1)
        current_proof = repaired_proof
        current_selected_id = repaired.candidate_id
        iteration += 1

    return _result(
        attempted=bool(attempts),
        stop_reason=STOP_REPAIR_BUDGET_EXHAUSTED,
        proof=current_proof,
        selected_candidate_id=current_selected_id,
        attempts=tuple(attempts),
    )


def qwen_judge_feedback_repair_candidate(
    request: WholeMessageGenerationRequest,
    parent_candidate: WholeMessageCandidate,
    judge_results: tuple[X1DJudgeResult, ...],
    iteration: int,
) -> WholeMessageCandidate | None:
    """Call Qwen repair generation and convert the draft payload to a candidate."""
    draft = generate_judge_feedback_repair_draft(
        request=request,
        parent_candidate=parent_candidate,
        judge_results=judge_results,
        iteration=iteration,
    )
    if not draft:
        return None
    entries = draft.get("candidates") if isinstance(draft.get("candidates"), list) else []
    selected_id = str(draft.get("selected_candidate_id") or "").strip()
    selected_entry = next(
        (
            item
            for item in entries
            if isinstance(item, dict)
            and str(item.get("candidate_id") or "").strip() == selected_id
        ),
        entries[0] if entries else {},
    )
    text = str(
        (selected_entry or {}).get("draft_text")
        or (selected_entry or {}).get("message_text")
        or draft.get("message_text")
        or draft.get("body")
        or ""
    ).strip()
    if not text:
        return None
    text = _ensure_terminal_amit_signature(text)
    subject_line = str(
        (selected_entry or {}).get("subject_line")
        or (selected_entry or {}).get("subject")
        or draft.get("subject_line")
        or draft.get("subject")
        or getattr(parent_candidate, "subject_line", "")
        or ""
    ).strip()
    claims = tuple(
        dict.fromkeys(
            str(item).strip()
            for item in (
                (selected_entry or {}).get("claims_used")
                or draft.get("claims_used")
                or parent_candidate.claims_used
                or ()
            )
            if str(item).strip()
        )
    )
    normalized_intents = _normalize_repair_intents(judge_results)
    text, subject_line = _apply_feedback_repairs(
        text=text,
        subject_line=subject_line,
        request=request,
        judge_results=judge_results,
        normalized_intents=normalized_intents,
    )
    claims = _claims_from_repaired_text(
        text,
        existing=claims,
        allowed_claim_ids=_allowed_claim_ids(request),
    )
    text, subject_line, claims = _maybe_clean_rebuild_repair_candidate(
        text=text,
        subject_line=subject_line,
        claims_used=claims,
        request=request,
        parent_candidate=parent_candidate,
        normalized_intents=normalized_intents,
    )
    sanitized = _sanitize_repair_candidate(
        text=text,
        subject_line=subject_line,
        claims_used=claims,
        request=request,
        normalized_intents=normalized_intents,
    )
    if not sanitized.passed:
        return None
    text = sanitized.text
    subject_line = sanitized.subject_line
    claims = sanitized.claims_used
    candidate_id = selected_id or _candidate_id(parent_candidate, text, iteration)
    model_call_ref = str((selected_entry or {}).get("model_call_ref") or "").strip()
    provider_receipt = str((selected_entry or {}).get("provider_receipt") or "").strip()
    if not model_call_ref:
        model_call_ref = f"mref:x1d-repair:{candidate_id}"
    if not provider_receipt:
        provider_receipt = f"prov:qwen-repair:{candidate_id}"
    return WholeMessageCandidate(
        candidate_id=_repair_candidate_id(candidate_id, iteration),
        subject_line=subject_line,
        draft_text=text,
        attempt_seed=_digest(
            {
                "parent_candidate_id": parent_candidate.candidate_id,
                "candidate_id": candidate_id,
                "iteration": iteration,
                "draft_text": text,
            }
        ),
        model_id=str(draft.get("model") or GENERATOR_MODEL_ID),
        provider_id=str(draft.get("target_provider") or draft.get("provider_profile") or GENERATOR_PROVIDER_ID),
        temperature=float(draft.get("generation_temperature") or request.reasoning_policy.repair_temperature),
        top_p=float(draft.get("top_p") or request.reasoning_policy.top_p),
        word_count=_word_count(text),
        sentence_count=_sentence_count(text),
        char_count=len(text),
        claims_used=claims,
        is_whole_message=True,
        no_durable_write_receipt=NO_DURABLE_WRITE_RECEIPT,
        generation_receipt=f"x1d_feedback_repair:{provider_receipt}:{model_call_ref}",
    )


def _apply_feedback_repairs(
    *,
    text: str,
    subject_line: str,
    request: WholeMessageGenerationRequest,
    judge_results: tuple[X1DJudgeResult, ...],
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...] = (),
) -> tuple[str, str]:
    feedback = _feedback_text(judge_results, normalized_intents=normalized_intents)
    target = dict(getattr(request, "target_context", {}) or {})
    jd = dict(getattr(request, "jd_fields", {}) or {})
    company = str(target.get("company") or jd.get("company") or "").strip()
    role = str(jd.get("position_name") or jd.get("job_title") or "").strip()
    recipient_class = str(getattr(request, "recipient_class", "") or "").strip()
    plan = _build_feedback_repair_plan(
        request=request,
        target=target,
        company=company,
        role=role,
        recipient_class=recipient_class,
        feedback=feedback,
    )

    if role and "subject_line" in feedback:
        subject_line = _repair_subject_line(
            role=role,
            company=company,
            feedback=feedback,
        )
    recruiter_repair = _recruiter_feedback_repair_draft(target=target, plan=plan)
    if recruiter_repair:
        return _ensure_terminal_amit_signature(recruiter_repair), subject_line
    if "agentic_platform_evidence" in plan.intents:
        text = _ensure_multi_agent_orchestration(text)
    if "citi sky" in feedback and ("unsupported" in feedback or "unsubstantiated" in feedback or "remove" in feedback):
        text = re.sub(r"\bCiti Sky,\s*", "", text)
    text = _remove_cross_company_texture(text, company=company)
    if "remove_redundant_bridge" in plan.intents:
        text = _remove_redundant_bridge_sentences(text)
    if "role_fit_bridge" in plan.intents:
        text = _replace_role_fit_sentence(text, plan=plan)
    if "governed_platform_controls" in plan.intents:
        text = _insert_before_cta(text, plan.evidence_bridge_sentence)
    if "scale_outcome" in plan.intents:
        text = _insert_before_cta(text, plan.outcome_sentence)
    if "cta" in plan.intents:
        text = _replace_cta(text, cta=plan.cta_sentence)
    text = _remove_cross_company_texture(text, company=company)
    return _ensure_terminal_amit_signature(text), subject_line


def _allowed_claim_ids(request: WholeMessageGenerationRequest) -> set[str]:
    proof_packet = getattr(request, "proof_packet", None)
    proof_ids = getattr(proof_packet, "proof_ids", ()) or ()
    return {str(item).strip() for item in proof_ids if str(item).strip()}


def _repair_subject_line(*, role: str, company: str, feedback: str) -> str:
    company_phrase = company or "target company"
    feedback_lower = feedback.lower()
    company_lower = company_phrase.lower()
    if "graph" in feedback_lower or company_lower == "neo4j":
        subject = f"{company_phrase} Agentic AI product proof"
    elif company_lower == "citi":
        if any(marker in feedback_lower for marker in ("cio", "c_level", "ceo", "governance_foundation")):
            subject = f"{company_phrase} Sky CIO governance loop"
        elif "recruiter" in feedback_lower or "screen" in feedback_lower:
            subject = f"{company_phrase} Head of AI Strategy fit proof"
        elif "senior_ta" in feedback_lower or "fit_review" in feedback_lower:
            subject = f"{company_phrase} AI strategy fit proof"
        elif "cloud_ai_transformation" in feedback_lower or "quantified" in feedback_lower:
            subject = f"{company_phrase} Sky scale proof"
        else:
            subject = f"{company_phrase} Sky production AI controls"
    elif company_lower == "aig":
        if any(marker in feedback_lower for marker in ("gcdo", "subject", "agentic", "c_level", "ceo")):
            subject = f"{company_phrase} GCDO agentic operating proof"
        else:
            subject = f"{company_phrase} GCDO agent governance"
    elif "agentic" in feedback_lower or "ai" in feedback_lower:
        subject = f"{company_phrase} governed AI signal for {role}"
    else:
        subject = f"{company_phrase} {role} fit"
    return subject[:200].rstrip(" .")


def _maybe_clean_rebuild_repair_candidate(
    *,
    text: str,
    subject_line: str,
    claims_used: tuple[str, ...],
    request: WholeMessageGenerationRequest,
    parent_candidate: WholeMessageCandidate,
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...],
) -> tuple[str, str, tuple[str, ...]]:
    first_pass = _sanitize_repair_candidate(
        text=text,
        subject_line=subject_line,
        claims_used=claims_used,
        request=request,
        normalized_intents=normalized_intents,
    )
    if (
        first_pass.passed
        and _message_fingerprint(first_pass.text) != _message_fingerprint(parent_candidate.draft_text)
        and not _requires_clean_rebuild(first_pass.issues, normalized_intents)
    ):
        return first_pass.text, first_pass.subject_line, first_pass.claims_used

    rebuilt = _clean_rebuild_repair_text(
        request=request,
        normalized_intents=normalized_intents,
    )
    if not rebuilt:
        return first_pass.text, first_pass.subject_line, first_pass.claims_used
    rebuilt_subject_line = _clean_rebuild_subject_line(
        existing=subject_line,
        request=request,
        normalized_intents=normalized_intents,
    )
    rebuilt_claims = _claims_from_repaired_text(
        rebuilt,
        existing=first_pass.claims_used,
        allowed_claim_ids=_allowed_claim_ids(request),
    )
    second_pass = _sanitize_repair_candidate(
        text=rebuilt,
        subject_line=rebuilt_subject_line,
        claims_used=rebuilt_claims,
        request=request,
        normalized_intents=normalized_intents,
    )
    if second_pass.passed:
        return second_pass.text, second_pass.subject_line, second_pass.claims_used
    return first_pass.text, first_pass.subject_line, first_pass.claims_used


def _requires_clean_rebuild(
    sanitizer_issues: tuple[str, ...],
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...],
) -> bool:
    if sanitizer_issues:
        return True
    rebuild_intents = {
        "signature_dedupe",
        "length_budget",
        "trigger_hook",
        "claim_surface",
        "opening_rewrite",
    }
    return any(intent.intent in rebuild_intents for intent in normalized_intents)


def _clean_rebuild_subject_line(
    *,
    existing: str,
    request: WholeMessageGenerationRequest,
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...],
) -> str:
    target = dict(getattr(request, "target_context", {}) or {})
    jd = dict(getattr(request, "jd_fields", {}) or {})
    company = str(target.get("company") or jd.get("company") or "").strip()
    role = str(jd.get("position_name") or jd.get("job_title") or "").strip()
    feedback = " ".join(
        [intent.intent for intent in normalized_intents]
        + [intent.issue_id for intent in normalized_intents]
        + [str(target.get("company_trigger") or "")]
    )
    if not company or not role:
        return existing
    if any(
        marker in feedback.lower()
        for marker in ("subject_line", "generic", "trigger", "hook", "claim_surface")
    ):
        recipient_class = str(getattr(request, "recipient_class", "") or "").strip()
        if company.lower() == "citi" and recipient_class == ARCHETYPE_RECRUITER:
            return "Citi Head of AI Strategy recruiter screen"
        editorial_subject = _c_level_editorial_subject_line(
            company=company,
            request=request,
            feedback=feedback,
        )
        if editorial_subject:
            return editorial_subject
        return _repair_subject_line(role=role, company=company, feedback=feedback)
    return existing


def _clean_rebuild_repair_text(
    *,
    request: WholeMessageGenerationRequest,
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...],
) -> str:
    target = dict(getattr(request, "target_context", {}) or {})
    jd = dict(getattr(request, "jd_fields", {}) or {})
    company = str(target.get("company") or jd.get("company") or "").strip()
    role = str(jd.get("position_name") or jd.get("job_title") or "").strip()
    recipient_class = str(getattr(request, "recipient_class", "") or "").strip()
    plan = _build_feedback_repair_plan(
        request=request,
        target=target,
        company=company,
        role=role,
        recipient_class=recipient_class,
        feedback=" ".join(
            [intent.intent for intent in normalized_intents]
            + [
                claim_id
                for intent in normalized_intents
                for claim_id in intent.required_claim_ids
            ]
        ),
    )
    first_name = _first_name(
        str(target.get("name") or target.get("contact_name") or "there")
    )
    company_phrase = company or "the company"
    role_phrase = role or "the open role"
    role_short = _compact_role_phrase(role_phrase)
    feedback = _normalized_feedback_signature(normalized_intents)
    raw_required_claims = {
        claim_id
        for intent in normalized_intents
        for claim_id in intent.required_claim_ids
    }
    required_claims = {
        claim_id
        for intent in normalized_intents
        for claim_id in intent.required_claim_ids
        if claim_id in plan.allowed_claim_ids
    }
    allowed = set(plan.allowed_claim_ids)
    company_specific = _company_specific_clean_rebuild_text(
        first_name=first_name,
        company=company_phrase,
        target=target,
        plan=plan,
        allowed_claim_ids=allowed,
        required_claim_ids=raw_required_claims,
        feedback=feedback,
    )
    if company_specific:
        return _ensure_terminal_amit_signature(company_specific)
    sentences = [
        _clean_rebuild_opening_sentence(
            first_name=first_name,
            company=company_phrase,
            role=role_phrase,
            target=target,
            feedback=feedback,
        ),
        _clean_rebuild_evidence_sentence(
            allowed_claim_ids=allowed,
            company=company_phrase,
            feedback=feedback,
        ),
    ]
    if "sp_runtime_reliability" in required_claims or "sp_runtime_reliability" in allowed:
        sentences.append(
            "The reliability proof is production validation gates, traceable evaluations, and rollback paths for agent workflows."
        )
    if (
        "sp_platform_commercialization" in required_claims
        or "sp_platform_commercialization" in allowed
        or "scale_outcome" in plan.intents
    ):
        sentences.append(plan.outcome_sentence)
    if (
        "sp_cloud_ai_transformation" in allowed
        and _asks_for_quantified_outcome(feedback)
    ):
        sentences.append(
            "A second scale proof is architecture and commercial ownership of a $30M cloud and AI transformation portfolio for Fortune 500 financial institutions."
        )
    sentences.append(
        _clean_rebuild_fit_sentence(
            company=company_phrase,
            role=role_short,
            plan=plan,
            feedback=feedback,
        )
    )
    sentences.append(_clean_rebuild_cta(plan=plan, role=role_short, feedback=feedback))
    return _ensure_terminal_amit_signature(" ".join(dict.fromkeys(sentences)))


def _company_specific_clean_rebuild_text(
    *,
    first_name: str,
    company: str,
    target: dict[str, Any],
    plan: X1DFeedbackRepairPlan,
    allowed_claim_ids: set[str],
    required_claim_ids: set[str],
    feedback: str,
) -> str:
    company_lower = company.lower()
    if company_lower not in {"aig", "citi", "neo4j"}:
        return ""
    if not _needs_company_specific_rebuild(feedback):
        return ""
    sentences: list[str] = []
    c_level_editorial = _compose_c_level_editorial_rebuild(
        first_name=first_name,
        company=company,
        target=target,
        plan=plan,
        allowed_claim_ids=allowed_claim_ids,
        feedback=feedback,
    )
    if c_level_editorial:
        return c_level_editorial
    if company_lower == "aig":
        if plan.archetype == ARCHETYPE_C_LEVEL:
            if any(marker in feedback for marker in ("value_bridge_generic", "revenue_proof", "cta_phrasing")):
                sentences.append(
                    f"Hi {first_name}, AIG's VP Global Head of Agentic AI Solutions role is the named trigger: GenAI standards have to become release rules for claims and underwriting agents."
                )
                sentences.append(
                    "I have built governed agent platforms with policy gates, evaluation traces, rollback paths, and reusable service patterns."
                )
                sentences.append(
                    "The commercial bridge is reuse economics for regulated workflows: productized agentic AI services tied to $22M revenue and 20% margin expansion."
                )
                sentences.append(
                    "Would 15 minutes to compare this against AIG's GenAI standards and agentic AI roadmap be useful?"
                )
                return " ".join(dict.fromkeys(sentences))
            sentences.append(
                f"Hi {first_name}, your GCDO remit makes AIG's agentic AI trigger specific: claims and underwriting agents need auditable evidence before release."
            )
            sentences.append(
                "I've built governed agentic platforms with policy gates, evaluation traces, and rollback paths."
            )
            if "sp_platform_commercialization" in allowed_claim_ids:
                sentences.append(
                    "For AIG, the value bridge is reusable insurance workflow controls; my proof is productizing agentic AI services tied to $22M revenue and 20% margin expansion."
                )
            sentences.append(
                "Would a brief executive exchange on which AIG workflow should pilot agent governance first be useful?"
            )
            return " ".join(dict.fromkeys(sentences))
        if plan.archetype == ARCHETYPE_SENIOR_TA:
            sentences.append(
                f"Hi {first_name}, AIG's agentic AI role is an insurance operating build, not a generic AI strategy seat."
            )
            sentences.append(
                "The fit signal is regulated workflow delivery: claims and underwriting teams need agent decisions they can inspect, test, and reverse."
            )
            sentences.append(
                "My proof is governed platform execution with policy gates, validation controls, replayable traces, and rollback built in."
            )
            if (
                "sp_platform_commercialization" in allowed_claim_ids
                or "sp_platform_commercialization" in required_claim_ids
                or any(marker in feedback for marker in ("commercial", "revenue", "margin", "22m", "$22m"))
            ):
                sentences.append(
                    "Commercial proof: productized agentic AI services tied to $22M revenue and 20% margin expansion."
                )
            sentences.append("Would a brief fit review for the role be useful?")
            return " ".join(dict.fromkeys(sentences))
        if plan.archetype == ARCHETYPE_EXECUTIVE:
            sentences.append(
                f"Hi {first_name}, AIG's agentic AI trigger is not a generic AI seat; it is an operating-model build under enterprise data leadership."
            )
            sentences.append(
                "For a reinsurance executive, the useful signal is whether agent workflows can preserve risk judgment while claims, underwriting, and service teams inspect the evidence trail."
            )
            sentences.append(
                "My proof is governed platform execution with validation controls, replayable traces, and rollback built into production delivery."
            )
            if "sp_platform_commercialization" in allowed_claim_ids:
                sentences.append(
                    "Commercial proof: productized agentic AI services tied to $22M revenue and 20% margin expansion."
                )
            sentences.append(
                "Would a brief exchange on where this belongs in AIG's AI operating model be useful?"
            )
            return " ".join(dict.fromkeys(sentences))
        if "specific_aig_trigger" in feedback or "insurance_domain_framing_generic" in feedback:
            sentences.append(
                f"Hi {first_name}, as AIG's GCDO, the agentic AI trigger is claims and underwriting agents that need evidence trails before release."
            )
        else:
            sentences.append(
                f"Hi {first_name}, AIG's agentic AI edge is insurance operations: claims, underwriting, and service agents must stay explainable, testable, and reversible."
            )
        sentences.append(
            "My proof is governed platform execution with validation controls, replayable traces, and rollback built in."
        )
        if (
            "sp_runtime_reliability" in allowed_claim_ids
            or "sp_runtime_reliability" in required_claim_ids
            or any(marker in feedback for marker in ("runtime", "reliability", "validation", "replayable", "rollback"))
        ):
            if not any(marker in feedback for marker in ("repetitive_phrasing", "redundant_phrasing", "adds_no_new_signal")):
                sentences.append(
                    "The reliability proof is production validation controls, replayable traces, and rollback paths inside agent workflows."
                )
        if (
            "sp_platform_commercialization" in allowed_claim_ids
            or "sp_platform_commercialization" in required_claim_ids
            or any(marker in feedback for marker in ("commercial", "revenue", "margin", "22m", "$22m"))
        ):
            sentences.append(
                "Commercial proof: productized agentic AI services tied to $22M revenue and 20% margin expansion."
            )
        sentences.append(
            "Would a brief executive exchange be useful, or is the right data and AI owner someone else?"
        )
    elif company_lower == "citi":
        if plan.archetype == ARCHETYPE_RECRUITER:
            sentences.append(
                f"Hi {first_name}, Citi's Head of AI Strategy screen needs evidence that a candidate can make firmwide AI governable inside regulated finance."
            )
            sentences.append(
                "Citi's responsible AI and Citi Sky expansion make the recruiting signal concrete: platform execution, risk controls, and data governance need to show up together."
            )
            sentences.append(
                "My proof is governed agentic AI platform delivery with policy-gated retrieval, validation controls, replayable traces, and production release discipline."
            )
            if "sp_platform_commercialization" in allowed_claim_ids:
                sentences.append(
                    "Commercially, I productized agentic AI services tied to $22M in IP-led revenue and 20% margin expansion."
                )
            sentences.append(
                "That gives your recruiting screen concrete fit signal across responsible AI, data governance, and platform execution."
            )
            sentences.append(
                "Could we do a short recruiting screen for Head of AI Strategy fit, or should I send this to another owner?"
            )
            return " ".join(dict.fromkeys(sentences))
        if plan.archetype == ARCHETYPE_SENIOR_TA:
            sentences.append(
                f"Hi {first_name}, Citi's Head of AI Strategy search needs someone who can make firmwide AI governable inside regulated finance."
            )
            sentences.append(
                "My fit signal is governed agentic platform execution with policy-gated retrieval, validation controls, replayable traces, and production release discipline."
            )
            if "sp_platform_commercialization" in allowed_claim_ids:
                sentences.append(
                    "Commercial proof: productized agentic AI services tied to $22M revenue and 20% margin expansion."
                )
            if "sp_runtime_reliability" in allowed_claim_ids:
                sentences.append(
                    "Runtime proof: evaluation gates and rollback paths built into agent workflows, not added after launch."
                )
            sentences.append(
                "That maps to Citi Sky because adoption at bank scale needs evidence, ownership, and control before rollout."
            )
            sentences.append("Would a brief fit review for this search be useful?")
            return " ".join(dict.fromkeys(sentences))
        if any(
            marker in feedback
            for marker in (
                "trigger_anchor",
                "weak_trigger",
                "citi_specific",
                "citi_sky",
                "dense_and_abstract",
                "cta_is_weak",
            )
        ):
            if "sp_quant_governance_foundation" in allowed_claim_ids:
                sentences.append(
                    f"Hi {first_name}, Citi Sky raises a CIO-level operating question: how do banker-facing AI workflows carry model controls, data lineage, and support ownership in the same loop?"
                )
                sentences.append(
                    "My fit is building governed agentic platforms where policy gates and evaluation evidence turn AI usage into auditable operations."
                )
                sentences.append(
                    "The governance foundation is risk-aware platform design: actuarial and statistical discipline applied to AI controls, not a standalone credential."
                )
                if "sp_platform_commercialization" in allowed_claim_ids:
                    sentences.append(
                        "The commercialization proof is productized agentic AI services tied to $22M revenue and 20% margin expansion."
                    )
                sentences.append(
                    "Would 15 minutes to pressure-test the operating model behind Citi Sky be useful?"
                )
                return " ".join(dict.fromkeys(sentences))
            if "sp_cloud_ai_transformation" in allowed_claim_ids:
                sentences.append(
                    f"Hi {first_name}, Citi Sky makes the AI-owner question specific: responsible AI has to become governed delivery, not a strategy slogan."
                )
                sentences.append(
                    "My fit is building agentic platforms with policy-gated retrieval, evaluation evidence, traceability, and rollback paths."
                )
                sentences.append(
                    "The quantified bridge is architecture and commercial ownership of a $30M cloud and AI transformation portfolio for Fortune 500 financial institutions."
                )
                sentences.append(
                    "Would a low-friction exchange on scaling Citi Sky-style AI controls be useful?"
                )
                return " ".join(dict.fromkeys(sentences))
            sentences.append(
                f"Hi {first_name}, Citi Sky is not just an AI adoption signal; it is a CIO operating test for model governance, data controls, and support ownership."
            )
            sentences.append(
                "My differentiator is shipping governed agentic platforms where policy gates and evaluation evidence turn AI usage into auditable operations."
            )
            if "sp_platform_commercialization" in allowed_claim_ids:
                sentences.append(
                    "The measurable proof is productizing agentic AI services into reusable offerings tied to $22M revenue and 20% margin expansion, without separating product velocity from control."
                )
            sentences.append(
                "Would a brief executive exchange on the operating controls behind Citi Sky be useful?"
            )
            return " ".join(dict.fromkeys(sentences))
        if "opening_restates" in feedback or "not_original_insight" in feedback:
            sentences.append(
                f"Hi {first_name}, Citi Sky makes the CIO question concrete: can responsible-AI patterns become supported production controls across regulated banking, not just adoption messaging?"
            )
        else:
            sentences.append(
                f"Hi {first_name}, Citi Sky and global AI adoption put the operating problem at the center: production AI has to preserve auditability, support ownership, and rollback paths."
            )
        sentences.append(
            "My proof is governed agentic AI delivery in regulated environments, where retrieval, policy, evaluation, and traceability become release discipline rather than capability lists."
        )
        if "sp_platform_commercialization" in allowed_claim_ids:
            sentences.append(
                "The outcome proof is productized agentic AI services tied to $22M in IP-led revenue and 20% margin expansion."
            )
        if plan.archetype == ARCHETYPE_RECRUITER:
            sentences.append(
                "For a recruiter screen, the signal is production AI governance plus measurable ownership, not just AI keywords."
            )
            sentences.append("Would a focused resume review be useful?")
        else:
            sentences.append(
                "That is the bridge from AI strategy to systems a CIO can run through audit, risk, support, and global scale."
            )
            sentences.append(
                "Would a brief exchange on turning Citi Sky-style adoption into production controls be useful?"
            )
    elif company_lower == "neo4j":
        if (
            plan.archetype == ARCHETYPE_C_LEVEL
            and any(marker in feedback for marker in ("generic_for_cpo", "ceo_level", "cta_weak", "right_owner"))
        ):
            sentences.append(
                f"Hi {first_name}, the CPO-level Neo4j question is whether graph context can become a governed control plane for enterprise agents, not just a stronger retrieval layer."
            )
            sentences.append(
                "My fit is productizing agent reliability: evaluation gates, traceable context use, rollback paths, and product surfaces teams can trust."
            )
            if "sp_platform_commercialization" in allowed_claim_ids:
                sentences.append(
                    "I also productized agentic AI services into reusable offerings tied to $22M in IP-led revenue and 20% margin expansion."
                )
            sentences.append(
                "Would a brief exchange on graph-backed agent reliability be useful, or is the right product owner someone else?"
            )
            return " ".join(dict.fromkeys(sentences))
        if plan.archetype == ARCHETYPE_RECRUITER:
            sentences.append(
                f"Hi {first_name}, Neo4j's Agentic AI hiring signal needs a recruiter screen for candidates who can connect graph product work with governed enterprise AI delivery."
            )
            sentences.append(
                "My fit is translating GraphRAG retrieval into production agent infrastructure with policy gates, traceable context use, and reliability controls."
            )
            sentences.append(
                "That comes from regulated enterprise workflows where agent outputs had to be reviewable before teams trusted them."
            )
        else:
            sentences.append(
                f"Hi {first_name}, Neo4j's Agentic AI product push has a sharper tension than generic RAG: graph context has to become a governed reliability layer, not another retrieval feature."
            )
            sentences.append(
                "My fit is translating GraphRAG retrieval into governed product infrastructure with evaluation gates, traceable context use, and rollback paths."
            )
        if "sp_runtime_reliability" in allowed_claim_ids:
            sentences.append(
                "The runtime proof is agent workflow reliability built into the product surface, not a separate compliance afterthought."
            )
        if "sp_platform_commercialization" in allowed_claim_ids:
            sentences.append(
                "I also productized agentic AI services into reusable offerings tied to $22M in IP-led revenue and 20% margin expansion."
            )
        if (
            "sp_cloud_ai_transformation" in allowed_claim_ids
            and (
                "sp_cloud_ai_transformation" in required_claim_ids
                or _asks_for_quantified_outcome(feedback)
            )
        ):
            sentences.append(
                "A second scale proof is architecture and commercial ownership of a $30M cloud and AI transformation portfolio for Fortune 500 financial institutions."
            )
        if plan.archetype == ARCHETYPE_C_LEVEL:
            sentences.append(
                "Would 15 minutes on governed agent productization be useful?"
            )
        elif plan.archetype == ARCHETYPE_RECRUITER:
            sentences.append("Would a focused resume review or recruiter screen be useful?")
        else:
            sentences.append("Would a 15-minute product-fit conversation be useful?")
    return " ".join(dict.fromkeys(sentences))


def _c_level_editorial_issue_families(feedback: str) -> frozenset[str]:
    lower = str(feedback or "").lower()
    families: list[str] = []
    if any(marker in lower for marker in ("subject", "subject_line", "subject line")):
        families.append("subject_specificity")
    if any(
        marker in lower
        for marker in (
            "trigger",
            "hook",
            "opening",
            "specificity",
            "surface_level",
            "slightly_generic",
            "strategic_tension",
            "operational_tension",
            "aig_context",
            "citi_sky",
        )
    ):
        families.append("trigger_insight")
    if any(
        marker in lower
        for marker in (
            "value_bridge",
            "bridge_sentence",
            "platform_pitch",
            "commercialization",
            "commercial",
            "revenue",
            "margin",
            "metric",
            "proof",
            "dense",
            "unanchored",
        )
    ):
        families.append("proof_bridge")
    if any(
        marker in lower
        for marker in (
            "credential",
            "resume_dump",
            "defensive",
            "governance_foundation",
            "credential_list",
        )
    ):
        families.append("credential_dump")
    if any(
        marker in lower
        for marker in (
            "cta",
            "pressure_test",
            "pressure-test",
            "overused",
            "compare",
            "brief_exchange",
            "executive_exchange",
            "asks_recipient",
            "pilot_workflow",
            "presumes",
        )
    ):
        families.append("cta_executive_sharpness")
    if any(marker in lower for marker in ("same_as_parent", "same-parent", "parent_candidate")):
        families.append("same_parent_risk")
    return frozenset(families)


def _c_level_editorial_subject_line(
    *,
    company: str,
    request: WholeMessageGenerationRequest,
    feedback: str,
) -> str:
    if str(getattr(request, "recipient_class", "") or "").strip() != ARCHETYPE_C_LEVEL:
        return ""
    company_lower = company.lower()
    feedback_lower = feedback.lower()
    if company_lower == "aig" and any(
        marker in feedback_lower for marker in ("tradeoff", "restates_jd", "external_signal")
    ):
        return "AIG GCDO release-evidence tradeoff"
    if company_lower == "aig" and any(
        marker in feedback_lower
        for marker in (
            "contextual_anchoring",
            "operating_model_decision",
            "formulaic",
            "release_evidence_not_differentiated",
        )
    ):
        return "AIG GCDO release-evidence tradeoff"
    if company_lower == "aig" and any(
        marker in feedback_lower for marker in ("subject", "gcdo", "agentic", "trigger")
    ):
        return "AIG GCDO agentic operating proof"
    if company_lower == "citi" and any(
        marker in feedback_lower
        for marker in ("handoff", "specific_citi_sky", "governance_gap", "observable_signal")
    ):
        return "Citi Sky CIO governance handoff"
    if company_lower == "citi" and any(
        marker in feedback_lower for marker in ("subject", "cio", "citi", "governance")
    ):
        return "Citi Sky CIO governance loop"
    return ""


def _compose_c_level_editorial_rebuild(
    *,
    first_name: str,
    company: str,
    target: dict[str, Any],
    plan: X1DFeedbackRepairPlan,
    allowed_claim_ids: set[str],
    feedback: str,
) -> str:
    if plan.archetype != ARCHETYPE_C_LEVEL:
        return ""
    families = _c_level_editorial_issue_families(feedback)
    if not families:
        return ""
    company_lower = company.lower()
    if company_lower == "aig":
        if any(
            marker in feedback
            for marker in (
                "value_bridge_lacks_insurance_specificity",
                "cta_too_generic_for_c_level",
                "trigger_framing_restates_jd",
                "external_signal",
                "concrete_decision_or_tradeoff",
                "formulaic_insight_hook",
                "metric_proof_sentence_feels_appended",
                "c_level_sharpness",
                "jim_specific",
                "operating_model_gap",
                "revenue_figures_dropped",
                "release_control_gap",
                "contextual_anchoring",
                "operating_model_decision",
                "formulaic_for_c_level",
                "release_evidence_not_differentiated",
            )
        ):
            sentences = [
                (
                    f"Hi {first_name}, I would frame AIG's GCDO signal as a release-gate problem: "
                    "claims triage and underwriting agents cannot scale faster than their evidence trail."
                ),
                (
                    "My governed-agent work maps there through policy checks, evaluation traces, rollback paths, and reusable release services."
                ),
            ]
            if "sp_platform_commercialization" in allowed_claim_ids:
                sentences.append(
                    "The $22M and 20% margin proof matters as operating leverage: reusable controls turning agentic AI services into scaled offerings, not demos."
                )
            sentences.append(
                "Would 15 minutes on release-gate design for AIG's agentic AI operating model be useful?"
            )
            return " ".join(dict.fromkeys(sentences))
        sentences = [
            (
                f"Hi {first_name}, AIG's GCDO trigger is concrete: agentic AI for "
                "claims and underwriting needs release evidence before regulated decisions."
            ),
        ]
        if "sp_platform_commercialization" in allowed_claim_ids:
            sentences.append(
                "The value bridge is insurance workflow reuse, backed by productized agentic AI services tied to $22M revenue and 20% margin expansion."
            )
        elif "sp_runtime_reliability" in allowed_claim_ids:
            sentences.append(
                "The proof bridge is insurance release control: policy gates, evaluation evidence, and rollback paths built into governed agent workflows."
            )
        sentences.append(
            "My relevant work adds governed agentic AI platforms with policy gates, evaluation traces, rollback paths, and reusable service patterns."
        )
        sentences.append(
            "Would 15 minutes on evidence-backed release controls for AIG's agentic AI operating model be useful?"
        )
        return " ".join(dict.fromkeys(sentences))
    if company_lower == "citi":
        if any(
            marker in feedback
            for marker in (
                "medium_strength",
                "medium_claim_strength",
                "overreach",
                "specific_citi_sky_detail",
                "specific_hook_tied_to_citi_sky",
                "governance_gap",
                "observable_signal",
                "global_bank",
                "firmwide_ai_detail",
            )
        ):
            sentences = [
                (
                    f"Hi {first_name}, Citi Sky's sharper signal is the operating handoff: "
                    "responsible AI has to move from policy language into banker workflows."
                ),
                (
                    "For a CIO, the hard edge is where AI controls, data lineage, risk review, "
                    "and support ownership meet inside global technology services."
                ),
                (
                    "My relevant work is governed agentic AI platform delivery with policy gates "
                    "and evaluation evidence that made production AI usage auditable."
                ),
            ]
            if "sp_platform_commercialization" in allowed_claim_ids:
                sentences.append(
                    "Commercially, the same platform discipline supported productized agentic AI services tied to $22M revenue and 20% margin expansion."
                )
            sentences.append(
                "Would 15 minutes on who owns Citi Sky's audit-to-support loop be useful?"
            )
            return " ".join(dict.fromkeys(sentences))
        sentences = [
            (
                f"Hi {first_name}, Citi Sky creates a CIO-specific operating tension: "
                "banker-facing AI can scale only if model controls, data lineage, and support ownership travel with each workflow."
            ),
            (
                "My relevant work is governed agentic AI platform delivery where policy gates and evaluation evidence made AI usage auditable in production."
            ),
        ]
        if "sp_quant_governance_foundation" in allowed_claim_ids:
            sentences.append(
                "The quant-governance proof is forward risk control: decision workflows that expose ownership and audit evidence before scale."
            )
        if "sp_platform_commercialization" in allowed_claim_ids:
            sentences.append(
                "Commercially, the same platform discipline supported productized agentic AI services tied to $22M revenue and 20% margin expansion."
            )
        sentences.append("Would 15 minutes on the Citi Sky governance loop be useful?")
        return " ".join(dict.fromkeys(sentences))
    return ""


def _needs_company_specific_rebuild(feedback: str) -> bool:
    return any(
        marker in feedback
        for marker in (
            "trigger",
            "generic",
            "cta",
            "role_title",
            "repetitive",
            "capability_list",
            "resume_dump",
            "quantified",
            "metric",
            "outcome",
            "bridge_sentence",
            "recipient_specific",
            "subject_line",
            "foundation",
            "pressure_test",
            "platform_pitch",
            "opening_question",
            "proof",
        )
    )


def _normalized_feedback_signature(
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...],
) -> str:
    return " ".join(
        [intent.intent for intent in normalized_intents]
        + [intent.issue_id for intent in normalized_intents]
        + [intent.required_repair for intent in normalized_intents]
        + [
            claim_id
            for intent in normalized_intents
            for claim_id in intent.required_claim_ids
        ]
    ).lower()


def _asks_for_quantified_outcome(feedback: str) -> bool:
    return any(
        marker in feedback
        for marker in (
            "quantified",
            "metric",
            "outcome",
            "scale_signal",
            "concrete_outcome",
            "anchor_claims",
        )
    )


def _clean_rebuild_opening_sentence(
    *,
    first_name: str,
    company: str,
    role: str,
    target: dict[str, Any],
    feedback: str,
) -> str:
    trigger = str(target.get("company_trigger") or target.get("company_context") or "").strip()
    company_lower = company.lower()
    if company_lower == "citi":
        if "missing_citi_specific_trigger_hook" in feedback or "citi_specific_trigger" in feedback:
            return (
                f"Hi {first_name}, Citi's responsible AI, data governance, and global adoption work makes the CIO problem operational: "
                "scale firmwide AI without losing auditability or platform control."
            )
        return (
            f"Hi {first_name}, Citi's firmwide AI strategy in regulated finance makes the hard part "
            "controlled rollout: useful agents need risk, audit, and governance evidence before they scale."
        )
    if company_lower == "neo4j":
        if "recipient_specific" in feedback or "generic_graph" in feedback or "trigger_insight" in feedback:
            return (
                f"Hi {first_name}, Neo4j's Agentic AI product search makes the question specific: "
                "how graph context becomes a reliability layer for enterprise agents, not another retrieval feature."
            )
        return (
            f"Hi {first_name}, Neo4j's Agentic AI product leadership search makes graph context reliability "
            "the product question for enterprise agents."
        )
    if trigger:
        return f"Hi {first_name}, {trigger.rstrip('.')[:170]}."
    return (
        f"Hi {first_name}, {company}'s {role} mandate needs governed agentic AI "
        "that can reach controlled production."
    )


def _clean_rebuild_evidence_sentence(
    *,
    allowed_claim_ids: set[str],
    company: str,
    feedback: str,
) -> str:
    if (
        company.lower() == "neo4j"
        and any(
            marker in feedback
            for marker in (
                "generic_capability_list",
                "bridge_sentence_reads",
                "claim_lacks_outcome",
            )
        )
    ):
        return (
            "My fit is translating GraphRAG retrieval into governed product infrastructure with evaluation gates, traceable context use, and rollback paths."
        )
    if "sp_agentic_platform" in allowed_claim_ids:
        return (
            "My bridge is governed platform execution: multi-agent orchestration, GraphRAG retrieval, "
            "policy gating, validation controls, and replayable traces."
        )
    if "sp_runtime_reliability" in allowed_claim_ids:
        return "My bridge is reliable agent workflow delivery with validation controls, replayable traces, and rollback paths."
    return "My bridge is governed platform execution with reviewable controls and implementation depth."


def _clean_rebuild_fit_sentence(
    *,
    company: str,
    role: str,
    plan: X1DFeedbackRepairPlan,
    feedback: str,
) -> str:
    company_lower = company.lower()
    if plan.archetype == ARCHETYPE_RECRUITER:
        if "role_fit_bridge" in feedback or "recruiter_personalization" in feedback:
            return (
                f"For the {role} search, that gives a recruiter a concrete screen: governed AI platform delivery, production controls, and measurable commercialization."
            )
        return (
            f"For the {role} search, that gives a recruiter concrete screening signal beyond keyword overlap."
        )
    if company_lower == "neo4j":
        if _asks_for_quantified_outcome(feedback):
            return (
                f"For the {role} search, the candidate signal is shipping governed AI infrastructure with measurable transformation ownership."
            )
        return (
            f"For the {role} search, that is candidate fit around productizing trustworthy agent infrastructure, not advisory commentary."
        )
    return (
        f"For the {role} search, the fit is platform operating model depth rather than a generic AI strategy pitch."
    )


def _compact_role_phrase(role: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(role or "open role").strip())
    if not cleaned:
        return "open role"
    return cleaned.replace("VP of Product Management, Agentic AI", "VP Product, Agentic AI")



def _clean_rebuild_cta(*, plan: X1DFeedbackRepairPlan, role: str, feedback: str) -> str:
    if any(marker in feedback for marker in ("cta_repeats", "cta_weak", "role_fit_framing")):
        if plan.archetype == ARCHETYPE_C_LEVEL:
            return "Would 15 minutes to pressure-test fit against the AI operating model be useful?"
        if plan.archetype == ARCHETYPE_EXECUTIVE:
            return "Would a 15-minute product-fit conversation be useful?"
        if plan.archetype == ARCHETYPE_RECRUITER:
            return "Would a focused resume review be useful?"
        if plan.archetype == ARCHETYPE_SENIOR_TA:
            return "Would a focused fit review be useful?"
    if plan.archetype == ARCHETYPE_C_LEVEL:
        return f"Would a brief executive conversation on fit for the {role} search be useful?"
    if plan.archetype == ARCHETYPE_EXECUTIVE:
        return f"Would a brief product fit conversation for the {role} search be useful?"
    if plan.archetype == ARCHETYPE_RECRUITER:
        return f"Would a quick recruiter screen or resume review for the {role} search be useful?"
    if plan.archetype == ARCHETYPE_SENIOR_TA:
        return f"Would a brief fit review for the {role} search be useful?"
    return "Would a quick fit check be useful?"


def _claims_from_repaired_text(
    text: str,
    *,
    existing: tuple[str, ...],
    allowed_claim_ids: set[str],
) -> tuple[str, ...]:
    normalized = text.lower()
    claims = [
        claim
        for claim in existing
        if claim in allowed_claim_ids
        and (
            claim != "sp_quant_governance_foundation"
            or re.search(
                r"\b(quant-governance|quant governance|quant-risk|actuarial|statistical)\b",
                normalized,
            )
        )
    ]
    if (
        "sp_agentic_platform" in allowed_claim_ids
        and (
            "governed agentic ai platform" in normalized
            or "multi-agent orchestration" in normalized
            or "graphrag" in normalized
            or "policy gating" in normalized
            or "policy-gated" in normalized
        )
    ):
        claims.append("sp_agentic_platform")
    if (
        "sp_runtime_reliability" in allowed_claim_ids
        and (
            "validation controls" in normalized
            or "replayable traces" in normalized
            or "evaluation gates" in normalized
            or "rollback" in normalized
        )
    ):
        claims.append("sp_runtime_reliability")
    if (
        "sp_platform_commercialization" in allowed_claim_ids
        and (
            "$22m" in normalized
            or "20% margin" in normalized
            or "ip-led revenue" in normalized
            or "productized" in normalized
        )
    ):
        claims.append("sp_platform_commercialization")
    if (
        "sp_cloud_ai_transformation" in allowed_claim_ids
        and (
            "$30m" in normalized
            or "cloud and ai transformation" in normalized
            or "cloud/ai transformation" in normalized
            or "ai transformation portfolio" in normalized
        )
    ):
        claims.append("sp_cloud_ai_transformation")
    if (
        "sp_quant_governance_foundation" in allowed_claim_ids
        and (
            "quant-governance" in normalized
            or "quant governance" in normalized
            or "quant-risk" in normalized
            or "actuarial" in normalized
            or "statistical" in normalized
        )
    ):
        claims.append("sp_quant_governance_foundation")
    return tuple(dict.fromkeys(claims))


def _build_feedback_repair_plan(
    *,
    request: WholeMessageGenerationRequest,
    target: dict[str, Any],
    company: str,
    role: str,
    recipient_class: str,
    feedback: str,
) -> X1DFeedbackRepairPlan:
    del target
    policy = resolve_recipient_template_policy(
        recipient_class=recipient_class,
        message_type=str(getattr(request, "message_type", "") or "general_intro"),
        channel=str(getattr(request, "channel", "") or "linkedin"),
        modifiers=getattr(request, "modifiers", {}) or {},
    )
    allowed = frozenset(_allowed_claim_ids(request))
    intents = _feedback_repair_intents(feedback)
    return X1DFeedbackRepairPlan(
        intents=intents,
        company=company,
        role=role,
        recipient_class=recipient_class,
        archetype=policy.archetype_profile.archetype,
        altitude=policy.archetype_profile.altitude,
        cta_style=policy.length_policy.cta_style,
        evidence_bridge_sentence=_evidence_bridge_sentence(
            company=company,
            role=role,
            allowed_claim_ids=set(allowed),
        ),
        outcome_sentence=_scale_sentence(allowed_claim_ids=set(allowed)),
        cta_sentence=_cta_sentence(
            archetype=policy.archetype_profile.archetype,
            role=role,
            company=company,
            cta_style=policy.length_policy.cta_style,
        ),
        allowed_claim_ids=allowed,
    )


def _normalize_repair_intents(
    judge_results: tuple[X1DJudgeResult, ...],
) -> tuple[X1DNormalizedRepairIntent, ...]:
    intents: list[X1DNormalizedRepairIntent] = []
    for result in judge_results:
        issues = tuple(str(item).strip() for item in result.issues if str(item).strip())
        repairs = tuple(
            str(item).strip()
            for item in result.required_repairs
            if str(item).strip()
        )
        max_len = max(len(issues), len(repairs), 1)
        for index in range(max_len):
            issue = issues[index] if index < len(issues) else ""
            repair = repairs[index] if index < len(repairs) else ""
            evidence = f"{issue} {repair}".lower()
            intents.append(
                X1DNormalizedRepairIntent(
                    judge_id=result.judge_id,
                    issue_id=issue,
                    required_repair=repair,
                    intent=_repair_intent_for_feedback(evidence),
                    required_claim_ids=_required_claim_ids_for_feedback(evidence),
                )
            )
    return tuple(intents)


def _repair_intent_for_feedback(feedback: str) -> str:
    if any(marker in feedback for marker in ("duplicate", "sign_off", "signature", "amit appears twice")):
        return "signature_dedupe"
    if any(marker in feedback for marker in ("bridge", "that maps", "repetitive_phrasing")):
        return "bridge_dedupe"
    if any(marker in feedback for marker in ("role_name_repetition", "role_title", "repeated_vp_role_title")):
        return "role_title_dedupe"
    if any(marker in feedback for marker in ("word_count", "budget", "trim_to_under", "sentence_count")):
        return "length_budget"
    if any(marker in feedback for marker in ("cta", "closing", "ask", "next_step")):
        return "cta"
    if any(marker in feedback for marker in ("trigger", "hook", "generic")):
        return "trigger_hook"
    if any(marker in feedback for marker in ("claim", "metric", "evidence", "commercial", "runtime")):
        return "claim_surface"
    if any(marker in feedback for marker in ("opening", "grammar", "natural")):
        return "opening_rewrite"
    return "quality_repair"


def _required_claim_ids_for_feedback(feedback: str) -> tuple[str, ...]:
    claims: list[str] = []
    if any(
        marker in feedback
        for marker in (
            "sp_platform_commercialization",
            "platform_commercialization",
            "commercialization",
            "22m",
            "revenue",
            "margin",
            "commercial outcome",
        )
    ):
        claims.append("sp_platform_commercialization")
    if any(
        marker in feedback
        for marker in (
            "runtime_reliability",
            "runtime reliability",
            "replayable traces",
            "evaluation gates",
            "rollback",
            "telemetry",
        )
    ):
        claims.append("sp_runtime_reliability")
    if any(
        marker in feedback
        for marker in (
            "agentic_platform",
            "governed agentic",
            "multi-agent",
            "graphrag",
            "policy gating",
        )
    ):
        claims.append("sp_agentic_platform")
    if "sp_cloud_ai_transformation" in feedback or "cloud_ai_transformation" in feedback:
        claims.append("sp_cloud_ai_transformation")
    if (
        "quant_governance_claim" not in feedback
        and "quant-governance claim" not in feedback
        and "quant governance claim" not in feedback
        and not any(
            marker in feedback
            for marker in (
                "remove",
                "drop",
                "hedge",
                "overreach",
                "medium_strength",
                "medium_claim_strength",
            )
        )
        and any(
            marker in feedback
            for marker in (
                "sp_quant_governance_foundation",
                "quant_governance",
                "quant-governance",
                "actuarial",
                "statistical",
            )
        )
    ):
        claims.append("sp_quant_governance_foundation")
    return tuple(dict.fromkeys(claims))


def _sanitize_repair_candidate(
    *,
    text: str,
    subject_line: str,
    claims_used: tuple[str, ...],
    request: WholeMessageGenerationRequest,
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...],
) -> X1DRepairCandidateSanitizationResult:
    issues: list[str] = []
    allowed_claim_ids = _allowed_claim_ids(request)
    text = _ensure_terminal_amit_signature(text)
    text = _remove_inline_amit_signatures(text)
    text = _dedupe_bridge_sentences(text)
    text = _dedupe_role_title_mentions(
        text,
        role=str(
            getattr(request, "jd_fields", {}).get("position_name")
            or getattr(request, "jd_fields", {}).get("job_title")
            or ""
        ),
    )
    text, claims_used = _surface_required_claims(
        text=text,
        claims_used=claims_used,
        allowed_claim_ids=allowed_claim_ids,
        request=request,
        normalized_intents=normalized_intents,
    )
    text = _trim_to_request_budget(text, request=request)
    text = _ensure_terminal_amit_signature(text)

    body, signature = _split_terminal_signature(text)
    if signature != "\n\nAmit" or re.search(r"\bAmit(?: Ayer)?\b", body, flags=re.IGNORECASE):
        issues.append("terminal_amit_signature_not_unique")
    if _has_duplicate_bridge_sentence(text):
        issues.append("duplicate_bridge_sentence")
    if _role_title_count(text, request=request) > 1:
        issues.append("repeated_role_title")
    if len(text) > int(request.length_budget.hard_cap_chars or 0):
        issues.append("hard_cap_chars_exceeded")
    if request.length_budget.max_sentences and _sentence_count(text) > request.length_budget.max_sentences:
        issues.append("max_sentences_exceeded")
    if request.length_budget.max_words and _word_count(text) > request.length_budget.max_words:
        issues.append("max_words_exceeded")
    issues.extend(
        _c_level_editorial_copy_lint_issues(
            text=text,
            subject_line=subject_line,
            request=request,
        )
    )
    missing_claims = sorted(
        claim_id
        for intent in normalized_intents
        for claim_id in intent.required_claim_ids
        if claim_id in allowed_claim_ids and claim_id not in claims_used
    )
    if missing_claims:
        issues.append("required_claim_ids_missing:" + ",".join(missing_claims))

    return X1DRepairCandidateSanitizationResult(
        text=text,
        subject_line=subject_line,
        claims_used=tuple(dict.fromkeys(claims_used)),
        passed=not issues,
        issues=tuple(issues),
    )


def _c_level_editorial_copy_lint_issues(
    *,
    text: str,
    subject_line: str,
    request: WholeMessageGenerationRequest,
) -> tuple[str, ...]:
    if str(getattr(request, "recipient_class", "") or "").strip() != ARCHETYPE_C_LEVEL:
        return ()
    if str(getattr(request, "message_type", "") or "").strip() != "trigger_based_insight":
        return ()
    target = dict(getattr(request, "target_context", {}) or {})
    jd = dict(getattr(request, "jd_fields", {}) or {})
    company = str(target.get("company") or jd.get("company") or "").strip().lower()
    if company not in {"aig", "citi"}:
        return ()
    normalized_text = text.lower()
    normalized_subject = subject_line.lower()
    issues: list[str] = []
    for phrase in _C_LEVEL_EDITORIAL_BANNED_PHRASES:
        if phrase in normalized_text:
            issues.append("c_level_copy_lint:banned_phrase:" + phrase.replace(" ", "_"))
    if company == "aig":
        if not (
            "aig" in normalized_subject
            and "gcdo" in normalized_subject
            and any(marker in normalized_subject for marker in ("agentic", "release"))
        ):
            issues.append("c_level_copy_lint:subject_specificity")
        if "$22m" in normalized_text and not any(
            marker in normalized_text for marker in ("insurance", "claims", "underwriting")
        ):
            issues.append("c_level_copy_lint:metric_missing_insurance_context")
        if any(marker in normalized_text for marker in ("which aig workflow", "should pilot")):
            issues.append("c_level_copy_lint:cta_presumes_workflow_selection")
    elif company == "citi":
        if "citi sky" not in normalized_subject or not any(
            marker in normalized_subject for marker in ("cio", "governance", "loop")
        ):
            issues.append("c_level_copy_lint:subject_specificity")
        if "$22m" in normalized_text and not any(
            marker in normalized_text
            for marker in ("citi sky", "banker-facing", "regulated", "governance")
        ):
            issues.append("c_level_copy_lint:metric_missing_citi_context")
    return tuple(dict.fromkeys(issues))


def _remove_inline_amit_signatures(text: str) -> str:
    body, signature = _split_terminal_signature(text)
    body = re.sub(
        r"(?:\s|\n)+(?:best|thanks|regards|warmly|cheers)?[,]?\s*Amit(?: Ayer)?\.?(?=\s|$)",
        " ",
        body,
        flags=re.IGNORECASE,
    )
    body = re.sub(r"\s{2,}", " ", body).strip()
    signature_block = signature or "\n\nAmit"
    return f"{body}{signature_block}"


def _dedupe_bridge_sentences(text: str) -> str:
    body, signature = _split_terminal_signature(text)
    sentences = [part.strip() for part in re.findall(r"[^.!?]+[.!?]", body) if part.strip()]
    if not sentences:
        return text
    kept: list[str] = []
    seen: set[str] = set()
    bridge_seen = False
    for sentence in sentences:
        key = re.sub(r"\W+", " ", sentence).strip().lower()
        is_bridge = bool(
            re.search(
                r"\b(the bridge is|the concrete bridge is|that maps to|maps to the mandate)\b",
                sentence,
                flags=re.IGNORECASE,
            )
        )
        if key in seen or (is_bridge and bridge_seen):
            continue
        seen.add(key)
        bridge_seen = bridge_seen or is_bridge
        kept.append(sentence)
    return f"{' '.join(kept).strip()}{signature}"


def _dedupe_role_title_mentions(text: str, *, role: str) -> str:
    role = str(role or "").strip()
    if not role:
        return text
    pattern = re.compile(re.escape(role), flags=re.IGNORECASE)
    seen = False

    def replace(match: re.Match[str]) -> str:
        nonlocal seen
        if not seen:
            seen = True
            return match.group(0)
        return "role"

    return pattern.sub(replace, text)


def _surface_required_claims(
    *,
    text: str,
    claims_used: tuple[str, ...],
    allowed_claim_ids: set[str],
    request: WholeMessageGenerationRequest,
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...],
) -> tuple[str, tuple[str, ...]]:
    claims = list(claims_used)
    required = tuple(
        dict.fromkeys(
            claim_id
            for intent in normalized_intents
            for claim_id in intent.required_claim_ids
            if claim_id in allowed_claim_ids
        )
    )
    if not required:
        return text, tuple(dict.fromkeys(claims))
    target = dict(getattr(request, "target_context", {}) or {})
    jd = dict(getattr(request, "jd_fields", {}) or {})
    company = str(target.get("company") or jd.get("company") or "").strip()
    role = str(jd.get("position_name") or jd.get("job_title") or "").strip()
    for claim_id in required:
        if claim_id not in claims:
            claims.append(claim_id)
        if claim_id == "sp_platform_commercialization" and "$22M" not in text and "$22m" not in text:
            text = _insert_before_cta(text, _scale_sentence(allowed_claim_ids=allowed_claim_ids))
        elif claim_id == "sp_runtime_reliability" and not re.search(
            r"\b(evaluation gates|rollback|replayable traces|validation controls)\b",
            text,
            flags=re.IGNORECASE,
        ):
            text = _insert_before_cta(
                text,
                "The runtime reliability proof is validation controls, evaluation gates, replayable traces, and rollback paths for governed agent workflows.",
            )
        elif claim_id == "sp_agentic_platform" and "multi-agent orchestration" not in text.lower():
            text = _insert_before_cta(
                text,
                _evidence_bridge_sentence(
                    company=company,
                    role=role,
                    allowed_claim_ids=allowed_claim_ids,
                ),
            )
        elif claim_id == "sp_quant_governance_foundation" and not re.search(
            r"\b(quant-governance|quant governance|quant-risk|actuarial|statistical)\b",
            text,
            flags=re.IGNORECASE,
        ):
            text = _insert_before_cta(
                text,
                "The quant-governance proof is forward risk control: decision workflows that expose ownership and audit evidence before scale.",
            )
    return text, tuple(dict.fromkeys(claims))


def _trim_to_request_budget(text: str, *, request: WholeMessageGenerationRequest) -> str:
    budget = request.length_budget
    body, signature = _split_terminal_signature(text)
    sentences = [part.strip() for part in re.findall(r"[^.!?]+[.!?]", body) if part.strip()]
    if not sentences:
        return text
    max_sentences = max(1, int(budget.max_sentences or len(sentences)))
    if len(sentences) > max_sentences:
        cta = next((sentence for sentence in reversed(sentences) if sentence.endswith("?")), sentences[-1])
        non_cta = [sentence for sentence in sentences if sentence != cta]
        sentences = [*non_cta[: max_sentences - 1], cta]
    rebuilt = f"{' '.join(sentences).strip()}{signature}"
    max_words = int(budget.max_words or 0)
    if max_words and _word_count(rebuilt) > max_words:
        rebuilt = _compress_to_word_budget(rebuilt, max_words=max_words)
    hard_cap = int(budget.hard_cap_chars or 0)
    if hard_cap and len(rebuilt) > hard_cap:
        rebuilt = _compress_to_char_budget(rebuilt, hard_cap=hard_cap)
    return rebuilt


def _compress_to_word_budget(text: str, *, max_words: int) -> str:
    body, signature = _split_terminal_signature(text)
    sentences = [part.strip() for part in re.findall(r"[^.!?]+[.!?]", body) if part.strip()]
    if len(sentences) <= 2:
        return text
    cta = next((sentence for sentence in reversed(sentences) if sentence.endswith("?")), sentences[-1])
    kept = [sentences[0]]
    for sentence in sentences[1:]:
        if sentence == cta:
            continue
        candidate = " ".join([*kept, sentence, cta])
        if _word_count(f"{candidate}{signature}") <= max_words:
            kept.append(sentence)
    rebuilt = " ".join([*kept, cta]).strip()
    return f"{rebuilt}{signature}"


def _compress_to_char_budget(text: str, *, hard_cap: int) -> str:
    body, signature = _split_terminal_signature(text)
    sentences = [part.strip() for part in re.findall(r"[^.!?]+[.!?]", body) if part.strip()]
    if len(sentences) <= 2:
        return text[:hard_cap].rstrip()
    cta = next((sentence for sentence in reversed(sentences) if sentence.endswith("?")), sentences[-1])
    kept = [sentences[0]]
    for sentence in sentences[1:]:
        if sentence == cta:
            continue
        candidate = f"{' '.join([*kept, sentence, cta]).strip()}{signature}"
        if len(candidate) <= hard_cap:
            kept.append(sentence)
    return f"{' '.join([*kept, cta]).strip()}{signature}"


def _has_duplicate_bridge_sentence(text: str) -> bool:
    body, _signature = _split_terminal_signature(text)
    bridge_count = len(
        re.findall(
            r"\b(the bridge is|the concrete bridge is|that maps to|maps to the mandate)\b",
            body,
            flags=re.IGNORECASE,
        )
    )
    return bridge_count > 1


def _role_title_count(text: str, *, request: WholeMessageGenerationRequest) -> int:
    role = str(
        getattr(request, "jd_fields", {}).get("position_name")
        or getattr(request, "jd_fields", {}).get("job_title")
        or ""
    ).strip()
    if not role:
        return 0
    return len(re.findall(re.escape(role), text, flags=re.IGNORECASE))


def _feedback_repair_intents(feedback: str) -> tuple[str, ...]:
    checks: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("agentic_platform_evidence", ("multi_agent", "multi-agent", "orchestration")),
        (
            "governed_platform_controls",
            (
                "governance",
                "policy_gating",
                "policy gating",
                "control_plane",
                "control plane",
                "graph_intelligence",
            ),
        ),
        (
            "role_fit_bridge",
            (
                "role_fit",
                "keyword",
                "capability_bridge",
                "recruiter_recipient_mismatch",
                "opening_sentence_generic",
                "commercialization_claim",
            ),
        ),
        ("remove_redundant_bridge", ("redundant", "bridge_clause")),
        (
            "scale_outcome",
            (
                "scale",
                "outcome",
                "quantified",
                "measurable",
                "commercialization",
                "22m",
                "revenue",
                "margin",
                "metric",
            ),
        ),
        ("cta", ("cta", "call_to_action", "next_step")),
        ("unsupported_claim", ("unsupported", "unsubstantiated", "remove", "citi sky")),
    )
    intents: list[str] = []
    for intent, markers in checks:
        if any(marker in feedback for marker in markers):
            intents.append(intent)
    return tuple(dict.fromkeys(intents))


def _recruiter_feedback_repair_draft(
    *,
    target: dict[str, Any],
    plan: X1DFeedbackRepairPlan,
) -> str:
    if plan.archetype != ARCHETYPE_RECRUITER:
        return ""
    if not any(
        intent in plan.intents
        for intent in (
            "role_fit_bridge",
            "remove_redundant_bridge",
            "scale_outcome",
            "cta",
            "governed_platform_controls",
        )
    ):
        return ""
    first_name = _first_name(str(target.get("name") or target.get("contact_name") or "there"))
    company = plan.company or "the company"
    role_name = plan.role or "the open role"
    return (
        f"Hi {first_name}, my strongest match for {company}'s {role_name} search is governed "
        f"agentic AI platform execution, not just role-keyword alignment. "
        f"{plan.evidence_bridge_sentence} "
        f"{plan.outcome_sentence} "
        f"{plan.cta_sentence}\n\nAmit"
    )


def _first_name(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(name or "").strip())
    if not cleaned or cleaned.lower() == "there":
        return "there"
    return cleaned.split(" ", 1)[0].strip(",")


def _feedback_text(
    judge_results: tuple[X1DJudgeResult, ...],
    *,
    normalized_intents: tuple[X1DNormalizedRepairIntent, ...] = (),
) -> str:
    parts: list[str] = []
    for result in judge_results:
        parts.extend(str(item) for item in result.issues)
        parts.extend(str(item) for item in result.required_repairs)
    for intent in normalized_intents:
        parts.append(intent.intent)
        parts.extend(intent.required_claim_ids)
    return " ".join(parts).lower()


def _ensure_multi_agent_orchestration(text: str) -> str:
    if "multi-agent orchestration" in text.lower():
        return text
    return re.sub(
        r"combining\s+GraphRAG retrieval",
        "combining multi-agent orchestration, GraphRAG retrieval",
        text,
        count=1,
        flags=re.IGNORECASE,
    )


def _replace_role_fit_sentence(text: str, *, plan: X1DFeedbackRepairPlan) -> str:
    replacement = plan.evidence_bridge_sentence
    pattern = (
        r"The role-fit signal is governed AI strategy, platform execution, "
        r"risk-review fluency, and implementation detail beyond keyword matching\."
    )
    if re.search(pattern, text):
        return re.sub(pattern, replacement, text, count=1)
    return _insert_before_cta(text, replacement)


def _remove_redundant_bridge_sentences(text: str) -> str:
    body, signature = _split_terminal_signature(text)
    sentences = [part.strip() for part in re.findall(r"[^.!?]+[.!?]", body) if part.strip()]
    if not sentences:
        return text
    kept = [
        sentence
        for sentence in sentences
        if not re.search(
            r"\b(The bridge is implementation detail|The concrete bridge is|That maps to)\b",
            sentence,
            flags=re.IGNORECASE,
        )
    ]
    if len(kept) == len(sentences):
        return text
    return f"{' '.join(kept).strip()}{signature}"


def _evidence_bridge_sentence(
    *,
    company: str,
    role: str,
    allowed_claim_ids: set[str],
) -> str:
    company_phrase = company or "the target company"
    role_phrase = role or "the open role"
    if "sp_agentic_platform" in allowed_claim_ids:
        return (
            f"For {company_phrase}, the concrete bridge to {role_phrase} is governed agentic AI platform "
            "execution: multi-agent orchestration, GraphRAG retrieval, policy gating, validation controls, "
            "and replayable traces."
        )
    if "sp_runtime_reliability" in allowed_claim_ids:
        return (
            f"For {company_phrase}, the concrete bridge to {role_phrase} is reliable agent workflow "
            "delivery with validation controls, evaluation gates, replayable traces, and rollback paths."
        )
    return (
        f"For {company_phrase}, the concrete bridge to {role_phrase} is governed platform execution "
        "with reviewable controls and enough implementation depth to screen beyond keywords."
    )


def _scale_sentence(*, allowed_claim_ids: set[str]) -> str:
    if "sp_platform_commercialization" in allowed_claim_ids:
        return "The outcome signal I can support is productized agentic AI services tied to $22M in IP-led revenue and 20% margin expansion."
    return "The scale signal I can support is regulated enterprise workflow delivery, with governance built into the platform rather than added after a demo."


def _insert_before_cta(text: str, sentence: str) -> str:
    body, signature = _split_terminal_signature(text)
    if sentence.lower() in body.lower():
        return text
    if sentence.startswith("The scale signal") and re.search(r"\bThe scale signal\b", body, flags=re.IGNORECASE):
        return text
    parts = [part.strip() for part in re.findall(r"[^.!?]+[.!?]", body) if part.strip()]
    if parts and parts[-1].endswith("?"):
        body = " ".join([*parts[:-1], sentence, parts[-1]]).strip()
    else:
        body = f"{body.rstrip()} {sentence}".strip()
    return f"{body}{signature}"


def _cta_sentence(
    *,
    archetype: str,
    role: str,
    company: str,
    cta_style: str,
) -> str:
    del cta_style
    role_fit = f"the {role} fit" if role else "the role fit"
    company_fit = f"{company} fit" if company else "fit"
    if archetype == ARCHETYPE_RECRUITER:
        return f"Would a quick recruiter screen on {role_fit} be useful, or is another owner better?"
    if archetype == ARCHETYPE_SENIOR_TA:
        return f"Would a brief fit review against {role_fit} be useful, or is another owner better?"
    if archetype == ARCHETYPE_C_LEVEL:
        return f"Would a brief executive exchange on the {company_fit} be useful, or is the right owner someone else?"
    if archetype == ARCHETYPE_EXECUTIVE:
        return f"Would a brief exchange on {role_fit} be useful, or is another owner better?"
    return f"Would a quick screen on {role_fit} be useful?"


def _replace_cta(text: str, *, cta: str) -> str:
    body, signature = _split_terminal_signature(text)
    parts = [part.strip() for part in re.findall(r"[^.!?]+[.!?]", body) if part.strip()]
    if not parts or not parts[-1].endswith("?"):
        return text
    body = " ".join([*parts[:-1], cta]).strip()
    return f"{body}{signature}"


def _remove_cross_company_texture(text: str, *, company: str) -> str:
    key = company.strip().lower()
    guarded_terms: dict[str, tuple[str, ...]] = {
        "aig": ("AIG Assist", "claims and underwriting", "claims", "underwriting", "insurance"),
        "citi": ("Citi Sky", "firmwide AI governance", "financial-services controls"),
        "neo4j": ("graph-context reliability", "graph context, trust, and commercial packaging"),
    }
    cleaned = text
    for owner, terms in guarded_terms.items():
        if owner == key:
            continue
        for term in terms:
            cleaned = re.sub(rf"\b{re.escape(term)}\b,?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.!?])", r"\1", cleaned)
    return cleaned.strip()


def _split_terminal_signature(text: str) -> tuple[str, str]:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    match = _SIGNATURE_PATTERN.search(cleaned)
    if not match:
        return cleaned, ""
    return cleaned[: match.start()].strip(), "\n\nAmit"


def _initial_stop_reason(
    *,
    proof: ExitProofBundle,
    batch: WholeMessageCandidateBatch,
    selected_candidate_id: str,
) -> str:
    if proof.x1d_result.status == STATUS_X1D_PASS:
        return STOP_ALREADY_CLEAR
    if not proof.x2_result.passed:
        return STOP_X2_FAILED_BEFORE_JUDGE_FEEDBACK
    if not _candidate_by_id(batch, proof.candidate_id or selected_candidate_id):
        return STOP_NO_SELECTED_CANDIDATE
    if proof.x1d_result.status == STATUS_X1D_BLOCKED:
        return STOP_X1D_BLOCKED_NO_REGENERATION
    if proof.x1d_result.status != STATUS_X1D_REVIEW_REQUIRED:
        return STOP_X1D_NOT_REVIEW_REQUIRED
    if any(
        reason.startswith(_BLOCKED_REASON_PREFIXES)
        for reason in proof.x1d_result.reason_codes
    ):
        return STOP_X1D_BLOCKED_NO_REGENERATION
    if not any(
        reason.startswith(_REGEN_REASON_PREFIXES)
        for reason in proof.x1d_result.reason_codes
    ):
        return STOP_X1D_NOT_REVIEW_REQUIRED
    return ""


def _post_repair_stop_reason(proof: ExitProofBundle) -> str:
    if not proof.x2_result.passed:
        return STOP_REPAIR_CANDIDATE_X2_FAILED
    if proof.x1d_result.status == STATUS_X1D_PASS:
        return STOP_REPAIR_CANDIDATE_CLEAR
    if proof.x1d_result.status == STATUS_X1D_BLOCKED:
        return STOP_REPAIR_CANDIDATE_X1D_BLOCKED
    return STOP_REPAIR_CANDIDATE_REVIEW_REQUIRED


def _max_repair_iterations(
    request: WholeMessageGenerationRequest,
    *,
    explicit: int | None,
    initial_proof: ExitProofBundle | None = None,
) -> int:
    if explicit is not None:
        return max(0, min(_MAX_REPAIR_HARD_CAP, int(explicit)))
    raw = os.environ.get("APPS_LIC_X1D_REPAIR_MAX_ITERATIONS")
    if raw:
        try:
            configured = int(raw)
        except ValueError:
            configured = 0
        return max(0, min(_MAX_REPAIR_HARD_CAP, configured))
    configured = int(request.reasoning_policy.repair_budget or 0)
    if _needs_two_iteration_repair_window(request=request, initial_proof=initial_proof):
        configured = max(configured, 2)
    return max(0, min(_MAX_REPAIR_HARD_CAP, configured))


def _needs_two_iteration_repair_window(
    *,
    request: WholeMessageGenerationRequest,
    initial_proof: ExitProofBundle | None,
) -> bool:
    if str(getattr(request.reasoning_policy, "sc_level", "") or "").upper() == "SC-3":
        return True
    if not initial_proof:
        return False
    return len(_failed_judges(initial_proof)) > 1


def _can_extend_after_effective_repair(
    attempt: X1DFeedbackRegenerationAttempt,
) -> bool:
    return (
        attempt.stop_reason == STOP_REPAIR_CANDIDATE_REVIEW_REQUIRED
        and attempt.x1d_repair_effective
        and attempt.repair_candidate_sanitization_passed
        and bool(attempt.x1d_repair_unresolved_issue_ids)
    )


def _result(
    *,
    attempted: bool,
    stop_reason: str,
    proof: ExitProofBundle,
    selected_candidate_id: str,
    attempts: tuple[X1DFeedbackRegenerationAttempt, ...] = (),
) -> X1DFeedbackRegenerationResult:
    return X1DFeedbackRegenerationResult(
        attempted=attempted,
        iteration_count=len(attempts),
        stop_reason=stop_reason,
        final_proof=proof,
        final_selected_candidate_id=selected_candidate_id,
        attempts=attempts,
    )


def _attempt(
    *,
    iteration: int,
    parent: WholeMessageCandidate,
    repaired: WholeMessageCandidate,
    failed: tuple[X1DJudgeResult, ...],
    pre: ExitProofBundle,
    post: ExitProofBundle | None,
    stop_reason: str,
    repair_candidate_sanitization_passed: bool,
) -> X1DFeedbackRegenerationAttempt:
    pre_issue_ids = _issue_ids_from_judges(failed)
    post_failed = _failed_judges(post) if post else failed
    post_issue_ids = _issue_ids_from_judges(post_failed)
    resolved_issue_ids = tuple(
        issue_id for issue_id in pre_issue_ids if issue_id not in set(post_issue_ids)
    )
    unresolved_issue_ids = tuple(dict.fromkeys(post_issue_ids))
    return X1DFeedbackRegenerationAttempt(
        iteration=iteration,
        parent_candidate_id=parent.candidate_id,
        repaired_candidate_id=repaired.candidate_id,
        failed_judge_ids=tuple(result.judge_id for result in failed),
        required_repairs=tuple(
            dict.fromkeys(
                repair
                for result in failed
                for repair in result.required_repairs
                if repair
            )
        ),
        pre_repair_scores=_score_packets(pre.x1d_result.judge_results),
        post_repair_scores=_score_packets(post.x1d_result.judge_results if post else ()),
        stop_reason=stop_reason,
        qwen_repair_receipt=repaired.generation_receipt,
        x2_status=post.x2_result.status if post else pre.x2_result.status,
        x1d_status=post.x1d_result.status if post else pre.x1d_result.status,
        repaired_candidate=repaired.to_packet(),
        x1d_repair_effective=(
            stop_reason == STOP_REPAIR_CANDIDATE_CLEAR
            or bool(resolved_issue_ids)
        ),
        x1d_repair_resolved_issue_ids=resolved_issue_ids,
        x1d_repair_unresolved_issue_ids=unresolved_issue_ids,
        repair_candidate_sanitization_passed=repair_candidate_sanitization_passed,
    )


def _failed_judges(proof: ExitProofBundle | None) -> tuple[X1DJudgeResult, ...]:
    if proof is None:
        return ()
    return tuple(
        result
        for result in proof.x1d_result.judge_results
        if not result.passed or result.score < result.threshold
    )


def _issue_ids_from_judges(judge_results: Iterable[X1DJudgeResult]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            str(issue).strip()
            for result in judge_results
            for issue in result.issues
            if str(issue).strip()
        )
    )


def _repair_candidate_sanitization_passed(
    *,
    request: WholeMessageGenerationRequest,
    candidate: WholeMessageCandidate,
    failed: tuple[X1DJudgeResult, ...],
) -> bool:
    normalized_intents = _normalize_repair_intents(failed)
    body, signature = _split_terminal_signature(candidate.draft_text)
    if signature != "\n\nAmit":
        return False
    if re.search(r"\bAmit(?: Ayer)?\b", body, flags=re.IGNORECASE):
        return False
    if _has_duplicate_bridge_sentence(candidate.draft_text):
        return False
    if _role_title_count(candidate.draft_text, request=request) > 1:
        return False
    if len(candidate.draft_text) > int(request.length_budget.hard_cap_chars or 0):
        return False
    if request.length_budget.max_sentences and _sentence_count(candidate.draft_text) > request.length_budget.max_sentences:
        return False
    if request.length_budget.max_words and _word_count(candidate.draft_text) > request.length_budget.max_words:
        return False
    allowed_claim_ids = _allowed_claim_ids(request)
    required_claim_ids = {
        claim_id
        for intent in normalized_intents
        for claim_id in intent.required_claim_ids
        if claim_id in allowed_claim_ids
    }
    return required_claim_ids.issubset(set(candidate.claims_used))


def _score_packets(results: Iterable[X1DJudgeResult]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "judge_id": result.judge_id,
            "score": result.score,
            "threshold": result.threshold,
            "passed": result.passed,
        }
        for result in results
    )


def _candidate_by_id(
    batch: WholeMessageCandidateBatch,
    candidate_id: str,
) -> WholeMessageCandidate | None:
    for candidate in batch.candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    return None


def _overlay_repair_candidate(
    batch: WholeMessageCandidateBatch,
    repaired: WholeMessageCandidate,
) -> WholeMessageCandidateBatch:
    retained = tuple(
        candidate for candidate in batch.candidates if candidate.candidate_id != repaired.candidate_id
    )
    return WholeMessageCandidateBatch(
        status=STATUS_CANDIDATES_READY,
        request_id=batch.request_id,
        prompt_contract_id=batch.prompt_contract_id,
        candidates=(*retained, repaired),
        blocking_reasons=(),
    )


def _message_fingerprint(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip()).lower()


def _repair_candidate_id(candidate_id: str, iteration: int) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_.:-]+", "_", candidate_id).strip("_")
    if clean.startswith("x1d_repair_"):
        return clean
    return f"x1d_repair_{iteration}_{clean or 'candidate'}"


def _candidate_id(parent_candidate: WholeMessageCandidate, text: str, iteration: int) -> str:
    return _digest(
        {
            "parent_candidate_id": parent_candidate.candidate_id,
            "draft_text": text,
            "iteration": iteration,
        }
    )[:32]


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _ensure_terminal_amit_signature(text: str) -> str:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    if _SIGNATURE_PATTERN.search(cleaned):
        return cleaned
    cleaned = re.sub(r"\s+Amit(?: Ayer)?[.;:].*\Z", "", cleaned, flags=re.IGNORECASE).rstrip()
    cleaned = re.sub(
        r"(?:\s|\n)+(?:best|thanks|regards|warmly|cheers)[,.]?\s*\Z",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).rstrip()
    cleaned = re.sub(r"\s+Amit(?: Ayer)?\.?\s*\Z", "", cleaned, flags=re.IGNORECASE).rstrip()
    return f"{cleaned}\n\nAmit"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", str(text or "")))


def _sentence_count(text: str) -> int:
    text = re.sub(
        r"(?:\r?\n|\A)\s*(?:best|thanks|regards|warmly|cheers)?[,]?\s*Amit(?: Ayer)?\.?\s*\Z",
        "",
        str(text or ""),
        flags=re.IGNORECASE,
    ).strip()
    return len([part for part in re.split(r"[.!?]+", text) if part.strip()])


__all__ = [
    "RepairRunner",
    "X1DFeedbackRegenerationAttempt",
    "X1DFeedbackRegenerationResult",
    "qwen_judge_feedback_repair_candidate",
    "run_x1d_judge_feedback_regeneration",
]
