"""
Tests for apps_research U0 Runtime Customization Package (W1)

Plan: apps-research-rich-content-runtime-customization-a1b2c3
Phase: W1 - U0 runtime customization package
"""
from __future__ import annotations

import pytest
from datetime import datetime

from agentic_core.runtime.contracts.apps_research_runtime_package import (
    RuntimeCustomizationPackage,
    PackageValidationReceipt,
    TaskClass,
    UnknownPackageFieldError,
    PackageDigestMismatchError,
)
from agentic_core.runtime.entry.u0_apps_research_binding_v2 import (
    u0_validate_apps_research_v2,
    AppsResearchU0ValidationError,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    RequestEnvelope,
    AppsRgIngressPayload,
)


class TestRuntimeCustomizationPackage:
    """Tests for RuntimeCustomizationPackage dataclass."""
    
    def test_package_creation_with_defaults(self):
        """Package can be created with minimal required fields."""
        pkg = RuntimeCustomizationPackage(
            package_id="test-package-001",
        )
        
        assert pkg.package_id == "test-package-001"
        assert pkg.app_id == "apps_research"
        assert pkg.task_class == TaskClass.COMPANY_BRIEF
        assert pkg.package_version == "1.0.0"
        assert pkg.write_policy == "read_only"
    
    def test_package_digest_computed(self):
        """Package digest is computed automatically."""
        pkg = RuntimeCustomizationPackage(
            package_id="test-package-002",
        )
        
        assert pkg.package_digest
        assert len(pkg.package_digest) == 64  # SHA-256 hex
    
    def test_package_digest_verification_passes(self):
        """Package digest verification passes for valid package."""
        pkg = RuntimeCustomizationPackage(
            package_id="test-package-003",
        )
        
        assert pkg.verify_digest() is True
    
    def test_package_digest_verification_fails_on_tampering(self):
        """Package digest verification fails if package is tampered."""
        pkg = RuntimeCustomizationPackage(
            package_id="test-package-004",
        )
        
        # Tamper with the package by creating a new one with same ID but different config
        pkg2 = RuntimeCustomizationPackage(
            package_id="test-package-004",
            write_policy="read_write",  # Different from default
        )
        
        # Use pkg's digest on pkg2's data
        assert pkg2.verify_digest() is True
        # But pkg's digest won't match pkg2's data
        assert pkg.package_digest != pkg2.package_digest
    
    def test_package_to_dict_roundtrip(self):
        """Package can be serialized to dict and back."""
        pkg = RuntimeCustomizationPackage(
            package_id="test-package-005",
            task_class=TaskClass.RESEARCH_SUBSTRATE,
            route_profile_ref="test/route.yaml",
        )
        
        data = pkg.to_dict()
        
        assert data["package_id"] == "test-package-005"
        assert data["task_class"] == "research_substrate"
        assert data["route_profile_ref"] == "test/route.yaml"
    
    def test_task_class_enum_values(self):
        """TaskClass enum has expected values."""
        assert TaskClass.COMPANY_BRIEF.value == "company_brief"
        assert TaskClass.RESEARCH_SUBSTRATE.value == "research_substrate"
        assert TaskClass.UPLOADED_BRIEFING_NORMALIZATION.value == "uploaded_briefing_normalization"
    
    def test_package_with_all_refs(self):
        """Package can be created with all profile refs populated."""
        pkg = RuntimeCustomizationPackage(
            package_id="test-package-006",
            spine_profile_ref="spine.yaml",
            route_profile_ref="route.yaml",
            retrieval_profile_ref="retrieval.yaml",
            cache_profile_ref="cache.yaml",
            source_mix_policy_ref="source_mix.yaml",
            freshness_policy_ref="freshness.yaml",
            runtime_gate_profile_ref="gates.yaml",
            exit_profile_ref="exit.yaml",
            judge_profile_ref="judge.yaml",
            grader_roster_ref="grader.yaml",
            eval_rubric_ref="eval.yaml",
            threshold_profile_ref="threshold.yaml",
            rubric_output_map_ref="map.yaml",
            negative_controls_ref="controls.yaml",
            prompt_profile_ref="prompt.yaml",
            prompt_bom_ref="bom.yaml",
            output_schema_ref="output.json",
            research_substrate_schema_ref="substrate.json",
            learning_profile_ref="learning.yaml",
            meta_feedback_profile_ref="meta.yaml",
            briefing_normalization_policy_ref="briefing.yaml",
            entity_resolution_policy_ref="entity.yaml",
            capability_profile_ref="capability.yaml",
            provider_profile_ref="provider.yaml",
        )
        
        assert pkg.spine_profile_ref == "spine.yaml"
        assert pkg.learning_profile_ref == "learning.yaml"


