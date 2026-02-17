"""Heal LLM call seam types for heal policy integrations.

Pure type definitions only (stdlib-only, no environment access or SDK imports).
Phase 7 Wave 7.1.
Phase 3: Added canonical seam enforcement via capability token.
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass
from typing import Any, Callable

# Capability token: only standard_heal may set this to True
_HEAL_SEAM_CAPABILITY: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "_HEAL_SEAM_CAPABILITY", default=False
)


class HealSeamBypassError(Exception):
    """Raised when LLM escalation is attempted outside canonical seam."""

    pass


def set_heal_seam_capability(enabled: bool) -> contextvars.Token[bool]:
    """Set the heal seam capability token. Only callable from standard_heal."""
    return _HEAL_SEAM_CAPABILITY.set(enabled)


def reset_heal_seam_capability(token: contextvars.Token[bool]) -> None:
    """Reset the heal seam capability token."""
    _HEAL_SEAM_CAPABILITY.reset(token)


def assert_heal_seam_capability() -> None:
    """Assert that the heal seam capability is enabled.

    Raises:
        HealSeamBypassError: If called outside the canonical standard_heal seam.
    """
    if not _HEAL_SEAM_CAPABILITY.get():
        raise HealSeamBypassError(
            "LLM escalation attempted outside canonical seam (standard_heal). "
            "Direct calls to DEFAULT_HEAL_LLM_CALLER are forbidden."
        )


@dataclass(frozen=True)
class HealLlmRequest:
    """Typed request payload for heal LLM calls.

    Attributes:
        prompt: The prompt text to send to the LLM.
        model_id: Optional model identifier; None means use the default model.
        metadata: Arbitrary metadata for observability/instrumentation.
    """

    prompt: str
    model_id: str | None
    metadata: dict[str, Any]


HealLlmCaller = Callable[[HealLlmRequest], str]


def guarded_heal_llm_call(request: HealLlmRequest) -> str | None:
    """Guarded LLM call that enforces canonical seam access.

    Returns:
        LLM response string, or None if no caller is configured.

    Raises:
        HealSeamBypassError: If called outside standard_heal context.
    """
    assert_heal_seam_capability()

    if DEFAULT_HEAL_LLM_CALLER is None:
        return None

    return DEFAULT_HEAL_LLM_CALLER(request)


# Default LLM caller seam for heal flows (not wired by default).
DEFAULT_HEAL_LLM_CALLER: HealLlmCaller | None = None


@dataclass(frozen=True)
class PolicyDecisionRecord:
    """Deterministic policy decision record (no timestamps/UUIDs).

    Emitted per heal run for observability.
    """

    confidence: float
    enable_llm: bool
    complexity: int
    prior_failures: int
    proceed: bool
    tier: str | None
    threshold_used: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "confidence": self.confidence,
            "enable_llm": self.enable_llm,
            "complexity": self.complexity,
            "prior_failures": self.prior_failures,
            "proceed": self.proceed,
            "tier": self.tier,
            "threshold_used": self.threshold_used,
            "rationale": self.rationale,
        }

    def input_hash(self) -> str:
        """Compute deterministic hash of inputs for stable filenames."""
        import hashlib

        input_str = f"{self.confidence}:{self.enable_llm}:{self.complexity}:{self.prior_failures}"
        return hashlib.sha256(input_str.encode()).hexdigest()[:16]
