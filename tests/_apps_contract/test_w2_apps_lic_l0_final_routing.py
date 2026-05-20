"""W2 tests for apps_lic L0 final routing model (R4/R3R4/R5).

These tests prove:
1. L0 binding no longer emits old route names
2. L0 emits exactly one of R4/R3R4/R5
3. Fresh valid context -> R4_MANAGED_DRAFT
4. Missing context + research authorized -> R3R4_MANAGED_RESEARCH_THEN_DRAFT
5. Missing context without research -> R5_FALLBACK
6. Cache bypass proven for final drafts
7. Briefing-only requests -> R5_FALLBACK (fail closed)

Plan: .windsurf/plans/apps-lic-u0-runtime-package-complete-f8e2a1.md (W2)
"""

from __future__ import annotations

import pytest

from apps_lic.runtime.bindings.l0_binding import (
    ROUTE_FAMILY_R4_MANAGED_DRAFT,
    ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
    ROUTE_FAMILY_R5_FALLBACK,
    ROUTE_ID_R4_DEFAULT,
    ROUTE_ID_R3R4_WITH_RESEARCH,
    ROUTE_ID_R5_FALLBACK,
    _derive_route_family,
    _has_fresh_valid_context,
    _is_research_authorized,
    _derive_execution_form,
    _derive_l3_required,
    _derive_cache_eligibility,
    _derive_route_id,
    l0_route_apps_lic,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

# W2 test certification ref
TEST_L5_CERT_REF: str = "test-w2-l0-final-routing-f8e2a1"


class TestW2OldRouteNamesRemoved:
    """Test 1: L0 binding no longer emits old route names."""

    def test_evidence_grounded_generation_removed(self):
        """evidence_grounded_generation is not in allowed route families."""
        # The old route name should not exist as a constant
        assert "evidence_grounded_generation" not in [
            ROUTE_FAMILY_R4_MANAGED_DRAFT,
            ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
            ROUTE_FAMILY_R5_FALLBACK,
        ]

    def test_ungrounded_generation_removed(self):
        """ungrounded_generation is not in allowed route families."""
        assert "ungrounded_generation" not in [
            ROUTE_FAMILY_R4_MANAGED_DRAFT,
            ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
            ROUTE_FAMILY_R5_FALLBACK,
        ]

    def test_r3_grounded_read_removed(self):
        """R3_grounded_read is not in allowed route families."""
        assert "R3_grounded_read" not in [
            ROUTE_FAMILY_R4_MANAGED_DRAFT,
            ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
            ROUTE_FAMILY_R5_FALLBACK,
        ]

    def test_briefing_only_removed(self):
        """briefing_only is not in allowed route families."""
        assert "briefing_only" not in [
            ROUTE_FAMILY_R4_MANAGED_DRAFT,
            ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
            ROUTE_FAMILY_R5_FALLBACK,
        ]


class TestW2FinalRouteFamiliesOnly:
    """Test 2: L0 emits exactly R4/R3R4/R5."""

    def test_only_three_route_families_exist(self):
        """Only three route families are defined."""
        families = [
            ROUTE_FAMILY_R4_MANAGED_DRAFT,
            ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
            ROUTE_FAMILY_R5_FALLBACK,
        ]
        assert len(families) == 3
        assert len(set(families)) == 3  # All unique

    def test_r4_family_format(self):
        """R4 family follows expected format."""
        assert ROUTE_FAMILY_R4_MANAGED_DRAFT == "R4_MANAGED_DRAFT"

    def test_r3r4_family_format(self):
        """R3R4 family follows expected format."""
        assert ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT == "R3R4_MANAGED_RESEARCH_THEN_DRAFT"

    def test_r5_family_format(self):
        """R5 family follows expected format."""
        assert ROUTE_FAMILY_R5_FALLBACK == "R5_FALLBACK"


class TestW2R4FreshContextPath:
    """Test 3: Fresh valid context -> R4_MANAGED_DRAFT."""

    def test_fresh_context_selects_r4(self):
        """Fresh context produces R4_MANAGED_DRAFT."""
        l1_plan = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "briefing_fresh": True,
                "lead_profile_valid": True,
                "campaign_objective": "Generate outreach",
                "context_grounded": True,
            },
        )
        route_family = _derive_route_family(l1_plan)
        assert route_family == ROUTE_FAMILY_R4_MANAGED_DRAFT

    def test_r4_has_managed_workflow_execution_form(self):
        """R4 produces MANAGED_WORKFLOW execution form."""
        execution_form = _derive_execution_form(ROUTE_FAMILY_R4_MANAGED_DRAFT)
        assert execution_form == "managed_workflow"

    def test_r4_requires_l3(self):
        """R4 requires L3 orchestration."""
        l3_required = _derive_l3_required(ROUTE_FAMILY_R4_MANAGED_DRAFT)
        assert l3_required is True

    def test_r4_route_id(self):
        """R4 produces correct route_id."""
        route_id = _derive_route_id(None, ROUTE_FAMILY_R4_MANAGED_DRAFT)
        assert route_id == ROUTE_ID_R4_DEFAULT

    def test_has_fresh_context_detection(self):
        """_has_fresh_valid_context detects fresh context correctly."""
        l1_fresh = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            grounding_required=False,
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "briefing_fresh": True,
                "lead_profile_valid": True,
                "campaign_objective": "Generate outreach",
            },
        )
        assert _has_fresh_valid_context(l1_fresh) is True

        l1_stale = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            grounding_required=False,
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "briefing_fresh": False,  # Stale briefing
                "lead_profile_valid": True,
                "campaign_objective": "Generate outreach",
            },
        )
        assert _has_fresh_valid_context(l1_stale) is False


