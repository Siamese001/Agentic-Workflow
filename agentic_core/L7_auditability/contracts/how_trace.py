"""Typed HOW trace contract for L7_AUDITABILITY.

The HOW trace is a thin projection over already-emitted chain artifacts.
It captures, for each spine stage:

    - what ran, was bypassed, was structural-only, was not applicable,
      or failed
    - the artifact refs that prove the claim
    - the forbidden-action assertions L7 imposes on that stage
    - the run/request/trace identity carried through

The HOW trace is hash-bound back to the source artifacts; verifiers
fail-closed if status, ref, identity continuity, or stage coverage is
violated.

L7_AUDITABILITY may observe, collect refs, hash, verify, emit evidence,
and fail closed.  L7_AUDITABILITY MUST NOT route, retrieve, assemble
prompts, orchestrate, execute tools/models, judge final output, mutate
current run, or write L4.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Final, Literal, Mapping

HOW_TRACE_SCHEMA_VERSION: Final[str] = "1.1"
RUNTIME_SUBJECT: Final[str] = "agentic_core"
EVIDENCE_PLANE: Final[str] = "L7_AUDITABILITY"
EVIDENCE_PLANE_MODE: Final[str] = "cross_cutting_non_mutating"

StageId = Literal[
    "U0_INTAKE",
    "L1_PLAN",
    "L0_ROUTE",
    "C0_CONTEXT",
    "PROMPT_ASSEMBLY",
    "L3_ORCHESTRATION",
    "L2_EXECUTE",
    "EXIT_X3",
    "UWG_L4",
    "L6_RUNTIME_EXHAUST",
]

ALLOWED_STAGE_IDS: Final[tuple[StageId, ...]] = (
    "U0_INTAKE",
    "L1_PLAN",
    "L0_ROUTE",
    "C0_CONTEXT",
    "PROMPT_ASSEMBLY",
    "L3_ORCHESTRATION",
    "L2_EXECUTE",
    "EXIT_X3",
    "UWG_L4",
    "L6_RUNTIME_EXHAUST",
)

StageStatus = Literal[
    "RAN",
    "BYPASSED",
    "STRUCTURAL_ONLY",
    "NOT_APPLICABLE",
    "FAILED",
]

ALLOWED_STAGE_STATUSES: Final[frozenset[str]] = frozenset(
    ("RAN", "BYPASSED", "STRUCTURAL_ONLY", "NOT_APPLICABLE", "FAILED")
)

SubStageStatus = Literal[
    "PASS",
    "FAIL",
    "WARN",
    "UNKNOWN",
    "NOT_APPLICABLE",
    "BYPASSED",
]


@dataclass(frozen=True)
class SubStageRecord:
    """One sub-stage record inside a HowTraceStage.

    Captures fine-grained execution detail: which sub-gate/step ran,
    its outcome, timing, and optional metadata (score, threshold, etc.).
    """

    sub_stage_id: str
    sub_stage_name: str
    status: SubStageStatus
    duration_ms: float = 0.0
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sub_stage_id": self.sub_stage_id,
            "sub_stage_name": self.sub_stage_name,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "meta": self.meta,
        }


@dataclass(frozen=True)
class HowTraceStage:
    """One stage record inside a HOW trace.

    Every stage carries identity continuity (run_id/request_id/trace_root)
    and a list of forbidden-action assertions L7 imposes on that stage.

    A stage marked ``RAN`` MUST have at least one ``output_artifact_ref``.
    A stage marked ``BYPASSED`` MUST have a ``bypass_reason`` and a
    bypass artifact ref.  A stage marked ``STRUCTURAL_ONLY`` MUST have
    a ``structural_only_reason``.
    """

    stage_id: StageId
    stage_name: str
    status: StageStatus
    run_id: str
    request_id: str
    trace_root: str
    route_id: str
    route_contract_id: str
    input_artifact_refs: tuple[str, ...]
    output_artifact_refs: tuple[str, ...]
    verifier_refs: tuple[str, ...]
    why_ran_or_bypassed: str
    forbidden_action_assertions: tuple[Mapping[str, Any], ...]
    hash_bound: bool
    blocking_gaps: tuple[str, ...] = ()
    bypass_reason: str = ""
    structural_only_reason: str = ""
    sub_stages: tuple[SubStageRecord, ...] = ()

    def __post_init__(self) -> None:  # noqa: D401
        if self.stage_id not in ALLOWED_STAGE_IDS:
            raise ValueError(
                f"HowTraceStage.stage_id must be one of "
                f"{ALLOWED_STAGE_IDS}; got {self.stage_id!r}"
            )
        if self.status not in ALLOWED_STAGE_STATUSES:
            raise ValueError(
                f"HowTraceStage.status must be one of "
                f"{sorted(ALLOWED_STAGE_STATUSES)}; got {self.status!r}"
            )
        for name in (
            "stage_name", "run_id", "request_id", "trace_root",
            "route_id", "route_contract_id", "why_ran_or_bypassed",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"HowTraceStage.{name} must be non-empty string"
                )
        if self.status == "BYPASSED" and not self.bypass_reason:
            raise ValueError(
                f"HowTraceStage[{self.stage_id}]: BYPASSED requires bypass_reason"
            )
        if self.status == "STRUCTURAL_ONLY" and not self.structural_only_reason:
            raise ValueError(
                f"HowTraceStage[{self.stage_id}]: STRUCTURAL_ONLY requires "
                f"structural_only_reason"
            )
        if self.status == "RAN" and not self.output_artifact_refs:
            raise ValueError(
                f"HowTraceStage[{self.stage_id}]: RAN requires at least one "
                f"output_artifact_ref"
            )
        if not isinstance(self.forbidden_action_assertions, tuple):
            raise ValueError(
                "HowTraceStage.forbidden_action_assertions must be a tuple"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "status": self.status,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "route_id": self.route_id,
            "route_contract_id": self.route_contract_id,
            "input_artifact_refs": list(self.input_artifact_refs),
            "output_artifact_refs": list(self.output_artifact_refs),
            "verifier_refs": list(self.verifier_refs),
            "why_ran_or_bypassed": self.why_ran_or_bypassed,
            "bypass_reason": self.bypass_reason,
            "structural_only_reason": self.structural_only_reason,
            "forbidden_action_assertions": [
                dict(a) for a in self.forbidden_action_assertions
            ],
            "hash_bound": self.hash_bound,
            "blocking_gaps": list(self.blocking_gaps),
            "sub_stages": [s.to_dict() for s in self.sub_stages],
        }


@dataclass(frozen=True)
class HowTrace:
    """Mandatory L7_AUDITABILITY HOW trace for one governed runtime run.

    Emitted as ``agentic_core_how_trace.json`` in the integrated-runtime
    artifact directory.  Every spine stage gets exactly one stage record.
    The trace is hash-bound to the spine_proof_bundle and the artifact
    manifest by ref+sha256.
    """

    schema_version: str
    runtime_subject: str
    evidence_plane: str
    evidence_plane_mode: str
    run_id: str
    request_id: str
    trace_root: str
    route_id: str
    route_contract_id: str
    execution_form: str
    chain_kind: str
    runtime_mode: str
    audit_mode: str
    mock_mode_detected: bool
    fixture_mode_detected: bool
    synthetic_trace_detected: bool
    stages: tuple[HowTraceStage, ...]
    artifact_manifest_ref: str
    artifact_manifest_sha256: str
    spine_proof_bundle_ref: str
    spine_proof_bundle_sha256: str
    deterministic_digest: str
    success: bool
    blocking_gaps: tuple[str, ...] = ()
    verifier_results_ref: str = ""
    app_recipe_execution: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:  # noqa: D401
        if self.schema_version != HOW_TRACE_SCHEMA_VERSION:
            raise ValueError(
                f"HowTrace.schema_version must be {HOW_TRACE_SCHEMA_VERSION!r}"
            )
        if self.runtime_subject != RUNTIME_SUBJECT:
            raise ValueError(
                f"HowTrace.runtime_subject must be {RUNTIME_SUBJECT!r}"
            )
        if self.evidence_plane != EVIDENCE_PLANE:
            raise ValueError(
                f"HowTrace.evidence_plane must be {EVIDENCE_PLANE!r}"
            )
        if self.evidence_plane_mode != EVIDENCE_PLANE_MODE:
            raise ValueError(
                f"HowTrace.evidence_plane_mode must be {EVIDENCE_PLANE_MODE!r}"
            )
        if not isinstance(self.stages, tuple):
            raise ValueError("HowTrace.stages must be a tuple")
        seen: set[str] = set()
        for s in self.stages:
            if s.stage_id in seen:
                raise ValueError(
                    f"HowTrace.stages: duplicate stage_id {s.stage_id!r}"
                )
            seen.add(s.stage_id)
        missing = set(ALLOWED_STAGE_IDS) - seen
        if missing:
            raise ValueError(
                f"HowTrace.stages: missing required stage_ids "
                f"{sorted(missing)}"
            )
        for stage in self.stages:
            if (
                stage.run_id != self.run_id
                or stage.request_id != self.request_id
                or stage.trace_root != self.trace_root
            ):
                raise ValueError(
                    f"HowTrace.stages[{stage.stage_id}]: identity mismatch "
                    f"(run_id/request_id/trace_root must match envelope)"
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "runtime_subject": self.runtime_subject,
            "evidence_plane": self.evidence_plane,
            "evidence_plane_mode": self.evidence_plane_mode,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "route_id": self.route_id,
            "route_contract_id": self.route_contract_id,
            "execution_form": self.execution_form,
            "chain_kind": self.chain_kind,
            "runtime_mode": self.runtime_mode,
            "audit_mode": self.audit_mode,
            "mock_mode_detected": self.mock_mode_detected,
            "fixture_mode_detected": self.fixture_mode_detected,
            "synthetic_trace_detected": self.synthetic_trace_detected,
            "stages": [s.to_dict() for s in self.stages],
            "artifact_manifest_ref": self.artifact_manifest_ref,
            "artifact_manifest_sha256": self.artifact_manifest_sha256,
            "spine_proof_bundle_ref": self.spine_proof_bundle_ref,
            "spine_proof_bundle_sha256": self.spine_proof_bundle_sha256,
            "verifier_results_ref": self.verifier_results_ref,
            "deterministic_digest": self.deterministic_digest,
            "success": self.success,
            "blocking_gaps": list(self.blocking_gaps),
            "app_recipe_execution": self.app_recipe_execution,
        }


def compute_how_trace_digest(payload: Mapping[str, Any]) -> str:
    """Deterministic sha256 digest over canonical-JSON of the HOW trace."""
    body = {k: v for k, v in payload.items() if k != "deterministic_digest"}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(blob.encode('utf-8')).hexdigest()}"


__all__ = [
    "ALLOWED_STAGE_IDS",
    "ALLOWED_STAGE_STATUSES",
    "EVIDENCE_PLANE",
    "EVIDENCE_PLANE_MODE",
    "HOW_TRACE_SCHEMA_VERSION",
    "HowTrace",
    "HowTraceStage",
    "RUNTIME_SUBJECT",
    "StageId",
    "StageStatus",
    "SubStageRecord",
    "SubStageStatus",
    "compute_how_trace_digest",
]
