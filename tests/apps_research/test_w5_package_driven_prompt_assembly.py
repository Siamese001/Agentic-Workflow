"""
W5 Package-Driven Prompt Assembly Tests for apps_research

Validates that:
1. PA consumes prompt_profile_ref from U0 package
2. PA loads prompt BOM, registry, templates from apps_research config
3. Canonical slot order S0-D0-I0-E0-C0-M0-U0-H0-R0 preserved
4. Evidence marked as EVIDENCE_DATA_ONLY
5. No apps_research prompt logic hardcoded in core
"""
from __future__ import annotations

import pytest
from pathlib import Path

class TestPromptProfileRefs:
    """Verify PA consumes profile refs from U0 package."""
    
    def test_w5_prompt_profile_ref_loaded_from_u0_package(self):
        """PA must load prompt_profile ref from runtime_customization_package."""
        repo_root = Path(__file__).parent.parent.parent
        package_path = repo_root / "apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml"
        
        assert package_path.exists()
        
        import yaml
        package = yaml.safe_load(package_path.read_text())
        
        assert "profile_refs" in package
        assert "pa_prompt_profile" in package["profile_refs"]


class TestPromptBOMAndRegistry:
    """Verify PA loads app-owned prompt configuration."""
    
    def test_w5_prompt_bom_loaded_from_apps_research_config(self):
        """PA must load prompt BOM from apps_research/prompts/."""
        repo_root = Path(__file__).parent.parent.parent
        bom_path = repo_root / "apps_research/prompt_assembly/prompt_bom.yaml"
        
        assert bom_path.exists(), "Prompt BOM must exist"
        
        import yaml
        bom = yaml.safe_load(bom_path.read_text())
        
        assert bom["app"] == "apps_research"
        assert bom["bom_id"] == "apps_research_prompt_bom_v1"
        assert bom["required_slots"] == ["S0", "I0", "C0", "U0", "D0", "R0"]
        assert "company_brief_synthesis_v1" in bom["template_registry_refs"]
    
    def test_w5_prompt_registry_loaded_from_apps_research_config(self):
        """PA must load prompt registry from apps_research/prompts/."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/prompts/prompt_registry.yaml"
        
        assert registry_path.exists(), "Prompt registry must exist"
        
        import yaml
        registry = yaml.safe_load(registry_path.read_text())
        
        assert "templates" in registry
        assert "resolution_rules" in registry


class TestTemplateResolution:
    """Verify template resolution from apps_research registry."""
    
    def test_w5_company_brief_template_resolved_from_apps_research(self):
        """company_brief_synthesis_v1 template must resolve from apps_research."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/prompts/prompt_registry.yaml"
        
        import yaml
        registry = yaml.safe_load(registry_path.read_text())
        
        templates = registry.get("templates", {})
        assert "company_brief_synthesis_v1" in templates
        
        template_entry = templates["company_brief_synthesis_v1"]
        assert "path" in template_entry
        assert "apps_research/prompts/templates/" in template_entry["path"]
    
    def test_w5_downstream_substrate_template_resolved_for_apps_rg(self):
        """downstream_research_substrate_v1 must resolve for apps_rg."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/prompts/prompt_registry.yaml"
        
        import yaml
        registry = yaml.safe_load(registry_path.read_text())
        
        resolution_rules = registry.get("resolution_rules", {})
        consumer_rules = resolution_rules.get("by_downstream_consumer", {})
        
        assert consumer_rules.get("apps_rg") == "downstream_research_substrate_v1"
    
    def test_w5_downstream_substrate_template_resolved_for_apps_lic(self):
        """apps_lic_research_substrate_v1 must resolve for apps_lic."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/prompts/prompt_registry.yaml"
        
        import yaml
        registry = yaml.safe_load(registry_path.read_text())
        
        resolution_rules = registry.get("resolution_rules", {})
        consumer_rules = resolution_rules.get("by_downstream_consumer", {})

        assert consumer_rules.get("apps_lic") == "apps_lic_research_substrate_v1"

    def test_w5_executive_brief_template_resolved_for_apps_exec(self):
        """apps_exec_executive_brief_v1 must resolve for apps_exec."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/prompts/prompt_registry.yaml"

        import yaml
        registry = yaml.safe_load(registry_path.read_text())

        resolution_rules = registry.get("resolution_rules", {})
        consumer_rules = resolution_rules.get("by_downstream_consumer", {})

        assert consumer_rules.get("apps_exec") == "apps_exec_executive_brief_v1"

    def test_w5_prompt_profile_includes_apps_lic_consumer_template(self):
        """Prompt profile must expose the apps_lic downstream consumer template."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"

        import yaml
        profile = yaml.safe_load(profile_path.read_text())

        templates = profile.get("template_resolution", {}).get("downstream_consumer_templates", {})

        assert templates.get("apps_lic") == "apps_lic_research_substrate_v1"

    def test_w5_prompt_profile_includes_apps_exec_consumer_template(self):
        """Prompt profile must expose the apps_exec downstream consumer template."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"

        import yaml
        profile = yaml.safe_load(profile_path.read_text())

        templates = profile.get("template_resolution", {}).get("downstream_consumer_templates", {})

        assert templates.get("apps_exec") == "apps_exec_executive_brief_v1"


class TestCanonicalSlotOrder:
    """Verify canonical slot order S0-D0-I0-E0-C0-M0-U0-H0-R0."""
    
    def test_w5_pa_preserves_canonical_slot_order(self):
        """PA must assemble slots in canonical order."""
        from agentic_core.prompt_governance.pa_package_driven_binding import CANONICAL_SLOT_ORDER
        
        expected_order = [
            "S0_system",
            "D0_fences",
            "I0_instructions",
            "E0_approved_examples",
            "C0_verified_evidence",
            "M0_provider_controls",
            "U0_neutralized_user_task",
            "H0_bounded_repair",
            "R0_response_schema",
        ]
        
        assert CANONICAL_SLOT_ORDER == expected_order


class TestEvidenceDataBoundary:
    """Verify EVIDENCE_DATA_ONLY boundary for all evidence."""
    
    def test_w5_pa_places_c0_evidence_only_in_c0_slot(self):
        """C0 evidence must only appear in C0 slot."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        slot_config = profile.get("slot_configuration", {})
        
        # C0 slot must exist
        assert "C0_verified_evidence" in slot_config
        
        # C0 must have data_boundary_label
        c0_config = slot_config["C0_verified_evidence"]
        assert c0_config.get("data_boundary_label") == "EVIDENCE_DATA_ONLY"
    
    def test_w5_pa_marks_retrieved_text_data_only(self):
        """Retrieved evidence must be marked as EVIDENCE_DATA_ONLY."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        evidence_boundary = profile.get("evidence_data_boundary", {})
        
        assert evidence_boundary.get("label") == "EVIDENCE_DATA_ONLY"
        assert "retrieved_evidence" in evidence_boundary.get("enforce_for", [])
    
    def test_w5_pa_marks_uploaded_briefing_data_only(self):
        """Uploaded briefings must be marked as EVIDENCE_DATA_ONLY."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        evidence_boundary = profile.get("evidence_data_boundary", {})
        
        assert "uploaded_briefings" in evidence_boundary.get("enforce_for", [])
    
    def test_w5_pa_marks_cached_substrate_data_only(self):
        """Cached substrate must be marked as EVIDENCE_DATA_ONLY."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        evidence_boundary = profile.get("evidence_data_boundary", {})
        
        assert "cached_research_substrate" in evidence_boundary.get("enforce_for", [])


class TestOutputSchemaBinding:
    """Verify R0 output schema binding."""
    
    def test_w5_pa_binds_output_schema_as_r0(self):
        """Output schema must be bound as R0 slot."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        slot_config = profile.get("slot_configuration", {})
        
        assert "R0_response_schema" in slot_config
        
        r0_config = slot_config["R0_response_schema"]
        assert r0_config.get("source") == "output_schema"
        assert r0_config.get("binding_required") is True


