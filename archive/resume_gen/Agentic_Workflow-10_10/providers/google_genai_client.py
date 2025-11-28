"""Google Generative AI (Gemini) client adapter for v10_10.

This module is the ONLY place where google.generativeai is imported.
It exposes a narrow run_llm interface used by runtime_utils.
"""

from __future__ import annotations

import os
from typing import Any


def run_llm_google(
    model: str,
    prompt: str,
    *,
    temperature: float,
    max_tokens: int,
    timeout_s: int,
) -> str:
    """Run a Gemini generate_content call and return the response text."""

    try:
        import google.generativeai as genai  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError("google-generativeai package not installed") from exc

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY must be set for Google provider")

    genai.configure(api_key=api_key)
    model_client = genai.GenerativeModel(model)

    # The SDK does not expose timeout/max_tokens identically to OpenAI/Anthropic;
    # those are left to higher-level routing and not enforced here.
    resp: Any = model_client.generate_content(prompt)
    return str(getattr(resp, "text", "") or "")



