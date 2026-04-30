"""Runtime artifact shape validators for the W4d-4 proof-evidence pilot.

Each validator asserts the *minimum* schema for the artifact named in the
ledger's ``runtime_artifact_expected`` column. The validators are
deliberately narrow — they enforce the field set, not the field contents.
They exist so a test can prove the artifact contract is honored even
before the runtime emits a real instance.

The five pilot REQs cover these artifact families:

  - REQ-049 -> ValidatedRequest         (U0 intake)
  - REQ-167 -> L5CertificationResult    (L5 policy plane)
  - REQ-086 -> CompiledPromptArtifact   (PA assembly)
  - REQ-089 -> ExecutionResult          (L2 sealed envelope)
  - REQ-122 -> CommitRequest            (UWG single-writer entry)
"""

from __future__ import annotations

from typing import Any, Mapping

# Field sets are sourced from the ledger's runtime_artifact_expected column
# plus the related mandatory OTEL attributes. Every field listed must be
# present in the dict-shaped record under test.
REQUIRED_FIELDS: Mapping[str, tuple[str, ...]] = {
    "ValidatedRequest": (
        "request_id",
        "session_id",
        "trace_root",
        "tenant",
        "transport",
        "ingress_envelope",
        "caller_scope_baseline",
        "ingress_time_utc",
        "owner_surface",
    ),
    "L5CertificationResult": (
        "certification_id",
        "certification_class",
        "policy_hash",
        "blueprint_hash",
        "evidence_refs",
        "owner_surface",
        "issued_at_utc",
        "is_runtime_disposition",  # MUST be False for L5
    ),
    "CompiledPromptArtifact": (
        "assembly_hash",
        "instruction_blocks",
        "evidence_refs",
        "citation_anchors",
        "contradiction_flags",
        "slot_order_hash",
        "owner_surface",
        "c0_resolved_before_u0",  # MUST be True for PA.2
    ),
    "ExecutionResult": (
        "execution_id",
        "blueprint_hash",
        "policy_hash",
        "tool_calls",
        "side_effects_proposed",  # PROPOSED only, never committed
        "replay_key",
        "owner_surface",
        "no_durable_commit_assertion",  # MUST be True for L2
        "no_hitl_invocation_assertion",  # MUST be True for L2
        "no_routing_assertion",  # MUST be True for L2
    ),
    "CommitRequest": (
        "commit_request_id",
        "writer_identity",
        "blueprint_hash",
        "policy_hash",
        "diff_payload_hash",
        "serial_seqno",  # strictly serialized write queue
        "owner_surface",
        "single_writer_attestation",  # MUST be True for UWG
    ),
}


class ArtifactShapeError(AssertionError):
    """Raised when a runtime artifact violates its required-field set."""


def validate_artifact_shape(artifact_type: str, record: Mapping[str, Any]) -> None:
    """Validate that ``record`` has every field required for ``artifact_type``.

    Raises ArtifactShapeError on missing fields. Returns None on success.
    """
    if artifact_type not in REQUIRED_FIELDS:
        raise ArtifactShapeError(
            f"unknown artifact_type '{artifact_type}'; known: {sorted(REQUIRED_FIELDS)}"
        )
    if not isinstance(record, Mapping):
        raise ArtifactShapeError(
            f"{artifact_type}: record must be a Mapping, got {type(record).__name__}"
        )
    missing = [f for f in REQUIRED_FIELDS[artifact_type] if f not in record]
    if missing:
        raise ArtifactShapeError(
            f"{artifact_type} missing required fields: {missing}"
        )


# Boundary-invariant assertions. Each takes a validated record and raises
# if the record violates a constitutional invariant for its surface.

def assert_l5_is_certification_only(record: Mapping[str, Any]) -> None:
    """L5 MUST NOT emit live runtime dispositions (constitutional rule)."""
    if record.get("is_runtime_disposition") is not False:
        raise ArtifactShapeError(
            "L5CertificationResult.is_runtime_disposition must be False; "
            "L5 emits certification evidence, never live ALLOW/DENY"
        )


def assert_pa_c0_before_u0(record: Mapping[str, Any]) -> None:
    """PA.2 MUST resolve C0 evidence before U0 user content (slot order)."""
    if record.get("c0_resolved_before_u0") is not True:
        raise ArtifactShapeError(
            "CompiledPromptArtifact.c0_resolved_before_u0 must be True; "
            "PA.2 invariant: evidence slots resolve before user content"
        )


def assert_l2_no_authority_leak(record: Mapping[str, Any]) -> None:
    """L2 MUST NOT route, escalate to HITL, or commit durably."""
    for flag in (
        "no_durable_commit_assertion",
        "no_hitl_invocation_assertion",
        "no_routing_assertion",
    ):
        if record.get(flag) is not True:
            raise ArtifactShapeError(
                f"ExecutionResult.{flag} must be True; "
                f"L2 invariant: no routing, no HITL, no durable commit"
            )


def assert_uwg_single_writer(record: Mapping[str, Any]) -> None:
    """UWG MUST be single-writer-with-pen with monotonic serial_seqno."""
    if record.get("single_writer_attestation") is not True:
        raise ArtifactShapeError(
            "CommitRequest.single_writer_attestation must be True; "
            "UWG invariant: only one clerk with master pen"
        )
    seqno = record.get("serial_seqno")
    if not isinstance(seqno, int) or seqno < 0:
        raise ArtifactShapeError(
            f"CommitRequest.serial_seqno must be a non-negative int, got {seqno!r}"
        )


def assert_u0_no_authority_leak(record: Mapping[str, Any]) -> None:
    """U0 MUST NOT carry semantic-routing / L1-planning / C0-retrieval state."""
    forbidden_keys = (
        "route_id",
        "plan_proposal",
        "retrieval_results",
        "execution_intent",
        "hitl_decision",
        "durable_commit_intent",
    )
    leaked = [k for k in forbidden_keys if k in record]
    if leaked:
        raise ArtifactShapeError(
            f"ValidatedRequest carries forbidden L1/L0/C0/L2/L5/UWG keys "
            f"in U0 surface: {leaked}; U0 owns identity/transport/schema only"
        )
