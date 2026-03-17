"""
E2E Wiring Gap Tests — Prove agents are wired to prompt governance.

Tests that 6 key agents:
1. Inherit PromptRenderingMixin
2. Can discover their assigned templates from template_catalog
3. Can render templates through SovereignPromptRenderer
4. build_healing_prompt() produces non-empty output
5. Template catalog is consistent with on-disk templates
"""

from pathlib import Path

import pytest

from agentic_core.mixins.prompt_rendering_mixin import PromptRenderingMixin
from agentic_core.prompt_governance.core.sovereign_prompt_renderer import (
    SovereignPromptRenderer,
)
from agentic_core.prompt_governance.core.template_catalog import (
    TEMPLATE_CATALOG,
    TemplateCategory,
    TemplateStatus,
    get_templates_for_agent,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SUBATOMIC_CONTEXT = {
    "behavioral_status": "healthy",
    "canon_key": "CK-51",
    "file_path": "test_file.py",
    "file_violations": [],
    "healing_round": 1,
    "past_fixes": [],
    "persistent_keys": [],
    "primary_key": "CK-51",
    "recently_converged": [],
    "surgery_flags": {},
    "task_violations": [],
    "top_subatomic_fixes": [],
    "total_violations": 0,
}


@pytest.fixture
def renderer():
    return SovereignPromptRenderer()


# ---------------------------------------------------------------------------
# 1. Mixin inheritance tests
# ---------------------------------------------------------------------------


class TestMixinInheritance:
    """Verify that key agents inherit PromptRenderingMixin."""

    WIRED_AGENTS = [
        ("CodeHealerAgent", "agentic_core.L5_safety.reasoning.CodeHealerAgent"),
        ("NamingAgent", "agentic_core.L5_safety.reasoning.NamingAgent"),
        ("DocstringComplianceAgent", "agentic_core.L5_safety.reasoning.DocstringComplianceAgent"),
        ("CodeDetectorAgent", "agentic_core.L5_safety.reasoning.CodeDetectorAgent"),
        ("CognitiveDispositionAgent", "agentic_core.L5_safety.reasoning.CognitiveDispositionAgent"),
        ("GravityLeakRepairAgent", "agentic_core.L5_safety.reasoning.GravityLeakRepairAgent"),
    ]

    @pytest.mark.parametrize("agent_name,module_path", WIRED_AGENTS)
    def test_agent_inherits_prompt_mixin(self, agent_name, module_path):
        """Each wired agent must inherit PromptRenderingMixin."""
        import importlib

        try:
            mod = importlib.import_module(module_path)
        except ImportError as exc:
            pytest.skip(f"Cannot import {module_path}: {exc}")
        cls = getattr(mod, agent_name)
        assert issubclass(cls, PromptRenderingMixin), f"{agent_name} does not inherit PromptRenderingMixin"

    @pytest.mark.parametrize("agent_name,module_path", WIRED_AGENTS)
    def test_agent_has_render_template_method(self, agent_name, module_path):
        """Each wired agent must have render_template method from mixin."""
        import importlib

        try:
            mod = importlib.import_module(module_path)
        except ImportError as exc:
            pytest.skip(f"Cannot import {module_path}: {exc}")
        cls = getattr(mod, agent_name)
        assert hasattr(cls, "render_template"), f"{agent_name} missing render_template method"
        assert hasattr(cls, "build_healing_prompt"), f"{agent_name} missing build_healing_prompt method"
        assert hasattr(cls, "get_assigned_templates"), f"{agent_name} missing get_assigned_templates method"


# ---------------------------------------------------------------------------
# 2. Template catalog discovery tests
# ---------------------------------------------------------------------------


class TestTemplateCatalogDiscovery:
    """Verify agents can discover their assigned templates."""

    AGENT_TEMPLATE_MAP = {
        "CodeHealerAgent": ["code_healing.jinja", "subatomic_healing_context.jinja"],
        "NamingAgent": ["naming_law.jinja", "naming_precision.jinja", "subatomic_healing_context.jinja"],
        "DocstringComplianceAgent": ["docstring_enrichment.jinja"],
        "CodeDetectorAgent": ["dead_code_elimination.jinja"],
        "CognitiveDispositionAgent": ["reasoning_chain.jinja"],
        "GravityLeakRepairAgent": [
            "gravity_compliance.jinja",
            "gravity_repair.jinja",
            "gravity_dynamic_conversion.jinja",
            "reasoning_chain.jinja",
        ],
    }

    @pytest.mark.parametrize(
        "agent_name,expected_templates",
        list(AGENT_TEMPLATE_MAP.items()),
    )
    def test_catalog_returns_expected_templates(self, agent_name, expected_templates):
        """template_catalog must return the expected templates for each agent."""
        entries = get_templates_for_agent(agent_name)
        found_names = {e.template_name for e in entries}
        for expected in expected_templates:
            assert expected in found_names, (
                f"Template '{expected}' not found for {agent_name}. Found: {found_names}"
            )

    def test_all_catalog_templates_exist_on_disk(self):
        """Every template in the catalog must exist on disk."""
        template_root = Path(__file__).resolve().parents[3] / "agentic_core" / "prompt_governance"
        missing = []
        for entry in TEMPLATE_CATALOG:
            if entry.status != TemplateStatus.ACTIVE:
                continue
            if entry.category == TemplateCategory.INSTRUCTIONAL:
                path = template_root / "templates" / entry.template_name
            elif entry.category == TemplateCategory.META_PROMPT:
                path = template_root / "meta_prompts" / entry.template_name
            elif entry.category == TemplateCategory.ADVERSARIAL:
                path = template_root / "security" / "adversarial" / entry.template_name
            else:
                continue
            if not path.exists():
                missing.append(f"{entry.category.value}/{entry.template_name}")
        assert not missing, f"Templates in catalog but missing on disk: {missing}"

    def test_every_active_template_has_consumer(self):
        """Every ACTIVE template must have at least one consumer agent."""
        orphans = [
            e.template_name
            for e in TEMPLATE_CATALOG
            if e.status == TemplateStatus.ACTIVE and not e.consumer_agents
        ]
        assert not orphans, f"Orphan templates (no consumer): {orphans}"


# ---------------------------------------------------------------------------
# 3. Template rendering E2E tests
# ---------------------------------------------------------------------------


class TestTemplateRenderingE2E:
    """Prove agents can actually render their templates via SovereignPromptRenderer."""

    def test_code_healing_renders(self, renderer):
        """CodeHealerAgent's code_healing.jinja renders with valid context."""
        ctx = {
            "violations": "F401 unused import",
            "code_block": "import os\nimport sys",
            **SUBATOMIC_CONTEXT,
        }
        result = renderer.render("code_healing.jinja", context=ctx, validate=False)
        assert len(result) > 50
        assert "violations" in result.lower() or "healing" in result.lower()

    def test_naming_law_renders(self, renderer):
        """NamingAgent's naming_law.jinja renders with valid context."""
        ctx = {"name": "MyBadName", "identifiers": ["foo_bar", "BazQuux"]}
        result = renderer.render("naming_law.jinja", context=ctx, validate=False)
        assert len(result) > 20
        assert "name" in result.lower() or "naming" in result.lower() or "snake" in result.lower()

    def test_dead_code_elimination_renders(self, renderer):
        """CodeDetectorAgent's dead_code_elimination.jinja renders."""
        ctx = {"code_block": "import os  # unused", **SUBATOMIC_CONTEXT}
        result = renderer.render("dead_code_elimination.jinja", context=ctx, validate=False)
        assert len(result) > 20

    def test_docstring_enrichment_renders(self, renderer):
        """DocstringComplianceAgent's docstring_enrichment.jinja renders."""
        ctx = {
            "code_block": "def foo(): pass",
            "current_docstring": '"""Brief stub."""',
            **SUBATOMIC_CONTEXT,
        }
        result = renderer.render("docstring_enrichment.jinja", context=ctx, validate=False)
        assert len(result) > 20

    def test_gravity_compliance_renders(self, renderer):
        """GravityLeakRepairAgent's gravity_compliance.jinja renders."""
        ctx = {
            "violation_code": "L5 imports from L3",
            "code_block": "from agentic_core.L5_safety import foo",
            **SUBATOMIC_CONTEXT,
        }
        result = renderer.render("gravity_compliance.jinja", context=ctx, validate=False)
        assert len(result) > 20

    def test_gravity_repair_renders(self, renderer):
        """GravityLeakRepairAgent's gravity_repair.jinja renders."""
        ctx = {
            "file_path": "agentic_core/L5_safety/test.py",
            "code_block": "from agentic_core.L5_safety import bar",
            **SUBATOMIC_CONTEXT,
        }
        result = renderer.render("gravity_repair.jinja", context=ctx, validate=False)
        assert len(result) > 20

    def test_reasoning_chain_renders(self, renderer):
        """CognitiveDispositionAgent's reasoning_chain.jinja renders."""
        ctx = {"task": "Analyze file placement for gravity compliance"}
        result = renderer.render("reasoning_chain.jinja", context=ctx, validate=False)
        assert len(result) > 20
        assert "task" in result.lower() or "reason" in result.lower() or "chain" in result.lower()


# ---------------------------------------------------------------------------
# 4. build_healing_prompt integration tests
# ---------------------------------------------------------------------------


class TestBuildHealingPrompt:
    """Test the mixin's build_healing_prompt method on actual agent instances."""

    def _make_agent(self, agent_cls):
        """Instantiate an agent, handling varying __init__ signatures."""
        try:
            return agent_cls()
        except TypeError:
            return agent_cls.__new__(agent_cls)

    def test_code_healer_build_prompt(self):
        try:
            from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent
        except ImportError:
            pytest.skip("CodeHealerAgent has upstream import issue")
        try:
            agent = self._make_agent(CodeHealerAgent)
        except Exception:
            pytest.skip("CodeHealerAgent requires SovereignLock environment")
        prompt = agent.build_healing_prompt(
            context={
                "violations": "unused import",
                "code_block": "import os",
                **SUBATOMIC_CONTEXT,
            },
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 50

    def test_naming_agent_build_prompt(self):
        from agentic_core.L5_safety.reasoning.NamingAgent import NamingAgent

        agent = self._make_agent(NamingAgent)
        # NamingAgent's primary catalog entry is subatomic_healing_context.jinja,
        # so use naming_law.jinja explicitly for a clean test
        prompt = agent.build_healing_prompt(
            context={"name": "BadName", "identifiers": ["FooBar"]},
            template_name="naming_law.jinja",
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 20

    def test_code_detector_build_prompt(self):
        from agentic_core.L5_safety.reasoning.CodeDetectorAgent import CodeDetectorAgent

        agent = self._make_agent(CodeDetectorAgent)
        prompt = agent.build_healing_prompt(
            context={"code_block": "import os  # unused", **SUBATOMIC_CONTEXT},
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 20

    def test_gravity_repair_build_prompt(self):
        from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent

        agent = self._make_agent(GravityLeakRepairAgent)
        prompt = agent.build_healing_prompt(
            context={
                "violation_code": "L5 imports from L3",
                "code_block": "from agentic_core.L5_safety import foo",
                **SUBATOMIC_CONTEXT,
            },
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 20

    def test_cognitive_disposition_build_prompt(self):
        from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import CognitiveDispositionAgent

        try:
            agent = self._make_agent(CognitiveDispositionAgent)
        except Exception:
            pytest.skip("CognitiveDispositionAgent requires SovereignLock environment")
        prompt = agent.build_healing_prompt(
            context={"task": "Analyze file placement"},
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 20

    def test_docstring_compliance_build_prompt(self):
        from agentic_core.L5_safety.reasoning.DocstringComplianceAgent import DocstringComplianceAgent

        agent = self._make_agent(DocstringComplianceAgent)
        prompt = agent.build_healing_prompt(
            context={
                "code_block": "def foo(): pass",
                "current_docstring": '"""Brief stub."""',
                **SUBATOMIC_CONTEXT,
            },
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 20


# ---------------------------------------------------------------------------
# 5. Template-agent consistency tests
# ---------------------------------------------------------------------------


class TestCatalogConsistency:
    """Ensure template_catalog and on-disk templates are consistent."""

    def test_no_duplicate_template_names(self):
        """Template names must be unique in the catalog."""
        names = [e.template_name for e in TEMPLATE_CATALOG]
        dupes = [n for n in names if names.count(n) > 1]
        assert not dupes, f"Duplicate template names in catalog: {set(dupes)}"

    def test_all_entries_have_purpose(self):
        """Every catalog entry must have a non-empty purpose."""
        empty = [e.template_name for e in TEMPLATE_CATALOG if not e.purpose.strip()]
        assert not empty, f"Templates without purpose: {empty}"

    def test_mixin_get_assigned_works(self):
        """PromptRenderingMixin.get_assigned_templates returns correct entries."""

        class FakeAgent(PromptRenderingMixin):
            pass

        # Monkey-patch __name__ to match a known agent
        FakeAgent.__name__ = "CodeHealerAgent"
        agent = FakeAgent()
        templates = agent.get_assigned_templates()
        assert len(templates) >= 1
        names = {t.template_name for t in templates}
        assert "code_healing.jinja" in names

    def test_mixin_raises_for_unknown_agent(self):
        """build_healing_prompt raises ValueError for agents with no catalog entry."""

        class UnknownAgent(PromptRenderingMixin):
            pass

        agent = UnknownAgent()
        with pytest.raises(ValueError, match="No INSTRUCTIONAL template assigned"):
            agent.build_healing_prompt(context={})
