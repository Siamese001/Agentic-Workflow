"""Google Generative AI (Gemini) client adapter for v10_10.

This module is the ONLY place where google.generativeai is imported.
It exposes a narrow run_llm interface used by runtime_utils.
"""

from __future__ import annotations

import os
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "providers_google_genai_client_util", "p0_governance")
_emit_reads_policy_state("p0", "providers_google_genai_client_util", "policy_binding")
_emit_snapshots_state("p0", "providers_google_genai_client_util", "state_snapshot")
emit_replay_key("p0", "providers_google_genai_client_util")
emit_determinism_digest("p0", "providers_google_genai_client_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
    _emit_records_execution_trace(
        str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "run_llm_google"
    )
    if use_interactions_api:
        try:
            from google import genai

            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY must be set for Google provider")
            client = genai.Client(api_key=api_key)
            input_messages = [{"role": "user", "content": prompt}]
            response = client.interactions.create(
                model=model,
                input=input_messages,
                config={"temperature": temperature, "max_output_tokens": max_tokens},
            )
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    return candidate.content.parts[0].text if candidate.content.parts else ""
            return ""
        except ImportError:
            pass
        # guardian: allow-silent-swallow
        except Exception as e:
            import logging

            logging.warning(f"Google GenAI v1beta API failed, falling back to legacy: {e}")
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise ImportError("google-generativeai package not installed") from exc
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY must be set for Google provider")
    genai.configure(api_key=api_key)
    model_client = genai.GenerativeModel(model)
    resp: Any = model_client.generate_content(prompt)
    return str(getattr(resp, "text", "") or "")
