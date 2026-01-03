#!/usr/bin/env python
"""Quick test to generate dashboard."""
import sys
from pathlib import Path

try:
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
    
    guardian = AutonomyGuardianAgent(project_root)
    guardian.generate_compliance_report(markdown=True)
    
    dashboard = project_root / "autonomy_dashboard.html"
    if dashboard.exists():
        print(f"SUCCESS: Dashboard created at {dashboard}")
        print(f"Size: {dashboard.stat().st_size} bytes")
    else:
        print("ERROR: Dashboard not created")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
