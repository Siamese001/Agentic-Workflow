"""Frontier-API second-judge rationale generator (W3.1).

Companion to the Qwen-first rationale enrichment in
``DecisionPacketAssembler._enrich_rationale_via_qwen``. Purpose is to
generate a SECOND rationale paragraph from a frontier-class model for
cross-check / agreement tracking — NOT to influence the verdict.

Compliance-posture floor (inherited from plan
``apps-underwriting-ai-activation-e8a3c5``): the verdict is fixed
BEFORE this judge runs; the frontier paragraph is telemetry-only and
NEVER mutates ``DecisionPacket.rationale``. The caller uses the
agreement tracker (see ``rationale_agreement_tracker``) to accumulate
rolling samples and raise a watchdog when Wilson-CI lower bound on
agreement drops below threshold.

Invocation surface is an OpenAI-compatible HTTP endpoint (works with
vLLM, Anthropic-proxy, Gemini-proxy, OpenAI directly). Environment:

  APPS_UW_FRONTIER_PAIRING_ENABLED=1   # arm the pairing path
  FRONTIER_API_BASE_URL=https://...    # OpenAI-compatible endpoint
  FRONTIER_API_KEY=...                 # bearer (use "not-needed" for
                                       # open proxies)
  APPS_UW_FRONTIER_JUDGE_MODEL=...     # e.g. "gemini-1.5-pro",
                                       # "claude-3-5-sonnet-20241022"

Every failure path falls through to ``None`` (no frontier rationale
recorded) — the Qwen-first path still serves ``DecisionPacket.rationale``
unchanged.
"""
from __future__ import annotations

import logging
import os

_LOGGER = logging.getLogger(__name__)

_REGULATOR_TOKENS = ("FCA", "OCC", "FINRA", "FDIC", "SEC", "CFPB")
"""Same hallucination-guard set as the Qwen path; frontier must not
fabricate regulator names either."""

_MAX_RATIONALE_CHARS = 600
"""Same length guard as the Qwen path."""


def _pairing_armed() -> bool:
    """Return True iff the frontier-pairing feature flag is set.

    Pairing is OFF by default so dev / contract suite / CI runs the
    deterministic + Qwen-only path. Production callers opt in via
    ``APPS_UW_FRONTIER_PAIRING_ENABLED=1``.
    """
    return os.environ.get("APPS_UW_FRONTIER_PAIRING_ENABLED") == "1"


def generate_frontier_rationale(
    *,
    verdict_value: str,
    evidence_count: int,
    feature_count: int,
    unresolved: int,
) -> tuple[str | None, str, str]:
    """Ask a frontier-class model for a second rationale paragraph.

    Args:
        verdict_value: Already-decided ``DecisionVerdict.value`` (string).
        evidence_count: From the evidence register.
        feature_count: From the derived risk features.
        unresolved: From the reconciliation result.

    Returns:
        ``(rationale_text_or_None, model_used, fallback_reason)``.

        ``rationale_text_or_None`` is ``None`` when pairing is disabled
        OR any failure path was taken (SDK missing / env missing /
        client init / API call / empty / length / regulator guard).
        Callers treat ``None`` as "no sample this turn" — the Qwen path
        remains authoritative for ``DecisionPacket.rationale``.

        ``model_used`` is the frontier model id string (empty if
        pairing never armed). ``fallback_reason`` is "accepted" on
        success, or one of the bypass reasons otherwise.
    """
    if not _pairing_armed():
        return None, "", "pairing_disabled"

    model = os.environ.get("APPS_UW_FRONTIER_JUDGE_MODEL", "").strip()
    base_url = os.environ.get("FRONTIER_API_BASE_URL", "").strip()
    api_key = os.environ.get("FRONTIER_API_KEY", "").strip()

    if not model or not base_url:
        return None, model, "env_missing"

    try:
        import openai  # type: ignore  # noqa: PLC0415
    except ImportError:
        return None, model, "sdk_missing"

    try:
        client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key or "not-needed",
            timeout=30.0,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- frontier client init heterogeneous (ssl/network/env); fail-soft returns None so Qwen-first path serves the rationale unchanged (regulated-domain compliance floor)
        _LOGGER.info(
            "[apps_underwriting_ai.frontier_judge] client init failed: %s", exc
        )
        return None, model, "client_init_failed"

    user_prompt = (
        f"Verdict: {verdict_value}\n"
        f"Evidence records: {evidence_count}\n"
        f"Risk features derived: {feature_count}\n"
        f"Unresolved document reconciliations: {unresolved}\n\n"
        "Write a 2-4 sentence plain-English rationale that explains "
        "this verdict to the underwriting analyst. Reference only "
        "the counts above; do NOT cite regulators, do NOT invent "
        "feature values, do NOT quote policy clauses."
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior underwriting analyst writing a "
                        "2-4 sentence plain-English explanation of an "
                        "already-decided underwriting verdict. The verdict "
                        "is fixed; you are NOT making the decision. "
                        "Reference only the counts provided. Do NOT cite "
                        "regulators, do NOT quote policy clauses, do NOT "
                        "invent feature values."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=250,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- frontier SDK raises heterogeneous (timeout/auth/5xx/rate-limit); fail-soft returns None so Qwen-first path serves the rationale unchanged (regulated-domain compliance floor)
        _LOGGER.info(
            "[apps_underwriting_ai.frontier_judge] call failed: %s", exc
        )
        return None, model, "gateway_exception"

    try:
        text = (resp.choices[0].message.content or "") if resp.choices else ""
    except (AttributeError, IndexError):
        return None, model, "empty_response"

    text = text.strip()
    if not text:
        return None, model, "empty_response"

    if len(text) > _MAX_RATIONALE_CHARS:
        return None, model, "length_guard_exceeded"

    upper = text.upper()
    for token in _REGULATOR_TOKENS:
        if token in upper:
            return None, model, "regulator_token_guard"

    return text, model, "accepted"


__all__ = ["generate_frontier_rationale"]
