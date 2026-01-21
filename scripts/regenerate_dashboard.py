#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidated Dashboard Regeneration Script
==========================================

Single entry point for all dashboard regeneration tasks.

Usage:
    python scripts/regenerate_dashboard.py --full        # Full regeneration (HTML + data)
    python scripts/regenerate_dashboard.py --data-only   # Regenerate data files only

This script consolidates:
- regenerate_dashboard_full.py (--full)
- regenerate_dashboard_data.py (--data-only)
"""
import argparse
import sys
import os
from pathlib import Path

# Windows UTF-8 support
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Setup project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def regenerate_full():
    """Run full dashboard regeneration (HTML + data)."""
    print("=" * 70)
    print("FULL Dashboard Regeneration")
    print("=" * 70)

    # Import and run the full regeneration script
    script_path = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "regenerate_dashboard_full.py"

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return 1

    # Execute the script
    import subprocess
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=False
    )

    return result.returncode


def regenerate_data_only():
    """Regenerate dashboard data files only (no HTML update)."""
    import json
    from collections import defaultdict

    print("=" * 70)
    print("Dashboard Data-Only Regeneration")
    print("=" * 70)

    # Import SSOT definitions
    from agentic_core.L5_safety.validators.dashboard_ssot_definitions import (
        calc_heal_cap_pct, calc_invocation_pct, calc_test_pct, calc_hardened_pct,
        calc_typed_pct, calc_documented_pct, calc_schema_strictness_pct,
        calc_canonical_inheritance_pct,
        calc_avg_cc, calc_complexity_health, is_l0_territory,
        get_canonical_health_score, get_canonical_code_quality_score,
        COL_TERRITORY, COL_TOTAL, COL_COMPLIANT, COL_HEAL_CAP, COL_INVOCATION,
        COL_TEST, COL_HARDENED, COL_COMPLEXITY_HEALTH, COL_TYPED, COL_DOCUMENTED,
        COL_SCHEMA_STRICTNESS, COL_CANONICAL_INHERITANCE, COL_CODE_QUALITY, COL_HEALTH,
        FIELD_TERRITORY, FIELD_HAS_HEALING, FIELD_INVOCATION, FIELD_HAS_TESTS,
        FIELD_MCP_HARDENED, FIELD_TYPED_PCT, FIELD_DOCUMENTED_PCT,
        FIELD_SCHEMA_STRICTNESS, FIELD_PROPER_BASE_CLASS, FIELD_CYCLOMATIC_COMPLEXITY
    )

    from agentic_core.L0_maintenance.scripts.territory_ssot_definitions import get_territory_sort_key

    # Load agent discovery
    discovery_file = PROJECT_ROOT / "agent_discovery_full.json"
    if not discovery_file.exists():
        print(f"❌ Discovery file not found: {discovery_file}")
        print("   Run: python scripts/full_agent_discovery.py")
        return 1

    with open(discovery_file, 'r', encoding='utf-8') as f:
        agents = json.load(f)

    print(f"Loaded {len(agents)} agents from discovery")

    # Group by territory
    territories = defaultdict(list)
    for agent in agents:
        territory = agent.get(FIELD_TERRITORY, 'Unknown')
        territories[territory].append(agent)

    # Build TOTAL row
    total_heal_cap = calc_heal_cap_pct(agents)
    total_invocation = calc_invocation_pct(agents)
    total_test = calc_test_pct(agents)
    total_typed_pct = calc_typed_pct(agents)
    total_documented_pct = calc_documented_pct(agents)
    total_schema_pct = calc_schema_strictness_pct(agents)
    total_canonical_pct = calc_canonical_inheritance_pct(agents)
    total_avg_cc = calc_avg_cc(agents)
    total_complexity_health = calc_complexity_health(total_avg_cc)
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

    total_health = get_canonical_health_score(total_metrics, is_l0=False)
    total_code_quality = get_canonical_code_quality_score(total_metrics)

    total_row = {
        COL_TERRITORY: "TOTAL",
        COL_TOTAL: len(agents),
        COL_COMPLIANT: sum(1 for a in agents if a.get(FIELD_HAS_HEALING, False)),
        COL_HEAL_CAP: total_heal_cap,
        COL_INVOCATION: total_invocation,
        COL_TEST: total_test,
        COL_HARDENED: total_hardened,
        COL_COMPLEXITY_HEALTH: total_complexity_health,
        COL_TYPED: total_typed_pct,
        COL_DOCUMENTED: total_documented_pct,
        COL_SCHEMA_STRICTNESS: total_schema_pct,
        COL_CANONICAL_INHERITANCE: total_canonical_pct,
        COL_CODE_QUALITY: total_code_quality,
        COL_HEALTH: total_health
    }

    # Build territory rows
    rows = [total_row]
    for territory in sorted(territories.keys(), key=get_territory_sort_key):
        ags = territories[territory]

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
            COL_HARDENED: hardened_pct,
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
    dashboard_data_file = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
    with open(dashboard_data_file, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated dashboard data\n")
        f.write("// DO NOT EDIT MANUALLY - regenerate with scripts/regenerate_dashboard.py --data-only\n\n")
        f.write("window.dashboardData = ")
        json.dump(rows, f, indent=2)
        f.write(";\n")

    print(f"\n✅ Dashboard data written to {dashboard_data_file}")
    print("\nRestart the dashboard server and clear browser cache to see changes.")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Consolidated Dashboard Regeneration Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/regenerate_dashboard.py --full        # Full regeneration (HTML + data)
  python scripts/regenerate_dashboard.py --data-only   # Regenerate data files only
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--full', action='store_true', help='Full regeneration (HTML + data)')
    group.add_argument('--data-only', action='store_true', help='Regenerate data files only')

    args = parser.parse_args()

    if args.full:
        return regenerate_full()
    elif args.data_only:
        return regenerate_data_only()


if __name__ == "__main__":
    sys.exit(main())
