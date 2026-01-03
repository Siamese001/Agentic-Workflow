#!/usr/bin/env python
"""Generate the self-contained autonomy dashboard with embedded data."""

from pathlib import Path
from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent

if __name__ == "__main__":
    project_root = Path(__file__).parent
    guardian = AutonomyGuardianAgent(project_root)
    
    print("Generating Autonomy Compliance Report with Self-Contained Dashboard...")
    print("=" * 80)
    
    guardian.generate_compliance_report(markdown=True)
    
    print("=" * 80)
    print("\n✅ Dashboard generation complete!")
    
    dashboard_file = project_root / "autonomy_dashboard.html"
    if dashboard_file.exists():
        file_size = dashboard_file.stat().st_size
        print(f"\n📊 Self-Contained Dashboard:")
        print(f"   File: {dashboard_file}")
        print(f"   Size: {file_size:,} bytes (~{file_size/1024:.1f} KB)")
        print(f"\n🚀 Open in browser:")
        print(f"   file://{dashboard_file.absolute()}")
        print(f"\n✨ Features:")
        print(f"   • No server required (file:// protocol works)")
        print(f"   • No CORS issues")
        print(f"   • Fully self-contained (data embedded as JSON)")
        print(f"   • Interactive tabs: Executive, Territory Analysis, Risk, Compliance, Recommendations")
        print(f"   • Top 10 prioritized recommendations with actionable diffs")
    else:
        print("❌ Dashboard file was not created. Check for errors above.")
