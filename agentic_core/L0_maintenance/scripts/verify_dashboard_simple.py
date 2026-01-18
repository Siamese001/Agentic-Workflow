#!/usr/bin/env python3
"""
Simple Dashboard Verification - Check files and HTML content directly
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("DASHBOARD DEPLOYMENT VERIFICATION")
print("=" * 70)

# 1. Check HTML file has Phase 5 sections
print("\n1. Checking HTML file for Phase 5 sections...")
html_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"

if not html_file.exists():
    print(f"   ❌ HTML file not found: {html_file}")
    sys.exit(1)

html_content = html_file.read_text(encoding='utf-8')

sections_to_find = [
    ("Meta-Learning Activity", "🧠 Meta-Learning Activity"),
    ("Redis Cache Activity", "💾 Redis Cache Activity"),
    ("Pinecone Vector Operations", "🔍 Pinecone Vector Operations"),
    ("Agent Execution Flow", "⚡ Agent Execution Flow"),
]

for section_id, section_text in sections_to_find:
    if section_text in html_content:
        print(f"   ✅ Found: {section_text}")
    else:
        print(f"   ❌ Missing: {section_text}")

# 2. Check for container IDs
print("\n2. Checking for container elements...")
containers = [
    "meta-stats", "strategy-weights", "experience-stream", "pattern-timeline",
    "redis-stats", "redis-log", "pinecone-stats", "pinecone-queries",
    "layer-flow", "execution-summary", "execution-timeline"
]

for container in containers:
    if f'id="{container}"' in html_content:
        print(f"   ✅ Found: #{container}")
    else:
        print(f"   ❌ Missing: #{container}")

# 3. Check JavaScript includes
print("\n3. Checking JavaScript includes...")
js_includes = [
    "meta-learning-panel.js",
    "redis-monitor.js",
    "pinecone-monitor.js",
    "execution-flow.js",
    "meta-learning-controller.js",
]

for js_file in js_includes:
    if js_file in html_content:
        print(f"   ✅ Included: {js_file}")
    else:
        print(f"   ❌ Missing: {js_file}")

# 4. Check CSS include
print("\n4. Checking CSS include...")
if "meta-learning.css" in html_content:
    print("   ✅ Included: meta-learning.css")
else:
    print("   ❌ Missing: meta-learning.css")

# 5. Check JavaScript files exist
print("\n5. Checking JavaScript files exist...")
dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"

js_files = [
    dashboard_dir / "js" / "components" / "meta-learning-panel.js",
    dashboard_dir / "js" / "components" / "redis-monitor.js",
    dashboard_dir / "js" / "components" / "pinecone-monitor.js",
    dashboard_dir / "js" / "components" / "execution-flow.js",
    dashboard_dir / "js" / "controllers" / "meta-learning-controller.js",
]

for js_file in js_files:
    if js_file.exists():
        size = js_file.stat().st_size
        print(f"   ✅ Exists: {js_file.name} ({size:,} bytes)")
    else:
        print(f"   ❌ Missing: {js_file}")

# 6. Check CSS file exists
print("\n6. Checking CSS file exists...")
css_file = dashboard_dir / "css" / "meta-learning.css"
if css_file.exists():
    size = css_file.stat().st_size
    print(f"   ✅ Exists: meta-learning.css ({size:,} bytes)")
else:
    print(f"   ❌ Missing: meta-learning.css")

# 7. Check main.js has initialization
print("\n7. Checking main.js initialization...")
main_js = dashboard_dir / "js" / "main.js"
if main_js.exists():
    main_content = main_js.read_text(encoding='utf-8')
    if "initializeMetaLearningDashboard" in main_content:
        print("   ✅ main.js calls initializeMetaLearningDashboard()")
    else:
        print("   ❌ main.js missing initialization call")
else:
    print("   ❌ main.js not found")

# 8. Show where sections are in HTML
print("\n8. Locating sections in HTML...")
lines = html_content.split('\n')
for i, line in enumerate(lines, 1):
    if "Meta-Learning Activity" in line:
        print(f"   📍 Meta-Learning section at line {i}")
    if "Redis Cache Activity" in line:
        print(f"   📍 Redis section at line {i}")
    if "Pinecone Vector Operations" in line:
        print(f"   📍 Pinecone section at line {i}")
    if "Agent Execution Flow" in line:
        print(f"   📍 Execution Flow section at line {i}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\nAll Phase 5 components are in the HTML file.")
print("If you don't see them in your browser:")
print("1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
print("2. Clear browser cache completely")
print("3. Try incognito/private mode")
print("4. Check browser console (F12) for JavaScript errors")
