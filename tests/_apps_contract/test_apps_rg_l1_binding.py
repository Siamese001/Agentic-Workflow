"""Tests for apps_rg L1 binding.

Validates:
- l1_plan_apps_rg emits all four NAA keys True
- Full resume modes set all work-shape hints True
- Section/correction modes set all work-shape hints False
- Import scan proves no forbidden C0/PA/L2/provider/network imports
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    ValidatedRequest,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
from apps_rg.runtime.bindings.u0_profile_manifest import (
    l1_planning_profile_digest,
    l1_planning_profile_ref,
)
from apps_rg.runtime.bindings.l1_binding import (
    APPS_RG_L1_CERT_REF,
    l1_plan_apps_rg,
    _derive_work_shape_hints,
    _FULL_RESUME_GENERATION_MODES,
    _SINGLE_SECTION_MODES,
)

_L5_DEFAULT = "test:valid:w6"


def _auth_receipt() -> AuthorityValidationReceipt:
    return AuthorityValidationReceipt(
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _profile_manifest_digest_only() -> dict[str, str]:
    return {
        "l1_planning_profile_ref": l1_planning_profile_ref(),
        "l1_planning_profile_digest": l1_planning_profile_digest(allow_missing=False),
    }


def _ap_base(**extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "task_spec": {"generation_mode": "strategic_tailor"},
        "profile_manifest": _profile_manifest_digest_only(),
    }
    base.update(extra)
    return base


class TestL1BindingExports:
    """Verify exports are correct."""

    def test_apss_rg_l1_cert_ref_exported(self) -> None:
        """APPS_RG_L1_CERT_REF has expected value."""
        assert APPS_RG_L1_CERT_REF == "apps_rg::l1::resume_generation::v1"

    def test_l1_plan_apps_rg_exported(self) -> None:
        """l1_plan_apps_rg function is exported."""
        assert callable(l1_plan_apps_rg)


class TestNonAuthorityAssertion:
    """NAA emission tests."""

    def test_l1_plan_emits_all_four_naa_keys_true(self) -> None:
        """l1_plan_apps_rg emits all four NAA keys with True values."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            trace_id="t1",
            l5_certification_ref=_L5_DEFAULT,
            app_payload=_ap_base(),
        )

        plan = l1_plan_apps_rg(validated)

        assert "no_evidence_retrieval" in plan.non_authority_assertion
        assert "no_pa_assembly" in plan.non_authority_assertion
        assert "no_model_call" in plan.non_authority_assertion
        assert "no_c0_import" in plan.non_authority_assertion

        assert plan.non_authority_assertion["no_evidence_retrieval"] is True
        assert plan.non_authority_assertion["no_pa_assembly"] is True
        assert plan.non_authority_assertion["no_model_call"] is True
        assert plan.non_authority_assertion["no_c0_import"] is True


class TestWorkShapeHints:
    """Work-shape hint derivation tests."""

    @pytest.mark.parametrize("mode", list(_FULL_RESUME_GENERATION_MODES))
    def test_full_resume_modes_set_all_hints_true(self, mode: str) -> None:
        """Full resume generation modes set all four work-shape hints True."""
        hints = _derive_work_shape_hints(mode)
        assert hints["multiple_work_units_hint"] is True
        assert hints["merge_required_hint"] is True
        assert hints["per_unit_quality_selection_hint"] is True
        assert hints["candidate_generation_expected_hint"] is True

    @pytest.mark.parametrize("mode", list(_SINGLE_SECTION_MODES))
    def test_single_section_modes_set_all_hints_false(self, mode: str) -> None:
        """Single-section modes set all four work-shape hints False."""
        hints = _derive_work_shape_hints(mode)
        assert hints["multiple_work_units_hint"] is False
        assert hints["merge_required_hint"] is False
        assert hints["per_unit_quality_selection_hint"] is False
        assert hints["candidate_generation_expected_hint"] is False

    def test_unknown_mode_sets_all_hints_false(self) -> None:
        """Unknown generation mode conservatively sets all hints False."""
        hints = _derive_work_shape_hints("unknown_mode")
        assert hints["multiple_work_units_hint"] is False
        assert hints["merge_required_hint"] is False
        assert hints["per_unit_quality_selection_hint"] is False
        assert hints["candidate_generation_expected_hint"] is False

    def test_full_resume_mode_via_validated_request(self) -> None:
        """Full resume mode via ValidatedRequest.app_payload sets hints True."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            trace_id="t1",
            l5_certification_ref=_L5_DEFAULT,
            app_payload=_ap_base(),
        )

        plan = l1_plan_apps_rg(validated)

        assert plan.multiple_work_units_hint is True
        assert plan.merge_required_hint is True
        assert plan.per_unit_quality_selection_hint is True
        assert plan.candidate_generation_expected_hint is True

    def test_section_regen_mode_sets_hints_false(self) -> None:
        """section_regen mode sets all hints False."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            trace_id="t1",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            l5_certification_ref=_L5_DEFAULT,
            app_payload=_ap_base(
                task_spec={"generation_mode": "section_regen"},
            ),
        )

        plan = l1_plan_apps_rg(validated)

        assert plan.multiple_work_units_hint is False
        assert plan.merge_required_hint is False
        assert plan.per_unit_quality_selection_hint is False
        assert plan.candidate_generation_expected_hint is False


