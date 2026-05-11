"""Ensemble execution types — generic, app-agnostic contracts.

Phase 1.1 of apps-rg-ensemble-judge-restoration-a7c4e2.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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

    # Generation metadata
    generated_content: str = ""
    model_ref: str = ""
    temperature: float = 0.0
    prompt_profile_digest: str = ""
    provider_receipt_ref: str = ""

    # Timing
    generation_timestamp: str = ""
    generation_duration_ms: int = 0

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""
    replay_key: str = ""

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class EnsembleSelectionReceipt:
    """Records which candidate won selection for a node and why.

    Produced by L2 after judge jury completes scoring.
    """

    node_id: str = ""
    run_id: str = ""
    app_context: str = ""

    # Selection outcome
    selected_candidate_id: str = ""
    selection_reason: str = ""  # e.g. "highest_jury_score", "sole_survivor"

    # Candidate pool summary
    total_candidates: int = 0
    candidates_passed_gates: int = 0
    candidates_scored: int = 0

    # Scoring summary
    winning_score: float = 0.0
    runner_up_score: float = 0.0
    score_gap: float = 0.0
    scoring_method: str = ""  # e.g. "weighted_jury_average"

    # Judge refs
    jury_result_refs: tuple[str, ...] = field(default_factory=tuple)
    gate_result_refs: tuple[str, ...] = field(default_factory=tuple)

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""
    replay_key: str = ""
    selection_timestamp: str = ""

    schema_version: str = "1.0"
