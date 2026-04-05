"""
Tests for prompt category taxonomy.
"""

from agentic_core.L2_execution.reasoning import AuthorityLevel
from agentic_core.L4_state.prompt_taxonomy import (
    CategoryRegistryEntry,
    CategoryTemplate,
    PromptCategory,
    PromptCategoryRegistry,
    get_default_template_path,
)


class TestPromptCategoryEnum:
    """Test the 10 prompt categories with authority levels."""

    def test_all_9_categories_exist(self):
        """Test that all 9 categories are defined."""
        categories = list(PromptCategory)
        assert len(categories) == 9

        names = [c.name for c in categories]
        expected = [
            "USER_PROMPT",
            "INSTRUCTIONAL",
            "INJECTIONS",
            "EXEMPLARS",
            "DEPENDENCY",
            "META_COGNITIVE",
            "SYNTHESIS",
            "SYSTEM_STATE",
            "HEALING_PROPOSAL",
        ]
        for exp in expected:
            assert exp in names

    def test_category_slot_codes(self):
        """Test that categories map to correct slot codes."""
        assert PromptCategory.SYSTEM_STATE.slot_code == "S0"
        assert PromptCategory.INSTRUCTIONAL.slot_code == "I0"
        assert PromptCategory.SYNTHESIS.slot_code == "I0"
        assert PromptCategory.INJECTIONS.slot_code == "D0"
        assert PromptCategory.HEALING_PROPOSAL.slot_code == "D0"
        assert PromptCategory.EXEMPLARS.slot_code == "C0"
        assert PromptCategory.DEPENDENCY.slot_code == "C0"
        assert PromptCategory.META_COGNITIVE.slot_code == "C0"
        assert PromptCategory.USER_PROMPT.slot_code == "U0"

    def test_category_authority_levels(self):
        """Test that categories have correct authority levels."""
        # ABSOLUTE
        assert PromptCategory.SYSTEM_STATE.authority_level == AuthorityLevel.ABSOLUTE

        # GOVERNED
        assert PromptCategory.INSTRUCTIONAL.authority_level == AuthorityLevel.GOVERNED
        assert PromptCategory.SYNTHESIS.authority_level == AuthorityLevel.GOVERNED

        # BINDING
        assert PromptCategory.INJECTIONS.authority_level == AuthorityLevel.BINDING
        assert PromptCategory.HEALING_PROPOSAL.authority_level == AuthorityLevel.BINDING

        # INFO
        assert PromptCategory.EXEMPLARS.authority_level == AuthorityLevel.INFO
        assert PromptCategory.DEPENDENCY.authority_level == AuthorityLevel.INFO
        assert PromptCategory.META_COGNITIVE.authority_level == AuthorityLevel.INFO

        # ZERO
        assert PromptCategory.USER_PROMPT.authority_level == AuthorityLevel.ZERO

    def test_from_slot_code(self):
        """Test looking up categories by slot code."""
        s0_categories = PromptCategory.from_slot_code("S0")
        assert len(s0_categories) == 1
        assert PromptCategory.SYSTEM_STATE in s0_categories

        c0_categories = PromptCategory.from_slot_code("C0")
        assert len(c0_categories) == 3
        assert PromptCategory.EXEMPLARS in c0_categories
        assert PromptCategory.DEPENDENCY in c0_categories
        assert PromptCategory.META_COGNITIVE in c0_categories

    def test_from_authority_level(self):
        """Test looking up categories by authority level."""
        absolute = PromptCategory.from_authority_level(AuthorityLevel.ABSOLUTE)
        assert len(absolute) == 1
        assert PromptCategory.SYSTEM_STATE in absolute

        info = PromptCategory.from_authority_level(AuthorityLevel.INFO)
        assert len(info) == 3


