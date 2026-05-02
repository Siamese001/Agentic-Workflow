"""L0 app-domain contract resolver (W4 runtime resolution).

Given ``(app_id, task_class)`` at L0 dispatch time, this module consults
:class:`InMemoryAppDomainStore` (the L4 read tier) and returns the full
bundle of resolved refs that RouteContract / V15RouteContract / Exit need
to enforce app-specific behavior.

Plan: ``.windsurf/plans/apps-domain-contract-fortknox-c4d8e2.md`` §W4.

Authority story:

- The resolver is a READ-ONLY surface. It consults the in-memory store
  populated by :func:`register_bundle`; no UWG write path.
- Fail-closed: if no active contract exists for (app_id, task_class),
  :class:`UnknownAppContractError` is raised. L0 callers MUST surface
  this as a routing failure, not silently fall back to a generic rubric.
- Deprecated contracts also fail closed via
  :class:`DeprecatedAppContractError`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple

from agentic_core.L0_routing.c0_retrieval.route_contract import RouteContract
from agentic_core.L4_state.contracts.app_domain_lookup import (
    InMemoryAppDomainStore,
    get_default_app_domain_store,
)

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppContractRefBundle:
    """Resolved app-contract refs ready to bind into RouteContract.

    All fields are non-empty strings when the contract is active. If the
    app has no orchestration_profile_refs (linear apps), that field stays
    empty. ``app_contract_l4_record_refs`` is the tuple of every L4 record
    id that backs this (app_id, task_class) — useful for proof bundles.
    """

    app_id: str
    task_class: str
    domain_contract_ref: str
    domain_contract_digest: str
    input_contract_ref: str
    output_schema_ref: str
    rubric_ref: str
    threshold_profile_ref: str
    grader_roster_ref: str
    retrieval_profile_ref: str
    prompt_profile_ref: str
    capability_profile_ref: str
    route_profile_ref: str
    orchestration_profile_ref: str = ""
    app_contract_l4_record_refs: Tuple[str, ...] = field(default_factory=tuple)


def _pick_single_ref(refs: Tuple[str, ...], default: str = "") -> str:
    """Select one ref from a tuple. Current schema places exactly one ref
    per subcontract type per (app, task_class); if multiple are present,
    pick the first deterministically."""
    if not refs:
        return default
    return refs[0]


def resolve_app_contract_refs(
    app_id: str,
    task_class: str,
    *,
    store: Optional[InMemoryAppDomainStore] = None,
    allow_draft: bool = False,
) -> AppContractRefBundle:
    """Resolve all app-contract refs for (app_id, task_class). Fail-closed.

    Raises:
        UnknownAppContractError: no contract for this (app_id, task_class).
        DeprecatedAppContractError: contract status == 'deprecated'.
        DraftAppContractError: contract status == 'draft' unless allow_draft=True.
    """
    backend = store or get_default_app_domain_store()
    contract = backend.get_contract(app_id, task_class, allow_draft=allow_draft)

    bundle = AppContractRefBundle(
        app_id=contract.app_id,
        task_class=task_class,
        domain_contract_ref=contract.app_domain_contract_id,
        domain_contract_digest=contract.deterministic_digest,
        input_contract_ref=contract.input_contract_ref,
        output_schema_ref=contract.output_schema_ref,
        rubric_ref=_pick_single_ref(contract.eval_rubric_refs),
        threshold_profile_ref=_pick_single_ref(contract.threshold_profile_refs),
        grader_roster_ref=_pick_single_ref(contract.grader_roster_refs),
        retrieval_profile_ref=_pick_single_ref(contract.retrieval_profile_refs),
        prompt_profile_ref=_pick_single_ref(contract.prompt_profile_refs),
        capability_profile_ref=_pick_single_ref(contract.capability_profile_refs),
        route_profile_ref=_pick_single_ref(contract.route_profile_refs),
        orchestration_profile_ref=_pick_single_ref(contract.orchestration_profile_refs),
        app_contract_l4_record_refs=(
            contract.input_contract_ref,
            contract.output_schema_ref,
            *contract.eval_rubric_refs,
            *contract.threshold_profile_refs,
            *contract.grader_roster_refs,
            *contract.retrieval_profile_refs,
            *contract.prompt_profile_refs,
            *contract.capability_profile_refs,
            *contract.route_profile_refs,
            *contract.orchestration_profile_refs,
            *contract.fixture_refs,
            *contract.negative_control_refs,
        ),
    )
    Logger.debug(
        "app_domain_resolver: resolved %s/%s -> digest=%s",
        app_id,
        task_class,
        bundle.domain_contract_digest[:12] if bundle.domain_contract_digest else "(empty)",
    )
    return bundle


def bind_app_refs_into_route(
    route: RouteContract,
    bundle: AppContractRefBundle,
) -> RouteContract:
    """Return a copy of ``route`` with every app-contract ref populated.

    The base route's fields (route_id, tenant_scope, etc.) are preserved;
    only the app-specific refs are set. This is called by L0 immediately
    after :func:`resolve_app_contract_refs` succeeds.
    """
    return replace(
        route,
        app_id=bundle.app_id,
        task_class=bundle.task_class,
        domain_contract_ref=bundle.domain_contract_ref,
        domain_contract_digest=bundle.domain_contract_digest,
        rubric_ref=bundle.rubric_ref,
        threshold_profile_ref=bundle.threshold_profile_ref,
        grader_roster_ref=bundle.grader_roster_ref,
        retrieval_profile_ref=bundle.retrieval_profile_ref,
        prompt_profile_ref=bundle.prompt_profile_ref,
        capability_profile_ref=bundle.capability_profile_ref,
        route_profile_ref=bundle.route_profile_ref,
        input_contract_ref=bundle.input_contract_ref,
        output_schema_ref=bundle.output_schema_ref,
        orchestration_profile_ref=bundle.orchestration_profile_ref,
        app_contract_l4_record_refs=bundle.app_contract_l4_record_refs,
    )


def resolve_and_bind(
    route: RouteContract,
    app_id: str,
    task_class: str,
    *,
    store: Optional[InMemoryAppDomainStore] = None,
    allow_draft: bool = False,
) -> RouteContract:
    """Convenience: resolve app refs and bind them into ``route`` in one call."""
    bundle = resolve_app_contract_refs(
        app_id, task_class, store=store, allow_draft=allow_draft,
    )
    return bind_app_refs_into_route(route, bundle)


__all__ = [
    "AppContractRefBundle",
    "resolve_app_contract_refs",
    "bind_app_refs_into_route",
    "resolve_and_bind",
]
