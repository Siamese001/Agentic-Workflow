"""PromptEnvelope posture validator (C0 J5 runtime enforcement).

Makes the C0 J5 invariant — "PromptEnvelope must bind citation_mode and
tool_use posture before L2 dispatch" — machine-enforceable at runtime.

Reads posture fields from the envelope's ``metadata`` dict (keys
``citation_mode`` and ``tool_use``). Rejects envelopes with missing or
invalid posture. Does not mutate the envelope.

Allowed values:
  citation_mode : {"native", "manual"}
  tool_use      : {"open", "closed"}

Architecture reference:
  - C0 J5 invariant in C0_Governance_Safety_Enforcement.md
  - PromptEnvelope contract: agentic_core/knowledge/retrieval/prompt_envelope.py
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any


def _load_prompt_envelope_cls() -> Any:
    """Runtime-load PromptEnvelope to avoid an L2 -> L_PG static import."""
    module = importlib.import_module("agentic_core.knowledge.retrieval")
    return module.PromptEnvelope


CITATION_MODE_NATIVE = "native"
CITATION_MODE_MANUAL = "manual"
_VALID_CITATION_MODES = frozenset({CITATION_MODE_NATIVE, CITATION_MODE_MANUAL})

TOOL_USE_OPEN = "open"
TOOL_USE_CLOSED = "closed"
_VALID_TOOL_USE = frozenset({TOOL_USE_OPEN, TOOL_USE_CLOSED})

_POSTURE_KEY_CITATION_MODE = "citation_mode"
_POSTURE_KEY_TOOL_USE = "tool_use"


class PromptEnvelopePostureError(ValueError):
    """Raised when a PromptEnvelope fails posture validation.

    Subclass of ``ValueError`` so callers using ``except ValueError`` still
    catch it, but the specific type lets gates discriminate posture failures
    from other value errors.
    """


@dataclass(frozen=True)
class PostureValidationResult:
    """Outcome of posture validation.

    Attributes
    ----------
    is_valid : bool
        True when both posture fields are present and in the allowed set.
    citation_mode : str | None
        Extracted citation_mode value, or None when missing.
    tool_use : str | None
        Extracted tool_use value, or None when missing.
    violations : tuple[str, ...]
        Human-readable reasons for invalidity (empty when is_valid).
    """

    is_valid: bool
    citation_mode: str | None
    tool_use: str | None
    violations: tuple[str, ...]


def _extract_metadata(envelope: Any) -> dict[str, Any]:
    """Return the metadata dict of the envelope, or raise if wrong type."""
    prompt_envelope_cls = _load_prompt_envelope_cls()
    if not isinstance(envelope, prompt_envelope_cls):
        raise PromptEnvelopePostureError(f"expected PromptEnvelope, got {type(envelope).__name__}")
    metadata = envelope.metadata
    if not isinstance(metadata, dict):
        raise PromptEnvelopePostureError(f"envelope.metadata must be a dict, got {type(metadata).__name__}")
    return metadata


def validate_prompt_envelope_posture(envelope: Any) -> PostureValidationResult:
    """Validate posture fields on a PromptEnvelope without raising on invalidity.

    Raises ``PromptEnvelopePostureError`` only for structural errors (wrong
    type or non-dict metadata). Soft field-level problems are surfaced via
    ``PostureValidationResult.violations``.

    Parameters
    ----------
    envelope : PromptEnvelope
        Envelope to inspect.

    Returns
    -------
    PostureValidationResult
        Validation outcome with extracted values and any violations.
    """
    metadata = _extract_metadata(envelope)

    citation_mode_raw = metadata.get(_POSTURE_KEY_CITATION_MODE)
    tool_use_raw = metadata.get(_POSTURE_KEY_TOOL_USE)

    violations: list[str] = []

    citation_mode: str | None
    if citation_mode_raw is None:
        violations.append(
            f"missing metadata.{_POSTURE_KEY_CITATION_MODE} (expected one of {sorted(_VALID_CITATION_MODES)})"
        )
        citation_mode = None
    elif not isinstance(citation_mode_raw, str):
        violations.append(
            f"metadata.{_POSTURE_KEY_CITATION_MODE} must be str, got {type(citation_mode_raw).__name__}"
        )
        citation_mode = None
    elif citation_mode_raw not in _VALID_CITATION_MODES:
        violations.append(
            f"metadata.{_POSTURE_KEY_CITATION_MODE}={citation_mode_raw!r} "
            f"not in {sorted(_VALID_CITATION_MODES)}"
        )
        citation_mode = citation_mode_raw
    else:
        citation_mode = citation_mode_raw

    tool_use: str | None
    if tool_use_raw is None:
        violations.append(
            f"missing metadata.{_POSTURE_KEY_TOOL_USE} (expected one of {sorted(_VALID_TOOL_USE)})"
        )
        tool_use = None
    elif not isinstance(tool_use_raw, str):
        violations.append(f"metadata.{_POSTURE_KEY_TOOL_USE} must be str, got {type(tool_use_raw).__name__}")
        tool_use = None
    elif tool_use_raw not in _VALID_TOOL_USE:
        violations.append(
            f"metadata.{_POSTURE_KEY_TOOL_USE}={tool_use_raw!r} not in {sorted(_VALID_TOOL_USE)}"
        )
        tool_use = tool_use_raw
    else:
        tool_use = tool_use_raw

    return PostureValidationResult(
        is_valid=not violations,
        citation_mode=citation_mode,
        tool_use=tool_use,
        violations=tuple(violations),
    )


def assert_prompt_envelope_posture(envelope: Any) -> PostureValidationResult:
    """Validate posture fields and raise on invalidity.

    Parameters
    ----------
    envelope : PromptEnvelope
        Envelope to inspect.

    Returns
    -------
    PostureValidationResult
        Validation outcome (always ``is_valid=True`` when returned).

    Raises
    ------
    PromptEnvelopePostureError
        When the envelope has wrong type, non-dict metadata, or any
        posture-field violation.
    """
    result = validate_prompt_envelope_posture(envelope)
    if not result.is_valid:
        joined = "; ".join(result.violations)
        raise PromptEnvelopePostureError(f"PromptEnvelope posture invalid: {joined}")
    return result


__all__ = [
    "CITATION_MODE_MANUAL",
    "CITATION_MODE_NATIVE",
    "PostureValidationResult",
    "PromptEnvelopePostureError",
    "TOOL_USE_CLOSED",
    "TOOL_USE_OPEN",
    "assert_prompt_envelope_posture",
    "validate_prompt_envelope_posture",
]
