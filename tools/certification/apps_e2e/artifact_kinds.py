"""ArtifactKind enum for the apps_e2e two-gate certification harness.

Plan: apps-e2e-two-gate-certification-d8b3a1 §6.5

Every `*_ref` declared in a proof bundle MUST resolve to an artifact-manifest
row carrying `{ref_field, artifact_kind, path, sha256, run_id}`. Strict mode
fails if a required kind is missing, duplicated against a single-occurrence
slot, or mismatched against the slot it occupies.
"""
from __future__ import annotations

from enum import Enum


class ArtifactKind(str, Enum):
    """Stable identifiers for every artifact a proof bundle can reference.

    Inherits from `str` (not StrEnum) for Python 3.10 compatibility while
    keeping `ArtifactKind.route_contract == "route_contract"` true.
    """

    # Spine receipts (single-occurrence — exactly one per bundle for cert).
    route_contract = "route_contract"
    l1_plan_contract = "l1_plan_contract"
    l3_runtime_receipt = "l3_runtime_receipt"
    l3_bypass_receipt = "l3_bypass_receipt"
    exit_x3_disposition = "exit_x3_disposition"
    runtime_exhaust_bundle = "runtime_exhaust_bundle"

    # Trace surfaces (otel_or_runtime_trace_ref slot accepts EITHER).
    otel_trace = "otel_trace"
    runtime_adg_trace = "runtime_adg_trace"

    # Optional spine surfaces (per-spec required flags).
    c0_grounding_receipt = "c0_grounding_receipt"
    prompt_assembly_receipt = "prompt_assembly_receipt"
    l2_sealed_artifact = "l2_sealed_artifact"
    uwg_durable_write_receipt = "uwg_durable_write_receipt"

    # Static / housekeeping artifacts.
    static_l3_dag_proof = "static_l3_dag_proof"
    runtime_intake = "runtime_intake"
    run_log = "run_log"
    adg_snapshot = "adg_snapshot"
    verifier_result = "verifier_result"

    @classmethod
    def values(cls) -> frozenset[str]:
        return frozenset(member.value for member in cls)


# Single-occurrence kinds — strict mode rejects two manifest rows with
# the same value. Trace kinds are NOT single-occurrence because a slot
# may contain either OTEL or runtime-ADG.
SINGLE_OCCURRENCE_KINDS: frozenset[ArtifactKind] = frozenset({
    ArtifactKind.route_contract,
    ArtifactKind.l1_plan_contract,
    ArtifactKind.l3_runtime_receipt,
    ArtifactKind.l3_bypass_receipt,
    ArtifactKind.exit_x3_disposition,
    ArtifactKind.runtime_exhaust_bundle,
})


# The trace slot accepts either kind. Anything else in that slot is a failure.
TRACE_SLOT_KINDS: frozenset[ArtifactKind] = frozenset({
    ArtifactKind.otel_trace,
    ArtifactKind.runtime_adg_trace,
})


__all__ = [
    "ArtifactKind",
    "SINGLE_OCCURRENCE_KINDS",
    "TRACE_SLOT_KINDS",
]
