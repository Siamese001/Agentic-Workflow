#!/usr/bin/env python3
"""Quick fix script to restore build_total_row return statement"""

import re

file_path = "agentic_core/L6_observability/dashboards/generate_dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the corrupted return statement
old_pattern = r'''        return \{
            "Territory": "TOTAL",
            "Total": total_agents,
            "Compliant": sum\(r\["Compliant"\] for r in rows\),
            "Heal Cap %": heal_cap_pct,
            "Heal Invocation %": heal_inv_pct,
            "Invocation %": heal_inv_pct,
            "Hardened %": hardened_pct,
            "MCP Capable %": mcp_pct,
            "Test %": test_pct,
            "Observable %": obs_pct,
            "Avg CC": avg_cc,
            "Avg LOC": avg_loc,  # PHASE 1 FIX: Real data
            "IsInfrastructure": False
        \}'''

new_return = '''        return {
            "Territory": "TOTAL",
            "Total": total_agents,
            "Compliant": sum(r["Compliant"] for r in rows),
            "Heal Cap %": heal_cap_pct,
            "Heal Invocation %": heal_inv_pct,
            "Invocation %": heal_inv_pct,
            "Hardened %": hardened_pct,
            "MCP Capable %": mcp_pct,
            "Test %": test_pct,
            "Observable %": obs_pct,
            "Avg CC": avg_cc,
            "Avg LOC": avg_loc,  # PHASE 1 FIX: Real data
            "Typed %": typed_pct,
            "Documented %": doc_pct,
            "Metadata %": 100.0,
            "Proper Base %": proper_base_pct,
            "Base Class Inherit %": proper_base_pct,
            "Schema Strictness %": schema_pct,  # PHASE 1 FIX: Real data
            "Complexity Health": complexity_health,
            "Code Quality Score": code_quality,
            "Criticality": avg_criticality,  # PHASE 2 FIX: Weighted average from territories
            "Health": health,
            "Health Breakdown": f"Heal:{heal_cap_pct:.0f}+Inv:{heal_inv_pct:.0f}+Test:{test_pct:.0f}+Obs:{obs_pct:.0f}+CC:{complexity_health:.0f}",
            "Risk": risk,
            "Used %": 95.0,
            "Priority": "ALL",
            "IsInfrastructure": False
        }'''

content = re.sub(old_pattern, new_return, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed build_total_row return statement")
