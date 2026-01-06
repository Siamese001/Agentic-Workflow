#!/usr/bin/env python3
"""
Test dashboard generation without circular imports.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_dashboard_generation():
    """Test dashboard generation end-to-end."""
    print("Testing dashboard generation...")
    
    try:
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        
        agent = AutonomyGuardianAgent(project_root)
        print("✓ AutonomyGuardianAgent initialized")
        
        agent.generate_compliance_report(markdown=False)
        print("✓ Dashboard generated")
        
        # Check if dashboard file exists
        dashboard_path = project_root / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            print("✗ Dashboard file not found")
            return False
        
        print(f"✓ Dashboard file exists: {dashboard_path}")
        
        # Check if strategic recommendations are present
        content = dashboard_path.read_text(encoding='utf-8')
        
        if '<!-- STRATEGIC_REVIEW_INSERT -->' in content:
            print("✗ Strategic review placeholder not replaced")
            return False
        
        if '<!-- TOP_RECS_INSERT -->' in content:
            print("✗ Top recommendations placeholder not replaced")
            return False
        
        print("✓ Strategic recommendations placeholders replaced")
        
        # Check if data is present
        if 'const dashboardData = [];' in content:
            print("✗ Dashboard data not injected")
            return False
        
        print("✓ Dashboard data injected")
        
        # Check if recommendations data is present
        if 'const recommendationsData = [];' in content:
            print("✗ Recommendations data not injected")
            return False
        
        print("✓ Recommendations data injected")
        
        print("\n✅ All dashboard generation tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard_generation()
    sys.exit(0 if success else 1)