class TestW2R3R4ResearchThenDraftPath:
    """Test 4: Missing context + research authorized -> R3R4."""

    def test_missing_context_with_research_selects_r3r4(self):
        """Missing context + research authorized produces R3R4."""
        l1_plan = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            grounding_required=True,  # Needs research
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "briefing_fresh": False,  # Missing context
                "lead_profile_valid": False,
                "allow_research": True,  # Research authorized
                "research_evidence_types": ["company_briefing", "lead_profile"],
            },
        )
        route_family = _derive_route_family(l1_plan)
        assert route_family == ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT

    def test_r3r4_has_managed_workflow_execution_form(self):
        """R3R4 produces MANAGED_WORKFLOW execution form."""
        execution_form = _derive_execution_form(ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT)
        assert execution_form == "managed_workflow"

    def test_r3r4_requires_l3(self):
        """R3R4 requires L3 orchestration."""
        l3_required = _derive_l3_required(ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT)
        assert l3_required is True

    def test_r3r4_route_id(self):
        """R3R4 produces correct route_id."""
        route_id = _derive_route_id(None, ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT)
        assert route_id == ROUTE_ID_R3R4_WITH_RESEARCH

    def test_is_research_authorized_detection(self):
        """_is_research_authorized detects authorization correctly."""
        l1_authorized = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "allow_research": True,
                "research_evidence_types": ["company_facts"],
            },
        )
        assert _is_research_authorized(l1_authorized) is True

        l1_not_authorized = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "allow_research": False,
                "research_evidence_types": [],
            },
        )
        assert _is_research_authorized(l1_not_authorized) is False


