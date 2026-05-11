"""Ensemble execution types — generic, app-agnostic contracts.

Phase 1.1 of apps-rg-ensemble-judge-restoration-a7c4e2.
W6 extended: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W6
  - CandidateArtifact: added variant_ref, payload/text, payload_digest,
    provider_profile, prompt_ref, evidence_refs, generation_digest,
    gate_results, gates_passed, judge_results, final_score, selection_rank,
    runtime_gate_refs.
  - EnsembleSelectionReceipt: added winner_candidate_id, winner_digest,
    selection_policy, candidate_count, passed_gate_count, judged_count,
    all_candidates_digest, rejected_candidate_ids, receipt_timestamp.
  All new fields default-empty; existing fields preserved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True, slots=True)
class CandidateArtifact:
    """A single generated candidate for one workflow node.

    Produced by L2 ENSEMBLE_MODEL lane.  Contains the raw generation
    plus metadata needed for downstream gating and judging.
    """

    candidate_id: str = ""
    node_id: str = ""
    run_id: str = ""
    app_context: str = ""

    # W6: explicit variant/payload shape
    variant_ref: str = ""             # e.g. "variant::temperature_high"
    payload: str = ""                 # structured payload (JSON string)
    text: str = ""                    # plain text form (may == payload)
    payload_digest: str = ""          # sha256 of payload/text

    # Generation metadata — original fields
    generated_content: str = ""
    model_ref: str = ""
    temperature: float = 0.0
    prompt_profile_digest: str = ""
    provider_receipt_ref: str = ""

    # W6: provider profile ref (registry key, not hardcoded provider name)
    provider_profile: str = ""        # registry key e.g. "provider::local_qwen_32b"
    prompt_ref: str = ""              # compiled prompt artifact ref
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    generation_digest: str = ""       # content-hash of entire generated response

    # Timing — original fields
    generation_timestamp: str = ""
    generation_duration_ms: int = 0

    # W6: gate / judge results (embedded for compact transport)
    gate_results: tuple[str, ...] = field(default_factory=tuple)   # serialised CandidateGateResult refs
    gates_passed: bool = False
    judge_results: tuple[str, ...] = field(default_factory=tuple)  # serialised JudgeResult refs
    final_score: float = 0.0
    selection_rank: int = 0           # 1 = winner, 0 = unranked

    # W6: runtime gate refs (UNKNOWN when harness absent)
    runtime_gate_refs: tuple[str, ...] = field(default_factory=tuple)

    # Tracing — original fields
    trace_root: str = ""
    otel_span_ref: str = ""
    replay_key: str = ""

    schema_version: str = "W6.a3f7e2"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "node_id": self.node_id,
            "run_id": self.run_id,
            "app_context": self.app_context,
            "variant_ref": self.variant_ref,
            "payload": self.payload,
            "text": self.text,
            "payload_digest": self.payload_digest,
            "generated_content": self.generated_content,
            "model_ref": self.model_ref,
            "temperature": self.temperature,
            "prompt_profile_digest": self.prompt_profile_digest,
            "provider_receipt_ref": self.provider_receipt_ref,
            "provider_profile": self.provider_profile,
            "prompt_ref": self.prompt_ref,
            "evidence_refs": list(self.evidence_refs),
            "generation_digest": self.generation_digest,
            "generation_timestamp": self.generation_timestamp,
            "generation_duration_ms": self.generation_duration_ms,
            "gate_results": list(self.gate_results),
            "gates_passed": self.gates_passed,
            "judge_results": list(self.judge_results),
            "final_score": self.final_score,
            "selection_rank": self.selection_rank,
            "runtime_gate_refs": list(self.runtime_gate_refs),
            "trace_root": self.trace_root,
            "otel_span_ref": self.otel_span_ref,
            "replay_key": self.replay_key,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class EnsembleSelectionReceipt:
    """Records which candidate won selection for a node and why.

    Produced by L2 after judge jury completes scoring.
    """

    node_id: str = ""
    run_id: str = ""
    app_context: str = ""

    # W6: explicit winner fields
    winner_candidate_id: str = ""
    winner_digest: str = ""
    selection_policy: str = ""        # e.g. "highest_mean", "consensus"

    # Selection outcome — original fields
    selected_candidate_id: str = ""   # alias for winner_candidate_id
    selection_reason: str = ""
    selection_policy_applied: str = ""

    # W6: candidate pool counts
    candidate_count: int = 0
    passed_gate_count: int = 0
    judged_count: int = 0
    all_candidates_digest: str = ""   # hash over all candidate_ids + digests
    rejected_candidate_ids: tuple[str, ...] = field(default_factory=tuple)

    # Candidate pool summary — original fields
    total_candidates: int = 0
    candidates_passed_gates: int = 0
    candidates_scored: int = 0

    # Scoring summary — original fields
    winning_score: float = 0.0
    runner_up_score: float = 0.0
    score_gap: float = 0.0
    scoring_method: str = ""

    # Judge refs — original fields
    jury_result_refs: tuple[str, ...] = field(default_factory=tuple)
    gate_result_refs: tuple[str, ...] = field(default_factory=tuple)

    # Tracing — original fields
    trace_root: str = ""
    otel_span_ref: str = ""
    replay_key: str = ""
    selection_timestamp: str = ""
    receipt_timestamp: str = ""       # W6 alias for selection_timestamp

    schema_version: str = "W6.a3f7e2"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "run_id": self.run_id,
            "app_context": self.app_context,
            "winner_candidate_id": self.winner_candidate_id or self.selected_candidate_id,
            "winner_digest": self.winner_digest,
            "selection_policy": self.selection_policy,
            "selected_candidate_id": self.selected_candidate_id or self.winner_candidate_id,
            "selection_reason": self.selection_reason,
            "selection_policy_applied": self.selection_policy_applied or self.selection_policy,
            "candidate_count": self.candidate_count or self.total_candidates,
            "passed_gate_count": self.passed_gate_count or self.candidates_passed_gates,
            "judged_count": self.judged_count or self.candidates_scored,
            "all_candidates_digest": self.all_candidates_digest,
            "rejected_candidate_ids": list(self.rejected_candidate_ids),
            "total_candidates": self.total_candidates or self.candidate_count,
            "candidates_passed_gates": self.candidates_passed_gates or self.passed_gate_count,
            "candidates_scored": self.candidates_scored or self.judged_count,
            "winning_score": self.winning_score,
            "runner_up_score": self.runner_up_score,
            "score_gap": self.score_gap,
            "scoring_method": self.scoring_method,
            "jury_result_refs": list(self.jury_result_refs),
            "gate_result_refs": list(self.gate_result_refs),
            "trace_root": self.trace_root,
            "otel_span_ref": self.otel_span_ref,
            "replay_key": self.replay_key,
            "selection_timestamp": self.selection_timestamp or self.receipt_timestamp,
            "receipt_timestamp": self.receipt_timestamp or self.selection_timestamp,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))
