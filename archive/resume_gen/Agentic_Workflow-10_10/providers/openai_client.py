"""OpenAI client adapter for v10_10.

This module is the ONLY place where the OpenAI SDK is imported.
It exposes a narrow run_llm interface used by runtime_utils.
"""

from __future__ import annotations

import os
from typing import Any


def run_llm_openai(
    model: str,
    prompt: str,
    *,
    temperature: float,
    max_tokens: int,
    timeout_s: int,
) -> str:
    """Run an OpenAI chat completion and return the response text.

    This helper performs no routing or caching; it is a thin wrapper
    around the OpenAI SDK. Errors are allowed to propagate and will be
    wrapped by the caller (runtime_utils.invoke_model).
    """

    try:
        import openai  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError("openai package not installed") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be set for OpenAI provider")

    client = openai.OpenAI(api_key=api_key)

    resp: Any = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout_s,
    )
    return str(resp.choices[0].message.content or "")



