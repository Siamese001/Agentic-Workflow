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
        return {
            "schema_version": "apps_lic.x1d_feedback_regeneration_result.v1",
            "attempted": self.attempted,
            "iteration_count": self.iteration_count,
            "stop_reason": self.stop_reason,
            "final_selected_candidate_id": self.final_selected_candidate_id,
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

    limit = _max_repair_iterations(request, explicit=max_iterations)
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

    for iteration in range(1, limit + 1):
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
            attempts.append(
                _attempt(
                    iteration=iteration,
                    parent=parent,
                    repaired=repaired,
                    failed=failed,
                    pre=current_proof,
                    post=None,
                    stop_reason=STOP_REPAIR_SAME_AS_PARENT,
                )
            )
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
        attempts.append(
            _attempt(
                iteration=iteration,
                parent=parent,
                repaired=repaired,
                failed=failed,
                pre=current_proof,
                post=repaired_proof,
                stop_reason=stop_reason,
            )
        )
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
        current_proof = repaired_proof
        current_selected_id = repaired.candidate_id

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
    text, subject_line = _apply_feedback_repairs(
        text=text,
        subject_line=subject_line,
        request=request,
        judge_results=judge_results,
    )
    claims = _claims_from_repaired_text(
        text,
        existing=claims,
        allowed_claim_ids=_allowed_claim_ids(request),
    )
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
) -> tuple[str, str]:
    feedback = _feedback_text(judge_results)
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
        subject_line = f"{role} fit at {company or 'target company'}"[:200].rstrip(" .")
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


def _claims_from_repaired_text(
    text: str,
    *,
    existing: tuple[str, ...],
    allowed_claim_ids: set[str],
) -> tuple[str, ...]:
    normalized = text.lower()
    claims = [claim for claim in existing if claim in allowed_claim_ids]
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
        ("scale_outcome", ("scale", "outcome", "quantified", "measurable", "commercialization_claim")),
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


def _feedback_text(judge_results: tuple[X1DJudgeResult, ...]) -> str:
    parts: list[str] = []
    for result in judge_results:
        parts.extend(str(item) for item in result.issues)
        parts.extend(str(item) for item in result.required_repairs)
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
    return max(0, min(_MAX_REPAIR_HARD_CAP, int(request.reasoning_policy.repair_budget or 0)))


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
) -> X1DFeedbackRegenerationAttempt:
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
    )


def _failed_judges(proof: ExitProofBundle) -> tuple[X1DJudgeResult, ...]:
    return tuple(
        result
        for result in proof.x1d_result.judge_results
        if not result.passed or result.score < result.threshold
    )


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
