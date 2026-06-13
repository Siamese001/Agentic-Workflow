"""Generalized spine contract envelopes.

Adapted from `apps_rg/runtime/contracts.py` by making `app_name` a plain
`str` (not `Literal["apps_rg"]`) and adding two optional receipt types
(`C0GroundingReceipt`, `PromptAssemblyManifest`) that apps_rg did not
need but other apps (apps_eval / apps_exec / apps_lic / apps_research /
) do, per `AppSpec.expects_c0_grounding` and
`AppSpec.expects_prompt_assembly`.

Contract identity is by JSON content, not Python class — two apps can
emit structurally-identical receipts via different class namespaces and
the verifier matches by `artifact_kind` in the manifest.

Plan: apps-e2e-spine-cert-wireup-e1c4d7 W1.1.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Common aliases (mirror apps_rg/runtime/contracts.py for consistency)
# ---------------------------------------------------------------------------

ExecutionForm = Literal[
    "MANAGED_WORKFLOW",
    "DETERMINISTIC_PIPELINE",
    "TERMINAL_SHORTCIRCUIT",
    "SINGLE_STEP",
    "FALLBACK",
]

X3Disposition = Literal[
    "EXIT_OK",
    "EXIT_PARTIAL",
    "EXIT_FAIL",
    "EXIT_ROLLBACK",
]

L3BypassReason = Literal[
    "TERMINAL_SHORTCIRCUIT",
    "SINGLE_STEP_ROUTE",
    "FALLBACK_RET",
    "NO_MANAGED_WORKFLOW_REQUIRED",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class _SpineEnvelope(BaseModel):
    """Common header — every receipt carries these fields."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    app_name: str
    run_id: str
    request_id: str
    trace_root: str
    emitted_at_utc: str = Field(default_factory=_utc_now)


# ---------------------------------------------------------------------------
# U0 / Intake
# ---------------------------------------------------------------------------


class U0IntakeEnvelope(_SpineEnvelope):
    intake_id: str
    entrypoint_command: str  # e.g. "python -m apps_exec"
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    cli_args_digest: str
    user_intent: str
    validated: bool = True


# ---------------------------------------------------------------------------
# L1 / Plan
# ---------------------------------------------------------------------------


class L1PlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step_id: str
    name: str
    kind: Literal["ingest", "transform", "render", "score", "retrieve", "assemble", "orchestrate"]
    optional: bool = False


class L1PlanContract(_SpineEnvelope):
    plan_id: str
    plan_kind: Literal[
        "deterministic_hop_pipeline",
        "managed_workflow",
        "single_step",
    ] = "deterministic_hop_pipeline"
    steps: list[L1PlanStep]
    grounding_required: bool = False
    prompt_assembly_required: bool = False
    estimated_wall_clock_s: Optional[float] = None
    plan_rationale: str


# ---------------------------------------------------------------------------
# L0 / Route
# ---------------------------------------------------------------------------


class RouteContract(_SpineEnvelope):
    route_contract_id: str
    route_id: str
    execution_form: ExecutionForm
    route_reason: str
    l3_required: bool
    static_dag_ref: Optional[str] = None
    static_dag_sha256: Optional[str] = None
    selected_capability: str


# ---------------------------------------------------------------------------
# L3 / Bypass receipt (SINGLE_STEP / DETERMINISTIC_PIPELINE path)
# ---------------------------------------------------------------------------


class L3BypassReceipt(_SpineEnvelope):
    l3_bypass_receipt_id: str
    route_contract_id: str
    execution_form: ExecutionForm
    l3_required: Literal[False] = False
    l3_bypass_reason: L3BypassReason
    static_dag_available: bool
    static_dag_ref: Optional[str] = None
    why_static_dag_not_used: str


# ---------------------------------------------------------------------------
# L3 / Runtime orchestration receipt (MANAGED_WORKFLOW path — apps_lic)
# ---------------------------------------------------------------------------


class L3OrchestrationReceipt(_SpineEnvelope):
    l3_runtime_receipt_id: str
    route_contract_id: str
    dag_id: str
    dag_sha256: str  # MUST equal the bundle's static_dag_sha256 (N6 guard)
    static_dag_hash: str  # explicit alias for the plan-canonical field name
    workflow_id: str
    execution_form: Literal["MANAGED_WORKFLOW"] = "MANAGED_WORKFLOW"
    selected_entry_node: str
    node_count: int
    scheduled_node_ids: list[str]
    ready_node_ids: list[str]
    step_contract_refs: list[str]
    checkpoint_refs: list[str] = Field(default_factory=list)
    retry_policy_ref: Optional[str] = None
    join_refs: list[str] = Field(default_factory=list)
    branch_refs: list[str] = Field(default_factory=list)
    sealed_workflow_package_ref: Optional[str] = None


