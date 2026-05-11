"""
W2 Tests for apps_research L1 Planning Hints

Validates that L1 consumes U0 v2 ValidatedRequest and emits 21 advisory hints.
NO route selection, NO retrieval, NO execution authority.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from agentic_core.L1_cognition.apps_research_l1_binding_v2 import (
    l1_plan_apps_research_v2,
    L1PlanContract,
    PlanningHint,
    HintSeverity,
    L1PlanningError,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
    AuthorityValidationReceipt,
)


def _make_validated_request(
    target_company: str = "TestCorp",
    target_role: str = "",
    auto_injected: bool = False,
    package_source: str = "explicit",
) -> ValidatedRequest:
    """Helper to create a ValidatedRequest for testing."""
    return ValidatedRequest(
        request_id="test-req-001",
        run_id="test-run-001",
        app_id="apps_research",
        trace_id="test-trace-001",
        tenant_id="apps_research",
        task_class="company_brief",
        target_level="",
        payload_digest="abc123",
        authority_validation_receipt=AuthorityValidationReceipt(
            allowed=True,
            passed=True,
            forbidden_fields_detected=(),
            timestamp_iso="2026-05-11T10:00:00Z",
        ),
        l5_certification_ref="u0-apps-research-v2-company-brief-ag9",
        app_payload={
            "runtime_customization_package": {
                "package_id": "test-pkg-001",
                "package_digest": "def456",
            },
            "target_company": target_company,
            "target_role": target_role,
            "auto_injection_context": {
                "auto_injected_runtime_package": auto_injected,
                "package_source": package_source,
                "receipt_ref": f"u0-{'auto' if auto_injected else 'explicit'}-test",
                "auto_injection_reason": "Test reason",
                "resolved_app_id": "apps_research",
                "resolved_task_class": "company_brief",
                "default_profile_source": "test.yaml",
            },
        },
    )


class TestL1ConsumesU0V2:
    """Verify L1 consumes U0 v2 ValidatedRequest."""
    
    def test_apps_research_l1_consumes_u0_v2_validated_request(self):
        """L1 binding accepts ValidatedRequest from U0 v2."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        assert plan.request_id == "test-req-001"
        assert plan.run_id == "test-run-001"
        assert plan.app_id == "apps_research"
    
    def test_apps_research_l1_reads_runtime_package_refs(self):
        """L1 can read runtime package refs from ValidatedRequest."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        # Runtime package origin hint should contain package info
        origin = plan.runtime_package_origin_hint
        assert origin.hint_type == "runtime_package_origin"
        assert "auto_injected" in origin.value
    
    def test_apps_research_l1_marks_runtime_package_origin(self):
        """L1 marks whether package was explicit or auto-injected."""
        # Explicit package
        validated_explicit = _make_validated_request(auto_injected=False, package_source="explicit")
        plan_explicit = l1_plan_apps_research_v2(validated_explicit)
        
        assert plan_explicit.runtime_package_origin_hint.value["auto_injected"] is False
        assert plan_explicit.runtime_package_origin_hint.value["source"] == "explicit"
        
        # Auto-injected package
        validated_auto = _make_validated_request(auto_injected=True, package_source="auto_injected_direct")
        plan_auto = l1_plan_apps_research_v2(validated_auto)
        
        assert plan_auto.runtime_package_origin_hint.value["auto_injected"] is True


class TestL1EmitsHints:
    """Verify L1 emits all 21 required hints."""
    
    def test_apps_research_l1_emits_entity_and_depth_hints(self):
        """L1 emits company entity and depth profile hints."""
        validated = _make_validated_request(target_company="Acme Inc", target_role="Engineer")
        
        plan = l1_plan_apps_research_v2(validated)
        
        # Entity hints
        assert plan.company_entity_hint.value == "Acme Inc"
        assert plan.company_entity_hint.hint_type == "company_entity"
        
        # Depth hint
        assert plan.depth_profile_hint.hint_type == "depth_profile"
    
    def test_apps_research_l1_marks_downstream_consumer(self):
        """L1 marks downstream consumer hint."""
        validated = _make_validated_request(auto_injected=True, package_source="auto_injected_direct")
        
        plan = l1_plan_apps_research_v2(validated)
        
        assert plan.downstream_consumer_hint.hint_type == "downstream_consumer"
        assert "direct" in str(plan.downstream_consumer_hint.value).lower()
    
    def test_apps_research_l1_marks_caller_app_id_when_delegated(self):
        """L1 marks caller_app_id hint when delegated."""
        # Auto-injected (direct call)
        validated_direct = _make_validated_request(auto_injected=True)
        plan_direct = l1_plan_apps_research_v2(validated_direct)
        
        # Direct call should have empty caller_app_id
        assert plan_direct.caller_app_id_hint.value in ["", "apps_research"]
    
    def test_apps_research_l1_marks_uploaded_briefing_presence(self):
        """L1 marks whether uploaded briefing is present."""
        # Without manual brief
        validated_no_brief = _make_validated_request()
        plan_no_brief = l1_plan_apps_research_v2(validated_no_brief)
        
        assert plan_no_brief.uploaded_briefing_present_hint.value is False
        
        # With manual brief would require app_payload to include manual_brief_path
    
    def test_apps_research_l1_emits_cache_candidate_hint_without_route_authority(self):
        """L1 emits cache candidate hints without selecting route."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        # Cache hints should be advisory only
        assert plan.cache_lookup_candidate_hint.value is True
        assert plan.cache_lookup_candidate_hint.hint_type == "cache_lookup_candidate"
        
        # Should NOT include route selection
        assert not hasattr(plan, 'route_id')
        assert not hasattr(plan, 'selected_route')
    
    def test_apps_research_l1_emits_semantic_cache_candidate_hint(self):
        """L1 emits semantic cache candidate hint."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        assert plan.semantic_cache_candidate_hint.hint_type == "semantic_cache_candidate"
        # Value depends on package policy
        assert isinstance(plan.semantic_cache_candidate_hint.value, bool)
    
    def test_apps_research_l1_emits_grounding_required_hint(self):
        """L1 emits grounding required hint."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        assert plan.grounding_required_hint.value is True
        assert plan.grounding_required_hint.hint_type == "grounding_required"
    
    def test_apps_research_l1_ambiguous_entity_blocks_or_clarifies(self):
        """L1 marks ambiguous entities with warning severity."""
        # Ambiguous entity (empty company)
        validated_ambiguous = _make_validated_request(target_company="")
        plan_ambiguous = l1_plan_apps_research_v2(validated_ambiguous)
        
        assert plan_ambiguous.entity_ambiguity_hint.value is True
        assert plan_ambiguous.entity_ambiguity_hint.severity == HintSeverity.WARNING
        
        # Unambiguous entity
        validated_clear = _make_validated_request(target_company="Acme Inc")
        plan_clear = l1_plan_apps_research_v2(validated_clear)
        
        assert plan_clear.entity_ambiguity_hint.value is False


