"""W3 tests for apps_lic Exit/L6 package consumption and no-bypass behavior.

These tests prove:
1. Exit binding consumes runtime_customization_package.exit_profile_ref
2. Exit loads required and conditional gates from the profile
3. Exit fails closed on missing GateMeshResult/required gate/material UNKNOWN/NOT_APPLICABLE without reason
4. Exit treats G27 as NOT_APPLICABLE with reason for read-only draft return
5. RuntimeExhaustBundle carries profile refs + cache bypass receipt
6. L6 consumes RuntimeExhaustBundle after current-run boundary
7. L6 outputs future-run proposals only
8. Any L6 promotion path requires UWG
9. Static scan: no L4 writes, no send path, no Exit/X3 emission, no cache return for final drafts

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-u0-runtime-package-complete-f8e2a1.md (W3)
"""

from __future__ import annotations

import pytest
from typing import Any
from unittest.mock import MagicMock

from apps_lic.runtime.bindings.exit_binding import (
    _load_exit_profile,
    _check_gate_mesh_result,
    _check_g27_for_read_only_draft,
    _build_runtime_exhaust_bundle,
    AppsLicExitProfileError,
)
from apps_lic.runtime.bindings.promo_binding import (
    L6PromoResult,
    l6_process_apps_lic,
    l6_require_uwg_for_promotion,
    _verify_no_direct_l4_writes,
    _verify_no_send_path,
    _verify_no_exit_x3_emission,
    _verify_no_cache_return,
)
from apps_lic.contracts.apps_lic_ingress_contract_v1 import (
    RuntimeCustomizationPackageSection,
    ProfileRef,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (
    RuntimeExhaustBundle,
)


class TestW3ExitProfileConsumption:
    """Test 1: Exit binding consumes runtime_customization_package.exit_profile_ref."""

    def test_exit_loads_default_profile(self):
        """Exit loads profile from JSON config (W3.5: no hardcoded default).

        Proves the gate IDs come from the config file, not from agentic_core code:
        the returned dict carries profile_id and config_path from the file.
        """
        profile = _load_exit_profile(None)
        assert isinstance(profile["required_gates"], list)
        assert isinstance(profile["conditional_gates"], list)
        assert len(profile["required_gates"]) > 0
        # W3.5 proof: data-from-config markers must be present
        assert "profile_id" in profile, "profile_id absent — gates may be hardcoded"
        assert "config_path" in profile, "config_path absent — gates may be hardcoded"
        assert "config_digest" in profile, "config_digest absent — gates may be hardcoded"
        assert profile["profile_id"] != "", "profile_id is empty — config file not read"

    def test_exit_loads_profile_from_package(self):
        """Exit loads exit_profile_ref from runtime_customization_package.

        ref_digest is omitted here so digest verification is skipped;
        see TestW35ExitProfileFailClosed.test_apps_lic_exit_profile_digest_mismatch_fails_closed
        for the mismatch path.
        """
        package = RuntimeCustomizationPackageSection(
            exit_profile_ref=ProfileRef(
                ref_id="exit-outreach-v1",
                ref_path="apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json",
                ref_digest=None,  # no digest check; real digest test is separate
            )
        )
        profile = _load_exit_profile(package)
        assert "profile_ref" in profile
        assert profile["profile_ref"]["ref_id"] == "exit-outreach-v1"
        assert "required_gates" in profile

    def test_exit_profile_has_required_gates(self):
        """Loaded profile has required_gates with canonical G-number IDs."""
        profile = _load_exit_profile(None)
        assert isinstance(profile["required_gates"], list)
        # W3.5 AC1: Required gates must be G21, G22, G23, G24, G26, G28
        for gate_id in ("G21", "G22", "G23", "G24", "G26", "G28"):
            assert gate_id in profile["required_gates"], f"{gate_id} missing from required_gates"

    def test_exit_profile_has_conditional_gates(self):
        """Loaded profile has conditional_gates with G25, G27."""
        profile = _load_exit_profile(None)
        assert isinstance(profile["conditional_gates"], list)
        # W3.5 AC1: Conditional gates must be G25, G27
        assert "G25" in profile["conditional_gates"]
        assert "G27" in profile["conditional_gates"]


class TestW3ExitFailClosedConditions:
    """Test 2: Exit fails closed on various gate conditions."""

    def test_fail_closed_missing_gate_mesh_result(self):
        """Exit fails closed when no verdicts (missing GateMeshResult)."""
        profile = {"required_gates": ["G1", "G2"]}
        verdicts = []  # Empty = missing GateMeshResult

        is_valid, reason = _check_gate_mesh_result(verdicts, profile)
        assert is_valid is False
        assert "missing_gate_mesh_result" in reason

    def test_fail_closed_missing_required_gate(self):
        """Exit fails closed when required gate is missing from verdicts."""
        profile = {"required_gates": ["G1", "G2", "G3"]}

        # Mock verdicts missing G2
        v1 = MagicMock()
        v1.gate_id = "G1"
        v1.result.value = "PASS"
        v3 = MagicMock()
        v3.gate_id = "G3"
        v3.result.value = "PASS"
        verdicts = [v1, v3]

        is_valid, reason = _check_gate_mesh_result(verdicts, profile)
        assert is_valid is False
        assert "missing_required_gate" in reason
        assert "G2" in reason

    def test_fail_closed_material_unknown(self):
        """Exit fails closed on material UNKNOWN verdict."""
        profile = {"required_gates": ["G1"]}

        v1 = MagicMock()
        v1.gate_id = "G1"
        v1.result.value = "UNKNOWN"  # Material UNKNOWN
        verdicts = [v1]

        is_valid, reason = _check_gate_mesh_result(verdicts, profile)
        assert is_valid is False
        assert "material_unknown" in reason
        assert "G1" in reason

    def test_pass_with_valid_verdicts(self):
        """Exit passes with valid PASS verdicts for all required gates."""
        profile = {"required_gates": ["G1", "G2"]}

        v1 = MagicMock()
        v1.gate_id = "G1"
        v1.result.value = "PASS"
        v2 = MagicMock()
        v2.gate_id = "G2"
        v2.result.value = "PASS"
        verdicts = [v1, v2]

        is_valid, reason = _check_gate_mesh_result(verdicts, profile)
        assert is_valid is True
        assert reason == ""


class TestW3G27ReadOnlyDraftHandling:
    """Test 3: G27 handling for read-only draft return."""

    def test_g27_not_applicable_with_reason(self):
        """G27 is NOT_APPLICABLE with reason for read-only draft return."""
        v_g27 = MagicMock()
        v_g27.gate_id = "G27"
        v_g27.result.value = "NOT_APPLICABLE"
        v_g27.reason = "read_only_draft_return"
        verdicts = [v_g27]

        l2 = MagicMock()
        is_valid, reason = _check_g27_for_read_only_draft(verdicts, l2)
        assert is_valid is True

    def test_g27_missing_is_ok(self):
        """G27 missing is OK for read-only apps_lic (conditional gate)."""
        verdicts = []  # No G27
        l2 = MagicMock()
        is_valid, reason = _check_g27_for_read_only_draft(verdicts, l2)
        assert is_valid is True

    def test_g27_wrong_result_fails(self):
        """G27 with wrong result (not NOT_APPLICABLE) fails."""
        v_g27 = MagicMock()
        v_g27.gate_id = "G27"
        v_g27.result.value = "PASS"  # Wrong result
        verdicts = [v_g27]

        l2 = MagicMock()
        is_valid, reason = _check_g27_for_read_only_draft(verdicts, l2)
        assert is_valid is False
        assert "g27_wrong_result" in reason

    def test_g27_not_applicable_without_reason_fails(self):
        """G27 NOT_APPLICABLE without reason fails."""
        v_g27 = MagicMock()
        v_g27.gate_id = "G27"
        v_g27.result.value = "NOT_APPLICABLE"
        v_g27.reason = ""  # No reason
        verdicts = [v_g27]

        l2 = MagicMock()
        is_valid, reason = _check_g27_for_read_only_draft(verdicts, l2)
        assert is_valid is False
        assert "g27_not_applicable_without_reason" in reason


class TestW3RuntimeExhaustBundle:
    """Test 4: RuntimeExhaustBundle (as dict) carries profile refs and cache bypass receipt."""

    def test_bundle_has_learning_profile_ref(self):
        """Bundle carries learning_profile_ref from package."""
        l2 = MagicMock()
        l2.request_id = "req1"
        l2.run_id = "run1"
        l2.trace_id = "trace1"
        l2.tenant_id = "tenant1"
        l2.compilation_hash = "hash123"

        package = RuntimeCustomizationPackageSection(
            learning_profile_ref=ProfileRef(
                ref_id="learning-v1",
                ref_path="learning.json",
                ref_digest="sha256:def456",
            )
        )

        bundle = _build_runtime_exhaust_bundle(l2, package, None)
        assert "learning_profile_ref" in bundle
        assert bundle["learning_profile_ref"]["ref_id"] == "learning-v1"
        assert bundle["learning_profile_ref"]["ref_path"] == "learning.json"
        assert bundle["learning_profile_ref"]["ref_digest"] == "sha256:def456"

    def test_bundle_has_meta_feedback_profile_ref(self):
        """Bundle carries meta_feedback_profile_ref from package."""
        l2 = MagicMock()
        l2.request_id = "req1"
        l2.run_id = "run1"
        l2.trace_id = "trace1"
        l2.tenant_id = "tenant1"
        l2.compilation_hash = "hash123"

        package = RuntimeCustomizationPackageSection(
            meta_feedback_profile_ref=ProfileRef(
                ref_id="meta-v1",
                ref_path="meta.json",
                ref_digest="sha256:ghi789",
            )
        )

        bundle = _build_runtime_exhaust_bundle(l2, package, None)
        assert "meta_feedback_profile_ref" in bundle
        assert bundle["meta_feedback_profile_ref"]["ref_id"] == "meta-v1"
        assert bundle["meta_feedback_profile_ref"]["ref_path"] == "meta.json"
        assert bundle["meta_feedback_profile_ref"]["ref_digest"] == "sha256:ghi789"

    def test_bundle_has_exit_profile_ref(self):
        """Bundle carries exit_profile_ref from package."""
        l2 = MagicMock()
        l2.request_id = "req1"
        l2.run_id = "run1"
        l2.trace_id = "trace1"
        l2.tenant_id = "tenant1"
        l2.compilation_hash = "hash123"

        package = RuntimeCustomizationPackageSection(
            exit_profile_ref=ProfileRef(
                ref_id="exit-v1",
                ref_path="exit.json",
                ref_digest="sha256:jkl012",
            )
        )

        bundle = _build_runtime_exhaust_bundle(l2, package, None)
        assert "exit_profile_ref" in bundle
        assert bundle["exit_profile_ref"]["ref_id"] == "exit-v1"
        assert bundle["exit_profile_ref"]["ref_path"] == "exit.json"
        assert bundle["exit_profile_ref"]["ref_digest"] == "sha256:jkl012"

    def test_bundle_has_cache_bypass_receipt(self):
        """Bundle carries cache bypass receipt for final drafts."""
        l2 = MagicMock()
        l2.request_id = "req1"
        l2.run_id = "run1"
        l2.trace_id = "trace1"
        l2.tenant_id = "tenant1"
        l2.compilation_hash = "hash123"

        bundle = _build_runtime_exhaust_bundle(l2, None, None)
        assert "cache_bypass_receipt" in bundle
        assert bundle["cache_bypass_receipt"]["final_draft_r1a_bypass"] is True
        assert bundle["cache_bypass_receipt"]["final_draft_r1b_bypass"] is True

    def test_bundle_marked_current_run(self):
        """Bundle is marked as current-run boundary."""
        l2 = MagicMock()
        l2.request_id = "req1"
        l2.run_id = "run1"
        l2.trace_id = "trace1"
        l2.tenant_id = "tenant1"
        l2.compilation_hash = "hash123"

        bundle = _build_runtime_exhaust_bundle(l2, None, None)
        assert bundle["boundary"] == "current_run"
        assert bundle["future_run_proposals"] == []


class TestW3L6PackageConsumption:
    """Test 5: L6 consumes RuntimeExhaustBundle and outputs future-run proposals only."""

    def test_l6_consumes_bundle_after_boundary(self):
        """L6 processes RuntimeExhaustBundle after current-run boundary."""
        # Use MagicMock to simulate RuntimeExhaustBundle with W3 fields
        bundle = MagicMock()
        bundle.bundle_id = "bundle1"
        bundle.tenant_id = "tenant1"

        result = l6_process_apps_lic(bundle, uwg_write_authority=False)
        # L6 uses bundle_id as request_id/run_id/trace_id
        assert result.request_id == "bundle1"
        assert result.run_id == "bundle1"
        assert result.trace_id == "bundle1"

    def test_l6_outputs_future_run_only(self):
        """L6 outputs future-run proposals only (empty for current run)."""
        bundle = MagicMock()
        bundle.bundle_id = "bundle1"
        bundle.tenant_id = "tenant1"
        # Mock lineage_manifest to return None for profile refs (no promotion eligibility)
        bundle.lineage_manifest.get.return_value = None

        result = l6_process_apps_lic(bundle, uwg_write_authority=False)
        assert result.future_run_proposals == []
        assert result.is_future_run_only is True  # L6 is post-run / future-run only

    def test_l6_preserves_profile_refs(self):
        """L6 preserves profile refs from bundle."""
        bundle = MagicMock()
        bundle.bundle_id = "bundle1"
        bundle.tenant_id = "tenant1"
        bundle.learning_profile_ref = {"ref_id": "learn-v1"}
        bundle.meta_feedback_profile_ref = {"ref_id": "meta-v1"}

        result = l6_process_apps_lic(bundle, uwg_write_authority=False)
        assert "learning_profile_ref" in result.consumed_profiles
        assert result.consumed_profiles["learning_profile_ref"]["ref_id"] == "learn-v1"

    def test_l6_preserves_cache_bypass_receipt(self):
        """L6 preserves cache bypass receipt from bundle."""
        bundle = MagicMock()
        bundle.bundle_id = "bundle1"
        bundle.tenant_id = "tenant1"
        bundle.cache_bypass_receipt = {"final_draft_r1a_bypass": True}

        result = l6_process_apps_lic(bundle, uwg_write_authority=False)
        assert result.cache_bypass_receipt == {"final_draft_r1a_bypass": True}


class TestW3L6UWGRequirement:
    """Test 6: Any L6 promotion path requires UWG."""

    def test_l6_requires_uwg_by_default(self):
        """L6 always signals UWG requirement."""
        bundle = MagicMock()
        bundle.bundle_id = "bundle1"
        bundle.tenant_id = "tenant1"

        result = l6_process_apps_lic(bundle, uwg_write_authority=False)
        assert result.requires_uwg is True
        assert result.uwg_write_authority is False

    def test_l6_with_uwg_authority(self):
        """L6 records UWG authority when granted."""
        bundle = MagicMock()
        bundle.bundle_id = "bundle1"
        bundle.tenant_id = "tenant1"

        result = l6_process_apps_lic(bundle, uwg_write_authority=True)
        assert result.uwg_write_authority is True
        assert result.requires_uwg is True  # Still requires UWG

    def test_uwg_enforcement_blocks_proposals_without_authority(self):
        """UWG enforcement blocks proposals without authority."""
        result = L6PromoResult("req1", "run1", "trace1")
        result.uwg_write_authority = False

        proposed = [{"action": "update_policy"}]
        updated = l6_require_uwg_for_promotion(result, proposed)

        assert updated.requires_uwg is True
        assert updated.future_run_proposals == []  # Blocked without UWG

    def test_uwg_enforcement_allows_proposals_with_authority(self):
        """UWG enforcement allows proposals with authority."""
        result = L6PromoResult("req1", "run1", "trace1")
        result.uwg_write_authority = True

        proposed = [{"action": "update_policy"}]
        updated = l6_require_uwg_for_promotion(result, proposed)

        assert updated.requires_uwg is True
        assert updated.future_run_proposals == proposed  # Allowed with UWG


class TestW3StaticNoBypassScan:
    """Test 7: Static scan proves no bypass behavior."""

    def test_no_direct_l4_writes(self):
        """Static verification: no apps_lic direct L4 writes."""
        assert _verify_no_direct_l4_writes() is True

    def test_no_send_path(self):
        """Static verification: no apps_lic direct send path."""
        assert _verify_no_send_path() is True

    def test_no_exit_x3_emission(self):
        """Static verification: no apps_lic Exit/X3 emission."""
        assert _verify_no_exit_x3_emission() is True

    def test_no_cache_return_for_final_drafts(self):
        """Static verification: no cache return path for final drafts."""
        assert _verify_no_cache_return() is True


class TestW35ExitProfileFailClosed:
    """W3.5: _load_exit_profile must fail closed — no hardcoded agentic_core fallback."""

    def test_apps_lic_exit_profile_loaded_from_config_exact_gate_ids(self):
        """Profile loads exact gate IDs from config file; no hardcoded fallback synthesised.

        Required gates: G21, G22, G23, G24, G26, G28
        Conditional gates: G25, G27
        Values come from apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json,
        NOT from any constant in agentic_core.
        """
        profile = _load_exit_profile(None)
        # Exact required gates from config SSOT
        assert set(profile["required_gates"]) == {"G21", "G22", "G23", "G24", "G26", "G28"}
        # Exact conditional gates from config SSOT
        assert set(profile["conditional_gates"]) == {"G25", "G27"}
        # These values must have come from the file (profile_id is the proof)
        assert profile["profile_id"] == "exit_profile.outreach_message.v1"
        # config_digest must be a sha256 hex string (non-empty, starts with sha256:)
        assert profile["config_digest"].startswith("sha256:")

    def test_apps_lic_exit_profile_missing_fails_closed(self, tmp_path, monkeypatch):
        """_load_exit_profile raises AppsLicExitProfileError when config is missing.

        agentic_core must NOT synthesise a fallback gate set. Absence of the
        config file is a terminal failure — callers must treat it as blocked.
        """
        import apps_lic.runtime.bindings.exit_binding as _mod

        nonexistent = tmp_path / "does_not_exist.json"
        monkeypatch.setattr(_mod, "_EXIT_PROFILE_PATH", nonexistent)

        with pytest.raises(AppsLicExitProfileError, match="fail_closed"):
            _load_exit_profile(None)

    def test_apps_lic_exit_profile_malformed_fails_closed(self, tmp_path, monkeypatch):
        """_load_exit_profile raises AppsLicExitProfileError when config is malformed JSON.

        A malformed config must not produce a synthesised gate set.
        """
        import apps_lic.runtime.bindings.exit_binding as _mod

        bad_json = tmp_path / "malformed.json"
        bad_json.write_text("{ not valid json !!!", encoding="utf-8")
        monkeypatch.setattr(_mod, "_EXIT_PROFILE_PATH", bad_json)

        with pytest.raises(AppsLicExitProfileError, match="fail_closed"):
            _load_exit_profile(None)

    def test_apps_lic_exit_profile_missing_keys_fails_closed(self, tmp_path, monkeypatch):
        """_load_exit_profile raises AppsLicExitProfileError when required keys are absent.

        Valid JSON but without required_exit_gates / conditional_exit_gates
        must not produce a synthesised gate set.
        """
        import json
        import apps_lic.runtime.bindings.exit_binding as _mod

        no_gates = tmp_path / "no_gates.json"
        no_gates.write_text(
            json.dumps({"profile_id": "stub", "version": "v1"}),
            encoding="utf-8",
        )
        monkeypatch.setattr(_mod, "_EXIT_PROFILE_PATH", no_gates)

        with pytest.raises(AppsLicExitProfileError, match="fail_closed"):
            _load_exit_profile(None)

    def test_apps_lic_exit_profile_digest_mismatch_fails_closed(self):
        """_load_exit_profile raises AppsLicExitProfileError on ref_digest mismatch.

        When package.exit_profile_ref carries a ref_digest that does not match
        the actual file's SHA-256, the binding must fail closed rather than
        silently accepting a tampered config.
        """
        package = RuntimeCustomizationPackageSection(
            exit_profile_ref=ProfileRef(
                ref_id="exit-outreach-v1",
                ref_path="apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json",
                ref_digest="sha256:000000000000000000000000000000000000000000000000000000000000dead",
            )
        )
        with pytest.raises(AppsLicExitProfileError, match="digest mismatch"):
            _load_exit_profile(package)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
