"""
L2/L0 BASELINE WEIGHT AUDIT VALIDATION
Ensures no generic utility script exceeds weight 9 per Global Weight Standard.
"""

import pytest

from agentic_core.L5_safety.config.structure_blueprint_config import AST_PLACEMENT_SIGNALS


class TestBaselineWeightAudit:
    """
    Validates that L2/L0 baseline weights don't exceed 9 per Global Weight Standard.
    Generic utilities should be in 5-9 range, never exceeding specialized domains.
    """

    def test_l2_execution_baseline_weights(self):
        """L2 Execution components must not exceed weight 9."""
        l2_paths = [
            "agentic_core/L2_execution/reasoning",
            "agentic_core/L2_execution/action_handlers",
            "agentic_core/L2_execution/enforcement",
        ]

        for path in l2_paths:
            assert path in AST_PLACEMENT_SIGNALS, f"FAIL: Missing L2 path {path}"
            weight = AST_PLACEMENT_SIGNALS[path]["weight"]
            assert weight <= 9, f"VIOLATION: {path} has weight {weight}, exceeds baseline max 9"
            assert weight >= 5, f"VIOLATION: {path} has weight {weight}, below baseline min 5"

    def test_l0_maintenance_baseline_weights(self):
        """L0 Maintenance components must not exceed weight 9."""
        # Check for any L0 maintenance patterns in AST signals
        l0_patterns = [
            path
            for path in AST_PLACEMENT_SIGNALS.keys()
            if "L0_routing" in path or "maintenance" in path.lower()
        ]

        for path in l0_patterns:
            weight = AST_PLACEMENT_SIGNALS[path]["weight"]
            assert weight <= 9, f"VIOLATION: {path} has weight {weight}, exceeds baseline max 9"
            assert weight >= 5, f"VIOLATION: {path} has weight {weight}, below baseline min 5"

    def test_utility_weights_compliance(self):
        """Utility components must not exceed weight 9."""
        utility_paths = [
            "agentic_core/utils/naming",
            "agentic_core/observability/metrics",
            "agentic_core/observability/tracing",
            "agentic_core/observability/compliance",
        ]

        for path in utility_paths:
            if path in AST_PLACEMENT_SIGNALS:
                weight = AST_PLACEMENT_SIGNALS[path]["weight"]
                assert weight <= 9, f"VIOLATION: {path} has weight {weight}, exceeds utility max 9"
                assert weight >= 5, f"VIOLATION: {path} has weight {weight}, below utility min 5"

    def test_no_baseline_exceeds_specialized_domains(self):
        """No baseline component should exceed the minimum specialized domain weight (10)."""
        baseline_weights = []

        # Collect all baseline/utility weights
        for path, signals in AST_PLACEMENT_SIGNALS.items():
            # Skip constitutional, safety, and specialized domain paths
            specialized_prefixes = [
                "agentic_core/base_agents",  # Constitutional (100)
                "agentic_core/L5_safety",  # Critical Safety (20-25)
                "agentic_core/L1_cognition",  # Domain Logic (15-18)
                "agentic_core/L3_orchestration",  # Domain Logic (15-18)
                "agentic_core/L4_state",  # State & Schema (10-14)
                "agentic_core/prompt_governance",  # Domain Logic (15-18)
                "agentic_core/schemas/models",  # State & Schema (10-14)
                "agentic_core/config",  # State & Schema (10-14)
            ]

            is_specialized = any(path.startswith(prefix) for prefix in specialized_prefixes)
            if not is_specialized:
                baseline_weights.append((path, signals["weight"]))

        # Ensure no baseline weight exceeds 9
        violations = [(path, weight) for path, weight in baseline_weights if weight > 9]
        assert not violations, f"BASELINE VIOLATIONS: {violations}"

    def test_global_weight_standard_ranges(self):
        """Validates complete Global Weight Standard ranges across all components."""
        ranges = {
            "constitutional": (100, 100),  # Base agents only
            "critical_safety": (20, 25),  # L5 Safety
            "domain_logic": (15, 18),  # L1, L3, prompt_governance
            "state_schema": (10, 14),  # L4, schemas, config
            "generic_utilities": (5, 9),  # L0, L2, utils, observability
        }

        for path, signals in AST_PLACEMENT_SIGNALS.items():
            weight = signals["weight"]

            if path == "agentic_core/base_agents":
                expected_range = ranges["constitutional"]
            elif path.startswith("agentic_core/L5_safety"):
                expected_range = ranges["critical_safety"]
            elif any(prefix in path for prefix in ["L1_cognition", "L3_orchestration", "prompt_governance"]):
                expected_range = ranges["domain_logic"]
            elif any(prefix in path for prefix in ["L4_state", "schemas/models", "config"]):
                expected_range = ranges["state_schema"]
            else:
                expected_range = ranges["generic_utilities"]

            min_weight, max_weight = expected_range
            assert min_weight <= weight <= max_weight, (
                f"WEIGHT RANGE VIOLATION: {path} has weight {weight}, expected range {min_weight}-{max_weight}"
            )

    def test_weight_hierarchy_strict_ordering(self):
        """Ensures strict weight hierarchy with no overlaps between tiers."""
        tier_weights = {
            "constitutional": [],
            "critical_safety": [],
            "domain_logic": [],
            "state_schema": [],
            "generic_utilities": [],
        }

        # Categorize weights by tier
        for path, signals in AST_PLACEMENT_SIGNALS.items():
            weight = signals["weight"]

            if path == "agentic_core/base_agents":
                tier_weights["constitutional"].append(weight)
            elif path.startswith("agentic_core/L5_safety"):
                tier_weights["critical_safety"].append(weight)
            elif any(prefix in path for prefix in ["L1_cognition", "L3_orchestration", "prompt_governance"]):
                tier_weights["domain_logic"].append(weight)
            elif any(prefix in path for prefix in ["L4_state", "schemas/models", "config"]):
                tier_weights["state_schema"].append(weight)
            else:
                tier_weights["generic_utilities"].append(weight)

        # Verify no overlaps between tiers
        max_utility = max(tier_weights["generic_utilities"]) if tier_weights["generic_utilities"] else 0
        min_state = min(tier_weights["state_schema"]) if tier_weights["state_schema"] else float("inf")
        max_state = max(tier_weights["state_schema"]) if tier_weights["state_schema"] else 0
        min_domain = min(tier_weights["domain_logic"]) if tier_weights["domain_logic"] else float("inf")
        max_domain = max(tier_weights["domain_logic"]) if tier_weights["domain_logic"] else 0
        min_safety = min(tier_weights["critical_safety"]) if tier_weights["critical_safety"] else float("inf")
        max_safety = max(tier_weights["critical_safety"]) if tier_weights["critical_safety"] else 0
        min_constitutional = (
            min(tier_weights["constitutional"]) if tier_weights["constitutional"] else float("inf")
        )

        # Strict ordering: utilities < state < domain < safety < constitutional
        assert max_utility < min_state, (
            f"TIER OVERLAP: Utilities (max {max_utility}) overlap with State (min {min_state})"
        )
        assert max_state < min_domain, (
            f"TIER OVERLAP: State (max {max_state}) overlap with Domain (min {min_domain})"
        )
        assert max_domain < min_safety, (
            f"TIER OVERLAP: Domain (max {max_domain}) overlap with Safety (min {min_safety})"
        )
        assert max_safety < min_constitutional, (
            f"TIER OVERLAP: Safety (max {max_safety}) overlap with Constitutional (min {min_constitutional})"
        )


if __name__ == "__main__":
    # Run the audit directly
    pytest.main([__file__, "-v"])
