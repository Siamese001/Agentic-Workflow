"""Developer-message vs system-message prompt envelope (ADR-043, W4/P4.3).

Implements the OpenAI / Anthropic best practice that the L1 thinking desk
separates:

- **system_message**    : L5 policy + hard constraints (stable, rarely changes)
- **developer_message** : M1 schemas + M2 safety envelope + M3 few-shot
                          exemplars (per-class, version-controlled)
- **user_message**      : I1 + I2 + I3 intent frame from the validated
                          request (per-request)

Reasoning models MUST NOT receive injected "think step by step" instructions.
:func:`build_envelope` enforces this at compile time: if ``is_reasoning_model``
is True and any of the three messages contains a forbidden scaffolding
phrase (case-insensitive), :class:`PromptEnvelopeViolation` is raised.

The envelope is frozen + serializable.  Consumers build it once per plan
and hand it unchanged to the model adapter; no further mutation allowed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Sequence


class PromptEnvelopeViolation(ValueError):
    """Raised when the envelope violates a structural or style invariant."""


# Forbidden scaffolding phrases for reasoning-class models (OpenAI guidance:
# reasoning models' chain-of-thought is internal; prepending "think step
# by step" degrades output).  Match is case-insensitive, word-boundary aware.
_REASONING_SCAFFOLD_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bthink\s+step[-\s]*by[-\s]*step\b", re.IGNORECASE),
    re.compile(r"\blet'?s\s+think\s+step[-\s]*by[-\s]*step\b", re.IGNORECASE),
    re.compile(r"\bthink\s+carefully\s+step[-\s]*by[-\s]*step\b", re.IGNORECASE),
    re.compile(r"\breason\s+step[-\s]*by[-\s]*step\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class PromptEnvelope:
    """A serializable, validated three-role prompt envelope.

    Fields:
        system_message:    L5 policy block; stable across requests of a class.
        developer_message: Schemas / safety / few-shot exemplars block;
            version-controlled per work-class.
        user_message:      Per-request user intent frame (I1+I2+I3).
        is_reasoning_model: Indicates the target model is a reasoning-class
            model (enforces scaffolding ban).
        metadata:          Opaque dict for caller bookkeeping; round-trips
            through :meth:`to_dict` unchanged.
    """

    system_message: str
    developer_message: str
    user_message: str
    is_reasoning_model: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_message": self.system_message,
            "developer_message": self.developer_message,
            "user_message": self.user_message,
            "is_reasoning_model": self.is_reasoning_model,
            "metadata": dict(self.metadata),
        }


def _policy_block_joiner(parts: Sequence[str]) -> str:
    """Join non-empty parts with a single blank line separator."""
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def build_envelope(
    *,
    l5_policy: str,
    schemas: str,
    safety_envelope: str,
    exemplars: str = "",
    user_intent: str,
    is_reasoning_model: bool = False,
    metadata: dict[str, Any] | None = None,
) -> PromptEnvelope:
    """Compose a :class:`PromptEnvelope` from its semantic parts.

    Layout rules (SSOT for L1 prompt envelope):
      - ``system_message``    = ``l5_policy``
      - ``developer_message`` = schemas + safety_envelope + exemplars, joined
                                by blank lines; empty parts skipped.
      - ``user_message``      = ``user_intent``

    Reasoning-model guard: if ``is_reasoning_model`` is True, none of the
    three messages may contain a forbidden scaffolding phrase.

    Args:
        l5_policy:        Hard policy text from the L5 plane.
        schemas:          M1 task schemas / output contracts block.
        safety_envelope:  M2 safety, compliance, escalation thresholds.
        exemplars:        M3 few-shot examples (may be empty for zero-shot).
        user_intent:      I1+I2+I3 intent frame.
        is_reasoning_model: Enforce scaffolding ban.  Default False.
        metadata:         Optional opaque caller metadata.

    Returns:
        Frozen :class:`PromptEnvelope`.

    Raises:
        PromptEnvelopeViolation: If any required field is empty, or if a
            scaffolding phrase leaks into a reasoning-model envelope.
    """
    for name, val in (
        ("l5_policy", l5_policy),
        ("schemas", schemas),
        ("safety_envelope", safety_envelope),
        ("user_intent", user_intent),
    ):
        if not isinstance(val, str) or not val.strip():
            raise PromptEnvelopeViolation(f"{name} must be a non-empty string.")

    developer_message = _policy_block_joiner([schemas, safety_envelope, exemplars])
    if not developer_message:
        raise PromptEnvelopeViolation(
            "developer_message must be non-empty after joining schemas + safety_envelope + exemplars."
        )

    envelope = PromptEnvelope(
        system_message=l5_policy.strip(),
        developer_message=developer_message,
        user_message=user_intent.strip(),
        is_reasoning_model=bool(is_reasoning_model),
        metadata=dict(metadata or {}),
    )

    if envelope.is_reasoning_model:
        _enforce_no_scaffolding(envelope)

    return envelope


def _enforce_no_scaffolding(env: PromptEnvelope) -> None:
    fields = (
        ("system_message", env.system_message),
        ("developer_message", env.developer_message),
        ("user_message", env.user_message),
    )
    for label, text in fields:
        for pat in _REASONING_SCAFFOLD_PATTERNS:
            if pat.search(text):
                raise PromptEnvelopeViolation(
                    f"Reasoning model envelope MUST NOT contain scaffolding; "
                    f"matched pattern {pat.pattern!r} in {label}."
                )


__all__ = [
    "PromptEnvelope",
    "PromptEnvelopeViolation",
    "build_envelope",
]
