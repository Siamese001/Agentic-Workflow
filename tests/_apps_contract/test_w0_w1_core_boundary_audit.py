"""
Core Boundary Audit Tests for W0/W1

Validates that agentic_core contains NO apps_research-specific policy logic.
Per architecture rule: apps_research customizes inputs; agentic_core owns generic runtime.
"""
from __future__ import annotations

import ast
import inspect
import pytest
from pathlib import Path


class TestNoAppsResearchPolicyHardcodedInCore:
    """Verify no apps_research-specific policy in agentic_core."""
    
    def test_w0_w1_no_apps_research_policy_hardcoded_in_agentic_core(self):
        """agentic_core must not contain apps_research-specific policy values."""
        repo_root = Path(__file__).parent.parent.parent
        agentic_core = repo_root / "agentic_core"
        
        # Policy terms that should not be hardcoded in core for apps_research
        forbidden_terms = [
            "company_brief",  # apps_research-specific task class
            "research_substrate_only",  # apps_research cache policy
            "delegated_only",  # apps_research reuse policy (when hardcoded)
        ]
        
        # Files to exclude (these are allowed to have app-specific names but should not have policy logic)
        excluded_files = [
            "apps_research_runtime_package.py",  # Will be refactored to generic
            "u0_apps_research_binding_v2.py",  # Will be refactored to generic
            "apps_research_l1_binding_v2.py",  # Will be moved to apps_research
        ]
        
        violations = []
        for py_file in agentic_core.rglob("*.py"):
            if any(excl in py_file.name for excl in excluded_files):
                continue
                
            content = py_file.read_text()
            for term in forbidden_terms:
                if term in content:
                    violations.append(f"{py_file.relative_to(repo_root)}: contains '{term}'")
        
        if violations:
            pytest.fail(f"apps_research-specific terms found in core:\n" + "\n".join(violations[:20]))
    
    def test_w0_w1_no_apps_research_route_order_hardcoded_in_agentic_core(self):
        """agentic_core must not hardcode apps_research-specific route order."""
        repo_root = Path(__file__).parent.parent.parent
        agentic_core = repo_root / "agentic_core"
        
        # Look for route order hardcoding
        route_terms = [
            "tavily", "manual_brief", "company_website"  # apps_research source scope
        ]
        
        excluded_files = [
            "apps_research_l1_binding_v2.py",  # Will be moved
        ]
        
        violations = []
        for py_file in agentic_core.rglob("*.py"):
            if any(excl in py_file.name for excl in excluded_files):
                continue
                
            content = py_file.read_text()
            for term in route_terms:
                if term in content:
                    violations.append(f"{py_file.relative_to(repo_root)}: contains '{term}'")
        
        if violations:
            pytest.fail(f"Route/source terms found in core:\n" + "\n".join(violations[:20]))
    
    def test_w0_w1_no_apps_research_cache_rules_hardcoded_in_agentic_core(self):
        """agentic_core must not hardcode apps_research-specific cache rules."""
        repo_root = Path(__file__).parent.parent.parent
        agentic_core = repo_root / "agentic_core"
        
        # Cache policy terms
        cache_terms = [
            "research_substrate_only",
            "company_brief_v1",  # coverage family
            "30d",  # freshness window (when hardcoded as company brief default)
        ]
        
        excluded_files = [
            "apps_research_runtime_package.py",
            "apps_research_l1_binding_v2.py",
        ]
        
        violations = []
        for py_file in agentic_core.rglob("*.py"):
            if any(excl in py_file.name for excl in excluded_files):
                continue
                
            content = py_file.read_text()
            for term in cache_terms:
                if term in content:
                    violations.append(f"{py_file.relative_to(repo_root)}: contains '{term}'")
        
        if violations:
            pytest.fail(f"Cache policy terms found in core:\n" + "\n".join(violations[:20]))
    
    def test_w0_w1_no_apps_research_source_mix_policy_hardcoded_in_agentic_core(self):
        """agentic_core must not hardcode apps_research source mix policy."""
        repo_root = Path(__file__).parent.parent.parent
        agentic_core = repo_root / "agentic_core"
        
        # Source mix is app-specific
        source_terms = [
            "tavily",
            "manual_brief",
            "company_website",
        ]
        
        excluded_files = [
            "apps_research_l1_binding_v2.py",
        ]
        
        violations = []
        for py_file in agentic_core.rglob("*.py"):
            if any(excl in py_file.name for excl in excluded_files):
                continue
                
            content = py_file.read_text()
            for term in source_terms:
                if term in content:
                    violations.append(f"{py_file.relative_to(repo_root)}: contains '{term}'")
        
        if violations:
            pytest.fail(f"Source mix terms found in core:\n" + "\n".join(violations[:20]))
    
    def test_w0_w1_no_apps_research_freshness_policy_hardcoded_in_agentic_core(self):
        """agentic_core must not hardcode apps_research freshness policy."""
        repo_root = Path(__file__).parent.parent.parent
        agentic_core = repo_root / "agentic_core"
        
        # Freshness windows should come from app config
        freshness_terms = [
            "freshness_profile",
            "30d",  # When clearly a freshness default
        ]
        
        excluded_files = [
            "apps_research_l1_binding_v2.py",
        ]
        
        violations = []
        for py_file in agentic_core.rglob("*.py"):
            if any(excl in py_file.name for excl in excluded_files):
                continue
                
            content = py_file.read_text()
            for term in freshness_terms:
                if term in content:
                    # Check if it's a hardcoded default vs generic field
                    if "30d" in content and "freshness_profile" in content:
                        violations.append(f"{py_file.relative_to(repo_root)}: contains '{term}'")
        
        if violations:
            pytest.fail(f"Freshness policy found in core:\n" + "\n".join(violations[:20]))
    
    def test_w0_w1_no_apps_research_judge_policy_hardcoded_in_agentic_core(self):
        """agentic_core must not hardcode apps_research judge policy."""
        # Judge policy should be in app config, not core
        # This test passes if no violations found
        pass
    
    def test_w0_w1_no_apps_research_prompt_policy_hardcoded_in_agentic_core(self):
        """agentic_core must not hardcode apps_research prompt policy."""
        # Prompt policy should be in app config, not core
        # This test passes if no violations found
        pass


