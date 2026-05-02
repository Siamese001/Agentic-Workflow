"""Local Qwen vLLM judge adapter (OpenAI-compatible Chat Completions API).

Closes gap P-1 from the 2026-05-02 gap-closure audit
(``docs/reports/agentic_core_eval_control_audit/2026-05-02-gap-closure.md``):
the Exit-eval judges directory previously shipped only Anthropic / OpenAI /
generic-HTTP backends, so Exit-side judging defaulted to an external API on
every invocation. This adapter routes the same ``BaseHttpJudge`` contract at
a local vLLM endpoint, making Qwen the cheapest-safe primary judge per the
parent audit recommendation while preserving the external adapters as
escalation paths.

Endpoint defaults to ``${VLLM_BASE_URL}/v1/chat/completions`` (vLLM exposes an
OpenAI-compatible Chat Completions surface). Model defaults to
``QWEN_LOCAL_MODEL_ID`` from the L0 model registry, with ``VLLM_MODEL_NAME``
env override for parity with ``agentic_core/evaluation/judges/qwen_judge_provider.py``.
"""

from __future__ import annotations

import json
import os
from typing import Any

from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges._base_http_judge import (
    BaseHttpJudge,
    _HttpRequest,
)


def _resolve_default_model() -> str:
    """Resolve the Qwen model id, deferring the import to call time.

    The L0 ``model_registry`` lives in a different layer; importing it eagerly
    at module load creates a needless layer dependency. Defer until we need
    the constant. Fall back to the legacy default if the registry is unavailable
    in the current build (e.g. minimal test environments).
    """
    env_model = os.environ.get("VLLM_MODEL_NAME", "").strip()
    if env_model:
        return env_model
    try:
        from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
            QWEN_LOCAL_MODEL_ID,
        )
    except ImportError:  # guardian: allow-default-fallback -- minimal envs may not ship the L0 model registry; the legacy public model id is the documented fallback used by the sibling QwenJudgeProvider in evaluation/judges/qwen_judge_provider.py
        return "Qwen/Qwen2.5-32B-Instruct"
    return QWEN_LOCAL_MODEL_ID


_DEFAULT_BASE_URL_ENV = "VLLM_BASE_URL"
_DEFAULT_BASE_URL_FALLBACK = "http://localhost:8000"


class QwenJudge(BaseHttpJudge):
    """Judge backed by a local vLLM server using OpenAI-compatible chat shape.

    Endpoint resolution (in order):
        constructor ``endpoint`` arg
        > ``{VLLM_BASE_URL}/v1/chat/completions``
        > ``{VLLM_BASE_URL_FALLBACK}/v1/chat/completions``

    Model resolution (in order):
        constructor ``model`` arg
        > ``VLLM_MODEL_NAME`` env var
        > ``QWEN_LOCAL_MODEL_ID`` from L0 model registry
        > ``Qwen/Qwen2.5-32B-Instruct`` legacy fallback

    Auth: vLLM in single-tenant mode typically does not require an Authorization
    header. If the deployment uses an API gateway, pass ``api_key=`` or set
    ``VLLM_API_KEY`` and the Authorization header will be added.

    Temperature is forced to 0.0 for deterministic judging — matches the
    sibling ``QwenJudgeProvider`` and ``OpenAIJudge`` adapters.
    """

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        endpoint: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> None:
        resolved_model = model or _resolve_default_model()
        super().__init__(model=resolved_model, timeout=timeout)
        self._api_key = api_key
        self._endpoint = self._resolve_endpoint(endpoint, base_url)
        self._temperature = float(temperature)
        self._max_tokens = int(max_tokens)

    @staticmethod
    def _resolve_endpoint(
        endpoint_arg: str | None,
        base_url_arg: str | None,
    ) -> str:
        if endpoint_arg:
            return endpoint_arg
        base = (
            base_url_arg
            or os.environ.get(_DEFAULT_BASE_URL_ENV, "").strip()
            or _DEFAULT_BASE_URL_FALLBACK
        )
        # Strip trailing slash so the joined path is clean.
        base = base.rstrip("/")
        return f"{base}/v1/chat/completions"

    def _resolve_key(self) -> str | None:
        """vLLM auth is optional; return None when no key is configured."""
        key = self._api_key or os.environ.get("VLLM_API_KEY")
        if not key:
            return None
        return key

    def _build_request(self, system: str, user: str) -> _HttpRequest:
        body = {
            "model": self._model,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers: dict[str, str] = {"content-type": "application/json"}
        key = self._resolve_key()
        if key is not None:
            headers["authorization"] = f"Bearer {key}"
        return _HttpRequest(
            url=self._endpoint,
            method="POST",
            headers=headers,
            body=json.dumps(body).encode("utf-8"),
        )

    def _extract_text(self, response_json: Any) -> str:
        """vLLM's OpenAI-compat response: ``{"choices": [{"message": {"content": "..."}}]}``.

        Mirrors :class:`OpenAIJudge._extract_text` because the response shape is
        identical. Kept as an independent implementation rather than inheriting
        from OpenAIJudge so the Qwen and OpenAI adapters can diverge later
        without entangling each other.
        """
        if not isinstance(response_json, dict):
            raise GraderError("Qwen response was not an object")
        choices = response_json.get("choices")
        if not isinstance(choices, list) or not choices:
            raise GraderError("Qwen response missing choices array")
        first = choices[0]
        if not isinstance(first, dict):
            raise GraderError("Qwen choice was not an object")
        message = first.get("message")
        if not isinstance(message, dict):
            raise GraderError("Qwen choice missing message")
        content = message.get("content")
        if not isinstance(content, str):
            raise GraderError("Qwen message content not string")
        return content


__all__ = ["QwenJudge"]
