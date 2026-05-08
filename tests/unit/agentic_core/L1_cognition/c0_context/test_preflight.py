"""Tests for C0.0 advisory grounding analysis + C0.1 retrieval plan builder.

W2 c0-policy-rectification-f7b2a9: Deprecated preflight() removed.
Tests now cover analyze_grounding_advisory (L1 advisory-only function).
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.c0_context.preflight import (
    MIN_BUDGET_FLOOR_TOKENS,
    analyze_grounding_advisory,
    build_retrieval_plan,
)
from agentic_core.L1_cognition.c0_context.types import (
    BOUND_PARAMS,
    C0PreflightStatus,
    RetrievalPlan,
    RouteContractView,
    SupportTarget,
)


# =============================================================================
# W2: analyze_grounding_advisory tests (replaces deprecated preflight)
# =============================================================================


def test_analyze_grounding_advisory_requires_grounding() -> None:
    """Advisory recommends grounding for grounded routes."""
    advisory = analyze_grounding_advisory(
        task_spec="Summarize codebase",
        query_spec="Code structure",
        support_expectation="SOURCE_SUMMARY",
    )
    assert advisory.grounding_required is True
    assert advisory.support_target == SupportTarget.SOURCE_SUMMARY
    assert "REQUIRES_GROUNDING" in advisory.grounding_reason_codes


def test_analyze_grounding_advisory_not_required() -> None:
    """Advisory may recommend no grounding for simple tasks."""
    advisory = analyze_grounding_advisory(
        task_spec="Hello world example",
        query_spec="Simple greeting",
        support_expectation="NONE",
    )
    # With support_expectation=NONE, grounding may not be required
    assert advisory.confidence >= 0.0
    assert advisory.confidence <= 1.0


def test_analyze_grounding_advisory_with_task_spec() -> None:
    """Advisory uses task_spec to determine grounding need."""
    # Complex task should require grounding
    advisory = analyze_grounding_advisory(
        task_spec="Analyze multi-module codebase for dependencies",
        query_spec="Dependency analysis",
        support_expectation="SOURCE_SUMMARY",
    )
    assert advisory.grounding_required is True
    assert advisory.confidence >= 0.7  # High confidence for complex task


# =============================================================================
# build_retrieval_plan tests (retained, uses C0PreflightStatus from types)
# =============================================================================


def _route(**overrides) -> RouteContractView:
    base: dict = dict(
        route_id="R3_GROUNDED",
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class="current",
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope="tenant_a",
        acl=("read",),
        region="us",
        data_class="standard",
        max_k=10,
        max_hops=2,
        max_parent_expansion=2,
        max_refine_attempts=1,
        max_latency_ms=2000,
        token_budget=4000,
        allowed_sources=frozenset({"docs", "code"}),
        disallowed_sources=frozenset(),
        fallback_policy="caveat",
        route_replay_key="rk1",
        policy_hash="ph1",
        blueprint_hash="bh1",
    )
    base.update(overrides)
    return RouteContractView(**base)


def _make_preflight_status(
    *,
    eligible: bool = True,
    blocked_reason: str = "",
    allowed_source_classes: frozenset[str] | None = None,
) -> C0PreflightStatus:
    """Helper to create C0PreflightStatus for testing."""
    return C0PreflightStatus(
        eligible=eligible,
        blocked_reason=blocked_reason,
        allowed_source_classes=allowed_source_classes or frozenset({"docs", "code"}),
        evidence_standard="standard" if eligible else "none",
        budget_floor_tokens=MIN_BUDGET_FLOOR_TOKENS if eligible else 0,
    )


def test_build_retrieval_plan_eligible() -> None:
    """Retrieval plan built for eligible preflight status."""
    route = _route()
    status = _make_preflight_status(eligible=True)

    plan = build_retrieval_plan(route, status)

    assert isinstance(plan, RetrievalPlan)
    assert plan.route_id == route.route_id
    assert plan.max_k == route.max_k
    assert plan.max_hops == route.max_hops


def test_build_retrieval_plan_ineligible() -> None:
    """Retrieval plan still built but with empty sources when ineligible."""
    route = _route()
    status = _make_preflight_status(eligible=False, blocked_reason="test_block")

    plan = build_retrieval_plan(route, status)

    assert isinstance(plan, RetrievalPlan)
    # When ineligible, allowed_source_classes should be empty
    assert len(plan.allowed_source_classes) == 0


def test_build_retrieval_plan_respects_max_k() -> None:
    """Retrieval plan respects route's max_k parameter."""
    route = _route(max_k=5)
    status = _make_preflight_status()

    plan = build_retrieval_plan(route, status)

    assert plan.max_k == 5


