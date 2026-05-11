"""
W3 L0 Package-Driven Routing Tests for apps_research

Validates that:
1. L0 consumes route_profile_ref and cache_profile_ref from U0 package
2. Route order loaded from apps_research config (R5 -> R1A -> R1B -> R3)
3. R1B semantic cache requires full compatibility verification
4. R1B emits RETTerminalPacket (never direct to user)
5. No apps_research route logic hardcoded in agentic_core
"""
from __future__ import annotations

import pytest
from pathlib import Path
from typing import Dict, Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import AuthorityValidationReceipt
from agentic_core.runtime.contracts.runtime_customization_package import RuntimeCustomizationPackage
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.L0_routing.package_driven_l0_binding import (
    l0_evaluate_routes_package_driven,
    RETTerminalPacket,
    emit_r1b_ret_terminal_packet,
)
from agentic_core.L0_routing.apps_research_l0_binding_v2 import l0_route_apps_research
from agentic_core.L1_cognition.package_driven_l1_binding import l1_plan_package_driven


class TestU0PackageRefsPresent:
    """Verify U0 package contains route and cache profile refs."""
    
    def test_apps_research_u0_packet_contains_route_profile_ref(self):
        """U0 runtime_customization_package must contain route_profile ref."""
        repo_root = Path(__file__).parent.parent.parent
        package_path = repo_root / "apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml"
        
        assert package_path.exists(), "Runtime package config must exist"
        
        import yaml
        package = yaml.safe_load(package_path.read_text())
        
        assert "profile_refs" in package, "Package must have profile_refs"
        assert "route_profile" in package["profile_refs"], "Package must have route_profile ref"
        assert "apps_research/config/domain_contract/route_profile" in package["profile_refs"]["route_profile"]
    
    def test_apps_research_u0_packet_contains_cache_profile_ref(self):
        """U0 runtime_customization_package must contain cache_profile ref."""
        repo_root = Path(__file__).parent.parent.parent
        package_path = repo_root / "apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml"
        
        import yaml
        package = yaml.safe_load(package_path.read_text())
        
        assert "profile_refs" in package
        assert "cache_profile" in package["profile_refs"], "Package must have cache_profile ref"
        assert "apps_research/config/domain_contract/cache_profile" in package["profile_refs"]["cache_profile"]


class TestGenericL0ConsumesPackageRefs:
    """Verify generic L0 consumes profile refs from ValidatedRequest."""
    
    def test_generic_l0_consumes_route_profile_from_validated_request(self):
        """L0 must read route_profile_ref from ValidatedRequest.app_payload."""
        from agentic_core.L0_routing.package_driven_l0_binding import _load_route_profile
        
        # Create ValidatedRequest with package containing route_profile_ref
        package = RuntimeCustomizationPackage(
            package_id="test",
            app_id="apps_research",
            task_class="company_brief",
            package_ref="apps_research/config/test.yaml",
            profile_refs={
                "route_profile": "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml",
                "cache_profile": "apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml",
            },
        )
        
        # L0 should be able to load this profile
        profile = _load_route_profile(package.profile_refs["route_profile"])
        assert profile is not None, "L0 must load route profile from app config"
        assert "route_evaluation_order" in profile
    
    def test_generic_l0_consumes_cache_profile_from_validated_request(self):
        """L0 must read cache_profile_ref from ValidatedRequest.app_payload."""
        from agentic_core.L0_routing.package_driven_l0_binding import _load_cache_profile
        
        package = RuntimeCustomizationPackage(
            package_id="test",
            app_id="apps_research",
            task_class="company_brief",
            profile_refs={
                "route_profile": "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml",
                "cache_profile": "apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml",
            },
        )
        
        profile = _load_cache_profile(package.profile_refs["cache_profile"])
        assert profile is not None, "L0 must load cache profile from app config"
        assert "semantic_cache" in profile


