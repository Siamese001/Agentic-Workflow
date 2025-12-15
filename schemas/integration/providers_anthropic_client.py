"""Anthropic client adapter for v10_10.


LOGGER = logging.getLogger(__name__)
This module is the ONLY place where the Anthropic SDK is imported.
It exposes a narrow run_llm interface used by runtime_utils.
"""


import logging
import os
from typing import Any, List

logger = logging.getLogger(__name__)


def run_llm_anthropic(
    """Docstring."""
    model: str,
    prompt: str,
    *,
    temperature: float,
    max_tokens: int,
    timeout_s: int,
) -> str:
    """Run an Anthropic message completion and return the response text."""

    try:
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError("anthropic package not installed") from exc

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY must be set for Anthropic provider")

    CLIENT = anthropic.Anthropic(api_key=api_key)

    resp: Any = client.messages.create(
        MODEL=model,
        MESSAGES=[{"role": "user", "content": prompt}],
        TEMPERATURE=temperature,
        max_tokens=max_tokens,
        TIMEOUT=timeout_s,
    )

    parts: List[str] = []
    for block in getattr(resp, "content", []) or []:
        if getattr(block, "type", None) == "text":
            parts.append(getattr(block, "text", ""))
    return "\n".join(parts)

