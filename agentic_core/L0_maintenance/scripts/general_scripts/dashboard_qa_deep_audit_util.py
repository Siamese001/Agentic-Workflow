#!/usr/bin/env python3
"""
DEEP QA AUDIT: Dashboard Data Integrity Validation
Traces every metric from agent_discovery_full.json to dashboard HTML.
Reports ALL data gaps and calculation errors.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent


def load_agent_discovery() -> list[dict]:
    """Load raw agent discovery data."""
    path = PROJECT_ROOT / "agent_discovery_full.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_dashboard_data() -> list[dict]:
    """Extract dashboardData from HTML."""
    html_path = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
    html = html_path.read_text(encoding="utf-8")

    # Extract dashboardData JSON
    lines = []
    in_data = False
    brace_count = 0

    for line in html.split("\n"):
        if "const dashboardData = [" in line:
            in_data = True
            lines.append("[")
            continue
        if in_data:
            lines.append(line)
            brace_count += line.count("{") - line.count("}")
            if "];" in line and brace_count == 0:
                lines[-1] = lines[-1].replace("];", "]")
                break

    return json.loads("".join(lines))


def get_territory_for_agent(agent: dict) -> str:
    """Determine territory for an agent based on its path."""
    path = agent.get("path", "").replace("\\", "/")
    layer = agent.get("layer", "")

    # L6 observability territories
    if "L6_observability" in path or layer == "L6":
        if "/metrics" in path:
            return "L6_Observability/Metrics"
        if "/telemetry" in path or "/agents" in path:
            return "L6_Observability/Telemetry"
        if "/tracing" in path:
            return "L6_Observability/Tracing"
        if "/compliance" in path:
            return "L6_Observability/Compliance"
        return "L6_Observability/Telemetry"  # Default L6

    # L5 Safety territories
    if "L5_safety" in path or layer == "L5":
        if "/guardrails" in path:
            return "L5 Safety/Guardrails"
        if "/validators" in path:
            return "L5 Safety/Validators"
        if "/red_teaming" in path:
            return "L5 Safety/Red Teaming"
        if "/gravity" in path:
            return "L5 Safety/Gravity"
        if "/bases" in path or "Base" in agent.get("class_name", ""):
            return "L5 Safety/Base Class"
        return "L5 Safety/Guardrails"  # Default

    # L4 State territories
    if "L4_state" in path or layer == "L4":
        if "/ValidationContext" in path or "/validation_context" in path:
            return "L4 State/Core"
        if "/ledger" in path:
            return "L4 State/Core"
        if "/memory" in path:
            return "L4 State/Core"
        if "Base" in agent.get("class_name", ""):
            return "L4 State/Base Class"
        if "/infrastructure" in path:
            return "L4 State/Infrastructure"
        return "L4 State/Core"

    # L3 Orchestration territories
    if "L3_orchestration" in path or layer == "L3":
        if "/workflow" in path or "/fission" in path or "/mcp" in path:
            return "L3 Orchestration/Core"
        if "Base" in agent.get("class_name", ""):
            return "L3 Orchestration/Base Class"
        return "L3 Orchestration/Core"

    # L2 Execution territories
    if "L2_execution" in path or layer == "L2":
        if "/tool_registry" in path or "/tool_registry" in path or "/mcp" in path:
            return "L2 Execution/Core"
        if "Base" in agent.get("class_name", ""):
            return "L2 Execution/Base Class"
        return "L2 Execution/Core"

    # L1 Cognition territories
    if "L1_cognition" in path or layer == "L1":
        if "Base" in agent.get("class_name", ""):
            return "L1 Cognition/Base Class"
        return "L1 Cognition/Core"

    # L0 Maintenance territories
    if "L0_maintenance" in path or layer == "L0":
        return "L0 Maintenance/Core"

    # Apps
    if "apps_lic" in path or layer == "apps_lic":
        return "Apps Lic"
    if "apps_rg" in path or layer == "apps_rg":
        return "Apps Rg"
    if "apps_shared" in path or layer == "apps_shared":
        return "Apps Shared"

    return "Unknown"


def calculate_expected_metrics(agents: list[dict], territory: str) -> dict[str, Any]:
    """Calculate expected metrics for a territory from raw agent data.

    Uses ACTUAL field names from agent_discovery_full.json:
    - has_healing (bool)
    - has_tests (bool)
    - observability (dict with logging/metrics/tracing)
    - mcp_hardened (bool)
    - typed_pct (float 0-100)
    - documented_pct (float 0-100)
    """
    # Filter agents for this territory
    territory_agents = [a for a in agents if get_territory_for_agent(a) == territory]

    total = len(territory_agents)
    if total == 0:
        return {
            "Total": 0,
            "Heal Cap %": 0.0,
            "Heal Cap Count": 0,
            "Test %": 0.0,
            "Test Count": 0,
            "Observable %": 0.0,
            "Observable Count": 0,
            "Hardened %": 0.0,
            "Hardened Count": 0,
            "MCP Capable %": 0.0,
            "MCP Capable Count": 0,
            "Typed %": 0.0,
            "Typed Count": 0,
            "Documented %": 0.0,
            "Documented Count": 0,
        }

    # Count each capability using CORRECT field names from agent_discovery_full.json
    heal_count = sum(1 for a in territory_agents if a.get("has_healing", False))
    test_count = sum(1 for a in territory_agents if a.get("has_tests", False))
    observable_count = sum(
        1 for a in territory_agents if a.get("observability")
    )  # dict is truthy if has any keys
    hardened_count = sum(1 for a in territory_agents if a.get("mcp_hardened", False))
    mcp_count = hardened_count  # mcp_hardened is the same metric
    # typed_pct and documented_pct are percentages, not counts - need to average them
    typed_sum = sum(a.get("typed_pct", 0) for a in territory_agents)
    doc_sum = sum(a.get("documented_pct", 0) for a in territory_agents)

    return {
        "Total": total,
        "Heal Cap %": round(heal_count / total * 100, 1),
        "Heal Cap Count": heal_count,
        "Test %": round(test_count / total * 100, 1),
        "Test Count": test_count,
        "Observable %": round(observable_count / total * 100, 1),
        "Observable Count": observable_count,
        "Hardened %": round(hardened_count / total * 100, 1),
        "Hardened Count": hardened_count,
        "MCP Capable %": round(mcp_count / total * 100, 1),
        "MCP Capable Count": mcp_count,
        "Typed %": round(typed_sum / total, 1),  # Average of typed_pct values
        "Typed Count": 0,  # N/A for percentage fields
        "Documented %": round(doc_sum / total, 1),  # Average of documented_pct values
        "Documented Count": 0,  # N/A for percentage fields
    }


def run_deep_audit():
    """Run comprehensive data audit."""
    print("=" * 100)
    print("DASHBOARD DEEP QA AUDIT")
    print("=" * 100)
    print()

    # Load data
    agents = load_agent_discovery()
    dashboard_data = load_dashboard_data()

    print(f"📊 Source Data: {len(agents)} agents in agent_discovery_full.json")
    print(f"📊 Dashboard Data: {len(dashboard_data)} territory rows")
    print()

    # Build dashboard lookup
    dashboard_by_territory = {row["Territory"]: row for row in dashboard_data}

    # Track all issues
    all_issues = []

    print("=" * 100)
    print("TERRITORY-BY-TERRITORY VALIDATION")
    print("=" * 100)

    # Get all unique territories from agents
    all_territories = set()
    for agent in agents:
        all_territories.add(get_territory_for_agent(agent))

    # Also include dashboard territories
    for row in dashboard_data:
        if row["Territory"] != "TOTAL":
            all_territories.add(row["Territory"])

    for territory in sorted(all_territories):
        expected = calculate_expected_metrics(agents, territory)
        actual = dashboard_by_territory.get(territory, {})

        issues = []

        # Check Total
        if actual.get("Total", 0) != expected["Total"]:
            issues.append(
                f"Total: Dashboard={actual.get('Total', 'MISSING')} vs Expected={expected['Total']}",
            )

        # Check percentages match counts
        if expected["Total"] > 0:
            # Heal Cap %
            if abs(actual.get("Heal Cap %", 0) - expected["Heal Cap %"]) > 1:
                issues.append(
                    f"Heal Cap %: Dashboard={actual.get('Heal Cap %', 0)}% but {expected['Heal Cap Count']}/{expected['Total']} = {expected['Heal Cap %']}%",
                )

            # Hardened %
            if abs(actual.get("Hardened %", 0) - expected["Hardened %"]) > 1:
                issues.append(
                    f"Hardened %: Dashboard={actual.get('Hardened %', 0)}% but {expected['Hardened Count']}/{expected['Total']} = {expected['Hardened %']}%",
                )

            # MCP Capable %
            if abs(actual.get("MCP Capable %", 0) - expected["MCP Capable %"]) > 1:
                issues.append(
                    f"MCP Capable %: Dashboard={actual.get('MCP Capable %', 0)}% but {expected['MCP Capable Count']}/{expected['Total']} = {expected['MCP Capable %']}%",
                )

            # Test %
            if abs(actual.get("Test %", 0) - expected["Test %"]) > 1:
                issues.append(
                    f"Test %: Dashboard={actual.get('Test %', 0)}% but {expected['Test Count']}/{expected['Total']} = {expected['Test %']}%",
                )

            # Observable %
            if abs(actual.get("Observable %", 0) - expected["Observable %"]) > 1:
                issues.append(
                    f"Observable %: Dashboard={actual.get('Observable %', 0)}% but {expected['Observable Count']}/{expected['Total']} = {expected['Observable %']}%",
                )

            # Typed %
            if abs(actual.get("Typed %", 0) - expected["Typed %"]) > 1:
                issues.append(
                    f"Typed %: Dashboard={actual.get('Typed %', 0)}% but {expected['Typed Count']}/{expected['Total']} = {expected['Typed %']}%",
                )

            # Documented %
            if abs(actual.get("Documented %", 0) - expected["Documented %"]) > 1:
                issues.append(
                    f"Documented %: Dashboard={actual.get('Documented %', 0)}% but {expected['Documented Count']}/{expected['Total']} = {expected['Documented %']}%",
                )

        # Print territory results
        if issues:
            print(f"\n❌ {territory}")
            print(f"   Agents: {expected['Total']} | Dashboard shows: {actual.get('Total', 'N/A')}")
            for issue in issues:
                print(f"   ⚠️  {issue}")
                all_issues.append((territory, issue))
        else:
            if expected["Total"] > 0:
                print(f"✅ {territory}: {expected['Total']} agents - ALL METRICS VALID")

    # L2 Execution specific deep dive (user's example)
    print("\n" + "=" * 100)
    print("DEEP DIVE: L2 EXECUTION (User's Example)")
    print("=" * 100)

    l2_agents = [a for a in agents if "L2_execution" in a.get("path", "") or a.get("layer") == "L2"]
    print(f"\nL2 Execution agents found: {len(l2_agents)}")

    # Count MCP capable in L2
    l2_mcp_count = sum(1 for a in l2_agents if a.get("has_mcp", False))
    l2_hardened_count = sum(1 for a in l2_agents if a.get("is_hardened", False))

    print("\nMCP Analysis:")
    print(f"  - Total L2 agents: {len(l2_agents)}")
    print(f"  - has_mcp=True: {l2_mcp_count}")
    print(f"  - Expected MCP %: {round(l2_mcp_count / len(l2_agents) * 100, 1) if l2_agents else 0}%")

    print("\nHardened Analysis:")
    print(f"  - is_hardened=True: {l2_hardened_count}")
    print(
        f"  - Expected Hardened %: {round(l2_hardened_count / len(l2_agents) * 100, 1) if l2_agents else 0}%",
    )

    # Show L2 dashboard data
    l2_core = dashboard_by_territory.get("L2 Execution/Core", {})
    print("\nDashboard L2 Execution/Core shows:")
    print(f"  - Total: {l2_core.get('Total', 'N/A')}")
    print(f"  - Hardened %: {l2_core.get('Hardened %', 'N/A')}")
    print(f"  - MCP Capable %: {l2_core.get('MCP Capable %', 'N/A')}")

    # Show sample L2 agents with their flags
    print("\nSample L2 agents (first 10):")
    for agent in l2_agents[:10]:
        print(
            f"  - {agent['class_name']}: has_mcp={agent.get('has_mcp')}, is_hardened={agent.get('is_hardened')}, has_heal={agent.get('has_heal')}",
        )

    # Summary
    print("\n" + "=" * 100)
    print("QA AUDIT SUMMARY")
    print("=" * 100)

    if all_issues:
        print(f"\n❌ FOUND {len(all_issues)} DATA INTEGRITY ISSUES")
        print()

        # Group by territory
        by_territory = defaultdict(list)
        for territory, issue in all_issues:
            by_territory[territory].append(issue)

        for territory, issues in sorted(by_territory.items()):
            print(f"\n{territory}:")
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("\n✅ ALL DATA VALIDATED - No issues found")

    return all_issues


if __name__ == "__main__":
    issues = run_deep_audit()
    print(f"\n\nTotal issues: {len(issues)}")
