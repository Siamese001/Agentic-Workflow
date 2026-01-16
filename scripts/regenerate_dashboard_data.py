#!/usr/bin/env python3
"""
Regenerate dashboard data files from agent_discovery_full.json
This updates the data/dashboard_data.js file with current agent metrics.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.dashboard_ssot_definitions import (
    calc_heal_cap_pct, calc_invocation_pct, calc_test_pct, calc_hardened_pct,
    calc_typed_pct, calc_documented_pct, calc_schema_strictness_pct,
    calc_canonical_inheritance_pct, calc_code_quality_score
)

# Load agent discovery
discovery_file = project_root / "agent_discovery_full.json"
with open(discovery_file, 'r', encoding='utf-8') as f:
    agents = json.load(f)

print(f"Loaded {len(agents)} agents from discovery")

# Group by territory
territories = defaultdict(list)
for agent in agents:
    territory = agent.get('territory', 'Unknown')
    territories[territory].append(agent)

# Build dashboard data rows
rows = []
for territory, ags in sorted(territories.items()):
    typed_pct = calc_typed_pct(ags)
    documented_pct = calc_documented_pct(ags)
    schema_pct = calc_schema_strictness_pct(ags)
    canonical_pct = calc_canonical_inheritance_pct(ags)
    
    row = {
        "Territory": territory,
        "Total": len(ags),
        "Compliant": sum(1 for a in ags if a.get('has_healing', False)),
        "Heal Cap %": calc_heal_cap_pct(ags),
        "Invocation %": calc_invocation_pct(ags),
        "Test %": calc_test_pct(ags),
        "MCP Hardened %": calc_hardened_pct(ags),
        "Typed %": typed_pct,
        "Documented %": documented_pct,
        "Schema Strictness %": schema_pct,
        "Canonical Inheritance %": canonical_pct,
        "Code Quality Score": calc_code_quality_score(typed_pct, documented_pct, schema_pct, canonical_pct)
    }
    rows.append(row)

# Add TOTAL row
total_typed_pct = calc_typed_pct(agents)
total_documented_pct = calc_documented_pct(agents)
total_schema_pct = calc_schema_strictness_pct(agents)
total_canonical_pct = calc_canonical_inheritance_pct(agents)

total_row = {
    "Territory": "TOTAL",
    "Total": len(agents),
    "Compliant": sum(1 for a in agents if a.get('has_healing', False)),
    "Heal Cap %": calc_heal_cap_pct(agents),
    "Invocation %": calc_invocation_pct(agents),
    "Test %": calc_test_pct(agents),
    "MCP Hardened %": calc_hardened_pct(agents),
    "Typed %": total_typed_pct,
    "Documented %": total_documented_pct,
    "Schema Strictness %": total_schema_pct,
    "Canonical Inheritance %": total_canonical_pct,
    "Code Quality Score": calc_code_quality_score(total_typed_pct, total_documented_pct, total_schema_pct, total_canonical_pct)
}
rows.append(total_row)

print(f"\nGenerated {len(rows)} rows (including TOTAL)")
print(f"MCP Hardened %: {total_row['MCP Hardened %']:.1f}%")
print(f"Test Coverage %: {total_row['Test %']:.1f}%")

# Write to dashboard_data.js
dashboard_data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
with open(dashboard_data_file, 'w', encoding='utf-8') as f:
    f.write("// Auto-generated dashboard data\n")
    f.write("// DO NOT EDIT MANUALLY - regenerate with scripts/regenerate_dashboard_data.py\n\n")
    f.write("const dashboardData = ")
    json.dump(rows, f, indent=2)
    f.write(";\n")

print(f"\n✅ Dashboard data written to {dashboard_data_file}")
print("\nNow restart the dashboard server and clear browser cache to see changes.")
