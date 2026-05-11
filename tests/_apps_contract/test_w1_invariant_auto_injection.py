"""
W1 Invariant Tests for Controlled Auto-Injection

Per W1 hardening requirement: Auto-injection is controlled and auditable.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from agentic_core.runtime.entry.u0_apps_research_binding_v2 import (
    u0_validate_apps_research_v2,
    AppsResearchU0ValidationError,
    AutoInjectionContext,
    RuntimeCustomizationPackage,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    RequestEnvelope,
    AppsRgIngressPayload,
)


class TestAutoInjectionStampsReceipt:
    """Verify auto-injection stamps receipt with required fields."""
    
    def test_apps_research_u0_auto_injection_stamps_receipt(self):
        """Auto-injection stamps receipt_ref on ValidatedRequest."""
        # No runtime package in payload - triggers auto-injection
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={},
            ),
            request_id="test-req-receipt",
            run_id="test-run-receipt",
        )
        
        validated, receipt, ctx = u0_validate_apps_research_v2(envelope)
        
        # Receipt ref should be stamped
        assert ctx.receipt_ref.startswith("u0-auto-inject-"), \
            f"Expected auto-inject receipt ref, got {ctx.receipt_ref}"
        assert ctx.auto_injected_runtime_package is True
        assert ctx.auto_injection_reason
        assert ctx.default_profile_source
    
    def test_apps_research_u0_explicit_package_stamps_different_receipt(self):
        """Explicit package gets different receipt ref."""
        pkg = RuntimeCustomizationPackage(package_id="test-explicit")
        
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={
                    "runtime_customization_package": pkg.to_dict(),
                },
            ),
            request_id="test-req-explicit",
            run_id="test-run-explicit",
        )
        
        validated, receipt, ctx = u0_validate_apps_research_v2(envelope)
        
        # Should get explicit receipt ref
        assert ctx.receipt_ref.startswith("u0-explicit-"), \
            f"Expected explicit receipt ref, got {ctx.receipt_ref}"
        assert ctx.auto_injected_runtime_package is False


class TestAutoInjectionMarksValidatedRequest:
    """Verify auto-injection marks ValidatedRequest for L1 visibility."""
    
    def test_apps_research_u0_auto_injection_marks_validated_request(self):
        """ValidatedRequest.app_payload contains auto_injection_context."""
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={},
            ),
            request_id="test-req-marks",
            run_id="test-run-marks",
        )
        
        validated, receipt, ctx = u0_validate_apps_research_v2(envelope)
        
        # L1 can see auto_injection_context in app_payload
        assert "auto_injection_context" in validated.app_payload, \
            "ValidatedRequest must include auto_injection_context for L1"
        
        aic = validated.app_payload["auto_injection_context"]
        assert aic["auto_injected_runtime_package"] is True
        assert aic["package_source"] == "auto_injected_direct"
        assert aic["receipt_ref"]
        assert aic["auto_injection_reason"]


class TestAutoInjectionAllowedForDirectPath:
    """Verify auto-injection is allowed for direct apps_research calls."""
    
    def test_apps_research_u0_auto_injection_allowed_for_direct_path(self):
        """Direct apps_research call without package gets auto-injected default."""
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={},  # No caller_app_id = direct
            ),
            request_id="test-req-direct",
            run_id="test-run-direct",
        )
        
        # Should succeed with auto-injection
        validated, receipt, ctx = u0_validate_apps_research_v2(envelope)
        
        assert ctx.auto_injected_runtime_package is True
        assert ctx.package_source == "auto_injected_direct"
        assert validated.app_id == "apps_research"


class TestAutoInjectionBlockedForDelegated:
    """Verify auto-injection is blocked for delegated calls without context."""
    
    def test_apps_research_u0_auto_injection_blocked_for_delegated_without_context(self):
        """Delegated call from apps_rg without explicit package is blocked."""
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={
                    "caller_app_id": "apps_rg",  # Delegated call
                },
            ),
            request_id="test-req-delegated",
            run_id="test-run-delegated",
        )
        
        # Should fail - no auto-injection for delegated
        with pytest.raises(AppsResearchU0ValidationError) as exc_info:
            u0_validate_apps_research_v2(envelope)
        
        assert "blocked" in str(exc_info.value.message).lower()
        assert "delegated" in str(exc_info.value.message).lower()
    
    def test_apps_research_u0_delegated_with_explicit_package_succeeds(self):
        """Delegated call with explicit package is allowed."""
        pkg = RuntimeCustomizationPackage(package_id="test-delegated-explicit")
        
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={
                    "caller_app_id": "apps_rg",
                    "runtime_customization_package": pkg.to_dict(),
                },
            ),
            request_id="test-req-delegated-ok",
            run_id="test-run-delegated-ok",
        )
        
        # Should succeed - explicit package provided
        validated, receipt, ctx = u0_validate_apps_research_v2(envelope)
        
        assert ctx.auto_injected_runtime_package is False
        assert ctx.package_source == "explicit"
    
    def test_apps_research_u0_auto_injection_blocked_for_apps_lic(self):
        """Delegated call from apps_lic without package is blocked."""
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={
                    "caller_app_id": "apps_lic",
                },
            ),
            request_id="test-req-lic",
            run_id="test-run-lic",
        )
        
        with pytest.raises(AppsResearchU0ValidationError) as exc_info:
            u0_validate_apps_research_v2(envelope)
        
        assert "apps_lic" in str(exc_info.value.message).lower()


class TestL1CanReadRuntimePackageOrigin:
    """Verify L1 can read runtime package origin from ValidatedRequest."""
    
    def test_apps_research_l1_can_read_runtime_package_origin(self):
        """L1 can determine if package was explicit or auto-injected."""
        # Auto-injected case
        envelope_auto = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={},
            ),
            request_id="test-auto",
            run_id="test-auto",
        )
        
        validated_auto, _, _ = u0_validate_apps_research_v2(envelope_auto)
        
        # L1 can check origin
        aic = validated_auto.app_payload.get("auto_injection_context", {})
        assert aic["package_source"] == "auto_injected_direct"
        assert aic["auto_injected_runtime_package"] is True
        
        # Explicit case
        pkg = RuntimeCustomizationPackage(package_id="test-explicit-l1")
        envelope_explicit = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={
                    "runtime_customization_package": pkg.to_dict(),
                },
            ),
            request_id="test-explicit",
            run_id="test-explicit",
        )
        
        validated_explicit, _, _ = u0_validate_apps_research_v2(envelope_explicit)
        
        aic_explicit = validated_explicit.app_payload.get("auto_injection_context", {})
        assert aic_explicit["package_source"] == "explicit"
        assert aic_explicit["auto_injected_runtime_package"] is False
    
    def test_apps_research_l1_sees_default_profile_source_when_auto_injected(self):
        """L1 can see which default profile was used for auto-injection."""
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={},
            ),
            request_id="test-profile",
            run_id="test-profile",
        )
        
        validated, _, ctx = u0_validate_apps_research_v2(envelope)
        
        aic = validated.app_payload["auto_injection_context"]
        assert "runtime_customization_package.company_brief.v1.yaml" in aic["default_profile_source"]


class TestAutoInjectionResolvesCorrectly:
    """Verify auto-injection resolves app_id and task_class correctly."""
    
    def test_auto_injection_resolves_app_id_unambiguously(self):
        """Auto-injection only proceeds when app_id resolves to apps_research."""
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",  # Unambiguous
                target_company="TestCorp",
                user_constraints={},
            ),
            request_id="test-unambiguous",
            run_id="test-unambiguous",
        )
        
        validated, _, ctx = u0_validate_apps_research_v2(envelope)
        
        assert ctx.resolved_app_id == "apps_research"
        assert validated.app_id == "apps_research"
    
    def test_auto_injection_resolves_task_class_correctly(self):
        """Auto-injection resolves task_class to company_brief."""
        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                task_class="company_brief",
                target_company="TestCorp",
                user_constraints={},
            ),
            request_id="test-task",
            run_id="test-task",
        )
        
        validated, _, ctx = u0_validate_apps_research_v2(envelope)
        
        assert ctx.resolved_task_class == "company_brief"
        assert validated.task_class == "company_brief"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
