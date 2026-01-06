#!/usr/bin/env python3
"""Trace dashboard generation to find where it's failing."""
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path.cwd()))

try:
    from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
    
    project_root = Path.cwd()
    agent = AutonomyGuardianAgent(project_root)
    
    print("=" * 80)
    print("TRACING DASHBOARD GENERATION")
    print("=" * 80)
    
    # Check template path
    template_path = project_root / "agentic_core" / "config" / "validators" / "dashboard_template.html"
    print(f"\nTemplate path: {template_path}")
    print(f"Template exists: {template_path.exists()}")
    
    if template_path.exists():
        template = template_path.read_text(encoding='utf-8')
        print(f"Template size: {len(template):,} bytes")
        has_dashboard = 'const dashboardData = [];' in template
        has_recommendations = 'const recommendationsData = [];' in template
        has_timestamp = 'const lastUpdatedStr = "";' in template
        has_gauge = 'const gaugeData = {};' in template
        print(f"Has 'const dashboardData = [];': {has_dashboard}")
        print(f"Has 'const recommendationsData = [];': {has_recommendations}")
        print(f"Has 'const lastUpdatedStr = \"\";': {has_timestamp}")
        print(f"Has 'const gaugeData = {{}}': {has_gauge}")
        print(f"Has '<!-- STRATEGIC_REVIEW_INSERT -->': {'<!-- STRATEGIC_REVIEW_INSERT -->' in template}")
        print(f"Has '<!-- TOP_RECS_INSERT -->': {'<!-- TOP_RECS_INSERT -->' in template}")
        
        # Try a simple injection test
        print("\n" + "=" * 80)
        print("TESTING SIMPLE INJECTION")
        print("=" * 80)
        
        test_data = [{"Territory": "Test", "Total": 1}]
        test_json = json.dumps(test_data)
        
        html = template.replace('const dashboardData = [];', f'const dashboardData = {test_json};')
        
        print(f"After injection, 'const dashboardData = [];' still present: {'const dashboardData = [];' in html}")
        print(f"After injection, 'const dashboardData = [' present: {'const dashboardData = [' in html}")
        
    print("\n" + "=" * 80)
    print("ATTEMPTING FULL GENERATION")
    print("=" * 80)
    
    try:
        agent.generate_compliance_report(markdown=False)
        print("✓ Generation completed successfully")
    except RuntimeError as e:
        print(f"✗ Generation failed with RuntimeError:")
        print(str(e))
    except Exception as e:
        print(f"✗ Generation failed with unexpected error:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Check if dashboard was created
    dashboard_path = project_root / "reports" / "autonomy_dashboard.html"
    print(f"\nDashboard exists: {dashboard_path.exists()}")
    
except Exception as e:
    print(f"Fatal error: {e}")
    import traceback
    traceback.print_exc()
