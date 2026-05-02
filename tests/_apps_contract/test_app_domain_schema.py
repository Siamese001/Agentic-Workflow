"""Schema unit tests for the app-domain contract pack.

Covers the Phase 7.1 test matrix from the discovery report:
valid contract passes, missing fields fail closed, duplicate
dimensions fail, vocabulary rejection.

Plan: ``.windsurf/plans/apps-domain-contract-fortknox-c4d8e2.md`` §P7.1.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.contracts import (
    AppDomainContractError,
    AppDomainContractRecord,
    AppEvalRubricRecord,
    AppInputContractRecord,
    AppOutputSchemaRecord,
    AppThresholdProfileRecord,
    ScoreDimension,
    TaskClassEntry,
    app_domain_record_kind,
)
from agentic_core.L4_state.contracts.records import stamp_digest


def _make_score_dim(dim_id: str = "factual_grounding") -> ScoreDimension:
    return ScoreDimension(
        dimension_id=dim_id,
        description="test",
        weight=0.25,
        grader_type="deterministic",
        min_required_score=0.95,
        evidence_required=True,
        fail_closed_if_unknown=True,
    )


# ---------------------------------------------------------------------------
# ScoreDimension
# ---------------------------------------------------------------------------


class TestScoreDimension:
    def test_valid_dimension_constructs(self) -> None:
        dim = _make_score_dim()
        assert dim.dimension_id == "factual_grounding"
        assert dim.grader_type == "deterministic"

    def test_empty_dimension_id_fails(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(
                dimension_id="",
                description="x",
                weight=0.5,
                grader_type="deterministic",
            )

    def test_invalid_grader_type_fails(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(
                dimension_id="x",
                description="x",
                weight=0.5,
                grader_type="magic",
            )

    def test_weight_out_of_range_fails(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(
                dimension_id="x",
                description="x",
                weight=1.5,
                grader_type="deterministic",
            )

    def test_min_required_score_out_of_range_fails(self) -> None:
        with pytest.raises(AppDomainContractError):
            ScoreDimension(
                dimension_id="x",
                description="x",
                weight=0.5,
                grader_type="deterministic",
                min_required_score=1.5,
            )

    def test_min_required_score_minus_one_allowed(self) -> None:
        # -1.0 means "no minimum"
        dim = ScoreDimension(
            dimension_id="x",
            description="x",
            weight=0.5,
            grader_type="deterministic",
            min_required_score=-1.0,
        )
        assert dim.min_required_score == -1.0


# ---------------------------------------------------------------------------
# TaskClassEntry
# ---------------------------------------------------------------------------


class TestTaskClassEntry:
    def test_valid_task_class(self) -> None:
        tc = TaskClassEntry(task_class="x", kind="generation", description="x")
        assert tc.task_class == "x"

    def test_empty_task_class_fails(self) -> None:
        with pytest.raises(AppDomainContractError):
            TaskClassEntry(task_class="", kind="generation", description="x")

    def test_invalid_kind_fails(self) -> None:
        with pytest.raises(AppDomainContractError):
            TaskClassEntry(task_class="x", kind="bogus", description="x")


# ---------------------------------------------------------------------------
# AppInputContractRecord
# ---------------------------------------------------------------------------


class TestAppInputContractRecord:
    def _base_kwargs(self) -> dict:
        return {
            "input_contract_id": "aic::apps_rg::rg::v1",
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "version": "1.0.0",
            "status": "active",
            "missing_input_behavior": "fail_closed",
            "ambiguity_behavior": "escalate",
        }

    def test_valid(self) -> None:
        rec = AppInputContractRecord(**self._base_kwargs())
        assert rec.app_id == "apps_rg"

    def test_bad_status_fails(self) -> None:
        kwargs = self._base_kwargs() | {"status": "live"}
        with pytest.raises(AppDomainContractError):
            AppInputContractRecord(**kwargs)

    def test_app_id_without_apps_prefix_fails(self) -> None:
        kwargs = self._base_kwargs() | {"app_id": "rg"}
        with pytest.raises(AppDomainContractError):
            AppInputContractRecord(**kwargs)

    def test_empty_task_class_fails(self) -> None:
        kwargs = self._base_kwargs() | {"task_class": ""}
        with pytest.raises(AppDomainContractError):
            AppInputContractRecord(**kwargs)


# ---------------------------------------------------------------------------
# AppOutputSchemaRecord
# ---------------------------------------------------------------------------


class TestAppOutputSchemaRecord:
    def _base_kwargs(self) -> dict:
        return {
            "output_schema_id": "aos::apps_rg::rg::v1",
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "version": "1.0.0",
            "status": "active",
            "output_type": "structured_record",
        }

    def test_valid(self) -> None:
        AppOutputSchemaRecord(**self._base_kwargs())

    def test_invalid_output_type_fails(self) -> None:
        kwargs = self._base_kwargs() | {"output_type": "zip_archive"}
        with pytest.raises(AppDomainContractError):
            AppOutputSchemaRecord(**kwargs)


# ---------------------------------------------------------------------------
# AppEvalRubricRecord
# ---------------------------------------------------------------------------


class TestAppEvalRubricRecord:
    def _base_kwargs(self) -> dict:
        return {
            "eval_rubric_id": "aer::apps_rg::rg::v1",
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "version": "1.0.0",
            "status": "active",
            "score_dimensions": (_make_score_dim("factual"),),
        }

    def test_valid(self) -> None:
        AppEvalRubricRecord(**self._base_kwargs())

    def test_empty_score_dimensions_fails(self) -> None:
        kwargs = self._base_kwargs() | {"score_dimensions": ()}
        with pytest.raises(AppDomainContractError):
            AppEvalRubricRecord(**kwargs)

    def test_duplicate_dimension_id_fails(self) -> None:
        kwargs = self._base_kwargs() | {
            "score_dimensions": (_make_score_dim("d1"), _make_score_dim("d1")),
        }
        with pytest.raises(AppDomainContractError):
            AppEvalRubricRecord(**kwargs)


# ---------------------------------------------------------------------------
# AppThresholdProfileRecord
# ---------------------------------------------------------------------------


class TestAppThresholdProfileRecord:
    def _base_kwargs(self) -> dict:
        return {
            "threshold_profile_id": "atp::apps_rg::rg::v1",
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "version": "1.0.0",
            "status": "active",
            "overall_pass_threshold": 0.75,
        }

    def test_valid(self) -> None:
        AppThresholdProfileRecord(**self._base_kwargs())

    def test_out_of_range_overall_fails(self) -> None:
        kwargs = self._base_kwargs() | {"overall_pass_threshold": 1.5}
        with pytest.raises(AppDomainContractError):
            AppThresholdProfileRecord(**kwargs)

    def test_bad_dimension_minimum_fails(self) -> None:
        kwargs = self._base_kwargs() | {"dimension_minimums": {"d": 1.5}}
        with pytest.raises(AppDomainContractError):
            AppThresholdProfileRecord(**kwargs)

    def test_bad_unknown_policy_fails(self) -> None:
        kwargs = self._base_kwargs() | {"unknown_policy": "silently_pass"}
        with pytest.raises(AppDomainContractError):
            AppThresholdProfileRecord(**kwargs)


# ---------------------------------------------------------------------------
# AppDomainContractRecord
# ---------------------------------------------------------------------------


class TestAppDomainContractRecord:
    def _base_kwargs(self) -> dict:
        return {
            "app_domain_contract_id": "adc::apps_rg::v1",
            "app_id": "apps_rg",
            "app_version": "1.0.0",
            "domain": "resume_generation",
            "owner_surface": "apps_rg",
            "status": "active",
            "task_classes": (TaskClassEntry(task_class="rg", kind="generation", description="x"),),
            "negative_control_refs": ("aneg::apps_rg::rg::x",),
        }

    def test_valid(self) -> None:
        AppDomainContractRecord(**self._base_kwargs())

    def test_owner_surface_must_match_app_id(self) -> None:
        kwargs = self._base_kwargs() | {"owner_surface": "apps_lic"}
        with pytest.raises(AppDomainContractError):
            AppDomainContractRecord(**kwargs)

    def test_active_without_task_classes_fails(self) -> None:
        kwargs = self._base_kwargs() | {"task_classes": ()}
        with pytest.raises(AppDomainContractError):
            AppDomainContractRecord(**kwargs)

    def test_active_without_negative_controls_fails(self) -> None:
        kwargs = self._base_kwargs() | {"negative_control_refs": ()}
        with pytest.raises(AppDomainContractError):
            AppDomainContractRecord(**kwargs)

    def test_draft_without_task_classes_allowed(self) -> None:
        kwargs = self._base_kwargs() | {"status": "draft", "task_classes": ()}
        AppDomainContractRecord(**kwargs)


# ---------------------------------------------------------------------------
# Digest determinism
# ---------------------------------------------------------------------------


class TestDigestDeterminism:
    def test_same_payload_same_digest(self) -> None:
        rec_a = AppInputContractRecord(
            input_contract_id="x",
            app_id="apps_rg",
            task_class="rg",
            version="1.0.0",
            status="active",
            missing_input_behavior="fail_closed",
            ambiguity_behavior="escalate",
            required_inputs=("a", "b"),
        )
        rec_b = AppInputContractRecord(
            input_contract_id="x",
            app_id="apps_rg",
            task_class="rg",
            version="1.0.0",
            status="active",
            missing_input_behavior="fail_closed",
            ambiguity_behavior="escalate",
            required_inputs=("a", "b"),
        )
        stamped_a = stamp_digest(rec_a)
        stamped_b = stamp_digest(rec_b)
        assert stamped_a.deterministic_digest == stamped_b.deterministic_digest
        assert stamped_a.deterministic_digest != ""

    def test_different_payload_different_digest(self) -> None:
        rec_a = AppInputContractRecord(
            input_contract_id="x",
            app_id="apps_rg",
            task_class="rg",
            version="1.0.0",
            status="active",
            missing_input_behavior="fail_closed",
            ambiguity_behavior="escalate",
        )
        rec_b = AppInputContractRecord(
            input_contract_id="x",
            app_id="apps_rg",
            task_class="rg",
            version="1.0.0",
            status="deprecated",  # different
            missing_input_behavior="fail_closed",
            ambiguity_behavior="escalate",
        )
        sa = stamp_digest(rec_a)
        sb = stamp_digest(rec_b)
        assert sa.deterministic_digest != sb.deterministic_digest


# ---------------------------------------------------------------------------
# Record-kind helper
# ---------------------------------------------------------------------------


def test_record_kind_string() -> None:
    rec = _make_score_dim()
    assert app_domain_record_kind(rec) == "ScoreDimension"
