"""W5 message quality and non-repetition controls for apps_lic.

This module is deterministic and data-only. It does not call model providers,
write durable state, or override C0 evidence/Exit decisions.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from apps_lic.engines.message_type_requirement_gate import (
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
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
)
from apps_lic.engines.standing_sender_knowledge import validate_sender_claims_before_l2


EXIT_CLEAR_DRAFT = "clear_draft"

STATUS_MESSAGE_QUALITY_PASS = "MESSAGE_QUALITY_PASS"
STATUS_MESSAGE_QUALITY_BLOCKED = "MESSAGE_QUALITY_BLOCKED"

GATE_IDENTICAL_DRAFTS = "identical_drafts_gate"
GATE_NGRAM_SIMILARITY = "ngram_similarity_gate"
GATE_BANNED_GENERIC_PHRASE = "banned_generic_phrase_gate"
GATE_ROLE_SPECIFIC_JD_FIELDS = "role_specific_jd_fields_gate"
GATE_UNSUPPORTED_SENDER_CLAIM = "unsupported_sender_claim_gate"

REASON_IDENTICAL_DRAFTS = "identical_drafts_same_class_different_recipient"
REASON_NGRAM_SIMILARITY_EXCEEDED = "ngram_similarity_ceiling_exceeded"
REASON_BANNED_GENERIC_PHRASE = "banned_generic_phrase"
REASON_MISSING_JD_TITLE_OR_REQ = "missing_jd_title_or_req_in_role_specific_draft"
REASON_UNSUPPORTED_SENDER_CLAIM = "unsupported_sender_claim"
REASON_MISSING_CLAIMS_USED = "missing_claims_used_for_clear_draft"

NGRAM_SIZE = 5
NGRAM_SIMILARITY_CEILING = 0.82

PROVIDER_BACKED_GENERATION_POLICY_ID = "apps_lic.provider_backed_generation.w5"
DETERMINISTIC_FALLBACK_RECEIPT = "pass:w6_deterministic_whole_message_fallback_available"

BANNED_GENERIC_PHRASES: tuple[str, ...] = (
    "hope you're doing well",
    "hope you are doing well",
    "i hope you're doing well",
    "i am reaching out",
    "i'm reaching out",
    "i came across your profile",
    "would love to connect",
    "looking for new opportunities",
    "open to new opportunities",
    "quick question",
    "picking your brain",
    "exciting opportunity",
    "i think i'd be a great fit",
    "please let me know if you have any questions",
    "is it worth 15 minutes",
    "would 15 minutes",
    "could we do 15 minutes",
    "15-minute product-fit",
    "compare where",
    "compare this against",
    "control plane should live",
    "release-gate",
    "release gate",
    "pressure-test",
    "pressure test",
    "which maps to",
    "not demo quality",
    "hard call",
)

_EXEC_CLASSES = {
    CLASS_EXECUTIVE,
    CLASS_C_LEVEL,
    CLASS_CEO,
    CLASS_CTO,
    CLASS_VP_ENG,
}

_ROLE_SPECIFIC_CLASSES = {
    CLASS_RECRUITER,
    CLASS_SENIOR_TA,
    CLASS_HIRING_MANAGER,
}

_DEFAULT_COMPANY_TRIGGER = (
    "AIG's enterprise AI operating-model signal"
)

_RHETORICAL_ANGLES: dict[str, tuple[tuple[str, str], ...]] = {
    CLASS_RECRUITER: (
        ("req_signal", "platform ownership, AI governance, and executive-scale adoption"),
        ("screen_signal", "regulated delivery, runtime controls, and reusable AI services"),
        ("mandate_bridge", "agentic-platform ambition, governance discipline, and operating-model clarity"),
        ("proof_signal", "AI platform scale, proof discipline, and enterprise adoption"),
        ("operator_signal", "builder/operator depth across governed AI, telemetry, and rollout discipline"),
        ("shortlist_signal", "a screenable bridge from regulated platforms to AI execution"),
        ("evidence_signal", "concrete evidence across governance, reliability, and platform productization"),
    ),
    CLASS_SENIOR_TA: (
        ("portfolio_signal", "a talent signal above one requisition: platform, governance, and adoption range"),
        ("bar_raiser", "a leadership pattern TA can reuse across regulated AI searches"),
        ("req_to_strategy", "a bridge between this req and the broader AI talent plan"),
        ("screen_design", "the screenable edge between technical depth and executive-facing AI governance"),
    ),
    CLASS_HIRING_MANAGER: (
        ("architecture_risk", "the point where architecture choices become operating risk"),
        ("runtime_signal", "production reliability, governance gates, and platform adoption"),
        ("builder_fit", "hands-on platform delivery with risk-aware AI controls"),
    ),
    CLASS_EXECUTIVE: (
        ("adoption_speed", "turning governance from approval drag into adoption speed"),
        ("platform_economics", "making AI platform investment compound instead of sprawl"),
        ("operating_model", "connecting AI operating-model design to measurable execution discipline"),
    ),
    CLASS_C_LEVEL: (
        ("adoption_speed", "turning governance from approval drag into adoption speed"),
        ("platform_economics", "making AI platform investment compound instead of sprawl"),
        ("operating_model", "connecting AI operating-model design to measurable execution discipline"),
        ("risk_to_speed", "converting risk control into faster enterprise AI reuse"),
    ),
    CLASS_CEO: (
        ("ceo_operating_edge", "making enterprise AI governance create speed, not ceremony"),
        ("ceo_compounding", "turning AI platform bets into reusable operating leverage"),
    ),
    CLASS_CTO: (
        ("cto_runtime_edge", "keeping agentic AI ambitious without losing runtime control"),
        ("cto_platform_edge", "making AI platform primitives reusable enough to survive scale"),
    ),
    CLASS_VP_ENG: (
        ("vp_execution_edge", "shipping agentic AI with enough governance to keep scaling credible"),
        ("vp_operating_edge", "turning evaluation, telemetry, and rollback discipline into delivery speed"),
    ),
}

_CLASS_CTAS: dict[str, tuple[str, ...]] = {
    CLASS_RECRUITER: (
        "If the req is still live, would a quick resume review be useful against the exact screen?",
        "Would it help if I send a tight fit note mapped to the req?",
        "Worth a short recruiter screen if the search is still active?",
        "Would a targeted resume review help decide whether to advance the conversation?",
    ),
    CLASS_SENIOR_TA: (
        "Would a short discussion help assess fit for this req and the broader AI talent plan?",
        "Would it be useful to compare the profile against the search strategy behind the req?",
        "Worth a brief conversation if this role is part of a larger AI platform buildout?",
    ),
    CLASS_HIRING_MANAGER: (
        "Worth a brief technical screen to compare the platform/governance edge against the mandate?",
        "Would a short technical conversation be useful before the req turns into resume keyword matching?",
        "Open to a brief screen focused on the platform and governance tradeoffs behind the role?",
    ),
    CLASS_EXECUTIVE: (
        "Worth a brief exchange on the operating risks behind that shift?",
        "Would a short discussion on the platform execution angle be useful?",
        "Open to a concise executive exchange if the operating-model angle is timely?",
    ),
    CLASS_C_LEVEL: (
        "Worth a brief exchange on the operating risks behind that shift?",
        "Would a short discussion on the platform execution angle be useful?",
        "Open to a concise executive exchange if the operating-model angle is timely?",
    ),
    CLASS_CEO: (
        "Worth a brief executive exchange on where AI governance should accelerate, not slow, adoption?",
        "Open to a concise discussion on the operating leverage behind that AI platform shift?",
    ),
    CLASS_CTO: (
        "Worth a brief technical exchange on the runtime controls behind that shift?",
        "Open to a short conversation on how platform primitives survive enterprise AI scale?",
    ),
    CLASS_VP_ENG: (
        "Worth a brief engineering exchange on the delivery controls behind that shift?",
        "Open to a short discussion on scaling agentic AI without weakening runtime discipline?",
    ),
}

_PROOF_ROTATION: dict[str, tuple[str, ...]] = {
    CLASS_RECRUITER: ("sp_agentic_platform",),
    CLASS_SENIOR_TA: ("sp_agentic_platform", "sp_runtime_reliability"),
    CLASS_HIRING_MANAGER: (
        "sp_runtime_reliability",
        "sp_cloud_ai_transformation",
        "sp_agentic_platform",
    ),
    CLASS_EXECUTIVE: (
        "sp_platform_commercialization",
        "sp_quant_governance_foundation",
        "sp_agentic_platform",
    ),
    CLASS_C_LEVEL: (
        "sp_platform_commercialization",
        "sp_quant_governance_foundation",
        "sp_runtime_reliability",
        "sp_agentic_platform",
    ),
    CLASS_CEO: ("sp_platform_commercialization", "sp_quant_governance_foundation"),
    CLASS_CTO: (
        "sp_runtime_reliability",
        "sp_cloud_ai_transformation",
        "sp_agentic_platform",
    ),
    CLASS_VP_ENG: (
        "sp_runtime_reliability",
        "sp_agentic_platform",
        "sp_cloud_ai_transformation",
    ),
}

_PROOF_TEXT: dict[str, str] = {
    "sp_agentic_platform": (
        "designed and operationalized a governed agentic AI platform for regulated enterprise workflows"
    ),
    "sp_runtime_reliability": (
        "strengthened enterprise retrieval quality, evaluation gates, telemetry, rollback controls, and AI CI/CD standards"
    ),
    "sp_platform_commercialization": (
        "productized agentic AI primitives into reusable platform services and scaled them into enterprise adoption"
    ),
    "sp_cloud_ai_transformation": (
        "architected cloud-native AI and analytics platforms for regulated financial environments"
    ),
    "sp_quant_governance_foundation": (
        "brings actuarial and statistical training to risk-aware AI platform governance"
    ),
}


@dataclass(frozen=True)
class ProviderBackedGenerationPolicy:
    policy_id: str
    enabled_by_default: bool
    requires_explicit_config: bool
    generator_temperature_min: float
    generator_temperature_max: float
    top_p_min: float
    whole_message_only: bool
    draft_only_required: bool
    no_send_authority: bool
    deterministic_fallback_receipt: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.provider_backed_generation_policy.v1",
            "policy_id": self.policy_id,
            "enabled_by_default": self.enabled_by_default,
            "requires_explicit_config": self.requires_explicit_config,
            "generator_temperature_min": self.generator_temperature_min,
            "generator_temperature_max": self.generator_temperature_max,
            "top_p_min": self.top_p_min,
            "whole_message_only": self.whole_message_only,
            "draft_only_required": self.draft_only_required,
            "no_send_authority": self.no_send_authority,
            "deterministic_fallback_receipt": self.deterministic_fallback_receipt,
        }


@dataclass(frozen=True)
class MessageQualityViolation:
    gate_id: str
    reason_code: str
    profile_ids: tuple[str, ...]
    recipient_class: str
    message_type: str
    similarity_score: float
    details: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "reason_code": self.reason_code,
            "profile_ids": list(self.profile_ids),
            "recipient_class": self.recipient_class,
            "message_type": self.message_type,
            "similarity_score": self.similarity_score,
            "details": self.details,
        }


@dataclass(frozen=True)
class MessageQualityReport:
    status: str
    passed: bool
    clear_draft_count: int
    diversity_passed_count: int
    max_ngram_similarity: float
    similarity_ceiling: float
    banned_generic_phrases: tuple[str, ...]
    violations: tuple[MessageQualityViolation, ...]

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.message_quality_report.v1",
            "status": self.status,
            "passed": self.passed,
            "clear_draft_count": self.clear_draft_count,
            "diversity_passed_count": self.diversity_passed_count,
            "max_ngram_similarity": self.max_ngram_similarity,
            "similarity_ceiling": self.similarity_ceiling,
            "banned_generic_phrases": list(self.banned_generic_phrases),
            "violation_count": len(self.violations),
            "violations": [violation.to_packet() for violation in self.violations],
        }


PROVIDER_BACKED_GENERATION_POLICY = ProviderBackedGenerationPolicy(
    policy_id=PROVIDER_BACKED_GENERATION_POLICY_ID,
    enabled_by_default=False,
    requires_explicit_config=True,
    generator_temperature_min=0.90,
    generator_temperature_max=0.98,
    top_p_min=0.94,
    whole_message_only=True,
    draft_only_required=True,
    no_send_authority=True,
    deterministic_fallback_receipt=DETERMINISTIC_FALLBACK_RECEIPT,
)


def _sha256_canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", value.lower()))


def _word_count(value: str) -> int:
    return len(_tokens(value))


def _sentence_count(value: str) -> int:
    return len([part for part in re.split(r"[.!?]+", value) if part.strip()])


def _first_name(name: Any) -> str:
    cleaned = _clean(name)
    return cleaned.split()[0] if cleaned else "there"


def _stable_index(row: Mapping[str, Any], modulo: int, *, salt: str = "") -> int:
    if modulo <= 0:
        return 0
    basis = "|".join(
        _clean(part)
        for part in (
            salt,
            row.get("profile_id") or row.get("id"),
            row.get("name"),
            row.get("title"),
            row.get("derived_class"),
        )
    )
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


def _select_angle(row: Mapping[str, Any]) -> tuple[str, str]:
    recipient_class = _clean(row.get("derived_class"))
    angles = _RHETORICAL_ANGLES.get(recipient_class) or _RHETORICAL_ANGLES[CLASS_RECRUITER]
    return angles[_stable_index(row, len(angles), salt="angle")]


def _select_cta(row: Mapping[str, Any]) -> str:
    recipient_class = _clean(row.get("derived_class"))
    ctas = _CLASS_CTAS.get(recipient_class) or _CLASS_CTAS[CLASS_RECRUITER]
    return ctas[_stable_index(row, len(ctas), salt="cta")]


def _select_proof_id(row: Mapping[str, Any]) -> str:
    recipient_class = _clean(row.get("derived_class"))
    rotation = _PROOF_ROTATION.get(recipient_class) or ("sp_agentic_platform",)
    return rotation[_stable_index(row, len(rotation), salt="proof")]


def compress_company_trigger(value: Any, *, max_words: int = 11) -> str:
    cleaned = _clean(value) or _DEFAULT_COMPANY_TRIGGER
    first_clause = re.split(r"[.;:]", cleaned, maxsplit=1)[0].strip()
    words = _tokens(first_clause)
    if len(words) <= max_words:
        return first_clause
    return " ".join(words[:max_words])


def _role_reference(row: Mapping[str, Any]) -> str:
    position = _clean(row.get("jd_position_name")) or _clean(row.get("position_name")) or "the open role"
    req = _clean(row.get("jd_requisition_number")) or _clean(row.get("requisition_number"))
    return f"{position} ({req})" if req else position


def _render_role_specific(row: Mapping[str, Any], *, angle_text: str, proof_text: str, cta: str) -> str:
    first = _first_name(row.get("name"))
    role_ref = _role_reference(row)
    recipient_class = _clean(row.get("derived_class"))
    if recipient_class == CLASS_SENIOR_TA:
        return (
            f"Hi {first}, AIG's {role_ref} looks like {angle_text}. "
            f"My relevant proof: {proof_text}. "
            f"{cta}"
        )
    if recipient_class == CLASS_HIRING_MANAGER:
        return (
            f"Hi {first}, AIG's {role_ref} looks like {angle_text}. "
            f"My relevant proof: {proof_text}. "
            f"{cta}"
        )
    return (
        f"Hi {first}, AIG's {role_ref} reads like a rare blend of {angle_text}. "
        f"My relevant proof: {proof_text}. "
        f"{cta}"
    )


def _render_trigger_based(row: Mapping[str, Any], *, angle_text: str, proof_text: str, cta: str) -> str:
    first = _first_name(row.get("name"))
    title = _clean(row.get("title"))
    vantage = f"from a {title} seat, " if title else ""
    trigger = compress_company_trigger(
        row.get("company_trigger")
        or row.get("company_context")
        or row.get("public_profile_signal")
        or _DEFAULT_COMPANY_TRIGGER
    )
    return (
        f"Hi {first}, {vantage}{trigger} points to the harder part of AI transformation: {angle_text}. "
        f"My relevant proof: {proof_text}. "
        f"{cta}"
    )


def _render_general(row: Mapping[str, Any], *, angle_text: str, proof_text: str, cta: str) -> str:
    first = _first_name(row.get("name"))
    return (
        f"Hi {first}, your AIG role points to {angle_text}. "
        f"My relevant proof: {proof_text}. "
        f"{cta}"
    )


def render_quality_controlled_draft(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return a W5 quality-controlled draft packet for one clear row."""
    angle_id, angle_text = _select_angle(row)
    proof_id = _select_proof_id(row)
    proof_text = _PROOF_TEXT[proof_id]
    cta = _select_cta(row)
    message_type = _clean(row.get("message_type"))
    if message_type == MESSAGE_ROLE_SPECIFIC:
        draft_text = _render_role_specific(row, angle_text=angle_text, proof_text=proof_text, cta=cta)
    elif message_type == MESSAGE_TRIGGER_BASED_INSIGHT:
        draft_text = _render_trigger_based(row, angle_text=angle_text, proof_text=proof_text, cta=cta)
    else:
        draft_text = _render_general(row, angle_text=angle_text, proof_text=proof_text, cta=cta)
    return {
        "draft_text": draft_text,
        "draft_word_count": _word_count(draft_text),
        "draft_sentence_count": _sentence_count(draft_text),
        "claims_used": [proof_id],
        "rhetorical_angle": angle_id,
        "recipient_class_cta": cta,
        "company_trigger_compressed": compress_company_trigger(
            row.get("company_trigger") or row.get("company_context") or _DEFAULT_COMPANY_TRIGGER
        ),
        "message_quality_variant_id": _sha256_canonical(
            {
                "profile_id": row.get("profile_id") or row.get("id"),
                "angle_id": angle_id,
                "proof_id": proof_id,
                "cta": cta,
            }
        ),
    }


