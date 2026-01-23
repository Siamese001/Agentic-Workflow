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
    use_interactions_api: bool = True,
) -> str:
    """Run a Gemini generate_content call and return the response text.

    Args:
        model: Gemini model name
        prompt: Input prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        timeout_s: Request timeout in seconds
        use_interactions_api: Force use of new v1beta Interactions API
    """

    # Try new v1beta Interactions API first
    if use_interactions_api:
        try:
            from google import genai

            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "GOOGLE_API_KEY or GEMINI_API_KEY must be set for Google provider"
                )

            client = genai.Client(api_key=api_key)

            # Prepare input for interactions.create
            input_messages = [{"role": "user", "content": prompt}]

            # Execute the interaction
            response = client.interactions.create(
                model=model,
                input=input_messages,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )

            # Extract content from response
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    return candidate.content.parts[0].text if candidate.content.parts else ""

            return ""

        except ImportError:
            # Fallback to legacy SDK if new SDK not installed
            pass
        except Exception as e:
            # Log error and fallback to legacy
            import logging

            logging.warning(f"Google GenAI v1beta API failed, falling back to legacy: {e}")

    # Legacy SDK implementation
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
