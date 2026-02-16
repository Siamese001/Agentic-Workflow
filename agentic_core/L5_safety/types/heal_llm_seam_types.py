"""Heal LLM call seam types for heal policy integrations.

Pure type definitions only (stdlib-only, no environment access or SDK imports).
Phase 7 Wave 7.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


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


# Default LLM caller seam for heal flows (not wired by default).
DEFAULT_HEAL_LLM_CALLER: HealLlmCaller | None = None
