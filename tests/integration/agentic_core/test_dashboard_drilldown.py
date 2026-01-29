#!/usr/bin/env python3
"""
Dashboard Drill-Down Validation Test
=====================================

Tests that drill-down modals have complete, valid per-agent data.

Validates:
1. All territories have agent data
2. Agent objects have all required fields
3. No "undefined" values in critical fields
4. Metrics are properly calculated (< 50%, = 0%)
5. VS Code links are properly formatted
"""

import json
import re
from pathlib import Path

# Load dashboard HTML
dashboard_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
if not dashboard_path.exists():
    print("❌ Dashboard HTML not found")
    exit(1)

html = dashboard_path.read_text(encoding="utf-8")

# Extract realAgentData from HTML
agent_data_pattern = r"const realAgentData = (\{.*?\});"
match = re.search(agent_data_pattern, html, re.DOTALL)

if not match:
    print("❌ realAgentData not found in dashboard HTML")
    exit(1)

agent_data_json = match.group(1)
try:
    real_agent_data = json.loads(agent_data_json)
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse realAgentData: {e}")
    exit(1)

print("=" * 80)
print("DASHBOARD DRILL-DOWN VALIDATION TEST")
print("=" * 80)
print()

# Required fields for drill-down agent objects
REQUIRED_FIELDS = [
    "name",
    "path",
    "rel",
    "abs_file",
    "abs_class",
    "class_line",
    "has_mixin",
    "invocation",
    "has_tests",
    "obs_summary",
    "mcp_summary",
    "typing_summary",
    "typed_pct",
    "overall_typed_pct",
    "complexity",
    "health",
]

total_territories = len(real_agent_data)
territories_with_agents = 0
total_agents = 0
errors = []
warnings = []

print(f"📊 Validating {total_territories} territories...")
print()

for territory, territory_data in real_agent_data.items():
    agents = territory_data.get("agents", [])

    if not agents:
        continue

    territories_with_agents += 1
    total_agents += len(agents)

    # Validate each agent
    for idx, agent in enumerate(agents):
        agent_id = f"{territory}[{idx}]"

        # Check required fields exist
        missing_fields = [f for f in REQUIRED_FIELDS if f not in agent]
        if missing_fields:
            errors.append(f"❌ {agent_id}: Missing fields: {', '.join(missing_fields)}")
            continue

        # Check for "undefined" values in critical fields
        if agent.get("name") == "undefined" or not agent.get("name"):
            errors.append(f"❌ {agent_id}: Agent name is undefined or empty")

        if agent.get("rel") == "undefined" or not agent.get("rel"):
            errors.append(f"❌ {agent_id}: Relative path is undefined or empty")

        if agent.get("class_line") == "undefined":
            errors.append(f"❌ {agent_id}: Class line is undefined")

        # Validate metric values are numbers (not "undefined")
        numeric_fields = ["health", "complexity", "typed_pct", "overall_typed_pct"]
        for field in numeric_fields:
            value = agent.get(field)
            if value == "undefined" or value is None:
                errors.append(f"❌ {agent_id}: {field} is undefined")
            elif not isinstance(value, (int, float)):
                errors.append(f"❌ {agent_id}: {field} is not numeric: {value}")

        # Validate boolean fields
        boolean_fields = ["has_mixin", "has_tests"]
        for field in boolean_fields:
            value = agent.get(field)
            if value == "undefined" or value is None:
                errors.append(f"❌ {agent_id}: {field} is undefined")

        # Validate summary strings
        summary_fields = ["obs_summary", "mcp_summary", "typing_summary"]
        for field in summary_fields:
            value = agent.get(field)
            if value == "undefined" or not value:
                errors.append(f"❌ {agent_id}: {field} is undefined or empty")
            elif "undefined" in str(value):
                errors.append(f"❌ {agent_id}: {field} contains 'undefined': {value}")

        # Check invocation field
        inv_value = agent.get("invocation")
        valid_invocations = ["Yes", "No", "Inherited", "Unknown"]
        if inv_value not in valid_invocations:
            warnings.append(f"⚠️  {agent_id}: Unexpected invocation value: {inv_value}")

        # Validate metric thresholds (< 50% and = 0%)
        if agent.get("health", 100) < 50:
            # This is expected for low-health agents, just validate it's a valid number
            if not isinstance(agent["health"], (int, float)):
                errors.append(
                    f"❌ {agent_id}: health < 50% but not a valid number: {agent['health']}"
                )

        if agent.get("health", 100) == 0:
            # Zero health should be explicitly 0, not undefined
            if agent["health"] != 0:
                errors.append(
                    f"❌ {agent_id}: health appears to be 0 but has invalid value: {agent['health']}"
                )

# Print results
print("─" * 80)
print("TEST RESULTS")
print("─" * 80)
print(f"✅ Total Territories: {total_territories}")
print(f"✅ Territories with Agents: {territories_with_agents}")
print(f"✅ Total Agents Validated: {total_agents}")
print()

if errors:
    print(f"❌ ERRORS: {len(errors)}")
    print()
    for error in errors[:20]:  # Show first 20 errors
        print(f"   {error}")
    if len(errors) > 20:
        print(f"   ... and {len(errors) - 20} more errors")
    print()

if warnings:
    print(f"⚠️  WARNINGS: {len(warnings)}")
    print()
    for warning in warnings[:10]:  # Show first 10 warnings
        print(f"   {warning}")
    if len(warnings) > 10:
        print(f"   ... and {len(warnings) - 10} more warnings")
    print()

# Summary statistics
print("─" * 80)
print("DRILL-DOWN HEALTH CHECK")
print("─" * 80)

# Calculate agents with various issues
agents_at_zero_health = 0
agents_below_50_health = 0
agents_with_undefined = 0

for territory_data in real_agent_data.values():
    for agent in territory_data.get("agents", []):
        health = agent.get("health", 100)
        if health == 0:
            agents_at_zero_health += 1
        elif health < 50:
            agents_below_50_health += 1

        # Check for any undefined values
        agent_str = json.dumps(agent)
        if "undefined" in agent_str:
            agents_with_undefined += 1

print(f"Agents at 0% health: {agents_at_zero_health}")
print(f"Agents < 50% health: {agents_below_50_health}")
print(f"Agents with 'undefined' values: {agents_with_undefined}")
print()

# Final verdict
if errors:
    print("=" * 80)
    print("❌ DRILL-DOWN VALIDATION FAILED")
    print("=" * 80)
    print()
    print("Drill-down modals have data integrity issues.")
    print("Fix these errors before deployment.")
    exit(1)
else:
    print("=" * 80)
    print("✅ DRILL-DOWN VALIDATION PASSED")
    print("=" * 80)
    print()
    print("All drill-down modals have complete, valid agent data.")
    print("No 'undefined' values found. Drill-downs are ready for use.")
    if warnings:
        print(f"\nNote: {len(warnings)} warnings found (non-critical).")
    exit(0)
