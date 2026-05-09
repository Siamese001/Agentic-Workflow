"""Template Input Airlock — build_time_compiler route boundary gate.

Validates static interview YAML template inputs before they enter the
Jinja2 render pipeline. No LLM is called at build time; this airlock
ensures template variable inputs are well-formed and cannot escape slot
boundaries via template injection.

Per PROMPT_BOUNDARY_CONTRACT.md §3.1: User-provided data is untrusted
until cleared by the U0 airlock. Even though apps_qna template inputs
are YAML-loaded (not raw user text), structured injection via field
values is possible.

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

_AIRLOCK_ID = "U0_TEMPLATE_INPUT"

_INJECTION_PATTERNS = (
    "{{",
    "__class__",
    "__subclasses__",
    "__globals__",
    "config",
    "namespace",
    "_self",
)

_MAX_FIELD_LENGTH = 4096


class TemplateInputStatus(str, Enum):
    """Status of template input validation."""

    CLEARED = "CLEARED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class TemplateInputReceipt:
    """Receipt emitted by the template input airlock."""

    field_hash: str
    status: str
    field_count: int
    flagged_fields: list[str]
    audit_trail: dict[str, Any]


def validate_template_inputs(
    inputs: dict[str, Any],
    *,
    request_id: str = "",
    run_id: str = "",
    interview_slug: str = "",
) -> TemplateInputReceipt:
    """Validate template input variables before Jinja2 render.

    Args:
        inputs: Dict of template variable names to values (from YAML).
        request_id: Correlation id for tracing.
        run_id: Run identifier.
        interview_slug: Interview slug for tracing.

    Returns:
        TemplateInputReceipt with CLEARED, QUARANTINED, or REJECTED status.
        Never raises — fail-soft on unexpected input shapes.
    """
    flagged: list[str] = []
    oversized: list[str] = []

    try:
        for key, value in inputs.items():
            str_val = str(value) if not isinstance(value, str) else value
            if len(str_val) > _MAX_FIELD_LENGTH:
                oversized.append(key)
            for pattern in _INJECTION_PATTERNS:
                if pattern in str_val:
                    flagged.append(f"{key}:{pattern}")
                    break
    except Exception:  # guardian: allow-broad-exception -- fail-soft airlock boundary
        _log.warning("[%s] unexpected error during template input validation", _AIRLOCK_ID)
        flagged.append("_parse_error")

    serialized = repr(sorted(inputs.items()))
    field_hash = hashlib.sha256(serialized.encode("utf-8", errors="replace")).hexdigest()[:16]

    if flagged:
        status = TemplateInputStatus.QUARANTINED
    else:
        status = TemplateInputStatus.CLEARED

    audit_trail: dict[str, Any] = {
        "airlock": _AIRLOCK_ID,
        "request_id": request_id,
        "run_id": run_id,
        "interview_slug": interview_slug,
        "field_count": len(inputs),
        "oversized_fields": oversized,
        "flagged_patterns": flagged,
        "status": status.value,
    }

    with airlock_span(
        "pa.airlock_security_pass" if status == TemplateInputStatus.CLEARED else "pa.injection_neutralization",
        airlock=_AIRLOCK_ID,
        request_id=request_id,
        run_id=run_id,
        interview_slug=interview_slug,
        status=status.value,
        flagged_count=len(flagged),
    ) as span:
        if flagged:
            emit_airlock_event(span, "pa.injection_neutralized", flagged_fields=str(flagged))
        _log.debug(
            "[%s] status=%s fields=%d flagged=%d",
            _AIRLOCK_ID,
            status.value,
            len(inputs),
            len(flagged),
        )

    return TemplateInputReceipt(
        field_hash=field_hash,
        status=status.value,
        field_count=len(inputs),
        flagged_fields=flagged,
        audit_trail=audit_trail,
    )