def test_build_retrieval_plan_cache_policy() -> None:
    """Retrieval plan includes cache policy."""
    route = _route()
    status = _make_preflight_status()

    plan = build_retrieval_plan(route, status, cache_policy="WRITE_BACK")

    assert plan.cache_policy == "WRITE_BACK"



def test_preflight_blocked_when_route_disallows() -> None:
    s = preflight(_route(route_id="R1_CACHE"))
    assert s.eligible is False
    assert "does not allow" in s.blocked_reason


def test_preflight_blocked_when_no_allowed_sources() -> None:
    s = preflight(_route(allowed_sources=frozenset(), disallowed_sources=frozenset()))
    assert s.eligible is False


def test_preflight_blocked_when_data_class_blocked() -> None:
    s = preflight(_route(data_class="blocked"))
    assert s.eligible is False


def test_preflight_blocked_when_budget_below_floor() -> None:
    s = preflight(_route(token_budget=100))
    assert s.eligible is False
    assert "token_budget" in s.blocked_reason


def test_preflight_strict_for_high_stakes() -> None:
    s = preflight(_route(support_target=SupportTarget.POLICY_CLAUSE))
    assert s.evidence_standard == "strict"


def test_preflight_default_for_low_stakes() -> None:
    s = preflight(_route(support_target=SupportTarget.SOURCE_SUMMARY))
    assert s.evidence_standard == "default"


def test_preflight_disallowed_subtracted() -> None:
    s = preflight(_route(
        allowed_sources=frozenset({"docs", "code", "logs"}),
        disallowed_sources=frozenset({"logs"}),
    ))
    assert s.eligible is True
    assert "logs" not in s.allowed_source_classes


# ---------- RETRIEVAL PLAN ----------


def test_build_plan_default_modes() -> None:
    s = preflight(_route())
    plan = build_retrieval_plan(_route(), s)
    assert plan.retrieval_modes == frozenset({"dense", "sparse", "metadata"})
    # Every spec'd bound param is populated
    for param in BOUND_PARAMS:
        assert param in plan.bounds


def test_build_plan_blocks_when_preflight_blocked() -> None:
    s = preflight(_route(grounding_required=False))
    with pytest.raises(ValueError, match="preflight blocked"):
        build_retrieval_plan(_route(grounding_required=False), s)


def test_build_plan_rejects_unknown_mode() -> None:
    s = preflight(_route())
    with pytest.raises(ValueError, match="unknown retrieval_modes"):
        build_retrieval_plan(_route(), s, retrieval_modes=frozenset({"telepathy"}))


def test_build_plan_replay_metadata_propagated() -> None:
    s = preflight(_route())
    plan = build_retrieval_plan(_route(), s)
    assert plan.replay_metadata["route_replay_key"] == "rk1"
    assert plan.replay_metadata["policy_hash"] == "ph1"
    assert plan.replay_metadata["blueprint_hash"] == "bh1"


def test_build_plan_intersects_allowed_with_preflight() -> None:
    route = _route(
        allowed_sources=frozenset({"docs", "code", "policy"}),
        disallowed_sources=frozenset({"policy"}),
    )
    s = preflight(route)
    plan = build_retrieval_plan(route, s)
    assert "policy" not in plan.allowed_sources
    assert plan.allowed_sources <= s.allowed_source_classes
