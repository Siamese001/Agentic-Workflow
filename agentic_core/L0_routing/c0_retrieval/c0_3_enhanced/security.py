"""Phase 6 — graph text is data, never instruction.

Detect instruction-like payloads inside neighbor previews / payloads. Reuses
patterns from the existing C0 ``injection`` module and adds C0.3-specific
markers (e.g. "approve this request", "delete this record", "bypass policy").
"""

from __future__ import annotations

import re

from .adapter import GraphNeighbor
from .contracts import InstructionPayloadFlag, SupportTarget


_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ignore_previous_instructions",
        re.compile(
            r"\bignore\s+(?:all\s+|the\s+)?(?:previous|prior|above)?\s*(?:instructions?|prompts?|rules?)\b",
            re.I,
        ),
    ),
    (
        "system_role_injection",
        re.compile(r"^\s*(system|assistant|user)\s*[:>\]]", re.I | re.M),
    ),
    (
        "override_safety",
        re.compile(
            r"\b(override|bypass|disable|disregard)\s+(safety|guard|policy|rules?|restrictions?|filter|acl)\b",
            re.I,
        ),
    ),
    (
        "you_are_now_allowed_to",
        re.compile(r"\byou\s+are\s+now\s+(?:allowed|permitted|authorized)\s+to\b", re.I),
    ),
    (
        "change_your_system_prompt",
        re.compile(
            r"\b(change|update|replace|edit)\s+your\s+(system\s+prompt|rules|instructions)\b",
            re.I,
        ),
    ),
    (
        "execute_directive",
        re.compile(r"\b(run|execute|invoke|call)\s+(this\s+command|the\s+following)\b", re.I),
    ),
    (
        "send_email",
        re.compile(r"\bsend\s+(this\s+)?(email|message)\s+to\b", re.I),
    ),
    (
        "approve_request",
        re.compile(r"\b(approve|deny|reject)\s+(this\s+)?(request|ticket|change)\b", re.I),
    ),
    (
        "delete_record",
        re.compile(r"\b(delete|drop|truncate|purge)\s+(this\s+)?(record|row|table|file|database)\b", re.I),
    ),
    (
        "credential_exfiltration",
        re.compile(
            r"\b(reveal|print|show|leak|dump)\s+(your\s+)?(system\s+prompt|api\s+key|token|secret|credential)\b",
            re.I,
        ),
    ),
    (
        "delimiter_breakout",
        re.compile(
            r"(```\s*end\s+of\s+context|---\s*end\s+of\s+context|<\s*/?\s*system\s*>|\[\s*/?\s*INST\s*\])",
            re.I,
        ),
    ),
)


def detect_instruction_payload(text: str | None) -> tuple[str, ...]:
    if not text or not isinstance(text, str):
        return ()
    found: list[str] = []
    for label, pattern in _PATTERNS:
        if pattern.search(text):
            found.append(label)
    return tuple(found)


def quarantine_neighbor_payload(
    neighbor: GraphNeighbor,
    *,
    support_target: SupportTarget | str,
    max_preview: int = 200,
) -> InstructionPayloadFlag | None:
    """If the neighbor's payload looks like an instruction, return a flag.

    The flag instructs C0.3 to:
      - exclude the payload from prompt-eligible context (always),
      - allow access only when ``support_target`` is the security analysis
        family (CLAIM_CHECK / GOVERNANCE_DECISION are NOT a security analysis;
        we treat only an explicit ``security_analysis`` string as such).
    """
    text = neighbor.payload_preview or ""
    markers = detect_instruction_payload(text)
    if not markers:
        return None
    target_str = support_target.value if isinstance(support_target, SupportTarget) else str(support_target)
    is_security = target_str.lower() in {"security_analysis", "security_review"}
    return InstructionPayloadFlag(
        neighbor_id=neighbor.node_id,
        matched_markers=markers,
        quarantined_preview=repr(text[:max_preview]),
        excluded_from_prompt=True,
        allowed_for_security_analysis=is_security,
    )


__all__ = ["detect_instruction_payload", "quarantine_neighbor_payload"]
