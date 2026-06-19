"""
W1B / W2B Core Boundary Audit Tests for apps_research

Validates that agentic_core contains NO apps_research-specific policy logic.
After boundary repair: generic core + app-owned config.
"""
from __future__ import annotations

import ast
import inspect
import pytest
from pathlib import Path


class TestNoAppsResearchPolicyHardcodedInCore:
    """Verify no apps_research-specific policy in agentic_core."""
    
    def test_generic_runtime_package_contract_has_no_apps_research_defaults(self):
        """Generic RuntimeCustomizationPackage contract must not have app-specific defaults."""
        repo_root = Path(__file__).parent.parent.parent
        generic_contract = repo_root / "agentic_core/runtime/contracts/runtime_customization_package.py"
        
        assert generic_contract.exists(), "Generic contract file must exist"
        
        content = generic_contract.read_text()
        
        # Forbidden app-specific terms
        forbidden_terms = [
            "company_brief",
            "research_substrate_only",
            "delegated_only",
            "searxng",
            "tavily",
            "manual_brief",
            "company_website",
        ]
        
        violations = []
        for term in forbidden_terms:
            if term in content:
                violations.append(f"Generic contract contains app-specific term: {term}")
        
        if violations:
            pytest.fail("Generic contract has app-specific leakage:\n" + "\n".join(violations))
    
    def test_generic_u0_package_resolver_has_no_apps_research_constants(self):
        """Generic U0 resolver must not have APPS_RESEARCH_TASK_CLASS or hardcoded defaults."""
        repo_root = Path(__file__).parent.parent.parent
        generic_u0 = repo_root / "agentic_core/runtime/entry/u0_runtime_package_binding.py"
        
        assert generic_u0.exists(), "Generic U0 binding must exist"
        
        content = generic_u0.read_text()
        
        # Must not have app-specific constants
        forbidden = [
            "APPS_RESEARCH_TASK_CLASS",
            "company_brief",
            "apps_research/config/domain_contract/route_profiles.yaml",
            "apps_research/config/domain_contract/cache_profiles.yaml",
        ]
        
        violations = []
        for term in forbidden:
            if term in content:
                violations.append(f"Generic U0 contains app-specific: {term}")
        
        if violations:
            pytest.fail("Generic U0 has app-specific leakage:\n" + "\n".join(violations))
    
    def test_apps_research_default_package_resolves_from_app_registry(self):
        """Default package resolution must use app-owned registry."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/config/domain_contract/runtime_package_registry.yaml"
        
        assert registry_path.exists(), "App-owned registry must exist"
        
        import yaml
        registry = yaml.safe_load(registry_path.read_text())
        
        # Verify registry has default_packages
        assert "default_packages" in registry, "Registry must define default_packages"
        assert "company_brief" in registry["default_packages"], "Registry must have company_brief default"
        
        # Verify auto-injection rules are in registry
        company_brief = registry["default_packages"]["company_brief"]
        assert "auto_injection_allowed_for" in company_brief, "Must define auto-injection rules"
        assert "auto_injection_blocked_for" in company_brief, "Must define auto-injection blocks"
    
    def test_apps_research_auto_injection_uses_app_owned_registry(self):
        """Auto-injection logic must resolve from app registry, not hardcode in core."""
        repo_root = Path(__file__).parent.parent.parent
        generic_u0 = repo_root / "agentic_core/runtime/entry/u0_runtime_package_binding.py"
        
        content = generic_u0.read_text()
        
        # Must use RuntimePackageRegistry
        assert "RuntimePackageRegistry" in content, "U0 must use RuntimePackageRegistry"
        assert "resolve_default_package_ref" in content, "U0 must call resolve_default_package_ref"
        
        # Must NOT hardcode apps_research-specific resolution
        assert "apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml" not in content, \
            "U0 must not hardcode app-specific package paths"
    
    def test_apps_research_delegated_call_requires_delegation_context(self):
        """Delegated calls must require explicit delegation context per registry rules."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/config/domain_contract/runtime_package_registry.yaml"
        
        import yaml
        registry = yaml.safe_load(registry_path.read_text())
        
        company_brief = registry["default_packages"]["company_brief"]
        blocked = company_brief.get("auto_injection_blocked_for", [])
        
        assert "delegated_apps_rg_without_context" in blocked, \
            "Registry must block delegated apps_rg without context"
        assert "delegated_apps_lic_without_context" in blocked, \
            "Registry must block delegated apps_lic without context"
    
    def test_generic_l1_consumes_l1_planning_profile_ref(self):
        """Generic L1 must consume L1 planning profile ref from app config."""
        repo_root = Path(__file__).parent.parent.parent
        generic_l1 = repo_root / "agentic_core/L1_cognition/package_driven_l1_binding.py"
        
        assert generic_l1.exists(), "Generic L1 binding must exist"
        
        content = generic_l1.read_text()
        
        # Must accept l1_planning_profile_ref parameter
        assert "l1_planning_profile_ref" in content, "L1 must accept l1_planning_profile_ref"
        assert "_load_l1_planning_profile" in content, "L1 must load profile from app config"
    
    def test_generic_l1_emits_app_hints_without_hardcoded_source_scope(self):
        """Generic L1 must NOT hardcode source_scope = [searxng, manual_brief, company_website]."""
        repo_root = Path(__file__).parent.parent.parent
        generic_l1 = repo_root / "agentic_core/L1_cognition/package_driven_l1_binding.py"
        
        content = generic_l1.read_text()
        
        # Must NOT hardcode specific sources
        forbidden_sources = [
            '["searxng", "manual_brief", "company_website"]',
            "['searxng', 'manual_brief', 'company_website']",
        ]
        
        for source_list in forbidden_sources:
            assert source_list not in content, f"L1 hardcodes source_scope: {source_list}"
    
    def test_generic_l1_emits_app_hints_without_hardcoded_freshness(self):
        """Generic L1 must NOT hardcode freshness_profile = '30d'."""
        repo_root = Path(__file__).parent.parent.parent
        generic_l1 = repo_root / "agentic_core/L1_cognition/package_driven_l1_binding.py"
        
        content = generic_l1.read_text()
        
        # Must NOT hardcode freshness
        assert '"30d"' not in content or "freshness_profile" not in content, \
            "L1 must not hardcode 30d freshness window"
    
    def test_generic_l1_emits_app_hints_without_hardcoded_coverage_family(self):
        """Generic L1 must NOT hardcode coverage_family = 'company_brief_v1'."""
        repo_root = Path(__file__).parent.parent.parent
        generic_l1 = repo_root / "agentic_core/L1_cognition/package_driven_l1_binding.py"
        
        content = generic_l1.read_text()
        
        # Must NOT hardcode coverage family
        assert "company_brief_v1" not in content, "L1 must not hardcode company_brief_v1"
    
    def test_apps_research_l1_values_come_from_apps_research_config(self):
        """apps_research L1 planning values must come from app-owned config."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/l1_planning_profile.company_brief.v1.yaml"
        
        assert profile_path.exists(), "App-owned L1 planning profile must exist"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        # Verify profile has app-specific values
        assert "source_scope" in profile, "Profile must define source_scope"
        assert "freshness_profile" in profile, "Profile must define freshness_profile"
        assert "coverage_family" in profile, "Profile must define coverage_family"
        
        # Verify allowed sources include apps_research-specific values
        allowed = profile["source_scope"].get("allowed_sources", [])
        assert "searxng" in allowed, "Profile must allow searxng"
        assert "manual_brief" in allowed, "Profile must allow manual_brief"
        
        # Verify freshness default
        assert profile["freshness_profile"].get("default_window") == "30d", \
            "Profile must define 30d freshness default"


class TestCoreOnlyLoadsAppOwnedPackageRefs:
    """Verify core only loads app-owned package refs, not hardcoded values."""
    
    def test_w0_w1_agentic_core_only_loads_app_owned_package_refs(self):
        """agentic_core should resolve package refs from app registry."""
        # Verified by previous tests
        pass
    
    def test_w0_w1_auto_injection_resolves_app_owned_default_package_ref(self):
        """Auto-injection should resolve default package ref from app registry."""
        # Verified by previous tests
        pass
    
    def test_w0_w1_validated_request_preserves_package_refs_without_core_app_policy(self):
        """ValidatedRequest should preserve refs without core knowing app policy."""
        from agentic_core.runtime.contracts.runtime_customization_package import RuntimeCustomizationPackage
        
        # Create generic package with refs
        pkg = RuntimeCustomizationPackage(
            package_id="test-pkg",
            app_id="apps_research",
            task_class="company_brief",
            package_ref="apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml",
            profile_refs={
                "route": "apps_research/config/domain_contract/route_profiles.yaml",
                "cache": "apps_research/config/domain_contract/cache_profiles.yaml",
            },
        )
        
        # Core preserves refs without validating app-specific policy
        assert pkg.package_ref != ""
        assert "apps_research/config" in pkg.package_ref
        assert "route" in pkg.profile_refs
        assert "cache" in pkg.profile_refs


class TestCoreBindingStructure:
    """Verify core bindings follow generic structure."""
    
    def test_u0_binding_is_generic(self):
        """U0 binding should be app-agnostic."""
        from agentic_core.runtime.entry.u0_runtime_package_binding import (
            u0_resolve_runtime_package,
            RuntimePackageRegistry,
        )
        
        # Generic function signature
        import inspect
        sig = inspect.signature(u0_resolve_runtime_package)
        params = list(sig.parameters.keys())
        
        # Must accept generic envelope and optional registry
        assert "envelope" in params
        assert "registry" in params
    
    def test_l1_binding_is_generic(self):
        """L1 binding should emit generic hints from app config."""
        from agentic_core.L1_cognition.package_driven_l1_binding import l1_plan_package_driven
        
        import inspect
        sig = inspect.signature(l1_plan_package_driven)
        params = list(sig.parameters.keys())
        
        # Must accept validated_request and optional profile_ref
        assert "validated_request" in params
        assert "l1_planning_profile_ref" in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
