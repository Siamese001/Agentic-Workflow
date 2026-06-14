"""Unit tests for agentic_core.L4_state.contracts.app_domain.

Wave 3.2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 state-contract
surface. ``app_domain`` (fan_in=15, L4_STATE) holds the Fort Knox per-app domain
contract records (frozen value bundles UWG resolves at L4). Coverage of the
closed-vocabulary ``__post_init__`` invariants (AppDomainContractError paths),
defaults, frozen immutability, and the helper surface.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L4_state.contracts.app_domain import (
    APP_DOMAIN_RECORD_TYPES,
    AppCapabilityProfileRecord,
    AppDomainContractError,
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
    ScoreDimension,
    TaskClassEntry,
    app_domain_record_kind,
)


class TestAppDomainContractError:
    def test_is_valueerror(self) -> None:
        assert issubclass(AppDomainContractError, ValueError)


class TestScoreDimension:
    def test_construction_and_defaults(self) -> None:
        d = ScoreDimension(
            dimension_id="d1", description="desc", weight=0.5,
            grader_type="deterministic",
        )
        assert d.min_required_score == -1.0
        assert d.evidence_required is True
        assert d.fail_closed_if_unknown is True
        assert d.trajectory_match_mode == ""
        assert d.score_bands == ()
        assert d.taxonomy_class == ""

    def test_frozen(self) -> None:
        d = ScoreDimension(
            dimension_id="d1", description="x", weight=0.5,
            grader_type="hybrid",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.weight = 0.9  # type: ignore[misc]

    def test_missing_dimension_id_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(dimension_id="", description="x", weight=0.5, grader_type="hybrid")

    def test_bad_grader_type_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(dimension_id="d1", description="x", weight=0.5, grader_type="nope")

    @pytest.mark.parametrize("weight", [-0.1, 1.1, 2.0])
    def test_weight_out_of_range_raises(self, weight: float) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(dimension_id="d1", description="x", weight=weight, grader_type="hybrid")

    def test_min_required_score_out_of_range_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(
                dimension_id="d1", description="x", weight=0.5,
                grader_type="hybrid", min_required_score=1.5,
            )

    def test_min_required_score_sentinel_allowed(self) -> None:
        d = ScoreDimension(
            dimension_id="d1", description="x", weight=0.5,
            grader_type="hybrid", min_required_score=-1.0,
        )
        assert d.min_required_score == -1.0

    def test_bad_trajectory_mode_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(
                dimension_id="d1", description="x", weight=0.5,
                grader_type="tool_calls", trajectory_match_mode="bogus",
            )

    def test_bad_taxonomy_class_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(
                dimension_id="d1", description="x", weight=0.5,
                grader_type="hybrid", taxonomy_class="bogus",
            )


class TestTaskClassEntry:
    def test_construction_and_defaults(self) -> None:
        t = TaskClassEntry(task_class="resume_generation", kind="generation", description="d")
        assert t.risk_tier == "standard"
        assert t.hitl_required is False

    def test_missing_task_class_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            TaskClassEntry(task_class="", kind="generation", description="d")

    def test_bad_kind_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            TaskClassEntry(task_class="tc", kind="nope", description="d")


class TestSubcontractValidators:
    """_validate_status / _validate_app_task fire through every subcontract."""

    def test_input_contract_ok_and_defaults(self) -> None:
        r = AppInputContractRecord(
            input_contract_id="ic-1", app_id="apps_rg", task_class="tc",
            version="1", status="active", missing_input_behavior="fail_closed",
            ambiguity_behavior="fail_closed",
        )
        assert r.created_by_surface == "UWG"
        assert r.required_inputs == ()
        assert r.deterministic_digest == ""

    def test_bad_status_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppInputContractRecord(
                input_contract_id="ic-1", app_id="apps_rg", task_class="tc",
                version="1", status="bogus", missing_input_behavior="fail_closed",
                ambiguity_behavior="fail_closed",
            )

    def test_non_apps_prefixed_app_id_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppInputContractRecord(
                input_contract_id="ic-1", app_id="core", task_class="tc",
                version="1", status="active", missing_input_behavior="fail_closed",
                ambiguity_behavior="fail_closed",
            )

    def test_missing_task_class_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppInputContractRecord(
                input_contract_id="ic-1", app_id="apps_rg", task_class="",
                version="1", status="active", missing_input_behavior="fail_closed",
                ambiguity_behavior="fail_closed",
            )

    def test_output_schema_bad_output_type_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppOutputSchemaRecord(
                output_schema_id="os-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", output_type="pdf",
            )

    def test_output_schema_ok(self) -> None:
        r = AppOutputSchemaRecord(
            output_schema_id="os-1", app_id="apps_rg", task_class="tc",
            version="1", status="active", output_type="markdown",
        )
        assert r.output_type == "markdown"

    def test_threshold_profile_out_of_range_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppThresholdProfileRecord(
                threshold_profile_id="tp-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", overall_pass_threshold=1.5,
            )

    def test_threshold_profile_bad_dimension_minimum_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppThresholdProfileRecord(
                threshold_profile_id="tp-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", overall_pass_threshold=0.8,
                dimension_minimums={"d1": 2.0},
            )

    def test_threshold_profile_bad_unknown_policy_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppThresholdProfileRecord(
                threshold_profile_id="tp-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", overall_pass_threshold=0.8,
                unknown_policy="bogus",
            )

    def test_retrieval_profile_bad_freshness_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppRetrievalProfileRecord(
                retrieval_profile_id="rp-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", freshness_class="whenever",
            )

    def test_capability_profile_bad_side_effect_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppCapabilityProfileRecord(
                capability_profile_id="cp-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", side_effect_class="nuke",
            )

    def test_prompt_profile_ok(self) -> None:
        r = AppPromptProfileRecord(
            prompt_profile_id="pp-1", app_id="apps_rg", task_class="tc",
            version="1", status="active", output_schema_ref="os-1",
        )
        assert r.created_by_surface == "UWG"

    def test_route_profile_missing_default_route_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppRouteProfileRecord(
                route_profile_id="rpr-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", default_route_id="",
            )

    def test_orchestration_profile_bad_kind_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppOrchestrationProfileRecord(
                orchestration_profile_id="op-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", orchestration_kind="spaghetti",
            )

    def test_fixture_bad_type_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppFixtureRecord(
                fixture_id="fx-1", app_id="apps_rg", task_class="tc",
                fixture_type="weird", version="1", status="active",
                input_ref="ref", expected_disposition="ALLOW",
            )

    def test_negative_control_missing_failure_dimension_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppNegativeControlRecord(
                negative_control_id="nc-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", expected_failure_dimension="",
                expected_failure_reason="r", input_ref="ref",
            )


class TestAppEvalRubricRecord:
    def test_requires_at_least_one_dimension(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppEvalRubricRecord(
                eval_rubric_id="er-1", app_id="apps_rg", task_class="tc",
                version="1", status="active",
            )

    def test_duplicate_dimension_id_raises(self) -> None:
        dim = ScoreDimension(dimension_id="d1", description="x", weight=0.5, grader_type="hybrid")
        with pytest.raises(AppDomainContractError):
            AppEvalRubricRecord(
                eval_rubric_id="er-1", app_id="apps_rg", task_class="tc",
                version="1", status="active", score_dimensions=(dim, dim),
            )

    def test_valid_rubric(self) -> None:
        dim = ScoreDimension(dimension_id="d1", description="x", weight=0.5, grader_type="hybrid")
        r = AppEvalRubricRecord(
            eval_rubric_id="er-1", app_id="apps_rg", task_class="tc",
            version="1", status="active", score_dimensions=(dim,),
        )
        assert len(r.score_dimensions) == 1


class TestAppGraderRosterRecord:
    def test_requires_at_least_one_grader(self) -> None:
        with pytest.raises(AppDomainContractError):
            AppGraderRosterRecord(
                grader_roster_id="gr-1", app_id="apps_rg", task_class="tc",
                version="1", status="active",
            )

    def test_deterministic_only_allowed(self) -> None:
        r = AppGraderRosterRecord(
            grader_roster_id="gr-1", app_id="apps_rg", task_class="tc",
            version="1", status="active", deterministic_graders=("g1",),
        )
        assert r.deterministic_graders == ("g1",)


class TestAppDomainContractRecord:
    def _draft(self, **kw: object) -> AppDomainContractRecord:
        base = dict(
            app_domain_contract_id="adc-1", app_id="apps_rg", app_version="1",
            domain="resume", owner_surface="apps_rg", status="draft",
        )
        base.update(kw)
        return AppDomainContractRecord(**base)  # type: ignore[arg-type]

    def test_draft_construction(self) -> None:
        r = self._draft()
        assert r.created_by_surface == "UWG"
        assert r.task_classes == ()

    def test_app_id_must_start_with_apps(self) -> None:
        with pytest.raises(AppDomainContractError):
            self._draft(app_id="core", owner_surface="core")

    def test_owner_surface_must_equal_app_id(self) -> None:
        with pytest.raises(AppDomainContractError):
            self._draft(owner_surface="apps_other")

    def test_missing_domain_raises(self) -> None:
        with pytest.raises(AppDomainContractError):
            self._draft(domain="")

    def test_active_requires_task_classes(self) -> None:
        with pytest.raises(AppDomainContractError):
            self._draft(status="active", negative_control_refs=("nc-1",))

    def test_active_requires_negative_control(self) -> None:
        tc = TaskClassEntry(task_class="tc", kind="generation", description="d")
        with pytest.raises(AppDomainContractError):
            self._draft(status="active", task_classes=(tc,))

    def test_active_valid(self) -> None:
        tc = TaskClassEntry(task_class="tc", kind="generation", description="d")
        r = self._draft(status="active", task_classes=(tc,), negative_control_refs=("nc-1",))
        assert r.status == "active"

    def test_frozen(self) -> None:
        r = self._draft()
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.domain = "other"  # type: ignore[misc]


class TestHelpers:
    def test_record_kind_returns_classname(self) -> None:
        dim = ScoreDimension(dimension_id="d1", description="x", weight=0.5, grader_type="hybrid")
        assert app_domain_record_kind(dim) == "ScoreDimension"

    def test_record_types_tuple_includes_top_level(self) -> None:
        assert AppDomainContractRecord in APP_DOMAIN_RECORD_TYPES
        assert all(isinstance(t, type) for t in APP_DOMAIN_RECORD_TYPES)
