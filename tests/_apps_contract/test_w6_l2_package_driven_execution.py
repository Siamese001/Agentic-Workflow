"""
W6 Package-Driven L2 Execution Tests for apps_research

Validates that:
1. L2 executes one bounded packet from RouteContract/FinalEvidenceContract/CompiledPromptArtifact
2. L2 consumes app-owned L2/provider/repair profiles
3. L2 calls approved model lane through generic provider gateway
4. L2 emits SealedL2Artifact with full provenance
5. L2 never retrieves, routes, assembles prompts, writes cache/L4
6. No apps_research execution logic hardcoded in core
"""
from __future__ import annotations

import pytest
from pathlib import Path


class TestL2ConsumesBoundedPacket:
    """Verify L2 consumes exactly one bounded packet."""
    
    def test_w6_l2_consumes_route_contract(self):
        """L2 must accept RouteContract as input."""
        import inspect
        from agentic_core.L2_execution.l2_package_driven_executor import l2_execute_package_driven
        
        sig = inspect.signature(l2_execute_package_driven)
        params = list(sig.parameters.keys())
        
        assert "route_contract" in params
    
    def test_w6_l2_consumes_final_evidence_contract(self):
        """L2 must accept FinalEvidenceContract as input."""
        import inspect
        from agentic_core.L2_execution.l2_package_driven_executor import l2_execute_package_driven
        
        sig = inspect.signature(l2_execute_package_driven)
        params = list(sig.parameters.keys())
        
        assert "final_evidence" in params
    
    def test_w6_l2_consumes_compiled_prompt_artifact(self):
        """L2 must accept CompiledPromptArtifact as input."""
        import inspect
        from agentic_core.L2_execution.l2_package_driven_executor import l2_execute_package_driven
        
        sig = inspect.signature(l2_execute_package_driven)
        params = list(sig.parameters.keys())
        
        assert "compiled_prompt" in params


