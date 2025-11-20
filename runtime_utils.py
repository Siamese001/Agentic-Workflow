# FILE: 10_10/runtime_utils.py
"""
Runtime Utilities for Agentic Workflow v10_10
=============================================

Responsibilities:
    • invoke_model():  unified LLM invocation for all cognitive agents.
    • SandboxConfig:   execution sandbox abstraction.
    • get_sandbox():   sandbox loader.
    • PredictiveCacheManager: in-memory predictive/semantic cache.

Non-Responsibilities:
    • No agent logic.
    • No planning or orchestration.
    • No global state.
    • No prompt logic.

This module aligns with:
    - Pillar 7 (Context Budgeting)
    - Pillar 8 (Tool Ecosystem / Resilience)
    - Pillar 11 (Cost & Optimization)
    - Pillar 14 (Execution Sandbox)
"""

from __future__ import annotations

import os
import json
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from observability import record_event, record_exception


# =============================================================================
# Sandbox Configuration
# =============================================================================

@dataclass
class SandboxConfig:
    """
    Sandbox abstraction for tool/LLM execution.

    Note: Windsurf / remote container provides actual isolation.
    This config supplies logical constraints for:
        • timeouts
        • max tokens
        • network usage
    """

    name: str = "default"
    allow_network: bool = True
    request_timeout_s: int = 60
    max_tokens_per_call: int = 2048


def get_sandbox(config: Optional[SandboxConfig]) -> SandboxConfig:
    """
    Ensure sandbox config is never None.
    """
    if config is None:
        return SandboxConfig()
    return config


# =============================================================================
# Predictive Cache (Optional)
# =============================================================================

@dataclass
class PredictiveCacheManager:
    """
    Lightweight predictive cache for expensive operations (RAG + LLM).

    Implementation:
        • In-memory dict keyed by stable SHA256 of (domain, plan, context).
        • Values = (timestamp, payload)
        • Evicts oldest entry when over capacity.

    Compatible with:
        • L2.execute_rag
        • L2 cognitive agents (future extensions)
    """

    max_entries: int = 1024
    _store: Dict[str, Tuple[float, Any]] = field(default_factory=dict)

    def make_key(self, domain: str, plan: Any, ctx: Any) -> str:
        """
        Create a stable hash key from:
            - domain string (e.g., "rag", "strategy")
            - plan object (must support model_dump)
            - job + config signature
        """
        try:
            p = plan.model_dump()
        except Exception:
            p = str(plan)

        ctx_sig = {
            "job_title": getattr(ctx.job, "title", ""),
            "seniority": getattr(ctx.job, "seniority", ""),
            "role_type": getattr(ctx.job, "role_type", ""),
            "config": getattr(ctx.config, "model_dump", lambda: {})(),
        }

        raw = json.dumps(
            {"domain": domain, "plan": p, "ctx": ctx_sig},
            sort_keys=True,
            default=str,
        )

        key = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{domain}:{key}"

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value, if present.
        """
        entry = self._store.get(key)
        if not entry:
            return None

        timestamp, value = entry
        record_event(
            "predictive_cache_hit",
            {"key": key, "age_s": time.time() - timestamp},
        )
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Insert or replace a cached entry.
        Evict oldest entry if capacity exceeded.
        """
        if len(self._store) >= self.max_entries:
            oldest_key = min(self._store, key=lambda k: self._store[k][0])
            self._store.pop(oldest_key, None)
            record_event("predictive_cache_evict", {"evicted_key": oldest_key})

        self._store[key] = (time.time(), value)
        record_event("predictive_cache_set", {"key": key})


# =============================================================================
# Unified LLM Invocation
# =============================================================================

class LLMInvocationError(RuntimeError):
    """Raised when an LLM request fails."""


def _detect_provider(model: str) -> str:
    """
    Infer provider from model identifier.
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
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """
    Unified LLM invocation for v10_10.

    Parameters:
        model:       model name from RoutingPolicy (e.g., "gpt-5.1-codex")
        prompt:      rendered prompt
        sandbox:     SandboxConfig
        temperature: sampling temperature
        max_tokens:  max generation tokens (capped by sandbox)

    Returns:
        text response from the LLM.

    Raises:
        LLMInvocationError on failure.
    """

    provider = _detect_provider(model)
    max_tokens = min(max_tokens, sandbox.max_tokens_per_call)

    record_event(
        "invoke_model_start",
        {"model": model, "provider": provider, "temperature": temperature, "max_tokens": max_tokens},
    )

    try:
        if provider == "openai":
            import openai

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
            import anthropic

            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=sandbox.request_timeout_s,
                messages=[{"role": "user", "content": prompt}],
            )

            chunks = []
            for block in resp.content:
                if getattr(block, "type", None) == "text":
                    chunks.append(block.text)
            text = "\n".join(chunks)

        else:
            raise LLMInvocationError(f"Unsupported provider inferred for model: {model}")

        record_event("invoke_model_success", {"model": model, "length": len(text)})
        return text

    except Exception as exc:
        record_exception("invoke_model_failure", exc)
        raise LLMInvocationError(f"LLM invocation failed for model {model}: {exc}") from exc
