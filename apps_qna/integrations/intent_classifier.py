"""Small-LLM intent-classifier fallback (W3.2).

Wave 3 phase 3.2 of ``apps-qna-dag-enhancements-e4c7b2``. The existing
route-selection pipeline is:

    bandit (Thompson sampled) -> embedding/keyword ranking -> static
    _FALLBACK_ROUTE_ORDER

If both the bandit (cold-start or absent) AND the embedding/keyword
ranking abstain (signal empty, below threshold, or registry empty), the
pipeline falls through to a hand-curated default order. That is a
perfectly reasonable prior — but on questions where the interviewer's
phrasing is outside the route descriptors (e.g. domain-specific jargon,
novel roles), a small LLM can often classify intent correctly on a
budget of a few hundred tokens.

This module is that optional path. It is:

* **Env-gated**: off unless ``APPS_QNA_INTENT_LLM`` is set to a truthy
  value. No network calls are made in test environments by default.
* **Fail-soft**: any failure (missing key, import error, network
  timeout, ambiguous LLM answer) returns ``None`` so callers fall back
  to the static order without branching.
* **Constitutional §29 compliant**: emits the paired
  ``ROUTER_DECISION: layer=L0 router=apps_qna_intent_llm ...`` marker +
  ``apps_qna_pack_lifecycle(event_kind=route_select_llm_fallback)``
  ledger row on every invocation (including abstains — so the audit
  surface captures attempted fallbacks).

No provider-specific dependency is imported at module load time —
provider selection is deferred to invocation, so the module remains
importable without ``anthropic`` / ``openai`` installed.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import TYPE_CHECKING

from agentic_core.config.model_catalog import (
    ANTHROPIC_HAIKU_DATED_MODEL_ID,
    OPENAI_SMALL_CLASSIFIER_MODEL_ID,
)
from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

if TYPE_CHECKING:
    from apps_qna.config.route_registry import RouteRegistry

_log = logging.getLogger(__name__)

_ENV_ENABLE_LLM: str = "APPS_QNA_INTENT_LLM"
_ENV_PROVIDER: str = "APPS_QNA_INTENT_LLM_PROVIDER"  # haiku|gpt-mini|custom
_ROUTER_LAYER: str = "L0"
_ROUTER_NAME: str = "apps_qna_intent_llm"


def _llm_enabled() -> bool:
    """True iff ``APPS_QNA_INTENT_LLM`` env flag is on."""
    return os.environ.get(_ENV_ENABLE_LLM, "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _emit_marker(
    *,
    decision_id: str,
    selected: str,
    reason: str,
) -> None:
    """Constitutional §29 paired marker."""
    print(
        f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
        f"decision_id={decision_id} selected={selected} reason={reason}"
    )


def _build_prompt(question: str, registry: "RouteRegistry") -> str:
    """Small classification prompt — one line per admissible route id."""
    lines = [
        "You are a deterministic classifier. Map the QUESTION onto exactly",
        "ONE of the route_ids below. Respond with the bare route_id only —",
        "no punctuation, no prose, no trailing whitespace.",
        "",
        "ROUTES:",
    ]
    for route in registry.routes:
        triggers = ", ".join(route.triggers[:4]) if route.triggers else "-"
        lines.append(f"- {route.id}: {route.name} (triggers: {triggers})")
    lines.append("")
    lines.append(f"QUESTION: {question}")
    lines.append("ROUTE_ID:")
    return "\n".join(lines)


def _invoke_provider(prompt: str) -> str | None:
    """Call the configured LLM provider. Returns raw route_id or None.

    Default provider is ``haiku`` (Anthropic Claude Haiku 4.5 class). All
    provider imports are deferred — a missing dependency simply returns
    None and the caller abstains.
    """
    provider = os.environ.get(_ENV_PROVIDER, "haiku").strip().lower()
    try:
        if provider == "haiku":
            return _invoke_anthropic(prompt)
        if provider in {"gpt-mini", OPENAI_SMALL_CLASSIFIER_MODEL_ID, "openai"}:
            return _invoke_openai(prompt)
    except (ImportError, RuntimeError, ValueError, OSError) as exc:
        _log.debug("intent LLM provider %s failed: %r", provider, exc)
        return None
    _log.debug("intent LLM provider unknown: %s", provider)
    return None


def _invoke_anthropic(prompt: str) -> str | None:
    """Best-effort Anthropic call. Returns None on any failure."""
    try:
        import anthropic  # noqa: PLC0415
    except ImportError:
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        # Small, deterministic config — this is a classifier, not a chat.
        resp = client.messages.create(
            model=os.environ.get(
                "APPS_QNA_INTENT_LLM_MODEL", ANTHROPIC_HAIKU_DATED_MODEL_ID
            ),
            max_tokens=16,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        # Extract text from response.
        content = getattr(resp, "content", []) or []
        for part in content:
            text = getattr(part, "text", "") or ""
            if text.strip():
                return text.strip().splitlines()[0].strip()
    except (AttributeError, RuntimeError, ValueError, OSError) as exc:
        _log.debug("anthropic call failed: %r", exc)
    return None


def _invoke_openai(prompt: str) -> str | None:
    """Best-effort OpenAI call. Returns None on any failure."""
    try:
        import openai  # noqa: PLC0415
    except ImportError:
        return None
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.environ.get(
                "APPS_QNA_INTENT_LLM_MODEL", OPENAI_SMALL_CLASSIFIER_MODEL_ID
            ),
            max_tokens=16,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        choices = getattr(resp, "choices", []) or []
        if choices:
            msg = getattr(choices[0], "message", None)
            text = getattr(msg, "content", "") if msg else ""
            if text and text.strip():
                return text.strip().splitlines()[0].strip()
    except (AttributeError, RuntimeError, ValueError, OSError) as exc:
        _log.debug("openai call failed: %r", exc)
    return None


def classify_intent(
    *,
    question: str,
    registry: "RouteRegistry",
) -> str | None:
    """Return a route_id from the registry, or ``None`` to abstain.

    Abstains when:
      - The env flag ``APPS_QNA_INTENT_LLM`` is off.
      - No configured provider can be reached (missing SDK, missing key,
        network failure).
      - The LLM response is empty or does not match any registry.route_id.

    Every call emits a §29 paired marker + ``apps_qna_pack_lifecycle``
    ``route_select_llm_fallback`` ledger row — even abstains, so the
    audit stream sees the attempted fallback.
    """
    decision_id = uuid.uuid4().hex
    if not _llm_enabled():
        _emit_marker(decision_id=decision_id, selected="", reason="env_gate_off")
        emit_pack_lifecycle_event(
            event_kind="route_select_llm_fallback",
            prediction={
                "question_length": len(question),
                "selected_route": "",
                "reason": "env_gate_off",
            },
            metadata={"decision_id": decision_id},
        )
        return None
    if not question or not question.strip():
        _emit_marker(
            decision_id=decision_id, selected="", reason="empty_question"
        )
        emit_pack_lifecycle_event(
            event_kind="route_select_llm_fallback",
            prediction={
                "question_length": 0,
                "selected_route": "",
                "reason": "empty_question",
            },
            metadata={"decision_id": decision_id},
        )
        return None
    admissible = {r.id for r in registry.routes}
    if not admissible:
        _emit_marker(
            decision_id=decision_id, selected="", reason="empty_registry"
        )
        emit_pack_lifecycle_event(
            event_kind="route_select_llm_fallback",
            prediction={
                "question_length": len(question),
                "selected_route": "",
                "reason": "empty_registry",
            },
            metadata={"decision_id": decision_id},
        )
        return None

    prompt = _build_prompt(question, registry)
    raw = _invoke_provider(prompt)
    if not raw:
        _emit_marker(
            decision_id=decision_id, selected="", reason="provider_abstain"
        )
        emit_pack_lifecycle_event(
            event_kind="route_select_llm_fallback",
            prediction={
                "question_length": len(question),
                "selected_route": "",
                "reason": "provider_abstain",
            },
            metadata={"decision_id": decision_id},
        )
        return None

    # Normalize — take the first token of the response and strip punctuation.
    candidate = raw.strip().strip(".,;:`'\"").lower().split()[0] if raw else ""
    if candidate not in admissible:
        _emit_marker(
            decision_id=decision_id,
            selected="",
            reason="unknown_route_id",
        )
        emit_pack_lifecycle_event(
            event_kind="route_select_llm_fallback",
            prediction={
                "question_length": len(question),
                "selected_route": "",
                "llm_raw": raw[:64],
                "reason": "unknown_route_id",
            },
            metadata={"decision_id": decision_id},
        )
        return None

    _emit_marker(
        decision_id=decision_id, selected=candidate, reason="llm_classified"
    )
    emit_pack_lifecycle_event(
        event_kind="route_select_llm_fallback",
        prediction={
            "question_length": len(question),
            "selected_route": candidate,
            "reason": "llm_classified",
        },
        metadata={"decision_id": decision_id},
    )
    return candidate


__all__ = ["classify_intent"]
