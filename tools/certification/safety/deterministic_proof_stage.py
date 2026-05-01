"""Deterministic veto stage — STRUCTURAL / FAIL-CLOSED / NEGATIVE PROOFS ONLY.

WARNING — Scope of authorized use (see W2 proof-hardening § rule 5):
    This stage MUST NOT be used as the sole basis for certifying
    RTC-REQ-056 ACCEPTED. The integrated-runtime acceptance path
    requires the approved C-primary ``LLMJudgeVeto`` stage. The
    ``run_integrated_safe_reuse`` entry point introspects the
    orchestrator and sets ``veto_stage_match_status = "STRUCTURAL_ONLY"``
    on any run that includes this class. The composer's
    ``_map_integrated_runtime_proof`` refuses PASS for STRUCTURAL_ONLY
    runs — only ``PASS`` (real LLMJudgeVeto, no proof stage) certifies.

Authorized uses:
    1. **Structural proof**: proving the integrated-runtime chain emits
       all 12 artifacts and that the entry point drives the full
       topology — allowed with ``match_status=STRUCTURAL_ONLY`` label.
    2. **Negative / fail-closed tests**: exercising the BLOCK /
       UNKNOWN / ERROR / TIMEOUT / PARSE_FAIL code paths deterministically
       inside unit tests. These runs are never submitted as evidence
       for RTC-REQ-056 acceptance.
    3. **CI-safe fallback evidence**: smoke runs where a live LLM
       endpoint is unavailable, labeled as STRUCTURAL.

Forbidden:
    - Combining this stage with the real ``LLMJudgeVeto`` in the same
      orchestrator stack for an acceptance run (the classification
      helper flags the mixed stack as STRUCTURAL_ONLY).
    - Silently producing ``veto_stage_match_status=PASS`` with this
      stage (impossible by design — the classifier rejects it).

This stage is production-side (not under ``tests/``). It implements the
``VetoStage`` Protocol and returns deterministic verdicts based on a
caller-supplied lookup table.

Usage:

    stage = DeterministicProofStage(
        verdicts={
            ("safe_query", "safe_cached_query"): "SAFE",
            ("hard_neg_query", "hard_neg_cached"): "UNSAFE_DIFFERENT_INTENT",
        },
        default="UNCERTAIN",  # fail-closed default
    )
    orchestrator = VetoOrchestrator(stages=[stage])
    run_integrated_safe_reuse(..., veto_orchestrator=orchestrator)

The stage reports its name as ``llm_judge`` so existing invocation
counters (``llm_judge_invocation_count``) increment correctly. This is
the SAME interface contract a real LLM judge satisfies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from tools.certification.safety.veto_protocol import (
    VetoResult,
    VetoStage,
    VetoStatus,
)


@dataclass
class DeterministicProofStage:
    """Deterministic veto stage for proofs that require a known verdict path.

    Attributes:
        verdicts: Mapping from ``(query, cached_query)`` to a verdict
            string (``SAFE`` / ``UNSAFE_DIFFERENT_INTENT`` /
            ``UNSAFE_POLICY_DRIFT`` / ``VETO`` / ``UNCERTAIN`` / ``ERROR``
            / ``TIMEOUT`` / ``PARSE_FAIL``).
        default: Verdict to return for any pair not in ``verdicts``.
            Default is ``UNCERTAIN`` (fail-closed).
        confidence: Returned with SAFE results.
        latency_ms: Simulated stage latency.
        announce_as: Stage identifier reported to the orchestrator. Default
            ``llm_judge`` so the production invocation counter logic (which
            looks for stage names starting with ``llm_judge``) works
            unchanged.
    """

    verdicts: dict[tuple[str, str], str] = field(default_factory=dict)
    default: str = "UNCERTAIN"
    confidence: float = 0.95
    latency_ms: float = 1.0
    announce_as: str = "llm_judge"

    @property
    def name(self) -> str:
        return self.announce_as

    def is_available(self) -> bool:
        return True

    def evaluate(
        self,
        query: str,
        cached_query: str,
        cached_answer: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> VetoResult:
        """Look up the verdict for ``(query, cached_query)`` and emit a
        ``VetoResult`` of the correct shape — including all fail-closed
        buckets. Production-shaped: same VetoResult.* factories the real
        LLMJudgeVeto uses."""
        t0 = time.perf_counter()
        verdict = self.verdicts.get((query, cached_query), self.default).upper()
        latency = (time.perf_counter() - t0) * 1000.0 + self.latency_ms

        if verdict == "SAFE":
            return VetoResult.safe(
                stage_name=self.name,
                confidence=self.confidence,
                rationale="DeterministicProofStage: pair classified SAFE",
                latency_ms=latency,
                metadata={"provider": "deterministic_proof", "verdict": "SAFE"},
            )
        if verdict == "UNSAFE_DIFFERENT_INTENT":
            return VetoResult.unsafe_intent(
                stage_name=self.name,
                contradiction="DeterministicProofStage: opposite-intent pair",
                confidence=self.confidence,
                latency_ms=latency,
            )
        if verdict == "UNSAFE_POLICY_DRIFT":
            return VetoResult.unsafe_policy(
                stage_name=self.name,
                violation="DeterministicProofStage: policy drift",
                confidence=self.confidence,
                latency_ms=latency,
            )
        if verdict == "VETO":
            return VetoResult.veto(
                stage_name=self.name,
                reason="DeterministicProofStage: generic veto",
                confidence=self.confidence,
                latency_ms=latency,
            )
        if verdict == "UNKNOWN" or verdict == "UNCERTAIN":
            return VetoResult.unknown(
                stage_name=self.name,
                reason="DeterministicProofStage: uncertain verdict",
                latency_ms=latency,
            )
        if verdict == "TIMEOUT":
            return VetoResult.error(
                stage_name=self.name,
                error="Timeout: simulated latency budget exhaustion",
                latency_ms=latency,
            )
        if verdict == "PARSE_FAIL":
            return VetoResult.error(
                stage_name=self.name,
                error="Parse error: malformed JSON verdict",
                latency_ms=latency,
            )
        if verdict == "ERROR":
            return VetoResult.error(
                stage_name=self.name,
                error="Simulated provider error",
                latency_ms=latency,
            )
        # Unknown verdict label → fail-closed UNKNOWN.
        return VetoResult.unknown(
            stage_name=self.name,
            reason=f"DeterministicProofStage: unrecognized verdict {verdict!r}",
            latency_ms=latency,
        )


__all__ = ["DeterministicProofStage"]
