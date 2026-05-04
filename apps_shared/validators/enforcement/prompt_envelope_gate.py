"""Fail-closed L2 dispatch gate for PromptEnvelope posture.

Thin wrapper around
``agentic_core.L2_execution.prompt_envelope_validator.assert_prompt_envelope_posture``
that L2 dispatch callers invoke before handing an envelope to a provider.

Refuses envelopes that do not bind posture (C0 J5). On invalid envelope,
raises ``PromptEnvelopePostureError`` — callers MUST NOT catch broadly and
continue; this is a hard gate.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L2_execution.prompt_envelope_validator import (
    PostureValidationResult,
    PromptEnvelopePostureError,
    assert_prompt_envelope_posture,
)


def enforce_prompt_envelope_posture(envelope: Any) -> PostureValidationResult:
    """Raise ``PromptEnvelopePostureError`` unless the envelope binds posture.

    Parameters
    ----------
    envelope : PromptEnvelope
        Envelope about to be dispatched to a provider.

    Returns
    -------
    PostureValidationResult
        Always ``is_valid=True`` when returned.

    Raises
    ------
    PromptEnvelopePostureError
        When posture is missing, non-string, or outside the allowed set.
    """
    return assert_prompt_envelope_posture(envelope)


__all__ = [
    "PromptEnvelopePostureError",
    "enforce_prompt_envelope_posture",
]
