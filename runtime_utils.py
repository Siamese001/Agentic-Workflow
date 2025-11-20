# FILE: 10_10/runtime_utils.py
"""
Runtime Utilities for Agentic Workflow v10_10
=============================================

Responsibilities:
    • invoke_model(): unified LLM invocation for OpenAI & Anthropic.
    • PredictiveCacheManager: semantic/predictive caching.
    • SandboxConfig: execution constraints.
    • get_sandbox(): normalized sandbox loader.

Non-Responsibilities:
    • No agent logic.
    • No planning/orchestration/state.
    • No tool policies.
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
# Sandbox
# =============================================================================

@dataclass
class SandboxConfig:
    """
    Logical sandbox constraints.
    Actual isolation is provided by container/runtime.
    """
    name: str = "default"
    allow_network: bool = True
    request_timeout_s: int = 60
    max_tokens_per_call: int = 2048


def get_sandbox(config: Optional[SandboxConfig]) -> SandboxConfig:
    """
    Ensure sandbox is never None.
    """
    return config or SandboxConfig()


# =============================================================================
# Predictive Cache
# =============================================================================

@dataclass
class PredictiveCacheManager:
    """
    Lightweight in-memory predictive cache.

    Stores:
        domain:plan:context → cached LLM or RAG results

    Evicts oldest entries when full.
    """

    max_entries: int = 1024
    _store: Dict[str, Tuple[float, Any]] = field(default_factory=dict)

    def make_key(self, domain: str, plan: Any, ctx: Any) -> str:
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
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{domain}:{digest}"

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None

        timestamp, value = entry
        record_event("predictive_cache_hit", {"key": key, "age_s": time.time() - timestamp})
        return value

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self.max_entries:
            oldest = min(self._store, key=lambda k: self._store[k][0])
            self._store.pop(oldest, None)
            record_event("predictive_cache_evict", {"evicted_key": oldest})

        self._store[key] = (time.time(), value)
        record_event("predictive_cache_set", {"key": key})


# =============================================================================
# LLM Invocation
# =============================================================================

class LLMInvocationError(RuntimeError):
    pass


def _detect_provider(model: str) -> str:
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
    Unified LLM invocation for OpenAI + Anthropic.
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
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=sandbox.request_timeout_s,
            )
            chunks = [
                block.text
                for block in resp.content
                if getattr(block, "type", None) == "text"
            ]
            text = "\n".join(chunks)

        else:
            raise LLMInvocationError(f"Unsupported provider inferred for model: {model}")

        record_event("invoke_model_success", {"model": model, "length": len(text)})
        return text

    except Exception as exc:
        record_exception("invoke_model_failure", exc)
        raise LLMInvocationError(f"LLM invocation failed for model {model}: {exc}") from exc
