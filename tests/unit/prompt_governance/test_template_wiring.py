"""Tests for Jinja template wiring completeness across prompt_governance/."""

import json
from pathlib import Path

import pytest


PG_ROOT = Path(__file__).resolve().parents[3] / "agentic_core" / "prompt_governance"


class TestAllTemplatesInCatalog:
    """Every .jinja file on disk must have a catalog entry."""

    def _discover_disk_templates(self) -> set[str]:
        """Find all .jinja filenames on disk."""
        md_files = set()
        for jinja in PG_ROOT.rglob("*.jinja"):
            md_files.add(jinja.name)
        return md_files

    def test_every_disk_template_has_catalog_entry(self):
        from agentic_core.prompt_governance.core.template_catalog import (
            TEMPLATE_BY_NAME,
            TEMPLATE_CATALOG,
            TemplateCategory,
            TemplateStatus,
            get_active_templates,
            get_deprecated_templates,
            get_orphan_templates,
            get_templates_for_agent,
        )
                from agentic_core.prompt_governance.core.sovereign_prompt_renderer import (
                    SovereignPromptRenderer,
                )
                from agentic_core.prompt_governance.core.sovereign_prompt_renderer import (
                    SovereignPromptRenderer,
                )

        disk = self._discover_disk_templates()
        catalog_names = set(TEMPLATE_BY_NAME.keys())
        missing = disk - catalog_names
        assert not missing, (
            f"Templates on disk but NOT in catalog: {sorted(missing)}. Add entries to template_catalog.py."
        )

    def test_no_phantom_catalog_entries(self):
        """Catalog entries must correspond to real files."""
        disk = self._discover_disk_templates()
        catalog_names = set(TEMPLATE_BY_NAME.keys())
        phantom = catalog_names - disk
        assert not phantom, (
            f"Catalog entries with NO file on disk: {sorted(phantom)}. "
            "Remove stale entries or restore missing templates."
        )

    def test_catalog_count_matches_disk(self):
        disk = self._discover_disk_templates()
        # Exclude the INSTRUCTIONAL_INJECTION_PATTERNS.md which is not .jinja
        assert len(TEMPLATE_CATALOG) == len(disk), (
            f"Catalog has {len(TEMPLATE_CATALOG)} entries but disk has {len(disk)} .jinja files"
        )


class TestCatalogIntegrity:
    """Validate catalog entry consistency."""

    def test_no_duplicate_entries(self):
        names = [e.template_name for e in TEMPLATE_CATALOG]
        assert len(names) == len(set(names)), (
            f"Duplicate catalog entries: {[n for n in names if names.count(n) > 1]}"
        )

    def test_all_entries_have_purpose(self):
        for entry in TEMPLATE_CATALOG:
            assert entry.purpose, f"No purpose for {entry.template_name}"

    def test_all_entries_have_category(self):
        for entry in TEMPLATE_CATALOG:
            assert isinstance(entry.category, TemplateCategory), f"Invalid category for {entry.template_name}"

    def test_active_templates_have_consumers(self):
        """Every ACTIVE template should have at least one consumer agent."""
        no_consumers = [
            e.template_name
            for e in TEMPLATE_CATALOG
            if e.status == TemplateStatus.ACTIVE and not e.consumer_agents
        ]
        assert not no_consumers, f"Active templates without consumer agents: {no_consumers}"


class TestCategoryCorrectness:
    """Templates must be in the right category matching their disk location."""

    def test_instructional_templates_exist_on_disk(self):
        for entry in TEMPLATE_CATALOG:
            if entry.category == TemplateCategory.INSTRUCTIONAL:
                path = PG_ROOT / "templates" / entry.template_name
                assert path.exists(), f"INSTRUCTIONAL template {entry.template_name} not found at {path}"

    def test_meta_prompt_templates_exist_on_disk(self):
        for entry in TEMPLATE_CATALOG:
            if entry.category == TemplateCategory.META_PROMPT:
                path = PG_ROOT / "meta_prompts" / entry.template_name
                assert path.exists(), f"META_PROMPT template {entry.template_name} not found at {path}"

    def test_adversarial_templates_exist_on_disk(self):
        for entry in TEMPLATE_CATALOG:
            if entry.category == TemplateCategory.ADVERSARIAL:
                path = PG_ROOT / "security" / "adversarial" / entry.template_name
                assert path.exists(), f"ADVERSARIAL template {entry.template_name} not found at {path}"


