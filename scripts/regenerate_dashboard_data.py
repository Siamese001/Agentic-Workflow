#!/usr/bin/env python3
"""
Regenerate Dashboard Data
==========================

Regenerates dashboard_data.js from agent_discovery_full.json
using SSOT calculation functions.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

# SSOT: Import territory ordering
sys.path.insert(0, str(Path(__file__).parent))
from territory_ssot_definitions import get_territory_sort_key

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.dashboard_ssot_definitions import (
    calc_heal_cap_pct, calc_invocation_pct, calc_test_pct, calc_hardened_pct,
    calc_typed_pct, calc_documented_pct, calc_schema_strictness_pct,
    calc_canonical_inheritance_pct, calc_code_quality_score,
    calc_avg_cc, calc_complexity_health, calc_health_score, is_l0_territory
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

# Define canonical sort order (TOTAL, Sovereign Base Agent, L6→L0 with Base Agents first, Apps)
CANONICAL_ORDER = [
    'Sovereign Base Agent',
    'L6_Observability/Base Agent',
    'L6_Observability/Metrics',
    'L6_Observability/Telemetry',
    'L5 Safety/Base Agent',
    'L5 Safety/Validators',
    'L5 Safety/Guardrails',
    'L5 Safety/Red Teaming',
    'L5 Safety/Gravity',
    'L4 State/Base Agent',
    'L4 State/Infrastructure',
    'L4 State/Core',
    'L3 Orchestration/Base Agent',
    'L3 Orchestration/Core',
    'L2 Execution/Base Agent',
    'L2 Execution/Core',
    'L1 Cognition/Base Agent',
    'L1 Cognition/Core',
    'L0 Maintenance/Base Agent',
    'L0 Maintenance/Core',
    'Apps Rg',
    'Apps Lic',
    'Apps Shared',
    'Utils'
]

# Create sort key function
def get_sort_key(territory):
    try:
        return CANONICAL_ORDER.index(territory)
    except ValueError:
        return 999  # Unknown territories go to end

# Add TOTAL row FIRST
total_heal_cap = calc_heal_cap_pct(agents)
total_invocation = calc_invocation_pct(agents)
total_test = calc_test_pct(agents)
total_typed_pct = calc_typed_pct(agents)
total_documented_pct = calc_documented_pct(agents)
total_schema_pct = calc_schema_strictness_pct(agents)
total_canonical_pct = calc_canonical_inheritance_pct(agents)
total_avg_cc = calc_avg_cc(agents)
total_complexity_health = calc_complexity_health(total_avg_cc)

# Calculate overall health score (assume 50% observability as placeholder)
total_health = calc_health_score(
    total_heal_cap, total_invocation, total_test, 
    50.0,  # Observable % placeholder
    total_complexity_health,
    is_l0=False
)

total_row = {
    "Territory": "TOTAL",
    "Total": len(agents),
    "Compliant": sum(1 for a in agents if a.get('has_healing', False)),
    "Heal Cap %": total_heal_cap,
    "Invocation %": total_invocation,
    "Test %": total_test,
    "MCP Hardened %": calc_hardened_pct(agents),
    "Complexity Health %": total_complexity_health,
    "Typed %": total_typed_pct,
    "Documented %": total_documented_pct,
    "Schema Strictness %": total_schema_pct,
    "Canonical Inheritance %": total_canonical_pct,
    "Code Quality Score": calc_code_quality_score(total_typed_pct, total_documented_pct, total_schema_pct, total_canonical_pct),
    "Health": total_health
}

# Build dashboard data rows in canonical order (TOTAL first, then territories)
rows = [total_row]
for territory in sorted(territories.keys(), key=get_territory_sort_key):
    ags = territories[territory]
    
    # Calculate all metrics
    heal_cap = calc_heal_cap_pct(ags)
    invocation = calc_invocation_pct(ags)
    test_pct = calc_test_pct(ags)
    typed_pct = calc_typed_pct(ags)
    documented_pct = calc_documented_pct(ags)
    schema_pct = calc_schema_strictness_pct(ags)
    canonical_pct = calc_canonical_inheritance_pct(ags)
    avg_cc = calc_avg_cc(ags)
    complexity_health = calc_complexity_health(avg_cc)
    
    # Calculate health score using SSOT formula
    is_l0 = is_l0_territory(territory)
    health = calc_health_score(
        heal_cap, invocation, test_pct,
        50.0,  # Observable % placeholder
        complexity_health,
        is_l0=is_l0
    )
    
    row = {
        "Territory": territory,
        "Total": len(ags),
        "Compliant": sum(1 for a in ags if a.get('has_healing', False)),
        "Heal Cap %": heal_cap,
        "Invocation %": invocation,
        "Test %": test_pct,
        "MCP Hardened %": calc_hardened_pct(ags),
        "Complexity Health %": complexity_health,
        "Typed %": typed_pct,
        "Documented %": documented_pct,
        "Schema Strictness %": schema_pct,
        "Canonical Inheritance %": canonical_pct,
        "Code Quality Score": calc_code_quality_score(typed_pct, documented_pct, schema_pct, canonical_pct),
        "Health": health
    }
    rows.append(row)

print(f"\nGenerated {len(rows)} rows (including TOTAL)")
print(f"MCP Hardened %: {total_row['MCP Hardened %']:.1f}%")
print(f"Test Coverage %: {total_row['Test %']:.1f}%")

# Write to dashboard_data.js
dashboard_data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
with open(dashboard_data_file, 'w', encoding='utf-8') as f:
    f.write("// Auto-generated dashboard data\n")
    f.write("// DO NOT EDIT MANUALLY - regenerate with scripts/regenerate_dashboard_data.py\n\n")
    f.write("window.dashboardData = ")
    json.dump(rows, f, indent=2)
    f.write(";\n")

print(f"\n✅ Dashboard data written to {dashboard_data_file}")
print("\nNow restart the dashboard server and clear browser cache to see changes.")
