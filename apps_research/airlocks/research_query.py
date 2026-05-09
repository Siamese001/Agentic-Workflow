"""Research Query Airlock — R3_SIMPLE_GROUNDED_READ route boundary gate.

Validates research topic/query text before it enters C0 retrieval and the
LLM synthesis pipeline (company_brief_engine._synthesize).

Per PROMPT_BOUNDARY_CONTRACT.md §3.1: user-provided research topic is
untrusted until cleared by the U0 airlock. Prompt injection via a crafted
topic string is possible when the topic is embedded verbatim in the synthesis
prompt.

Plan: apps-research-pa-spine-hardening-a28ea8 W3
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from apps_research.airlocks._otel_spans import airlock_span, emit_airlock_event

_log = logging.getLogger(__name__)
_AIRLOCK_ID = "U0_RESEARCH_QUERY"

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

_MAX_TOPIC_LENGTH = 2048


class ResearchQueryStatus(str, Enum):
    CLEARED = "CLEARED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ResearchQueryReceipt:
    topic_hash: str
    status: str
    topic_length: int
    flagged_signals: list[str]
    audit_trail: dict[str, Any]


def validate_research_query(
    topic: str,
    *,
    request_id: str = "",
    run_id: str = "",
    mode: str = "",
) -> ResearchQueryReceipt:
    """Validate research topic before C0 retrieval + LLM synthesis dispatch.

    Args:
        topic: Raw research topic/query string.
        request_id: Correlation id for tracing.
        run_id: Run identifier.
        mode: Research mode (e.g. 'company', 'topic').

    Returns:
        ResearchQueryReceipt. Never raises — fail-soft.
    """
    flagged: list[str] = []
    try:
        q_lower = topic.lower()
        for signal in _INJECTION_SIGNALS:
            if signal in q_lower:
                flagged.append(signal)
    except Exception:  # guardian: allow-broad-exception -- fail-soft airlock boundary
        _log.warning("[%s] unexpected error during topic validation", _AIRLOCK_ID)
        flagged.append("_parse_error")

    topic_hash = hashlib.sha256(topic.encode("utf-8", errors="replace")).hexdigest()[:16]
    status = ResearchQueryStatus.QUARANTINED if flagged else ResearchQueryStatus.CLEARED

    audit_trail: dict[str, Any] = {
        "airlock": _AIRLOCK_ID,
        "request_id": request_id,
        "run_id": run_id,
        "mode": mode,
        "topic_length": len(topic),
        "flagged_signals": flagged,
        "status": status.value,
    }

    span_name = (
        "pa.airlock_security_pass" if status == ResearchQueryStatus.CLEARED else "pa.injection_neutralization"
    )
    with airlock_span(
        span_name,
        airlock=_AIRLOCK_ID,
        request_id=request_id,
        run_id=run_id,
        mode=mode,
        status=status.value,
        flagged_count=len(flagged),
    ) as span:
        if flagged:
            emit_airlock_event(span, "pa.injection_neutralized", flagged_signals=str(flagged))
        _log.debug("[%s] status=%s len=%d flagged=%d", _AIRLOCK_ID, status.value, len(topic), len(flagged))

    return ResearchQueryReceipt(
        topic_hash=topic_hash,
        status=status.value,
        topic_length=len(topic),
        flagged_signals=flagged,
        audit_trail=audit_trail,
    )
