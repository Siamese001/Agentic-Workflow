"""PA.3 U0 Airlock — formal record for the user-task neutralization step.

Wraps the existing
:class:`agentic_core.prompt_governance.security.assembly_injection_neutralizer.AssemblyInjectionNeutralizer`
and produces a typed :class:`U0AirlockResult` matching the spec
(lines 893–960):

  * raw_text_hash + neutralized_text_hash + injection_score
  * disposition ∈ {clean, sanitized, reject}
  * stripped_segments + retained_constraints
  * origin_trust = "user_turn" enforced
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from agentic_core.prompt_governance.security.assembly_injection_neutralizer import (
    AssemblyInjectionNeutralizer,
    NeutralizationResult,
)

REJECT_THRESHOLD: float = 0.85
"""Above this injection score, the U0 task is REJECTED rather than sanitized."""


@dataclass(frozen=True)
class U0AirlockResult:
    """Spec PA.3 U0 airlock literal."""

    raw_text: str
    neutralized_text: str
    raw_text_hash: str
    neutralized_text_hash: str
    injection_score: float
    disposition: str  # clean | sanitized | reject
    detected_patterns: tuple[str, ...]
    stripped_segments: tuple[str, ...]
    retained_constraints: tuple[str, ...]
    origin_trust: str = "user_turn"

    @property
    def safe_to_proceed(self) -> bool:
        return self.disposition in {"clean", "sanitized"}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _injection_score_from(patterns: tuple[str, ...]) -> float:
    if not patterns:
        return 0.0
    high_severity = {
        "ROLE_PLAY_HIJACK",
        "PROMPT_LEAKING_ATTACK",
    }
    base = 0.4
    if any(p in high_severity for p in patterns):
        base = 0.9
    elif "IGNORE_INSTRUCTIONS_ATTACK" in patterns:
        base = 0.6
    return min(1.0, base + 0.05 * (len(patterns) - 1))


def run_u0_airlock(
    raw_user_task: str,
    *,
    neutralizer: AssemblyInjectionNeutralizer | None = None,
    reject_threshold: float = REJECT_THRESHOLD,
    retained_constraints: tuple[str, ...] = (),
) -> U0AirlockResult:
    """Run the U0 airlock on the raw user task and return a typed record."""
    if neutralizer is None:
        neutralizer = AssemblyInjectionNeutralizer()
    result: NeutralizationResult = neutralizer.neutralize(raw_user_task or "")
    patterns = tuple(result.detection_patterns)
    score = _injection_score_from(patterns)
    if score >= reject_threshold:
        disposition = "reject"
        neutralized = ""
    elif patterns:
        disposition = "sanitized"
        neutralized = result.sanitized_prompt
    else:
        disposition = "clean"
        neutralized = result.sanitized_prompt or raw_user_task

    # B4 hardening: be precise. Only emit stripped_segments when the
    # neutralizer's edit was a clean prefix / suffix trim. If the edit is
    # internal we cannot reliably attribute a segment, so we return ().
    # Reject disposition emits the entire raw input so audit logs see what
    # was suppressed.
    stripped_segments: list[str] = []
    if disposition == "reject":
        if raw_user_task:
            stripped_segments.append(raw_user_task)
    elif disposition == "sanitized" and patterns:
        raw_str = raw_user_task or ""
        if raw_str and neutralized and raw_str != neutralized and len(raw_str) > len(neutralized):
            if raw_str.startswith(neutralized):
                stripped_segments.append(raw_str[len(neutralized) :])
            elif raw_str.endswith(neutralized):
                stripped_segments.append(raw_str[: -len(neutralized)])
            # else: an internal edit — do NOT fabricate a whole-text marker.

    return U0AirlockResult(
        raw_text=raw_user_task or "",
        neutralized_text=neutralized,
        raw_text_hash=_sha(raw_user_task or ""),
        neutralized_text_hash=_sha(neutralized),
        injection_score=score,
        disposition=disposition,
        detected_patterns=patterns,
        stripped_segments=tuple(stripped_segments),
        retained_constraints=retained_constraints,
        origin_trust="user_turn",
    )


__all__ = ["REJECT_THRESHOLD", "U0AirlockResult", "run_u0_airlock"]