# ---------------------------------------------------------------------------
# C0 / Grounding receipt (optional — apps_eval/apps_research/apps_lic)
# ---------------------------------------------------------------------------


class C0GroundingReceipt(_SpineEnvelope):
    """Canonical filename: `final_evidence_contract.json` (verifier keyword)."""
    c0_grounding_receipt_id: str
    route_contract_id: str
    retrieval_plan_id: str
    retrieval_backend: str  # e.g. "deterministic_fixture", "vector_db"
    evidence_count: int
    evidence_refs: list[str] = Field(default_factory=list)
    grounding_coverage: float = 1.0  # 0..1
    deterministic: bool = True
    sealed: bool = True


# ---------------------------------------------------------------------------
# Prompt Assembly manifest (optional — apps_eval/apps_exec/apps_research/apps_lic)
# ---------------------------------------------------------------------------


class PromptAssemblyManifest(_SpineEnvelope):
    """Canonical filename: `prompt_assembly_manifest.json` (verifier keyword)."""
    prompt_assembly_manifest_id: str
    route_contract_id: str
    assembly_strategy: Literal[
        "deterministic_template",
        "model_driven",
        "hybrid",
    ] = "deterministic_template"
    prompt_artifact_refs: list[str] = Field(default_factory=list)
    prompt_sha256_map: dict[str, str] = Field(default_factory=dict)
    assembly_note: str


# ---------------------------------------------------------------------------
# L2 / Execution receipt
# ---------------------------------------------------------------------------


class L2ExecutionReceipt(_SpineEnvelope):
    l2_receipt_id: str
    route_contract_id: str
    terminal_class: Literal["ok", "partial", "fail"]
    attempt_count: int = 1
    repair_count: int = 0
    output_artifact_refs: list[str]
    pipeline_stages_executed: list[str]
    wall_clock_s: float


# ---------------------------------------------------------------------------
# Exit / X3 disposition
# ---------------------------------------------------------------------------


class ExitReviewPacket(_SpineEnvelope):
    exit_review_packet_id: str
    route_contract_id: str
    x3_disposition: X3Disposition
    disposition_reason: str
    subprocess_exit_code: int
    failed_stages: list[str] = Field(default_factory=list)
    sealed: bool = True


# ---------------------------------------------------------------------------
# L6 / Runtime exhaust (post-exit observation bundle)
# ---------------------------------------------------------------------------


class RuntimeExhaustBundle(_SpineEnvelope):
    runtime_exhaust_bundle_id: str
    exit_review_packet_id: str
    observed_after_exit_at_utc: str  # MUST be >= ExitReviewPacket.emitted_at_utc (N7 guard)
    artifact_refs: list[str]
    artifact_sha256_map: dict[str, str]
    metric_summary: dict[str, Any] = Field(default_factory=dict)
    sealed: bool = True


# ---------------------------------------------------------------------------
# OTEL runtime trace (single artifact per run)
# ---------------------------------------------------------------------------


class OtelSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    span_id: str
    name: str
    started_at_utc: str
    finished_at_utc: str
    duration_ms: float
    attributes: dict[str, Any] = Field(default_factory=dict)
    status: Literal["OK", "ERROR"] = "OK"
    is_synthetic: bool = False


class OtelRuntimeTrace(_SpineEnvelope):
    trace_id: str
    spans: list[OtelSpan]
    span_count: int
    earliest_start_utc: str
    latest_finish_utc: str
    contains_synthetic_spans: bool = False


__all__ = [
    "ExecutionForm", "X3Disposition", "L3BypassReason",
    "U0IntakeEnvelope",
    "L1PlanStep", "L1PlanContract",
    "RouteContract",
    "L3BypassReceipt", "L3OrchestrationReceipt",
    "C0GroundingReceipt", "PromptAssemblyManifest",
    "L2ExecutionReceipt",
    "ExitReviewPacket",
    "RuntimeExhaustBundle",
    "OtelSpan", "OtelRuntimeTrace",
]
