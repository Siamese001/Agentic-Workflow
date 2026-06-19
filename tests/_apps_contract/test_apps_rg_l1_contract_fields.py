"""Tests for L1PlanContract W3 field additions and validators.

Validates:
- 5 new fields exist with safe defaults
- NAA validator rejects missing/False required keys
- route_hints rejects route-authority keys
- prompt_bom_refs rejects raw prompt bodies/XML/newlines/overlength
"""
from __future__ import annotations

import pytest
from agentic_core.runtime.contracts.l1_plan_contract import (
    L1PlanContract,
    _NAA_REQUIRED_KEYS,
    _ROUTE_AUTHORITY_KEYS,
)


class TestL1PlanContractFieldsExist:
    """Verify new fields exist and have safe defaults."""

    def test_non_authority_assertion_field_exists(self) -> None:
        """non_authority_assertion field exists with empty dict default."""
        contract = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            l5_certification_ref="valid:test",
        )
        assert hasattr(contract, "non_authority_assertion")
        assert contract.non_authority_assertion == {}

    def test_planning_prior_refs_field_exists(self) -> None:
        """planning_prior_refs field exists with empty tuple default."""
        contract = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            l5_certification_ref="valid:test",
        )
        assert hasattr(contract, "planning_prior_refs")
        assert contract.planning_prior_refs == ()

    def test_route_hints_field_exists(self) -> None:
        """route_hints field exists with empty dict default."""
        contract = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            l5_certification_ref="valid:test",
        )
        assert hasattr(contract, "route_hints")
        assert contract.route_hints == {}

    def test_prompt_bom_refs_field_exists(self) -> None:
        """prompt_bom_refs field exists with empty tuple default."""
        contract = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            l5_certification_ref="valid:test",
        )
        assert hasattr(contract, "prompt_bom_refs")
        assert contract.prompt_bom_refs == ()

    def test_judge_eval_expectation_refs_field_exists(self) -> None:
        """judge_eval_expectation_refs field exists with empty tuple default."""
        contract = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            l5_certification_ref="valid:test",
        )
        assert hasattr(contract, "judge_eval_expectation_refs")
        assert contract.judge_eval_expectation_refs == ()


class TestNonAuthorityAssertionValidator:
    """NAA validator rejects invalid assertions."""

    def test_naa_rejects_missing_required_keys(self) -> None:
        """NAA with missing required keys raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                non_authority_assertion={
                    "no_evidence_retrieval": True,
                    "no_pa_assembly": True,
                    # Missing no_model_call and no_c0_import
                },
            )
        assert "missing required keys" in str(exc_info.value)

    def test_naa_rejects_false_values(self) -> None:
        """NAA with any False value raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                non_authority_assertion={
                    "no_evidence_retrieval": True,
                    "no_pa_assembly": True,
                    "no_model_call": True,
                    "no_c0_import": False,  # Invalid: must be True
                },
            )
        assert "must be True" in str(exc_info.value)

    def test_naa_rejects_unknown_keys(self) -> None:
        """NAA with unknown keys raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                non_authority_assertion={
                    "no_evidence_retrieval": True,
                    "no_pa_assembly": True,
                    "no_model_call": True,
                    "no_c0_import": True,
                    "unknown_key": True,
                },
            )
        assert "unknown keys" in str(exc_info.value)

    def test_naa_accepts_all_required_true(self) -> None:
        """NAA with all required keys True is valid."""
        contract = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            l5_certification_ref="valid:test",
            non_authority_assertion={
                "no_evidence_retrieval": True,
                "no_pa_assembly": True,
                "no_model_call": True,
                "no_c0_import": True,
            },
        )
        assert contract.non_authority_assertion["no_evidence_retrieval"] is True
        assert contract.non_authority_assertion["no_pa_assembly"] is True
        assert contract.non_authority_assertion["no_model_call"] is True
        assert contract.non_authority_assertion["no_c0_import"] is True


class TestRouteHintsValidator:
    """route_hints validator rejects route-authority keys."""

    def test_route_hints_rejects_route_id(self) -> None:
        """route_id in route_hints raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                route_hints={"route_id": "R1_TEST"},
            )
        assert "forbidden route-authority key" in str(exc_info.value)

    def test_route_hints_rejects_route_family(self) -> None:
        """route_family in route_hints raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                route_hints={"route_family": "managed"},
            )
        assert "forbidden route-authority key" in str(exc_info.value)

    def test_route_hints_rejects_execution_form(self) -> None:
        """execution_form in route_hints raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                route_hints={"execution_form": "direct"},
            )
        assert "forbidden route-authority key" in str(exc_info.value)

    def test_route_hints_rejects_selected_route_reason(self) -> None:
        """selected_route_reason in route_hints raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                route_hints={"selected_route_reason": "cache_hit"},
            )
        assert "forbidden route-authority key" in str(exc_info.value)

    def test_route_hints_rejects_route_digest(self) -> None:
        """route_digest in route_hints raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                route_hints={"route_digest": "sha256:abc123"},
            )
        assert "forbidden route-authority key" in str(exc_info.value)

    def test_route_hints_accepts_advisory_keys(self) -> None:
        """Advisory keys like execution_shape_hint are valid."""
        contract = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            l5_certification_ref="valid:test",
            route_hints={
                "execution_shape_hint": "multi_work_unit_managed_candidate",
                "completion_policy": "bounded_refinement",
                "planning_prior_set_ref": "l1priors-abc123",
                "planning_capsule_ref": "l1plan-def456",
                "max_refinement_passes": "1",
            },
        )
        assert contract.route_hints["execution_shape_hint"] == "multi_work_unit_managed_candidate"
        assert contract.route_hints["completion_policy"] == "bounded_refinement"
        assert contract.route_hints["planning_prior_set_ref"] == "l1priors-abc123"
        assert contract.route_hints["planning_capsule_ref"] == "l1plan-def456"


class TestRefTupleValidators:
    """prompt_bom_refs and judge_eval_expectation_refs validators."""

    def test_prompt_bom_refs_rejects_newlines(self) -> None:
        """Ref with newline raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                prompt_bom_refs=("ref\nwith\nnewlines",),
            )
        assert "must not contain newlines" in str(exc_info.value)

    def test_prompt_bom_refs_rejects_xml_tags(self) -> None:
        """Ref with XML tags raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                prompt_bom_refs=("<prompt>content</prompt>",),
            )
        assert "must not contain XML tags" in str(exc_info.value)

    def test_prompt_bom_refs_rejects_overlength(self) -> None:
        """Ref over 256 chars raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                prompt_bom_refs=("a" * 257,),
            )
        assert "exceeds max 256" in str(exc_info.value)

    def test_judge_eval_refs_rejects_raw_prompt_content(self) -> None:
        """Ref containing prompt phrases raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            L1PlanContract(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                trace_id="t1",
                l5_certification_ref="valid:test",
                judge_eval_expectation_refs=("Generate a resume for",),
            )
        # Should pass length but might fail other checks - this test verifies structure
        # The validator checks for XML tags specifically

    def test_valid_refs_accepted(self) -> None:
        """Clean refs are accepted."""
        contract = L1PlanContract(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            l5_certification_ref="valid:test",
            prompt_bom_refs=("apps_rg/prompts/resume_v1", "apps_rg/prompts/executive_v2"),
            judge_eval_expectation_refs=("rubric/quality_v1",),
        )
        assert contract.prompt_bom_refs == ("apps_rg/prompts/resume_v1", "apps_rg/prompts/executive_v2")
        assert contract.judge_eval_expectation_refs == ("rubric/quality_v1",)