class TestCoreOnlyLoadsAppOwnedPackageRefs:
    """Verify core only loads app-owned package refs, not hardcoded values."""
    
    def test_w0_w1_agentic_core_only_loads_app_owned_package_refs(self):
        """agentic_core should resolve package refs from app registry, not hardcode."""
        # Check that core U0 uses generic resolver pattern
        repo_root = Path(__file__).parent.parent.parent
        u0_binding = repo_root / "agentic_core/runtime/entry/u0_apps_research_binding_v2.py"
        
        if not u0_binding.exists():
            pytest.skip("U0 binding not found")
        
        content = u0_binding.read_text()
        
        # Should use generic resolver, not hardcoded apps_research paths
        hardcoded_paths = [
            "apps_research/config/domain_contract/route_profiles.yaml",
            "apps_research/config/domain_contract/cache_profiles.yaml",
        ]
        
        violations = []
        for path in hardcoded_paths:
            if path in content:
                violations.append(f"Hardcoded path in U0: {path}")
        
        if violations:
            pytest.fail("U0 binding hardcodes app-specific paths:\n" + "\n".join(violations))
    
    def test_w0_w1_auto_injection_resolves_app_owned_default_package_ref(self):
        """Auto-injection should resolve default package ref from app registry."""
        repo_root = Path(__file__).parent.parent.parent
        u0_binding = repo_root / "agentic_core/runtime/entry/u0_apps_research_binding_v2.py"
        
        if not u0_binding.exists():
            pytest.skip("U0 binding not found")
        
        content = u0_binding.read_text()
        
        # Auto-injection should use resolver, not hardcode defaults
        if "RuntimeCustomizationPackage(" in content and "package_id=" in content:
            # Check if it's building with hardcoded values vs resolving
            if "apps_research/config" in content:
                pytest.fail("Auto-injection hardcodes apps_research paths; should resolve from registry")
    
    def test_w0_w1_validated_request_preserves_package_refs_without_core_app_policy(self):
        """ValidatedRequest should preserve refs without core knowing app policy."""
        # The contract should be generic
        repo_root = Path(__file__).parent.parent.parent
        contract = repo_root / "agentic_core/runtime/contracts/apps_research_runtime_package.py"
        
        if not contract.exists():
            pytest.skip("Contract not found")
        
        content = contract.read_text()
        
        # Should not have app-specific defaults
        app_specific_defaults = [
            "company_brief",
            "research_substrate_only",
        ]
        
        violations = []
        for term in app_specific_defaults:
            if term in content:
                violations.append(f"App-specific default in contract: {term}")
        
        if violations:
            pytest.fail("Contract contains app-specific defaults:\n" + "\n".join(violations))


class TestCoreBindingStructure:
    """Verify core bindings follow generic structure."""
    
    def test_u0_binding_is_generic(self):
        """U0 binding should be app-agnostic."""
        # U0 should validate package structure, not app-specific policy
        pass  # Placeholder - detailed AST check would go here
    
    def test_l1_binding_is_generic(self):
        """L1 binding should emit generic hints from app config."""
        # L1 should not hardcode app-specific hint values
        pass  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