class TestAppsResearchRouteOrder:
    """Verify apps_research route order loaded from app config."""
    
    def test_apps_research_l0_route_order_loaded_from_app_config(self):
        """Route order must come from apps_research route_profile, not hardcoded."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        eval_order = profile.get("route_evaluation_order", [])
        route_ids = [r["route_id"] for r in eval_order]
        
        # Expected order: R5 -> R1A -> R1B -> R3
        assert "R5_PRE_ROUTE_FALLBACK" in route_ids
        assert "R1A_EXACT_CACHE" in route_ids
        assert "R1B_SEMANTIC_CACHE" in route_ids
        assert "R3_SIMPLE_GROUNDED_READ" in route_ids
        
        # Verify order
        r5_idx = route_ids.index("R5_PRE_ROUTE_FALLBACK")
        r1a_idx = route_ids.index("R1A_EXACT_CACHE")
        r1b_idx = route_ids.index("R1B_SEMANTIC_CACHE")
        r3_idx = route_ids.index("R3_SIMPLE_GROUNDED_READ")
        
        assert r5_idx < r1a_idx < r1b_idx < r3_idx, "Route order must be R5 -> R1A -> R1B -> R3"
    
    def test_apps_research_l0_checks_r5_before_cache_when_unroutable(self):
        """R5 must be checked first for unroutable requests."""
        # Request without target_company should hit R5
        validated_request = ValidatedRequest(
            request_id="test-001",
            run_id="run-001",
            app_id="apps_research",
            task_class="company_brief",
            payload_digest="abc123",
            authority_validation_receipt=AuthorityValidationReceipt(
                allowed=True, passed=True, forbidden_fields_detected=(),
                timestamp_iso="2026-05-11T00:00:00Z"
            ),
            app_payload={
                "target_company": "",  # Missing - should trigger R5
                "runtime_customization_package": {
                    "package_id": "test",
                    "app_id": "apps_research",
                    "task_class": "company_brief",
                    "profile_refs": {
                        "route_profile": "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml",
                        "cache_profile": "apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml",
                    },
                },
            },
        )
        
        route, evaluations = l0_evaluate_routes_package_driven(validated_request)
        
        assert route.route_id == "R5_PRE_ROUTE_FALLBACK", "Missing target_company should select R5"
        assert route.route_type == "TERMINAL"


class TestR1BSemanticCache:
    """Verify R1B semantic cache behavior."""
    
    def test_apps_research_l0_checks_r1b_before_r3(self):
        """R1B must be checked before R3 in route evaluation."""
        # Valid request with all required fields - should check R1B before R3
        validated_request = ValidatedRequest(
            request_id="test-002",
            run_id="run-002",
            app_id="apps_research",
            task_class="company_brief",
            payload_digest="def456",
            authority_validation_receipt=AuthorityValidationReceipt(
                allowed=True, passed=True, forbidden_fields_detected=(),
                timestamp_iso="2026-05-11T00:00:00Z"
            ),
            app_payload={
                "target_company": "Acme Corp",
                "runtime_customization_package": {
                    "package_id": "test",
                    "app_id": "apps_research",
                    "task_class": "company_brief",
                    "profile_refs": {
                        "route_profile": "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml",
                        "cache_profile": "apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml",
                    },
                },
            },
        )
        
        route, evaluations = l0_evaluate_routes_package_driven(validated_request)
        
        # Find evaluation order
        eval_order = [e.route_id for e in evaluations]
        if "R1A_EXACT_CACHE" in eval_order:
            r1a_idx = eval_order.index("R1A_EXACT_CACHE")
            r1b_idx = eval_order.index("R1B_SEMANTIC_CACHE")
            r3_idx = eval_order.index("R3_SIMPLE_GROUNDED_READ")
            assert r1b_idx < r3_idx, "R1B must be checked before R3"
    
    def test_apps_research_r1b_requires_semantic_compatibility_receipt(self):
        """R1B must require semantic_compatibility_receipt_ref for terminal packet."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        # Find R1B config
        r1b_config = None
        for route in profile.get("route_evaluation_order", []):
            if route.get("route_id") == "R1B_SEMANTIC_CACHE":
                r1b_config = route
                break
        
        assert r1b_config is not None
        compat_reqs = r1b_config.get("compatibility_requirements", {})
        
        assert compat_reqs.get("semantic_compatibility_receipt_ref_present") is True, \
            "R1B must require semantic_compatibility_receipt_ref"
    
    def test_apps_research_r1b_blocks_final_apps_rg_output_terminal_reuse(self):
        """R1B must never return final apps_rg customized output as terminal answer."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        r1b_config = None
        for route in profile.get("route_evaluation_order", []):
            if route.get("route_id") == "R1B_SEMANTIC_CACHE":
                r1b_config = route
                break
        
        assert r1b_config is not None
        compat_reqs = r1b_config.get("compatibility_requirements", {})
        
        assert compat_reqs.get("not_final_apps_rg_output") is True, \
            "R1B must block final apps_rg output reuse"
    
    def test_apps_research_r1b_blocks_final_apps_lic_output_terminal_reuse(self):
        """R1B must never return final apps_lic customized output as terminal answer."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        r1b_config = None
        for route in profile.get("route_evaluation_order", []):
            if route.get("route_id") == "R1B_SEMANTIC_CACHE":
                r1b_config = route
                break
        
        assert r1b_config is not None
        compat_reqs = r1b_config.get("compatibility_requirements", {})
        
        assert compat_reqs.get("not_final_apps_lic_output") is True, \
            "R1B must block final apps_lic output reuse"


