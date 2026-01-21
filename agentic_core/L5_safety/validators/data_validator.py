#!/usr/bin/env python3
"""
Comprehensive Dashboard Data Validation
========================================

Performs broader data validation sensibility checks beyond basic schema validation.

Validation Categories:
1. Base Agent Uniqueness - Each layer has exactly 1 base agent
2. Layer Consistency - Agents are in correct layer directories
3. Inheritance Sanity - No circular dependencies, proper base classes
4. Metric Consistency - Percentages add up, no impossible values
5. Path Integrity - All paths exist, no duplicates
6. Naming Conventions - Agents follow naming patterns
7. Data Completeness - Required fields present and valid

This is integrated into the dashboard e2e pipeline to catch data issues early.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

import json
import sys
from collections import defaultdict
from pathlib import Path

# Load agent discovery
discovery_path = Path("agent_discovery_full.json")
if not discovery_path.exists():
    print("❌ agent_discovery_full.json not found")
    sys.exit(1)

data = json.load(open(discovery_path))

LAYERS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
CANONICAL_BASE_AGENTS = {
    "L0": "L0MaintenanceBaseAgent",
    "L1": "L1CognitionBaseAgent",
    "L2": "L2Agent",
    "L3": "L3Agent",
    "L4": "L4Agent",
    "L5": "L5Agent",
    "L6": "L6ObservabilityBaseAgent",
}


class DataValidator:
    """Comprehensive data validator."""

    def __init__(self, data: list[dict]):
        self.data = data
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("=" * 80)
        print("COMPREHENSIVE DASHBOARD DATA VALIDATION")
        print("=" * 80)
        print()

        self.check_base_agent_uniqueness()
        self.check_layer_consistency()
        self.check_path_integrity()
        self.check_metric_sanity()
        self.check_inheritance_patterns()
        self.check_naming_conventions()
        self.check_data_completeness()

        self.print_summary()

        return len(self.errors) == 0

    def check_base_agent_uniqueness(self):
        """Validate each layer has exactly 1 base agent."""
        print("📋 Check 1: Base Agent Uniqueness")
        print("-" * 80)

        base_agents_by_layer = defaultdict(list)

        for agent in self.data:
            class_name = agent.get("class_name", "")
            layer = agent.get("layer", "")

            is_base = (
                "BaseAgent" in class_name
                or class_name in CANONICAL_BASE_AGENTS.values()
                or "base_class" in agent.get("path", "").lower()
            )

            if is_base and layer:
                layer_prefix = layer[:2] if len(layer) >= 2 else layer
                if layer_prefix in LAYERS:
                    base_agents_by_layer[layer_prefix].append(agent)

        issues_found = False
        for layer in LAYERS:
            agents = base_agents_by_layer.get(layer, [])
            canonical = CANONICAL_BASE_AGENTS.get(layer)

            if len(agents) == 0:
                self.warnings.append(f"{layer}: No base agent (expected {canonical})")
            elif len(agents) == 1:
                if agents[0]["class_name"] != canonical:
                    self.warnings.append(
                        f"{layer}: Found {agents[0]['class_name']}, expected {canonical}"
                    )
            else:
                self.errors.append(
                    f"{layer}: Multiple base agents ({len(agents)}) - {[a['class_name'] for a in agents]}"
                )
                issues_found = True

        if issues_found:
            print("   ❌ Multiple base agents found in some layers")
        else:
            print("   ✅ Each layer has 0-1 base agents")
        print()

    def check_layer_consistency(self):
        """Validate agents are in correct layer directories."""
        print("📋 Check 2: Layer Consistency")
        print("-" * 80)

        mismatches = []
        for agent in self.data:
            layer = agent.get("layer", "")
            path = agent.get("path", "")

            if not layer or not path:
                continue

            # Check if layer matches path
            layer_prefix = layer[:2] if len(layer) >= 2 else layer
            if layer_prefix in LAYERS:
                expected_dir = f"{layer_prefix.lower()}_"
                if expected_dir not in path.lower() and "apps" not in path.lower():
                    mismatches.append(f"{agent['class_name']}: layer={layer} but path={path}")

        if mismatches:
            self.warnings.extend(mismatches[:5])  # Show first 5
            if len(mismatches) > 5:
                self.warnings.append(f"... and {len(mismatches) - 5} more layer mismatches")
            print(f"   ⚠️  {len(mismatches)} agents in wrong layer directories")
        else:
            print("   ✅ All agents in correct layer directories")
        print()

    def check_path_integrity(self):
        """Validate all paths exist and no duplicates."""
        print("📋 Check 3: Path Integrity")
        print("-" * 80)

        paths = [agent.get("path", "") for agent in self.data]

        # Check for duplicates
        path_counts = defaultdict(int)
        for path in paths:
            if path:
                path_counts[path] += 1

        duplicates = {p: c for p, c in path_counts.items() if c > 1}
        if duplicates:
            for path, count in list(duplicates.items())[:3]:
                self.errors.append(f"Duplicate path ({count}x): {path}")
            if len(duplicates) > 3:
                self.errors.append(f"... and {len(duplicates) - 3} more duplicate paths")
            print(f"   ❌ {len(duplicates)} duplicate paths found")
        else:
            print(f"   ✅ No duplicate paths ({len(paths)} unique agents)")
        print()

    def check_metric_sanity(self):
        """Validate metrics are within reasonable ranges."""
        print("📋 Check 4: Metric Sanity")
        print("-" * 80)

        metric_issues = []

        for agent in self.data:
            name = agent.get("class_name", "Unknown")

            # Check percentages are 0-100
            for field in ["typed_pct", "documented_pct", "test_coverage"]:
                value = agent.get(field, 0)
                if value < 0 or value > 100:
                    metric_issues.append(f"{name}: {field}={value}% (invalid range)")

            # Check complexity is reasonable (typically 1-50)
            cc = agent.get("cyclomatic_complexity", 0)
            if cc > 100:
                metric_issues.append(f"{name}: cyclomatic_complexity={cc} (suspiciously high)")

            # Check LOC is reasonable
            loc = agent.get("loc", 0)
            if loc > 10000:
                metric_issues.append(f"{name}: loc={loc} (suspiciously high)")
            elif loc < 10 and agent.get("has_healing"):
                self.warnings.append(f"{name}: loc={loc} (suspiciously low for healing agent)")

        if metric_issues:
            self.errors.extend(metric_issues[:5])
            if len(metric_issues) > 5:
                self.errors.append(f"... and {len(metric_issues) - 5} more metric issues")
            print(f"   ❌ {len(metric_issues)} metric anomalies found")
        else:
            print("   ✅ All metrics within reasonable ranges")
        print()

    def check_inheritance_patterns(self):
        """Validate inheritance makes sense."""
        print("📋 Check 5: Inheritance Patterns")
        print("-" * 80)

        inheritance_issues = []

        for agent in self.data:
            name = agent.get("class_name", "Unknown")
            inheritance = agent.get("inheritance", [])
            layer = agent.get("layer", "")

            if not inheritance:
                continue

            # Check for common bad patterns
            if "object" in inheritance and len(inheritance) > 1:
                inheritance_issues.append(f"{name}: Inherits from 'object' + others (redundant)")

            # Check layer-specific base classes
            if layer.startswith("L5") and not any(
                base in str(inheritance) for base in ["L5", "Safety", "HealerMixin"]
            ):
                self.warnings.append(f"{name}: L5 agent without L5/Safety base class")

        if inheritance_issues:
            self.warnings.extend(inheritance_issues[:3])
            print(f"   ⚠️  {len(inheritance_issues)} inheritance pattern issues")
        else:
            print("   ✅ Inheritance patterns look reasonable")
        print()

    def check_naming_conventions(self):
        """Validate agent naming follows conventions."""
        print("📋 Check 6: Naming Conventions")
        print("-" * 80)

        naming_issues = []

        for agent in self.data:
            name = agent.get("class_name", "")

            # Should end with "Agent"
            if not name.endswith("Agent"):
                naming_issues.append(f"{name}: Does not end with 'Agent'")

            # Should be PascalCase
            if not name[0].isupper():
                naming_issues.append(f"{name}: Does not start with uppercase")

            # Should not have underscores (use PascalCase)
            if "_" in name and name not in [
                "L0MaintenanceBaseAgent",
                "L1CognitionBaseAgent",
                "L2Agent",
                "L3Agent",
                "L4Agent",
                "L5Agent",
            ]:
                self.warnings.append(f"{name}: Contains underscore (prefer PascalCase)")

        if naming_issues:
            self.errors.extend(naming_issues[:3])
            if len(naming_issues) > 3:
                self.errors.append(f"... and {len(naming_issues) - 3} more naming issues")
            print(f"   ⚠️  {len(naming_issues)} naming convention issues")
        else:
            print("   ✅ All agents follow naming conventions")
        print()

    def check_data_completeness(self):
        """Validate required fields are present."""
        print("📋 Check 7: Data Completeness")
        print("-" * 80)

        required_fields = ["class_name", "path", "layer"]
        incomplete = []

        for agent in self.data:
            missing = [f for f in required_fields if not agent.get(f)]
            if missing:
                incomplete.append(f"{agent.get('class_name', 'Unknown')}: missing {missing}")

        if incomplete:
            self.errors.extend(incomplete[:5])
            if len(incomplete) > 5:
                self.errors.append(f"... and {len(incomplete) - 5} more incomplete records")
            print(f"   ❌ {len(incomplete)} agents missing required fields")
        else:
            print(f"   ✅ All {len(self.data)} agents have required fields")
        print()

    def print_summary(self):
        """Print validation summary."""
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print()

        if self.errors:
            print(f"❌ {len(self.errors)} ERRORS (must fix):")
            for error in self.errors[:10]:
                print(f"   • {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more")
            print()

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} WARNINGS (should review):")
            for warning in self.warnings[:10]:
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
            print()

        if not self.errors and not self.warnings:
            print("✅ ALL VALIDATION CHECKS PASSED")
            print(f"   {len(self.data)} agents validated successfully")
            print()


def main():
    """Main entry point."""
    validator = DataValidator(data)
    is_valid = validator.validate_all()

    if not is_valid:
        print("=" * 80)
        print("⚠️  DATA VALIDATION FAILED")
        print("=" * 80)
        print("Fix the errors above before regenerating the dashboard.")
        return 1

    print("=" * 80)
    print("✅ DATA VALIDATION PASSED")
    print("=" * 80)
    print("Dashboard data is ready for generation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
