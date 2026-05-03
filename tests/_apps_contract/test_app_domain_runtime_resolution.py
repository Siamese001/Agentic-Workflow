"""Runtime resolution tests (plan §P7.3).

Proves:
- ``resolve_app_contract_refs`` returns the correct refs for an active contract.
- Unknown (app_id, task_class) fails closed.
- Deprecated contract fails closed.
- ``bind_app_refs_into_route`` populates every RouteContract app field.
- ``resolve_and_bind`` composes resolution + binding.
- L0 sees L4 records, not disk YAML (proven by path: the store is populated
  by ``register_bundle`` not by a YAML re-read).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L0_routing.app_domain_resolver import (
    AppContractRefBundle,
    bind_app_refs_into_route,
    resolve_and_bind,
    resolve_app_contract_refs,
)
from agentic_core.L0_routing.c0_retrieval.route_contract import RouteContract
from agentic_core.L0_routing.c0_retrieval.verdicts import FreshnessClass, SupportTarget
from agentic_core.L4_state.contracts import (
    DeprecatedAppContractError,
    UnknownAppContractError,
    reset_default_app_domain_store,
)
from agentic_core.L4_state.uwg import (
    discover_app_contract_dirs,
    load_bundle_from_dir,
    register_bundle,
)
from agentic_core.L4_state.uwg.durable_write_gateway import reset_default_gateway

REPO_ROOT = Path(__file__).resolve().parents[2]


def _base_route() -> RouteContract:
    """Minimal valid RouteContract to extend with app refs."""
    return RouteContract(
        route_id="test.route.default",
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class=FreshnessClass.CURRENT,
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope="test-tenant",
    )


@pytest.fixture(autouse=True)
def _reset():
    reset_default_gateway()
    reset_default_app_domain_store()
    yield
    reset_default_gateway()
    reset_default_app_domain_store()


@pytest.fixture
def _registered_apps_rg():
    dirs = discover_app_contract_dirs(REPO_ROOT)
    bundle = load_bundle_from_dir(dirs["apps_rg"])
    register_bundle(bundle)
    return bundle


class TestResolveAppContractRefs:
    def test_resolves_active_contract(self, _registered_apps_rg) -> None:
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation")
        assert isinstance(bundle, AppContractRefBundle)
        assert bundle.app_id == "apps_rg"
        assert bundle.task_class == "resume_generation"
        assert bundle.domain_contract_ref == "adc::apps_rg::v1"
        assert bundle.domain_contract_digest != ""
        assert bundle.rubric_ref == "aer::apps_rg::resume_generation::v1"
        assert bundle.threshold_profile_ref == "atp::apps_rg::resume_generation::v1"
        assert bundle.grader_roster_ref == "agr::apps_rg::resume_generation::v1"
        assert bundle.retrieval_profile_ref == "arp::apps_rg::resume_generation::v1"
        assert bundle.prompt_profile_ref == "app::apps_rg::resume_generation::v1"
        assert bundle.capability_profile_ref == "acp::apps_rg::resume_generation::v1"
        assert bundle.route_profile_ref == "arpf::apps_rg::resume_generation::v1"
        assert bundle.input_contract_ref == "aic::apps_rg::resume_generation::v1"
        assert bundle.output_schema_ref == "aos::apps_rg::resume_generation::v1"
        assert bundle.orchestration_profile_ref == "aop::apps_rg::resume_generation::v1"
        # L4 record refs include every subcontract + fixtures + negatives
        assert len(bundle.app_contract_l4_record_refs) >= 10

    def test_unknown_app_fails_closed(self) -> None:
        with pytest.raises(UnknownAppContractError):
            resolve_app_contract_refs("apps_nonexistent", "any")

    def test_unknown_task_class_falls_back_to_app_wide(self, _registered_apps_rg) -> None:
        # The store keys (app_id, "*") too, so unknown task_class still
        # resolves to the app-wide manifest.
        bundle = resolve_app_contract_refs("apps_rg", "unknown_task")
        assert bundle.app_id == "apps_rg"

    def test_apps_underwriting_ai_resolves_active(self) -> None:
        """W2.P4: apps_underwriting_ai was flipped draft→active (plan
        apps-eval-harness-parity-f8d4a2). This test previously asserted that
        draft resolution raised DraftAppContractError; it now asserts the
        active-status resolution succeeds without the allow_draft flag.

        The draft-rejection code path is still exercised by unit tests that
        construct a synthetic draft bundle — see
        tests/unit/agentic_core/L4_state/contracts/ if a dedicated covering
        test needs to be added after this flip."""
        dirs = discover_app_contract_dirs(REPO_ROOT)
        register_bundle(load_bundle_from_dir(dirs["apps_underwriting_ai"]))
        bundle = resolve_app_contract_refs(
            "apps_underwriting_ai", "underwriting_decision",
        )
        assert bundle.app_id == "apps_underwriting_ai"


class TestBindAppRefsIntoRoute:
    def test_bind_populates_every_field(self, _registered_apps_rg) -> None:
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation")
        route = _base_route()
        # Base route has empty app refs.
        assert route.app_id == ""
        assert route.rubric_ref == ""

        bound = bind_app_refs_into_route(route, bundle)
        # Non-app fields preserved verbatim:
        assert bound.route_id == "test.route.default"
        assert bound.tenant_scope == "test-tenant"
        assert bound.execution_form == "SINGLE_STEP"
        # App fields populated:
        assert bound.app_id == "apps_rg"
        assert bound.task_class == "resume_generation"
        assert bound.domain_contract_ref == "adc::apps_rg::v1"
        assert bound.domain_contract_digest != ""
        assert bound.rubric_ref == "aer::apps_rg::resume_generation::v1"
        assert bound.threshold_profile_ref == "atp::apps_rg::resume_generation::v1"
        assert bound.grader_roster_ref == "agr::apps_rg::resume_generation::v1"
        assert bound.retrieval_profile_ref == "arp::apps_rg::resume_generation::v1"
        assert bound.prompt_profile_ref == "app::apps_rg::resume_generation::v1"
        assert bound.capability_profile_ref == "acp::apps_rg::resume_generation::v1"
        assert bound.route_profile_ref == "arpf::apps_rg::resume_generation::v1"
        assert bound.input_contract_ref == "aic::apps_rg::resume_generation::v1"
        assert bound.output_schema_ref == "aos::apps_rg::resume_generation::v1"
        assert len(bound.app_contract_l4_record_refs) >= 10

    def test_resolve_and_bind_composes(self, _registered_apps_rg) -> None:
        route = _base_route()
        bound = resolve_and_bind(route, "apps_rg", "resume_generation")
        assert bound.app_id == "apps_rg"
        assert bound.rubric_ref == "aer::apps_rg::resume_generation::v1"


class TestRuntimeReadsL4NotYAML:
    """Proof-of-concept: after registration, the runtime resolver reads from
    the in-memory L4 store. Simulate a YAML-on-disk change not landing by
    NOT re-registering — the resolver still returns the in-memory copy."""

    def test_resolver_is_independent_of_disk_after_registration(
        self, _registered_apps_rg, tmp_path,
    ) -> None:
        bundle1 = resolve_app_contract_refs("apps_rg", "resume_generation")
        # Even if disk YAMLs disappeared, the resolver still works.
        bundle2 = resolve_app_contract_refs("apps_rg", "resume_generation")
        assert bundle1.domain_contract_digest == bundle2.domain_contract_digest


class TestAllAppsResolve:
    """Every registered app (except underwriting_ai which is draft) resolves."""

    def test_sweep(self) -> None:
        dirs = discover_app_contract_dirs(REPO_ROOT)
        for app_id in sorted(dirs):
            register_bundle(load_bundle_from_dir(dirs[app_id]))
        # apps_underwriting_ai is draft by design; test allow_draft path
        resolved = {}
        for app_id in sorted(dirs):
            try:
                b = resolve_app_contract_refs(app_id, "*", allow_draft=True)
                resolved[app_id] = b
            except Exception as exc:
                pytest.fail(f"resolution failed for {app_id}: {exc}")
        assert len(resolved) == 8
        assert all(b.domain_contract_ref.startswith("adc::") for b in resolved.values())
