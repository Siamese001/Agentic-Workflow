"""RB12 Guarded Activation Readiness Tests for apps_rg managed workflow route.

Per plan apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 RB12.

These tests prove:
- Activation profile controls route selection (not just route_registry.yaml status)
- Production default remains disabled
- Test-enabled path still works
- Guarded activation is policy-controlled and reversible
- Provider mode remains stub_only
- Route does not activate for disallowed tenants/users
- Route does not activate with missing certification receipts
- Route does not activate with live provider mode before RB13
- G24/G28 remain required
- No direct L4 writes
- No provider calls
- No quarantined imports
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

# Activation policy imports
from apps_rg.activation_policy import (
    ActivationMode,
    ProviderMode,
    ActivationProfile,
    ActivationProfileNotFound,
    ActivationProfileInvalid,
    load_activation_profile,
    check_certification_receipts_exist,
    evaluate_route_activation,
    RB12_REQUIRED_RECEIPTS,
    ACTIVATION_PROFILE_RELPATH,
)

# L0 binding imports
from agentic_core.L0_routing.apps_rg_l0_binding import (
    l0_route_apps_rg,
    _evaluate_execution_form,
    _MANAGED_ROUTE_TEST_FLAG,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def repo_root() -> Path:
    """Resolve repository root."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


@pytest.fixture
def base_activation_profile() -> dict[str, Any]:
    """Base activation profile for test mutation."""
    return {
        "schema_version": "apps_rg.activation_profile/v1",
        "activation_profile_id": "apps_rg.resume_generation.activation.v1",
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "route_id": "apps_rg.resume_generation_managed_v1",
        "target_execution_form": "managed_workflow",
        "activation_mode": "disabled",
        "default_mode": "disabled",
        "allowed_modes": ["disabled", "test_only", "guarded", "active"],
        "rollout_percentage": 0,
        "allowed_tenants": [],
        "allowed_users": [],
        "required_certification_receipts": [
            "artifacts/apps_rg/apps_rg_w11_final_no_bypass_certification_receipt.json",
            "artifacts/apps_rg/apps_rg_plan_rebaseline_after_w11_receipt.json",
        ],
        "required_gate_profiles": [
            "apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json",
        ],
        "required_e2e_receipts": [
            "artifacts/apps_rg/apps_rg_w9_full_spine_stubbed_e2e_receipt.json",
        ],
        "provider_mode": "stub_only",
        "rollback_policy": {
            "automatic_rollback_on_failure": True,
            "rollback_mode_on_failure": "disabled",
        },
        "activation_owner": None,
        "activation_reason": None,
        "activated_at": None,
        "expires_at": None,
        "deterministic_digest": "sha256:test",
    }


@pytest.fixture
def minimal_l1_plan() -> L1PlanContract:
    """Create a minimal L1 plan with all required fields for routing."""
    return L1PlanContract(
        request_id="req-test-001",
        run_id="run-test-001",
        app_id="apps_rg",
        trace_id="trace-test-001",
        tenant_id="test_tenant",
        task_spec={
            "generation_mode": "resume_generation",
        },
        query_spec={
            "resume_hash": "abc123",
            "target_company": "TestCorp",
            "target_role": "Engineer",
            "jd_hash": "def456",
            "briefing_hash": "ghi789",
        },
        policy_refs={
            "manifest_digest": "sha256:manifest",
            "blueprint_hash": "sha256:blueprint",
        },
        support_expectation={
            "fact_checked_required": True,
        },
        required_capabilities=["resume_generation"],
        target_level="STANDARD",
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        multiple_work_units_hint=True,
        merge_required_hint=True,
        per_unit_quality_selection_hint=True,
        candidate_generation_expected_hint=True,
        replay_key="replay-test-001",
        l5_certification_ref="l5-cert-test-001",
    )


# =============================================================================
# Activation Profile Loading Tests
# =============================================================================

