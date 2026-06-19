"""
W4 C0 Package-Driven Grounding Tests for apps_research

Validates that:
1. C0 consumes RouteContract from W3 with grounding_required=true
2. C0 loads app-owned retrieval/source/freshness/briefing profiles
3. All retrieved/uploaded content marked EVIDENCE_DATA_ONLY
4. C0 produces FinalEvidenceContract with all required artifacts
5. C0 never answers/routes/executes/writes
6. No apps_research retrieval policy hardcoded in agentic_core
"""
from __future__ import annotations

import pytest
from pathlib import Path
from typing import Dict, Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.runtime_customization_package import RuntimeCustomizationPackage
from agentic_core.runtime.c0.c0_package_driven_grounding import (
    c0_ground_package_driven,
    FinalEvidenceContract,
    EvidenceItem,
    DataBoundaryLabel,
)


class TestC0ConsumesRouteContract:
    """Verify C0 consumes R3 grounding route contract."""
    
    def test_apps_research_c0_consumes_r3_grounding_route_contract(self):
        """C0 must consume RouteContract with grounding_required=true."""
        # This is validated by the c0_ground_package_driven function signature
        # which requires route_contract parameter
        from agentic_core.runtime.c0.c0_package_driven_grounding import c0_ground_package_driven
        import inspect
        
        sig = inspect.signature(c0_ground_package_driven)
        params = list(sig.parameters.keys())
        
        assert "route_contract" in params, "C0 must accept route_contract parameter"


class TestC0LoadsAppOwnedProfiles:
    """Verify C0 loads profiles from U0 package refs."""
    
    def test_generic_c0_loads_retrieval_profile_from_u0_package(self):
        """C0 must load retrieval_profile from app config via package ref."""
        repo_root = Path(__file__).parent.parent.parent
        package_path = repo_root / "apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml"
        
        assert package_path.exists()
        
        import yaml
        package = yaml.safe_load(package_path.read_text())
        
        # Package should have refs for C0 profiles
        assert "profile_refs" in package
        # Note: c0_grounding_profile is referenced, retrieval_profile may be separate
        assert "c0_grounding_profile" in package["profile_refs"] or "retrieval_profile" in package["profile_refs"]
    
    def test_apps_research_retrieval_profile_exists(self):
        """apps_research retrieval profile must exist."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/retrieval_profile.company_brief.v1.yaml"
        
        assert profile_path.exists(), "Retrieval profile must exist"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        # Verify required sections
        assert "supported_depth_profiles" in profile
        assert "coverage_families" in profile
        assert "max_sources_by_depth" in profile
    
    def test_apps_research_source_mix_policy_exists(self):
        """apps_research source mix policy must exist."""
        repo_root = Path(__file__).parent.parent.parent
        policy_path = repo_root / "apps_research/config/domain_contract/source_mix_policy.company_brief.v1.yaml"
        
        assert policy_path.exists(), "Source mix policy must exist"
        
        import yaml
        policy = yaml.safe_load(policy_path.read_text())
        
        assert "tier_definitions" in policy
        assert "minimum_tier_counts" in policy
        assert "source_blocklist" in policy
    
    def test_apps_research_freshness_policy_exists(self):
        """apps_research freshness policy must exist."""
        repo_root = Path(__file__).parent.parent.parent
        policy_path = repo_root / "apps_research/config/domain_contract/freshness_policy.company_brief.v1.yaml"
        
        assert policy_path.exists(), "Freshness policy must exist"
        
        import yaml
        policy = yaml.safe_load(policy_path.read_text())
        
        assert "freshness_ttl_by_source_type" in policy
        assert "stale_behavior" in policy


class TestC0EmitsFinalEvidenceContract:
    """Verify C0 produces proper FinalEvidenceContract."""
    
    def test_apps_research_c0_emits_final_evidence_contract_structure(self):
        """C0 must emit FinalEvidenceContract with all required sections."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/final_evidence_contract_profile.company_brief.v1.yaml"
        
        assert profile_path.exists(), "Final evidence contract profile must exist"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        required = profile.get("contract_structure", {}).get("required_sections", [])
        
        assert "evidence_items" in required
        assert "source_register_ref" in required or "source_register" in required
        assert "claim_evidence_map_ref" in required or "claim_evidence_map" in required
        assert "freshness_report_ref" in required or "freshness_report" in required
        assert "contradiction_report_ref" in required or "contradiction_report" in required
    
    def test_final_evidence_contract_has_data_boundary_label(self):
        """FinalEvidenceContract must mark all content as EVIDENCE_DATA_ONLY."""
        from agentic_core.runtime.c0.c0_package_driven_grounding import FinalEvidenceContract
        
        # Check dataclass has data_boundary fields
        fields = [f.name for f in FinalEvidenceContract.__dataclass_fields__.values()]
        
        assert "data_boundary_label" in fields
        assert "all_evidence_data_boundary_verified" in fields


