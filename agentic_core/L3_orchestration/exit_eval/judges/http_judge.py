"""Provider-agnostic HTTP judge adapter.

For local vLLM / Ollama / Mistral / self-hosted endpoints. Caller
provides the response-extraction lambda because response shapes differ
across providers. Default extractor handles the common
``{"choices": [{"message": {"content": "..."}}]}`` OpenAI-compatible
shape.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges._base_http_judge import (
    BaseHttpJudge,
    _HttpRequest,
)


def _default_extractor(resp: Any) -> str:
    if not isinstance(resp, dict):
        raise GraderError("HttpJudge response not a JSON object")
    choices = resp.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            msg = first.get("message")
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"]
    text = resp.get("text")
    if isinstance(text, str):
        return text
    raise GraderError("HttpJudge default extractor found no text in response")


class HttpJudge(BaseHttpJudge):
    """Generic HTTP judge for OpenAI-compatible endpoints.

    Args:
        endpoint: full URL (must end in chat-completion-style path).
        model: model id sent in the body.
        auth_header: optional pre-formatted value for ``Authorization``.
        extra_headers: merged into the request headers.
        extractor: function converting parsed JSON → assistant text.
        request_builder: optional function overriding the default body.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        model: str,
        auth_header: str | None = None,
        extra_headers: dict[str, str] | None = None,
        extractor: Callable[[Any], str] = _default_extractor,
        request_builder: Callable[[str, str, str, int], dict[str, Any]] | None = None,
        timeout: float = 30.0,
        max_tokens: int = 512,
    ) -> None:
        super().__init__(model=model, timeout=timeout)
        self._endpoint = endpoint
        self._auth_header = auth_header
        self._extra_headers = dict(extra_headers or {})
        self._extractor = extractor
        self._request_builder = request_builder or self._default_body
        self._max_tokens = int(max_tokens)

    @staticmethod
    def _default_body(system: str, user: str, model: str, max_tokens: int) -> dict[str, Any]:
        return {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0.0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

    def _build_request(self, system: str, user: str) -> _HttpRequest:
        body = self._request_builder(system, user, self._model, self._max_tokens)
        headers: dict[str, str] = {"content-type": "application/json"}
        if self._auth_header:
            headers["authorization"] = self._auth_header
        headers.update(self._extra_headers)
        return _HttpRequest(
            url=self._endpoint,
            method="POST",
            headers=headers,
            body=json.dumps(body).encode("utf-8"),
        )

    def _extract_text(self, response_json: Any) -> str:
        return self._extractor(response_json)


__all__ = ["HttpJudge"]
