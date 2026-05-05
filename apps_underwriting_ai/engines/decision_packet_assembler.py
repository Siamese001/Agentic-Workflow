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
import os
from typing import Any

from apps_underwriting_ai.engines.risk_scorer import DeterministicRiskScorer
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
    """Assembles the final decision packet from upstream stage outputs.

    Delegates verdict computation to :class:`DeterministicRiskScorer` so
    the scoring rubric, thresholds, and per-component breakdown live in
    one inspectable place. The breakdown is surfaced in
    ``feature_summary`` under stable keys so downstream consumers can
    audit the decision without re-running the pipeline.
    """

    def __init__(self, scorer: DeterministicRiskScorer | None = None) -> None:
        self._scorer = scorer or DeterministicRiskScorer()

    def assemble(
        self,
        request: UnderwritingRequest | None = None,
        register: EvidenceRegister | None = None,
        features: RiskFeatures | None = None,
        reconciliation: ReconciliationResult | None = None,
    ) -> DecisionPacket:
        """Assemble a DecisionPacket from the four upstream stage outputs.

        Verdict logic delegates to
        :class:`DeterministicRiskScorer`. The breakdown is exposed via
        ``feature_summary`` keys with the prefix ``risk_*`` so audit
        consumers can read the score, ceilings, and per-component
        contributions without re-running the pipeline.

        Args:
            request: The originating UnderwritingRequest.
            register: Evidence register from stage 1.
            features: Risk features from stage 3.
            reconciliation: Reconciliation result from stage 2.

        Returns:
            DecisionPacket with verdict, rationale, and audit fields populated.
        """
        request_id = request.request_id if request else ""

        if request is None:
            # Defensive: callers should always provide a request, but the
            # legacy tests pass None. Preserve INSUFFICIENT_EVIDENCE behavior.
            verdict = DecisionVerdict.INSUFFICIENT_EVIDENCE
            rationale = (
                "No UnderwritingRequest provided; cannot score. "
                "[apps_underwriting_ai.decision_packet_assembler/no-request]"
            )
            evidence_refs: tuple[str, ...] = (
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

        breakdown = self._scorer.score(
            request=request,
            register=register,
            features=features,
            reconciliation=reconciliation,
        )

        evidence_refs = (
            tuple(r.evidence_id for r in register.records) if register else ()
        )
        feature_summary: dict[str, float] = (
            dict(features.feature_vector) if features else {}
        )
        # Surface scorer breakdown under stable risk_* keys for audit.
        feature_summary.update(
            {
                "risk_score": breakdown.risk_score,
                "risk_evidence_completeness": breakdown.evidence_completeness,
                "risk_reconciliation_completeness": (
                    breakdown.reconciliation_completeness
                ),
                "risk_document_density": breakdown.document_density,
                "risk_coverage_score": breakdown.coverage_score,
                "risk_product_tier": breakdown.product_risk_tier,
            }
        )

        # Optional Qwen enrichment of the rationale paragraph. Verdict is
        # already fixed (legally-binding in the regulated domain per the
        # module docstring); enrichment ONLY edits the human-readable
        # paragraph. Falls through to the deterministic rationale on any
        # failure (preflight / SDK / gateway / empty / length / regulator-token).
        evidence_count = len(register.records) if register else 0
        feature_count = len(features.feature_vector) if features else 0
        unresolved = reconciliation.unresolved_count if reconciliation else 0

        # W4.1 — LLM Firewall gate: PA compiler MUST run before any Qwen call.
        # The firewall binds verdict_hash + reason_codes_hash into the artifact.
        # On PromptAssemblyError, firewall returns deterministic_fallback_used=True.
        firewall_result = self._run_firewall_gate(
            verdict=breakdown.verdict,
            reason_codes=list(breakdown.reason_code_bundle)
            if hasattr(breakdown, "reason_code_bundle")
            else [],
            c0_bundle=feature_summary,
            deterministic_rationale=breakdown.rationale,
            request_id=request_id,
        )
        feature_summary["firewall_passed"] = firewall_result.firewall_passed
        feature_summary["deterministic_rationale_fallback_used"] = (
            firewall_result.deterministic_fallback_used
        )

        # When the firewall has passed and no LLM callable was supplied, the
        # existing Qwen path handles enrichment (preserving prior behavior).
        if firewall_result.firewall_passed and firewall_result.failure_reason in (
            "no_llm_callable", "none"
        ):
            rationale = self._enrich_rationale_via_qwen(
                verdict=breakdown.verdict,
                evidence_count=evidence_count,
                feature_count=feature_count,
                unresolved=unresolved,
                deterministic_rationale=breakdown.rationale,
            )
        else:
            rationale = firewall_result.rationale

        return DecisionPacket(
            request_id=request_id,
            verdict=breakdown.verdict,
            rationale=rationale,
            evidence_refs=evidence_refs,
            feature_summary=feature_summary,
            gate_violations=(),
        )

    def run_pa_firewall(
        self,
        *,
        verdict: str,
        reason_codes: list[str],
        c0_bundle: dict[str, Any],
        deterministic_rationale: str,
        request_id: str = "",
        run_id: str = "",
        trace_id: str = "",
        template_id: str = "decision_rationale_enrichment_v1",
        llm_callable: Any = None,
        slot_overrides: dict[str, str] | None = None,
    ) -> Any:
        """Public entry point: run the PA-compiler LLM firewall gate.

        This is the canonical W4 integration surface. Callers that own
        a `verdict` + `reason_codes` pair from DeterministicRiskScorer
        invoke this before any LLM call.

        Args:
            verdict: Locked verdict from DeterministicRiskScorer.
            reason_codes: Locked reason codes from DeterministicRiskScorer.
            c0_bundle: FinalEvidenceContract dict from C0 adapter.
            deterministic_rationale: Fallback if firewall blocks.
            request_id: Request ID for tracing.
            run_id: Run ID.
            trace_id: Trace ID.
            template_id: PA compiler template (default: rationale enrichment).
            llm_callable: Optional LLM callable(artifact) -> str.
            slot_overrides: Optional slot content overrides.

        Returns:
            FirewallResult from UnderwritingLLMFirewall.gate().
        """
        return self._run_firewall_gate(
            verdict=verdict,
            reason_codes=reason_codes,
            c0_bundle=c0_bundle,
            deterministic_rationale=deterministic_rationale,
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            template_id=template_id,
            llm_callable=llm_callable,
            slot_overrides=slot_overrides,
        )

    @staticmethod
    def _run_firewall_gate(
        *,
        verdict: Any,
        reason_codes: list[str],
        c0_bundle: dict[str, Any],
        deterministic_rationale: str,
        request_id: str = "",
        run_id: str = "",
        trace_id: str = "",
        template_id: str = "decision_rationale_enrichment_v1",
        llm_callable: Any = None,
        slot_overrides: dict[str, str] | None = None,
    ) -> Any:
        """Instantiate UnderwritingLLMFirewall and run the gate sequence.

        Returns a FirewallResult. Never raises — any internal failure
        produces a deterministic_fallback_used=True result.
        """
        try:
            from apps_underwriting_ai.integrations.underwriting_llm_firewall import (  # noqa: PLC0415
                UnderwritingLLMFirewall,
            )

            verdict_str = verdict.value if hasattr(verdict, "value") else str(verdict)
            return UnderwritingLLMFirewall().gate(
                verdict=verdict_str,
                reason_codes=reason_codes,
                c0_bundle=c0_bundle,
                deterministic_rationale=deterministic_rationale,
                request_id=request_id,
                run_id=run_id,
                trace_id=trace_id,
                template_id=template_id,
                llm_callable=llm_callable,
                slot_overrides=slot_overrides,
            )
        except Exception as exc:  # guardian: allow-broad-except -- firewall import/init failure must fall through to deterministic rationale (regulated-domain compliance floor)
            _LOGGER.info("[apps_underwriting_ai] firewall gate error: %s", exc)
            # Return a minimal duck-typed object so callers work without import.
            from types import SimpleNamespace  # noqa: PLC0415
            return SimpleNamespace(
                rationale=deterministic_rationale,
                deterministic_fallback_used=True,
                firewall_passed=False,
                failure_reason="firewall_import_error",
                pa_error=True,
                immutability_violation=False,
                artifact_id="",
                artifact_hash="",
                verdict_hash="",
                reason_codes_hash="",
                audit_refs=[],
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

        Test bypass: ``APPS_UW_RATIONALE_LLM_DISABLED=1`` skips the
        cascade entirely. Used by contract tests that assert the
        deterministic rationale text — those tests verify the
        skeleton-stage floor that survives any Qwen failure.
        """
        if os.environ.get("APPS_UW_RATIONALE_LLM_DISABLED") == "1":
            return deterministic_rationale

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
        # W3.3 (plan apps-underwriting-ai-activation-e8a3c5): best-effort
        # frontier-pairing telemetry. NEVER mutates the accepted Qwen
        # rationale. Runs only when APPS_UW_FRONTIER_PAIRING_ENABLED=1
        # and the frontier-provider env is configured. All failures are
        # silent (regulated-domain compliance floor: the Qwen-first
        # rationale served to the DecisionPacket is final at this point).
        _pair_with_frontier_best_effort(
            accepted_qwen_text=text,
            verdict=verdict,
            evidence_count=evidence_count,
            feature_count=feature_count,
            unresolved=unresolved,
        )
        return text


def _emit_marker(
    *,
    accepted: bool,
    model_used: str,
    fallback_reason: str,
    request_id: str = "",
    rationale_chars: int = 0,
) -> None:
    """Best-effort ``JUDGE_DECISION`` marker + telemetry. Never raises.

    Wired by plan ``apps-underwriting-feature-complete-aa79a7`` W5 P5.1
    to use the live rubric id + version from
    :class:`apps_underwriting_ai.services.RubricWiringService` instead of
    hardcoded constants, and to additionally surface the judge outcome
    via :class:`apps_underwriting_ai.services.LLMJudgeTelemetryService`.
    Both enhancements are fail-soft — any failure falls through to the
    pre-existing marker behavior (regulated-domain compliance floor).
    """
    rubric_id, rubric_version = _load_rubric_identity_safe()
    payload = (
        "JUDGE_DECISION: type=judge_decision, "
        "app_name=apps_underwriting_ai.decision_rationale, "
        f"rubric_id={rubric_id}, "
        f"rubric_version={rubric_version}, "
        "rubric_hash=inline, "
        f"accepted={accepted}, "
        "composite=0.0, "
        f"model_used={model_used}, "
        f"fallback_reason={fallback_reason}, "
        "first_failed_gate=none, "
        "latency_ms=0.0"
    )
    try:
        from tools.capture.append_marker import append_marker  # noqa: PLC0415

        try:
            append_marker(payload, session_hint="apps_underwriting_ai.decision")
        except (OSError, PermissionError):
            pass
    except ImportError:
        pass

    # Additionally emit via ObservabilityAdapter for runtime telemetry
    # consumers. Fail-soft — never raises.
    try:
        from apps_underwriting_ai.services import (  # noqa: PLC0415
            JudgeTelemetryEvent,
            LLMJudgeTelemetryService,
        )

        LLMJudgeTelemetryService().emit(
            JudgeTelemetryEvent(
                request_id=request_id,
                rubric_id=rubric_id,
                rubric_version=rubric_version,
                passed=accepted,
                model_used=model_used,
                fallback_reason=fallback_reason,
                rationale_chars=rationale_chars,
            )
        )
    except Exception as exc:  # guardian: allow-broad-exception -- telemetry is fail-soft; any failure must fall through to preserve the deterministic rationale pipeline (regulated-domain compliance floor)
        _LOGGER.info(
            "[apps_underwriting_ai] judge_result telemetry emit skipped: %s", exc
        )


def _load_rubric_identity_safe() -> tuple[str, int]:
    """Return (rubric_id, rubric_version); fall back on any failure."""
    try:
        from apps_underwriting_ai.services import (  # noqa: PLC0415
            RubricWiringService,
        )

        spec = RubricWiringService().load()
        return spec.rubric_id, int(spec.rubric_version)
    except Exception as exc:  # guardian: allow-broad-exception -- rubric loader touches disk + yaml + dataclass construction; fail-soft to prior hardcoded identity so the judge marker pipeline never breaks (regulated-domain compliance floor)
        _LOGGER.info("[apps_underwriting_ai] rubric load fallback: %s", exc)
        return "underwriting_decision_rationale_v1", 1


def _pair_with_frontier_best_effort(
    *,
    accepted_qwen_text: str,
    verdict: DecisionVerdict,
    evidence_count: int,
    feature_count: int,
    unresolved: int,
) -> None:
    """Best-effort frontier-second-judge pairing (W3.3).

    NEVER mutates ``accepted_qwen_text`` — the Qwen-first rationale is
    already final for the DecisionPacket by the time this runs. Records
    one :class:`AgreementSample` to the rolling log when both paths
    produced non-empty text. Silent on every failure path.
    """
    if os.environ.get("APPS_UW_FRONTIER_PAIRING_ENABLED") != "1":
        return
    try:
        from apps_underwriting_ai.services import (  # noqa: PLC0415
            generate_frontier_rationale,
            record_pair,
        )
    except ImportError:
        return
    try:
        frontier_text, frontier_model, _reason = generate_frontier_rationale(
            verdict_value=verdict.value,
            evidence_count=evidence_count,
            feature_count=feature_count,
            unresolved=unresolved,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- frontier pairing is telemetry-only; ANY failure must fall through silently so the Qwen-first rationale remains the authoritative DecisionPacket.rationale (regulated-domain compliance floor)
        _LOGGER.info("[apps_underwriting_ai] frontier pairing failed: %s", exc)
        return
    if frontier_text is None:
        return
    try:
        record_pair(
            request_id="",
            verdict_value=verdict.value,
            qwen_rationale=accepted_qwen_text,
            frontier_rationale=frontier_text,
            frontier_model=frontier_model,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- tracker record is telemetry-only; filesystem or serialization hiccups must never leak into the assembler hot path (regulated-domain compliance floor)
        _LOGGER.info("[apps_underwriting_ai] agreement record skipped: %s", exc)
