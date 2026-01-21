#!/usr/bin/env python3
"""Clean dashboard HTML by removing all realAgentData blocks."""
import re
from pathlib import Path

dashboard_path = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html')

print("Reading HTML...")
html = dashboard_path.read_text(encoding='utf-8')
print(f"Original size: {len(html)} chars, {html.count(chr(10))} lines")

# Find all realAgentData blocks
pattern = r'const realAgentData = \{[\s\S]*?\n\s*\};'
matches = list(re.finditer(pattern, html))
print(f"Found {len(matches)} realAgentData blocks")

if len(matches) > 1:
    print(f"⚠️  Multiple realAgentData blocks found - removing all")
    # Remove all matches
    for match in reversed(matches):  # Reverse to maintain indices
        html = html[:match.start()] + html[match.end():]

    print(f"After cleanup: {len(html)} chars, {html.count(chr(10))} lines")

    # Write back
    dashboard_path.write_text(html, encoding='utf-8')
    print("✅ HTML cleaned and saved")
elif len(matches) == 1:
    print("✅ Only one realAgentData block - HTML is clean")
else:
    print("✅ No realAgentData blocks - HTML is clean")
