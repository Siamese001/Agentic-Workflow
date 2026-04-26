"""L2 Execution Request — Entry-time normalized packet (doc 04.1).

Maps to: docs/reference/04_L2_Execute/04.1_L2_Execution_Entry_Authority_and_Packet_Intake_detailed.md

This module owns the L2 *entry surface* — the normalized packet that L2
constructs from a signed L0 single-step packet, an L3 current-step contract,
or a replay-resume token, before E1 Prep takes over.

Three contracts are exposed:

  * :class:`L2ExecutionRequest`        — normalized entry packet for E1.
  * :class:`ExecutionAuthorityContext` — issuer/scope/lane bindings.
  * :class:`L2BoundaryAssertion`       — L2-cannot-do bits asserted at entry.

Design invariants (per 04.1):

1. L2 receives authority. It does not create authority. The
   :class:`ExecutionAuthorityContext` enforces ``human_input_scope=DATA_ONLY``
   and ``durable_write_authority=NONE`` at the type level.
2. The entry packet must originate from a *governed channel*: either
   ``L0_SINGLE_STEP`` (R3/R4) or ``L3_CURRENT_STEP`` (managed workflow), or
   a ``REPLAY_RESUME`` of a prior governed packet.
3. Boundary assertions are not flags-by-default — they are explicit, sealed,
   and required for the request to be considered well-formed.

This module is **additive**. It composes with the v3/v4 receipt schemas
already in ``l2_v3_receipts.py`` / ``l2_v4_contracts.py`` — neither is edited
by this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
# Source packet provenance
# ---------------------------------------------------------------------------


class SourcePacketType(str, Enum):
    """04.1 §PHASE 1 source_packet_type — where the entry packet came from."""

    L0_SINGLE_STEP = "L0_SINGLE_STEP"
    L3_CURRENT_STEP = "L3_CURRENT_STEP"
    REPLAY_RESUME = "REPLAY_RESUME"


class IssuerSurface(str, Enum):
    """Allowed issuer surfaces. L2 will reject anything else."""

    L0 = "L0"
    L3 = "L3"


class HumanInputScope(str, Enum):
    """04.1 §PHASE 1 ExecutionAuthorityContext.human_input_scope."""

    DATA_ONLY = "DATA_ONLY"


class DurableWriteAuthority(str, Enum):
    """04.1 §PHASE 1 ExecutionAuthorityContext.durable_write_authority."""

    NONE = "NONE"


# ---------------------------------------------------------------------------
# 1. ExecutionAuthorityContext (04.1 §PHASE 1.2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionAuthorityContext:
    """04.1 §PHASE 1.2 — bound authority for one L2 invocation.

    L2 may *receive* authority through this context but never *create* it.
    Two constraints are baked into the type:

      * ``human_input_scope`` is constrained by :class:`HumanInputScope`
        which has only ``DATA_ONLY`` — so any human text reaching L2 is data,
        never authority.
      * ``durable_write_authority`` is constrained by
        :class:`DurableWriteAuthority` which has only ``NONE`` — so L2
        cannot self-grant a write path.
    """

    authority_context_id: str
    issuer_surface: IssuerSurface
    issuer_receipt_ref: str
    route_authority_ref: str
    capability_scope: str
    sandbox_scope: str
    tenant_scope: str
    acl_scope: str
    provider_lane: str
    filesystem_scope: str
    network_scope: str
    credential_scope: str
    step_authority_ref: str | None = None
    model_lane: str | None = None
    tool_lane: str | None = None
    human_input_scope: HumanInputScope = HumanInputScope.DATA_ONLY
    durable_write_authority: DurableWriteAuthority = DurableWriteAuthority.NONE
    allowed_side_effect_classes: tuple[str, ...] = ()
    disallowed_side_effect_classes: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# 2. L2BoundaryAssertion (04.1 §PHASE 1.3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class L2BoundaryAssertion:
    """04.1 §PHASE 1.3 — L2 cannot-do bits asserted at entry.

    Each field corresponds to an explicit L2 invariant from the
    ``GLOBAL NO-OVERLAP LOCK``. They MUST all be ``True`` for the request to
    be considered well-formed. Setting any to ``False`` flags a forbidden
    construction that the entry pipeline must reject.
    """

    no_route_decision_asserted: bool = True
    no_workflow_expansion_asserted: bool = True
    no_c0_retrieval_asserted: bool = True
    no_prompt_assembly_asserted: bool = True
    no_direct_human_call_asserted: bool = True
    no_direct_l4_write_asserted: bool = True
    no_exit_disposition_asserted: bool = True
    no_l6_learning_asserted: bool = True

    def all_clean(self) -> bool:
        """All boundary bits asserted (the only well-formed state)."""
        return all(
            (
                self.no_route_decision_asserted,
                self.no_workflow_expansion_asserted,
                self.no_c0_retrieval_asserted,
                self.no_prompt_assembly_asserted,
                self.no_direct_human_call_asserted,
                self.no_direct_l4_write_asserted,
                self.no_exit_disposition_asserted,
                self.no_l6_learning_asserted,
            )
        )

    def violations(self) -> tuple[str, ...]:
        """Return the names of any unasserted boundary bits."""
        bad: list[str] = []
        for name in (
            "no_route_decision_asserted",
            "no_workflow_expansion_asserted",
            "no_c0_retrieval_asserted",
            "no_prompt_assembly_asserted",
            "no_direct_human_call_asserted",
            "no_direct_l4_write_asserted",
            "no_exit_disposition_asserted",
            "no_l6_learning_asserted",
        ):
            if not getattr(self, name):
                bad.append(name)
        return tuple(bad)


# ---------------------------------------------------------------------------
# 3. L2ExecutionRequest (04.1 §PHASE 1.1)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class L2ExecutionRequest:
    """04.1 §PHASE 1.1 — normalized entry packet for E1.

    Required fields per 04.1 spec; optional refs (prompt envelope, evidence
    contract, L3 step contract) appear depending on the route's needs.

    Validation rules (enforced by :func:`packet_normalizer.normalize_to_request`):

    * Must come from a governed channel (``issuer_surface`` ∈ {L0, L3}).
    * Must include ``route_contract_ref``.
    * Must include ``policy_hash``, ``blueprint_hash``, ``replay_key``,
      and refs to capability + sandbox.
    * Grounded routes must include ``final_evidence_contract_ref`` and
      ``prompt_envelope_ref``.
    * Model execution must include ``prompt_envelope_ref`` (or compiled
      artifact ref carried in the same field).
    * PTC execution must include ``ptc_execution_profile_ref``,
      ``script_digest``, and ``sandbox_profile_ref``.
    """

    request_id: str
    run_id: str
    trace_root: str
    route_id: str
    route_contract_ref: str
    execution_form: str
    source_packet_type: SourcePacketType
    signed_packet_ref: str
    task_spec_ref: str
    capability_token_ref: str
    sandbox_envelope_ref: str
    side_effect_class: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    snapshot_manifest_ref: str
    expected_output_contract: str
    max_attempts: int
    max_repair_count: int
    timeout_ms: int
    cost_budget: float
    authority_context: ExecutionAuthorityContext
    boundary_assertion: L2BoundaryAssertion
    # Optional refs depending on route type
    prompt_envelope_ref: str | None = None
    final_evidence_contract_ref: str | None = None
    l3_step_contract_ref: str | None = None
    ptc_execution_profile_ref: str | None = None
    script_digest: str | None = None
    sandbox_profile_ref: str | None = None
    telemetry_keys: tuple[str, ...] = ()
    grounded: bool = False
    is_model_execution: bool = False
    is_ptc_execution: bool = False
    issuer_signature_hmac: str = ""

    def is_governed_channel(self) -> bool:
        """True iff this packet originated from L0 or L3 (per spec)."""
        return self.authority_context.issuer_surface in (
            IssuerSurface.L0,
            IssuerSurface.L3,
        )


# ---------------------------------------------------------------------------
# 4. EntryRejection (rejection result for unsigned/route-mutated packets)
# ---------------------------------------------------------------------------


class EntryRejectionReason(str, Enum):
    """04.1 §PHASE 3 fail-closed conditions."""

    NO_ROUTE_CONTRACT_REF = "no_route_contract_ref"
    NON_GOVERNED_ISSUER = "non_governed_issuer"  # not L0/L3
    UNSIGNED_PACKET = "unsigned_packet"
    ROUTE_DIGEST_MISMATCH = "route_digest_mismatch"
    GRANTS_DURABLE_WRITE = "grants_durable_write"
    HUMAN_TEXT_IN_AUTHORITY = "human_text_in_authority"
    ASKS_L2_TO_RETRIEVE_OR_ROUTE = "asks_l2_to_retrieve_or_route"
    PTC_MISSING_DIGEST_OR_PROFILE = "ptc_missing_digest_or_profile"
    BOUNDARY_VIOLATION = "boundary_violation"
    MISSING_REQUIRED_REF = "missing_required_ref"
    GROUNDED_MISSING_EVIDENCE_CONTRACT = "grounded_missing_evidence_contract"
    MODEL_EXECUTION_MISSING_PROMPT_ENVELOPE = "model_execution_missing_prompt_envelope"


@dataclass(frozen=True)
class EntryRejection:
    """Sealed entry-time rejection. No work performed, no E1 spawned."""

    rejection_id: str
    reason: EntryRejectionReason
    detail: str
    source_packet_type: SourcePacketType | None = None
    failed_field: str = ""
    boundary_violations: tuple[str, ...] = field(default_factory=tuple)


__all__ = [
    "DurableWriteAuthority",
    "EntryRejection",
    "EntryRejectionReason",
    "ExecutionAuthorityContext",
    "HumanInputScope",
    "IssuerSurface",
    "L2BoundaryAssertion",
    "L2ExecutionRequest",
    "SourcePacketType",
]
