"""User Question Airlock — R4_SINGLE_ACTION live-interview route boundary gate.

Validates user-provided interview question text before it is dispatched to
the LLM (via provider_dispatch.py or intent_classifier.py).

Per PROMPT_BOUNDARY_CONTRACT.md §3.1: user question text is untrusted until
cleared by the U0 airlock. Prompt injection via crafted question text is a
realistic attack surface when the question is included verbatim in the LLM
prompt.

Plan: .windsurf/plans/apps-qna-pa-spine-hardening-498d20.md W3.1
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from apps_qna.airlocks._otel_spans import airlock_span, emit_airlock_event

_log = logging.getLogger(__name__)

_AIRLOCK_ID = "U0_USER_QUESTION"

_INJECTION_SIGNALS = (
    "ignore previous instructions",
    "disregard the above",
    "you are now",
    "system:",
    "assistant:",
    "<|im_start|>",
    "<|im_end|>",
    "[[",
    "]]",
)

_MAX_QUESTION_LENGTH = 2048


class UserQuestionStatus(str, Enum):
    """Status of user question validation."""

    CLEARED = "CLEARED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class UserQuestionReceipt:
    """Receipt emitted by the user question airlock."""

    question_hash: str
    status: str
    question_length: int
    flagged_signals: list[str]
    audit_trail: dict[str, Any]


def validate_user_question(
    question: str,
    *,
    request_id: str = "",
    run_id: str = "",
    route_id: str = "",
) -> UserQuestionReceipt:
    """Validate user question text before LLM dispatch.

    Args:
        question: Raw user question string.
        request_id: Correlation id for tracing.
        run_id: Run identifier.
        route_id: Selected route id for tracing.

    Returns:
        UserQuestionReceipt with CLEARED, QUARANTINED, or REJECTED status.
        Never raises — fail-soft on unexpected input.
    """
    flagged: list[str] = []

    try:
        q_lower = question.lower()
        for signal in _INJECTION_SIGNALS:
            if signal in q_lower:
                flagged.append(signal)
    except Exception:  # guardian: allow-broad-exception -- fail-soft airlock boundary
        _log.warning("[%s] unexpected error during question validation", _AIRLOCK_ID)
        flagged.append("_parse_error")

    truncated = len(question) > _MAX_QUESTION_LENGTH

    question_hash = hashlib.sha256(question.encode("utf-8", errors="replace")).hexdigest()[:16]

    if flagged:
        status = UserQuestionStatus.QUARANTINED
    else:
        status = UserQuestionStatus.CLEARED

    audit_trail: dict[str, Any] = {
        "airlock": _AIRLOCK_ID,
        "request_id": request_id,
        "run_id": run_id,
        "route_id": route_id,
        "question_length": len(question),
        "truncated": truncated,
        "flagged_signals": flagged,
        "status": status.value,
    }

    span_name = (
        "pa.airlock_security_pass" if status == UserQuestionStatus.CLEARED else "pa.injection_neutralization"
    )

    with airlock_span(
        span_name,
        airlock=_AIRLOCK_ID,
        request_id=request_id,
        run_id=run_id,
        route_id=route_id,
        status=status.value,
        question_length=len(question),
        flagged_count=len(flagged),
    ) as span:
        if flagged:
            emit_airlock_event(span, "pa.injection_neutralized", flagged_signals=str(flagged))
        _log.debug(
            "[%s] status=%s len=%d flagged=%d",
            _AIRLOCK_ID,
            status.value,
            len(question),
            len(flagged),
        )

    return UserQuestionReceipt(
        question_hash=question_hash,
        status=status.value,
        question_length=len(question),
        flagged_signals=flagged,
        audit_trail=audit_trail,
    )