class TestRegistryJsonSync:
    """registry.json must be in sync with the catalog."""

    @pytest.fixture
    def registry(self):
        reg_path = PG_ROOT / "registry" / "registry.json"
        assert reg_path.exists(), "registry.json not found"
        return json.loads(reg_path.read_text(encoding="utf-8"))

    def test_all_active_templates_in_registry(self, registry):
        active = get_active_templates()
        reg_names = set(registry.get("prompts", {}).keys())
        active_names = {e.template_name for e in active}
        missing = active_names - reg_names
        assert not missing, f"Active templates NOT in registry.json: {sorted(missing)}"

    def test_registry_entries_are_active_in_catalog(self, registry):
        for name in registry.get("prompts", {}):
            versions = registry["prompts"][name]
            for v in versions:
                if v.get("active"):
                    assert name in TEMPLATE_BY_NAME, f"registry.json has active entry '{name}' not in catalog"


class TestRedTeamAdversarialWiring:
    """All adversarial templates must be in RedTeamAgent.ADVERSARIAL_FRAGMENTS."""

    def test_all_adversarial_templates_assigned_to_redteam(self):
        adversarial = [
            e
            for e in TEMPLATE_CATALOG
            if e.category == TemplateCategory.ADVERSARIAL and e.status == TemplateStatus.ACTIVE
        ]
        for entry in adversarial:
            assert "RedTeamAgent" in entry.consumer_agents, (
                f"Adversarial template {entry.template_name} not assigned to RedTeamAgent"
            )

    def test_adversarial_count(self):
        adversarial = [
            e
            for e in TEMPLATE_CATALOG
            if e.category == TemplateCategory.ADVERSARIAL and e.status == TemplateStatus.ACTIVE
        ]
        assert len(adversarial) == 11, f"Expected 11 adversarial templates, got {len(adversarial)}"


class TestRendererDefaultPath:
    """SovereignPromptRenderer default path must point to actual templates."""

    def test_default_template_root_exists(self):

        renderer = SovereignPromptRenderer()
        assert renderer.template_root.exists(), (
            f"Default template_root does not exist: {renderer.template_root}"
        )

    def test_default_template_root_has_templates(self):

        renderer = SovereignPromptRenderer()
        jinja_files = list(renderer.template_root.glob("*.jinja"))
        assert len(jinja_files) >= 20, (
            f"Expected >= 20 .jinja files in template_root, found {len(jinja_files)}"
        )


class TestGetTemplatesForAgent:
    """Test agent-to-template lookup."""

    def test_redteam_has_adversarial_templates(self):
        templates = get_templates_for_agent("RedTeamAgent")
        names = {t.template_name for t in templates}
        assert "jailbreak_classic.jinja" in names
        assert "cot_jailbreak.jinja" in names
        assert len(templates) >= 11

    def test_gravity_agent_has_gravity_templates(self):
        templates = get_templates_for_agent("GravityLeakRepairAgent")
        names = {t.template_name for t in templates}
        assert "gravity_compliance.jinja" in names
        assert "gravity_repair.jinja" in names

    def test_naming_agent_has_naming_templates(self):
        templates = get_templates_for_agent("NamingAgent")
        names = {t.template_name for t in templates}
        assert "naming_law.jinja" in names
        assert "naming_precision.jinja" in names

    def test_unknown_agent_returns_empty(self):
        templates = get_templates_for_agent("NonExistentAgent")
        assert templates == []

    def test_no_orphan_active_templates(self):
        orphans = get_orphan_templates()
        assert not orphans, f"Orphan active templates (no consumers): {[o.template_name for o in orphans]}"


class TestDeprecatedTemplates:
    """Deprecated templates should have DEPRECATED header in their content."""

    def test_all_meta_prompts_deprecated_or_wired(self):
        meta = [e for e in TEMPLATE_CATALOG if e.category == TemplateCategory.META_PROMPT]
        for entry in meta:
            assert entry.status == TemplateStatus.DEPRECATED or entry.consumer_agents, (
                f"Meta-prompt {entry.template_name} is neither deprecated nor has consumers"
            )

    def test_deprecated_count(self):
        deprecated = get_deprecated_templates()
        assert len(deprecated) >= 13, f"Expected >= 13 deprecated templates, got {len(deprecated)}"
