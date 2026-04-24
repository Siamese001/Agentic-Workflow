"""QwenJudgeProvider — local-vLLM judge provider.

Implements the ``JudgeProvider`` protocol (see
``agentic_core.evaluation.judges.types``) by routing judge prompts through
the L3 ``QwenInferenceGateway``. Mirrors ``GeminiJudgeProvider`` in
``agentic_core.evaluation.judges.provider_registry`` so callers can swap
``JUDGE_PROVIDER=qwen`` with no other changes.

Why local-vLLM judges matter
----------------------------
* Zero marginal cost — eliminates per-eval Gemini/OpenAI billing.
* No rate limiting — bulk rubric runs and regression sweeps complete
  without 429s.
* Deterministic by default (temperature=0.0) — matches how other judges
  are configured for reproducibility.

Plan ref: ``.windsurf/plans/qwen-adoption-waves-a7f3c2.md`` Wave A / Phase A3.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from typing import Any, cast

from agentic_core.L0_routing.config.model_registry import (
    QWEN_LOCAL_MODEL_ID,
)

_log = logging.getLogger(__name__)


def _run_async(coro: Any) -> Any:
    """Run ``coro`` regardless of running-loop state.

    Mirrors the helper in
    ``agentic_core.L2_execution.enforcement._provider_local_vllm`` but is
    inlined here to avoid reaching into L2 private internals from
    the evaluation layer.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    import threading  # noqa: PLC0415

    result: dict[str, Any] = {}

    def _worker() -> None:
        loop = asyncio.new_event_loop()
        try:
            result["value"] = loop.run_until_complete(coro)
        except (
            BaseException
        ) as exc:  # guardian: allow-broad-catch -- propagate worker exception back to caller thread
            result["error"] = exc
        finally:
            loop.close()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join()
    if "error" in result:
        raise result["error"]
    return result.get("value")


class QwenJudgeProvider:
    """Local-vLLM Qwen judge provider.

    Shape-compatible with ``GeminiJudgeProvider``:
    * ``provider_id`` — ``"qwen"``
    * ``cost_per_eval`` — ``0.0`` (local GPU, no billing)
    * ``model_id`` — resolved from ``QWEN_LOCAL_MODEL_ID`` SSOT (env override
      via ``VLLM_MODEL_NAME``)
    * ``judge(prompt, rubric_id)`` — async; returns the standard judge dict
      shape (``score``, ``reasoning``, ``rubric_id``, ``provider``,
      ``criteria_scores``, ``model``).
    """

    def __init__(self, model: str | None = None, app_name: str = "qwen_judge") -> None:
        env_model = os.getenv("VLLM_MODEL_NAME")
        self._model = model or env_model or QWEN_LOCAL_MODEL_ID
        self._app_name = app_name

    @property
    def provider_id(self) -> str:
        return "qwen"

    @property
    def cost_per_eval(self) -> float:
        # Local GPU inference — zero marginal cost.
        return 0.0

    @property
    def model_id(self) -> str:
        return self._model

    @staticmethod
    def _clean(raw: str) -> str:
        return re.sub(r"```(?:json)?|```", "", raw).strip()

    @staticmethod
    def _parse(raw: str) -> dict[str, Any]:
        try:
            return cast(dict[str, Any], json.loads(raw))
        except json.JSONDecodeError:
            return cast(dict[str, Any], json.loads(QwenJudgeProvider._clean(raw)))

    async def judge(self, prompt: str, rubric_id: str) -> dict[str, Any]:
        """Score ``prompt`` against ``rubric_id`` using local vLLM Qwen.

        Returns a dict with ``score``, ``reasoning``, ``rubric_id``,
        ``provider``, ``criteria_scores``, and ``model`` keys — same shape
        as ``GeminiJudgeProvider.judge`` so caller code is interchangeable.
        """
        # Import locally to avoid L_SHARED→L3 cycle risk at module load.
        from agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway import (  # noqa: PLC0415
            QwenInferenceRequest,
            get_qwen_inference_gateway,
        )

        gateway = await get_qwen_inference_gateway(model_id=self._model)
        request = QwenInferenceRequest(
            app_name=self._app_name,
            prompt=prompt,
            temperature=0.0,  # determinism for judge rubrics
            max_tokens=2048,
            use_cache=True,
        )
        response = await gateway.infer(request)

        if not response.success:
            _log.warning(
                "[QwenJudgeProvider] inference failed for %s: %s",
                rubric_id,
                response.error_message,
            )
            return {
                "score": 0.0,
                "reasoning": f"Qwen inference failed: {response.error_message}",
                "rubric_id": rubric_id,
                "provider": self.provider_id,
                "error": response.error_message,
                "model": self._model,
            }

        raw = response.response or ""
        try:
            data = self._parse(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            _log.warning(
                "[QwenJudgeProvider] Failed to parse response for %s: %s",
                rubric_id,
                exc,
            )
            return {
                "score": 0.0,
                "reasoning": f"Parse error: {exc}",
                "rubric_id": rubric_id,
                "provider": self.provider_id,
                "error": str(exc),
                "raw_response": raw[:500],
                "model": self._model,
            }

        reasoning = data.pop("reasoning", "")
        criteria_scores = {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}

        if criteria_scores:
            score = sum(criteria_scores.values()) / len(criteria_scores)
        else:
            score = 0.0

        return {
            "score": round(score, 4),
            "reasoning": reasoning,
            "rubric_id": rubric_id,
            "provider": self.provider_id,
            "criteria_scores": criteria_scores,
            "model": self._model,
        }

    def judge_sync(self, prompt: str, rubric_id: str) -> dict[str, Any]:
        """Sync wrapper over :meth:`judge` for callers outside an event loop."""
        return _run_async(self.judge(prompt, rubric_id))


__all__ = ["QwenJudgeProvider"]
