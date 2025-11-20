# FILE: 10_10/runtime_utils.py
"""
Runtime Utilities for v10_10
============================

This module provides the infrastructure utilities required by the L2 cognitive
agents and the rest of the workflow:

    • invoke_model()          — unified LLM invocation wrapper
    • PredictiveCacheManager  — semantic/predictive cache
    • SandboxConfig           — execution sandbox abstraction
    • get_sandbox()           — normalized sandbox allocator

Design Goals:
    • Zero business logic.
    • Zero coupling to L1–L5 semantics.
    • All external calls routed through invoke_model().
    • DI-friendly: no global registries, no global state.
    • Observability integrated into every invocation.
"""

from __future__ import annotations

import os
import json
import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional, Any, Dict, Tuple

from observability import record_event, record_exception


# ==============================================================================
# Optional Provider SDKs
# ==============================================================================

try:  # pragma: no cover
    import openai
except ImportError:  # pragma: no cover
    openai = None

try:  # pragma: no cover
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None


# ==============================================================================
# Sandbox
# ==============================================================================

@dataclass
class SandboxConfig:
    """
    Sandbox descriptor for runtime execution.

    NOTE:
        Windsurf provides the actual isolation. This structure just
        enforces logical constraints for policy, token limits, and timeouts.
    """

    name: str = "default"
    allow_network: bool = True
    request_timeout_s: int = 60
    max_tokens_per_call: int = 2048


def get_sandbox(config: Optional[SandboxConfig]) -> SandboxConfig:
    """
    Normalize sandbox configuration (never return None).
    """
    return config if config is not None else SandboxConfig()


# ==============================================================================
# Predictive Cache Manager
# ==============================================================================

@dataclass
class PredictiveCacheManager:
    """
    Simple in-memory cache for deterministic speed-ups and cost savings.

    Keys are derived from domain ("rag", "drafting", etc.), plan, and context.

    You may replace this with Redis or any other backing store as long as:
        .make_key(), .get(), .set() remain stable.
    """

    max_entries: int = 1024
    _store: Dict[str, Tuple[float, Any]] = field(default_factory=dict)

    def make_key(self, domain: str, plan: Any, ctx: Any) -> str:
        """
        Create a stable hash key from (domain, plan, context signature).
        """
        try:
            plan_data = (
                plan.model_dump()
                if hasattr(plan, "model_dump")
                else plan.__dict__
            )
        except Exception:
            plan_data = str(plan)

        ctx_data = {
            "job_title": getattr(getattr(ctx, "job", None), "title", ""),
            "role_type": getattr(getattr(ctx, "job", None), "role_type", ""),
            "seniority": getattr(getattr(ctx, "job", None), "seniority", ""),
            "config_hash": hashlib.sha256(
                json.dumps(
                    getattr(ctx.config, "model_dump", lambda: {})(),
                    sort_keys=True,
                    default=str,
                ).encode("utf-8")
            ).hexdigest(),
        }

        raw = json.dumps(
            {"domain": domain, "plan": plan_data, "ctx": ctx_data},
            sort_keys=True,
            default=str,
        )
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        return f"{domain}:{digest}"

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value.
        """
        entry = self._store.get(key)
        if not entry:
            return None

        ts, value = entry
        record_event("predictive_cache_hit", {"key": key, "age_s": time.time() - ts})
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Store a cached value (evicting oldest if needed).
        """
        if len(self._store) >= self.max_entries:
            oldest_key = min(self._store.items(), key=lambda kv: kv[1][0])[0]
            self._store.pop(oldest_key, None)
            record_event("predictive_cache_eviction", {"evicted_key": oldest_key})

        self._store[key] = (time.time(), value)
        record_event("predictive_cache_set", {"key": key})


# ==============================================================================
# Provider Inference
# ==============================================================================

def _infer_provider(model: str) -> str:
    """
    Infer provider (OpenAI/Anthropic) from model name.

    This is deliberately simple, but can be extended to use explicit routing.
    """
    m = model.lower()

    if m.startswith("gpt") or m.startswith("o") or m.startswith("gpt-5"):
        return "openai"

    if m.startswith("claude"):
        return "anthropic"

    # Future support (Gemini, Cohere, etc.)
    return "openai"


# ==============================================================================
# invoke_model(): Single entrypoint for all LLM calls
# ==============================================================================

class LLMInvocationError(RuntimeError):
    pass


def invoke_model(
    model: str,
    prompt: str,
    sandbox: SandboxConfig,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """
    Unified LLM invocation API for v10_10.

    Ensures:
        - provider detection
        - sandbox max_tokens enforcement
        - observability
        - consistent exception handling

    Called by:
        - StrategyLLMAgent
        - DraftingGuild
        - SemanticQAAgent
        - ConstitutionalSafetyAgent
    """

    provider = _infer_provider(model)
    max_tokens = min(max_tokens, sandbox.max_tokens_per_call)

    record_event(
        "llm_invoke_start",
        {"model": model, "provider": provider, "temperature": temperature, "max_tokens": max_tokens},
    )

    try:
        # ----------------------------------------------------------------------
        # OpenAI Provider
        # ----------------------------------------------------------------------
        if provider == "openai":
            if openai is None:
                raise LLMInvocationError("openai package is not installed.")

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=sandbox.request_timeout_s,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.choices[0].message.content or ""
            record_event("llm_invoke_success", {"provider": provider, "len": len(text)})
            return text

        # ----------------------------------------------------------------------
        # Anthropic Provider
        # ----------------------------------------------------------------------
        elif provider == "anthropic":
            if anthropic is None:
                raise LLMInvocationError("anthropic package is not installed.")

            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=sandbox.request_timeout_s,
                messages=[{"role": "user", "content": prompt}],
            )

            parts = []
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    parts.append(getattr(block, "text", ""))
            text = "\n".join(parts)

            record_event("llm_invoke_success", {"provider": provider, "len": len(text)})
            return text

        # ----------------------------------------------------------------------
        # Unsupported provider
        # ----------------------------------------------------------------------
        else:
            raise LLMInvocationError(f"Unsupported provider inferred for model: {model}")

    except Exception as exc:
        record_exception("llm_invoke_failure", exc)
        raise LLMInvocationError(f"Failed to invoke model {model}: {exc}") from exc
