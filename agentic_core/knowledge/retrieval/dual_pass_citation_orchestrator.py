"""Dual-pass citation + JSON orchestrator.

Anthropic's native-citations feature is incompatible with strict JSON output
(``response_format`` / tool-use structured output). When a caller needs BOTH
a grounded answer with verifiable citations AND a machine-parseable JSON
response, the Anthropic guidance is a two-pass design:

    Pass 1  (grounded answer)
      prompt  = render_anthropic_prompt(envelope, query)
      payload = build_messages_payload(..., cache_boundary_hint=...)
      call    = gateway(payload, citations_enabled=True)
      output  = extract_answer_text(response) + extract_citations(response)

    Pass 2  (JSON shape)
      prompt  = "{answer_from_pass_1}\n\nReformat as JSON per schema: {schema}"
      call    = gateway(prompt)                 # NO citations, NO retrieval
      output  = json.loads(response_text)

Pass 2 deliberately does NOT re-query retrieval — it shapes the pass-1 answer
only. This preserves the audit trail: the grounded evidence for every factual
claim lives in the pass-1 Citations; pass 2 is a pure transformation.

Composable with any gateway via two narrow callables:
    - ``pass1_fn(payload: dict) -> Any``  (returns Anthropic response)
    - ``pass2_fn(prompt: str) -> str``    (returns raw text)

Both callables are OPTIONAL. When ``pass1_fn`` is None, the orchestrator
returns an empty ``DualPassResult`` with a diagnostic reason — this supports
offline test runs and the current broken-executor state without crashing.

References:
- https://docs.anthropic.com/en/docs/build-with-claude/citations (incompatibility)
- Plan: .windsurf/plans/anthropic-rag-gaps-7f3c2a.md (phase P2.3)
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    CACHE_TTL_5M,
    build_messages_payload,
)
from agentic_core.knowledge.retrieval.anthropic_citation_adapter import (
    citation_coverage_ratio,
    extract_answer_text,
    extract_citations,
)
from agentic_core.knowledge.retrieval.anthropic_prompt_renderer import (
    render_anthropic_prompt,
)
from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    Citation,
    VerifiedChunk,
)
from agentic_core.knowledge.retrieval.prompt_envelope import PromptEnvelope

Logger = logging.getLogger(__name__)

# Reason codes for DualPassResult.status
STATUS_OK = "ok"
STATUS_ABSTAIN = "abstain"  # envelope.abstain_recommended was True
STATUS_NO_GATEWAY = "no_gateway"  # pass1_fn not provided (offline mode)
STATUS_PASS1_FAILED = "pass1_failed"
STATUS_PASS2_FAILED = "pass2_failed"
STATUS_JSON_PARSE_FAILED = "json_parse_failed"
STATUS_JSON_NOT_REQUESTED = "json_not_requested"


class _Pass1Fn(Protocol):
    """Pass-1 gateway callable: takes an Anthropic messages payload, returns response."""

    def __call__(self, payload: dict[str, Any]) -> Any: ...


class _Pass2Fn(Protocol):
    """Pass-2 gateway callable: takes a prompt string, returns response text."""

    def __call__(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class DualPassResult:
    """Output of a full two-pass citation + JSON flow.

    Attributes
    ----------
    answer_text:
        The grounded answer from pass 1 (citations text joined). Empty when
        the orchestrator skipped pass 1 (abstain or offline).
    citations:
        Internal Citation records extracted from the pass-1 response. Empty
        when no citations were returned or when pass 1 was skipped.
    structured_output:
        The JSON-shaped dict from pass 2. None when no schema was requested,
        when pass 1 was skipped, or when JSON parsing failed.
    citation_coverage:
        Fraction of must-use chunks cited at least once (0.0..1.0).
    status:
        One of the STATUS_* constants. Allows callers to route on outcome.
    pass1_raw_response:
        The raw response object from pass 1 (dict or SDK object). Retained
        for audit / replay even when parsing succeeds.
    pass2_raw_text:
        The raw text from pass 2 before JSON parsing. None when pass 2 was
        not run.
    reason:
        Human-readable diagnostic when status != STATUS_OK.
    """

    answer_text: str
    citations: tuple[Citation, ...]
    structured_output: dict[str, Any] | None
    citation_coverage: float
    status: str
    pass1_raw_response: Any = None
    pass2_raw_text: str | None = None
    reason: str = ""


def _build_json_shape_prompt(answer: str, json_schema: dict[str, Any]) -> str:
    """Compose the pass-2 prompt: reshape the grounded answer as JSON.

    Pass 2 is a PURE transformation — it must not add facts, retrieve new
    context, or contradict the pass-1 answer. The instruction explicitly
    forbids augmentation.
    """
    schema_text = json.dumps(json_schema, indent=2, ensure_ascii=False)
    return (
        "You are given a previously-generated grounded answer and a target "
        "JSON schema. Your task is to reformat the answer into JSON matching "
        "the schema EXACTLY. Do not add new facts. Do not remove information "
        "that maps onto a schema field. If the answer does not contain a "
        "value for a required field, use null.\n\n"
        "<answer>\n"
        f"{answer}\n"
        "</answer>\n\n"
        "<schema>\n"
        f"{schema_text}\n"
        "</schema>\n\n"
        "Respond with ONLY the JSON object, no prose, no markdown fences."
    )


# Regex for extracting JSON from a fenced code block. Python's stdlib re
# does not support recursive patterns, so for raw (unfenced) JSON we rely on
# the outermost-brace-span fallback in _extract_json_from_text.
_FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _extract_json_from_text(text: str) -> dict[str, Any] | None:
    """Best-effort JSON object extraction from a model response.

    Tries, in order:
      1. Direct ``json.loads(text)``
      2. Fenced block ```json ... ```
      3. First outermost ``{...}`` span in the text
    Returns None when no parsable object is found.
    """
    if not text:
        return None

    stripped = text.strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    fenced = _FENCED_JSON_RE.search(text)
    if fenced:
        try:
            parsed = json.loads(fenced.group(1))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    # Outermost brace span: find first '{' and last '}'
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last > first:
        try:
            parsed = json.loads(text[first : last + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None

    return None


class DualPassCitationOrchestrator:
    """Executes the two-pass cited-answer + JSON-shape pipeline.

    Gateways are injected as narrow callables — no knowledge of
    SovereignLLMGateway / Anthropic SDK / transport. This keeps the
    orchestrator testable end-to-end without live API access.

    Parameters
    ----------
    pass1_fn:
        Callable that performs the grounded pass. Receives the dict produced
        by build_messages_payload (system + messages). MUST pass
        ``citations.enabled=True`` and the model args to the actual API.
        When None, orchestrator skips pass 1 and returns STATUS_NO_GATEWAY.
    pass2_fn:
        Callable that performs the JSON-shape pass. Receives a plain prompt
        string and returns response text. When None, pass 2 is skipped even
        if json_schema is provided.
    cache_ttl:
        TTL for cache_control markers on the pass-1 prefix. Default 5m.
    """

    def __init__(
        self,
        pass1_fn: _Pass1Fn | Callable[[dict[str, Any]], Any] | None = None,
        pass2_fn: _Pass2Fn | Callable[[str], str] | None = None,
        *,
        cache_ttl: str = CACHE_TTL_5M,
    ) -> None:
        self._pass1_fn = pass1_fn
        self._pass2_fn = pass2_fn
        self._cache_ttl = cache_ttl

    def execute(
        self,
        envelope: PromptEnvelope,
        query: str,
        *,
        json_schema: dict[str, Any] | None = None,
        system_prompt: str = "",
    ) -> DualPassResult:
        """Run both passes and return a DualPassResult.

        Parameters
        ----------
        envelope:
            Completed PromptEnvelope from PromptEnvelopeFactory.
        query:
            User query string to render at the bottom of the pass-1 prompt.
        json_schema:
            When provided, pass 2 runs to reshape the grounded answer.
            When None, pass 2 is skipped and status becomes
            STATUS_JSON_NOT_REQUESTED (a non-error).
        system_prompt:
            Optional system prompt; cached as a static prefix when non-empty.
        """
        if envelope.abstain_recommended:
            return DualPassResult(
                answer_text="",
                citations=(),
                structured_output=None,
                citation_coverage=0.0,
                status=STATUS_ABSTAIN,
                reason="envelope.abstain_recommended=True; no generation",
            )

        if self._pass1_fn is None:
            return DualPassResult(
                answer_text="",
                citations=(),
                structured_output=None,
                citation_coverage=0.0,
                status=STATUS_NO_GATEWAY,
                reason="pass1_fn not provided; orchestrator in offline mode",
            )

        # --- Pass 1: grounded answer with citations -------------------------
        rendered = render_anthropic_prompt(envelope, query)
        payload = build_messages_payload(
            user_prompt=rendered.text,
            system_prompt=system_prompt,
            cache_boundary_hint=rendered.cache_boundary_hint,
            ttl=self._cache_ttl,
        )
        # The caller's pass1_fn is responsible for flipping
        # citations.enabled=True on the actual API request.

        try:
            pass1_response = self._pass1_fn(payload)
        except (RuntimeError, ValueError, OSError) as exc:
            Logger.warning("Pass 1 failed: %s", exc)
            return DualPassResult(
                answer_text="",
                citations=(),
                structured_output=None,
                citation_coverage=0.0,
                status=STATUS_PASS1_FAILED,
                reason=f"pass1_fn raised: {exc!r}",
            )

        answer_text = extract_answer_text(pass1_response)
        chunk_by_index: dict[int, VerifiedChunk] = {
            i: chunk for i, chunk in enumerate(envelope.verified_chunks)
        }
        citations_list = extract_citations(pass1_response, chunk_by_index=chunk_by_index)
        coverage = citation_coverage_ratio(
            citations_list,
            [c for c in envelope.verified_chunks if c.is_must_use],
        )

        # --- Pass 2: JSON shape (optional) ---------------------------------
        if json_schema is None:
            return DualPassResult(
                answer_text=answer_text,
                citations=tuple(citations_list),
                structured_output=None,
                citation_coverage=coverage,
                status=STATUS_JSON_NOT_REQUESTED,
                pass1_raw_response=pass1_response,
            )

        if self._pass2_fn is None:
            return DualPassResult(
                answer_text=answer_text,
                citations=tuple(citations_list),
                structured_output=None,
                citation_coverage=coverage,
                status=STATUS_PASS2_FAILED,
                reason="pass2_fn not provided but json_schema was requested",
                pass1_raw_response=pass1_response,
            )

        shape_prompt = _build_json_shape_prompt(answer_text, json_schema)
        try:
            pass2_text = self._pass2_fn(shape_prompt)
        except (RuntimeError, ValueError, OSError) as exc:
            Logger.warning("Pass 2 failed: %s", exc)
            return DualPassResult(
                answer_text=answer_text,
                citations=tuple(citations_list),
                structured_output=None,
                citation_coverage=coverage,
                status=STATUS_PASS2_FAILED,
                reason=f"pass2_fn raised: {exc!r}",
                pass1_raw_response=pass1_response,
            )

        structured = _extract_json_from_text(pass2_text)
        if structured is None:
            return DualPassResult(
                answer_text=answer_text,
                citations=tuple(citations_list),
                structured_output=None,
                citation_coverage=coverage,
                status=STATUS_JSON_PARSE_FAILED,
                reason="pass 2 response did not contain parseable JSON object",
                pass1_raw_response=pass1_response,
                pass2_raw_text=pass2_text,
            )

        return DualPassResult(
            answer_text=answer_text,
            citations=tuple(citations_list),
            structured_output=structured,
            citation_coverage=coverage,
            status=STATUS_OK,
            pass1_raw_response=pass1_response,
            pass2_raw_text=pass2_text,
        )


__all__ = [
    "DualPassCitationOrchestrator",
    "DualPassResult",
    "STATUS_OK",
    "STATUS_ABSTAIN",
    "STATUS_NO_GATEWAY",
    "STATUS_PASS1_FAILED",
    "STATUS_PASS2_FAILED",
    "STATUS_JSON_PARSE_FAILED",
    "STATUS_JSON_NOT_REQUESTED",
]
