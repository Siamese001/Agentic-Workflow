"""L2 Judge Jury Runner — generic, app-agnostic.

W6: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

Implements JudgeJuryRunner.run_jury() which scores gate-passing candidates
through an injected judge gateway, aggregates scores, and selects a winner
using the configured selection_policy.

Invariants:
- Missing required judge → fails closed (MissingRequiredJudgeError).
- Missing informational judge → warn only, does NOT hard fail.
- Judge timeout for required dimension → fails closed.
- No external LLM calls in W6 (injected judge_gateway used).
- Quarantine: apps_rg.engines.judges.executive_positioning_judge is forbidden.
- No L4 writes, no X3.
- Selection policies: highest_mean | consensus | best_of_n | first_passed.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol, Sequence, Tuple

from agentic_core.runtime.contracts.ensemble_types import (
    CandidateArtifact,
    EnsembleSelectionReceipt,
)
from agentic_core.runtime.contracts.judge_types import (
    JudgeJuryResult,
    JudgeResult,
)

_GATE_REF_UNKNOWN = "GATE_REF::UNKNOWN::NOT_EVALUATED"

# ---------------------------------------------------------------------------
# Protocols / gateway interface
# ---------------------------------------------------------------------------

class JudgeGateway(Protocol):
    """Injectable judge gateway.

    Implementations may call LLMs, use stubs, or replay fixtures.
    W6 tests inject FakeJudgeGateway.
    """

    def score_candidate(
        self,
        candidate: CandidateArtifact,
        judge_spec: Mapping[str, Any],
    ) -> JudgeResult:
        """Score one candidate for one judge_spec.

        Raises JudgeTimeoutError on timeout.
        """
        ...


class JudgeTimeoutError(Exception):
    """Raised by a judge gateway when scoring exceeds timeout."""


class MissingRequiredJudgeError(Exception):
    """Raised when a required judge is absent and no stub is available."""


# ---------------------------------------------------------------------------
# Selection policies
# ---------------------------------------------------------------------------

_SELECTION_POLICIES = frozenset({"highest_mean", "consensus", "best_of_n", "first_passed"})


def _select_winner(
    scored_candidates: Sequence[Tuple[CandidateArtifact, float]],
    policy: str,
) -> Tuple[CandidateArtifact, str]:
    """Select winner from scored candidates using policy.

    Returns (winner_candidate, selection_reason).
    """
    if not scored_candidates:
        raise ValueError("No scored candidates available for selection.")

    if policy in ("highest_mean", "best_of_n", "consensus"):
        winner, score = max(scored_candidates, key=lambda t: t[1])
        return winner, f"{policy}: score={score:.4f}"

    if policy == "first_passed":
        winner, score = scored_candidates[0]
        return winner, f"first_passed: first gate-surviving candidate, score={score:.4f}"

    winner, score = max(scored_candidates, key=lambda t: t[1])
    return winner, f"fallback_highest_mean: unknown policy {policy!r}, score={score:.4f}"


# ---------------------------------------------------------------------------
# JudgeJuryRunner
# ---------------------------------------------------------------------------

class JudgeJuryRunner:
    """Run judge jury over gate-passing candidates and select a winner.

    Design:
    - Injected judge_gateway for testability (no direct LLM SDK imports here).
    - Judge profile is a list of judge spec dicts from config.
    - required_for_exit=True judges that fail → MissingRequiredJudgeError.
    - informational_only=True judges that fail → warn only.
    - Selection policy configurable per node.
    """

    def __init__(
        self,
        judge_gateway: Optional[JudgeGateway] = None,
    ) -> None:
        self._gateway = judge_gateway

    def run_jury(
        self,
        candidates: Sequence[CandidateArtifact],
        judge_profile: Sequence[Mapping[str, Any]],
        selection_policy: str = "highest_mean",
    ) -> Tuple[EnsembleSelectionReceipt, CandidateArtifact]:
        """Score candidates through judge jury and return (receipt, winner).

        Args:
            candidates: gate-passing CandidateArtifacts.
            judge_profile: list of judge spec dicts.
            selection_policy: one of highest_mean|consensus|best_of_n|first_passed.

        Returns:
            (EnsembleSelectionReceipt, winner CandidateArtifact)

        Raises:
            MissingRequiredJudgeError: when a required judge is absent / errors.
            ValueError: when candidates is empty.
        """
        if not candidates:
            raise ValueError("No candidates supplied to judge jury runner.")

        if selection_policy not in _SELECTION_POLICIES:
            selection_policy = "highest_mean"

        scored: List[Tuple[CandidateArtifact, float]] = []
        all_jury_results: List[JudgeJuryResult] = []

        for candidate in candidates:
            jury_result, agg_score = self._score_one(candidate, judge_profile)
            all_jury_results.append(jury_result)
            scored.append((candidate, agg_score))

        winner, selection_reason = _select_winner(scored, selection_policy)

        all_candidate_ids_digest = _digest_str(
            "|".join(c.candidate_id for c, _ in scored)
        )
        winner_digest = _digest_str(winner.payload or winner.text or winner.generated_content)
        rejected_ids = tuple(c.candidate_id for c, _ in scored if c.candidate_id != winner.candidate_id)
        winner_score = next(s for c, s in scored if c.candidate_id == winner.candidate_id)

        receipt = EnsembleSelectionReceipt(
            node_id=winner.node_id,
            run_id=winner.run_id,
            winner_candidate_id=winner.candidate_id,
            winner_digest=winner_digest,
            selected_candidate_id=winner.candidate_id,
            selection_policy=selection_policy,
            selection_policy_applied=selection_policy,
            selection_reason=selection_reason,
            candidate_count=len(candidates),
            total_candidates=len(candidates),
            passed_gate_count=len(candidates),
            candidates_passed_gates=len(candidates),
            judged_count=len(scored),
            candidates_scored=len(scored),
            all_candidates_digest=all_candidate_ids_digest,
            rejected_candidate_ids=rejected_ids,
            winning_score=winner_score,
            runner_up_score=sorted(s for _, s in scored)[-2] if len(scored) > 1 else 0.0,
            score_gap=winner_score - (sorted(s for _, s in scored)[-2] if len(scored) > 1 else 0.0),
            scoring_method=selection_policy,
            replay_key=winner.replay_key,
            receipt_timestamp=datetime.now(timezone.utc).isoformat(),
            selection_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        winner_with_judges = _replace_candidate_judges(
            winner,
            judge_results=tuple(r.as_json() for r in all_jury_results if r.candidate_id == winner.candidate_id),
            final_score=winner_score,
            selection_rank=1,
        )

        return receipt, winner_with_judges

    def _score_one(
        self,
        candidate: CandidateArtifact,
        judge_profile: Sequence[Mapping[str, Any]],
    ) -> Tuple[JudgeJuryResult, float]:
        """Score one candidate against all judges in profile.

        Returns (JudgeJuryResult, aggregate_score).
        """
        judge_results: List[JudgeResult] = []
        missing_required: List[str] = []
        missing_informational: List[str] = []
        scores: List[float] = []

        for judge_spec in judge_profile:
            judge_id = judge_spec.get("judge_id", "")
            required = judge_spec.get("required_for_exit", False)
            informational = judge_spec.get("informational_only", False)

            if self._gateway is None:
                if required:
                    missing_required.append(judge_id)
                    continue
                else:
                    missing_informational.append(judge_id)
                    continue

            try:
                result = self._gateway.score_candidate(candidate, judge_spec)
                judge_results.append(result)
                if not result.abstained and not result.error:
                    scores.append(result.score)
                elif required:
                    missing_required.append(judge_id)
            except JudgeTimeoutError:
                if required:
                    missing_required.append(judge_id)
                else:
                    missing_informational.append(judge_id)
            except Exception as exc:
                if required:
                    missing_required.append(judge_id)
                else:
                    missing_informational.append(judge_id)

        if missing_required:
            raise MissingRequiredJudgeError(
                f"Required judge(s) missing or failed: {missing_required}. Failing closed."
            )

        agg_score = (sum(scores) / len(scores)) if scores else 0.5

        consensus = "consensus" if len(set(round(s, 1) for s in scores)) <= 1 else "split"
        if not scores:
            consensus = "abstained"

        jury = JudgeJuryResult(
            candidate_id=candidate.candidate_id,
            node_id=candidate.node_id,
            run_id=candidate.run_id,
            aggregate_score=agg_score,
            aggregated_score=agg_score,
            consensus_status=consensus,
            selection_policy_applied="",
            decisive_reason=f"agg_score={agg_score:.4f}",
            missing_required_judges=tuple(missing_required),
            informational_judges_missing=tuple(missing_informational),
            judge_count=len(judge_results),
            abstain_count=sum(1 for r in judge_results if r.abstained),
            judge_result_refs=tuple(r.as_json() for r in judge_results),
            judge_results=tuple(r.as_json() for r in judge_results),
            verdict_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        return jury, agg_score


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _digest_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()[:16]


def _replace_candidate_judges(
    candidate: CandidateArtifact,
    *,
    judge_results: Tuple[str, ...],
    final_score: float,
    selection_rank: int,
) -> CandidateArtifact:
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
        gate_results=candidate.gate_results,
        gates_passed=candidate.gates_passed,
        judge_results=judge_results,
        final_score=final_score,
        selection_rank=selection_rank,
        runtime_gate_refs=candidate.runtime_gate_refs or (_GATE_REF_UNKNOWN,),
        trace_root=candidate.trace_root,
        otel_span_ref=candidate.otel_span_ref,
        replay_key=candidate.replay_key,
    )
