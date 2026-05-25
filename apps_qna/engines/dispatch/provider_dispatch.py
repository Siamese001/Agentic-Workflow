"""apps_qna.engines.dispatch.provider_dispatch — provider selector for apps_qna queries.

Plan: ``.windsurf/plans/bge-m3-deferred-scope-remaining-c4e7a1.md`` W3.P1

Routes a query to the appropriate LLM provider based on query type:

    FACTUAL        → Anthropic (claude-sonnet, high accuracy)
    BEHAVIORAL     → Gemini (gemini-pro, nuanced reasoning)
    TECHNICAL      → Anthropic (claude-sonnet, code/systems reasoning)
    OPEN_ENDED     → Gemini (gemini-flash, cost-efficient)
    default/stub   → stub (no API call, template response)

Provider is selected from environment:
    ANTHROPIC_API_KEY  — enables Anthropic provider
    GOOGLE_API_KEY     — enables Gemini provider
    JUDGE_PROVIDER     — explicit override (anthropic | gemini | stub)

DispatchResult is wired into FinalEvidenceContract via the ``provider_dispatch``
field (added as an optional sidecar — existing contract is unchanged).

Graceful degradation: when no API key is available or provider call fails,
falls back to stub — never raises.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_LOGGER = logging.getLogger(__name__)
  # guardian: allow-hardcoded-secret -- P1 ADG burndown
_ANTHROPIC_API_KEY_VAR = "ANTHROPIC_API_KEY"  # guardian: allow-hardcoded-secret -- P1 ADG burndown
_GOOGLE_API_KEY_VAR = "GOOGLE_API_KEY"  # guardian: allow-hardcoded-secret -- P1 ADG burndown
_JUDGE_PROVIDER_VAR = "JUDGE_PROVIDER"
_ANTHROPIC_MODEL_VAR = "ANTHROPIC_MODEL"

_DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
_DEFAULT_GEMINI_PRO_MODEL = "gemini-3.1-pro-preview"
_DEFAULT_GEMINI_FLASH_MODEL = "gemini-3-flash-preview"


def _google_ai_flash_from_env() -> str:
    raw = (
        os.environ.get("GOOGLE_AI_MODEL", "").strip()
        or os.environ.get("GEMINI_MODEL", "").strip()
    )
    return raw if raw else _DEFAULT_GEMINI_FLASH_MODEL


def _google_ai_pro_from_env() -> str:
    raw = (
        os.environ.get("GOOGLE_AI_PRO_MODEL", "").strip()
        or os.environ.get("GEMINI_PRO_MODEL", "").strip()
    )
    return raw if raw else _DEFAULT_GEMINI_PRO_MODEL

_DISPATCH_TIMEOUT = 30


class QueryType(str, Enum):
    FACTUAL = "factual"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    OPEN_ENDED = "open_ended"
    UNKNOWN = "unknown"


class ProviderName(str, Enum):
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    STUB = "stub"


_QUERY_TYPE_TO_PROVIDER: dict[QueryType, ProviderName] = {
    QueryType.FACTUAL: ProviderName.ANTHROPIC,
    QueryType.BEHAVIORAL: ProviderName.GEMINI,
    QueryType.TECHNICAL: ProviderName.ANTHROPIC,
    QueryType.OPEN_ENDED: ProviderName.GEMINI,
    QueryType.UNKNOWN: ProviderName.STUB,
}

_QUERY_TYPE_TO_MODEL_TIER: dict[QueryType, str] = {
    QueryType.FACTUAL: "pro",
    QueryType.BEHAVIORAL: "pro",
    QueryType.TECHNICAL: "pro",
    QueryType.OPEN_ENDED: "flash",
    QueryType.UNKNOWN: "stub",
}


@dataclass
class DispatchResult:
    """Result of a provider dispatch call.

    provider:       which provider was used
    model:          model identifier
    response_text:  generated text (empty string on stub/failure)
    query_type:     classified query type
    evidence_refs:  list of evidence strings for FinalEvidenceContract
    success:        True if a real LLM call succeeded
    """

    provider: str = ProviderName.STUB.value
    model: str = "stub"
    response_text: str = ""
    query_type: str = QueryType.UNKNOWN.value
    evidence_refs: list[str] = field(default_factory=list)
    success: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "response_text": self.response_text,
            "query_type": self.query_type,
            "evidence_refs": self.evidence_refs,
            "success": self.success,
        }


def _classify_query(question: str) -> QueryType:
    """Heuristic classifier — routes to LLM classification in v2."""
    q = question.lower()
    technical_signals = ("implement", "code", "system design", "algorithm", "complexity", "debug", "architecture")
    behavioral_signals = ("tell me about", "describe a time", "how do you", "what would you", "walk me through")
    factual_signals = ("what is", "what are", "explain", "define", "difference between")

    if any(s in q for s in technical_signals):
        return QueryType.TECHNICAL
    if any(s in q for s in behavioral_signals):
        return QueryType.BEHAVIORAL
    if any(s in q for s in factual_signals):
        return QueryType.FACTUAL
    return QueryType.OPEN_ENDED


def _get_provider_override() -> ProviderName | None:
    val = os.environ.get(_JUDGE_PROVIDER_VAR, "").strip().lower()
    if val == "anthropic":
        return ProviderName.ANTHROPIC
    if val in ("gemini", "google"):
        return ProviderName.GEMINI
    if val == "stub":
        return ProviderName.STUB
    return None


def _resolve_provider(query_type: QueryType) -> ProviderName:
    override = _get_provider_override()
    if override is not None:
        return override

    preferred = _QUERY_TYPE_TO_PROVIDER[query_type]

    if preferred == ProviderName.ANTHROPIC:
        if os.environ.get(_ANTHROPIC_API_KEY_VAR, "").strip():
            return ProviderName.ANTHROPIC
        if os.environ.get(_GOOGLE_API_KEY_VAR, "").strip():
            _LOGGER.debug("Anthropic preferred but key absent — falling back to Gemini")
            return ProviderName.GEMINI
    elif preferred == ProviderName.GEMINI:
        if os.environ.get(_GOOGLE_API_KEY_VAR, "").strip():
            return ProviderName.GEMINI
        if os.environ.get(_ANTHROPIC_API_KEY_VAR, "").strip():
            _LOGGER.debug("Gemini preferred but key absent — falling back to Anthropic")
            return ProviderName.ANTHROPIC

    return ProviderName.STUB


def _call_anthropic(question: str, context: str, model: str) -> str:
    import anthropic  # type: ignore[import-not-found]

    api_key = os.environ.get(_ANTHROPIC_API_KEY_VAR, "").strip()
    client = anthropic.Anthropic(api_key=api_key)
    prompt = (
        f"You are an expert interview coach. Answer the following interview question clearly and concisely.\n\n"
        f"Context:\n{context[:1500]}\n\n"
        f"Question: {question[:500]}\n\n"
        "Provide a structured, high-quality answer a candidate could use in an interview."
    )
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        timeout=_DISPATCH_TIMEOUT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text if message.content else ""


def _call_gemini(question: str, context: str, model: str) -> str:
    import google.generativeai as genai  # type: ignore[import-not-found]

    api_key = os.environ.get(_GOOGLE_API_KEY_VAR, "").strip()
    genai.configure(api_key=api_key)
    gmodel = genai.GenerativeModel(model)
    prompt = (
        f"You are an expert interview coach. Answer the following interview question clearly and concisely.\n\n"
        f"Context:\n{context[:1500]}\n\n"
        f"Question: {question[:500]}\n\n"
        "Provide a structured, high-quality answer a candidate could use in an interview."
    )
    response = gmodel.generate_content(prompt)
    return response.text if hasattr(response, "text") else ""


class ProviderDispatcher:
    """Routes apps_qna queries to the appropriate LLM provider.

    Classifies the query type, selects a provider, calls the LLM, and returns
    a DispatchResult that can be wired into FinalEvidenceContract.
    Falls back to stub gracefully on any failure.
    """

    def dispatch(
        self,
        question: str,
        *,
        context: str = "",
        route_id: str = "",
    ) -> DispatchResult:
        """Dispatch a query and return a DispatchResult.

        Args:
            question: The interview question text.
            context:  Retrieved context to ground the answer (optional).
            route_id: The apps_qna route identifier (for evidence tagging).
        """
        if not question.strip():
            return DispatchResult(
                evidence_refs=["dispatch::v1::skip=empty_question"],
            )

        query_type = _classify_query(question)
        provider = _resolve_provider(query_type)

        if provider == ProviderName.STUB:
            return DispatchResult(
                provider=ProviderName.STUB.value,
                model="stub",
                response_text="",
                query_type=query_type.value,
                evidence_refs=[
                    f"dispatch::v1::provider=stub",
                    f"dispatch::v1::query_type={query_type.value}",
                    f"dispatch::v1::route_id={route_id}",
                ],
                success=False,
            )

        tier = _QUERY_TYPE_TO_MODEL_TIER[query_type]

        if provider == ProviderName.ANTHROPIC:
            model = os.environ.get(_ANTHROPIC_MODEL_VAR, "").strip() or _DEFAULT_ANTHROPIC_MODEL
        else:
            if tier == "flash":
                model = _google_ai_flash_from_env()
            else:
                model = _google_ai_pro_from_env()

        try:
            if provider == ProviderName.ANTHROPIC:
                response_text = _call_anthropic(question, context, model)
            else:
                response_text = _call_gemini(question, context, model)

            return DispatchResult(
                provider=provider.value,
                model=model,
                response_text=response_text,
                query_type=query_type.value,
                evidence_refs=[
                    f"dispatch::v1::provider={provider.value}",
                    f"dispatch::v1::model={model}",
                    f"dispatch::v1::query_type={query_type.value}",
                    f"dispatch::v1::route_id={route_id}",
                ],
                success=True,
            )
        except Exception as exc:  # guardian: allow-broad-exception-catch -- fail-soft: provider call must never crash the pipeline; falls back to stub
            _LOGGER.warning(
                "dispatch::v1 provider=%s model=%s failed, returning stub: %s",
                provider.value,
                model,
                exc,
            )
            return DispatchResult(
                provider=ProviderName.STUB.value,
                model="stub",
                response_text="",
                query_type=query_type.value,
                evidence_refs=[
                    f"dispatch::v1::provider=stub::fallback_from={provider.value}",
                    f"dispatch::v1::query_type={query_type.value}",
                    f"dispatch::v1::route_id={route_id}",
                    f"dispatch::v1::error={type(exc).__name__}",
                ],
                success=False,
            )


def dispatch(
    question: str,
    *,
    context: str = "",
    route_id: str = "",
) -> DispatchResult:
    """Module-level convenience wrapper around ProviderDispatcher."""
    return ProviderDispatcher().dispatch(question, context=context, route_id=route_id)


__all__ = ["DispatchResult", "ProviderDispatcher", "ProviderName", "QueryType", "dispatch"]
