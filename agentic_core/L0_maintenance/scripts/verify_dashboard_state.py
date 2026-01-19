#!/usr/bin/env python3
"""Verify dashboard file state and Plotly loading."""
from pathlib import Path
import re

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

print("=" * 80)
print("DASHBOARD STATE VERIFICATION")
print("=" * 80)

# Check files exist
reports_dir = Path(REPORTS_DIR)
dashboard_path = reports_dir / "autonomy_dashboard.html"
plotly_path = reports_dir / "plotly.min.js"

print(f"\n1. File Existence:")
print(f"   Dashboard: {dashboard_path.exists()} ({dashboard_path.stat().st_size / 1024:.1f}KB)" if dashboard_path.exists() else f"   Dashboard: MISSING")
print(f"   Plotly:    {plotly_path.exists()} ({plotly_path.stat().st_size / 1024 / 1024:.1f}MB)" if plotly_path.exists() else f"   Plotly:    MISSING")

if not dashboard_path.exists():
    print("\n❌ Dashboard HTML missing - regenerate with:")
    print("   python -c \"from pathlib import Path; from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent; AutonomyGuardianAgent(Path.cwd()).generate_compliance_report(markdown=False)\"")
    exit(1)

# Read dashboard HTML
html = dashboard_path.read_text(encoding='utf-8')

print(f"\n2. Dashboard HTML Analysis:")
print(f"   Total size: {len(html):,} characters")

# Check Plotly references
plotly_refs = re.findall(r'(plotly[^"\'<>]*\.js)', html, re.IGNORECASE)
print(f"   Plotly references: {len(plotly_refs)}")
for ref in set(plotly_refs):
    print(f"     - {ref}")

# Check for loadScript calls
load_script_match = re.search(r"loadScript\(['\"]([^'\"]+)['\"]\)", html)
if load_script_match:
    print(f"   Primary load: {load_script_match.group(1)}")

# Check CDN fallback
cdn_match = re.search(r"https://[^'\"]+plotly[^'\"]+\.js", html)
if cdn_match:
    print(f"   CDN fallback: {cdn_match.group(0)}")

# Check for data injection
print(f"\n3. Data Injection:")
has_dashboard_data = 'const dashboardData = [' in html and 'const dashboardData = [];' not in html
has_recommendations = 'const recommendationsData = [' in html and 'const recommendationsData = [];' not in html
has_gauge_data = 'const gaugeData = {' in html and 'const gaugeData = {};' not in html

print(f"   dashboardData populated: {has_dashboard_data}")
print(f"   recommendationsData populated: {has_recommendations}")
print(f"   gaugeData populated: {has_gauge_data}")

if has_dashboard_data:
    # Count territories
    territory_count = html.count('"Territory"')
    print(f"   Territories found: {territory_count}")

# Check for Strategic Recommendations section
strategic_section = 'Strategic Recommendations' in html
strategic_content = re.search(r'Strategic Recommendations.*?</div>', html, re.DOTALL)
if strategic_section:
    print(f"\n4. Strategic Recommendations Section:")
    print(f"   Section present: ✓")
    if strategic_content:
        content_length = len(strategic_content.group(0))
        print(f"   Content length: {content_length} characters")
        # Check if it has actual recommendations
        has_list = '<ol>' in strategic_content.group(0) or '<ul>' in strategic_content.group(0)
        print(f"   Has list items: {has_list}")
else:
    print(f"\n4. Strategic Recommendations Section: MISSING")

# Check for Plotly.newPlot calls
plotly_calls = len(re.findall(r'Plotly\.newPlot\(', html))
print(f"\n5. Plotly Chart Calls:")
print(f"   Total Plotly.newPlot() calls: {plotly_calls}")

# Check for chart div IDs
chart_ids = ['riskMatrix', 'healthChart', 'healingChart', 'complianceChart', 
             'observabilityChart', 'complexityChart', 'healthGauge', 'complianceGauge']
print(f"   Chart containers:")
for chart_id in chart_ids:
    exists = f'id="{chart_id}"' in html
    print(f"     - {chart_id}: {'✓' if exists else '✗'}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)

if not plotly_path.exists():
    print("❌ Plotly.min.js is MISSING")
    print("   → Regenerate dashboard to auto-download Plotly v3.3.1")
elif plotly_path.stat().st_size < 3_000_000:
    print("⚠️  Plotly.min.js is too small (corrupted download?)")
    print("   → Delete and regenerate to re-download")
else:
    print("✓ Plotly.min.js present and correct size")

if not has_dashboard_data:
    print("❌ Dashboard data not injected")
    print("   → Regenerate dashboard")
else:
    print("✓ Dashboard data injected correctly")

print("\n📋 To view dashboard:")
print("   1. Ensure HTTP server is running:")
print("      python scripts/serve_dashboard.py")
print("   2. Open in browser:")
print("      http://localhost:8765/autonomy_dashboard.html")
print("   3. Check browser console (F12) for errors")
print("\n" + "=" * 80)
