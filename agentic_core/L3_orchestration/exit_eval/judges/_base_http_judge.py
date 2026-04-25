"""Shared HTTP + JSON-parse scaffolding for LLM-judge adapters.

Kept private (leading-underscore filename) because the public surface is
the three concrete adapters (``AnthropicJudge``, ``OpenAIJudge``,
``HttpJudge``). This module handles:

- Timeout-bounded HTTP via ``urllib`` (zero external dep).
- JSON response parsing with abstain detection (``UNKNOWN`` verdict).
- Score clamping to the dimension scale.
- Explicit failure modes mapped to ``TimeoutError`` / ``GraderError`` so
  the gate layer can route correctly per H8.

The adapters subclass ``BaseHttpJudge`` and override
``_build_request(system, user)`` to produce provider-specific JSON
bodies, and ``_extract_text(resp_json)`` to pull the assistant's text
out of the provider's response shape.
"""

from __future__ import annotations

import json
import re
import socket
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import (
    JudgeProtocol,
    JudgeResponse,
)
from agentic_core.L3_orchestration.exit_eval.judges.prompt_templates import (
    build_judge_prompt,
)


@dataclass(frozen=True)
class _HttpRequest:
    url: str
    method: str
    headers: dict[str, str]
    body: bytes


# Matches a JSON object at the start or anywhere in the text. Judges
# sometimes wrap the JSON in prose despite instructions; we tolerate
# that by extracting the first well-formed object.
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


class BaseHttpJudge(JudgeProtocol, ABC):
    """Base class for HTTP-backed LLM-judge adapters.

    Subclasses provide the provider-specific request shape and response
    parsing; this base handles timeout, input sanitation via shared
    prompt templates, and structured response parsing.
    """

    def __init__(self, *, model: str, timeout: float = 30.0) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        self._model = model
        self._timeout = float(timeout)

    # ------------------------------------------------------------------ #
    # JudgeProtocol
    # ------------------------------------------------------------------ #

    def judge(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> JudgeResponse:
        if dimension.grader_class is not GraderClass.MODEL_BASED:
            raise GraderError(f"judge called on non-MODEL_BASED dimension {dimension.name}")
        system_prompt, user_prompt = build_judge_prompt(dimension.name, context)
        request = self._build_request(system_prompt, user_prompt)
        raw_text = self._call_http(request)
        return self._parse_response(dimension, raw_text)

    # ------------------------------------------------------------------ #
    # Extension points
    # ------------------------------------------------------------------ #

    @abstractmethod
    def _build_request(self, system: str, user: str) -> _HttpRequest: ...

    @abstractmethod
    def _extract_text(self, response_json: Any) -> str:
        """Pull the assistant-generated text out of a parsed JSON response."""

    # ------------------------------------------------------------------ #
    # HTTP + JSON plumbing
    # ------------------------------------------------------------------ #

    def _call_http(self, req: _HttpRequest) -> str:
        request = urllib.request.Request(
            url=req.url,
            data=req.body,
            method=req.method,
            headers=req.headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as resp:
                body = resp.read()
        except socket.timeout as exc:
            raise TimeoutError(f"judge HTTP timeout after {self._timeout}s: {exc}") from exc
        except urllib.error.HTTPError as exc:
            # 4xx/5xx from provider. Route as GraderError (non-timeout).
            detail = ""
            try:
                detail = exc.read().decode("utf-8", errors="ignore")[:500]
            except OSError:  # guardian: allow-default-fallback -- best-effort extraction of error-response body during HTTPError handling; placeholder is the conventional surface when the underlying socket has already closed; the GraderError is raised unconditionally below so the failure is never silenced
                detail = "<body unavailable>"
            raise GraderError(f"judge HTTP {exc.code} {exc.reason}: {detail}") from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, socket.timeout):
                raise TimeoutError(f"judge HTTP timeout: {exc.reason}") from exc
            raise GraderError(f"judge HTTP URLError: {exc.reason}") from exc

        try:
            parsed = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise GraderError(f"judge response was not JSON: {exc}") from exc
        return self._extract_text(parsed)

    def _parse_response(self, dimension: Dimension, text: str) -> JudgeResponse:
        """Extract verdict/score/reasoning from the judge's text reply."""
        if not isinstance(text, str) or not text.strip():
            raise GraderError("judge returned empty text")

        match = _JSON_OBJECT_RE.search(text)
        if not match:
            raise GraderError(f"no JSON object in judge response: {text[:200]!r}")
        try:
            blob = json.loads(match.group(0))
        except ValueError as exc:
            raise GraderError(f"judge JSON parse failed: {exc}") from exc
        if not isinstance(blob, dict):
            raise GraderError("judge JSON was not an object")

        verdict_raw = str(blob.get("verdict", "")).strip().upper()
        reasoning = str(blob.get("reasoning", ""))[:500]

        if verdict_raw == "UNKNOWN":
            return JudgeResponse(score=0.0, abstain=True, reasoning=reasoning)

        if verdict_raw not in ("PASS", "FAIL"):
            raise GraderError(f"judge verdict must be PASS|FAIL|UNKNOWN, got {verdict_raw!r}")

        score_raw = blob.get("score")
        try:
            score = float(score_raw) if score_raw is not None else (1.0 if verdict_raw == "PASS" else 0.0)
        except (TypeError, ValueError) as exc:
            raise GraderError(f"judge score not numeric: {score_raw!r}") from exc

        # Clamp to the dimension's declared scale.
        lo, hi = dimension.scale
        score = max(lo, min(hi, score))
        return JudgeResponse(score=score, abstain=False, reasoning=reasoning)


__all__ = ["BaseHttpJudge", "_HttpRequest"]
