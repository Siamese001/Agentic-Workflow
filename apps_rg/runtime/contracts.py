"""apps_rg spine contract envelopes.

One pydantic model per stage receipt. Field names mirror the user's e2e
proof spec verbatim. Each contract carries the same ``run_id`` so the
verifier can prove the run is end-to-end, not stitched from separate
runs.

Why local schemas instead of agentic_core's canonical types: the
agentic_core L0/L1/L3/L5 contract families have multiple competing
doctrine versions (v6, v7, v33, v43) with rich nested types. apps_rg
attesting its own runtime governance with a flat receipt is honest and
decoupled from doctrine churn. The receipts are still real contracts —
schema-validated, hash-bound, run_id-threaded — just locally scoped.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Common
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

    app_name: Literal["apps_rg"] = "apps_rg"
    run_id: str
    request_id: str
    trace_root: str
    emitted_at_utc: str = Field(default_factory=_utc_now)


# ---------------------------------------------------------------------------
# U0 / Intake
# ---------------------------------------------------------------------------


class U0IntakeEnvelope(_SpineEnvelope):
    intake_id: str
    entrypoint_command: Literal["python -m apps_rg"] = "python -m apps_rg"
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    cli_args_digest: str  # SHA-256 of the canonicalized CLI args
    user_intent: str  # one-line human-readable summary
    validated: bool = True


# ---------------------------------------------------------------------------
# L1 / Plan
# ---------------------------------------------------------------------------


class L1PlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step_id: str
    name: str
    kind: Literal["ingest", "transform", "render", "score"]
    optional: bool = False


class L1PlanContract(_SpineEnvelope):
    plan_id: str
    plan_kind: Literal["deterministic_hop_pipeline"] = "deterministic_hop_pipeline"
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
    selected_capability: str = "apps_rg.resume_generation_v1"


# ---------------------------------------------------------------------------
# L3 / Bypass receipt (apps_rg always uses this — never managed workflow)
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
# L3 / Runtime orchestration receipt (kept for forward-compat; not used today)
# ---------------------------------------------------------------------------


class L3OrchestrationReceipt(_SpineEnvelope):
    l3_runtime_receipt_id: str
    route_contract_id: str
    dag_id: str
    dag_sha256: str
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
    observed_after_exit_at_utc: str
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
    is_synthetic: bool = False  # MUST be False for certifying spans


class OtelRuntimeTrace(_SpineEnvelope):
    trace_id: str
    spans: list[OtelSpan]
    span_count: int
    earliest_start_utc: str
    latest_finish_utc: str
    contains_synthetic_spans: bool = False