class TestArtifactEmission:
    """Verify PA emits required artifacts."""
    
    def test_w5_pa_emits_compiled_prompt_artifact(self):
        """PA must emit CompiledPromptArtifact."""
        from agentic_core.prompt_governance.pa_package_driven_binding import CompiledPromptArtifact
        
        # Verify dataclass structure
        fields = [f.name for f in CompiledPromptArtifact.__dataclass_fields__.values()]
        
        assert "compilation_hash" in fields
        assert "component_hash_map" in fields
        assert "slot_lineage_map" in fields
        assert "replay_manifest_ref" in fields
        assert "per_input_hash_map" in fields
        assert "system_preamble" in fields
        assert "user_instruction" in fields
    
    def test_w5_pa_emits_prompt_hash(self):
        """CompiledPromptArtifact must include compilation_hash."""
        from agentic_core.prompt_governance.pa_package_driven_binding import CompiledPromptArtifact
        
        fields = [f.name for f in CompiledPromptArtifact.__dataclass_fields__.values()]
        assert "compilation_hash" in fields
    
    def test_w5_pa_emits_component_hash_map(self):
        """CompiledPromptArtifact must include component_hash_map."""
        from agentic_core.prompt_governance.pa_package_driven_binding import CompiledPromptArtifact
        
        fields = [f.name for f in CompiledPromptArtifact.__dataclass_fields__.values()]
        assert "component_hash_map" in fields
    
    def test_w5_pa_emits_slot_lineage_map(self):
        """CompiledPromptArtifact must include slot_lineage_map."""
        from agentic_core.prompt_governance.pa_package_driven_binding import CompiledPromptArtifact
        
        fields = [f.name for f in CompiledPromptArtifact.__dataclass_fields__.values()]
        assert "slot_lineage_map" in fields
    
    def test_w5_pa_emits_replay_manifest_ref(self):
        """CompiledPromptArtifact must include replay_manifest_ref."""
        from agentic_core.prompt_governance.pa_package_driven_binding import CompiledPromptArtifact
        
        fields = [f.name for f in CompiledPromptArtifact.__dataclass_fields__.values()]
        assert "replay_manifest_ref" in fields


