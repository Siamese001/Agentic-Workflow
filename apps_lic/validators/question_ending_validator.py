"""Question-ending validator for outreach messages.

W2-P6 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Empirical rule: LinkedIn outreach messages that end in a question mark
convert at ~1.4x the reply rate of statement-ending messages for
executive and senior-TA audiences. This validator enforces question-
ending for those archetypes and returns a structured result HOP6 can
consume to route the message back to HOP5 for regeneration.

Archetypes that REQUIRE a question-ending message (hard gate):
    - EXECUTIVE
    - C_LEVEL
    - SENIOR_TA

Archetypes where question-ending is OPTIONAL (soft — validator passes
either way):
    - RECRUITER (pipeline-pitch framing often ends in statement)
    - OTHER
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable, Optional

# Archetypes for which the ending-question rule is a hard gate.
REQUIRED_QUESTION_ARCHETYPES: Final[frozenset[str]] = frozenset(
    {"EXECUTIVE", "C_LEVEL", "SENIOR_TA"}
)

# Terminal punctuation that counts as a question. Ordered for explicit
# documentation: "?" is canonical; a trailing "?!" also counts. A period
# or exclamation-only ending does not.
_QUESTION_TERMINATORS: Final[tuple[str, ...]] = ("?", "?!", "??")

# Signature lines that often trail the functional body of a message.
# Stripped before the terminator check so messages with a formal
# signature (e.g., "Regards, Jane") are still evaluated on their
# outreach body. Signatures are detected by line-prefix match on a
# normalised lowercase form.
_SIGNATURE_PREFIXES: Final[tuple[str, ...]] = (
    "regards",
    "best",
    "thanks",
    "thank you",
    "cheers",
    "sincerely",
    "kind regards",
    "warm regards",
    "yours",
)


@dataclass(frozen=True)
class QuestionEndingResult:
    """Result of a single question-ending validation.

    Attributes:
        is_valid: True when the message is acceptable for the archetype.
            For non-required archetypes, always True.
        archetype: Echo of the requested archetype.
        ends_in_question: Whether the functional body terminates in
            a question-mark terminator.
        required_for_archetype: Whether question-ending was enforced.
        reason: Human-readable reason string. Empty when valid.
        last_char: The last meaningful character of the body. Useful
            for logging / operator triage.
    """

    is_valid: bool
    archetype: str
    ends_in_question: bool
    required_for_archetype: bool
    reason: str
    last_char: str


def validate_question_ending(text: str, archetype: str) -> QuestionEndingResult:
    """Pure-function question-ending check.

    Strips trailing signature lines, trailing whitespace, and trailing
    empty lines before inspecting the terminator. A message that ends
    with any of ``_QUESTION_TERMINATORS`` counts as question-ending.

    Args:
        text: Full message body (pre-dispatch).
        archetype: One of the five canonical ProfilePlanner archetypes.
            Unknown archetypes are treated as non-required (validator
            passes regardless of terminator).

    Returns:
        ``QuestionEndingResult`` with every field populated. Never raises.
    """
    required = archetype in REQUIRED_QUESTION_ARCHETYPES
    body = _strip_signature(text or "")
    if not body.strip():
        # Empty body — other validators catch this. Pass through here.
        return QuestionEndingResult(
            is_valid=True,
            archetype=archetype,
            ends_in_question=False,
            required_for_archetype=required,
            reason="",
            last_char="",
        )
    ends_q = any(body.rstrip().endswith(term) for term in _QUESTION_TERMINATORS)
    last_char = body.rstrip()[-1]
    if not required or ends_q:
        return QuestionEndingResult(
            is_valid=True,
            archetype=archetype,
            ends_in_question=ends_q,
            required_for_archetype=required,
            reason="",
            last_char=last_char,
        )
    reason = (
        f"Outreach to {archetype} must end in a question; last character "
        f"was {last_char!r}. Regenerate with a soft-question close."
    )
    return QuestionEndingResult(
        is_valid=False,
        archetype=archetype,
        ends_in_question=False,
        required_for_archetype=required,
        reason=reason,
        last_char=last_char,
    )


class QuestionEndingValidator:
    """Stateful wrapper for HOP6 wiring with telemetry emission.

    Behaviour identical to ``validate_question_ending`` except it emits
    a ``question_ending_violation`` telemetry event when the validator
    rejects a message.
    """

    def __init__(self, telemetry_bus: Optional[object] = None) -> None:
        self._telemetry_bus = telemetry_bus

    def validate(self, text: str, archetype: str) -> QuestionEndingResult:
        result = validate_question_ending(text, archetype)
        if not result.is_valid and self._telemetry_bus is not None:
            try:
                self._telemetry_bus.record(
                    "question_ending_violation",
                    {
                        "archetype": result.archetype,
                        "last_char": result.last_char,
                        "required_for_archetype": result.required_for_archetype,
                    },
                )
            except (AttributeError, TypeError, RuntimeError, ValueError, OSError):  # guardian: allow-log-and-swallow -- telemetry must never break validation
                pass
        return result


# ----------------------------------------------------------------------
# Internals
# ----------------------------------------------------------------------


def _strip_signature(text: str) -> str:
    """Return ``text`` with a trailing signature block removed.

    Scans bottom-up for the first non-empty line and, if it starts with
    a known sign-off prefix, drops every line from that line onward.
    Also drops trailing empty lines regardless.
    """
    if not text:
        return text
    lines = text.splitlines()
    # Strip trailing blank lines first.
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""
    # Heuristic: if any of the last 4 lines starts with a sign-off prefix,
    # treat that line and everything after it as signature.
    scan_window = min(4, len(lines))
    cut_index: int | None = None
    for offset in range(1, scan_window + 1):
        idx = len(lines) - offset
        candidate = lines[idx].strip().lower().rstrip(",. ")
        if _has_signature_prefix(candidate):
            cut_index = idx
            break
    if cut_index is not None:
        lines = lines[:cut_index]
        while lines and not lines[-1].strip():
            lines.pop()
    return "\n".join(lines)


def _has_signature_prefix(line: str) -> bool:
    """Return True if ``line`` opens with a known signature prefix."""
    for prefix in _SIGNATURE_PREFIXES:
        if line == prefix or line.startswith(prefix + " ") or line.startswith(prefix + ","):
            return True
    return False


__all__ = [
    "REQUIRED_QUESTION_ARCHETYPES",
    "QuestionEndingResult",
    "QuestionEndingValidator",
    "validate_question_ending",
]
