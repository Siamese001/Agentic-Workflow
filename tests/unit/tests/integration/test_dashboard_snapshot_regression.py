"""
Dashboard Snapshot Regression Test
Compares t-1 (previous) vs t (current) agent discovery state and identifies variances.

This test ensures quality control for dashboard changes by:
1. Comparing agent counts across territories
2. Verifying base class uniqueness (1 per layer)
3. Detecting unexpected agent additions/removals
4. Rationalizing all variances
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_discovery(path: str) -> list[dict]:
    """Load agent discovery JSON."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_base_class_summary(agents: list[dict]) -> dict[str, list[str]]:
    """Extract base class agents grouped by layer."""
    base_classes = defaultdict(list)
    for agent in agents:
        if "Base Class" in agent.get("territory", ""):
            layer = agent.get("layer", "Unknown")
            base_classes[layer].append(agent["class_name"])
    return dict(base_classes)


def get_territory_counts(agents: list[dict]) -> dict[str, int]:
    """Get agent counts per territory."""
    counts = defaultdict(int)
    for agent in agents:
        territory = agent.get("territory", "Unknown")
        counts[territory] += 1
    return dict(counts)


def get_agent_list(agents: list[dict]) -> set:
    """Get set of agent class names."""
    return {a["class_name"] for a in agents}


def compare_snapshots(t_minus_1: list[dict], t: list[dict]) -> dict[str, Any]:
    """
    Compare two discovery snapshots and identify variances.

    Returns:
        Dictionary with comparison results and variance analysis
    """
    results = {
        "total_agents": {"t-1": len(t_minus_1), "t": len(t), "delta": len(t) - len(t_minus_1)},
        "base_classes": {},
        "territories": {},
        "agents_added": [],
        "agents_removed": [],
        "territory_changes": [],
        "issues": [],
    }

    # Compare base classes
    base_t1 = get_base_class_summary(t_minus_1)
    base_t = get_base_class_summary(t)

    all_layers = sorted(set(base_t1.keys()) | set(base_t.keys()))
    for layer in all_layers:
        agents_t1 = base_t1.get(layer, [])
        agents_t = base_t.get(layer, [])

        results["base_classes"][layer] = {
            "t-1": agents_t1,
            "t": agents_t,
            "t-1_count": len(agents_t1),
            "t_count": len(agents_t),
            "delta": len(agents_t) - len(agents_t1),
        }

        # Check for issues
        if len(agents_t) > 1:
            results["issues"].append(
                f"CRITICAL: {layer} has {len(agents_t)} base classes (expected 1): {agents_t}"
            )
        elif len(agents_t) == 0:
            results["issues"].append(f"WARNING: {layer} has no base class")

    # Compare territories
    terr_t1 = get_territory_counts(t_minus_1)
    terr_t = get_territory_counts(t)

    all_territories = sorted(set(terr_t1.keys()) | set(terr_t.keys()))
    for territory in all_territories:
        count_t1 = terr_t1.get(territory, 0)
        count_t = terr_t.get(territory, 0)
        delta = count_t - count_t1

        if delta != 0:
            results["territory_changes"].append(
                {"territory": territory, "t-1": count_t1, "t": count_t, "delta": delta}
            )

    # Compare agent lists
    agents_t1 = get_agent_list(t_minus_1)
    agents_t = get_agent_list(t)

    results["agents_added"] = sorted(agents_t - agents_t1)
    results["agents_removed"] = sorted(agents_t1 - agents_t)

    return results


