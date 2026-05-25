"""L2 Ensemble Model Lane — generic, app-agnostic.

W6: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

Implements EnsembleModelLane which consumes one L3ToL2StepContract and
produces one SealedSectionArtifact through:
  1. Generator gateway → N CandidateArtifacts.
  2. CandidateGateRunner → filtered pool.
  3. JudgeJuryRunner → EnsembleSelectionReceipt + winner.
  4. Seal winner → SealedSectionArtifact.

Invariants:
- Consumes EXACTLY ONE L3ToL2StepContract.
- Produces EXACTLY ONE SealedSectionArtifact.
- allowed_execution_lane must be "ENSEMBLE_MODEL" (case-insensitive).
- Generator gateway is injected — no real provider SDK calls in W6.
- No route / workflow expansion.
- No L4 writes, no X3, no call to L3.
- No hardcoded provider names in generic core.
- No hardcoded resume section names.
- Quarantine: apps_rg.integrations.hops and integrations.gates are forbidden.
- runtime_gate_refs set to UNKNOWN when harness not wired.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Protocol, Sequence, Tuple

from agentic_core.runtime.contracts.ensemble_types import (
    CandidateArtifact,
    EnsembleSelectionReceipt,
)
from agentic_core.runtime.contracts.judge_types import JudgeResult
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract
from agentic_core.runtime.contracts.sealed_workflow_types import SealedSectionArtifact
from agentic_core.L2_execution.candidate_gate_runner import (
    AllCandidatesGatedError,
    CandidateGateRunner,
)
from agentic_core.L2_execution.judge_jury_runner import (
    JudgeJuryRunner,
    MissingRequiredJudgeError,
)

_REQUIRED_LANE = "ENSEMBLE_MODEL"
_GATE_REF_UNKNOWN = "GATE_REF::UNKNOWN::NOT_EVALUATED"


class EnsembleLaneError(Exception):
    """Raised on any fail-closed path in EnsembleModelLane."""


# ---------------------------------------------------------------------------
# Generator gateway protocol
# ---------------------------------------------------------------------------

class GeneratorGateway(Protocol):
    """Injectable candidate generator.

    W6 tests inject FakeGeneratorGateway.
    Real implementations call provider SDK via existing gateway abstraction.
    """

    def generate_candidates(
        self,
        step_contract: L3ToL2StepContract,
        prompt_variants: Sequence[str],
        provider_profile: str,
        candidate_count: int,
        temperature_profile: Sequence[float],
    ) -> Tuple[CandidateArtifact, ...]:
        """Generate candidate_count CandidateArtifacts for step_contract."""
        ...


# ---------------------------------------------------------------------------
# EnsembleModelLane
# ---------------------------------------------------------------------------

class EnsembleModelLane:
    """Generic L2 execution lane for ENSEMBLE_MODEL workflow nodes.

    Usage:
        lane = EnsembleModelLane(
            generator_gateway=FakeGeneratorGateway(),
            gate_runner=CandidateGateRunner(),
            judge_runner=JudgeJuryRunner(judge_gateway=FakeJudgeGateway()),
        )
        artifact = lane.execute(step_contract, gate_profile=[], judge_profile=[])
    """

    def __init__(
        self,
        *,
        generator_gateway: GeneratorGateway,
        gate_runner: Optional[CandidateGateRunner] = None,
        judge_runner: Optional[JudgeJuryRunner] = None,
    ) -> None:
        self._generator = generator_gateway
        self._gate_runner = gate_runner or CandidateGateRunner()
        self._judge_runner = judge_runner or JudgeJuryRunner()

    def execute(
        self,
        step_contract: L3ToL2StepContract,
        *,
        gate_profile: Sequence[Mapping[str, Any]],
        judge_profile: Sequence[Mapping[str, Any]],
        selection_policy: str = "highest_mean",
        prompt_variants: Optional[Sequence[str]] = None,
        temperature_profile: Optional[Sequence[float]] = None,
    ) -> SealedSectionArtifact:
        """Execute one bounded node and return a sealed artifact.

        Args:
            step_contract: from L3 for exactly one workflow node.
            gate_profile: list of gate config dicts.
            judge_profile: list of judge spec dicts.
            selection_policy: winner selection strategy.
            prompt_variants: optional prompt refs for generator.
            temperature_profile: optional temperature settings per variant.

        Returns:
            SealedSectionArtifact for the winning candidate.

        Raises:
            EnsembleLaneError: on any fail-closed path.
        """
        # ── 1. Validate execution lane ────────────────────────────────────
        lane = getattr(step_contract, "allowed_execution_lane", "") or ""
        if lane.upper() != _REQUIRED_LANE:
            raise EnsembleLaneError(
                f"EnsembleModelLane requires allowed_execution_lane={_REQUIRED_LANE!r}, "
                f"got {lane!r}. Non-ensemble lanes must not reach this runner."
            )

        node_id = getattr(step_contract, "node_id", "")
        run_id = getattr(step_contract, "run_id", "")
        workflow_ref = getattr(step_contract, "workflow_ref", "")
        route_contract_ref = getattr(step_contract, "route_contract_ref", "")
        replay_key = getattr(step_contract, "replay_key", "")
        trace_root = getattr(step_contract, "trace_root", "")
        provider_profile = getattr(step_contract, "provider_profile_ref", "") or ""
        candidate_count = getattr(step_contract, "candidate_count", 3) or 3
        prompt_ref = getattr(step_contract, "prompt_profile_ref", "") or ""
        evidence_refs = tuple(getattr(step_contract, "evidence_refs", ()) or ())
        output_schema_ref = getattr(step_contract, "output_schema_ref", "") or ""

        # ── W7: Consume compiled prompt refs from step contract ───────────
        # Prefer W7 prompt_artifact_ref; fall back to carried_prompt_refs;
        # fall back to legacy prompt_profile_ref.
        prompt_artifact_ref = getattr(step_contract, "prompt_artifact_ref", "") or ""
        carried_prompt_refs = tuple(getattr(step_contract, "carried_prompt_refs", ()) or ())
        # Resolve the best available prompt ref for generator context
        resolved_prompt_ref = (
            prompt_artifact_ref
            or (carried_prompt_refs[0] if carried_prompt_refs else "")
            or prompt_ref
        )

        # ── 2. Generate candidates ────────────────────────────────────────
        _prompt_variants = list(prompt_variants or [resolved_prompt_ref] or [""])
        _temp_profile = list(temperature_profile or [0.7] * candidate_count)

        try:
            candidates = self._generator.generate_candidates(
                step_contract,
                _prompt_variants,
                provider_profile,
                candidate_count,
                _temp_profile,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
            raise EnsembleLaneError(f"Generator gateway failed: {exc}") from exc

        if not candidates:
            raise EnsembleLaneError("Generator gateway returned zero candidates.")

        # ── 3. Run candidate gates ────────────────────────────────────────
        try:
            passing_candidates = self._gate_runner.run_gates(
                candidates, gate_profile, context={"node_id": node_id, "run_id": run_id}
            )
        except AllCandidatesGatedError as exc:
            raise EnsembleLaneError(f"All candidates failed gates: {exc}") from exc

        # ── 4. Run judge jury ─────────────────────────────────────────────
        try:
            receipt, winner = self._judge_runner.run_jury(
                passing_candidates, judge_profile, selection_policy=selection_policy
            )
        except MissingRequiredJudgeError as exc:
            raise EnsembleLaneError(f"Judge jury failed closed: {exc}") from exc
        except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
            raise EnsembleLaneError(f"Judge jury runner error: {exc}") from exc

        # ── 5. Seal section artifact ──────────────────────────────────────
        return _seal_artifact(
            winner=winner,
            receipt=receipt,
            node_id=node_id,
            workflow_ref=workflow_ref,
            route_contract_ref=route_contract_ref,
            replay_key=replay_key,
            output_schema_ref=output_schema_ref,
            evidence_refs=evidence_refs,
        )


# ---------------------------------------------------------------------------
# Top-level convenience function (matches spec: execute_ensemble_node)
# ---------------------------------------------------------------------------

def execute_ensemble_node(
    step_contract: L3ToL2StepContract,
    generator_gateway: GeneratorGateway,
    gate_runner: Optional[CandidateGateRunner] = None,
    judge_runner: Optional[JudgeJuryRunner] = None,
    *,
    gate_profile: Sequence[Mapping[str, Any]],
    judge_profile: Sequence[Mapping[str, Any]],
    selection_policy: str = "highest_mean",
) -> SealedSectionArtifact:
    """Functional entry point wrapping EnsembleModelLane.execute()."""
    lane = EnsembleModelLane(
        generator_gateway=generator_gateway,
        gate_runner=gate_runner,
        judge_runner=judge_runner,
    )
    return lane.execute(
        step_contract,
        gate_profile=gate_profile,
        judge_profile=judge_profile,
        selection_policy=selection_policy,
    )


# ---------------------------------------------------------------------------
# Sealing helper
# ---------------------------------------------------------------------------

def _seal_artifact(
    *,
    winner: CandidateArtifact,
    receipt: EnsembleSelectionReceipt,
    node_id: str,
    workflow_ref: str,
    route_contract_ref: str,
    replay_key: str,
    output_schema_ref: str,
    evidence_refs: Tuple[str, ...],
) -> SealedSectionArtifact:
    payload = winner.payload or winner.text or winner.generated_content
    payload_digest = winner.payload_digest or _digest_str(payload)
    receipt_ref = f"receipt::ensemble_selection::{node_id}::{receipt.winner_digest}"
    gate_result_refs = winner.gate_results or (_GATE_REF_UNKNOWN,)
    judge_result_refs = winner.judge_results or (_GATE_REF_UNKNOWN,)

    return SealedSectionArtifact(
        node_id=node_id,
        workflow_ref=workflow_ref,
        artifact_id=f"artifact::{node_id}::{payload_digest[:8]}",
        sealed_content=payload,
        payload_ref=receipt_ref,
        payload_digest=payload_digest,
        output_schema_ref=output_schema_ref,
        gate_result_refs=gate_result_refs,
        judge_result_refs=judge_result_refs,
        l2_trace_refs=(f"trace::{winner.trace_root}",) if winner.trace_root else (),
        terminal_class="success",
        decisive_reason=receipt.selection_reason or "ensemble_selection",
        trace_root=winner.trace_root,
        sealed_at=datetime.now(timezone.utc).isoformat(),
    )


def _digest_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()[:16]