class TestPAnAuthorityBoundaries:
    """Verify PA has no retrieve/execute/write authority."""
    
    def test_w5_pa_never_retrieves(self):
        """PA must never retrieve evidence."""
        import inspect
        from agentic_core.prompt_governance import pa_package_driven_binding
        
        source = inspect.getsource(pa_package_driven_binding)
        
        forbidden = [
            "retrieve(",
            ".retrieve(",
            "fetch_evidence(",
            ".fetch_evidence(",
            "get_evidence(",
            ".get_evidence(",
        ]
        for term in forbidden:
            assert term not in source.lower(), f"PA must not retrieve: {term}"
    
    def test_w5_pa_never_executes(self):
        """PA must never execute LLM calls."""
        import inspect
        from agentic_core.prompt_governance import pa_package_driven_binding
        
        source = inspect.getsource(pa_package_driven_binding)
        
        forbidden = ["llm.call", "execute_", "provider.call", "model.generate"]
        for term in forbidden:
            assert term not in source.lower(), f"PA must not execute: {term}"
    
    def test_w5_pa_never_calls_provider(self):
        """PA must never call provider APIs."""
        import inspect
        from agentic_core.prompt_governance import pa_package_driven_binding
        
        source = inspect.getsource(pa_package_driven_binding)
        
        forbidden = ["provider.call", "api.call", "http.post"]
        for term in forbidden:
            assert term not in source.lower(), f"PA must not call provider: {term}"
    
    def test_w5_pa_never_writes_cache(self):
        """PA must never write to cache."""
        import inspect
        from agentic_core.prompt_governance import pa_package_driven_binding
        
        source = inspect.getsource(pa_package_driven_binding)
        
        forbidden = ["cache.write", "write_cache", "populate_cache"]
        for term in forbidden:
            assert term not in source.lower(), f"PA must not write cache: {term}"
    
    def test_w5_pa_never_writes_l4(self):
        """PA must never write to L4 state."""
        import inspect
        from agentic_core.prompt_governance import pa_package_driven_binding
        
        source = inspect.getsource(pa_package_driven_binding)
        
        forbidden = ["l4.write", "state.write", "write_state"]
        for term in forbidden:
            assert term not in source.lower(), f"PA must not write L4: {term}"
    
    def test_w5_pa_does_not_inflate_c0_support_status(self):
        """PA must preserve (not inflate) C0 support_status."""
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"
        
        import yaml
        profile = yaml.safe_load(profile_path.read_text())
        
        support_handling = profile.get("support_status_handling", {})
        assert support_handling.get("preserve_c0_support_status") is True


class TestNoAppsResearchHardcodingInCore:
    """Verify no apps_research prompt logic in core."""
    
    def test_w5_no_apps_research_prompt_names_hardcoded_in_agentic_core(self):
        """Generic PA must not hardcode apps_research template names."""
        repo_root = Path(__file__).parent.parent.parent
        generic_pa = repo_root / "agentic_core/prompt_governance/pa_package_driven_binding.py"
        
        content = generic_pa.read_text()
        
        forbidden = [
            "company_brief_synthesis_v1",
            "downstream_research_substrate_v1",
            "apps_research/prompts/templates/",
        ]
        
        for term in forbidden:
            assert term not in content, f"Generic PA hardcodes apps_research: {term}"
    
    def test_w5_no_company_brief_prompt_logic_hardcoded_in_agentic_core(self):
        """Generic PA must not hardcode company_brief logic."""
        repo_root = Path(__file__).parent.parent.parent
        generic_pa = repo_root / "agentic_core/prompt_governance/pa_package_driven_binding.py"
        
        content = generic_pa.read_text()
        
        forbidden = [
            "if task_class == 'company_brief'",
            "company_brief_template",
            "research_substrate_only",
        ]
        
        for term in forbidden:
            assert term not in content, f"Generic PA hardcodes company_brief: {term}"
    
    def test_w5_apps_research_pa_adapter_is_thin_only(self):
        """apps_research PA adapter must only delegate."""
        repo_root = Path(__file__).parent.parent.parent
        adapter_path = repo_root / "agentic_core/prompt_governance/apps_research_pa_binding.py"
        
        content = adapter_path.read_text()
        
        # Must delegate to generic
        assert "pa_assemble_prompt_package_driven" in content
        
        # Must NOT have slot logic
        forbidden = [
            "S0_system = ",  # Hardcoded slot content
            "C0_evidence = ",
            "assemble_slot",
        ]
        
        for term in forbidden:
            assert term not in content, f"PA adapter has assembly logic: {term}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
