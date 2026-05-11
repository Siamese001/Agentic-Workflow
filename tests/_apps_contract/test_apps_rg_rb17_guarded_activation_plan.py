"""RB17 Guarded Activation Plan Tests for apps_rg managed workflow route.

Per plan apps-rg-zip-based-full-spine-runtime-restoration-v1 RB17.

These tests prove:
- Default route remains registered_not_active (no accidental activation)
- Default activation_mode remains disabled
- Default provider_mode remains stub_only
- Guarded profile exists and is valid (template, not activated)
- Guarded profile has required safety fields (expiry, allowed lists)
- Guarded profile blocks external live provider by default
- Rollback procedure exists and is documented
- Operator checklist exists
- Risk register exists
- Activation decision matrix exists
- G24/G28 remain required (no bypass)
- NO route activation is performed in RB17
- NO provider_mode escalation is performed in RB17
- NO direct L4 write paths exist

This is a PLANNING wave — tests verify the PLAN exists, not that activation occurred.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
import yaml


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
def route_registry_path(repo_root: Path) -> Path:
    """Path to route_registry.yaml."""
    return repo_root / "apps_rg" / "config" / "route_registry.yaml"


@pytest.fixture
def activation_profile_path(repo_root: Path) -> Path:
    """Path to default activation profile."""
    return repo_root / "apps_rg" / "config" / "domain_contract" / "activation_profile.resume_generation.v1.json"


@pytest.fixture
def guarded_profile_path(repo_root: Path) -> Path:
    """Path to guarded activation profile template."""
    return repo_root / "apps_rg" / "config" / "domain_contract" / "activation_profile.resume_generation.guarded.v1.json"


@pytest.fixture
def decision_matrix_path(repo_root: Path) -> Path:
    """Path to activation decision matrix."""
    return repo_root / "artifacts" / "apps_rg" / "apps_rg_rb17_activation_decision_matrix.md"


@pytest.fixture
def rollback_procedure_path(repo_root: Path) -> Path:
    """Path to rollback procedure."""
    return repo_root / "artifacts" / "apps_rg" / "apps_rg_rb17_rollback_procedure.md"


@pytest.fixture
def operator_checklist_path(repo_root: Path) -> Path:
    """Path to operator checklist."""
    return repo_root / "artifacts" / "apps_rg" / "apps_rg_rb17_operator_activation_checklist.md"


@pytest.fixture
def risk_register_path(repo_root: Path) -> Path:
    """Path to risk register."""
    return repo_root / "artifacts" / "apps_rg" / "apps_rg_rb17_activation_risk_register.md"


@pytest.fixture
def rb16_receipt_path(repo_root: Path) -> Path:
    """Path to RB16 receipt."""
    return repo_root / "artifacts" / "apps_rg" / "apps_rg_rb16_judge_boundary_cleanup_receipt.json"


@pytest.fixture
def w11_receipt_path(repo_root: Path) -> Path:
    """Path to W11 final certification receipt."""
    return repo_root / "artifacts" / "apps_rg" / "apps_rg_w11_final_no_bypass_certification_receipt.json"


# =============================================================================
# Default State Preservation Tests (RB17 Critical)
# =============================================================================

class TestDefaultRouteStatePreserved:
    """Verify default route remains safely disabled (no accidental activation)."""

    def test_rb17_default_route_remains_registered_not_active(
        self, repo_root: Path, route_registry_path: Path
    ):
        """CRITICAL: Route registry status must remain registered_not_active."""
        assert route_registry_path.exists(), f"Route registry not found: {route_registry_path}"
        
        registry = yaml.safe_load(route_registry_path.read_text())
        managed_route = [
            r for r in registry["routes"]
            if r["route_id"] == "apps_rg.resume_generation_managed_v1"
        ][0]
        
        assert managed_route.get("status") == "registered_not_active", (
            f"CRITICAL: Route status is {managed_route.get('status')}, "
            f"expected registered_not_active. RB17 must NOT activate route."
        )

    def test_rb17_default_activation_mode_remains_disabled(
        self, repo_root: Path, activation_profile_path: Path
    ):
        """CRITICAL: Default activation mode must remain disabled."""
        assert activation_profile_path.exists(), f"Activation profile not found: {activation_profile_path}"
        
        profile = json.loads(activation_profile_path.read_text())
        
        assert profile["activation_mode"] == "disabled", (
            f"CRITICAL: activation_mode is {profile['activation_mode']}, "
            f"expected disabled. RB17 must NOT change default."
        )

    def test_rb17_default_provider_mode_remains_stub_only(
        self, repo_root: Path, activation_profile_path: Path
    ):
        """CRITICAL: Default provider mode must remain stub_only."""
        profile = json.loads(activation_profile_path.read_text())
        
        assert profile["provider_mode"] == "stub_only", (
            f"CRITICAL: provider_mode is {profile['provider_mode']}, "
            f"expected stub_only. RB17 must NOT escalate provider."
        )


class TestGuardedProfileExistsButNotActivated:
    """Verify guarded profile exists as template but is NOT activated."""

    def test_rb17_guarded_profile_exists_and_loads(
        self, repo_root: Path, guarded_profile_path: Path
    ):
        """Guarded profile template exists and is valid JSON."""
        assert guarded_profile_path.exists(), (
            f"Guarded profile not found: {guarded_profile_path}. "
            f"RB17 must create the guarded profile template."
        )
        
        profile = json.loads(guarded_profile_path.read_text())
        
        # Validate required fields
        assert profile["schema_version"] == "apps_rg.activation_profile/guarded.v1"
        assert profile["activation_profile_id"] == "apps_rg.resume_generation.guarded.v1"
        assert profile["app_id"] == "apps_rg"
        assert profile["activation_mode"] == "guarded"
        assert profile["rb17_metadata"]["created_for_wave"] == "RB17"

    def test_rb17_guarded_profile_has_expiry(
        self, repo_root: Path, guarded_profile_path: Path
    ):
        """Guarded profile has mandatory expiry configuration."""
        profile = json.loads(guarded_profile_path.read_text())
        
        expiry = profile.get("expiry", {})
        assert expiry.get("expires_at"), "Guarded profile missing expiry date"
        assert expiry.get("auto_disable_on_expiry") is True, "Guarded profile must auto-disable on expiry"
        assert expiry.get("renewal_requires_approval") is True, "Guarded profile renewal requires approval"

    def test_rb17_guarded_profile_has_allowed_tenants_or_users(
        self, repo_root: Path, guarded_profile_path: Path
    ):
        """Guarded profile has allowed_tenants and allowed_users fields (template has empty lists)."""
        profile = json.loads(guarded_profile_path.read_text())
        
        # Template has empty lists that must be filled before activation
        assert "allowed_tenants" in profile, "Guarded profile missing allowed_tenants"
        assert "allowed_users" in profile, "Guarded profile missing allowed_users"
        assert isinstance(profile["allowed_tenants"], list), "allowed_tenants must be a list"
        assert isinstance(profile["allowed_users"], list), "allowed_users must be a list"
        
        # Template has empty lists — this is correct (must be filled before use)
        # Empty = fail-closed (no one allowed until explicitly configured)

    def test_rb17_guarded_profile_blocks_external_live_provider_by_default(
        self, repo_root: Path, guarded_profile_path: Path
    ):
        """Guarded profile blocks live_allowed provider mode."""
        profile = json.loads(guarded_profile_path.read_text())
        
        # Provider mode in template is stub_only
        assert profile["provider_mode"] == "stub_only", (
            "Guarded profile must default to stub_only"
        )
        
        # blocked_provider_modes should include live_allowed
        blocked = profile.get("blocked_provider_modes", [])
        assert "live_allowed" in blocked, (
            "Guarded profile must block live_allowed in blocked_provider_modes"
        )


# =============================================================================
# Artifact Existence Tests
# =============================================================================

class TestActivationPlanArtifactsExist:
    """Verify all RB17 plan artifacts exist."""

    def test_rb17_activation_decision_matrix_exists(
        self, repo_root: Path, decision_matrix_path: Path
    ):
        """Activation decision matrix document exists."""
        assert decision_matrix_path.exists(), (
            f"Decision matrix not found: {decision_matrix_path}"
        )
        
        content = decision_matrix_path.read_text()
        assert "Activation Decision Matrix" in content
        assert "Option A" in content
        assert "Option B" in content
        assert "Option C" in content
        assert "Option D" in content
        assert "Option E" in content

    def test_rb17_rollback_procedure_exists(
        self, repo_root: Path, rollback_procedure_path: Path
    ):
        """Rollback procedure document exists."""
        assert rollback_procedure_path.exists(), (
            f"Rollback procedure not found: {rollback_procedure_path}"
        )
        
        content = rollback_procedure_path.read_text()
        assert "Rollback Procedure" in content
        assert "revert activation profile to disabled" in content.lower()
        assert "post-rollback tests" in content.lower()

    def test_rb17_operator_checklist_exists(
        self, repo_root: Path, operator_checklist_path: Path
    ):
        """Operator checklist document exists."""
        assert operator_checklist_path.exists(), (
            f"Operator checklist not found: {operator_checklist_path}"
        )
        
        content = operator_checklist_path.read_text()
        assert "Operator Activation Checklist" in content
        assert "G24" in content
        assert "G28" in content
        assert "GateMesh" in content

    def test_rb17_risk_register_exists(
        self, repo_root: Path, risk_register_path: Path
    ):
        """Risk register document exists."""
        assert risk_register_path.exists(), (
            f"Risk register not found: {risk_register_path}"
        )
        
        content = risk_register_path.read_text()
        assert "Risk Register" in content
        assert "Accidental production activation" in content
        assert "Live provider enabled" in content
        assert "GateMesh bypass" in content


# =============================================================================
# No-Bypass Preservation Tests
# =============================================================================

class TestNoBypassPreserved:
    """Verify no-bypass invariants remain enforced."""

    def test_rb17_g24_g28_remain_required(
        self, repo_root: Path, w11_receipt_path: Path
    ):
        """G24 and G28 remain required for Exit (verified via W11 receipt)."""
        assert w11_receipt_path.exists(), "W11 certification receipt required"
        
        receipt = json.loads(w11_receipt_path.read_text())
        gate_proof = receipt.get("gate_exit_proof", {})
        
        assert gate_proof.get("g24_required") is True, "G24 no longer required!"
        assert gate_proof.get("g28_required") is True, "G28 no longer required!"

    def test_rb17_no_direct_l4_write_paths(
        self, repo_root: Path, w11_receipt_path: Path
    ):
        """No direct L4 writes from core layers (verified via W11 receipt)."""
        receipt = json.loads(w11_receipt_path.read_text())
        no_bypass = receipt.get("no_bypass_write_proof", {})
        
        assert no_bypass.get("no_direct_l4_write_patterns_in_layer_modules") is True, (
            "Direct L4 write patterns detected!"
        )
        assert no_bypass.get("l4_adapter_rejects_all_non_uwg_callers") is True, (
            "UWG is not the sole admission path!"
        )


# =============================================================================
# Activation Prevention Tests (RB17 Critical)
# =============================================================================

class TestNoActivationPerformed:
    """Verify NO activation is performed in RB17."""

    def test_rb17_no_route_activation_performed(
        self, repo_root: Path, route_registry_path: Path
    ):
        """RB17 does NOT change route_registry status to active."""
        registry = yaml.safe_load(route_registry_path.read_text())
        managed_route = [
            r for r in registry["routes"]
            if r["route_id"] == "apps_rg.resume_generation_managed_v1"
        ][0]
        
        # RB17 does NOT activate — status must remain registered_not_active
        assert managed_route.get("status") != "active", (
            "CRITICAL: RB17 activated the route! This violates the planning wave scope."
        )
        
        # Verify it's the expected state
        assert managed_route.get("status") == "registered_not_active", (
            f"Unexpected route status: {managed_route.get('status')}"
        )

    def test_rb17_no_provider_mode_escalation_performed(
        self, repo_root: Path, activation_profile_path: Path
    ):
        """RB17 does NOT escalate provider_mode from stub_only."""
        profile = json.loads(activation_profile_path.read_text())
        
        # RB17 does NOT escalate provider
        assert profile["provider_mode"] != "live_allowed", (
            "CRITICAL: RB17 escalated provider_mode to live_allowed! "
            "This violates the planning wave scope."
        )
        assert profile["provider_mode"] != "local_only", (
            "WARNING: RB17 escalated provider_mode to local_only without explicit scope. "
            "This may violate the planning wave scope if local_only was not explicitly approved."
        )
        
        # Verify it's the expected state
        assert profile["provider_mode"] == "stub_only", (
            f"Unexpected provider_mode: {profile['provider_mode']}"
        )


# =============================================================================
# Guarded Profile Safety Tests
# =============================================================================

class TestGuardedProfileSafety:
    """Verify guarded profile has all safety mechanisms."""

    def test_guarded_profile_has_safety_gates(
        self, repo_root: Path, guarded_profile_path: Path
    ):
        """Guarded profile defines pre-activation and runtime safety gates."""
        profile = json.loads(guarded_profile_path.read_text())
        
        safety = profile.get("safety_gates", {})
        
        # Pre-activation checks
        pre_checks = safety.get("pre_activation_checks", [])
        assert len(pre_checks) >= 10, "Expected at least 10 pre-activation safety gates"
        
        gate_ids = [g["gate_id"] for g in pre_checks]
        assert "PRE_ACT_001" in gate_ids, "Missing receipt verification gate"
        assert "PRE_ACT_003" in gate_ids, "Missing provider mode verification gate"
        assert "PRE_ACT_004" in gate_ids, "Missing allowed_tenants verification gate"
        assert "PRE_ACT_005" in gate_ids, "Missing allowed_users verification gate"

    def test_guarded_profile_has_rollback_policy(
        self, repo_root: Path, guarded_profile_path: Path
    ):
        """Guarded profile defines rollback policy."""
        profile = json.loads(guarded_profile_path.read_text())
        
        rollback = profile.get("rollback_policy", {})
        assert rollback.get("automatic_rollback_on_failure") is True
        assert rollback.get("rollback_mode_on_failure") == "disabled"
        assert rollback.get("max_consecutive_failures_before_rollback") > 0

    def test_guarded_profile_has_monitoring(
        self, repo_root: Path, guarded_profile_path: Path
    ):
        """Guarded profile defines monitoring configuration."""
        profile = json.loads(guarded_profile_path.read_text())
        
        monitoring = profile.get("monitoring", {})
        assert monitoring.get("alert_on_failure") is True
        assert "ledger_events" in monitoring


# =============================================================================
# Receipt Verification Tests
# =============================================================================

class TestRB17ReceiptsVerified:
    """Verify RB17 can access and validate required receipts."""

    def test_rb16_receipt_exists_and_complete(
        self, repo_root: Path, rb16_receipt_path: Path
    ):
        """RB16 receipt exists and shows DONE status."""
        assert rb16_receipt_path.exists(), (
            f"RB16 receipt required for RB17: {rb16_receipt_path}"
        )
        
        receipt = json.loads(rb16_receipt_path.read_text())
        
        assert receipt.get("rb16_status") == "DONE", (
            f"RB16 status is {receipt.get('rb16_status')}, expected DONE"
        )
        
        # Verify boundary drift is fixed
        assert receipt.get("boundary_drift_fixed", {}).get("fix_status") == "FIXED", (
            "RB16 boundary drift not fixed!"
        )

    def test_rb16_receipt_shows_no_boundary_drift_remaining(
        self, repo_root: Path, rb16_receipt_path: Path
    ):
        """RB16 receipt confirms zero remaining boundary drift."""
        receipt = json.loads(rb16_receipt_path.read_text())
        
        boundary_summary = receipt.get("boundary_drift_resolution_summary", {})
        assert "0 BOUNDARY_DRIFT remaining" in boundary_summary.get("post_rb16_status", ""), (
            f"Boundary drift not resolved: {boundary_summary}"
        )


# =============================================================================
# Integration Tests
# =============================================================================

class TestRB17IntegrationWithExistingTests:
    """Verify RB17 plan integrates with existing test infrastructure."""

    def test_guarded_activation_readiness_still_passes(
        self, repo_root: Path
    ):
        """Existing RB12 guarded activation readiness tests still pass."""
        # This test is a marker for CI — the actual test run is in test_commands
        # We verify the test file exists and has the expected structure
        
        test_path = repo_root / "tests" / "_apps_contract" / "test_apps_rg_guarded_activation_readiness.py"
        assert test_path.exists(), "RB12 test file must exist"
        
        content = test_path.read_text()
        assert "test_apps_rg_activation_profile_loads" in content
        assert "test_apps_rg_activation_profile_default_disabled" in content
        assert "test_apps_rg_activation_profile_provider_mode_stub_only" in content


# =============================================================================
# Documentation Completeness Tests
# =============================================================================

class TestDocumentationCompleteness:
    """Verify all RB17 documentation is complete and consistent."""

    def test_decision_matrix_covers_all_options(
        self, repo_root: Path, decision_matrix_path: Path
    ):
        """Decision matrix covers Options A through E with required fields."""
        content = decision_matrix_path.read_text()
        
        # Each option must have required sections
        for option in ["Option A", "Option B", "Option C", "Option D", "Option E"]:
            assert option in content, f"Decision matrix missing {option}"
        
        # Critical fields must be present
        required_fields = [
            "Route Registry Change",
            "Activation Profile Change",
            "Provider Mode",
            "Rollback Method",
            "Risk Level",
            "Required Receipts",
            "Expected X3 Behavior",
        ]
        
        for field in required_fields:
            assert field in content, f"Decision matrix missing field: {field}"

    def test_rollback_procedure_has_all_scenarios(
        self, repo_root: Path, rollback_procedure_path: Path
    ):
        """Rollback procedure covers all scenarios."""
        content = rollback_procedure_path.read_text()
        
        scenarios = [
            "Revert Activation Profile to Disabled",
            "Keep Route Registry Registered-Not-Active",
            "Invalidate Guarded Activation",
            "Block Specific Tenants/Users",
            "Verify Production Route Disabled",
        ]
        
        for scenario in scenarios:
            # Check for scenario headers (case insensitive)
            assert any(scenario.lower() in line.lower() for line in content.split("\n")), (
                f"Rollback procedure missing scenario: {scenario}"
            )

    def test_operator_checklist_has_all_items(
        self, repo_root: Path, operator_checklist_path: Path
    ):
        """Operator checklist has all 11 required verification items."""
        content = operator_checklist_path.read_text()
        
        # Required checks
        required_checks = [
            "Receipts Verified",
            "Route Status Verified",
            "Activation Profile Verified",
            "Provider Mode Verified",
            "G24 Required",
            "G28 Required",
            "GateMesh Required",
            "Exactly One X3",
            "UWG-Only Writeback",
            "No Quarantined Imports",
            "Rollback Validated",
        ]
        
        for check in required_checks:
            assert check in content or check.lower().replace("-", " ") in content.lower(), (
                f"Operator checklist missing: {check}"
            )

    def test_risk_register_has_all_risks(
        self, repo_root: Path, risk_register_path: Path
    ):
        """Risk register catalogs all 11 defined risks."""
        content = risk_register_path.read_text()
        
        risks = [
            "Accidental Production Activation",
            "Live Provider Enabled",
            "Provider Cost Runaway",
            "Stale Activation Profile",
            "Disallowed Tenant Access",
            "Route Fallback",
            "GateMesh Bypass",
            "Exit Writeback Regression",
            "L6 Current-Run Rescue",
            "Judge Timeout",
            "Quality Drift",
        ]
        
        for risk in risks:
            assert any(risk.lower() in line.lower() for line in content.split("\n")), (
                f"Risk register missing risk: {risk}"
            )
