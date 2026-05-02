"""DecisionPacketAssembler — assembles the final decision packet.

Skeleton implementation. Combines evidence + features + reconciliation
into a structured DecisionPacket with a deterministic verdict heuristic.
Real underwriting decision logic (actuarial scoring, regulatory checks,
risk-tier mapping) will replace the heuristic in feature-complete
implementations.

LLM activation (2026-05-02, plan apps-underwriting-ai-activation-e8a3c5
W1 P1.2): the human-readable ``rationale`` field is enriched via a
Qwen-first cascade. The verdict path remains 100% deterministic (the
legally-binding mechanism in this regulated domain). The LLM produces
ONLY the rationale paragraph; falls through to the pre-existing
template text on any failure (preflight, SDK, gateway, empty response,
length guard, regulator-name guard). Compliance posture floor is
enforced by:
    1. verdict computed BEFORE the LLM call
    2. evidence_refs / feature_summary / gate_violations untouched
       by LLM
    3. rubric YAML at apps_underwriting_ai/policy/rubrics/
       judge_underwriting_decision.yaml documents the invariant
"""

from __future__ import annotations

import logging
from typing import Any

from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    DecisionVerdict,
    EvidenceRegister,
    ReconciliationResult,
    RiskFeatures,
    UnderwritingRequest,
)

_LOGGER = logging.getLogger(__name__)

_REGULATOR_TOKENS = ("FCA", "OCC", "FINRA", "FDIC", "SEC", "CFPB")
"""Hallucination guard — these tokens MUST NOT appear in Qwen rationale
unless they were in the inputs (today's input shape never includes
them, so any occurrence is a fabrication)."""

_MAX_RATIONALE_CHARS = 600
"""Length guard against runaway generation in a regulated domain."""


