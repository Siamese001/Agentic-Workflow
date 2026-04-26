"""Tests for route_contract — RouteContract + L1PlanContract validation."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval import (
    FreshnessClass,
    L1PlanContract,
    RouteContract,
    SourceClass,
    SupportTarget,
)
from tests.agentic_core.L0_routing.c0_retrieval._factories import (
    make_plan_contract,
    make_route,
)


class TestL1PlanContract:
    def test_minimal_construct(self):
        p = L1PlanContract(task_spec="t", query_spec="q")
        assert p.grounding_required is True

    def test_task_spec_must_be_str(self):
        with pytest.raises(TypeError):
            L1PlanContract(task_spec=123, query_spec="q")  # type: ignore[arg-type]

    def test_query_spec_must_be_str(self):
        with pytest.raises(TypeError):
            L1PlanContract(task_spec="t", query_spec=None)  # type: ignore[arg-type]


class TestRouteContractValidation:
    def test_default_construct(self):
        r = make_route()
        assert r.route_id == "R3_GROUNDED"
        assert r.grounding_required is True

    def test_invalid_max_k(self):
        with pytest.raises(ValueError):
            make_route()  # ok
            RouteContract(
                route_id="R3", grounding_required=True, execution_form="SINGLE_STEP",
                freshness_class=FreshnessClass.STATIC,
                support_target=SupportTarget.SOURCE_SUMMARY, tenant_scope="t",
                max_k=0,
            )

    def test_invalid_max_hops(self):
        with pytest.raises(ValueError):
            RouteContract(
                route_id="R3", grounding_required=True, execution_form="SINGLE_STEP",
                freshness_class=FreshnessClass.STATIC,
                support_target=SupportTarget.SOURCE_SUMMARY, tenant_scope="t",
                max_hops=-1,
            )

    def test_invalid_execution_form(self):
        with pytest.raises(ValueError):
            RouteContract(
                route_id="R3", grounding_required=True, execution_form="WHATEVER",
                freshness_class=FreshnessClass.STATIC,
                support_target=SupportTarget.SOURCE_SUMMARY, tenant_scope="t",
            )

    def test_invalid_fallback_policy(self):
        with pytest.raises(ValueError):
            RouteContract(
                route_id="R3", grounding_required=True, execution_form="SINGLE_STEP",
                freshness_class=FreshnessClass.STATIC,
                support_target=SupportTarget.SOURCE_SUMMARY, tenant_scope="t",
                fallback_policy="lol",
            )

    def test_zero_token_context_rejected(self):
        with pytest.raises(ValueError):
            RouteContract(
                route_id="R3", grounding_required=True, execution_form="SINGLE_STEP",
                freshness_class=FreshnessClass.STATIC,
                support_target=SupportTarget.SOURCE_SUMMARY, tenant_scope="t",
                max_token_context=0,
            )


class TestSourceClassPolicy:
    def test_allows_source_when_no_filter(self):
        r = make_route()
        for sc in SourceClass:
            assert r.allows_source(sc) is True

    def test_disallows_source_in_disallowed(self):
        r = make_route(disallowed_sources=(SourceClass.LOGS,))
        assert r.allows_source(SourceClass.LOGS) is False
        assert r.allows_source(SourceClass.DOCS) is True

    def test_allowed_whitelist_excludes_others(self):
        r = make_route(allowed_sources=(SourceClass.DOCS,))
        assert r.allows_source(SourceClass.DOCS) is True
        assert r.allows_source(SourceClass.LOGS) is False


class TestDataClassPolicy:
    def test_default_allows_internal(self):
        r = make_route()
        assert r.allows_data_class("internal") is True
        assert r.allows_data_class("public") is True
        assert r.allows_data_class("restricted") is False

    def test_custom_data_classes(self):
        r = make_route(allowed_data_classes=("public",))
        assert r.allows_data_class("public") is True
        assert r.allows_data_class("internal") is False


class TestImmutability:
    def test_route_is_frozen(self):
        r = make_route()
        with pytest.raises(Exception):
            r.tenant_scope = "other"  # type: ignore[misc]

    def test_plan_is_frozen(self):
        p = make_plan_contract()
        with pytest.raises(Exception):
            p.task_spec = "other"  # type: ignore[misc]