class TestRouteHints:
    """Advisory route hints tests."""

    def test_full_resume_mode_sets_execution_shape_hint(self) -> None:
        """Full resume mode sets execution_shape_hint."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            trace_id="t1",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            l5_certification_ref=_L5_DEFAULT,
            app_payload=_ap_base(
                task_spec={"generation_mode": "generate_scratch"},
            ),
        )

        plan = l1_plan_apps_rg(validated)

        assert "execution_shape_hint" in plan.route_hints
        assert plan.route_hints["execution_shape_hint"] == "multi_work_unit_managed_candidate"

    def test_single_section_mode_sets_direct_hint(self) -> None:
        """Single-section mode sets single_work_unit_direct hint."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            trace_id="t1",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            l5_certification_ref=_L5_DEFAULT,
            app_payload=_ap_base(
                task_spec={"generation_mode": "healing_fact_check"},
            ),
        )

        plan = l1_plan_apps_rg(validated)

        assert "execution_shape_hint" in plan.route_hints
        assert plan.route_hints["execution_shape_hint"] == "single_work_unit_direct"


class TestPlanningPriorRefs:
    """Planning prior refs extraction tests."""

    def test_extracts_from_profile_manifest(self) -> None:
        """Extracts planning ref from profile_manifest.rg_planning_profile."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            trace_id="t1",
            l5_certification_ref=_L5_DEFAULT,
            app_payload={
                "task_spec": {"generation_mode": "strategic_tailor"},
                "profile_manifest": {"rg_planning_profile": "custom/planning.yaml"},
            },
        )

        plan = l1_plan_apps_rg(validated)

        assert "custom/planning.yaml" in plan.planning_prior_refs

    def test_uses_canonical_default_when_no_profile(self) -> None:
        """Uses canonical default when no profile ref in payload."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            trace_id="t1",
            l5_certification_ref=_L5_DEFAULT,
            app_payload={
                "task_spec": {"generation_mode": "strategic_tailor"},
                "profile_manifest": {"prompt_registry_ref": "apps_rg/prompt_assembly/x.yaml"},
            },
        )

        plan = l1_plan_apps_rg(validated)

        assert "apps_rg/profiles/rg_planning_profile.yaml" in plan.planning_prior_refs


class TestImportScan:
    """AST import scan for forbidden imports."""

    def test_no_forbidden_c0_pa_l2_provider_imports(self) -> None:
        """AST scan proves no C0/PA/L2/provider/network imports in l1_binding."""
        binding_path = Path(__file__).parent.parent.parent / "apps_rg" / "runtime" / "bindings" / "l1_binding.py"
        source = binding_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        forbidden_patterns = [
            "c0", "C0", "c0_binding", "c0_retrieve",
            "pa_binding", "prompt_governance", "pa_assembly",
            "l2_binding", "L2_execution", "l2_execute",
            "provider_gateway", "SovereignLLMGateway",
            "openai", "anthropic", "httpx", "requests", "aiohttp",
        ]

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)
                for alias in node.names:
                    full = f"{module}.{alias.name}" if module else alias.name
                    imports.append(full)

        # Check no forbidden patterns in imports
        forbidden_found = []
        for pattern in forbidden_patterns:
            for imp in imports:
                if pattern.lower() in imp.lower():
                    forbidden_found.append((pattern, imp))

        if forbidden_found:
            pytest.fail(f"Forbidden imports found: {forbidden_found}")

    def test_only_allowed_imports(self) -> None:
        """Only allowed imports from agentic_core contracts and stdlib."""
        binding_path = Path(__file__).parent.parent.parent / "apps_rg" / "runtime" / "bindings" / "l1_binding.py"
        source = binding_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        allowed_prefixes = [
            "agentic_core.runtime.contracts",
            "apps_rg.runtime.bindings",
            "__future__",
            "typing",
            "logging",
            "os",
        ]

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)

        # Filter to external imports only
        external_imports = [imp for imp in imports if imp and not imp.startswith("__")]

        for imp in external_imports:
            is_allowed = any(imp.startswith(prefix) for prefix in allowed_prefixes)
            if not is_allowed:
                pytest.fail(f"Import not in allowed list: {imp}")