class DecisionPacketAssembler:
    """Assembles the final decision packet from upstream stage outputs."""

    def assemble(
        self,
        request: UnderwritingRequest | None = None,
        register: EvidenceRegister | None = None,
        features: RiskFeatures | None = None,
        reconciliation: ReconciliationResult | None = None,
    ) -> DecisionPacket:
        """Assemble a DecisionPacket from the four upstream stage outputs.

        Skeleton verdict heuristic (deterministic, never delegated to LLM):
            - INSUFFICIENT_EVIDENCE if register is empty AND no features.
            - REFER if reconciliation has unresolved documents.
            - APPROVE otherwise (deterministic placeholder — real logic TBD).

        After the verdict is decided, ``_enrich_rationale_via_qwen`` is
        called to optionally replace the canned template rationale with
        a richer plain-English explanation. Any failure preserves the
        deterministic rationale byte-for-byte.

        Args:
            request: The originating UnderwritingRequest.
            register: Evidence register from stage 1.
            features: Risk features from stage 3.
            reconciliation: Reconciliation result from stage 2.

        Returns:
            DecisionPacket with verdict, rationale, and audit fields populated.
        """
        request_id = request.request_id if request else ""
        evidence_count = len(register.records) if register else 0
        feature_count = len(features.feature_vector) if features else 0
        unresolved = reconciliation.unresolved_count if reconciliation else 0

        if evidence_count == 0 and feature_count == 0:
            verdict = DecisionVerdict.INSUFFICIENT_EVIDENCE
            deterministic_rationale = (
                "No evidence registered and no risk features derived."
            )
        elif unresolved > 0:
            verdict = DecisionVerdict.REFER
            deterministic_rationale = (
                f"{unresolved} unresolved document reconciliations require "
                "manual review."
            )
        else:
            verdict = DecisionVerdict.APPROVE
            deterministic_rationale = (
                "Skeleton placeholder verdict: evidence registered, features "
                "derived, documents reconciled. Real verdict logic TBD."
            )

        # P1.2 — Qwen-first rationale enrichment. NEVER touches verdict.
        rationale = self._enrich_rationale_via_qwen(
            verdict=verdict,
            evidence_count=evidence_count,
            feature_count=feature_count,
            unresolved=unresolved,
            deterministic_rationale=deterministic_rationale,
        )

        evidence_refs = (
            tuple(r.evidence_id for r in register.records) if register else ()
        )
        feature_summary = dict(features.feature_vector) if features else {}

        return DecisionPacket(
            request_id=request_id,
            verdict=verdict,
            rationale=rationale,
            evidence_refs=evidence_refs,
            feature_summary=feature_summary,
            gate_violations=(),
        )

    @staticmethod
    def _enrich_rationale_via_qwen(
        *,
        verdict: DecisionVerdict,
        evidence_count: int,
        feature_count: int,
        unresolved: int,
        deterministic_rationale: str,
    ) -> str:
        """Try Qwen-local for a richer rationale; fall through on any failure.

        Returns the deterministic rationale unchanged on any cascade
        failure path (preflight / SDK / model_registry / client_init /
        gateway / empty / length-guard / regulator-token-guard).
        """
        # Preflight via L2 health probe.
        try:
            from agentic_core.L2_execution.healers.vllm_health_probe import (  # noqa: PLC0415
                is_qwen_available,
            )
        except ImportError:
            return deterministic_rationale
        if not is_qwen_available():
            _emit_marker(
                accepted=False,
                model_used="qwen_unavailable",
                fallback_reason="preflight_failed",
            )
            return deterministic_rationale

        try:
            import openai  # type: ignore  # noqa: PLC0415
        except ImportError:
            return deterministic_rationale

        try:
            from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
                QWEN_LOCAL_MODEL_ID,
                VLLM_BASE_URL,
            )
        except ImportError:
            return deterministic_rationale

        try:
            client = openai.OpenAI(
                base_url=VLLM_BASE_URL,
                api_key="not-needed",  # vLLM ignores auth in local mode
                timeout=20.0,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI init heterogeneous (ssl/network/env); fail-soft preserves deterministic rationale (regulated-domain compliance floor)
            _LOGGER.info("[apps_underwriting_ai] qwen client init failed: %s", exc)
            _emit_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="client_init_failed",
            )
            return deterministic_rationale

        user_prompt = (
            f"Verdict: {verdict.value}\n"
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
                model=QWEN_LOCAL_MODEL_ID,
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
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI-SDK-over-vLLM raises heterogeneous; fail-soft preserves deterministic rationale (regulated-domain compliance floor)
            _LOGGER.info("[apps_underwriting_ai] qwen call failed: %s", exc)
            _emit_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="gateway_exception",
            )
            return deterministic_rationale

        text = (resp.choices[0].message.content or "") if resp.choices else ""
        text = text.strip()
        if not text:
            _emit_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="empty_response",
            )
            return deterministic_rationale

        # Length guard.
        if len(text) > _MAX_RATIONALE_CHARS:
            _emit_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="length_guard_exceeded",
            )
            return deterministic_rationale

        # Regulator-name hallucination guard.
        upper = text.upper()
        for token in _REGULATOR_TOKENS:
            if token in upper:
                _emit_marker(
                    accepted=False,
                    model_used=QWEN_LOCAL_MODEL_ID,
                    fallback_reason="regulator_token_guard",
                )
                return deterministic_rationale

        _emit_marker(
            accepted=True,
            model_used=QWEN_LOCAL_MODEL_ID,
            fallback_reason="none",
        )
        return text


def _emit_marker(
    *,
    accepted: bool,
    model_used: str,
    fallback_reason: str,
) -> None:
    """Best-effort ``JUDGE_DECISION`` marker. Never raises."""
    try:
        from tools.capture.append_marker import append_marker  # noqa: PLC0415
    except ImportError:
        return
    payload = (
        "JUDGE_DECISION: type=judge_decision, "
        "app_name=apps_underwriting_ai.decision_rationale, "
        "rubric_id=underwriting_decision_rationale_v1, "
        "rubric_hash=inline, "
        f"accepted={accepted}, "
        "composite=0.0, "
        f"model_used={model_used}, "
        f"fallback_reason={fallback_reason}, "
        "first_failed_gate=none, "
        "latency_ms=0.0"
    )
    try:
        append_marker(payload, session_hint="apps_underwriting_ai.decision")
    except (OSError, PermissionError):
        pass