def rationalize_variances(results: dict[str, Any]) -> list[str]:
    """
    Rationalize all variances between snapshots.

    Returns:
        List of rationalization statements
    """
    rationale = []

    # Total count change
    delta = results["total_agents"]["delta"]
    if delta > 0:
        rationale.append(f"✅ Added {delta} agents (new functionality or discovered agents)")
    elif delta < 0:
        rationale.append(f"⚠️  Removed {abs(delta)} agents (refactoring or exclusion)")
    else:
        rationale.append("✅ Total agent count unchanged")

    # Base class changes
    base_issues = [issue for issue in results["issues"] if "base class" in issue.lower()]
    if base_issues:
        rationale.append(f"❌ Base class violations detected: {len(base_issues)}")
        for issue in base_issues:
            rationale.append(f"   - {issue}")
    else:
        rationale.append("✅ All layers have exactly 1 base class")

    # Agent additions
    if results["agents_added"]:
        rationale.append(f"📥 Agents added ({len(results['agents_added'])}):")
        for agent in results["agents_added"][:5]:  # Show first 5
            rationale.append(f"   + {agent}")
        if len(results["agents_added"]) > 5:
            rationale.append(f"   ... and {len(results['agents_added']) - 5} more")

    # Agent removals
    if results["agents_removed"]:
        rationale.append(f"📤 Agents removed ({len(results['agents_removed'])}):")
        for agent in results["agents_removed"][:5]:  # Show first 5
            rationale.append(f"   - {agent}")
        if len(results["agents_removed"]) > 5:
            rationale.append(f"   ... and {len(results['agents_removed']) - 5} more")

    # Territory changes
    if results["territory_changes"]:
        rationale.append(f"🔄 Territory changes ({len(results['territory_changes'])}):")
        for change in results["territory_changes"][:10]:  # Show first 10
            territory = change["territory"]
            delta = change["delta"]
            sign = "+" if delta > 0 else ""
            rationale.append(f"   {territory}: {change['t-1']} → {change['t']} ({sign}{delta})")

    return rationale


def print_comparison_report(results: dict[str, Any], rationale: list[str]):
    """Print formatted comparison report."""
    print("\n" + "=" * 80)
    print("DASHBOARD SNAPSHOT REGRESSION TEST")
    print("=" * 80)

    # Summary
    print("\n📊 SUMMARY")
    print("-" * 80)
    print(f"Total Agents (t-1): {results['total_agents']['t-1']}")
    print(f"Total Agents (t):   {results['total_agents']['t']}")
    print(f"Delta:              {results['total_agents']['delta']:+d}")

    # Base classes
    print("\n🏛️  BASE CLASS ANALYSIS")
    print("-" * 80)
    for layer in sorted(results["base_classes"].keys()):
        info = results["base_classes"][layer]
        status = "✅" if info["t_count"] == 1 else "❌"
        print(f"{status} {layer:6s}: {info['t-1_count']} → {info['t_count']} | t: {info['t']}")

    # Issues
    if results["issues"]:
        print("\n⚠️  ISSUES DETECTED")
        print("-" * 80)
        for issue in results["issues"]:
            print(f"  {issue}")

    # Rationale
    print("\n📝 VARIANCE RATIONALIZATION")
    print("-" * 80)
    for line in rationale:
        print(line)

    # Pass/Fail
    print("\n" + "=" * 80)
    if results["issues"]:
        print("❌ REGRESSION TEST FAILED")
        print(f"   {len(results['issues'])} critical issues detected")
        return False
    else:
        print("✅ REGRESSION TEST PASSED")
        print("   All variances rationalized and acceptable")
        return True


def main():
    """Run snapshot regression test."""
    project_root = Path(__file__).parent.parent

    # Load snapshots
    snapshot_t1 = project_root / "agent_discovery_snapshot_t-1.json"
    current_t = project_root / "agent_discovery_full.json"

    if not snapshot_t1.exists():
        print(f"❌ ERROR: Snapshot file not found: {snapshot_t1}")
        print(
            "   Run: git show HEAD~5:agent_discovery_full.json > agent_discovery_snapshot_t-1.json"
        )
        return False

    if not current_t.exists():
        print(f"❌ ERROR: Current discovery not found: {current_t}")
        return False

    print("Loading snapshots...")
    t_minus_1 = load_discovery(snapshot_t1)
    t = load_discovery(current_t)

    # Compare
    print("Comparing t-1 vs t...")
    results = compare_snapshots(t_minus_1, t)

    # Rationalize
    print("Rationalizing variances...")
    rationale = rationalize_variances(results)

    # Report
    passed = print_comparison_report(results, rationale)

    return passed


if __name__ == "__main__":
    passed = main()
    sys.exit(0 if passed else 1)
