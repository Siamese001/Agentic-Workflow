"""Tests for C0.1 RetrievalPlan + build_retrieval_plan."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval import (
    Budgets,
    CachePolicy,
    DenseQuerySpec,
    FreshnessClass,
    GraphBounds,
    MetadataFilters,
    RetrievalPlan,
    SourceClass,
    SparseQuerySpec,
    SupportTarget,
    build_retrieval_plan,
    run_preflight,
)
from agentic_core.L0_routing.c0_retrieval.preflight import EvidenceStandard
from agentic_core.L0_routing.c0_retrieval.verdicts import RetrievalMode
from tests.agentic_core.L0_routing.c0_retrieval._factories import (
    make_plan_contract,
    make_route,
)


class TestGraphBounds:
    def test_default(self):
        b = GraphBounds()
        assert b.max_hops == 1

    def test_negative_hops_rejected(self):
        with pytest.raises(ValueError):
            GraphBounds(max_hops=-1)

    def test_negative_expansion_rejected(self):
        with pytest.raises(ValueError):
            GraphBounds(max_parent_expansion=-1)


class TestBudgets:
    def test_default(self):
        b = Budgets()
        assert b.max_k == 20

    def test_zero_max_k_rejected(self):
        with pytest.raises(ValueError):
            Budgets(max_k=0)

    def test_zero_token_context_rejected(self):
        with pytest.raises(ValueError):
            Budgets(max_token_context=0)


class TestQuerySpecs:
    def test_dense_requires_text(self):
        with pytest.raises(ValueError):
            DenseQuerySpec(query_text="   ")

    def test_dense_threshold_range(self):
        with pytest.raises(ValueError):
            DenseQuerySpec(query_text="foo", similarity_threshold=1.5)

    def test_dense_top_k_positive(self):
        with pytest.raises(ValueError):
            DenseQuerySpec(query_text="foo", top_k=0)

    def test_sparse_needs_terms_or_must_include(self):
        with pytest.raises(ValueError):
            SparseQuerySpec(terms=())

    def test_sparse_with_must_include_only_ok(self):
        s = SparseQuerySpec(terms=(), must_include=("alpha",))
        assert s.must_include == ("alpha",)

    def test_metadata_requires_tenant(self):
        with pytest.raises(ValueError):
            MetadataFilters(tenant_id="")


class TestCachePolicy:
    def test_default_no_cache(self):
        cp = CachePolicy()
        assert cp.allow_cache is False

    def test_allow_cache_requires_max_age(self):
        with pytest.raises(ValueError):
            CachePolicy(allow_cache=True, max_cache_age_seconds=0)

    def test_allow_cache_with_age(self):
        cp = CachePolicy(allow_cache=True, max_cache_age_seconds=3600)
        assert cp.max_cache_age_seconds == 3600


class TestRetrievalPlanValidation:
    def _base_kwargs(self, **over):
        kw = {
            "plan_id": "p1",
            "route_replay_key": "rrk",
            "policy_hash": "ph",
            "blueprint_hash": "bp",
            "support_target": SupportTarget.SOURCE_SUMMARY,
            "evidence_standard": EvidenceStandard.STANDARD,
            "freshness_class": FreshnessClass.STATIC,
            "source_classes": (SourceClass.DOCS,),
            "allowed_sources": (SourceClass.DOCS,),
            "disallowed_sources": (),
            "retrieval_modes": (RetrievalMode.HYBRID,),
            "dense_query_spec": DenseQuerySpec(query_text="q"),
            "sparse_query_spec": None,
            "metadata_filters": MetadataFilters(tenant_id="t"),
            "cache_policy": CachePolicy(),
            "graph_bounds": GraphBounds(),
            "budgets": Budgets(),
        }
        kw.update(over)
        return kw

    def test_valid(self):
        p = RetrievalPlan(**self._base_kwargs())
        assert p.plan_id == "p1"

    def test_empty_plan_id_rejected(self):
        with pytest.raises(ValueError):
            RetrievalPlan(**self._base_kwargs(plan_id=""))

    def test_empty_source_classes_rejected(self):
        with pytest.raises(ValueError):
            RetrievalPlan(**self._base_kwargs(source_classes=()))

    def test_empty_modes_rejected(self):
        with pytest.raises(ValueError):
            RetrievalPlan(**self._base_kwargs(retrieval_modes=()))

    def test_invalid_weak_policy(self):
        with pytest.raises(ValueError):
            RetrievalPlan(**self._base_kwargs(weak_support_policy="lol"))

    def test_exactness_target_requires_sparse_or_metadata(self):
        # EXACT_QUOTE with only DENSE mode should be rejected (C0.I5).
        with pytest.raises(ValueError):
            RetrievalPlan(
                **self._base_kwargs(
                    support_target=SupportTarget.EXACT_QUOTE,
                    retrieval_modes=(RetrievalMode.DENSE,),
                )
            )

    def test_exactness_target_with_sparse_ok(self):
        p = RetrievalPlan(
            **self._base_kwargs(
                support_target=SupportTarget.EXACT_QUOTE,
                retrieval_modes=(RetrievalMode.SPARSE, RetrievalMode.DENSE),
            )
        )
        assert p.support_target == SupportTarget.EXACT_QUOTE

    def test_exactness_target_with_hybrid_ok(self):
        p = RetrievalPlan(
            **self._base_kwargs(
                support_target=SupportTarget.POLICY_CLAUSE,
                retrieval_modes=(RetrievalMode.HYBRID,),
            )
        )
        assert p.support_target == SupportTarget.POLICY_CLAUSE

    def test_source_in_both_allowed_and_disallowed_rejected(self):
        with pytest.raises(ValueError):
            RetrievalPlan(
                **self._base_kwargs(
                    allowed_sources=(SourceClass.DOCS,),
                    disallowed_sources=(SourceClass.DOCS,),
                )
            )


class TestBuildRetrievalPlan:
    def test_builds_from_route_and_preflight(self):
        route = make_route()
        plan_contract = make_plan_contract()
        pre = run_preflight(route, plan_contract)
        plan = build_retrieval_plan(
            route=route, plan_contract=plan_contract, preflight=pre, plan_id="p1",
        )
        assert plan.plan_id == "p1"
        assert plan.route_replay_key == route.route_replay_key
        assert plan.metadata_filters.tenant_id == route.tenant_scope

    def test_rejects_ineligible_preflight(self):
        route = make_route(grounding_required=False)
        plan_contract = make_plan_contract()
        pre = run_preflight(route, plan_contract)
        assert not pre.eligible
        with pytest.raises(ValueError):
            build_retrieval_plan(
                route=route, plan_contract=plan_contract, preflight=pre, plan_id="p1",
            )

    def test_static_freshness_enables_cache(self):
        route = make_route(freshness_class=FreshnessClass.STATIC)
        plan_contract = make_plan_contract()
        pre = run_preflight(route, plan_contract)
        plan = build_retrieval_plan(
            route=route, plan_contract=plan_contract, preflight=pre, plan_id="p1",
        )
        assert plan.cache_policy.allow_cache is True

    def test_latest_freshness_disables_cache(self):
        route = make_route(freshness_class=FreshnessClass.LATEST)
        plan_contract = make_plan_contract()
        pre = run_preflight(route, plan_contract)
        plan = build_retrieval_plan(
            route=route, plan_contract=plan_contract, preflight=pre, plan_id="p1",
        )
        assert plan.cache_policy.allow_cache is False

    def test_zero_refine_attempts_picks_abstain_policy(self):
        route = make_route(max_refine_attempts=0)
        plan_contract = make_plan_contract()
        pre = run_preflight(route, plan_contract)
        plan = build_retrieval_plan(
            route=route, plan_contract=plan_contract, preflight=pre, plan_id="p1",
        )
        assert plan.weak_support_policy == "abstain"

    def test_exactness_target_picks_sparse_modes(self):
        route = make_route(support_target=SupportTarget.EXACT_QUOTE)
        plan_contract = make_plan_contract()
        pre = run_preflight(route, plan_contract)
        plan = build_retrieval_plan(
            route=route, plan_contract=plan_contract, preflight=pre, plan_id="p1",
        )
        assert RetrievalMode.SPARSE in plan.retrieval_modes
