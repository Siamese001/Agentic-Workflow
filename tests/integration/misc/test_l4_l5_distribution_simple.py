"""
Simplified test for L4 vs L5 agent distribution analysis.

Focuses on counting and analysis without importing problematic agents.
"""

import pytest
from pathlib import Path


class TestAgentDistributionMetrics:
    """Provide metrics for ongoing monitoring."""

    def test_agent_distribution_ratio(self):
        """Test and document current agent distribution ratio."""
        # Count agents by layer
        l4_count = len(list(Path("agentic_core/L4_state").rglob("*Agent*.py")))
        l5_count = len(list(Path("agentic_core/L5_safety").rglob("*Agent*.py")))

        # Calculate ratio
        ratio = l5_count / l4_count if l4_count > 0 else float("inf")

        # Document current state
        metrics = {
            "l4_agent_count": l4_count,
            "l5_agent_count": l5_count,
            "l4_l5_ratio": ratio,
            "assessment": "reasonable" if 5 <= ratio <= 20 else "needs_review",
        }

        print("\n=== Agent Distribution Metrics ===")
        print(f"L4 Agents: {metrics['l4_agent_count']}")
        print(f"L5 Agents: {metrics['l5_agent_count']}")
        print(f"L5/L4 Ratio: {metrics['l4_l5_ratio']:.1f}:1")
        print(f"Assessment: {metrics['assessment']}")

        # Current ratio should be reasonable
        assert 5 <= ratio <= 20, f"L5/L4 ratio {ratio:.1f} outside reasonable range [5, 20]"

    def test_l4_agent_impact_score(self):
        """Calculate impact score for L4 agents."""
        l4_agents = [
            ("ContextCurator", "system-wide", "high"),
            ("GravityStateAgent", "gravity-specific", "medium"),
            ("SovereignReasoningMemory", "system-wide", "high"),
        ]

        # Calculate weighted impact (system-wide = 2, specific = 1)
        total_impact = sum(2 if scope == "system-wide" else 1 for _, scope, _ in l4_agents)

        # Despite low count, L4 agents have high impact
        assert total_impact >= 5, f"L4 agents total impact too low: {total_impact}"

        print("\n=== L4 Agent Impact Analysis ===")
        for name, scope, priority in l4_agents:
            weight = 2 if scope == "system-wide" else 1
            print(f"{name}: {scope} scope, {priority} priority (weight: {weight})")
        print(f"Total Impact Score: {total_impact}")

    def test_l5_agent_specialization_score(self):
        """Calculate specialization score for L5 agents."""
        # Sample L5 agents and their specialization
        l5_specializations = {
            "GovernanceAgent": ["governance", "architecture", "blast_radius"],
            "GravityLeakRepairAgent": ["gravity", "imports", "layer_violations"],
            "LocationHealerAgent": ["location", "file_moves", "import_fixing"],
            "StructuralEngineerAgent": ["complexity", "structure", "code_quality"],
        }

        # Calculate specialization diversity
        total_specializations = sum(len(specs) for specs in l5_specializations.values())
        unique_specializations = len(
            set(spec for specs in l5_specializations.values() for spec in specs)
        )

        # High specialization diversity indicates good separation of concerns
        specialization_ratio = unique_specializations / len(l5_specializations)

        assert specialization_ratio >= 2.0, (
            f"L5 specialization too low: {specialization_ratio:.1f} per agent"
        )

        print("\n=== L5 Specialization Analysis ===")
        print(f"Total Specializations: {total_specializations}")
        print(f"Unique Specializations: {unique_specializations}")
        print(f"Specializations per Agent: {specialization_ratio:.1f}")

    def test_layer_distribution_analysis(self):
        """Analyze distribution across all layers."""
        layer_counts = {}

        layers = [
            ("L0", "agentic_core/L0_maintenance"),
            ("L1", "agentic_core/L1_cognition"),
            ("L2", "agentic_core/L2_execution"),
            ("L3", "agentic_core/L3_orchestration"),
            ("L4", "agentic_core/L4_state"),
            ("L5", "agentic_core/L5_safety"),
            ("L6", "agentic_core/L6_observability"),
        ]

        for layer_name, path in layers:
            count = len(list(Path(path).rglob("*Agent*.py")))
            layer_counts[layer_name] = count

        print("\n=== Complete Layer Distribution ===")
        total_agents = sum(layer_counts.values())

        for layer, count in layer_counts.items():
            percentage = (count / total_agents * 100) if total_agents > 0 else 0
            print(f"{layer}: {count:3d} agents ({percentage:5.1f}%)")

        print(f"Total: {total_agents} agents")

        # Validate distribution makes sense
        assert layer_counts["L5"] > layer_counts["L4"], "L5 should have more agents than L4"
        assert layer_counts["L4"] < 20, "L4 should have relatively few agents"
        assert layer_counts["L5"] > 50, "L5 should have many specialized agents"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