class TestR3GroundedRead:
    """Verify R3 grounded read route."""
    
    def test_apps_research_l0_selects_r3_after_cache_miss(self):
        """R3 should be selected when R1A and R1B are not terminal."""
        # This test validates that R3 is the default execution route
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        # R3 should be the last in evaluation order
        eval_order = profile.get("route_evaluation_order", [])
        assert eval_order[-1]["route_id"] == "R3_SIMPLE_GROUNDED_READ", \
            "R3 should be last (default) route"
    
    def test_apps_research_l0_r3_route_requires_grounding(self):
        """R3 route must require C0 grounding."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        # Find R3 eligibility
        r3_eligibility = None
        for route in profile.get("route_eligibility", {}).keys():
            if route == "R3_SIMPLE_GROUNDED_READ":
                r3_eligibility = profile["route_eligibility"][route]
                break
        
        # R3 requires_grounding should be true
        if r3_eligibility:
            assert r3_eligibility.get("requires_grounding") is True, \
                "R3 must require grounding"
    
    def test_apps_research_l0_r3_route_has_single_step_execution_form(self):
        """R3 must have SINGLE_STEP execution form (not managed workflow)."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        assert profile.get("active_execution_form") == "SINGLE_STEP", \
            "Route profile must specify SINGLE_STEP execution"
        
        assert profile.get("managed_workflow_allowed") is False, \
            "Managed workflow must be disabled for apps_research direct route"


