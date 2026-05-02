"""Qwen-local LLM client adapter for apps_lic HOP5 generation.

Wave 4 P4.1 (plan apps-eval-qwen32b-rollout-b7c4d9): provides a thin,
async ``llm_client``-shaped adapter that routes
:meth:`HOP5GenerationAgent` LLM calls to the local Qwen-32B vLLM
server. The HOP5 agent already declares the injection point
(``llm_client: Any | None``) and consumes it via ``self.llm.generate(
prompt, temperature=...)`` inside ``_run_async`` (see lines 313 + 394
of ``apps_lic/engines/HOP5GenerationAgent.py``). This module supplies
the canonical Qwen-backed implementation.

Contract
--------
Public method::

    await client.generate(prompt: str, *, temperature: float = 0.7,
                          max_tokens: int = 500) -> str

The return is the raw assistant text — no JSON parsing, no envelope.
HOP5's K.3 / K.5A consumers strip the text and embed it into the
candidate body / synthetic-bullet slots. The temperature is honored
per-call (the resolver in
``apps_lic/engines/section_temperature_resolver.py`` derives
per-(archetype, section) temperatures upstream).

Failure semantics
-----------------
The adapter is fail-soft. On any preflight failure, SDK absence,
gateway exception, or empty response it returns ``""`` (empty string).
HOP5 already treats empty / missing LLM output as "fall back to
deterministic stub" (lines 315-317 / 398-401), so an empty return
keeps the candidate-generation pipeline green even when the local
Qwen server is unreachable.

Marker emission
---------------
Each call emits a ``JUDGE_DECISION`` marker (used loosely here as a
generation-availability marker; the calibration harness aggregates by
``app_name`` and ``rubric_id``). ``app_name=apps_lic.hop5_generation``,
``rubric_id=lic_hop5_generation_v1`` so the weekly calibration report
can track Qwen-uptime + parse-success ratio per app.

Composition root wiring
-----------------------
The composition root (or test fixture) injects an instance via the
``llm_client`` keyword on ``HOP5GenerationAgent``::

    from apps_lic.integrations.qwen_llm_client import QwenLLMClient
    from apps_lic.engines.HOP5GenerationAgent import HOP5GenerationAgent

    agent = HOP5GenerationAgent(llm_client=QwenLLMClient())

Authoring this adapter does NOT mutate any composition root — it
supplies the canonical implementation that future wiring will pick
up. The HOP5 fallback path (``self.llm is None`` → deterministic
stub) keeps the today-state safe.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover — type-checking-only imports
    pass

_LOGGER = logging.getLogger(__name__)


class QwenLLMClient:
    """Async LLM-client adapter pointed at the local Qwen vLLM server.

    Use one instance per process (or one per agent in tests). The
    adapter holds a single ``openai.AsyncOpenAI`` client and reuses
    its connection pool across calls.
    """

    def __init__(
        self,
        *,
        timeout_s: float = 30.0,
        emit_marker: bool = True,
    ) -> None:
        self._timeout_s = timeout_s
        self._emit_marker = emit_marker
        self._client = None  # lazy-initialized in generate()
        self._client_init_failed = False

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Run ``prompt`` through Qwen-local; return raw assistant text.

        Returns empty string on any failure path so HOP5's downstream
        ``elif self.llm:`` / ``if self.llm:`` defensive checks keep
        the candidate-generation pipeline green.
        """
        # Preflight: is local vLLM up?
        try:
            from agentic_core.L2_execution.healers.vllm_health_probe import (  # noqa: PLC0415
                is_qwen_available,
            )
        except ImportError:
            return ""
        if not is_qwen_available():
            self._emit("preflight_failed", "deterministic_fallback", 0.0)
            return ""

        # Lazy SDK + model-registry imports.
        try:
            import openai  # type: ignore  # noqa: PLC0415
        except ImportError:
            return ""

        try:
            from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
                QWEN_LOCAL_MODEL_ID,
                VLLM_BASE_URL,
            )
        except ImportError:
            return ""

        # Lazy client init — survives across calls; on init-failure
        # set the flag so subsequent calls don't retry the broken
        # client until the process restarts.
        if self._client is None and not self._client_init_failed:
            try:
                self._client = openai.AsyncOpenAI(
                    base_url=VLLM_BASE_URL,
                    api_key="not-needed",  # vLLM ignores auth in local mode
                    timeout=self._timeout_s,
                )
            except Exception as exc:  # guardian: allow-broad-exception -- AsyncOpenAI raises heterogeneous on init (ssl, network, env); fail-soft preserves HOP5 deterministic stub
                _LOGGER.info("[apps_lic.qwen_llm] async client init failed: %s", exc)
                self._client_init_failed = True
                self._emit("client_init_failed", QWEN_LOCAL_MODEL_ID, 0.0)
                return ""
        if self._client is None:
            return ""

        started = time.time()
        try:
            resp = await self._client.chat.completions.create(
                model=QWEN_LOCAL_MODEL_ID,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior B2B copywriter producing crisp, "
                            "compliance-aware LinkedIn outreach. Return ONLY "
                            "the requested fragment — no preamble, no JSON, "
                            "no markdown fence."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=float(temperature),
                max_tokens=int(max_tokens),
            )
        except Exception as exc:  # guardian: allow-broad-exception -- AsyncOpenAI-over-vLLM raises heterogeneous (APIError/Connection/Timeout); fail-soft preserves HOP5 deterministic stub
            _LOGGER.info("[apps_lic.qwen_llm] qwen call failed: %s", exc)
            self._emit(
                "gateway_exception",
                QWEN_LOCAL_MODEL_ID,
                (time.time() - started) * 1000.0,
            )
            return ""

        text = (resp.choices[0].message.content or "") if resp.choices else ""
        if not text.strip():
            self._emit(
                "empty_response",
                QWEN_LOCAL_MODEL_ID,
                (time.time() - started) * 1000.0,
            )
            return ""

        self._emit(
            "none",
            QWEN_LOCAL_MODEL_ID,
            (time.time() - started) * 1000.0,
            accepted=True,
        )
        return text.strip()

    def _emit(
        self,
        fallback_reason: str,
        model_used: str,
        latency_ms: float,
        *,
        accepted: bool = False,
    ) -> None:
        """Best-effort ``JUDGE_DECISION`` marker emission. Never raises."""
        if not self._emit_marker:
            return
        try:
            from tools.capture.append_marker import append_marker  # noqa: PLC0415
        except ImportError:
            return
        payload = (
            "JUDGE_DECISION: type=judge_decision, "
            "app_name=apps_lic.hop5_generation, "
            "rubric_id=lic_hop5_generation_v1, "
            "rubric_hash=inline, "
            f"accepted={accepted}, "
            "composite=0.0, "
            f"model_used={model_used}, "
            f"fallback_reason={fallback_reason}, "
            "first_failed_gate=none, "
            f"latency_ms={latency_ms:.1f}"
        )
        try:
            append_marker(payload, session_hint="apps_lic.hop5_generation")
        except (OSError, PermissionError):
            pass


__all__ = ["QwenLLMClient"]