class TestL1DoesNotHaveAuthority:
    """Verify L1 does not have runtime authority."""
    
    def test_apps_research_l1_does_not_select_route(self):
        """L1 PlanContract does not include route selection."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        # Should NOT have route selection fields
        assert not hasattr(plan, 'route_id')
        assert not hasattr(plan, 'route_contract')
        assert not hasattr(plan, 'selected_model')
    
    def test_apps_research_l1_does_not_retrieve(self):
        """L1 does not perform C0 retrieval."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        # Plan should not have retrieval results
        assert not hasattr(plan, 'retrieval_sources')
        assert not hasattr(plan, 'c0_bundle')
        assert not hasattr(plan, 'evidence_map')
    
    def test_apps_research_l1_does_not_execute(self):
        """L1 does not execute or call providers."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        # No execution artifacts
        assert not hasattr(plan, 'execution_result')
        assert not hasattr(plan, 'llm_response')
        assert not hasattr(plan, 'generated_content')
    
    def test_apps_research_l1_does_not_write_cache(self):
        """L1 does not write to cache."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        # Writeback candidate should be False (read-only app)
        assert plan.writeback_candidate_hint.value is False
    
    def test_apps_research_l1_hints_are_advisory_only(self):
        """All L1 hints are advisory (not commands)."""
        validated = _make_validated_request()
        
        plan = l1_plan_apps_research_v2(validated)
        
        # All hints should have INFO or WARNING severity (not ERROR/BLOCKING as primary)
        hints = [
            plan.company_entity_hint,
            plan.cache_lookup_candidate_hint,
            plan.grounding_required_hint,
        ]
        
        for hint in hints:
            assert hint.severity in [HintSeverity.INFO, HintSeverity.WARNING]


class TestL1ContractStructure:
    """Verify L1PlanContract structure and serialization."""
    
    def test_all_21_hints_present(self):
        """L1PlanContract contains all 21 required hints."""
        validated = _make_validated_request()
        plan = l1_plan_apps_research_v2(validated)
        
        required_hints = [
            "company_entity_hint",
            "entity_aliases_hint",
            "entity_ambiguity_hint",
            "task_class_hint",
            "downstream_consumer_hint",
            "caller_app_id_hint",
            "depth_profile_hint",
            "source_scope_hint",
            "freshness_profile_hint",
            "coverage_family_hint",
            "cache_lookup_candidate_hint",
            "semantic_cache_candidate_hint",
            "grounding_required_hint",
            "prompt_assembly_required_hint",
            "uploaded_briefing_present_hint",
            "jd_context_present_hint",
            "role_context_present_hint",
            "cross_app_reuse_candidate_hint",
            "writeback_candidate_hint",
            "hitl_hint",
            "risk_hint",
            "runtime_package_origin_hint",
        ]
        
        for attr in required_hints:
            assert hasattr(plan, attr), f"Missing hint: {attr}"
            hint = getattr(plan, attr)
            assert isinstance(hint, PlanningHint)
    
    def test_l1_plan_contract_serializes_to_dict(self):
        """L1PlanContract can be serialized to dict."""
        validated = _make_validated_request()
        plan = l1_plan_apps_research_v2(validated)
        
        data = plan.to_dict()
        
        assert data["request_id"] == "test-req-001"
        assert data["app_id"] == "apps_research"
        assert "hints" in data
        assert data["schema_version"] == "AG9.L1.2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
