"""App-domain contract registration adapter (UWG-side).

Plan: ``.windsurf/plans/apps-domain-contract-fortknox-c4d8e2.md`` §W3.

Converts a validated bundle of app-domain records (parsed from
``apps_<name>/config/domain_contract/*.yaml``) into a ``CommitRequest`` +
``StateDiff`` set and submits them through :class:`DurableWriteGateway`.

Authority story:

- ``source_surface == "Exit"`` is preserved verbatim per the UWG invariant
  (see ``durable_write_gateway.py`` ``_validate``). The registrar acts as
  a synthetic Exit pseudo-run whose ``cleared_exit_review_packet_ref``
  carries the deterministic digest of the bundle. Apps NEVER write
  directly to L4 — they author proposals, the registrar (running with
  Exit authority) performs the write.
- Operation type: ``"app_domain_contract_register"`` (added to
  ``ALLOWED_OPERATIONS``).
- Each record produces one ``StateDiff`` with ``target_surface``
  ``"l4.app_domain.<record_kind>"``.
- After successful commit, every record is also placed in the in-memory
  store so the runtime resolver can read it. The store is the runtime's
  read tier; the audit ledger is the durable lineage trail.

Failure mode is fail-closed: any record that fails its dataclass
``__post_init__`` invariant raises ``AppDomainContractError`` and the
whole bundle is rejected before any UWG call.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from agentic_core.L4_state.contracts.app_domain import (
    AppCapabilityProfileRecord,
    AppDomainContractRecord,
    AppEvalRubricRecord,
    AppFixtureRecord,
    AppGraderRosterRecord,
    AppInputContractRecord,
    AppNegativeControlRecord,
    AppOrchestrationProfileRecord,
    AppOutputSchemaRecord,
    AppPromptProfileRecord,
    AppRetrievalProfileRecord,
    AppRouteProfileRecord,
    AppThresholdProfileRecord,
    app_domain_record_kind,
)
from agentic_core.L4_state.contracts.app_domain_lookup import (
    InMemoryAppDomainStore,
    get_default_app_domain_store,
)
from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from agentic_core.L4_state.contracts.records import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
    UWGBlockedCommitReceipt,
    UWGCommitReceipt,
    record_canonical_payload,
    stamp_digest,
)
from agentic_core.L4_state.uwg.durable_write_gateway import (
    DurableWriteGateway,
    get_default_gateway,
)

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppDomainContractBundle:
    """A complete app-domain contract proposal.

    The :func:`register_bundle` function expects every subcontract record
    to have already been constructed and ``stamp_digest``-ed. The bundle
    is the unit of UWG admission.
    """

    contract: AppDomainContractRecord
    input_contract: AppInputContractRecord
    output_schema: AppOutputSchemaRecord
    eval_rubrics: Tuple[AppEvalRubricRecord, ...] = field(default_factory=tuple)
    threshold_profiles: Tuple[AppThresholdProfileRecord, ...] = field(default_factory=tuple)
    grader_rosters: Tuple[AppGraderRosterRecord, ...] = field(default_factory=tuple)
    retrieval_profiles: Tuple[AppRetrievalProfileRecord, ...] = field(default_factory=tuple)
    prompt_profiles: Tuple[AppPromptProfileRecord, ...] = field(default_factory=tuple)
    capability_profiles: Tuple[AppCapabilityProfileRecord, ...] = field(default_factory=tuple)
    route_profiles: Tuple[AppRouteProfileRecord, ...] = field(default_factory=tuple)
    orchestration_profiles: Tuple[AppOrchestrationProfileRecord, ...] = field(default_factory=tuple)
    fixtures: Tuple[AppFixtureRecord, ...] = field(default_factory=tuple)
    negative_controls: Tuple[AppNegativeControlRecord, ...] = field(default_factory=tuple)

    def all_records(self) -> List[object]:
        """Iteration helper — every record in canonical order."""
        out: List[object] = [self.contract, self.input_contract, self.output_schema]
        out.extend(self.eval_rubrics)
        out.extend(self.threshold_profiles)
        out.extend(self.grader_rosters)
        out.extend(self.retrieval_profiles)
        out.extend(self.prompt_profiles)
        out.extend(self.capability_profiles)
        out.extend(self.route_profiles)
        out.extend(self.orchestration_profiles)
        out.extend(self.fixtures)
        out.extend(self.negative_controls)
        return out


@dataclass(frozen=True)
class RegistrationReceipt:
    """Outcome of a single bundle registration."""

    app_id: str
    bundle_digest: str
    commit_receipt: Optional[UWGCommitReceipt]
    blocked_receipt: Optional[UWGBlockedCommitReceipt]
    state_diff_count: int
    refresh_receipt_count: int

    @property
    def accepted(self) -> bool:
        return self.commit_receipt is not None


def _build_state_diff(record: object, *, app_id: str) -> StateDiff:
    """Construct a StateDiff for one app-domain record.

    Operation type is the dedicated ``app_domain_contract_register``
    (registered in ``ALLOWED_OPERATIONS``). ``target_surface`` is
    namespaced by record kind for downstream audit-grep clarity.
    """
    record_kind = app_domain_record_kind(record)
    record_id_attr = _record_id_attr(record_kind)  # guardian: allow-hallucinated-tool-name -- P1 ADG burndown
    record_id = getattr(record, record_id_attr)  # guardian: allow-hallucinated-tool-name -- P1 ADG burndown
    after_candidate = f"l4://app_domain/{record_kind}/{record_id}"
    rollback_plan_ref = f"rollback://app_domain/{record_kind}/{record_id}"
    schema_ref = f"schema://app_domain/{record_kind}"
    sd = StateDiff(
        state_diff_id=str(uuid.uuid4()),
        target_surface=f"l4.app_domain.{record_kind}",
        operation_type="app_domain_contract_register",
        after_candidate=after_candidate,
        schema_ref=schema_ref,
        blast_radius="registry_scoped",
        rollback_plan_ref=rollback_plan_ref,
        proposed_by_surface="Exit",
        created_at=str(int(time.time())),
        validation_rules=("dataclass_post_init", f"vocab_check::{record_kind}"),
        policy_refs=(f"policy://app_domain/{app_id}",),
    )
    return stamp_digest(sd)


def _record_id_attr(record_kind: str) -> str:
    """Map record class name → its id-attribute name."""
    mapping = {
        "AppDomainContractRecord": "app_domain_contract_id",
        "AppInputContractRecord": "input_contract_id",
        "AppOutputSchemaRecord": "output_schema_id",
        "AppEvalRubricRecord": "eval_rubric_id",
        "AppThresholdProfileRecord": "threshold_profile_id",
        "AppGraderRosterRecord": "grader_roster_id",
        "AppRetrievalProfileRecord": "retrieval_profile_id",
        "AppPromptProfileRecord": "prompt_profile_id",
        "AppCapabilityProfileRecord": "capability_profile_id",
        "AppRouteProfileRecord": "route_profile_id",
        "AppOrchestrationProfileRecord": "orchestration_profile_id",
        "AppFixtureRecord": "fixture_id",
        "AppNegativeControlRecord": "negative_control_id",
    }
    if record_kind not in mapping:
        raise KeyError(f"unknown app-domain record kind {record_kind!r}")
    return mapping[record_kind]


def _compute_bundle_digest(bundle: AppDomainContractBundle) -> str:
    """Bundle-level digest = SHA-256 of canonical payload of every record's
    canonical payload, in canonical order."""
    payload = {
        "app_id": bundle.contract.app_id,
        "app_version": bundle.contract.app_version,
        "records": [
            {
                "kind": app_domain_record_kind(r),
                "payload": record_canonical_payload(r),
            }
            for r in bundle.all_records()
        ],
    }
    return compute_deterministic_digest(payload)


def _stamp_bundle(bundle: AppDomainContractBundle) -> AppDomainContractBundle:
    """Return a new bundle with every record stamped (digest filled in)."""
    return AppDomainContractBundle(
        contract=stamp_digest(bundle.contract),
        input_contract=stamp_digest(bundle.input_contract),
        output_schema=stamp_digest(bundle.output_schema),
        eval_rubrics=tuple(stamp_digest(r) for r in bundle.eval_rubrics),
        threshold_profiles=tuple(stamp_digest(r) for r in bundle.threshold_profiles),
        grader_rosters=tuple(stamp_digest(r) for r in bundle.grader_rosters),
        retrieval_profiles=tuple(stamp_digest(r) for r in bundle.retrieval_profiles),
        prompt_profiles=tuple(stamp_digest(r) for r in bundle.prompt_profiles),
        capability_profiles=tuple(stamp_digest(r) for r in bundle.capability_profiles),
        route_profiles=tuple(stamp_digest(r) for r in bundle.route_profiles),
        orchestration_profiles=tuple(stamp_digest(r) for r in bundle.orchestration_profiles),
        fixtures=tuple(stamp_digest(r) for r in bundle.fixtures),
        negative_controls=tuple(stamp_digest(r) for r in bundle.negative_controls),
    )


def register_bundle(
    bundle: AppDomainContractBundle,
    *,
    gateway: Optional[DurableWriteGateway] = None,
    store: Optional[InMemoryAppDomainStore] = None,
    tenant_id: str = "platform",
    policy_hash: Optional[str] = None,
    blueprint_hash: Optional[str] = None,
) -> RegistrationReceipt:
    """Register a complete app-domain contract bundle through UWG.

    Steps:
      1. Stamp every record's deterministic_digest.
      2. Compute bundle-level digest (replay key).
      3. Build one StateDiff per record.
      4. Construct CommitRequest with source_surface="Exit".
      5. Submit through DurableWriteGateway.commit.
      6. On accepted commit, hydrate the in-memory store so the runtime
         resolver can read the records immediately.
      7. Return a RegistrationReceipt.

    Failure modes:
      - dataclass invariant failure → AppDomainContractError raised
        before the UWG call (we never poison the audit ledger with a
        bad bundle).
      - UWG validation failure → returns a receipt with
        ``commit_receipt=None`` and ``blocked_receipt`` populated.

    Args:
        bundle: The validated bundle.
        gateway: Override gateway (test injection).
        store: Override read-tier store (test injection).
        tenant_id: Tenant scope. Defaults to ``"platform"`` for
            non-tenant-scoped contracts.
        policy_hash: Override the per-app policy_hash. Defaults to the
            bundle's contract.policy_hash.
        blueprint_hash: Same for blueprint_hash.

    Returns:
        RegistrationReceipt with commit/blocked outcome and counts.
    """
    gw = gateway or get_default_gateway()
    backend_store = store or get_default_app_domain_store()
    stamped = _stamp_bundle(bundle)
    bundle_digest = _compute_bundle_digest(stamped)

    state_diffs: List[StateDiff] = [
        _build_state_diff(record, app_id=stamped.contract.app_id)
        for record in stamped.all_records()
    ]

    commit_request_id = f"app-domain-register::{stamped.contract.app_id}::{bundle_digest[:12]}"
    rollback_plan_id = f"rollback-plan::{commit_request_id}"
    refresh_plan_id = f"refresh-plan::{commit_request_id}"
    target_surfaces = tuple(sorted({sd.target_surface for sd in state_diffs}))

    rollback_plan = stamp_digest(
        RollbackPlan(
            rollback_plan_id=rollback_plan_id,
            blast_radius="registry_scoped",
            target_surfaces=target_surfaces,
            rollback_operation_types=tuple("tombstone" for _ in state_diffs),
            policy_refs=(f"policy://app_domain/{stamped.contract.app_id}",),
            schema_refs=tuple(sd.schema_ref for sd in state_diffs),
        ),
    )
    refresh_plan = stamp_digest(
        ReadSurfaceRefreshPlan(
            refresh_plan_id=refresh_plan_id,
            source_commit_receipt_ref="",  # rebound by UWG after commit
            before_snapshot=gw.last_snapshot_id,
            expected_after_snapshot="",  # filled in by RefreshCoordinator
            stale_projection_policy="serve_with_warn",
            retry_policy="exponential_backoff_max_3",
            policy_hash=policy_hash or stamped.contract.policy_hash or "no-policy",
            blueprint_hash=blueprint_hash or stamped.contract.blueprint_hash or "no-blueprint",
            affected_surfaces=target_surfaces,
            required_refreshes=target_surfaces,
            refresh_order=target_surfaces,
        ),
    )

    commit_request = stamp_digest(
        CommitRequest(
            commit_request_id=commit_request_id,
            cleared_exit_review_packet_ref=f"erp://app-domain-register::{bundle_digest}",
            request_id=f"req::{commit_request_id}",
            run_id=f"run::{commit_request_id}",
            trace_root=f"trace::{commit_request_id}",
            tenant_id=tenant_id,
            policy_hash=policy_hash or stamped.contract.policy_hash or "no-policy",
            blueprint_hash=blueprint_hash or stamped.contract.blueprint_hash or "no-blueprint",
            route_contract_ref=f"route://app-domain-register::{stamped.contract.app_id}",
            replay_key=bundle_digest,
            rollback_plan_ref=rollback_plan_id,
            blast_radius="registry_scoped",
            source_surface="Exit",
            state_diff_refs=tuple(sd.state_diff_id for sd in state_diffs),
            gate_verdict_refs=(f"gate://app-domain-register::{bundle_digest}",),
            affected_state_surfaces=target_surfaces,
            expected_read_surface_refreshes=target_surfaces,
        ),
    )

    Logger.info(
        "app_domain_registration: submitting bundle app_id=%s digest=%s n_records=%d",
        stamped.contract.app_id,
        bundle_digest,
        len(state_diffs),
    )

    commit_receipt, blocked_receipt, refresh_receipts = gw.commit(
        commit_request=commit_request,
        state_diffs=state_diffs,
        rollback_plan=rollback_plan,
        refresh_plan=refresh_plan,
    )

    if commit_receipt is not None:
        _hydrate_store(backend_store, stamped)

    return RegistrationReceipt(
        app_id=stamped.contract.app_id,
        bundle_digest=bundle_digest,
        commit_receipt=commit_receipt,
        blocked_receipt=blocked_receipt,
        state_diff_count=len(state_diffs),
        refresh_receipt_count=len(refresh_receipts),
    )


def _hydrate_store(store: InMemoryAppDomainStore, bundle: AppDomainContractBundle) -> None:
    """Place the bundle's records into the in-memory read tier."""
    for r in bundle.input_contract, bundle.output_schema:
        if isinstance(r, AppInputContractRecord):
            store.put_input_contract(r)
        elif isinstance(r, AppOutputSchemaRecord):
            store.put_output_schema(r)
    for r in bundle.eval_rubrics:
        store.put_eval_rubric(r)
    for r in bundle.threshold_profiles:
        store.put_threshold_profile(r)
    for r in bundle.grader_rosters:
        store.put_grader_roster(r)
    for r in bundle.retrieval_profiles:
        store.put_retrieval_profile(r)
    for r in bundle.prompt_profiles:
        store.put_prompt_profile(r)
    for r in bundle.capability_profiles:
        store.put_capability_profile(r)
    for r in bundle.route_profiles:
        store.put_route_profile(r)
    for r in bundle.orchestration_profiles:
        store.put_orchestration_profile(r)
    for r in bundle.fixtures:
        store.put_fixture(r)
    for r in bundle.negative_controls:
        store.put_negative_control(r)
    # Top-level last so a partial hydrate never exposes a contract whose
    # subcontracts haven't all landed.
    store.put_contract(bundle.contract)


def register_bundles(
    bundles: Sequence[AppDomainContractBundle],
    *,
    gateway: Optional[DurableWriteGateway] = None,
    store: Optional[InMemoryAppDomainStore] = None,
    tenant_id: str = "platform",
) -> List[RegistrationReceipt]:
    """Convenience: register multiple bundles in declaration order."""
    receipts: List[RegistrationReceipt] = []
    for b in bundles:
        receipts.append(
            register_bundle(b, gateway=gateway, store=store, tenant_id=tenant_id),
        )
    return receipts


__all__ = [
    "AppDomainContractBundle",
    "RegistrationReceipt",
    "register_bundle",
    "register_bundles",
]