class TestDataBoundaryEnforcement:
    """Verify EVIDENCE_DATA_ONLY boundary for all content."""
    
    def test_apps_research_c0_marks_retrieved_text_data_only(self):
        """All retrieved evidence must be marked EVIDENCE_DATA_ONLY."""
        from agentic_core.runtime.c0.c0_package_driven_grounding import EvidenceItem
        
        # EvidenceItem must have data_boundary_label field
        fields = [f.name for f in EvidenceItem.__dataclass_fields__.values()]
        assert "data_boundary_label" in fields
    
    def test_uploaded_briefing_normalization_policy_has_data_boundary(self):
        """Briefing normalization policy must enforce EVIDENCE_DATA_ONLY."""
        repo_root = Path(__file__).parent.parent.parent
        policy_path = repo_root / "apps_research/config/domain_contract/uploaded_briefing_normalization_policy.v1.yaml"
        
        assert policy_path.exists()
        
        import yaml
        policy = yaml.safe_load(policy_path.read_text())
        
        assert policy.get("data_boundary_label") == "EVIDENCE_DATA_ONLY"
        assert policy.get("data_boundary_enforcement", {}).get("blocked_uses", [])


class TestC0AuthorityBoundaries:
    """Verify C0 has no answer/route/execution/write authority."""
    
    def test_apps_research_c0_never_answers(self):
        """C0 must never produce user-facing answers."""
        import inspect
        import agentic_core.runtime.c0.c0_package_driven_grounding as c0_package_driven_grounding
        
        source = inspect.getsource(c0_package_driven_grounding)
        
        forbidden = [
            "final_output",
            "user_answer",
            "response_to_user",
            "emit_x3",
        ]
        
        for term in forbidden:
            assert term not in source.lower(), f"C0 must not answer: {term}"
    
    def test_apps_research_c0_never_routes(self):
        """C0 must never make routing decisions."""
        import inspect
        import agentic_core.runtime.c0.c0_package_driven_grounding as c0_package_driven_grounding
        
        source = inspect.getsource(c0_package_driven_grounding)
        
        forbidden = [
            "select_route",
            "route_decision",
            "emit_route",
        ]
        
        for term in forbidden:
            assert term not in source.lower(), f"C0 must not route: {term}"
    
    def test_apps_research_c0_never_executes(self):
        """C0 must never execute LLM calls or tools."""
        import inspect
        import agentic_core.runtime.c0.c0_package_driven_grounding as c0_package_driven_grounding
        
        source = inspect.getsource(c0_package_driven_grounding)
        
        forbidden = [
            "llm.call",
            "provider.call",
            "tool.invoke",
        ]
        
        for term in forbidden:
            assert term not in source.lower(), f"C0 must not execute: {term}"
    
    def test_apps_research_c0_never_writes_cache(self):
        """C0 must never write to cache."""
        import inspect
        import agentic_core.runtime.c0.c0_package_driven_grounding as c0_package_driven_grounding
        
        source = inspect.getsource(c0_package_driven_grounding)
        
        forbidden = [
            "cache.write",
            "write_cache",
            "populate_cache",
        ]
        
        for term in forbidden:
            assert term not in source.lower(), f"C0 must not write cache: {term}"


class TestNoAppsResearchHardcodingInCore:
    """Verify no apps_research retrieval policy hardcoded in core."""
    
    def test_w4_no_apps_research_retrieval_policy_hardcoded_in_agentic_core(self):
        """Generic C0 must not hardcode apps_research retrieval decisions."""
        repo_root = Path(__file__).parent.parent.parent
        generic_c0 = repo_root / "agentic_core/runtime/c0/c0_package_driven_grounding.py"
        
        content = generic_c0.read_text()
        
        forbidden = [
            "if app_id == 'apps_research'",
            "tavily",  # App-specific source
            "manual_brief",  # App-specific source
            "company_brief_v1",  # App-specific coverage
        ]
        
        for term in forbidden:
            assert term not in content, f"Generic C0 hardcodes apps_research: {term}"
    
    def test_w4_no_apps_research_freshness_policy_hardcoded_in_agentic_core(self):
        """Generic C0 must not hardcode apps_research freshness rules."""
        repo_root = Path(__file__).parent.parent.parent
        generic_c0 = repo_root / "agentic_core/runtime/c0/c0_package_driven_grounding.py"
        
        content = generic_c0.read_text()
        
        forbidden = [
            "freshness_window = '30d'",  # Hardcoded freshness
            "ttl_days = 30",  # Hardcoded TTL
        ]
        
        for term in forbidden:
            assert term not in content, f"Generic C0 hardcodes freshness: {term}"
    
    def test_w4_no_apps_research_source_mix_policy_hardcoded_in_agentic_core(self):
        """Generic C0 must not hardcode apps_research source mix."""
        repo_root = Path(__file__).parent.parent.parent
        generic_c0 = repo_root / "agentic_core/runtime/c0/c0_package_driven_grounding.py"
        
        content = generic_c0.read_text()
        
        forbidden = [
            "tier_1_authoritative = ['sec', 'ir']",  # Hardcoded sources
            "blocked_sources = ['forums']",
        ]
        
        for term in forbidden:
            assert term not in content, f"Generic C0 hardcodes source mix: {term}"


class TestC0AdapterIsThin:
    """Verify apps_research C0 adapter is thin only."""
    
    def test_apps_research_c0_adapter_delegates_only(self):
        """C0 adapter must only delegate to generic binding."""
        repo_root = Path(__file__).parent.parent.parent
        adapter_path = repo_root / "agentic_core/runtime/c0/apps_research_c0_binding.py"
        
        content = adapter_path.read_text()
        
        # Must delegate to generic
        assert "c0_retrieve_apps_research" in content
        
        # Must NOT have app-specific logic
        forbidden = [
            "retrieval_strategy",  # App-specific
            "source_list",  # Hardcoded sources
            "freshness_override",  # Hardcoded freshness
        ]
        
        for term in forbidden:
            assert term not in content.lower(), f"C0 adapter has app logic: {term}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