class TestCategoryTemplate:
    """Test CategoryTemplate functionality."""

    def test_template_creation(self):
        """Test creating a category template."""
        template = CategoryTemplate(
            category=PromptCategory.SYSTEM_STATE,
            template_id="S0_system_state",
            template_path="templates/S0_system_state.j2",
            required_variables=["constitution_rules"],
        )

        assert template.category == PromptCategory.SYSTEM_STATE
        assert template.template_id == "S0_system_state"

    def test_validate_variables(self):
        """Test variable validation."""
        template = CategoryTemplate(
            category=PromptCategory.SYSTEM_STATE,
            template_id="test",
            template_path="test.j2",
            required_variables=["required_var"],
            optional_variables=["optional_var"],
        )

        # Missing required
        missing, unknown = template.validate_variables({"optional_var": "value"})
        assert "required_var" in missing

        # Unknown variable
        missing, unknown = template.validate_variables({"required_var": "value", "unknown_var": "value"})
        assert "unknown_var" in unknown

        # Valid
        missing, unknown = template.validate_variables({"required_var": "value", "optional_var": "value"})
        assert not missing
        assert not unknown

    def test_merge_with_defaults(self):
        """Test merging with default values."""
        template = CategoryTemplate(
            category=PromptCategory.SYSTEM_STATE,
            template_id="test",
            template_path="test.j2",
            default_values={"var1": "default1", "var2": "default2"},
        )

        merged = template.merge_with_defaults({"var2": "override"})
        assert merged["var1"] == "default1"
        assert merged["var2"] == "override"

    def test_to_slot(self):
        """Test conversion to AuthoritySlot."""
        template = CategoryTemplate(
            category=PromptCategory.SYSTEM_STATE,
            template_id="S0_system",
            template_path="templates/S0_system.j2",
            required_variables=[],
        )

        slot = template.to_slot("System content", "L4")

        assert slot.slot_type == "S0"
        assert slot.content == "System content"
        assert slot.authority_level == AuthorityLevel.ABSOLUTE
        assert slot.source_layer == "L4"
        assert slot.metadata["category"] == "SYSTEM_STATE"


class TestPromptCategoryRegistry:
    """Test PromptCategoryRegistry functionality."""

    def test_register_and_get(self):
        """Test registering and retrieving entries."""
        registry = PromptCategoryRegistry()

        template = CategoryTemplate(
            category=PromptCategory.SYSTEM_STATE,
            template_id="S0_system",
            template_path="templates/S0_system.j2",
        )

        entry = CategoryRegistryEntry(
            category=PromptCategory.SYSTEM_STATE,
            template=template,
        )

        registry.register(entry)

        retrieved = registry.get(PromptCategory.SYSTEM_STATE)
        assert retrieved is not None
        assert retrieved.category == PromptCategory.SYSTEM_STATE

    def test_get_by_slot(self):
        """Test getting entries by slot code."""
        registry = PromptCategoryRegistry()

        # Register S0
        s0_template = CategoryTemplate(
            category=PromptCategory.SYSTEM_STATE,
            template_id="S0_system",
            template_path="templates/S0_system.j2",
        )
        registry.register(
            CategoryRegistryEntry(
                category=PromptCategory.SYSTEM_STATE,
                template=s0_template,
            )
        )

        # Register U0
        u0_template = CategoryTemplate(
            category=PromptCategory.USER_PROMPT,
            template_id="U0_user",
            template_path="templates/U0_user.j2",
        )
        registry.register(
            CategoryRegistryEntry(
                category=PromptCategory.USER_PROMPT,
                template=u0_template,
            )
        )

        s0_entries = registry.get_by_slot("S0")
        assert len(s0_entries) == 1

        u0_entries = registry.get_by_slot("U0")
        assert len(u0_entries) == 1

    def test_get_by_authority(self):
        """Test getting entries by authority level."""
        registry = PromptCategoryRegistry()

        template = CategoryTemplate(
            category=PromptCategory.SYSTEM_STATE,
            template_id="S0_system",
            template_path="templates/S0_system.j2",
        )
        registry.register(
            CategoryRegistryEntry(
                category=PromptCategory.SYSTEM_STATE,
                template=template,
            )
        )

        absolute = registry.get_by_authority(AuthorityLevel.ABSOLUTE)
        assert len(absolute) == 1

    def test_is_registered(self):
        """Test registration check."""
        registry = PromptCategoryRegistry()

        assert not registry.is_registered(PromptCategory.SYSTEM_STATE)

        template = CategoryTemplate(
            category=PromptCategory.SYSTEM_STATE,
            template_id="S0_system",
            template_path="templates/S0_system.j2",
        )
        registry.register(
            CategoryRegistryEntry(
                category=PromptCategory.SYSTEM_STATE,
                template=template,
            )
        )

        assert registry.is_registered(PromptCategory.SYSTEM_STATE)


class TestGetDefaultTemplatePath:
    """Test default template path function."""

    def test_paths_for_all_categories(self):
        """Test that all categories have default paths."""
        for category in PromptCategory:
            path = get_default_template_path(category)
            assert path.startswith("templates/")
            assert path.endswith(".j2")
            assert category.slot_code in path
