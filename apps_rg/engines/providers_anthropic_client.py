"""Anthropic client adapter for v10_10.

This module is the ONLY place where the Anthropic SDK is imported.
It exposes a narrow run_llm interface used by runtime_utils.
"""

from __future__ import annotations

import os
from typing import Any


def run_llm_anthropic(
    model: str,
    prompt: str,
    *,
    temperature: float,
    max_tokens: int,
    timeout_s: int,
) -> str:
    """Run an Anthropic message completion and return the response text."""

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError("anthropic package not installed") from exc

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY must be set for Anthropic provider")

    client = anthropic.Anthropic(api_key=api_key)

    resp: Any = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout_s,
    )

    parts: list[str] = []
    for block in getattr(resp, "content", []) or []:
        if getattr(block, "type", None) == "text":
            parts.append(getattr(block, "text", ""))
    return "\n".join(parts)
