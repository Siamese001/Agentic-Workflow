# FILE: 10_10/runtime_utils.py
"""
Unified Runtime Utilities (v10_10) — INFRASTRUCTURE LAYER
=========================================================

This is the v10_10 refactor of the v10_9 runtime_utils module. :contentReference[oaicite:1]{index=1}

It removes:
    • v10_9 telemetry buffer (_TELEMETRY_EVENTS)
    • CostTracker / Optimization helpers
    • Retrieval / Ranking / RAGUtils meta-layer helpers

Those concerns have been moved into:
    • observability.py          — spans, events, exceptions logging
    • retrieval.py              — deterministic post-processing of raw hits
    • ranking.py                — deterministic ranking of Evidence

This module now provides ONLY:

    1. Exception hierarchy for runtime surfaces
    2. SandboxConfig + get_sandbox()
    3. PredictiveCacheManager (optional predictive/semantic cache)
    4. invoke_model() unified LLM gateway (OpenAI + Anthropic)

Design constraints:
    • No planning (L1).
    • No tool logic besides LLM call wrappers (L2).
    • No DAG/orchestration (L3).
    • No state mutation (L4).
    • No safety/policy decisions (L5).
    • No meta-learning or telemetry aggregation.
"""

from __future__ import annotations

import os
import json
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from observability import record_event, record_exception


# ============================================================================
# 1. EXCEPTIONS (RUNTIME SURFACES)
# ============================================================================


class ValidationError(Exception):
    """Malformed state, plan, or configuration (runtime-level)."""


class ToolExecutionError(Exception):
    """Execution error during tool / sandboxed operation."""


class ModelClientError(Exception):
    """Low-level model provider call failure (OpenAI/Anthropic error)."""


class SafetyException(Exception):
    """Safety contract violation (L5 error surface)."""


class WorkflowTimeoutError(Exception):
    """Async workflow exceeded its time budget."""


class LLMInvocationError(RuntimeError):
    """Raised when an LLM invocation fails."""


# ============================================================================
# 2. SANDBOX CONFIGURATION
# ============================================================================

@dataclass
class SandboxConfig:
    """
    Logical sandbox configuration for tool/LLM invocations.

    Actual isolation is provided by the surrounding environment (e.g.,
    Windsurf container). This object provides *logical* constraints:

        • allow_network: whether network calls are permitted.
        • request_timeout_s: per-call timeout.
        • max_tokens_per_call: cap on LLM token generation.
    """

    name: str = "default"
    allow_network: bool = True
    request_timeout_s: int = 60
    max_tokens_per_call: int = 2048


def get_sandbox(config: Optional[SandboxConfig]) -> SandboxConfig:
    """
    Normalize a possibly-None sandbox config.
    """
    return config or SandboxConfig()


# ============================================================================
# 3. PREDICTIVE CACHE
# ============================================================================

@dataclass
class PredictiveCacheManager:
    """
    Lightweight in-memory predictive/semantic cache.

    Intended use:
        • Cache expensive L2 operations (RAG, cognitive agent calls).
        • Keyed by (domain, plan, context signature).

    Behavior:
        • In-memory only.
        • Evicts oldest entry when capacity exceeded.
    """

    max_entries: int = 1024
    _store: Dict[str, Tuple[float, Any]] = field(default_factory=dict)

    def make_key(self, domain: str, plan: Any, ctx: Any) -> str:
        """
        Build a stable cache key based on:
            - domain         (e.g., "rag", "strategy", "drafting")
            - plan.model_dump() or __dict__
            - job + config signature
        """
        try:
            plan_data = plan.model_dump()
        except Exception:
            plan_data = getattr(plan, "__dict__", str(plan))

        ctx_sig = {
            "job_title": getattr(getattr(ctx, "job", None), "title", ""),
            "role_type": getattr(getattr(ctx, "job", None), "role_type", ""),
            "seniority": getattr(getattr(ctx, "job", None), "seniority", ""),
            "config": getattr(getattr(ctx, "config", None), "model_dump", lambda: {})(),
        }

        raw = json.dumps(
            {"domain": domain, "plan": plan_data, "ctx": ctx_sig},
            sort_keys=True,
            default=str,
        )
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{domain}:{digest}"

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value or None if not present.
        """
        entry = self._store.get(key)
        if not entry:
            return None

        ts, value = entry
        record_event(
            "predictive_cache_hit",
            {"key": key, "age_s": time.time() - ts},
        )
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Insert or replace a cache entry, evicting oldest if full.
        """
        if len(self._store) >= self.max_entries:
            # Evict oldest
            oldest_key = min(self._store, key=lambda k: self._store[k][0])
            self._store.pop(oldest_key, None)
            record_event("predictive_cache_evict", {"evicted_key": oldest_key})

        self._store[key] = (time.time(), value)
        record_event("predictive_cache_set", {"key": key})


# ============================================================================
# 4. UNIFIED LLM GATEWAY
# ============================================================================

def _detect_provider(model: str) -> str:
    """
    Infer provider from model name string.

    Very simple heuristic:
        - "gpt-" or "o"  → OpenAI
        - "claude"       → Anthropic
        - default        → OpenAI
    """
    m = model.lower()
    if m.startswith("gpt") or m.startswith("o"):
        return "openai"
    if m.startswith("claude"):
        return "anthropic"
    return "openai"


def invoke_model(
    model: str,
    prompt: str,
    sandbox: SandboxConfig,
    *,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """
    Unified LLM invocation for v10_10.

    Parameters:
        model:       model ID selected by RoutingPolicy (e.g. "gpt-5.1-codex").
        prompt:      final rendered prompt text.
        sandbox:     SandboxConfig (request_timeout_s, max_tokens_per_call).
        temperature: sampling temperature.
        max_tokens:  max token count (capped by sandbox).

    Returns:
        Model's text response.

    Raises:
        LLMInvocationError on failure.
    """
    provider = _detect_provider(model)
    max_tokens = min(max_tokens, sandbox.max_tokens_per_call)

    record_event(
        "invoke_model_start",
        {
            "model": model,
            "provider": provider,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    )

    try:
        if provider == "openai":
            try:
                import openai  # type: ignore
            except ImportError as exc:  # pragma: no cover
                raise ModelClientError("openai package not installed") from exc

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=sandbox.request_timeout_s,
            )
            text = resp.choices[0].message.content or ""

        elif provider == "anthropic":
            try:
                import anthropic  # type: ignore
            except ImportError as exc:  # pragma: no cover
                raise ModelClientError("anthropic package not installed") from exc

            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            resp = client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=sandbox.request_timeout_s,
            )

            parts = []
            for block in resp.content:
                if getattr(block, "type", None) == "text":
                    parts.append(getattr(block, "text", ""))
            text = "\n".join(parts)

        else:
            raise LLMInvocationError(f"Unsupported provider inferred for model: {model}")

        record_event(
            "invoke_model_success",
            {"model": model, "provider": provider, "response_len": len(text)},
        )
        return text

    except Exception as exc:
        # Log and re-raise as LLMInvocationError to keep a clean surface.
        record_exception("invoke_model_failure", exc)
        raise LLMInvocationError(f"LLM invocation failed for model {model}: {exc}") from exc
