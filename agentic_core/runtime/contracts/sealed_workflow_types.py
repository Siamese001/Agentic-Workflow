"""Sealed workflow types — generic, app-agnostic contracts.

Phase 1.4 of apps-rg-ensemble-judge-restoration-a7c4e2.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SealedSectionArtifact:
    """Final sealed output for one workflow node after selection.

    Produced by L2 after EnsembleSelectionReceipt determines the winner.
    L3 collects these to build the SealedWorkflowPackage.
    """

    node_id: str = ""
    run_id: str = ""
    app_context: str = ""

    # Content
    sealed_content: str = ""
    content_digest: str = ""

    # Provenance
    selected_candidate_id: str = ""
    selection_receipt_ref: str = ""
    candidate_artifact_ref: str = ""

    # Execution metadata
    lane: str = "ENSEMBLE_MODEL"
    node_order: int = 0
    merge_order: int = 0

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""
    sealed_at: str = ""

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class SealedWorkflowPackage:
    """Complete sealed output of a managed workflow.

    Assembled by L3 after all section nodes complete.
    Passed to Exit for final evaluation and X3 disposition.
    """

    workflow_id: str = ""
    run_id: str = ""
    app_context: str = ""

    # Sealed sections (ordered)
    sealed_sections: tuple[SealedSectionArtifact, ...] = field(default_factory=tuple)
    section_count: int = 0

    # Merged output
    merged_content: str = ""
    merged_content_digest: str = ""
    merge_strategy_ref: str = ""

    # Workflow execution summary
    total_candidates_generated: int = 0
    total_candidates_gated: int = 0
    total_judges_invoked: int = 0
    total_execution_duration_ms: int = 0

    # Provenance
    workflow_spec_digest: str = ""
    manifest_digest: str = ""
    registry_digest_set: str = ""

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""
    completed_at: str = ""

    schema_version: str = "1.0"
