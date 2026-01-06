#!/usr/bin/env python3
"""Check which template is being used and verify Strategic Recommendations section."""
from pathlib import Path
import hashlib

project_root = Path.cwd()

# Check all three template locations
templates = [
    'agentic_core/config/validators/dashboard_template.html',
    'agentic_core/L5_safety/validators/dashboard_template.html',
    'agentic_core/observability/dashboard/dashboard_template.html'
]

print("=" * 80)
print("TEMPLATE ANALYSIS")
print("=" * 80)

for template_path in templates:
    p = project_root / template_path
    if p.exists():
        content = p.read_text(encoding='utf-8')
        h = hashlib.md5(content.encode()).hexdigest()[:8]
        has_strategic = 'Strategic Recommendations' in content
        has_placeholder = 'STRATEGIC_REVIEW_INSERT' in content
        size = len(content)
        
        print(f"\n{template_path}:")
        print(f"  Hash: {h}")
        print(f"  Size: {size:,} bytes")
        print(f"  Has 'Strategic Recommendations': {has_strategic}")
        print(f"  Has 'STRATEGIC_REVIEW_INSERT': {has_placeholder}")
    else:
        print(f"\n{template_path}: NOT FOUND")

# Check generated dashboard
dashboard_path = project_root / 'reports' / 'autonomy_dashboard.html'
if dashboard_path.exists():
    content = dashboard_path.read_text(encoding='utf-8')
    h = hashlib.md5(content.encode()).hexdigest()[:8]
    has_strategic = 'Strategic Recommendations' in content
    has_review_text = 'Portfolio health at' in content
    size = len(content)
    
    print(f"\n{'=' * 80}")
    print("GENERATED DASHBOARD")
    print("=" * 80)
    print(f"  Hash: {h}")
    print(f"  Size: {size:,} bytes")
    print(f"  Has 'Strategic Recommendations' section: {has_strategic}")
    print(f"  Has strategic review text: {has_review_text}")
    
    # Check if placeholders were replaced
    has_placeholder1 = 'STRATEGIC_REVIEW_INSERT' in content
    has_placeholder2 = 'TOP_RECS_INSERT' in content
    print(f"  Placeholder 'STRATEGIC_REVIEW_INSERT' still present: {has_placeholder1}")
    print(f"  Placeholder 'TOP_RECS_INSERT' still present: {has_placeholder2}")
else:
    print("\nGenerated dashboard NOT FOUND")

print("\n" + "=" * 80)
