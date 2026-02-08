"""
Test: Instructional Injection Patterns

Verifies that all worker agents across SSOT-approved folders have access to
the 30 instructional injection patterns from v5.

SOURCE: data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
"""

from pathlib import Path

import pytest


def get_project_root() -> Path:
    """Get project root directory."""
    import os

    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"])

    known_root = Path("C:/Git/Agentic-Workflow")
    if known_root.exists() and (known_root / "agentic_core").is_dir():
        return known_root

    test_file = Path(__file__).resolve()
    return test_file.parent.parent.parent


# SSOT-approved folders containing worker agents
SSOT_AGENT_FOLDERS = [
    "agentic_core/L0_maintenance/scripts",
    "agentic_core/L1_cognition/thought_engine",
    "agentic_core/L2_execution/reasoning",
    "agentic_core/L3_orchestration/reasoning",
    "agentic_core/L3_orchestration/reasoning",
    "agentic_core/L4_state/memory",
    "agentic_core/L5_safety/validators",
    "agentic_core/L5_safety/enforcement",
    "agentic_core/L5_safety/enforcement",
    "agentic_core/L6_observability/reasoning",
    "agentic_core/prompt_governance",
]


class TestInstructionalInjectionMixin:
    """Test suite for instructional_injection_mixin."""

    @pytest.fixture
    def project_root(self) -> Path:
        return get_project_root()

    def test_mixin_can_be_imported(self):
        """Verify instructional_injection_mixin can be imported."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            instructional_injection_mixin,
        )

        assert instructional_injection_mixin is not None

    def test_mixin_has_30_patterns(self):
        """Verify all 30 patterns are defined."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            INSTRUCTIONAL_PATTERNS,
        )

        assert len(INSTRUCTIONAL_PATTERNS) == 30

    def test_patterns_cover_all_layers(self):
        """Verify patterns cover all 6 layers."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            INSTRUCTIONAL_PATTERNS,
            InjectionLayer,
        )

        layers_covered = set()
        for pattern in INSTRUCTIONAL_PATTERNS.values():
            layers_covered.add(pattern.layer)

        assert len(layers_covered) == 6
        for layer in InjectionLayer:
            assert layer in layers_covered, f"Missing layer: {layer}"

    def test_mixin_has_inject_methods(self):
        """Verify mixin has all inject_*_layer methods."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            instructional_injection_mixin,
        )

        required_methods = [
            "inject_framing_layer",
            "inject_context_layer",
            "inject_reasoning_layer",
            "inject_tooling_layer",
            "inject_safety_layer",
            "inject_output_layer",
            "inject_all_layers",
            "get_pattern",
            "get_patterns_by_layer",
            "get_injection_summary",
        ]

        for method in required_methods:
            assert hasattr(instructional_injection_mixin, method), f"Missing method: {method}"

    def test_healer_mixin_inherits_injection(self):
        """Verify HealerMixin inherits instructional_injection_mixin."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            instructional_injection_mixin,
        )
        from agentic_core.mixins.healer_mixin import HealerMixin

        assert issubclass(HealerMixin, instructional_injection_mixin)

    def test_subatomic_testing_mixin_inherits_injection(self):
        """Verify SubatomicTestingMixin inherits instructional_injection_mixin."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            instructional_injection_mixin,
        )
        from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

        assert issubclass(SubatomicTestingMixin, instructional_injection_mixin)

    def test_mcp_hardened_mixin_inherits_injection(self):
        """Verify MCPHardenedMixin inherits instructional_injection_mixin."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            instructional_injection_mixin,
        )
        from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin

        assert issubclass(MCPHardenedMixin, instructional_injection_mixin)

    def test_inject_safety_layer_works(self):
        """Verify inject_safety_layer actually injects patterns."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            instructional_injection_mixin,
        )

        mixin = instructional_injection_mixin()
        original_prompt = "Do something"
        injected = mixin.inject_safety_layer(original_prompt)

        # Should have safety patterns injected
        assert "[INJECTION SHIELD]" in injected
        assert "[CONSTITUTIONAL]" in injected
        assert original_prompt in injected

    def test_inject_output_layer_works(self):
        """Verify inject_output_layer actually injects patterns."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            instructional_injection_mixin,
        )

        mixin = instructional_injection_mixin()
        original_prompt = "Generate output"
        injected = mixin.inject_output_layer(original_prompt, schema='{"type": "object"}')

        # Should have output patterns injected
        assert "[JSON-ONLY]" in injected
        assert "[SCHEMA]" in injected
        assert original_prompt in injected

    def test_get_injection_summary(self):
        """Verify get_injection_summary returns correct structure."""
        from agentic_core.base_agents.instructional_injection_mixin import (
            instructional_injection_mixin,
        )

        mixin = instructional_injection_mixin()
        summary = mixin.get_injection_summary()

        assert "total_patterns" in summary
        assert summary["total_patterns"] == 30
        assert "layers" in summary
        assert len(summary["layers"]) == 6
        assert "enabled_count" in summary


class TestAgentInstructionalInjection:
    """Test that specific agents have instructional injection capabilities."""

    @pytest.fixture
    def project_root(self) -> Path:
        return get_project_root()

    def test_naming_agent_has_injection(self):
        """Verify NamingAgent has instructional injection."""
        from agentic_core.L5_safety.reasoning.NamingAgent import NamingAgent

        assert hasattr(NamingAgent, "inject_safety_layer")
        assert hasattr(NamingAgent, "inject_all_layers")

    def test_location_agent_has_injection(self):
        """Verify LocationAgent has instructional injection."""
        from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent

        assert hasattr(LocationAgent, "inject_safety_layer")
        assert hasattr(LocationAgent, "get_injection_summary")

    def test_hierarchy_agent_has_injection(self):
        """Verify HierarchyAgent has instructional injection."""
        from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent

        assert hasattr(HierarchyAgent, "inject_safety_layer")

    def test_ddd_alignment_agent_has_injection(self):
        """Verify DDDAlignmentAgent has instructional injection."""
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import DDDAlignmentAgent

        assert hasattr(DDDAlignmentAgent, "inject_safety_layer")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
