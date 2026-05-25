"""L2 Candidate Gate Runner — generic, app-agnostic.

W6: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

Implements CandidateGateRunner.run_gates() which applies declarative gate
config to a tuple of CandidateArtifacts and returns only those that pass
all fail_closed gates.

Invariants:
- UNKNOWN is NOT PASS.
- NOT_APPLICABLE requires not_applicable_reason.
- FAIL with fail_closed=True blocks candidate.
- If ALL candidates are blocked and no repair policy allows continuation,
  AllCandidatesGatedError is raised (fail-closed).
- Quarantine: apps_rg.integrations.hops and integrations.gates are forbidden.
- No hardcoded resume section names.
- No hardcoded provider names.
- No L4 writes.
- No X3 emission.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from agentic_core.runtime.contracts.ensemble_types import CandidateArtifact
from agentic_core.runtime.contracts.judge_types import (
    GATE_RESULT_FAIL,
    GATE_RESULT_NOT_APPLICABLE,
    GATE_RESULT_PASS,
    GATE_RESULT_UNKNOWN,
    GATE_RESULT_WARN,
    CandidateGateResult,
)

_GATE_REF_UNKNOWN = "GATE_REF::UNKNOWN::NOT_EVALUATED"


class AllCandidatesGatedError(Exception):
    """Raised when all candidates fail fail_closed gates and no repair is possible."""


# ---------------------------------------------------------------------------
# Built-in deterministic gate functions (W6 stubs — no external calls)
# ---------------------------------------------------------------------------

def _gate_always_pass(candidate: CandidateArtifact, gate_cfg: Mapping[str, Any]) -> CandidateGateResult:
    return CandidateGateResult(
        gate_id=gate_cfg.get("gate_id", "always_pass"),
        candidate_id=candidate.candidate_id,
        node_id=candidate.node_id,
        result=GATE_RESULT_PASS,
        passed=True,
        reason="always_pass gate",
        gate_family=gate_cfg.get("gate_family", ""),
        severity=gate_cfg.get("severity", "warn"),
        fail_closed=gate_cfg.get("fail_closed", False),
        repair_allowed=gate_cfg.get("repair_allowed", True),
        threshold=float(gate_cfg.get("threshold", 0.0)),
    )


def _gate_always_fail(candidate: CandidateArtifact, gate_cfg: Mapping[str, Any]) -> CandidateGateResult:
    return CandidateGateResult(
        gate_id=gate_cfg.get("gate_id", "always_fail"),
        candidate_id=candidate.candidate_id,
        node_id=candidate.node_id,
        result=GATE_RESULT_FAIL,
        passed=False,
        rejection_reason="always_fail gate — deterministic rejection",
        reason="always_fail gate — deterministic rejection",
        gate_family=gate_cfg.get("gate_family", ""),
        severity=gate_cfg.get("severity", "hard_fail"),
        fail_closed=gate_cfg.get("fail_closed", True),
        repair_allowed=gate_cfg.get("repair_allowed", False),
        threshold=float(gate_cfg.get("threshold", 0.0)),
    )


def _gate_min_score_fixture(candidate: CandidateArtifact, gate_cfg: Mapping[str, Any]) -> CandidateGateResult:
    threshold = float(gate_cfg.get("threshold", 0.5))
    content = candidate.payload or candidate.text or candidate.generated_content
    score = float(gate_cfg.get("fixture_score", 0.8))
    passed = score >= threshold
    return CandidateGateResult(
        gate_id=gate_cfg.get("gate_id", "min_score_fixture"),
        candidate_id=candidate.candidate_id,
        node_id=candidate.node_id,
        result=GATE_RESULT_PASS if passed else GATE_RESULT_FAIL,
        passed=passed,
        gate_score=score,
        rejection_reason="" if passed else f"score {score:.3f} < threshold {threshold:.3f}",
        reason="" if passed else f"score {score:.3f} < threshold {threshold:.3f}",
        gate_family=gate_cfg.get("gate_family", ""),
        severity=gate_cfg.get("severity", "hard_fail"),
        fail_closed=gate_cfg.get("fail_closed", True),
        repair_allowed=gate_cfg.get("repair_allowed", False),
        threshold=threshold,
    )


def _gate_prompt_leakage_fixture(candidate: CandidateArtifact, gate_cfg: Mapping[str, Any]) -> CandidateGateResult:
    content = candidate.payload or candidate.text or candidate.generated_content
    leakage_markers = ("{{", "}}", "<|system|>", "<|assistant|>", "SLOT_", "GOVERNANCE_")
    leaked = any(m in content for m in leakage_markers)
    return CandidateGateResult(
        gate_id=gate_cfg.get("gate_id", "prompt_leakage_fixture"),
        candidate_id=candidate.candidate_id,
        node_id=candidate.node_id,
        result=GATE_RESULT_FAIL if leaked else GATE_RESULT_PASS,
        passed=not leaked,
        rejection_reason="prompt leakage detected" if leaked else "",
        reason="prompt leakage detected" if leaked else "",
        gate_family=gate_cfg.get("gate_family", "G23"),
        severity="hard_fail",
        fail_closed=True,
        repair_allowed=False,
        threshold=0.0,
    )


def _gate_no_fabrication_fixture(candidate: CandidateArtifact, gate_cfg: Mapping[str, Any]) -> CandidateGateResult:
    content = candidate.payload or candidate.text or candidate.generated_content
    fabrication_markers = ("FABRICATED_", "INVENTED_EMPLOYER", "FAKE_CREDENTIAL")
    fabricated = any(m in content for m in fabrication_markers)
    return CandidateGateResult(
        gate_id=gate_cfg.get("gate_id", "no_fabrication_fixture"),
        candidate_id=candidate.candidate_id,
        node_id=candidate.node_id,
        result=GATE_RESULT_FAIL if fabricated else GATE_RESULT_PASS,
        passed=not fabricated,
        rejection_reason="fabrication marker detected" if fabricated else "",
        reason="fabrication marker detected" if fabricated else "",
        gate_family=gate_cfg.get("gate_family", "G14"),
        severity="hard_fail",
        fail_closed=True,
        repair_allowed=False,
        threshold=0.99,
    )


_BUILTIN_GATES: Dict[str, Any] = {
    "always_pass": _gate_always_pass,
    "always_fail": _gate_always_fail,
    "min_score_fixture": _gate_min_score_fixture,
    "prompt_leakage_fixture": _gate_prompt_leakage_fixture,
    "no_fabrication_fixture": _gate_no_fabrication_fixture,
}


# ---------------------------------------------------------------------------
# CandidateGateRunner
# ---------------------------------------------------------------------------

class CandidateGateRunner:
    """Apply declarative gate config to a pool of CandidateArtifacts.

    Design:
    - Gate functions are injected via _custom_gates for testability.
    - Built-in stub gates cover W6 deterministic test scenarios.
    - Config-driven: gate_profile is a list of gate_cfg dicts from YAML.
    - Fail-closed: if a gate_fn raises, result is UNKNOWN (not PASS).
    - AllCandidatesGatedError raised when pool is exhausted.
    """

    def __init__(
        self,
        *,
        custom_gates: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self._gates: Dict[str, Any] = {**_BUILTIN_GATES, **(custom_gates or {})}

    def run_gates(
        self,
        candidates: Sequence[CandidateArtifact],
        gate_profile: Sequence[Mapping[str, Any]],
        context: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[CandidateArtifact, ...]:
        """Run all gates in gate_profile against each candidate.

        Returns the tuple of candidates that pass all fail_closed gates.
        Raises AllCandidatesGatedError if no candidates survive.

        Args:
            candidates: pool produced by generator gateway.
            gate_profile: list of gate config dicts (from candidate_gates.yaml or test fixture).
            context: optional runtime context for gate functions.

        Returns:
            Tuple of CandidateArtifacts with gate_results populated, gates_passed=True.
        """
        if not candidates:
            raise AllCandidatesGatedError("No candidates supplied to gate runner.")

        surviving: List[CandidateArtifact] = []

        for candidate in candidates:
            gate_results: List[str] = []
            candidate_blocked = False

            for gate_cfg in gate_profile:
                gate_id = gate_cfg.get("gate_id", "")
                gate_fn = self._gates.get(gate_id)

                if gate_fn is None:
                    result = CandidateGateResult(
                        gate_id=gate_id,
                        candidate_id=candidate.candidate_id,
                        node_id=candidate.node_id,
                        result=GATE_RESULT_UNKNOWN,
                        passed=False,
                        unknown_reason=f"No gate implementation found for gate_id={gate_id!r}",
                        reason=f"No gate implementation found for gate_id={gate_id!r}",
                        severity=gate_cfg.get("severity", "hard_fail"),
                        fail_closed=gate_cfg.get("fail_closed", True),
                        repair_allowed=gate_cfg.get("repair_allowed", False),
                        threshold=float(gate_cfg.get("threshold", 0.0)),
                    )
                else:
                    try:
                        result = gate_fn(candidate, gate_cfg)
                    except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
                        result = CandidateGateResult(
                            gate_id=gate_id,
                            candidate_id=candidate.candidate_id,
                            node_id=candidate.node_id,
                            result=GATE_RESULT_UNKNOWN,
                            passed=False,
                            unknown_reason=f"gate_fn raised: {exc}",
                            reason=f"gate_fn raised: {exc}",
                            severity=gate_cfg.get("severity", "hard_fail"),
                            fail_closed=gate_cfg.get("fail_closed", True),
                            repair_allowed=gate_cfg.get("repair_allowed", False),
                            threshold=float(gate_cfg.get("threshold", 0.0)),
                        )

                gate_results.append(result.as_json())

                if result.result not in (GATE_RESULT_PASS, GATE_RESULT_WARN, GATE_RESULT_NOT_APPLICABLE):
                    if result.fail_closed:
                        candidate_blocked = True

            if not candidate_blocked:
                survived = _replace_candidate(candidate, gate_results=tuple(gate_results), gates_passed=True)
                surviving.append(survived)

        if not surviving:
            raise AllCandidatesGatedError(
                f"All {len(candidates)} candidate(s) failed fail_closed gates. "
                "No repair policy allows continuation."
            )

        return tuple(surviving)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _replace_candidate(
    candidate: CandidateArtifact,
    *,
    gate_results: Tuple[str, ...],
    gates_passed: bool,
) -> CandidateArtifact:
    """Return a new CandidateArtifact with gate results populated."""
    return CandidateArtifact(
        candidate_id=candidate.candidate_id,
        node_id=candidate.node_id,
        run_id=candidate.run_id,
        app_context=candidate.app_context,
        variant_ref=candidate.variant_ref,
        payload=candidate.payload,
        text=candidate.text,
        payload_digest=candidate.payload_digest,
        generated_content=candidate.generated_content,
        model_ref=candidate.model_ref,
        temperature=candidate.temperature,
        prompt_profile_digest=candidate.prompt_profile_digest,
        provider_receipt_ref=candidate.provider_receipt_ref,
        provider_profile=candidate.provider_profile,
        prompt_ref=candidate.prompt_ref,
        evidence_refs=candidate.evidence_refs,
        generation_digest=candidate.generation_digest,
        generation_timestamp=candidate.generation_timestamp,
        generation_duration_ms=candidate.generation_duration_ms,
        gate_results=gate_results,
        gates_passed=gates_passed,
        judge_results=candidate.judge_results,
        final_score=candidate.final_score,
        selection_rank=candidate.selection_rank,
        runtime_gate_refs=candidate.runtime_gate_refs or (_GATE_REF_UNKNOWN,),
        trace_root=candidate.trace_root,
        otel_span_ref=candidate.otel_span_ref,
        replay_key=candidate.replay_key,
    )
