"""Thin LLM client adapter for narrative-pipeline ensemble + judge.

Decision lock D6: Anthropic Sonnet generator + Anthropic Haiku judge —
single auth, solid diversity, cheaper than cross-provider. Falls back
to OpenAI / Gemini if Anthropic key is absent. Final fallback is the
deterministic stub generator already used by `_ensemble_runner`.

Public surface:
  - `make_generator(role)` -> Callable[[label, prompt], str]
  - `make_judge_score(prompt)` -> dict (or None if no provider available)

The adapter does NOT route through the heavy SovereignLLMGateway because
the narrative pipeline is end-user-facing, not runtime-governed. Direct
SDK calls match the apps_rg architecture's layer-gravity rule (see
`config/contracts/README.md`).

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md
(NEXT_STEP-1 — wire SovereignLLMGateway into ensemble + judge live).
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Callable, Dict, Optional

_log = logging.getLogger(__name__)

# Model IDs — sourced from agentic_core/L0_routing/config/model_registry.py
# but pinned locally to avoid an L0 cycle for a leaf adapter.
_DEFAULTS = {
    "anthropic_generator": "claude-sonnet-4-5-20250929",
    "anthropic_judge": "claude-haiku-4-5-20251001",
    "openai_generator": "gpt-4o-2024-08-06",
    "openai_judge": "gpt-4o-mini-2024-07-18",
    "gemini_generator": "gemini-2.5-pro",
    "gemini_judge": "gemini-2.5-flash",
}


# ----------------------------------------------------------------- generator


def make_generator(
    role: str = "narrative",
    *,
    timeout_s: float = 60.0,
    temperature: float = 0.75,
    max_tokens: int = 600,
) -> Optional[Callable[..., str]]:
    """Return a generator callable, or None if no provider is wired.

    Wave 5 P5.1 (plan apps-eval-qwen32b-rollout-b7c4d9): tries local
    Qwen-32B vLLM first when the server is healthy. Falls through to
    Anthropic → OpenAI → Gemini → None on any preflight failure or SDK
    absence. Same cascade pattern Wave 2/3/4 established for judges
    and synthesizers — the local path is effectively free per call,
    cloud APIs are the regulated-egress fallback.

    The returned callable accepts an optional ``temperature`` keyword:
        gen(label, prompt) -> uses default temperature
        gen(label, prompt, temperature=0.95) -> overrides per-call

    This per-call override lets the ensemble runner sweep a temperature
    ladder across the 3 candidates without instantiating 3 generators.
    """
    qwen_gen = _make_qwen_generator(
        timeout_s=timeout_s, temperature=temperature, max_tokens=max_tokens
    )
    if qwen_gen is not None:
        return qwen_gen
    if os.getenv("ANTHROPIC_API_KEY"):
        return _make_anthropic_generator(timeout_s=timeout_s, temperature=temperature, max_tokens=max_tokens)
    if os.getenv("OPENAI_API_KEY"):
        return _make_openai_generator(timeout_s=timeout_s, temperature=temperature, max_tokens=max_tokens)
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return _make_gemini_generator(timeout_s=timeout_s, temperature=temperature, max_tokens=max_tokens)
    _log.info("[narrative_llm] No LLM provider available (Qwen unhealthy + no cloud key) — using stub")
    return None


def _make_qwen_generator(*, timeout_s: float, temperature: float, max_tokens: int):
    """Return a Qwen-local generator callable, or None when unavailable.

    Wave 5 P5.1. Preflight via :func:`is_qwen_available`; lazy-import
    the OpenAI SDK and the model registry. Returns ``None`` on any
    guard failure so :func:`make_generator` falls through to the
    cloud generators. The closure captures a single ``openai.OpenAI``
    client (not async — the ensemble runner is sync); reuses the
    connection pool across the 3+ candidate sweep.
    """
    try:
        from agentic_core.L2_execution.healers.vllm_health_probe import (  # noqa: PLC0415
            is_qwen_available,
        )
    except ImportError:
        return None

    # Optional blocking wait for vLLM to become ready (cold-start scenarios)
    wait_sec = float(os.getenv("VLLM_WAIT_FOR_READY", "0"))  # noqa: PLW1508
    if wait_sec > 0 and not is_qwen_available():
        _log.info("[narrative_llm] vLLM not ready, waiting up to %.0fs...", wait_sec)
        deadline = time.time() + wait_sec
        while time.time() < deadline:
            if is_qwen_available():
                _log.info("[narrative_llm] vLLM became ready after %.1fs", wait_sec - (deadline - time.time()))
                break
            time.sleep(2.0)

    if not is_qwen_available():
        _log.info("[narrative_llm] qwen preflight failed; cascading to cloud")
        return None

    try:
        import openai  # type: ignore  # noqa: PLC0415
    except ImportError:
        return None

    try:
        from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
            QWEN_LOCAL_MODEL_ID,
            VLLM_BASE_URL,
        )
    except ImportError:
        return None

    try:
        client = openai.OpenAI(
            base_url=VLLM_BASE_URL,
            api_key="not-needed",  # vLLM ignores auth in local mode
            timeout=timeout_s,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- OpenAI client init heterogeneous (ssl, network, env); fail-soft cascades to cloud generators
        _log.info("[narrative_llm] qwen client init failed: %s", exc)
        return None
    default_temp = temperature

    def _gen(label: str, prompt: str, *, temperature: float | None = None) -> str:
        temp = float(temperature) if temperature is not None else default_temp
        try:
            resp = client.chat.completions.create(
                model=QWEN_LOCAL_MODEL_ID,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior recruiter rewriting executive resume "
                            "narrative. Return ONLY the rewritten text — no "
                            "explanations, no preamble."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temp,
                max_tokens=max_tokens,
            )
            text = (resp.choices[0].message.content or "") if resp.choices else ""
            _emit_narrative_generator_marker(
                accepted=bool(text.strip()),
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="none" if text.strip() else "empty_response",
            )
            return text.strip()
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI-SDK-over-vLLM raises heterogeneous; per-call fail-soft preserves ensemble (matches sibling cloud generators)
            _log.warning("[narrative_llm] qwen %s failed: %s", label, exc)
            _emit_narrative_generator_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="gateway_exception",
            )
            return ""

    _gen.__name__ = "qwen_local"  # type: ignore[attr-defined]
    return _gen


def _emit_narrative_generator_marker(
    *,
    accepted: bool,
    model_used: str,
    fallback_reason: str,
) -> None:
    """Best-effort ``JUDGE_DECISION`` marker for generator availability.

    Used loosely as a generation-availability signal so the W1
    judge-calibration harness can report Qwen-uptime + fallback-rate
    for the apps_rg generator surface alongside its judge surfaces.
    Never raises.
    """
    try:
        from tools.capture.append_marker import append_marker  # noqa: PLC0415
    except ImportError:
        return
    payload = (
        "JUDGE_DECISION: type=judge_decision, "
        "app_name=apps_rg.narrative_generator, "
        "rubric_id=rg_narrative_generator_v1, "
        "rubric_hash=inline, "
        f"accepted={accepted}, "
        "composite=0.0, "
        f"model_used={model_used}, "
        f"fallback_reason={fallback_reason}, "
        "first_failed_gate=none, "
        "latency_ms=0.0"
    )
    try:
        append_marker(payload, session_hint="apps_rg.narrative_generator")
    except (OSError, PermissionError):
        pass


def _make_anthropic_generator(*, timeout_s: float, temperature: float, max_tokens: int):
    try:
        import anthropic  # type: ignore
    except ImportError:
        _log.info("[narrative_llm] anthropic SDK not installed")
        return None

    api_key = os.environ["ANTHROPIC_API_KEY"]
    model = os.getenv("ANTHROPIC_NARRATIVE_GENERATOR_MODEL", _DEFAULTS["anthropic_generator"])
    client = anthropic.Anthropic(api_key=api_key, timeout=timeout_s)
    default_temp = temperature

    def _gen(label: str, prompt: str, *, temperature: float | None = None) -> str:
        temp = float(temperature) if temperature is not None else default_temp
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temp,
                system=(
                    "You are a senior recruiter rewriting executive resume narrative. "
                    "Return ONLY the rewritten text — no explanations, no preamble."
                ),
                messages=[{"role": "user", "content": prompt}],
            )
            text = ""
            for block in getattr(resp, "content", []) or []:
                t = getattr(block, "text", None)
                if t:
                    text += t
            return text.strip()
        except Exception as exc:  # guardian: allow-broad-exception -- Anthropic SDK raises heterogeneous (APIError/RateLimit/Timeout); per-call fail-soft preserves ensemble
            _log.warning("[narrative_llm] anthropic %s failed: %s", label, exc)
            return ""

    _gen.__name__ = "anthropic_sonnet"  # type: ignore[attr-defined]
    return _gen


def _make_openai_generator(*, timeout_s: float, temperature: float, max_tokens: int):
    try:
        import openai  # type: ignore
    except ImportError:
        _log.info("[narrative_llm] openai SDK not installed")
        return None

    api_key = os.environ["OPENAI_API_KEY"]
    model = os.getenv("OPENAI_NARRATIVE_GENERATOR_MODEL", _DEFAULTS["openai_generator"])
    client = openai.OpenAI(api_key=api_key, timeout=timeout_s)
    default_temp = temperature

    def _gen(label: str, prompt: str, *, temperature: float | None = None) -> str:
        temp = float(temperature) if temperature is not None else default_temp
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior recruiter rewriting executive resume narrative. Return ONLY the rewritten text.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temp,
                max_tokens=max_tokens,
            )
            return (resp.choices[0].message.content or "").strip() if resp.choices else ""
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI SDK raises heterogeneous; per-call fail-soft preserves ensemble
            _log.warning("[narrative_llm] openai %s failed: %s", label, exc)
            return ""

    _gen.__name__ = "openai_gpt4o"  # type: ignore[attr-defined]
    return _gen


def _make_gemini_generator(*, timeout_s: float, temperature: float, max_tokens: int):
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError:
        _log.info("[narrative_llm] google-generativeai SDK not installed")
        return None

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    model_id = os.getenv("GEMINI_NARRATIVE_GENERATOR_MODEL", _DEFAULTS["gemini_generator"])
    model = genai.GenerativeModel(model_id)
    default_temp = temperature

    def _gen(label: str, prompt: str, *, temperature: float | None = None) -> str:
        temp = float(temperature) if temperature is not None else default_temp
        try:
            resp = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temp,
                    "max_output_tokens": max_tokens,
                },
                request_options={"timeout": timeout_s},
            )
            return (getattr(resp, "text", "") or "").strip()
        except Exception as exc:  # guardian: allow-broad-exception -- Gemini SDK raises heterogeneous; per-call fail-soft preserves ensemble
            _log.warning("[narrative_llm] gemini %s failed: %s", label, exc)
            return ""

    _gen.__name__ = "gemini_pro"  # type: ignore[attr-defined]
    return _gen


# --------------------------------------------------------------------- judge


def call_judge(prompt: str, *, timeout_s: float = 30.0, max_tokens: int = 256) -> Optional[Dict[str, float]]:
    """Call the judge model and parse JSON soft-scores.

    Decision lock D6: prefer Anthropic Haiku for the judge slot.
    Returns dict with `tone_executive_register` and `naturalness` keys, or
    None on any failure (caller falls back to heuristics).
    """
    text = _judge_raw(prompt, timeout_s=timeout_s, max_tokens=max_tokens)
    if not text:
        return None
    try:
        first = text.find("{")
        last = text.rfind("}")
        if first < 0 or last <= first:
            return None
        data = json.loads(text[first : last + 1])
        return {
            "tone_executive_register": float(data.get("tone_executive_register", 0.0)),
            "naturalness": float(data.get("naturalness", 0.0)),
        }
    except (ValueError, TypeError) as exc:
        _log.info("[narrative_llm] judge JSON parse failed: %s", exc)
        return None


def _judge_raw(prompt: str, *, timeout_s: float, max_tokens: int) -> str:
    if os.getenv("ANTHROPIC_API_KEY"):
        return _judge_anthropic(prompt, timeout_s=timeout_s, max_tokens=max_tokens)
    if os.getenv("OPENAI_API_KEY"):
        return _judge_openai(prompt, timeout_s=timeout_s, max_tokens=max_tokens)
    return ""


def _judge_anthropic(prompt: str, *, timeout_s: float, max_tokens: int) -> str:
    try:
        import anthropic  # type: ignore
    except ImportError:
        return ""
    model = os.getenv("ANTHROPIC_NARRATIVE_JUDGE_MODEL", _DEFAULTS["anthropic_judge"])
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=timeout_s)
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.0,
            system="You are a senior recruiter scoring resume narrative. Respond ONLY with valid JSON.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = ""
        for block in getattr(resp, "content", []) or []:
            t = getattr(block, "text", None)
            if t:
                text += t
        return text
    except Exception as exc:  # guardian: allow-broad-exception -- Anthropic SDK raises heterogeneous; judge fail-soft drops to heuristics
        _log.warning("[narrative_llm] anthropic judge failed: %s", exc)
        return ""


def _judge_openai(prompt: str, *, timeout_s: float, max_tokens: int) -> str:
    try:
        import openai  # type: ignore
    except ImportError:
        return ""
    model = os.getenv("OPENAI_NARRATIVE_JUDGE_MODEL", _DEFAULTS["openai_judge"])
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=timeout_s)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior recruiter scoring resume narrative. Respond ONLY with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return (resp.choices[0].message.content or "") if resp.choices else ""
    except Exception as exc:  # guardian: allow-broad-exception -- OpenAI SDK raises heterogeneous; judge fail-soft drops to heuristics
        _log.warning("[narrative_llm] openai judge failed: %s", exc)
        return ""


__all__ = ["call_judge", "make_generator"]
