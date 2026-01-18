#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
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
    calc_canonical_inheritance_pct,
    calc_avg_cc, calc_complexity_health, is_l0_territory,
    # PHASE 3: New canonical calculation functions
    get_canonical_health_score, get_canonical_code_quality_score,
    # SSOT CONSTANTS
    COL_TERRITORY, COL_TOTAL, COL_COMPLIANT, COL_HEAL_CAP, COL_INVOCATION,
    COL_TEST, COL_HARDENED, COL_COMPLEXITY_HEALTH, COL_TYPED, COL_DOCUMENTED,
    COL_SCHEMA_STRICTNESS, COL_CANONICAL_INHERITANCE, COL_CODE_QUALITY, COL_HEALTH,
    # SSOT FIELD CONSTANTS
    FIELD_TERRITORY, FIELD_HAS_HEALING, FIELD_INVOCATION, FIELD_HAS_TESTS,
    FIELD_MCP_HARDENED, FIELD_TYPED_PCT, FIELD_DOCUMENTED_PCT,
    FIELD_SCHEMA_STRICTNESS, FIELD_PROPER_BASE_CLASS, FIELD_CYCLOMATIC_COMPLEXITY
)
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

# Load agent discovery
discovery_file = project_root / "agent_discovery_full.json"
with open(discovery_file, 'r', encoding='utf-8') as f:
    agents = json.load(f)

print(f"Loaded {len(agents)} agents from discovery")

# Group by territory
territories = defaultdict(list)
for agent in agents:
    territory = agent.get(FIELD_TERRITORY, 'Unknown')  # SSOT: Use field constant
    territories[territory].append(agent)

# REMOVED: Redundant CANONICAL_ORDER and get_sort_key
# Now using SSOT get_territory_sort_key from territory_ssot_definitions.py

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

# PHASE 3: Build metrics dictionary for canonical calculation
total_hardened = calc_hardened_pct(agents)
total_metrics = {
    FIELD_HAS_HEALING: total_heal_cap,
    FIELD_INVOCATION: total_invocation,
    FIELD_HAS_TESTS: total_test,
    FIELD_MCP_HARDENED: total_hardened,
    FIELD_CYCLOMATIC_COMPLEXITY: total_complexity_health,
    FIELD_TYPED_PCT: total_typed_pct,
    FIELD_DOCUMENTED_PCT: total_documented_pct,
    FIELD_SCHEMA_STRICTNESS: total_schema_pct,
    FIELD_PROPER_BASE_CLASS: total_canonical_pct
}

# PHASE 3: Use canonical calculation functions (driven by YAML weights)
total_health = get_canonical_health_score(total_metrics, is_l0=False)
total_code_quality = get_canonical_code_quality_score(total_metrics)

total_row = {
    COL_TERRITORY: "TOTAL",
    COL_TOTAL: len(agents),
    COL_COMPLIANT: sum(1 for a in agents if a.get(FIELD_HAS_HEALING, False)),
    COL_HEAL_CAP: total_heal_cap,
    COL_INVOCATION: total_invocation,
    COL_TEST: total_test,
    COL_HARDENED: calc_hardened_pct(agents),
    COL_COMPLEXITY_HEALTH: total_complexity_health,
    COL_TYPED: total_typed_pct,
    COL_DOCUMENTED: total_documented_pct,
    COL_SCHEMA_STRICTNESS: total_schema_pct,
    COL_CANONICAL_INHERITANCE: total_canonical_pct,
    COL_CODE_QUALITY: total_code_quality,
    COL_HEALTH: total_health
}

# Build dashboard data rows in canonical order (TOTAL first, then territories)
rows = [total_row]
for territory in sorted(territories.keys(), key=get_territory_sort_key):
    ags = territories[territory]
    
    # Calculate all metrics
    heal_cap = calc_heal_cap_pct(ags)
    invocation = calc_invocation_pct(ags)
    test_pct = calc_test_pct(ags)
    hardened_pct = calc_hardened_pct(ags)
    typed_pct = calc_typed_pct(ags)
    documented_pct = calc_documented_pct(ags)
    schema_pct = calc_schema_strictness_pct(ags)
    canonical_pct = calc_canonical_inheritance_pct(ags)
    avg_cc = calc_avg_cc(ags)
    complexity_health = calc_complexity_health(avg_cc)
    
    # PHASE 3: Build metrics dictionary for canonical calculation
    territory_metrics = {
        FIELD_HAS_HEALING: heal_cap,
        FIELD_INVOCATION: invocation,
        FIELD_HAS_TESTS: test_pct,
        FIELD_MCP_HARDENED: hardened_pct,
        FIELD_CYCLOMATIC_COMPLEXITY: complexity_health,
        FIELD_TYPED_PCT: typed_pct,
        FIELD_DOCUMENTED_PCT: documented_pct,
        FIELD_SCHEMA_STRICTNESS: schema_pct,
        FIELD_PROPER_BASE_CLASS: canonical_pct
    }
    
    # PHASE 3: Use canonical calculation functions (driven by YAML weights)
    is_l0 = is_l0_territory(territory)
    health = get_canonical_health_score(territory_metrics, is_l0=is_l0)
    code_quality = get_canonical_code_quality_score(territory_metrics)
    
    row = {
        COL_TERRITORY: territory,
        COL_TOTAL: len(ags),
        COL_COMPLIANT: sum(1 for a in ags if a.get(FIELD_HAS_HEALING, False)),
        COL_HEAL_CAP: heal_cap,
        COL_INVOCATION: invocation,
        COL_TEST: test_pct,
        COL_HARDENED: calc_hardened_pct(ags),
        COL_COMPLEXITY_HEALTH: complexity_health,
        COL_TYPED: typed_pct,
        COL_DOCUMENTED: documented_pct,
        COL_SCHEMA_STRICTNESS: schema_pct,
        COL_CANONICAL_INHERITANCE: canonical_pct,
        COL_CODE_QUALITY: code_quality,
        COL_HEALTH: health
    }
    rows.append(row)

print(f"\nGenerated {len(rows)} rows (including TOTAL)")
print(f"MCP Hardened %: {total_row[COL_HARDENED]:.1f}%")
print(f"Test Coverage %: {total_row[COL_TEST]:.1f}%")

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