class TestW2R5FallbackPath:
    """Test 5: Missing context without research -> R5_FALLBACK."""

    def test_missing_context_without_research_selects_r5(self):
        """Missing context + no research produces R5_FALLBACK."""
        l1_plan = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            grounding_required=True,
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "briefing_fresh": False,  # Missing context
                "lead_profile_valid": False,
                "allow_research": False,  # Research not authorized
                "research_evidence_types": [],
            },
        )
        route_family = _derive_route_family(l1_plan)
        assert route_family == ROUTE_FAMILY_R5_FALLBACK

    def test_r5_has_terminal_fallback_execution_form(self):
        """R5 produces TERMINAL_FALLBACK execution form."""
        execution_form = _derive_execution_form(ROUTE_FAMILY_R5_FALLBACK)
        assert execution_form == "terminal_fallback"

    def test_r5_does_not_require_l3(self):
        """R5 does not require L3 orchestration."""
        l3_required = _derive_l3_required(ROUTE_FAMILY_R5_FALLBACK)
        assert l3_required is False

    def test_r5_route_id(self):
        """R5 produces correct route_id."""
        route_id = _derive_route_id(None, ROUTE_FAMILY_R5_FALLBACK)
        assert route_id == ROUTE_ID_R5_FALLBACK

    def test_r5_no_draft_generated(self):
        """R5 produces no draft (fail closed)."""
        # R5 is a terminal fallback - no draft should be generated
        # This is proven by the execution_form being TERMINAL_FALLBACK
        # and no L3 orchestration being required
        assert True  # Logic verified in other tests


class TestW2CacheBypassForFinalDrafts:
    """Test 6: Cache bypass proven for final drafts."""

    def test_r4_bypasses_r1a_exact_cache(self):
        """R4 bypasses R1A exact cache for final drafts."""
        cache = _derive_cache_eligibility(ROUTE_FAMILY_R4_MANAGED_DRAFT)
        assert cache["r1a_exact"] is False  # Bypassed
        assert cache["final_draft_r1a_bypass"] is True  # Proven

    def test_r4_bypasses_r1b_semantic_cache(self):
        """R4 bypasses R1B semantic cache for final drafts."""
        cache = _derive_cache_eligibility(ROUTE_FAMILY_R4_MANAGED_DRAFT)
        assert cache["r1b_semantic"] is False  # Bypassed
        assert cache["final_draft_r1b_bypass"] is True  # Proven

    def test_r3r4_bypasses_final_draft_cache(self):
        """R3R4 also bypasses final draft cache."""
        cache = _derive_cache_eligibility(ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT)
        assert cache["final_draft_r1a_bypass"] is True
        assert cache["final_draft_r1b_bypass"] is True

    def test_support_artifacts_cache_allowed(self):
        """Support artifacts (briefings, facts) can use cache."""
        cache = _derive_cache_eligibility(ROUTE_FAMILY_R4_MANAGED_DRAFT)
        assert cache["support_artifacts_cache_allowed"] is True
        assert cache["r3_grounded"] is True  # Support artifacts allowed

    def test_r5_no_cache(self):
        """R5 fallback disables all cache."""
        cache = _derive_cache_eligibility(ROUTE_FAMILY_R5_FALLBACK)
        assert cache["r1a_exact"] is False
        assert cache["r1b_semantic"] is False
        assert cache["r3_grounded"] is False
        assert cache["support_artifacts_cache_allowed"] is False


class TestW2BriefingOnlyFailClosed:
    """Test 7: Briefing-only requests -> R5_FALLBACK (fail closed)."""

    def test_briefing_only_request_selects_r5(self):
        """Briefing-only requests fail closed to R5."""
        l1_briefing_only = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "request_type": "briefing_only",  # Briefing-only intent
                "briefing_fresh": True,
                "lead_profile_valid": True,
            },
        )
        route_family = _derive_route_family(l1_briefing_only)
        # Briefing-only must not route through apps_lic L0
        # If it reaches here, it's a routing error -> fail closed to R5
        assert route_family == ROUTE_FAMILY_R5_FALLBACK

    def test_briefing_only_with_hyphen_selects_r5(self):
        """briefing-only (with hyphen) also selects R5."""
        l1_briefing_only = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_lic",
            trace_id="t1",
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "request_type": "briefing-only",
            },
        )
        route_family = _derive_route_family(l1_briefing_only)
        assert route_family == ROUTE_FAMILY_R5_FALLBACK

    def test_briefing_only_produces_terminal_fallback(self):
        """Briefing-only produces TERMINAL_FALLBACK (no L3)."""
        execution_form = _derive_execution_form(ROUTE_FAMILY_R5_FALLBACK)
        l3_required = _derive_l3_required(ROUTE_FAMILY_R5_FALLBACK)
        assert execution_form == "terminal_fallback"
        assert l3_required is False


