"""Archetype-specific message length validator.

W1-P2 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

LinkedIn InMail / cold outreach industry data shows the sharpest cliff in
reply rate at message length:

    - 0-400 chars: baseline reply rate
    - 400-800 chars: ~0.6x baseline
    - 800+ chars:    ~0.4x baseline (EXECUTIVE audiences drop to ~0.25x)

Different recipient archetypes tolerate different message ceilings. The
caps below are derived from per-archetype A/B buckets:

    EXECUTIVE : 400   ("one strategic paragraph" ceiling)
    C_LEVEL   : 400   (same as EXECUTIVE — brevity is deference)
    SENIOR_TA : 600   (pipeline pitches need a touch more room)
    RECRUITER : 500   (mid-tier — filter-framing needs brief context)
    OTHER     : 500   (general default)

The validator operates as a pure function + a stateful class. The pure
``validate_length(text, archetype)`` path is suitable for HOP6
``ValidationAgent`` integration; the class path is suitable for pipeline
wiring where additional config (telemetry, telemetry bus) is needed.

Design choices:

1. Validation is **hard-gate** — a message over the cap returns
   ``is_valid=False`` with the excess count and the cap. Callers decide
   whether to regenerate (HOP5 with shorter-message hint) or truncate.
2. Archetype matching is **case-sensitive** for the five canonical labels
   and falls back to the OTHER cap for unknown archetypes. This matches
   the same fallback discipline used by
   ``subject_line_bandit_config.admissible_variants_for``.
3. Length counted is ``len(text.strip())`` — whitespace padding does not
   exempt a message from the cap, but leading/trailing whitespace is
   ignored per LinkedIn's own counting behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Mapping, Optional

# SSOT for the archetype → max-character mapping. Change values here only
# after an A/B experiment justifies the new cap. Downstream reporting
# scripts read from this dict — do not duplicate the numbers elsewhere.
ARCHETYPE_LENGTH_CAPS: Final[Mapping[str, int]] = {
    "EXECUTIVE": 400,
    "C_LEVEL":   400,
    "SENIOR_TA": 600,
    "RECRUITER": 500,
    "OTHER":     500,
}

# Fallback cap for archetypes not in the canonical set. Defensive: when
# the profile planner emits a new archetype label, validator continues
# to function at the general default rather than raising.
DEFAULT_LENGTH_CAP: Final[int] = ARCHETYPE_LENGTH_CAPS["OTHER"]


@dataclass(frozen=True)
class LengthValidationResult:
    """Result of a single length validation.

    Attributes:
        is_valid: True when the message is at or below the cap.
        archetype: Echo of the requested archetype.
        message_length: Post-strip length of the message in characters.
        cap: The cap applied for this archetype.
        excess: ``max(0, message_length - cap)``. Zero when valid.
        reason: Human-readable reason string. Empty when valid.
    """

    is_valid: bool
    archetype: str
    message_length: int
    cap: int
    excess: int
    reason: str


def cap_for(archetype: str) -> int:
    """Return the length cap for ``archetype`` with OTHER fallback."""
    return ARCHETYPE_LENGTH_CAPS.get(archetype, DEFAULT_LENGTH_CAP)


def validate_length(text: str, archetype: str) -> LengthValidationResult:
    """Pure-function length validation.

    Args:
        text: The outreach message body. Leading / trailing whitespace is
            stripped before counting, matching LinkedIn's counting.
        archetype: One of the five canonical archetypes. Unknown values
            fall back to the OTHER cap (500).

    Returns:
        ``LengthValidationResult`` with all fields populated. Zero-length
        strings are considered valid (they fail other validators, not
        this one).
    """
    stripped = text.strip() if text else ""
    length = len(stripped)
    cap = cap_for(archetype)
    if length <= cap:
        return LengthValidationResult(
            is_valid=True,
            archetype=archetype,
            message_length=length,
            cap=cap,
            excess=0,
            reason="",
        )
    excess = length - cap
    return LengthValidationResult(
        is_valid=False,
        archetype=archetype,
        message_length=length,
        cap=cap,
        excess=excess,
        reason=(
            f"Message length {length} exceeds the {archetype} cap of {cap} "
            f"by {excess} characters. Shorten before dispatch."
        ),
    )


class ArchetypeMessageLengthValidator:
    """Stateful validator suitable for HOP6 wiring.

    Holds an optional telemetry bus — the same contract used by
    ``MessageDiversityValidator`` and ``PersonaPlannerValidator`` — so
    violations can be recorded without the caller having to plumb the
    bus through every call site.

    Typical wiring:

        validator = ArchetypeMessageLengthValidator(telemetry_bus=bus)
        result = validator.validate(message_text, archetype="EXECUTIVE")
        if not result.is_valid:
            # HOP6 returns message to HOP5 with the regeneration hint
            ...

    The class is intentionally thin — it delegates to ``validate_length``
    and emits one telemetry event per violation. Adding more rules to
    this validator is out of scope; new rules land in sibling validators.
    """

    def __init__(self, telemetry_bus: Optional[object] = None) -> None:
        """Construct validator with optional telemetry bus.

        Args:
            telemetry_bus: Any object implementing
                ``record(event_name: str, payload: dict) -> None``.
                When None, telemetry emits are skipped silently.
        """
        self._telemetry_bus = telemetry_bus

    def validate(
        self,
        text: str,
        archetype: str,
    ) -> LengthValidationResult:
        """Validate ``text`` against the archetype's length cap.

        Emits a ``message_length_cap_violation`` telemetry event on the
        bus when ``is_valid=False``.
        """
        result = validate_length(text, archetype)
        if not result.is_valid and self._telemetry_bus is not None:
            try:
                self._telemetry_bus.record(
                    "message_length_cap_violation",
                    {
                        "archetype": result.archetype,
                        "length": result.message_length,
                        "cap": result.cap,
                        "excess": result.excess,
                    },
                )
            except (AttributeError, TypeError, RuntimeError, ValueError, OSError):  # guardian: allow-log-and-swallow -- telemetry must never break validation
                pass
        return result


__all__ = [
    "ARCHETYPE_LENGTH_CAPS",
    "DEFAULT_LENGTH_CAP",
    "ArchetypeMessageLengthValidator",
    "LengthValidationResult",
    "cap_for",
    "validate_length",
]