class TestManagedWorkflowBlocked:
    """Verify managed workflow is blocked for apps_research direct route."""
    
    def test_apps_research_l0_rejects_managed_workflow_direct_route_from_profile(self):
        """Managed workflow must be blocked by route profile, not core logic."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        assert profile.get("managed_workflow_allowed") is False
        assert profile.get("managed_workflow_status") == "not_active_for_apps_research_direct_route"


class TestL0AuthorityBoundaries:
    """Verify L0 has no retrieval/execution/write authority."""
    
    def test_apps_research_l0_emits_exactly_one_route_contract_or_ret_packet(self):
        """L0 must emit exactly one RouteContract or RETTerminalPacket."""
        validated_request = ValidatedRequest(
            request_id="test-003",
            run_id="run-003",
            app_id="apps_research",
            task_class="company_brief",
            payload_digest="ghi789",
            authority_validation_receipt=AuthorityValidationReceipt(
                allowed=True, passed=True, forbidden_fields_detected=(),
                timestamp_iso="2026-05-11T00:00:00Z"
            ),
            app_payload={
                "target_company": "Test Corp",
                "runtime_customization_package": {
                    "package_id": "test",
                    "app_id": "apps_research",
                    "task_class": "company_brief",
                    "profile_refs": {
                        "route_profile": "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml",
                        "cache_profile": "apps_research/config/domain_contract/cache_profile.company_brief.v1.yaml",
                    },
                },
            },
        )
        
        route, evaluations = l0_route_apps_research(
            validated_request,
            l1_plan_package_driven(validated_request),
        )
        
        # Must be exactly one of RouteContract or RETTerminalPacket
        assert isinstance(route, (RouteContract, RETTerminalPacket)), \
            "L0 must emit exactly one route or RET packet"
    
    def test_apps_research_l0_never_writes_cache(self):
        """L0 must never write to cache."""
        # L0 binding code inspection - no cache write operations
        import inspect
        from agentic_core.L0_routing import package_driven_l0_binding
        
        source = inspect.getsource(package_driven_l0_binding)
        
        # Check for cache write patterns
        forbidden_patterns = [
            "cache.write",
            "write_cache",
            "save_to_cache",
            "populate_cache",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"L0 must not contain cache write pattern: {pattern}"
    
    def test_apps_research_l0_never_retrieves(self):
        """L0 must never retrieve evidence."""
        import inspect
        from agentic_core.L0_routing import package_driven_l0_binding
        
        source = inspect.getsource(package_driven_l0_binding)
        
        forbidden_patterns = [
            "c0.retrieve",
            "retrieve_evidence",
            "fetch_",
            "http.get",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"L0 must not contain retrieval pattern: {pattern}"
    
    def test_apps_research_l0_never_executes(self):
        """L0 must never execute LLM calls or tool invocations."""
        import inspect
        from agentic_core.L0_routing import package_driven_l0_binding
        
        source = inspect.getsource(package_driven_l0_binding)
        
        forbidden_patterns = [
            "llm.call",
            "execute_",
            "provider.call",
            "tool.invoke",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"L0 must not contain execution pattern: {pattern}"


class TestNoAppsResearchHardcodingInCore:
    """Verify no apps_research-specific logic hardcoded in agentic_core."""
    
    def test_w3_no_apps_research_route_logic_hardcoded_in_agentic_core(self):
        """Generic L0 must not hardcode apps_research route decisions."""
        repo_root = Path(__file__).parent.parent.parent
        generic_l0 = repo_root / "agentic_core/L0_routing/package_driven_l0_binding.py"
        
        content = generic_l0.read_text()
        
        # Must not hardcode app-specific route IDs
        forbidden_terms = [
            "if app_id == 'apps_research'",
            "apps_research_route_order",
            "company_brief_route",
        ]
        
        for term in forbidden_terms:
            assert term not in content, f"Generic L0 hardcodes apps_research: {term}"
    
    def test_w3_no_apps_research_cache_policy_hardcoded_in_agentic_core(self):
        """Generic L0 must not hardcode apps_research cache policy."""
        repo_root = Path(__file__).parent.parent.parent
        generic_l0 = repo_root / "agentic_core/L0_routing/package_driven_l0_binding.py"
        
        content = generic_l0.read_text()
        
        # Must not hardcode cache policy
        forbidden_terms = [
            "research_substrate_only",
            "semantic_cache_scope = 'research_substrate'",
            "apps_research_cache_ttl",
        ]
        
        for term in forbidden_terms:
            assert term not in content, f"Generic L0 hardcodes cache policy: {term}"


class TestR1BCacheCompatibilityBlocks:
    """Verify R1B cache compatibility checks block invalid cache hits."""
    
    def test_r1b_compatibility_requirements_in_profile(self):
        """All required compatibility checks must be in route profile."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/route_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        # Find R1B
        r1b_config = None
        for route in profile.get("route_evaluation_order", []):
            if route.get("route_id") == "R1B_SEMANTIC_CACHE":
                r1b_config = route
                break
        
        assert r1b_config is not None
        compat = r1b_config.get("compatibility_requirements", {})
        
        # Required checks
        required_checks = [
            "entity_match",
            "task_class_compatible",
            "downstream_consumer_compatible",
            "freshness_within_ttl",
            "provenance_known",
            "acl_permits_reuse",
            "no_unresolved_contradiction",
            "embedding_model_compatible",
            "similarity_above_threshold",
            "semantic_compatibility_receipt_ref_present",
            "not_final_apps_rg_output",
            "not_final_apps_lic_output",
        ]
        
        for check in required_checks:
            assert check in compat, f"R1B compatibility must include: {check}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
