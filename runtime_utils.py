# FILE: 10_10/runtime_utils.py
"""
Unified Runtime Utilities (v10_10) — INFRASTRUCTURE LAYER
=========================================================

This module is the v10_10 runtime utility layer.

Responsibilities:
    1. Exception hierarchy for runtime surfaces.
    2. SandboxConfig + get_sandbox() for logical isolation.
    3. PredictiveCacheManager for in-memory predictive/semantic caching.
    4. invoke_model() unified LLM gateway (OpenAI + Anthropic).

Design constraints:
    • No planning (L1).
    • No tool logic besides LLM call wrappers (L2).
    • No DAG/orchestration (L3).
    • No state mutation of WorkflowState (L4).
    • No safety/policy decisions (L5).
    • No meta-learning or telemetry aggregation (telemetry is delegated
      to observability.py via record_event / record_exception).
"""

from __future__ import annotations

import hashlib
import json
import os
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
    """Safety-related error at runtime (e.g., policy violations)."""


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
    container). This object provides *logical* constraints:

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
    Return a non-None SandboxConfig, falling back to defaults.
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
            - plan           (serialized in a stable way)
            - selected ctx fields (e.g., job id, resume id)
        """
        payload = {
            "domain": domain,
            "plan": self._safe_serialize(plan),
            "ctx": self._safe_serialize(ctx),
        }
        raw = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{domain}:{digest}"

    @staticmethod
    def _safe_serialize(obj: Any) -> Any:
        """
        Convert objects into a JSON-serializable structure where possible.
        """
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, dict):
            return {str(k): PredictiveCacheManager._safe_serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [PredictiveCacheManager._safe_serialize(v) for v in obj]
        # Fallback to string representation
        return str(obj)

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
# 4. LLM INVOCATION
# ============================================================================


def _infer_provider(model: str) -> str:
    """
    Infer provider from model string.

    Heuristics (deterministic):

        • If "claude" in model → "anthropic"
        • Else → "openai"
    """
    m = (model or "").lower()
    if "claude" in m:
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
        max_tokens:  requested max tokens (will be clamped to sandbox).
    """
    if not sandbox.allow_network:
        raise ToolExecutionError("Network access disabled by SandboxConfig")

    # Clamp max_tokens to sandbox policy.
    if max_tokens > sandbox.max_tokens_per_call:
        max_tokens = sandbox.max_tokens_per_call

    provider = _infer_provider(model)

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