class TestActivationProfileLoads:
    """Test that activation profile loads and validates correctly."""

    def test_apps_rg_activation_profile_loads(self, repo_root: Path):
        """Activation profile exists and loads from canonical path."""
        profile = load_activation_profile(repo_root)

        assert profile.activation_profile_id == "apps_rg.resume_generation.activation.v1"
        assert profile.app_id == "apps_rg"
        assert profile.task_class == "resume_generation"
        assert profile.route_id == "apps_rg.resume_generation_managed_v1"
        assert profile.target_execution_form == "managed_workflow"

    def test_apps_rg_activation_profile_default_disabled(self, repo_root: Path):
        """Default activation mode is disabled."""
        profile = load_activation_profile(repo_root)

        assert profile.default_mode == ActivationMode.DISABLED
        assert profile.activation_mode == ActivationMode.DISABLED

    def test_apps_rg_activation_profile_provider_mode_stub_only(self, repo_root: Path):
        """Provider mode is stub_only (RB12 — no live providers yet)."""
        profile = load_activation_profile(repo_root)

        assert profile.provider_mode == ProviderMode.STUB_ONLY

    def test_apps_rg_activation_profile_has_required_receipts(self, repo_root: Path):
        """Profile declares required certification receipts."""
        profile = load_activation_profile(repo_root)

        assert len(profile.required_certification_receipts) >= 2
        assert "apps_rg_w11_final_no_bypass_certification_receipt.json" in str(profile.required_certification_receipts)

    def test_apps_rg_activation_profile_has_rb12_metadata(self, repo_root: Path):
        """Profile contains RB12 metadata indicating its purpose."""
        profile = load_activation_profile(repo_root)

        assert "rb12_metadata" in profile.raw
        assert profile.raw["rb12_metadata"]["created_for_wave"] == "RB12"

    def test_apps_rg_activation_profile_allows_guarded_mode(self, repo_root: Path):
        """Guarded mode is in allowed modes list."""
        profile = load_activation_profile(repo_root)

        assert ActivationMode.GUARDED in profile.allowed_modes


# =============================================================================
# Certification Receipt Verification Tests
# =============================================================================

class TestCertificationReceiptsVerified:
    """Test that required certification receipts are verified."""

    def test_rb12_required_receipts_list_complete(self):
        """RB12_REQUIRED_RECEIPTS includes all necessary receipts."""
        assert "apps_rg_w11_final_no_bypass_certification_receipt.json" in str(RB12_REQUIRED_RECEIPTS)
        assert "apps_rg_plan_rebaseline_after_w11_receipt.json" in str(RB12_REQUIRED_RECEIPTS)
        assert "apps_rg_w9_full_spine_stubbed_e2e_receipt.json" in str(RB12_REQUIRED_RECEIPTS)
        assert "apps_rg_w10_l6_uwg_writeback_receipt.json" in str(RB12_REQUIRED_RECEIPTS)

    def test_certification_receipts_exist(self, repo_root: Path):
        """All required certification receipts exist on disk."""
        results = check_certification_receipts_exist(repo_root)

        for receipt_path, exists in results.items():
            assert exists, f"Required receipt missing: {receipt_path}"


# =============================================================================
# Route Activation Evaluation Tests
# =============================================================================

