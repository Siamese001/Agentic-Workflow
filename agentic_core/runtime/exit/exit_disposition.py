"""ExitDispositionReceipt — W8 Exit contract.

W8 plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

X3 codes:
  X3A_DENY_REROUTE          — hard FAIL; reroute or deny
  X3B_ESCALATE_HITL         — material UNKNOWN or anomaly; human review
  X3C_COMMIT_REQUEST_TO_UWG — durable write requested + G27/G28 satisfied
  X3D_ALLOW_FINISH          — all required gates passed; no blockers
  X3E_SAFE_ABSTAIN          — cannot evaluate safely; safe abstention

Invariants:
- Exactly one x3_code per disposition.
- Exit does NOT write L4, cache, vector store, or evidence index.
- Exit does NOT call providers.
- GateMeshResult REQUIRED before any X3 except X3E.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ── X3 disposition codes ──────────────────────────────────────────────────────

X3A_DENY_REROUTE = "X3A_DENY_REROUTE"
X3B_ESCALATE_HITL = "X3B_ESCALATE_HITL"
X3C_COMMIT_REQUEST_TO_UWG = "X3C_COMMIT_REQUEST_TO_UWG"
X3D_ALLOW_FINISH = "X3D_ALLOW_FINISH"
X3E_SAFE_ABSTAIN = "X3E_SAFE_ABSTAIN"

ALL_X3_CODES = frozenset({
    X3A_DENY_REROUTE,
    X3B_ESCALATE_HITL,
    X3C_COMMIT_REQUEST_TO_UWG,
    X3D_ALLOW_FINISH,
    X3E_SAFE_ABSTAIN,
})

EXIT_DISPOSITION_SCHEMA_VERSION = "W8.a3f7e2"


@dataclass(frozen=True, slots=True)
class ExitDispositionReceipt:
    """Canonical output of the exit gate harness.

    Contains exactly one x3_code and the decisive gate blockers.
    Does NOT write to any durable store.
    """

    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    app_id: str = ""
    task_class: str = ""

    # The single X3 disposition — exactly one per request
    x3_code: str = X3E_SAFE_ABSTAIN

    # Why this X3 was chosen
    decisive_reason: str = ""
    decisive_blocker_gate_ids: tuple[str, ...] = field(default_factory=tuple)
    decisive_blocker_codes: tuple[str, ...] = field(default_factory=tuple)

    # Gate mesh summary
    gate_mesh_result_ref: str = ""
    required_gates_passed: bool = False
    hard_fail_count: int = 0
    unknown_count: int = 0
    warn_count: int = 0
    missing_gate_count: int = 0

    # Commit path (X3C only)
    commit_request_ref: str = ""
    uwg_path_evidence_ref: str = ""

    # Downstream refs
    sealed_workflow_package_ref: str = ""
    output_artifact_digest: str = ""
    workflow_ref: str = ""

    # Provenance
    exit_profile_ref: str = ""
    policy_hash: str = ""
    deterministic_digest: str = ""

    created_at: str = ""
    schema_version: str = EXIT_DISPOSITION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.x3_code not in ALL_X3_CODES:
            raise ValueError(
                f"ExitDispositionReceipt: invalid x3_code={self.x3_code!r}. "
                f"Must be one of {sorted(ALL_X3_CODES)}"
            )

    @property
    def allows_finish(self) -> bool:
        return self.x3_code == X3D_ALLOW_FINISH

    @property
    def is_deny(self) -> bool:
        return self.x3_code == X3A_DENY_REROUTE

    @property
    def is_hitl(self) -> bool:
        return self.x3_code == X3B_ESCALATE_HITL

    @property
    def is_commit(self) -> bool:
        return self.x3_code == X3C_COMMIT_REQUEST_TO_UWG

    def as_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "app_id": self.app_id,
            "task_class": self.task_class,
            "x3_code": self.x3_code,
            "decisive_reason": self.decisive_reason,
            "decisive_blocker_gate_ids": list(self.decisive_blocker_gate_ids),
            "decisive_blocker_codes": list(self.decisive_blocker_codes),
            "gate_mesh_result_ref": self.gate_mesh_result_ref,
            "required_gates_passed": self.required_gates_passed,
            "hard_fail_count": self.hard_fail_count,
            "unknown_count": self.unknown_count,
            "warn_count": self.warn_count,
            "missing_gate_count": self.missing_gate_count,
            "commit_request_ref": self.commit_request_ref,
            "uwg_path_evidence_ref": self.uwg_path_evidence_ref,
            "sealed_workflow_package_ref": self.sealed_workflow_package_ref,
            "output_artifact_digest": self.output_artifact_digest,
            "workflow_ref": self.workflow_ref,
            "exit_profile_ref": self.exit_profile_ref,
            "policy_hash": self.policy_hash,
            "deterministic_digest": self.deterministic_digest,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


# ── ExitReviewPacket — X1+X2+X3 summary ─────────────────────────────────────

@dataclass(frozen=True, slots=True)
class ExitReviewPacket:
    """Review packet from Exit — contains X1, X2, gate summary.

    Does NOT write to any durable store.
    """
    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    app_id: str = ""
    task_class: str = ""
    input_type: str = ""
    x1_checkout_result: "X1CheckoutResult" = field(default_factory=lambda: X1CheckoutResult())
    x2_aggregation_result: "X2AggregationResult" = field(default_factory=lambda: X2AggregationResult())
    gate_mesh_summary: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    schema_version: str = EXIT_DISPOSITION_SCHEMA_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "app_id": self.app_id,
            "task_class": self.task_class,
            "input_type": self.input_type,
            "x1_checkout_result": self.x1_checkout_result.as_dict(),
            "x2_aggregation_result": self.x2_aggregation_result.as_dict(),
            "gate_mesh_summary": self.gate_mesh_summary,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }


# ── X1CheckoutResult — Today’s Rules, Answered It, Safe to Leave, etc. ──────

@dataclass(frozen=True, slots=True)
class X1CheckoutResult:
    """Result of X1 checkout — 10 required checks.

    Invariants:
    - UNKNOWN is never PASS
    - NOT_APPLICABLE requires reason
    """
    checks: dict[str, Any] = field(default_factory=dict)
    overall_pass: bool = False
    blockers: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "checks": self.checks,
            "overall_pass": self.overall_pass,
            "blockers": self.blockers,
        }


# ── X2AggregationResult — Gate verdicts + evidence + trajectory ─────────────

@dataclass(frozen=True, slots=True)
class X2AggregationResult:
    """Result of X2 aggregation — rolls up gate verdicts and metrics.

    Invariants:
    - UNKNOWN is never PASS
    """
    gate_verdicts: dict[str, list[str]] = field(default_factory=dict)
    evidence_quality_score: float = 0.0
    trajectory_metrics: dict[str, Any] = field(default_factory=dict)
    x1_integration: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate_verdicts": self.gate_verdicts,
            "evidence_quality_score": self.evidence_quality_score,
            "trajectory_metrics": self.trajectory_metrics,
            "x1_integration": self.x1_integration,
        }


# ── RuntimeExhaustBundle placeholder ─────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class RuntimeExhaustBundle:
    """Minimal inert placeholder — L6 writeback is NOT W8 scope.

    Carries exit disposition ref for downstream consumers.
    Does NOT write to any durable store.
    """

    run_id: str = ""
    trace_root: str = ""
    route_contract_ref: str = ""
    sealed_result_ref: str = ""
    exit_disposition_ref: str = ""
    gate_mesh_result_ref: str = ""
    learning_profile_ref: str = ""   # optional
    writeback_candidates: list[str] = field(default_factory=list)  # Deferred to L6/UWG
    created_after_exit: bool = True

    schema_version: str = EXIT_DISPOSITION_SCHEMA_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "route_contract_ref": self.route_contract_ref,
            "sealed_result_ref": self.sealed_result_ref,
            "exit_disposition_ref": self.exit_disposition_ref,
            "gate_mesh_result_ref": self.gate_mesh_result_ref,
            "learning_profile_ref": self.learning_profile_ref,
            "writeback_candidates": self.writeback_candidates,
            "created_after_exit": self.created_after_exit,
            "schema_version": self.schema_version,
        }
