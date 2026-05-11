"""Sealed workflow types — generic, app-agnostic contracts.

Phase 1.4 of apps-rg-ensemble-judge-restoration-a7c4e2.
W5 extended: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W5
  - SealedSectionArtifact: added artifact_id, workflow_ref, payload_ref,
    payload_digest, output_schema_ref, gate_result_refs, judge_result_refs,
    l2_trace_refs, terminal_class, decisive_reason.
  - SealedWorkflowPackage: added package_id, route_contract_ref,
    workflow_ref, workflow_manifest_ref, trace_root fields, section_artifact_refs,
    merged_payload_ref, merged_payload_digest, unresolved/skipped/failed node refs,
    workflow_budget_summary, dependency_graph_ref, telemetry_refs,
    runtime_gate_refs, terminal_class, decisive_reason, replay_manifest,
    audit_manifest_ref.
  All new fields default-empty; existing fields preserved for backward compat.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SealedSectionArtifact:
    """Final sealed output for one workflow node after selection.

    Produced by L2 after EnsembleSelectionReceipt determines the winner.
    L3 collects these to build the SealedWorkflowPackage.
    """

    # W5: explicit artifact identity
    artifact_id: str = ""
    workflow_ref: str = ""

    node_id: str = ""
    run_id: str = ""
    app_context: str = ""

    # Content — original fields
    sealed_content: str = ""
    content_digest: str = ""

    # W5: payload refs (alternative to inline sealed_content for large payloads)
    payload_ref: str = ""
    payload_digest: str = ""
    output_schema_ref: str = ""

    # Provenance
    selected_candidate_id: str = ""
    selection_receipt_ref: str = ""
    candidate_artifact_ref: str = ""

    # W5: gate / judge result refs
    gate_result_refs: tuple[str, ...] = field(default_factory=tuple)
    judge_result_refs: tuple[str, ...] = field(default_factory=tuple)
    l2_trace_refs: tuple[str, ...] = field(default_factory=tuple)

    # Execution metadata
    lane: str = "ENSEMBLE_MODEL"
    node_order: int = 0
    merge_order: int = 0

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""
    sealed_at: str = ""

    # W5: terminal classification
    terminal_class: str = ""   # e.g. "success" | "skipped" | "failed"
    decisive_reason: str = ""

    schema_version: str = "W5.a3f7e2"

    def as_dict(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "workflow_ref": self.workflow_ref,
            "node_id": self.node_id,
            "run_id": self.run_id,
            "app_context": self.app_context,
            "sealed_content": self.sealed_content,
            "content_digest": self.content_digest,
            "payload_ref": self.payload_ref,
            "payload_digest": self.payload_digest,
            "output_schema_ref": self.output_schema_ref,
            "selected_candidate_id": self.selected_candidate_id,
            "selection_receipt_ref": self.selection_receipt_ref,
            "candidate_artifact_ref": self.candidate_artifact_ref,
            "gate_result_refs": list(self.gate_result_refs),
            "judge_result_refs": list(self.judge_result_refs),
            "l2_trace_refs": list(self.l2_trace_refs),
            "lane": self.lane,
            "node_order": self.node_order,
            "merge_order": self.merge_order,
            "trace_root": self.trace_root,
            "otel_span_ref": self.otel_span_ref,
            "sealed_at": self.sealed_at,
            "terminal_class": self.terminal_class,
            "decisive_reason": self.decisive_reason,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class SealedWorkflowPackage:
    """Complete sealed output of a managed workflow.

    Assembled by L3 after all section nodes complete.
    Passed to Exit for final evaluation and X3 disposition.
    """

    # W5: explicit package identity
    package_id: str = ""
    route_contract_ref: str = ""
    workflow_ref: str = ""
    workflow_manifest_ref: str = ""

    workflow_id: str = ""
    run_id: str = ""
    app_context: str = ""

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""
    completed_at: str = ""

    # Sealed sections (ordered) — original field
    sealed_sections: tuple[SealedSectionArtifact, ...] = field(default_factory=tuple)
    section_count: int = 0

    # W5: section artifact refs (stable IDs for audit consumers)
    section_artifact_refs: tuple[str, ...] = field(default_factory=tuple)

    # Merged output — original fields
    merged_content: str = ""
    merged_content_digest: str = ""
    merge_strategy_ref: str = ""

    # W5: payload ref alternatives
    merged_payload_ref: str = ""
    merged_payload_digest: str = ""

    # W5: node execution summaries
    unresolved_node_refs: tuple[str, ...] = field(default_factory=tuple)
    skipped_node_refs: tuple[str, ...] = field(default_factory=tuple)
    failed_node_refs: tuple[str, ...] = field(default_factory=tuple)

    # Workflow execution summary — original fields
    total_candidates_generated: int = 0
    total_candidates_gated: int = 0
    total_judges_invoked: int = 0
    total_execution_duration_ms: int = 0

    # W5: budget / telemetry / audit
    workflow_budget_summary: str = ""    # serialised budget summary JSON
    dependency_graph_ref: str = ""       # serialised or ref to DAG used
    telemetry_refs: tuple[str, ...] = field(default_factory=tuple)
    runtime_gate_refs: tuple[str, ...] = field(default_factory=tuple)

    # W5: terminal classification
    terminal_class: str = ""
    decisive_reason: str = ""

    # W5: replay / audit manifests
    replay_manifest: str = ""            # serialised replay manifest JSON
    audit_manifest_ref: str = ""

    # Provenance — original fields
    workflow_spec_digest: str = ""
    manifest_digest: str = ""
    registry_digest_set: str = ""

    schema_version: str = "W5.a3f7e2"

    def as_dict(self) -> dict:
        return {
            "package_id": self.package_id,
            "route_contract_ref": self.route_contract_ref,
            "workflow_ref": self.workflow_ref,
            "workflow_manifest_ref": self.workflow_manifest_ref,
            "workflow_id": self.workflow_id,
            "run_id": self.run_id,
            "app_context": self.app_context,
            "trace_root": self.trace_root,
            "otel_span_ref": self.otel_span_ref,
            "completed_at": self.completed_at,
            "section_count": self.section_count,
            "section_artifact_refs": list(self.section_artifact_refs),
            "merged_content_digest": self.merged_content_digest,
            "merge_strategy_ref": self.merge_strategy_ref,
            "merged_payload_ref": self.merged_payload_ref,
            "merged_payload_digest": self.merged_payload_digest,
            "unresolved_node_refs": list(self.unresolved_node_refs),
            "skipped_node_refs": list(self.skipped_node_refs),
            "failed_node_refs": list(self.failed_node_refs),
            "total_candidates_generated": self.total_candidates_generated,
            "total_candidates_gated": self.total_candidates_gated,
            "total_judges_invoked": self.total_judges_invoked,
            "total_execution_duration_ms": self.total_execution_duration_ms,
            "workflow_budget_summary": self.workflow_budget_summary,
            "dependency_graph_ref": self.dependency_graph_ref,
            "telemetry_refs": list(self.telemetry_refs),
            "runtime_gate_refs": list(self.runtime_gate_refs),
            "terminal_class": self.terminal_class,
            "decisive_reason": self.decisive_reason,
            "replay_manifest": self.replay_manifest,
            "audit_manifest_ref": self.audit_manifest_ref,
            "workflow_spec_digest": self.workflow_spec_digest,
            "manifest_digest": self.manifest_digest,
            "registry_digest_set": self.registry_digest_set,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))
