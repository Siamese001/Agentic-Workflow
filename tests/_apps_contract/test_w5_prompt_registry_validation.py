"""
W5 Prompt Registry Validation Tests for apps_research

Validates that:
1. All prompt registry templates exist as real files
2. No dangling template references in registry
3. Prompt BOM references resolve to existing registry entries
"""
from __future__ import annotations

import pytest
from pathlib import Path


class TestPromptRegistryTemplatesExist:
    """Verify all referenced templates exist as files."""
    
    def test_w5_all_prompt_registry_templates_exist(self):
        """All templates referenced in registry must exist as files."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/prompts/prompt_registry.yaml"
        
        assert registry_path.exists(), "Prompt registry must exist"
        
        import yaml
        registry = yaml.safe_load(registry_path.read_text())
        
        templates = registry.get("templates", {})
        
        for template_name, template_config in templates.items():
            template_path = template_config.get("path", "")
            if template_path:
                full_path = repo_root / template_path
                assert full_path.exists(), f"Template file missing for {template_name}: {template_path}"
    
    def test_w5_company_brief_synthesis_template_exists(self):
        """company_brief_synthesis_v1 template must exist."""
        repo_root = Path(__file__).parent.parent.parent
        template_path = repo_root / "apps_research/prompts/templates/company_brief_synthesis_v1.jinja"
        
        assert template_path.exists(), "company_brief_synthesis_v1.jinja must exist"
    
    def test_w5_downstream_research_substrate_template_exists(self):
        """downstream_research_substrate_v1 template must exist."""
        repo_root = Path(__file__).parent.parent.parent
        template_path = repo_root / "apps_research/prompts/templates/downstream_research_substrate_v1.jinja"
        
        assert template_path.exists(), "downstream_research_substrate_v1.jinja must exist"
    
    def test_w5_degraded_support_caveat_template_exists(self):
        """degraded_support_caveat_v1 template must exist."""
        repo_root = Path(__file__).parent.parent.parent
        template_path = repo_root / "apps_research/prompts/templates/degraded_support_caveat_v1.jinja"
        
        assert template_path.exists(), "degraded_support_caveat_v1.jinja must exist"
    
    def test_w5_brief_citation_repair_template_exists(self):
        """brief_citation_repair_v1 template must exist."""
        repo_root = Path(__file__).parent.parent.parent
        template_path = repo_root / "apps_research/prompts/templates/brief_citation_repair_v1.jinja"
        
        assert template_path.exists(), "brief_citation_repair_v1.jinja must exist"
    
    def test_w5_system_base_template_exists(self):
        """system_base_v1 template must exist."""
        repo_root = Path(__file__).parent.parent.parent
        template_path = repo_root / "apps_research/prompts/templates/system_base_v1.jinja"
        
        assert template_path.exists(), "system_base_v1.jinja must exist"


class TestPromptBOMReferences:
    """Verify prompt BOM references resolve correctly."""
    
    def test_w5_prompt_bom_references_existing_registry_entries(self):
        """Prompt BOM template refs must match registry entries."""
        repo_root = Path(__file__).parent.parent.parent
        
        bom_path = repo_root / "apps_research/prompts/prompt_bom.yaml"
        registry_path = repo_root / "apps_research/prompts/prompt_registry.yaml"
        
        assert bom_path.exists(), "Prompt BOM must exist"
        assert registry_path.exists(), "Prompt registry must exist"
        
        import yaml
        bom = yaml.safe_load(bom_path.read_text())
        registry = yaml.safe_load(registry_path.read_text())
        
        bom_templates = bom.get("task_templates", {})
        bom_base = bom.get("base_templates", {})
        registry_templates = registry.get("templates", {})
        
        # All BOM template names must exist in registry
        for template_name in bom_templates:
            assert template_name in registry_templates, \
                f"BOM task_template '{template_name}' not found in registry"
        
        for template_name in bom_base:
            assert template_name in registry_templates, \
                f"BOM base_template '{template_name}' not found in registry"


class TestNoDanglingTemplateRefs:
    """Verify no dangling template references."""
    
    def test_w5_no_dangling_prompt_template_refs(self):
        """All template paths in registry must resolve to real files."""
        repo_root = Path(__file__).parent.parent.parent
        registry_path = repo_root / "apps_research/prompts/prompt_registry.yaml"
        
        import yaml
        registry = yaml.safe_load(registry_path.read_text())
        
        templates = registry.get("templates", {})
        dangling = []
        
        for template_name, template_config in templates.items():
            template_path = template_config.get("path", "")
            if template_path:
                full_path = repo_root / template_path
                if not full_path.exists():
                    dangling.append(f"{template_name}: {template_path}")
        
        assert len(dangling) == 0, f"Dangling template references found: {dangling}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