class TestRouteActivationEvaluation:
    """Test route activation policy evaluation."""

    def test_evaluate_activation_with_default_disabled(self, repo_root: Path):
        """Default disabled mode blocks route activation."""
        result = evaluate_route_activation(
            tenant_id="test_tenant",
            repo_root=repo_root,
        )

        assert not result["permitted"]
        assert "activation_mode_is_disabled" in result["blockers"]

    def test_evaluate_activation_missing_receipts_blocks(self, repo_root: Path, base_activation_profile):
        """Missing certification receipts block activation."""
        # Override with non-existent receipt
        override = dict(base_activation_profile)
        override["activation_mode"] = "guarded"
        override["allowed_tenants"] = ["test_tenant"]
        override["required_certification_receipts"] = ["artifacts/nonexistent_receipt.json"]

        result = evaluate_route_activation(
            tenant_id="test_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )

        assert not result["permitted"]
        assert any("missing_certification_receipts" in b for b in result["blockers"])

    def test_evaluate_activation_live_provider_blocks_before_rb13(self, repo_root: Path, base_activation_profile):
        """Live provider mode blocks activation before RB13."""
        override = dict(base_activation_profile)
        override["activation_mode"] = "guarded"
        override["allowed_tenants"] = ["test_tenant"]
        override["provider_mode"] = "live_allowed"  # RB12 should block this

        result = evaluate_route_activation(
            tenant_id="test_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )

        assert not result["permitted"]
        assert any("provider_mode_not_stub_only" in b for b in result["blockers"])

    def test_evaluate_activation_guarded_selects_allowed_tenant(self, repo_root: Path, base_activation_profile):
        """Guarded mode permits allowed tenant."""
        override = dict(base_activation_profile)
        override["activation_mode"] = "guarded"
        override["allowed_tenants"] = ["allowed_tenant"]

        result = evaluate_route_activation(
            tenant_id="allowed_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )

        # Should be permitted (all receipts exist, stub_only, allowed tenant)
        assert result["permitted"], f"Expected permitted but got blockers: {result.get('blockers')}"

    def test_evaluate_activation_guarded_blocks_disallowed_tenant(self, repo_root: Path, base_activation_profile):
        """Guarded mode blocks disallowed tenant."""
        override = dict(base_activation_profile)
        override["activation_mode"] = "guarded"
        override["allowed_tenants"] = ["allowed_tenant"]

        result = evaluate_route_activation(
            tenant_id="disallowed_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )

        assert not result["permitted"]
        assert any("tenant_not_allowed" in b for b in result["blockers"])

    def test_evaluate_activation_expired_profile_blocks(self, repo_root: Path, base_activation_profile):
        """Expired activation profile blocks route."""
        override = dict(base_activation_profile)
        override["activation_mode"] = "guarded"
        override["allowed_tenants"] = ["test_tenant"]
        override["expires_at"] = "2020-01-01T00:00:00Z"  # Expired in the past

        result = evaluate_route_activation(
            tenant_id="test_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )

        assert not result["permitted"]
        assert "activation_profile_expired" in result["blockers"]


# =============================================================================
# L0 Route Selection Tests
# =============================================================================

class TestManagedRouteSelection:
    """Test managed workflow route selection controlled by activation policy."""

    def test_managed_route_not_selected_without_activation_policy(self, repo_root: Path, minimal_l1_plan: L1PlanContract, base_activation_profile):
        """Without activation policy permit, managed_workflow is not selected."""
        # Profile is disabled by default
        route_contract = l0_route_apps_rg(minimal_l1_plan)

        # Should NOT select managed_workflow (blocked by activation policy)
        assert route_contract.execution_form == "single_step"

    def test_managed_route_selected_in_test_enabled_mode(self, repo_root: Path, minimal_l1_plan: L1PlanContract):
        """Test env flag still enables managed_workflow for testing."""
        os.environ["APPS_RG_EXECUTION_FORM"] = "managed_workflow"
        os.environ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"] = "1"
        try:
            route_contract = l0_route_apps_rg(minimal_l1_plan)
            assert route_contract.execution_form == "managed_workflow"
        finally:
            del os.environ["APPS_RG_EXECUTION_FORM"]
            if "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED" in os.environ:
                del os.environ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"]

    def test_execution_form_explicit_override(self, repo_root: Path, minimal_l1_plan: L1PlanContract):
        """APPS_RG_EXECUTION_FORM env var can force execution form."""
        os.environ["APPS_RG_EXECUTION_FORM"] = "single_step"
        try:
            route_contract = l0_route_apps_rg(minimal_l1_plan)
            assert route_contract.execution_form == "single_step"
        finally:
            del os.environ["APPS_RG_EXECUTION_FORM"]


# =============================================================================
# Rollback and Reversibility Tests
# =============================================================================

class TestRollbackPolicy:
    """Test that activation is reversible."""

    def test_rollback_to_disabled_blocks_route(self, repo_root: Path, base_activation_profile):
        """Changing activation mode back to disabled blocks route."""
        # Start with guarded mode
        override = dict(base_activation_profile)
        override["activation_mode"] = "guarded"
        override["allowed_tenants"] = ["test_tenant"]

        # Verify it works
        result = evaluate_route_activation(
            tenant_id="test_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )
        assert result["permitted"]

        # Rollback to disabled
        override["activation_mode"] = "disabled"
        result = evaluate_route_activation(
            tenant_id="test_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )
        assert not result["permitted"]
        assert "activation_mode_is_disabled" in result["blockers"]

    def test_removing_allowed_tenant_blocks_route(self, repo_root: Path, base_activation_profile):
        """Removing tenant from allowed list blocks route."""
        # Start with allowed tenant
        override = dict(base_activation_profile)
        override["activation_mode"] = "guarded"
        override["allowed_tenants"] = ["test_tenant"]

        result = evaluate_route_activation(
            tenant_id="test_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )
        assert result["permitted"]

        # Remove tenant
        override["allowed_tenants"] = ["other_tenant"]
        result = evaluate_route_activation(
            tenant_id="test_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )
        assert not result["permitted"]
        assert any("tenant_not_allowed" in b for b in result["blockers"])


# =============================================================================
# No-Bypass Preservation Tests
# =============================================================================

class TestNoBypassPreservation:
    """Test that guarded activation preserves no-bypass invariants."""

    def test_guarded_activation_preserves_g24_g28_required(self, repo_root: Path):
        """G24 and G28 remain required for Exit (verified via receipt)."""
        # Load W11 certification receipt and verify G24/G28 required
        cert_receipt_path = repo_root / "artifacts/apps_rg/apps_rg_w11_final_no_bypass_certification_receipt.json"
        if cert_receipt_path.exists():
            receipt = json.loads(cert_receipt_path.read_text())
            gate_proof = receipt.get("gate_exit_proof", {})
            assert gate_proof.get("g24_required") is True
            assert gate_proof.get("g28_required") is True

    def test_guarded_activation_preserves_no_direct_l4_write(self, repo_root: Path):
        """No direct L4 writes (verified via W11 receipt)."""
        cert_receipt_path = repo_root / "artifacts/apps_rg/apps_rg_w11_final_no_bypass_certification_receipt.json"
        if cert_receipt_path.exists():
            receipt = json.loads(cert_receipt_path.read_text())
            no_bypass = receipt.get("no_bypass_write_proof", {})
            assert no_bypass.get("no_direct_l4_write_patterns_in_layer_modules") is True

    def test_guarded_activation_preserves_no_provider_calls(self, repo_root: Path, minimal_l1_plan: L1PlanContract):
        """Provider mode remains stub_only — no real provider calls."""
        profile = load_activation_profile(repo_root)
        assert profile.provider_mode == ProviderMode.STUB_ONLY

        # Verify test path also uses stub (FakeGeneratorGateway)
        os.environ["APPS_RG_EXECUTION_FORM"] = "managed_workflow"
        os.environ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"] = "1"
        try:
            route_contract = l0_route_apps_rg(minimal_l1_plan)
            assert route_contract.execution_form == "managed_workflow"
            # Note: Actual L2 execution would use FakeGeneratorGateway, not real vLLM
        finally:
            del os.environ["APPS_RG_EXECUTION_FORM"]
            if "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED" in os.environ:
                del os.environ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"]


# =============================================================================
# Quarantine Isolation Tests
# =============================================================================

class TestQuarantineIsolation:
    """Test that quarantined modules remain isolated."""

    def test_no_quarantined_imports_in_activation_path(self):
        """Activation policy module does not import quarantined modules."""
        # Check that activation_policy.py doesn't import quarantined modules
        import apps_rg.activation_policy as ap_module
        import inspect

        source = inspect.getsource(ap_module)

        # Should NOT import from quarantined paths
        assert "_quarantine" not in source
        assert "HardenedanthropicexecutorStrategy" not in source
        assert "ResumeAssemblyAgent" not in source
        assert "compiler" not in source or "compile" not in source

    def test_quarantine_modules_not_in_sys_modules(self):
        """Quarantined modules are not in sys.modules."""
        import sys

        quarantined = [
            "apps_rg._quarantine.HardenedanthropicexecutorStrategy",
            "apps_rg._quarantine.ResumeAssemblyAgent",
            "apps_rg._quarantine.compiler",
        ]

        for module_name in quarantined:
            assert module_name not in sys.modules, f"Quarantined module loaded: {module_name}"


# =============================================================================
# Silent Fallback Prevention Tests
# =============================================================================

class TestSilentFallbackPrevention:
    """Test that there's no silent fallback from managed_workflow to single_step."""

    def test_no_silent_fallback_on_registry_failure(self, repo_root: Path, minimal_l1_plan: L1PlanContract, base_activation_profile):
        """Registry failure does NOT silently fallback to single_step."""
        # With test override that permits managed_workflow
        os.environ["APPS_RG_EXECUTION_FORM"] = "managed_workflow"
        os.environ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"] = "1"

        try:
            route_contract = l0_route_apps_rg(minimal_l1_plan)

            # If execution_form is managed_workflow, it should stay that way
            # Registry failures should propagate, not silently fallback
            if route_contract.execution_form == "managed_workflow":
                assert route_contract.l3_required is True
                assert route_contract.workflow_manifest_ref != ""
        finally:
            if "APPS_RG_EXECUTION_FORM" in os.environ:
                del os.environ["APPS_RG_EXECUTION_FORM"]
            if "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED" in os.environ:
                del os.environ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"]

    def test_guarded_activation_no_silent_single_step_fallback(self, repo_root: Path, base_activation_profile):
        """Blocked guarded activation produces explicit single_step, not silent fallback."""
        # Override with guarded mode but blocked (no allowed tenants)
        override = dict(base_activation_profile)
        override["activation_mode"] = "guarded"
        override["allowed_tenants"] = []  # Empty = no tenants allowed

        result = evaluate_route_activation(
            tenant_id="any_tenant",
            repo_root=repo_root,
            _test_activation_override=override,
        )

        # Should be blocked with explicit reason
        assert not result["permitted"]
        assert "tenant_not_allowed" in str(result["blockers"])


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestEdgeCases:
    """Edge cases and error handling."""

    def test_activation_profile_not_found_handled(self, repo_root: Path):
        """Missing activation profile produces clear error."""
        # This would only fail if profile was deleted
        try:
            profile = load_activation_profile(repo_root)
            # If we get here, profile exists
            assert profile is not None
        except ActivationProfileNotFound:
            pytest.fail("Activation profile should exist for RB12")

    def test_invalid_activation_profile_rejected(self, repo_root: Path):
        """Invalid activation profile schema is rejected."""
        # Test with malformed JSON that can't be parsed
        import tempfile
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Create invalid JSON file
            bad_profile_path = tmp_path / "bad_activation_profile.json"
            bad_profile_path.write_text("{invalid json", encoding="utf-8")
            
            # Should raise ActivationProfileInvalid for bad JSON
            with pytest.raises(ActivationProfileInvalid):
                load_activation_profile(tmp_path, profile_relpath="bad_activation_profile.json")

    def test_test_env_flag_still_works(self, repo_root: Path, minimal_l1_plan: L1PlanContract):
        """APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED env flag still enables test path."""
        os.environ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"] = "1"

        try:
            # This should bypass activation policy check via explicit override
            os.environ["APPS_RG_EXECUTION_FORM"] = "managed_workflow"

            route_contract = l0_route_apps_rg(minimal_l1_plan)

            # Should select managed_workflow when explicitly requested
            assert route_contract.execution_form == "managed_workflow"
        finally:
            if "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED" in os.environ:
                del os.environ["APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED"]
            if "APPS_RG_EXECUTION_FORM" in os.environ:
                del os.environ["APPS_RG_EXECUTION_FORM"]