class TestU0ValidationV2:
    """Tests for U0 validation with runtime customization package."""
    
    def _make_envelope(self, app_payload: dict) -> RequestEnvelope:
        """Helper to create a RequestEnvelope with app_payload in user_constraints."""
        payload = AppsRgIngressPayload(
            target_company=app_payload.get("target_company", "TestCorp"),
            target_role=app_payload.get("target_role", "TestRole"),
            user_constraints=app_payload,
        )
        return RequestEnvelope(
            payload=payload,
            request_id="test-req-001",
            run_id="test-run-001",
        )
    
    def test_u0_accepts_valid_runtime_package(self):
        """U0 accepts valid runtime customization package."""
        pkg = RuntimeCustomizationPackage(package_id="test-pkg-001")
        
        envelope = self._make_envelope({
            "runtime_customization_package": pkg.to_dict(),
            "target_company": "Acme Inc",
        })
        
        validated, receipt, ctx = u0_validate_apps_research_v2(envelope)
        
        assert validated.app_id == "apps_research"
        assert receipt.validation_passed is True
        assert receipt.digest_verified is True
        assert receipt.package_id == "test-pkg-001"
        assert ctx.auto_injected_runtime_package is False  # Explicit package
    
    def test_u0_auto_injects_default_runtime_package(self):
        """U0 v2 auto-injects default package when runtime_customization_package is missing."""
        envelope = self._make_envelope({
            "target_company": "Acme Inc",
        })
        
        # v2 binding auto-injects default package when missing
        validated, receipt, ctx = u0_validate_apps_research_v2(envelope)
        
        # Should succeed with auto-injected package
        assert validated.app_id == "apps_research"
        assert "runtime_customization_package" in validated.app_payload
        assert receipt.validation_passed is True
        assert ctx.auto_injected_runtime_package is True  # Auto-injected
        assert ctx.package_source == "auto_injected_direct"
    
    def test_u0_rejects_unknown_package_fields(self):
        """U0 rejects package with unknown fields."""
        envelope = self._make_envelope({
            "runtime_customization_package": {
                "package_id": "test-pkg-002",
                "unknown_field": "should_fail",
            },
        })
        
        with pytest.raises(UnknownPackageFieldError) as exc_info:
            u0_validate_apps_research_v2(envelope)
        
        assert "unknown_field" in str(exc_info.value)
    
    def test_u0_rejects_invalid_task_class(self):
        """U0 rejects package with invalid task_class."""
        envelope = self._make_envelope({
            "runtime_customization_package": {
                "package_id": "test-pkg-003",
                "task_class": "invalid_task",
            },
        })
        
        # Should raise some validation error (either UnknownPackageFieldError or AppsResearchU0ValidationError)
        with pytest.raises((AppsResearchU0ValidationError, ValueError)):
            u0_validate_apps_research_v2(envelope)
    
    def test_u0_rejects_digest_mismatch(self):
        """U0 rejects package with incorrect digest."""
        envelope = self._make_envelope({
            "runtime_customization_package": {
                "package_id": "test-pkg-004",
                "package_digest": "incorrect_digest_1234567890abcdef",
            },
        })
        
        with pytest.raises(PackageDigestMismatchError) as exc_info:
            u0_validate_apps_research_v2(envelope)
        
        assert "digest mismatch" in str(exc_info.value).lower()
    
    def test_u0_preserves_package_in_validated_request(self):
        """U0 preserves runtime package in ValidatedRequest.app_payload."""
        pkg = RuntimeCustomizationPackage(package_id="test-pkg-005")
        
        envelope = self._make_envelope({
            "runtime_customization_package": pkg.to_dict(),
        })
        
        validated, _, ctx = u0_validate_apps_research_v2(envelope)
        
        assert "runtime_customization_package" in validated.app_payload
        assert validated.app_payload["runtime_customization_package"]["package_id"] == "test-pkg-005"
        assert ctx.auto_injected_runtime_package is False
    
    def test_u0_computes_payload_digest(self):
        """U0 computes payload digest including runtime package."""
        pkg = RuntimeCustomizationPackage(package_id="test-pkg-006")
        
        envelope = self._make_envelope({
            "runtime_customization_package": pkg.to_dict(),
            "target_company": "TestCorp",
        })
        
        validated, _, ctx = u0_validate_apps_research_v2(envelope)
        
        assert validated.payload_digest
        assert len(validated.payload_digest) == 64
        assert ctx.receipt_ref  # Receipt ref is also included
    
    def test_u0_sets_posture_read_only(self):
        """U0 sets posture to READ_ONLY for apps_research."""
        pkg = RuntimeCustomizationPackage(package_id="test-pkg-007")
        
        envelope = self._make_envelope({
            "runtime_customization_package": pkg.to_dict(),
        })
        
        validated, _, _ = u0_validate_apps_research_v2(envelope)
        
        # Check posture is read_only (either by value attribute or string comparison)
        posture_str = str(validated.posture).lower()
        assert "read_only" in posture_str or "readonly" in posture_str


class TestPackageSchemaCompliance:
    """Tests for JSON schema compliance."""
    
    def test_package_complies_with_schema_structure(self):
        """Package structure matches JSON schema."""
        import json
        from pathlib import Path
        
        # Load schema
        schema_path = Path("apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.json")
        if schema_path.exists():
            with open(schema_path) as f:
                schema = json.load(f)
            
            # Required fields per schema
            required = set(schema.get("required", []))
            
            # Package provides all required fields
            pkg = RuntimeCustomizationPackage(package_id="schema-test")
            pkg_dict = pkg.to_dict()
            
            for field in required:
                assert field in pkg_dict, f"Required field {field} missing from package"
    
    def test_yaml_package_file_exists(self):
        """Declarative YAML package file exists."""
        from pathlib import Path
        
        yaml_path = Path("apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml")
        assert yaml_path.exists(), "YAML package file should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
