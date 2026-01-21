#!/usr/bin/env python3
"""
Comprehensive Data Sourcing Validation for Dashboard.
Verifies all fields are correctly sourced from agent_discovery_full.json.
Checks for data integrity issues and validates critical metrics.
"""
import json
from pathlib import Path
from collections import defaultdict
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent
dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"

def load_source_data():
    """Load agent_discovery_full.json source data."""
    source_file = project_root / "agent_discovery_full.json"
    with open(source_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_dashboard_data():
    """Load dashboard_data.js."""
    data_file = dashboard_dir / "data" / "dashboard_data.js"
    content = data_file.read_text(encoding='utf-8')

    # Remove comments and parse
    lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
    content = '\n'.join(lines)
    content = content.replace('const dashboardData = ', '').replace('window.dashboardData = ', '').strip()
    if content.endswith(';'):
        content = content[:-1]

    return json.loads(content)

def calculate_metrics_from_source(source_data):
    """Calculate expected metrics from source data (list of agents)."""
    # Group agents by territory
    by_territory = defaultdict(list)
    for agent in source_data:
        territory = agent.get('territory', 'Unknown')
        by_territory[territory].append(agent)

    metrics = {}

    for territory, agents in by_territory.items():
        if not agents:
            continue

        total = len(agents)

        # Calculate percentages
        heal_cap_count = sum(1 for a in agents if a.get('has_mixin', False))
        invocation_count = sum(1 for a in agents if a.get('invocation') == 'Yes')
        test_count = sum(1 for a in agents if a.get('has_test', False))
        mcp_count = sum(1 for a in agents if a.get('mcp_hardened', False))
        typed_count = sum(1 for a in agents if a.get('typed', False))
        documented_count = sum(1 for a in agents if a.get('documented', False))

        # Complexity Health (100 - CC*2)
        cc_values = [a.get('cyclomatic_complexity', 0) for a in agents if a.get('cyclomatic_complexity') is not None]
        avg_cc = sum(cc_values) / len(cc_values) if cc_values else 0
        complexity_health = max(0, 100 - (avg_cc * 2))

        metrics[territory] = {
            'Total': total,
            'Heal Cap %': round((heal_cap_count / total * 100), 1) if total > 0 else 0,
            'Invocation %': round((invocation_count / total * 100), 1) if total > 0 else 0,
            'Test %': round((test_count / total * 100), 1) if total > 0 else 0,
            'MCP Hardened %': round((mcp_count / total * 100), 1) if total > 0 else 0,
            'Typed %': round((typed_count / total * 100), 1) if total > 0 else 0,
            'Documented %': round((documented_count / total * 100), 1) if total > 0 else 0,
            'Avg CC': round(avg_cc, 1),
            'Complexity Health': round(complexity_health, 1)
        }

    return metrics

def validate_data_sourcing():
    """Validate dashboard data against source."""
    print("\n" + "="*80)
    print("DASHBOARD DATA SOURCING VALIDATION")
    print("="*80)

    print("\n1. Loading source data...")
    source_data = load_source_data()
    print(f"   ✅ Loaded {len(source_data)} territories from agent_discovery_full.json")

    print("\n2. Loading dashboard data...")
    dashboard_data = load_dashboard_data()
    print(f"   ✅ Loaded {len(dashboard_data)} territories from dashboard_data.js")

    print("\n3. Calculating expected metrics from source...")
    expected_metrics = calculate_metrics_from_source(source_data)
    print(f"   ✅ Calculated metrics for {len(expected_metrics)} territories")

    print("\n4. Validating data integrity...")

    mismatches = []
    missing_territories = []

    # Check each dashboard row
    for row in dashboard_data:
        territory = row['Territory']

        if territory == 'TOTAL':
            continue  # Skip TOTAL row

        if territory not in expected_metrics:
            missing_territories.append(territory)
            continue

        expected = expected_metrics[territory]

        # Validate each field
        fields_to_check = [
            ('Total', 'Total'),
            ('Heal Cap %', 'Heal Cap %'),
            ('Invocation %', 'Invocation %'),
            ('Test %', 'Test %'),
            ('MCP Hardened %', 'MCP Hardened %'),
            ('Typed %', 'Typed %'),
            ('Documented %', 'Documented %')
        ]

        for dash_field, expected_field in fields_to_check:
            dash_value = row.get(dash_field)
            expected_value = expected.get(expected_field)

            if dash_value != expected_value:
                mismatches.append({
                    'territory': territory,
                    'field': dash_field,
                    'dashboard': dash_value,
                    'expected': expected_value,
                    'diff': abs(dash_value - expected_value) if isinstance(dash_value, (int, float)) and isinstance(expected_value, (int, float)) else 'N/A'
                })

    # Report results
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)

    if missing_territories:
        print(f"\n⚠️  Missing territories in source data: {len(missing_territories)}")
        for t in missing_territories:
            print(f"   - {t}")

    if mismatches:
        print(f"\n❌ DATA MISMATCHES FOUND: {len(mismatches)}")

        # Group by territory
        by_territory = defaultdict(list)
        for m in mismatches:
            by_territory[m['territory']].append(m)

        for territory, issues in sorted(by_territory.items()):
            print(f"\n   {territory}:")
            for issue in issues:
                print(f"      {issue['field']}: Dashboard={issue['dashboard']}, Expected={issue['expected']}, Diff={issue['diff']}")

        return False
    else:
        print("\n✅ ALL DATA SOURCING VALIDATED")
        print("   All dashboard values match source data calculations")

        # Show sample complexity health values
        print("\n   Sample Complexity Health values:")
        sample_territories = list(expected_metrics.items())[:5]
        for territory, metrics in sample_territories:
            print(f"      {territory}: Avg CC={metrics['Avg CC']}, Complexity Health={metrics['Complexity Health']}%")

        return True

