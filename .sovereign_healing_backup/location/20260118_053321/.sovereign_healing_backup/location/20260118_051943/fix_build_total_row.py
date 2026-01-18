#!/usr/bin/env python3
"""Fix the corrupted build_total_row return statement"""

file_path = "agentic_core/L6_observability/dashboards/generate_dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with the incomplete return statement
for i, line in enumerate(lines):
    if '"Avg LOC": avg_loc,  # PHASE 1 FIX: Real data' in line and i > 400:
        # Check if next line is missing fields
        if '"IsInfrastructure": False' in lines[i+1]:
            print(f"Found corrupted return at line {i+1}")
            # Insert the missing fields
            missing_lines = [
                '            "Typed %": typed_pct,\n',
                '            "Documented %": doc_pct,\n',
                '            "Metadata %": 100.0,\n',
                '            "Proper Base %": proper_base_pct,\n',
                '            "Base Class Inherit %": proper_base_pct,\n',
                '            "Schema Strictness %": schema_pct,  # PHASE 1 FIX: Real data\n',
                '            "Complexity Health": complexity_health,\n',
                '            "Code Quality Score": code_quality,\n',
                '            "Criticality": avg_criticality,  # PHASE 2 FIX: Weighted average from territories\n',
                '            "Health": health,\n',
                '            "Health Breakdown": f"Heal:{heal_cap_pct:.0f}+Inv:{heal_inv_pct:.0f}+Test:{test_pct:.0f}+Obs:{obs_pct:.0f}+CC:{complexity_health:.0f}",\n',
                '            "Risk": risk,\n',
                '            "Used %": 95.0,\n',
                '            "Priority": "ALL",\n',
            ]
            # Insert after the Avg LOC line
            for j, missing_line in enumerate(missing_lines):
                lines.insert(i + 1 + j, missing_line)
            print(f"Inserted {len(missing_lines)} missing lines")
            break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed build_total_row return statement")