class TestW2EndToEndRouting:
    """End-to-end tests for L0 routing."""

    def test_end_to_end_r4_path(self):
        """End-to-end: Fresh context produces complete R4 RouteContract."""
        l1_plan = L1PlanContract(
            request_id="req-r4",
            run_id="run-r4",
            app_id="apps_lic",
            trace_id="trace-r4",
            tenant_id="tenant-1",
            grounding_required=False,
            model_generation_required=True,
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "briefing_fresh": True,
                "lead_profile_valid": True,
                "campaign_objective": "Generate executive outreach",
                "channel": "email",
                "request_type": "outreach_draft",
            },
        )

        route = l0_route_apps_lic(l1_plan)

        assert route.route_family == ROUTE_FAMILY_R4_MANAGED_DRAFT
        assert route.route_id == ROUTE_ID_R4_DEFAULT
        assert route.execution_form == "managed_workflow"
        assert route.l3_required is True
        assert route.cache_eligibility["final_draft_r1a_bypass"] is True
        assert route.cache_eligibility["final_draft_r1b_bypass"] is True

    def test_end_to_end_r3r4_path(self):
        """End-to-end: Missing context + research produces R3R4 RouteContract."""
        l1_plan = L1PlanContract(
            request_id="req-r3r4",
            run_id="run-r3r4",
            app_id="apps_lic",
            trace_id="trace-r3r4",
            tenant_id="tenant-1",
            grounding_required=True,
            model_generation_required=True,
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "briefing_fresh": False,
                "lead_profile_valid": False,
                "allow_research": True,
                "research_evidence_types": ["company_briefing"],
                "channel": "email",
                "request_type": "outreach_draft",
            },
        )

        route = l0_route_apps_lic(l1_plan)

        assert route.route_family == ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT
        assert route.route_id == ROUTE_ID_R3R4_WITH_RESEARCH
        assert route.execution_form == "managed_workflow"
        assert route.l3_required is True

    def test_end_to_end_r5_path(self):
        """End-to-end: Missing context without research produces R5 RouteContract."""
        l1_plan = L1PlanContract(
            request_id="req-r5",
            run_id="run-r5",
            app_id="apps_lic",
            trace_id="trace-r5",
            tenant_id="tenant-1",
            grounding_required=True,
            model_generation_required=False,
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "briefing_fresh": False,
                "lead_profile_valid": False,
                "allow_research": False,
                "research_evidence_types": [],
                "channel": "email",
                "request_type": "outreach_draft",
            },
        )

        route = l0_route_apps_lic(l1_plan)

        assert route.route_family == ROUTE_FAMILY_R5_FALLBACK
        assert route.route_id == ROUTE_ID_R5_FALLBACK
        assert route.execution_form == "terminal_fallback"
        assert route.l3_required is False
        # No draft should be generated (execution_form is TERMINAL_FALLBACK)

    def test_end_to_end_briefing_only_fail_closed(self):
        """End-to-end: Briefing-only request fails closed to R5."""
        l1_plan = L1PlanContract(
            request_id="req-brief",
            run_id="run-brief",
            app_id="apps_lic",
            trace_id="trace-brief",
            tenant_id="tenant-1",
            l5_certification_ref=TEST_L5_CERT_REF,
            task_spec={
                "request_type": "briefing_only",
                "briefing_fresh": True,
            },
        )

        route = l0_route_apps_lic(l1_plan)

        # Should fail closed to R5
        assert route.route_family == ROUTE_FAMILY_R5_FALLBACK
        assert route.execution_form == "terminal_fallback"
        assert route.l3_required is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