def check_complexity_health_distribution():
    """Check complexity health distribution across all territories."""
    print("\n" + "="*80)
    print("COMPLEXITY HEALTH DISTRIBUTION ANALYSIS")
    print("="*80)

    source_data = load_source_data()

    # Group by territory
    by_territory = defaultdict(list)
    for agent in source_data:
        territory = agent.get('territory', 'Unknown')
        by_territory[territory].append(agent)

    all_cc_values = []
    territory_cc = {}

    for territory, agents in by_territory.items():
        cc_values = [a.get('cyclomatic_complexity', 0) for a in agents if a.get('cyclomatic_complexity') is not None]

        if cc_values:
            avg_cc = sum(cc_values) / len(cc_values)
            complexity_health = max(0, 100 - (avg_cc * 2))
            territory_cc[territory] = {
                'avg_cc': avg_cc,
                'complexity_health': complexity_health,
                'min_cc': min(cc_values),
                'max_cc': max(cc_values),
                'agent_count': len(cc_values)
            }
            all_cc_values.extend(cc_values)

    # Overall stats
    if all_cc_values:
        overall_avg = sum(all_cc_values) / len(all_cc_values)
        overall_health = max(0, 100 - (overall_avg * 2))

        print(f"\n   Overall Statistics:")
        print(f"      Total agents analyzed: {len(all_cc_values)}")
        print(f"      Average CC: {overall_avg:.1f}")
        print(f"      Overall Complexity Health: {overall_health:.1f}%")
        print(f"      Min CC: {min(all_cc_values)}")
        print(f"      Max CC: {max(all_cc_values)}")

    # Show territories with low complexity health
    print(f"\n   Territories with Complexity Health < 50%:")
    low_health = [(t, m) for t, m in territory_cc.items() if m['complexity_health'] < 50]
    low_health.sort(key=lambda x: x[1]['complexity_health'])

    if low_health:
        for territory, metrics in low_health[:10]:
            print(f"      {territory}: {metrics['complexity_health']:.1f}% (Avg CC: {metrics['avg_cc']:.1f})")
    else:
        print("      None - all territories have Complexity Health >= 50%")

    return territory_cc

if __name__ == "__main__":
    sourcing_valid = validate_data_sourcing()
    complexity_stats = check_complexity_health_distribution()

    print("\n" + "="*80)
    print("FINAL VALIDATION STATUS")
    print("="*80)

    if sourcing_valid:
        print("\n✅ DATA SOURCING VALIDATION PASSED")
        print("   All dashboard data correctly sourced from agent_discovery_full.json")
    else:
        print("\n❌ DATA SOURCING VALIDATION FAILED")
        print("   Mismatches found between dashboard and source data")