def apply_message_quality_variants(rows: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Apply W5 quality variants to clear drafts only."""
    materialized: list[dict[str, Any]] = []
    for row in rows:
        next_row = dict(row)
        next_row.setdefault("profile_id", next_row.get("id"))
        if _clean(next_row.get("exit_disposition")) == EXIT_CLEAR_DRAFT:
            next_row.update(render_quality_controlled_draft(next_row))
            next_row["message_quality_status"] = STATUS_MESSAGE_QUALITY_PASS
            next_row["provider_backed_generation_policy_id"] = PROVIDER_BACKED_GENERATION_POLICY_ID
            next_row["deterministic_fallback_receipt"] = DETERMINISTIC_FALLBACK_RECEIPT
        materialized.append(next_row)
    return tuple(materialized)


def _normalize_for_duplicate(text: str) -> str:
    normalized = _clean(text).lower()
    normalized = re.sub(r"^hi\s+[a-z][a-z'\-]*,\s*", "hi <recipient>, ", normalized)
    normalized = re.sub(r"\b(jr|req)[-\s]?\d+[a-z0-9-]*\b", "<req>", normalized)
    return normalized


def ngram_similarity(left: str, right: str, *, ngram_size: int = NGRAM_SIZE) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    left_ngrams = _ngram_set(left_tokens, ngram_size)
    right_ngrams = _ngram_set(right_tokens, ngram_size)
    if not left_ngrams or not right_ngrams:
        return 0.0
    intersection = len(left_ngrams & right_ngrams)
    union = len(left_ngrams | right_ngrams)
    return round(intersection / union if union else 0.0, 4)


def _ngram_set(tokens: tuple[str, ...], ngram_size: int) -> set[tuple[str, ...]]:
    if len(tokens) < ngram_size:
        return {tokens}
    return {
        tuple(tokens[index : index + ngram_size])
        for index in range(0, len(tokens) - ngram_size + 1)
    }


def _clear_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[Mapping[str, Any], ...]:
    return tuple(row for row in rows if _clean(row.get("exit_disposition")) == EXIT_CLEAR_DRAFT)


def validate_message_quality(
    rows: Iterable[Mapping[str, Any]],
    *,
    similarity_ceiling: float = NGRAM_SIMILARITY_CEILING,
    banned_phrases: Iterable[str] = BANNED_GENERIC_PHRASES,
) -> MessageQualityReport:
    """Validate non-repetition, generic phrasing, JD retention, and claim IDs."""
    clear_rows = _clear_rows(tuple(rows))
    violations: list[MessageQualityViolation] = []
    max_similarity = 0.0
    banned = tuple(dict.fromkeys(_clean(item).lower() for item in banned_phrases if _clean(item)))

    seen_by_class: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in clear_rows:
        text = _clean(row.get("draft_text"))
        recipient_class = _clean(row.get("derived_class"))
        message_type = _clean(row.get("message_type"))
        profile_id = _clean(row.get("profile_id") or row.get("id"))
        normalized = _normalize_for_duplicate(text)
        duplicate_key = (recipient_class, normalized)
        previous = seen_by_class.get(duplicate_key)
        if previous is not None and _clean(previous.get("profile_id") or previous.get("id")) != profile_id:
            violations.append(
                MessageQualityViolation(
                    gate_id=GATE_IDENTICAL_DRAFTS,
                    reason_code=REASON_IDENTICAL_DRAFTS,
                    profile_ids=(
                        _clean(previous.get("profile_id") or previous.get("id")),
                        profile_id,
                    ),
                    recipient_class=recipient_class,
                    message_type=message_type,
                    similarity_score=1.0,
                    details="Normalized drafts are identical within recipient class.",
                )
            )
        else:
            seen_by_class[duplicate_key] = row

        lowered = text.lower()
        for phrase in banned:
            if phrase in lowered:
                violations.append(
                    MessageQualityViolation(
                        gate_id=GATE_BANNED_GENERIC_PHRASE,
                        reason_code=REASON_BANNED_GENERIC_PHRASE,
                        profile_ids=(profile_id,),
                        recipient_class=recipient_class,
                        message_type=message_type,
                        similarity_score=0.0,
                        details=phrase,
                    )
                )

        if message_type == MESSAGE_ROLE_SPECIFIC and recipient_class in _ROLE_SPECIFIC_CLASSES:
            position = _clean(row.get("jd_position_name") or row.get("position_name"))
            req = _clean(row.get("jd_requisition_number") or row.get("requisition_number"))
            if not position or not req or position not in text or req not in text:
                violations.append(
                    MessageQualityViolation(
                        gate_id=GATE_ROLE_SPECIFIC_JD_FIELDS,
                        reason_code=REASON_MISSING_JD_TITLE_OR_REQ,
                        profile_ids=(profile_id,),
                        recipient_class=recipient_class,
                        message_type=message_type,
                        similarity_score=0.0,
                        details="Role-specific recruiter/TA/hiring-manager draft must include JD title and req.",
                    )
                )

        claims_used = tuple(_clean(item) for item in row.get("claims_used") or () if _clean(item))
        if not claims_used:
            violations.append(
                MessageQualityViolation(
                    gate_id=GATE_UNSUPPORTED_SENDER_CLAIM,
                    reason_code=REASON_MISSING_CLAIMS_USED,
                    profile_ids=(profile_id,),
                    recipient_class=recipient_class,
                    message_type=message_type,
                    similarity_score=0.0,
                    details="Clear drafts must carry explicit C0.3 claim IDs.",
                )
            )
        else:
            claim_validation = validate_sender_claims_before_l2(
                claims_used,
                recipient_class=recipient_class,
                message_type=message_type,
            )
            if claim_validation.status != "PASS":
                violations.append(
                    MessageQualityViolation(
                        gate_id=GATE_UNSUPPORTED_SENDER_CLAIM,
                        reason_code=REASON_UNSUPPORTED_SENDER_CLAIM,
                        profile_ids=(profile_id,),
                        recipient_class=recipient_class,
                        message_type=message_type,
                        similarity_score=0.0,
                        details=json.dumps(
                            list(claim_validation.blocked_claims),
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                    )
                )

    for left_index, left in enumerate(clear_rows):
        for right in clear_rows[left_index + 1 :]:
            score = ngram_similarity(
                _normalize_for_duplicate(_clean(left.get("draft_text"))),
                _normalize_for_duplicate(_clean(right.get("draft_text"))),
            )
            max_similarity = max(max_similarity, score)
            if score > similarity_ceiling:
                violations.append(
                    MessageQualityViolation(
                        gate_id=GATE_NGRAM_SIMILARITY,
                        reason_code=REASON_NGRAM_SIMILARITY_EXCEEDED,
                        profile_ids=(
                            _clean(left.get("profile_id") or left.get("id")),
                            _clean(right.get("profile_id") or right.get("id")),
                        ),
                        recipient_class=_clean(left.get("derived_class")),
                        message_type=_clean(left.get("message_type")),
                        similarity_score=score,
                        details=f"Pairwise {NGRAM_SIZE}-gram Jaccard exceeds {similarity_ceiling}.",
                    )
                )

    passed = not violations
    return MessageQualityReport(
        status=STATUS_MESSAGE_QUALITY_PASS if passed else STATUS_MESSAGE_QUALITY_BLOCKED,
        passed=passed,
        clear_draft_count=len(clear_rows),
        diversity_passed_count=len(clear_rows) if passed else max(0, len(clear_rows) - len(violations)),
        max_ngram_similarity=round(max_similarity, 4),
        similarity_ceiling=similarity_ceiling,
        banned_generic_phrases=banned,
        violations=tuple(violations),
    )


__all__ = [
    "BANNED_GENERIC_PHRASES",
    "DETERMINISTIC_FALLBACK_RECEIPT",
    "EXIT_CLEAR_DRAFT",
    "GATE_BANNED_GENERIC_PHRASE",
    "GATE_IDENTICAL_DRAFTS",
    "GATE_NGRAM_SIMILARITY",
    "GATE_ROLE_SPECIFIC_JD_FIELDS",
    "GATE_UNSUPPORTED_SENDER_CLAIM",
    "NGRAM_SIMILARITY_CEILING",
    "PROVIDER_BACKED_GENERATION_POLICY",
    "PROVIDER_BACKED_GENERATION_POLICY_ID",
    "REASON_BANNED_GENERIC_PHRASE",
    "REASON_IDENTICAL_DRAFTS",
    "REASON_MISSING_CLAIMS_USED",
    "REASON_MISSING_JD_TITLE_OR_REQ",
    "REASON_NGRAM_SIMILARITY_EXCEEDED",
    "REASON_UNSUPPORTED_SENDER_CLAIM",
    "STATUS_MESSAGE_QUALITY_BLOCKED",
    "STATUS_MESSAGE_QUALITY_PASS",
    "MessageQualityReport",
    "MessageQualityViolation",
    "ProviderBackedGenerationPolicy",
    "apply_message_quality_variants",
    "compress_company_trigger",
    "ngram_similarity",
    "render_quality_controlled_draft",
    "validate_message_quality",
]