class TestL1PlanOutput:
    """Full L1 plan output validation."""

    def test_returns_valid_l1_plan_contract(self) -> None:
        """l1_plan_apps_rg returns a valid L1PlanContract."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            trace_id="t1",
            payload_digest="sha256:test123",
            tenant_id="tenant_1",
            authority_validation_receipt=_auth_receipt(),
            l5_certification_ref=_L5_DEFAULT,
            app_payload=_ap_base(
                query_spec={"target_level": "EXECUTIVE"},
            ),
        )

        plan = l1_plan_apps_rg(validated)

        assert isinstance(plan, L1PlanContract)
        assert plan.request_id == "r1"
        assert plan.run_id == "run1"
        assert plan.app_id == "apps_rg"
        assert plan.trace_id == "t1"
        assert plan.tenant_id == "tenant_1"
        assert plan.profile_manifest_digest == "sha256:test123"
        assert plan.target_level == "EXECUTIVE"
        assert plan.grounding_required is True
        assert plan.model_generation_required is True
        assert plan.write_authority_present is False

    def test_task_plan_contains_expected_steps(self) -> None:
        """Task plan contains expected pipeline steps."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            trace_id="t1",
            l5_certification_ref=_L5_DEFAULT,
            app_payload=_ap_base(),
        )
        plan = l1_plan_apps_rg(validated)

        assert "validate_ingress" in plan.task_plan
        assert "load_profiles" in plan.task_plan
        assert "collect_evidence" in plan.task_plan
        assert "generate_resume" in plan.task_plan
        assert "exit_eval" in plan.task_plan

    def test_capabilities_include_required(self) -> None:
        """Required capabilities are populated."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            trace_id="t1",
            l5_certification_ref=_L5_DEFAULT,
            app_payload=_ap_base(),
        )

        plan = l1_plan_apps_rg(validated)

        assert "ingress_validation" in plan.required_capabilities
        assert "evidence_collection" in plan.required_capabilities
        assert "model_generation" in plan.required_capabilities


class TestL5CertificationRefPropagation:
    """Verify L5 certification reference propagates U0→L1 and validation fails closed."""

    def test_l1_plan_preserves_l5_certification_ref_from_validated_request(self) -> None:
        """l1_plan_apps_rg preserves l5_certification_ref from ValidatedRequest."""
        validated = ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="sha256:test",
            authority_validation_receipt=_auth_receipt(),
            trace_id="t1",
            l5_certification_ref="test:valid:abc123",
            app_payload=_ap_base(),
        )

        plan = l1_plan_apps_rg(validated)

        assert plan.l5_certification_ref == "test:valid:abc123"

    def test_l1_plan_fails_closed_when_l5_certification_ref_missing(self) -> None:
        """ValidatedRequest fails closed when l5_certification_ref is missing."""
        with pytest.raises(ValueError) as exc_info:
            ValidatedRequest(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                task_class="resume_generation",
                payload_digest="sha256:test",
                authority_validation_receipt=_auth_receipt(),
                trace_id="t1",
                l5_certification_ref=None,
                app_payload=_ap_base(),
            )

        assert "AG-W0-5=fail_closed" in str(exc_info.value)

    def test_l1_plan_fails_closed_when_l5_certification_ref_invalid(self) -> None:
        """ValidatedRequest fails closed when l5_certification_ref is empty."""
        with pytest.raises(ValueError) as exc_info:
            ValidatedRequest(
                request_id="r1",
                run_id="run1",
                app_id="apps_rg",
                task_class="resume_generation",
                payload_digest="sha256:test",
                authority_validation_receipt=_auth_receipt(),
                trace_id="t1",
                l5_certification_ref="",
                app_payload=_ap_base(),
            )

        assert "AG-W0-5=fail_closed" in str(exc_info.value)
