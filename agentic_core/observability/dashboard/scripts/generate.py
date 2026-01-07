"""
Unified Report Generator - Sovereign CLI (L6 Observability)
Consolidates: check_dashboard.py, verify_dashboard.py, trace_dashboard_generation.py
"""
import sys
from pathlib import Path
from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent

def trigger_unified_report():
    """Trigger the hardened AutonomyGuardianAgent report pipeline."""
    project_root = Path(__file__).parent.parent.parent.parent.parent
    print(f"🛡️ Triggering Unified SSOT Compliance Scan...")
    
    try:
        guardian = AutonomyGuardianAgent(project_root)
        # Executes L6 Modular Engine for Markdown and HTML
        guardian.generate_compliance_report(markdown=True)
        print(f"✅ Unified Report Generation Complete.")
        print(f"📂 View artifacts in: {project_root / 'reports'}")
    except Exception as e:
        print(f"❌ Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    trigger_unified_report()
