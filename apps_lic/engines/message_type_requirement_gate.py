"""C0-B message type resolution and requirement gate for apps_lic W4.

This module is deterministic and read-only. It consumes W2 opportunity facts and
W3 recipient_class derivation, then decides whether the requested message shape
has enough evidence to proceed.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY_TRIGGER,
    NAMESPACE_JD,
    NAMESPACE_PRIOR_THREAD,
    NAMESPACE_REFERRAL,
    NAMESPACE_RELATIONSHIP,
    OpportunityFactDocument,
    OpportunityFactStore,
)
from apps_lic.engines.recipient_classification import (
    CLASS_HIRING_MANAGER,
    CLASS_RECRUITER,
    CLASS_SENIOR_TA,
    CLASS_UNKNOWN,
    STATUS_DERIVED as RECIPIENT_STATUS_DERIVED,
    RecipientClassDerivation,
)


MESSAGE_GENERAL_INTRO = "general_intro"
MESSAGE_ROLE_SPECIFIC = "role_specific"
MESSAGE_TRIGGER_BASED_INSIGHT = "trigger_based_insight"
MESSAGE_REFERRAL_ASK = "referral_ask"
MESSAGE_FOLLOW_UP = "follow_up"

CANONICAL_MESSAGE_TYPES = (
    MESSAGE_GENERAL_INTRO,
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
    MESSAGE_REFERRAL_ASK,
    MESSAGE_FOLLOW_UP,
)

MODIFIER_USES_JD = "uses_jd"
MODIFIER_APPLICATION_STATUS_CLAIMED = "application_status_claimed"
MODIFIER_USES_COMPANY_TRIGGER = "uses_company_trigger"
MODIFIER_USES_REFERRAL_CONTEXT = "uses_referral_context"
MODIFIER_USES_PRIOR_THREAD = "uses_prior_thread"
MODIFIER_USES_SENSITIVE_CONSTRAINTS = "uses_sensitive_constraints"

CANONICAL_MODIFIERS = (
    MODIFIER_USES_JD,
    MODIFIER_APPLICATION_STATUS_CLAIMED,
    MODIFIER_USES_COMPANY_TRIGGER,
    MODIFIER_USES_REFERRAL_CONTEXT,
    MODIFIER_USES_PRIOR_THREAD,
    MODIFIER_USES_SENSITIVE_CONSTRAINTS,
)

STATUS_REQUIREMENTS_PASS = "MESSAGE_REQUIREMENTS_PASS"
STATUS_REQUIREMENTS_BLOCKED = "MESSAGE_REQUIREMENTS_BLOCKED"

RECIPIENT_CLASS_NOT_DERIVED = "RECIPIENT_CLASS_NOT_DERIVED"
MISSING_JD_FACTS = "MISSING_JD_FACTS"
MISSING_POSITION_NAME = "MISSING_POSITION_NAME"
MISSING_REQUISITION_NUMBER = "MISSING_REQUISITION_NUMBER"
MISSING_APPLICATION_STATUS = "MISSING_APPLICATION_STATUS"
MISSING_PRIOR_THREAD = "MISSING_PRIOR_THREAD"
MISSING_REFERRER_CONTEXT = "MISSING_REFERRER_CONTEXT"
MISSING_RELATIONSHIP_CONTEXT = "MISSING_RELATIONSHIP_CONTEXT"
MISSING_COMPANY_TRIGGER = "MISSING_COMPANY_TRIGGER"


_HINT_ALIASES: tuple[tuple[str, str], ...] = (
    (MESSAGE_GENERAL_INTRO, MESSAGE_GENERAL_INTRO),
    ("general intro", MESSAGE_GENERAL_INTRO),
    ("intro", MESSAGE_GENERAL_INTRO),
    ("cold intro", MESSAGE_GENERAL_INTRO),
    (MESSAGE_ROLE_SPECIFIC, MESSAGE_ROLE_SPECIFIC),
    ("role specific", MESSAGE_ROLE_SPECIFIC),
    ("role-specific", MESSAGE_ROLE_SPECIFIC),
    ("job specific", MESSAGE_ROLE_SPECIFIC),
    ("recruiter note", MESSAGE_ROLE_SPECIFIC),
    ("senior ta note", MESSAGE_ROLE_SPECIFIC),
    (MESSAGE_TRIGGER_BASED_INSIGHT, MESSAGE_TRIGGER_BASED_INSIGHT),
    ("trigger based", MESSAGE_TRIGGER_BASED_INSIGHT),
    ("trigger-based", MESSAGE_TRIGGER_BASED_INSIGHT),
    ("exec peer note", MESSAGE_TRIGGER_BASED_INSIGHT),
    ("company trigger", MESSAGE_TRIGGER_BASED_INSIGHT),
    ("asymmetric insight", MESSAGE_TRIGGER_BASED_INSIGHT),
    (MESSAGE_REFERRAL_ASK, MESSAGE_REFERRAL_ASK),
    ("referral", MESSAGE_REFERRAL_ASK),
    ("referral ask", MESSAGE_REFERRAL_ASK),
    ("warm intro", MESSAGE_REFERRAL_ASK),
    (MESSAGE_FOLLOW_UP, MESSAGE_FOLLOW_UP),
    ("follow up", MESSAGE_FOLLOW_UP),
    ("follow-up", MESSAGE_FOLLOW_UP),
    ("followup", MESSAGE_FOLLOW_UP),
)

_MESSAGE_PATTERNS: tuple[tuple[str, str], ...] = (
    (MESSAGE_FOLLOW_UP, r"\b(follow[- ]?up|following up|circling back|prior note|previous message|no reply|last touch)\b"),
    (MESSAGE_REFERRAL_ASK, r"\b(referral|refer|referrer|warm intro|introduction|introduced by)\b"),
    (MESSAGE_TRIGGER_BASED_INSIGHT, r"\b(trigger|announcement|recent news|company signal|market signal|public post|asymmetric insight)\b"),
    (MESSAGE_ROLE_SPECIFIC, r"\b(jd|job description|job id|role|opening|position|req|requisition|applied|application|resume review)\b"),
)

_MODIFIER_PATTERNS: dict[str, str] = {
    MODIFIER_USES_JD: r"\b(jd|job description|job id|role|opening|position|req|requisition|job|applied|application|resume review)\b",
    MODIFIER_APPLICATION_STATUS_CLAIMED: r"\b(applied|submitted|application status|referred|interviewing|interviewed)\b",
    MODIFIER_USES_COMPANY_TRIGGER: r"\b(trigger|announcement|recent news|company signal|market signal|public post|asymmetric insight)\b",
    MODIFIER_USES_REFERRAL_CONTEXT: r"\b(referral|refer|referrer|warm intro|introduction|introduced by)\b",
    MODIFIER_USES_PRIOR_THREAD: r"\b(follow[- ]?up|following up|circling back|prior thread|prior note|previous message|no reply|last touch)\b",
    MODIFIER_USES_SENSITIVE_CONSTRAINTS: r"\b(visa|sponsor|compensation|salary|remote|hybrid|relocation|location constraint|work authorization)\b",
}

_RELATIONSHIP_PATTERN = re.compile(
    r"\b(warm|relationship|former colleague|worked together|met at|introduced by|mutual connection)\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class MessageTypeResolution:
    message_type: str
    modifiers: Mapping[str, bool]
    source: str
    reason_codes: tuple[str, ...]
    normalized_hint: str
    intent_digest: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.message_type_resolution.v1",
            "message_type": self.message_type,
            "modifiers": dict(self.modifiers),
            "source": self.source,
            "reason_codes": list(self.reason_codes),
            "normalized_hint": self.normalized_hint,
            "intent_digest": self.intent_digest,
        }


@dataclass(frozen=True)
class MessageRequirementGateResult:
    status: str
    allowed: bool
    message_type: str
    modifiers: Mapping[str, bool]
    recipient_class: str
    missing_fields: tuple[str, ...]
    required_namespaces: tuple[str, ...]
    reason_codes: tuple[str, ...]
    source_snapshot_ids: tuple[str, ...]
    resolution: MessageTypeResolution

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.message_requirement_gate.v1",
            "status": self.status,
            "allowed": self.allowed,
            "message_type": self.message_type,
            "modifiers": dict(self.modifiers),
            "recipient_class": self.recipient_class,
            "missing_fields": list(self.missing_fields),
            "required_namespaces": list(self.required_namespaces),
            "reason_codes": list(self.reason_codes),
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "resolution": self.resolution.to_packet(),
        }


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalize_hint(value: str) -> str:
    lowered = _clean(value).lower().replace("_", " ")
    lowered = re.sub(r"[^a-z0-9 -]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _canonical_hint(message_type_hint: str) -> tuple[str, str] | None:
    normalized = _normalize_hint(message_type_hint)
    if not normalized:
        return None
    for alias, canonical in _HINT_ALIASES:
        alias_norm = _normalize_hint(alias)
        if normalized == alias_norm or alias_norm in normalized:
            return canonical, alias_norm
    return None


def _infer_message_type(text: str) -> tuple[str, str]:
    for message_type, pattern in _MESSAGE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return message_type, f"intent_pattern:{message_type}"
    return MESSAGE_GENERAL_INTRO, "default:general_intro"


def _resolve_modifiers(text: str, explicit_modifiers: Mapping[str, bool] | None) -> dict[str, bool]:
    modifiers = {
        modifier: re.search(pattern, text, flags=re.IGNORECASE) is not None
        for modifier, pattern in _MODIFIER_PATTERNS.items()
    }
    for modifier in CANONICAL_MODIFIERS:
        modifiers.setdefault(modifier, False)
    for modifier, enabled in dict(explicit_modifiers or {}).items():
        if modifier in modifiers:
            modifiers[modifier] = bool(enabled)
    return modifiers


def resolve_message_type(
    *,
    intent_text: str = "",
    message_type_hint: str = "",
    explicit_modifiers: Mapping[str, bool] | None = None,
) -> MessageTypeResolution:
    """Resolve apps_lic message_type and modifiers deterministically."""
    combined_text = _clean(f"{message_type_hint} {intent_text}")
    hint_match = _canonical_hint(message_type_hint)
    reason_codes: list[str] = []
    if hint_match:
        message_type, matched_alias = hint_match
        source = "u0_hint_normalized"
        reason_codes.append(f"hint:{matched_alias}")
    else:
        message_type, reason_code = _infer_message_type(combined_text)
        source = "intent_text"
        reason_codes.append(reason_code)

    modifiers = _resolve_modifiers(combined_text, explicit_modifiers)
    if message_type == MESSAGE_ROLE_SPECIFIC:
        modifiers[MODIFIER_USES_JD] = True
    if message_type == MESSAGE_TRIGGER_BASED_INSIGHT:
        modifiers[MODIFIER_USES_COMPANY_TRIGGER] = True
    if message_type == MESSAGE_REFERRAL_ASK:
        modifiers[MODIFIER_USES_REFERRAL_CONTEXT] = True
    if message_type == MESSAGE_FOLLOW_UP:
        modifiers[MODIFIER_USES_PRIOR_THREAD] = True

    reason_codes.extend(
        f"modifier:{modifier}"
        for modifier, enabled in modifiers.items()
        if enabled
    )
    return MessageTypeResolution(
        message_type=message_type,
        modifiers=modifiers,
        source=source,
        reason_codes=tuple(dict.fromkeys(reason_codes)),
        normalized_hint=_normalize_hint(message_type_hint),
        intent_digest=_digest({"hint": message_type_hint, "intent": intent_text}),
    )


def _docs_by_namespace(
    documents: Iterable[OpportunityFactDocument],
) -> dict[str, tuple[OpportunityFactDocument, ...]]:
    grouped: dict[str, list[OpportunityFactDocument]] = {}
    for document in documents:
        grouped.setdefault(document.namespace, []).append(document)
    return {namespace: tuple(items) for namespace, items in grouped.items()}


def _metadata_value(
    documents: Iterable[OpportunityFactDocument],
    *field_names: str,
) -> str:
    for document in documents:
        metadata = dict(document.metadata)
        for field_name in field_names:
            value = _clean(metadata.get(field_name))
            if value:
                return value
    return ""


def _has_application_status(
    documents: Iterable[OpportunityFactDocument],
    application_status: str,
) -> bool:
    if _clean(application_status):
        return True
    return bool(_metadata_value(documents, "application_status", "candidate_status"))


def _needs_jd(
    resolution: MessageTypeResolution,
) -> bool:
    return (
        resolution.message_type == MESSAGE_ROLE_SPECIFIC
        or bool(resolution.modifiers.get(MODIFIER_USES_JD))
    )


def _needs_position_name(
    resolution: MessageTypeResolution,
    recipient_class: str,
) -> bool:
    return _needs_jd(resolution) or (
        resolution.message_type == MESSAGE_ROLE_SPECIFIC
        and recipient_class == CLASS_HIRING_MANAGER
    )


def _needs_requisition_number(
    resolution: MessageTypeResolution,
    recipient_class: str,
) -> bool:
    return recipient_class in {CLASS_RECRUITER, CLASS_SENIOR_TA} and _needs_jd(resolution)


def _needs_relationship_context(
    resolution: MessageTypeResolution,
    intent_text: str,
    message_type_hint: str,
) -> bool:
    text = _clean(f"{message_type_hint} {intent_text}")
    return resolution.message_type == MESSAGE_REFERRAL_ASK or bool(_RELATIONSHIP_PATTERN.search(text))


def _add_missing(missing: list[str], status: str) -> None:
    if status not in missing:
        missing.append(status)


def _add_namespace(required: list[str], namespace: str) -> None:
    if namespace not in required:
        required.append(namespace)


def evaluate_message_requirements(
    *,
    recipient_derivation: RecipientClassDerivation,
    documents: Iterable[OpportunityFactDocument],
    intent_text: str = "",
    message_type_hint: str = "",
    explicit_modifiers: Mapping[str, bool] | None = None,
    application_status: str = "",
) -> MessageRequirementGateResult:
    """Gate message requirements after W3 recipient_class derivation."""
    resolution = resolve_message_type(
        intent_text=intent_text,
        message_type_hint=message_type_hint,
        explicit_modifiers=explicit_modifiers,
    )
    document_tuple = tuple(documents)
    grouped = _docs_by_namespace(document_tuple)
    recipient_class = recipient_derivation.derived_recipient_class
    missing: list[str] = []
    required_namespaces: list[str] = []
    reason_codes: list[str] = list(resolution.reason_codes)

    if (
        recipient_derivation.status != RECIPIENT_STATUS_DERIVED
        or recipient_class == CLASS_UNKNOWN
    ):
        _add_missing(missing, RECIPIENT_CLASS_NOT_DERIVED)
        reason_codes.append("recipient_class_gate:blocked")

    jd_docs = grouped.get(NAMESPACE_JD, ())
    if _needs_jd(resolution):
        _add_namespace(required_namespaces, NAMESPACE_JD)
        if not jd_docs:
            _add_missing(missing, MISSING_JD_FACTS)
        else:
            if _needs_position_name(resolution, recipient_class) and not _metadata_value(
                jd_docs,
                "position_name",
                "job_title",
                "title",
            ):
                _add_missing(missing, MISSING_POSITION_NAME)
            if _needs_requisition_number(resolution, recipient_class) and not _metadata_value(
                jd_docs,
                "requisition_number",
                "req_id",
                "job_id",
            ):
                _add_missing(missing, MISSING_REQUISITION_NUMBER)

    if resolution.modifiers.get(MODIFIER_APPLICATION_STATUS_CLAIMED):
        if not _has_application_status(document_tuple, application_status):
            _add_missing(missing, MISSING_APPLICATION_STATUS)

    if (
        resolution.message_type == MESSAGE_FOLLOW_UP
        or resolution.modifiers.get(MODIFIER_USES_PRIOR_THREAD)
    ):
        _add_namespace(required_namespaces, NAMESPACE_PRIOR_THREAD)
        if not grouped.get(NAMESPACE_PRIOR_THREAD):
            _add_missing(missing, MISSING_PRIOR_THREAD)

    if (
        resolution.message_type == MESSAGE_REFERRAL_ASK
        or resolution.modifiers.get(MODIFIER_USES_REFERRAL_CONTEXT)
    ):
        _add_namespace(required_namespaces, NAMESPACE_REFERRAL)
        if not grouped.get(NAMESPACE_REFERRAL):
            _add_missing(missing, MISSING_REFERRER_CONTEXT)

    if _needs_relationship_context(resolution, intent_text, message_type_hint):
        _add_namespace(required_namespaces, NAMESPACE_RELATIONSHIP)
        if not grouped.get(NAMESPACE_RELATIONSHIP):
            _add_missing(missing, MISSING_RELATIONSHIP_CONTEXT)

    if (
        resolution.message_type == MESSAGE_TRIGGER_BASED_INSIGHT
        or resolution.modifiers.get(MODIFIER_USES_COMPANY_TRIGGER)
    ):
        _add_namespace(required_namespaces, NAMESPACE_COMPANY_TRIGGER)
        if not grouped.get(NAMESPACE_COMPANY_TRIGGER):
            _add_missing(missing, MISSING_COMPANY_TRIGGER)

    if resolution.modifiers.get(MODIFIER_USES_SENSITIVE_CONSTRAINTS):
        reason_codes.append("sensitive_constraints:downstream_scrutiny_required")

    allowed = not missing
    status = STATUS_REQUIREMENTS_PASS if allowed else STATUS_REQUIREMENTS_BLOCKED
    source_snapshot_ids = tuple(
        dict.fromkeys(document.source_snapshot_id for document in document_tuple)
    )
    return MessageRequirementGateResult(
        status=status,
        allowed=allowed,
        message_type=resolution.message_type,
        modifiers=dict(resolution.modifiers),
        recipient_class=recipient_class,
        missing_fields=tuple(missing),
        required_namespaces=tuple(required_namespaces),
        reason_codes=tuple(dict.fromkeys(reason_codes)),
        source_snapshot_ids=source_snapshot_ids,
        resolution=resolution,
    )


def evaluate_message_requirements_from_store(
    *,
    store: OpportunityFactStore,
    recipient_derivation: RecipientClassDerivation,
    intent_text: str = "",
    message_type_hint: str = "",
    explicit_modifiers: Mapping[str, bool] | None = None,
    application_status: str = "",
) -> MessageRequirementGateResult:
    """Read W2 opportunity facts from the store and run the W4 gate."""
    documents: list[OpportunityFactDocument] = []
    for namespace in (
        NAMESPACE_JD,
        NAMESPACE_COMPANY_TRIGGER,
        NAMESPACE_REFERRAL,
        NAMESPACE_RELATIONSHIP,
        NAMESPACE_PRIOR_THREAD,
    ):
        documents.extend(store.query_namespace(namespace))
    return evaluate_message_requirements(
        recipient_derivation=recipient_derivation,
        documents=documents,
        intent_text=intent_text,
        message_type_hint=message_type_hint,
        explicit_modifiers=explicit_modifiers,
        application_status=application_status,
    )


__all__ = [
    "CANONICAL_MESSAGE_TYPES",
    "CANONICAL_MODIFIERS",
    "MESSAGE_FOLLOW_UP",
    "MESSAGE_GENERAL_INTRO",
    "MESSAGE_REFERRAL_ASK",
    "MESSAGE_ROLE_SPECIFIC",
    "MESSAGE_TRIGGER_BASED_INSIGHT",
    "MISSING_APPLICATION_STATUS",
    "MISSING_COMPANY_TRIGGER",
    "MISSING_JD_FACTS",
    "MISSING_POSITION_NAME",
    "MISSING_PRIOR_THREAD",
    "MISSING_REFERRER_CONTEXT",
    "MISSING_RELATIONSHIP_CONTEXT",
    "MISSING_REQUISITION_NUMBER",
    "MODIFIER_APPLICATION_STATUS_CLAIMED",
    "MODIFIER_USES_COMPANY_TRIGGER",
    "MODIFIER_USES_JD",
    "MODIFIER_USES_PRIOR_THREAD",
    "MODIFIER_USES_REFERRAL_CONTEXT",
    "MODIFIER_USES_SENSITIVE_CONSTRAINTS",
    "RECIPIENT_CLASS_NOT_DERIVED",
    "STATUS_REQUIREMENTS_BLOCKED",
    "STATUS_REQUIREMENTS_PASS",
    "MessageRequirementGateResult",
    "MessageTypeResolution",
    "evaluate_message_requirements",
    "evaluate_message_requirements_from_store",
    "resolve_message_type",
]