class TestL2LoadsAppOwnedProfiles:
    """Verify L2 loads profiles from U0 package refs."""
    
    def test_w6_l2_execution_profile_loaded_from_apps_research(self):
        """L2 execution profile must exist in apps_research config."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/l2_execution_profile.company_brief.v1.yaml"
        
        assert profile_path.exists(), "L2 execution profile must exist"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        assert "execution_bounds" in profile
        assert "provider_lane" in profile
    
    def test_w6_provider_profile_loaded_from_apps_research(self):
        """Provider profile must exist in apps_research config."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/provider_profile.company_brief.v1.yaml"
        
        assert profile_path.exists(), "Provider profile must exist"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        assert "approved_model_lanes" in profile
    
    def test_w6_repair_profile_loaded_from_apps_research(self):
        """Repair profile must exist in apps_research config."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/repair_profile.company_brief.v1.yaml"
        
        assert profile_path.exists(), "Repair profile must exist"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        assert "repair_strategy" in profile
        assert "same_authority_only" in profile.get("repair_authority", {})


class TestL2EmitsSealedArtifact:
    """Verify L2 emits proper SealedL2Artifact."""
    
    def test_w6_l2_emits_sealed_l2_artifact(self):
        """L2 must emit SealedL2Artifact."""
        from agentic_core.L2_execution.l2_package_driven_executor import SealedL2Artifact
        
        # Verify dataclass structure
        fields = [f.name for f in SealedL2Artifact.__dataclass_fields__.values()]
        
        assert "seal_hash" in fields
        assert "execution_status" in fields
        assert "output_content" in fields
        assert "attempt_receipts" in fields
    
    def test_w6_l2_emits_execution_validation_receipt(self):
        """L2 must emit ExecutionValidationReceipt."""
        from agentic_core.L2_execution.l2_package_driven_executor import ExecutionValidationReceipt
        
        fields = [f.name for f in ExecutionValidationReceipt.__dataclass_fields__.values()]
        
        assert "validation_passed" in fields
        assert "schema_compliant" in fields
    
    def test_w6_l2_emits_attempt_receipt(self):
        """L2 must emit AttemptReceipt for each attempt."""
        from agentic_core.L2_execution.l2_package_driven_executor import AttemptReceipt
        
        fields = [f.name for f in AttemptReceipt.__dataclass_fields__.values()]
        
        assert "attempt_number" in fields
        assert "model_lane_used" in fields
        assert "latency_ms" in fields


class TestL2AuthorityBoundaries:
    """Verify L2 has no retrieve/route/write authority."""
    
    def test_w6_l2_never_retrieves(self):
        """L2 must never retrieve evidence."""
        import inspect
        from agentic_core.L2_execution import l2_package_driven_executor
        
        source = inspect.getsource(l2_package_driven_executor)
        
        forbidden = ["c0.retrieve", "fetch_evidence", "get_evidence"]
        for term in forbidden:
            assert term not in source.lower(), f"L2 must not retrieve: {term}"
    
    def test_w6_l2_never_calls_c0(self):
        """L2 must never call C0."""
        import inspect
        from agentic_core.L2_execution import l2_package_driven_executor
        
        source = inspect.getsource(l2_package_driven_executor)
        
        forbidden = ["c0_ground", "c0.retrieve", "call_c0"]
        for term in forbidden:
            assert term not in source.lower(), f"L2 must not call C0: {term}"
    
    def test_w6_l2_never_routes(self):
        """L2 must never make routing decisions."""
        import inspect
        from agentic_core.L2_execution import l2_package_driven_executor
        
        source = inspect.getsource(l2_package_driven_executor)
        
        forbidden = ["select_route", "route_decision", "emit_route"]
        for term in forbidden:
            assert term not in source.lower(), f"L2 must not route: {term}"
    
    def test_w6_l2_never_assembles_prompts(self):
        """L2 must never assemble prompts."""
        import inspect
        from agentic_core.L2_execution import l2_package_driven_executor
        
        source = inspect.getsource(l2_package_driven_executor)
        
        forbidden = ["pa_assemble", "assemble_prompt", "compile_prompt"]
        for term in forbidden:
            assert term not in source.lower(), f"L2 must not assemble prompts: {term}"
    
    def test_w6_l2_never_writes_cache(self):
        """L2 must never write to cache."""
        import inspect
        from agentic_core.L2_execution import l2_package_driven_executor
        
        source = inspect.getsource(l2_package_driven_executor)
        
        forbidden = ["cache.write", "write_cache", "populate_cache"]
        for term in forbidden:
            assert term not in source.lower(), f"L2 must not write cache: {term}"
    
    def test_w6_l2_never_writes_l4(self):
        """L2 must never write to L4 state."""
        import inspect
        from agentic_core.L2_execution import l2_package_driven_executor
        
        source = inspect.getsource(l2_package_driven_executor)
        
        forbidden = ["l4.write", "state.write", "write_state"]
        for term in forbidden:
            assert term not in source.lower(), f"L2 must not write L4: {term}"


class TestNoAppsResearchHardcodingInCore:
    """Verify no apps_research execution logic in core."""
    
    def test_w6_no_apps_research_execution_logic_in_agentic_core(self):
        """Generic L2 must not hardcode apps_research execution."""
        repo_root = Path(__file__).parent.parent.parent
        generic_l2 = repo_root / "agentic_core/L2_execution/l2_package_driven_executor.py"
        
        content = generic_l2.read_text()
        
        forbidden = [
            "if app_id == 'apps_research'",
            "company_brief_execution",
            "research_synthesis_only",
        ]
        
        for term in forbidden:
            assert term not in content, f"Generic L2 hardcodes apps_research: {term}"
    
    def test_w6_no_vllm_url_hardcoded_in_generic_l2(self):
        """Generic L2 must not hardcode vLLM URL."""
        repo_root = Path(__file__).parent.parent.parent
        generic_l2 = repo_root / "agentic_core/L2_execution/l2_package_driven_executor.py"
        
        content = generic_l2.read_text()
        
        forbidden = [
            "localhost:8000",
            "_VLLM_BASE_URL",
        ]
        
        for term in forbidden:
            assert term not in content, f"Generic L2 hardcodes vLLM URL: {term}"
    
    def test_w6_apps_research_l2_adapter_is_thin_only(self):
        """apps_research L2 adapter must only delegate."""
        repo_root = Path(__file__).parent.parent.parent
        adapter_path = repo_root / "agentic_core/L2_execution/apps_research_l2_binding.py"
        
        content = adapter_path.read_text()
        
        # Must delegate to generic
        assert "l2_execute_package_driven" in content
        
        # Must NOT have execution logic
        forbidden = [
            "_call_llm",
            "vllm_url",
            "urllib.request",
        ]
        
        for term in forbidden:
            assert term not in content, f"L2 adapter has execution logic: {term}"


class TestL2ProfileConfiguration:
    """Verify L2 profile configuration correctness."""
    
    def test_w6_l2_execution_bounds_configured(self):
        """L2 execution bounds must be configured."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/l2_execution_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        bounds = profile.get("execution_bounds", {})
        assert "max_attempts" in bounds
        assert "same_authority_repair_allowed" in bounds
    
    def test_w6_l2_same_authority_repair_only(self):
        """L2 repair must be same-authority only."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/repair_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        authority = profile.get("repair_authority", {})
        assert authority.get("same_authority_only") is True
        assert authority.get("cross_authority_repair_blocked") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
