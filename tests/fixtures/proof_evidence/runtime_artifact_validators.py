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
    # --- Wave 1 additions (24 CRITICAL NEEDS_PROOF rows) ---
    "ChunkSealedEnvelope": (
        # Offline ingestion: REQ-005, REQ-163. Metadata MUST be bound BEFORE
        # embedding (constitutional ingestion invariant).
        "chunk_id",
        "tenant_id",
        "acl",
        "confidentiality_tier",
        "freshness_band",
        "effective_date",
        "expiry_date",
        "embedding_schema_version",
        "embedding_emitted",  # MUST be False until metadata-bound
        "metadata_bound_before_embedding",  # MUST be True
        "owner_surface",
    ),
    "L1PlanContract": (
        # L1 plan output: REQ-064, REQ-074. L1 produces notepad plan only,
        # no execution / no retrieval / no routing.
        "proposed_route",
        "query_spec",
        "task_spec",
        "route_risk",
        "confidence",
        "grounding_required",
        "declared_assumptions",
        "unresolved_gaps",
        "no_execution_assertion",  # MUST be True
        "no_retrieval_assertion",  # MUST be True
        "no_routing_assertion",    # MUST be True
        "owner_surface",
    ),
    "RouteContract": (
        # L0 route decision: REQ-075. Pre-routing gate must check ACL +
        # region + confidentiality + dates + bind policy with pre-filter.
        "route_id",
        "route_class",
        "decision_record_id",
        "tenant_acl_checked",        # MUST be True
        "region_checked",             # MUST be True
        "confidentiality_checked",    # MUST be True
        "effective_dates_checked",    # MUST be True
        "freshness_band_checked",     # MUST be True
        "policy_bound",               # MUST be True
        "single_route_per_request",   # MUST be True (no multi-route emission)
        "owner_surface",
    ),
    "X3DispositionPacket": (
        # Exit control: REQ-099. Disposition must be from explicit set,
        # no silent fallback / no hidden commit / no ungated human mod.
        "disposition_id",
        "disposition",  # MUST be in {ALLOW, DENY, RETURN, ESCALATE_TO_HITL, COMMIT_TO_UWG}
        "owner_surface",
        "no_silent_fallback_assertion",     # MUST be True
        "no_hidden_commit_path_assertion",  # MUST be True
        "no_ungated_human_mod_assertion",   # MUST be True
        "single_disposition_per_request",   # MUST be True
    ),
    "L6EvalRecord": (
        # L6 shadow eval: REQ-191. Replay-tied, no current-run mutation.
        "eval_record_id",
        "owner_surface",
        "is_shadow",  # MUST be True (or replay-only)
        "no_current_run_mutation_assertion",  # MUST be True
        "judge_calibrated",  # MUST be True (calibration provenance)
        "replay_tied",       # MUST be True
        "calibration_age_days",  # MUST be int and within budget
    ),
    "OtelTraceAuditRecord": (
        # Cross-cutting OTEL: REQ-165, REQ-166. Replay-key audit + W3C
        # TraceContext propagation. Every span must carry replay_key, owner
        # surface; all decisions must be reachable from a trace.
        "trace_id",
        "replay_key",
        "owner_surface",
        "w3c_traceparent",
        "w3c_tracestate",
        "replay_key_audit_present",  # MUST be True
        "policy_hash",
        "blueprint_hash",
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


# ---------------------------------------------------------------------------
# Wave 1 additions: 6 boundary-invariant helpers for the 24 CRITICAL rows
# ---------------------------------------------------------------------------

def assert_chunk_metadata_bound_before_embedding(record: Mapping[str, Any]) -> None:
    """Ingestion MUST bind ACL/tenant/confidentiality/freshness BEFORE embedding."""
    if record.get("metadata_bound_before_embedding") is not True:
        raise ArtifactShapeError(
            "ChunkSealedEnvelope.metadata_bound_before_embedding must be True; "
            "constitutional ingestion invariant: metadata-binding precedes embedding"
        )
    if record.get("embedding_emitted") is True and record.get("metadata_bound_before_embedding") is not True:
        raise ArtifactShapeError(
            "ChunkSealedEnvelope: embedding emitted before metadata bound"
        )
    required_metadata = ("tenant_id", "acl", "confidentiality_tier", "freshness_band",
                         "effective_date", "expiry_date", "embedding_schema_version")
    missing = [k for k in required_metadata if not record.get(k)]
    if missing:
        raise ArtifactShapeError(
            f"ChunkSealedEnvelope missing pre-embedding metadata: {missing}"
        )


def assert_l1_no_authority_leak(record: Mapping[str, Any]) -> None:
    """L1 plan MUST NOT execute / retrieve / route — notepad plan only."""
    for flag in ("no_execution_assertion", "no_retrieval_assertion", "no_routing_assertion"):
        if record.get(flag) is not True:
            raise ArtifactShapeError(
                f"L1PlanContract.{flag} must be True; "
                f"L1 invariant: notepad plan only, no execution/retrieval/routing"
            )


def assert_l0_route_pre_filter_invariants(record: Mapping[str, Any]) -> None:
    """L0 pre-routing gate MUST check ACL/region/confidentiality/dates and bind policy."""
    for flag in ("tenant_acl_checked", "region_checked", "confidentiality_checked",
                 "effective_dates_checked", "freshness_band_checked", "policy_bound",
                 "single_route_per_request"):
        if record.get(flag) is not True:
            raise ArtifactShapeError(
                f"RouteContract.{flag} must be True; "
                f"L0 invariant: pre-routing gate enforces all checks before bind"
            )


_ALLOWED_X3_DISPOSITIONS = frozenset({
    "ALLOW", "DENY", "RETURN", "ESCALATE_TO_HITL", "COMMIT_TO_UWG",
    # legacy aliases used in some doctrine sections:
    "ALLOW_RESPONSE", "DENY_RETURN",
})


def assert_x3_disposition_explicit(record: Mapping[str, Any]) -> None:
    """Exit X3 disposition MUST be from the explicit set, with no silent fallback."""
    disp = record.get("disposition")
    if disp not in _ALLOWED_X3_DISPOSITIONS:
        raise ArtifactShapeError(
            f"X3DispositionPacket.disposition '{disp}' not in allowed set "
            f"{sorted(_ALLOWED_X3_DISPOSITIONS)}"
        )
    for flag in ("no_silent_fallback_assertion", "no_hidden_commit_path_assertion",
                 "no_ungated_human_mod_assertion", "single_disposition_per_request"):
        if record.get(flag) is not True:
            raise ArtifactShapeError(
                f"X3DispositionPacket.{flag} must be True; exit-gate invariant"
            )


def assert_l6_eval_no_current_run_mutation(record: Mapping[str, Any]) -> None:
    """L6 shadow eval MUST NOT mutate current run; must be replay-tied + calibrated."""
    for flag in ("is_shadow", "no_current_run_mutation_assertion",
                 "judge_calibrated", "replay_tied"):
        if record.get(flag) is not True:
            raise ArtifactShapeError(
                f"L6EvalRecord.{flag} must be True; "
                f"L6 invariant: shadow + replay-tied + calibrated, no current-run mutation"
            )
    age = record.get("calibration_age_days")
    if not isinstance(age, int) or age < 0:
        raise ArtifactShapeError(
            f"L6EvalRecord.calibration_age_days must be a non-negative int, got {age!r}"
        )


def assert_otel_replay_key_audit_present(record: Mapping[str, Any]) -> None:
    """Cross-cutting OTEL: every trace MUST carry replay_key, W3C TraceContext, owner_surface."""
    if record.get("replay_key_audit_present") is not True:
        raise ArtifactShapeError(
            "OtelTraceAuditRecord.replay_key_audit_present must be True; "
            "constitutional OTEL invariant: replay-key audit on every trace"
        )
    for f in ("trace_id", "replay_key", "owner_surface", "w3c_traceparent", "w3c_tracestate"):
        if not record.get(f):
            raise ArtifactShapeError(
                f"OtelTraceAuditRecord missing required field {f!r}"
            )


def assert_l5_certification_chain_present(record: Mapping[str, Any]) -> None:
    """L5 emits certification evidence (never live ALLOW/DENY).

    Wraps the existing assert_l5_is_certification_only, plus checks that the
    certification carries authority + policy binding receipts (via evidence_refs).
    """
    assert_l5_is_certification_only(record)
    refs = record.get("evidence_refs") or ()
    # evidence_refs should be a list/tuple of refs; for the proof-pack pilot
    # we just require non-empty.
    if not refs:
        raise ArtifactShapeError(
            "L5CertificationResult.evidence_refs must be non-empty; "
            "L5 certification chain requires authority + policy binding receipts"
        )


def assert_uwg_commit_request_invariants(record: Mapping[str, Any]) -> None:
    """UWG CommitRequest MUST be single-writer + monotonic seqno + policy-bound.

    Wraps assert_uwg_single_writer plus checks that policy_hash and
    blueprint_hash are present (durable commit must be policy-bound).
    """
    assert_uwg_single_writer(record)
    for f in ("policy_hash", "blueprint_hash", "diff_payload_hash"):
        if not record.get(f):
            raise ArtifactShapeError(
                f"CommitRequest missing required write-admission field {f!r}"
            )


def assert_l2_execution_sealed(record: Mapping[str, Any]) -> None:
    """L2 ExecutionResult MUST be sealed (no commit / no HITL / no routing).

    Wraps assert_l2_no_authority_leak and additionally checks that
    side_effects_proposed is present (sealed envelope shape).
    """
    assert_l2_no_authority_leak(record)
    if "side_effects_proposed" not in record:
        raise ArtifactShapeError(
            "ExecutionResult missing side_effects_proposed; "
            "L2 sealed-envelope invariant: side effects PROPOSED only, never committed"
        )
