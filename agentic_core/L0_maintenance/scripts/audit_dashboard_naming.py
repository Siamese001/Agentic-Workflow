#!/usr/bin/env python3
"""
Complete End-to-End Audit of Dashboard Variable and Column Naming Conventions.
Identifies all mismatches between data files and renderers.
"""
import json
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"

def extract_js_variable(file_path, patterns):
    """Extract variable name and structure from JS file."""
    content = file_path.read_text(encoding='utf-8')
    results = {}
    for pattern_name, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            results[pattern_name] = match.group(1) if match.groups() else True
    return results, content

def extract_json_keys(js_content, var_pattern):
    """Extract JSON keys from JS file content."""
    # Remove comments
    lines = [l for l in js_content.split('\n') if not l.strip().startswith('//')]
    content = '\n'.join(lines)
    
    # Try to extract JSON array/object
    match = re.search(var_pattern + r'\s*=\s*(\[[\s\S]*?\]);?$', content, re.MULTILINE)
    if match:
        try:
            data = json.loads(match.group(1))
            if isinstance(data, list) and len(data) > 0:
                return list(data[0].keys()) if isinstance(data[0], dict) else []
            elif isinstance(data, dict):
                return list(data.keys())
        except:
            pass
    return []

def audit_data_files():
    """Audit all data files for variable names and schemas."""
    print("\n" + "="*80)
    print("AUDIT: DATA FILES")
    print("="*80)
    
    findings = {}
    
    # 1. dashboard_data.js
    print("\n1. dashboard_data.js:")
    file_path = dashboard_dir / "data" / "dashboard_data.js"
    content = file_path.read_text(encoding='utf-8')
    
    # Check variable declaration
    if 'window.dashboardData' in content:
        print("   ✅ Variable: window.dashboardData")
        findings['dashboardData'] = 'window.dashboardData'
    elif 'const dashboardData' in content:
        print("   ❌ Variable: const dashboardData (should be window.dashboardData)")
        findings['dashboardData'] = 'const dashboardData'
    
    # Extract schema
    lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
    json_content = '\n'.join(lines)
    json_content = re.sub(r'^(window\.)?dashboardData\s*=\s*', '', json_content.strip())
    if json_content.endswith(';'):
        json_content = json_content[:-1]
    try:
        data = json.loads(json_content)
        if data:
            schema = list(data[0].keys())
            print(f"   Schema ({len(schema)} columns):")
            for col in schema:
                print(f"      - {col}")
            findings['dashboardData_schema'] = schema
    except Exception as e:
        print(f"   ❌ Failed to parse schema: {e}")
    
    # 2. agent_data.js
    print("\n2. agent_data.js:")
    file_path = dashboard_dir / "data" / "agent_data.js"
    content = file_path.read_text(encoding='utf-8')
    
    if 'window.realAgentData' in content:
        print("   ✅ Variable: window.realAgentData")
        findings['agentData'] = 'window.realAgentData'
    elif 'window.globalAgentData' in content:
        print("   ⚠️  Variable: window.globalAgentData (needs mapping to realAgentData)")
        findings['agentData'] = 'window.globalAgentData'
    elif 'const agentData' in content:
        print("   ❌ Variable: const agentData (should be window.realAgentData)")
        findings['agentData'] = 'const agentData'
    
    # 3. observations.js
    print("\n3. observations.js:")
    file_path = dashboard_dir / "data" / "observations.js"
    content = file_path.read_text(encoding='utf-8')
    
    if 'window.observations' in content:
        print("   ✅ Variable: window.observations")
        findings['observations'] = 'window.observations'
    elif 'window.strategicObservationsData' in content:
        print("   ⚠️  Variable: window.strategicObservationsData (needs mapping to observations)")
        findings['observations'] = 'window.strategicObservationsData'
    
    # 4. recommendations.js
    print("\n4. recommendations.js:")
    file_path = dashboard_dir / "data" / "recommendations.js"
    content = file_path.read_text(encoding='utf-8')
    
    if 'window.recommendations' in content:
        print("   ✅ Variable: window.recommendations")
        findings['recommendations'] = 'window.recommendations'
    elif 'window.recommendationsData' in content:
        print("   ⚠️  Variable: window.recommendationsData (needs mapping to recommendations)")
        findings['recommendations'] = 'window.recommendationsData'
    
    return findings

def audit_renderers(data_schema):
    """Audit renderer files for column references."""
    print("\n" + "="*80)
    print("AUDIT: RENDERER FILES")
    print("="*80)
    
    mismatches = []
    
    # table-renderer.js
    print("\n1. table-renderer.js:")
    file_path = dashboard_dir / "js" / "renderers" / "table-renderer.js"
    content = file_path.read_text(encoding='utf-8')
    
    # Find all row['...'] references
    row_refs = re.findall(r"row\['([^']+)'\]", content)
    row_refs = list(set(row_refs))
    
    print(f"   Column references found ({len(row_refs)}):")
    for ref in sorted(row_refs):
        if ref in data_schema:
            print(f"      ✅ row['{ref}']")
        else:
            print(f"      ❌ row['{ref}'] - NOT IN SCHEMA")
            mismatches.append(('table-renderer.js', ref))
    
    # Find row.Property references
    row_dot_refs = re.findall(r"row\.(\w+)", content)
    row_dot_refs = list(set(row_dot_refs))
    
    print(f"\n   row.Property references ({len(row_dot_refs)}):")
    for ref in sorted(row_dot_refs):
        if ref in data_schema or ref in ['Territory', 'Total']:
            print(f"      ✅ row.{ref}")
        else:
            print(f"      ⚠️  row.{ref} - Check if valid")
    
    # kpi-renderer.js
    print("\n2. kpi-renderer.js:")
    file_path = dashboard_dir / "js" / "renderers" / "kpi-renderer.js"
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # Check variable references
        var_refs = []
        if 'dashboardData' in content:
            var_refs.append('dashboardData')
        if 'realAgentData' in content:
            var_refs.append('realAgentData')
        if 'observations' in content:
            var_refs.append('observations')
        if 'recommendations' in content:
            var_refs.append('recommendations')
        
        print(f"   Variable references: {var_refs}")
    else:
        print("   File not found")
    
    # content-renderer.js
    print("\n3. content-renderer.js:")
    file_path = dashboard_dir / "js" / "renderers" / "content-renderer.js"
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        row_refs = re.findall(r"row\['([^']+)'\]", content)
        row_refs = list(set(row_refs))
        
        print(f"   Column references ({len(row_refs)}):")
        for ref in sorted(row_refs):
            if ref in data_schema:
                print(f"      ✅ row['{ref}']")
            else:
                print(f"      ❌ row['{ref}'] - NOT IN SCHEMA")
                mismatches.append(('content-renderer.js', ref))
    else:
        print("   File not found")
    
    return mismatches

def audit_main_js():
    """Audit main.js for variable mappings."""
    print("\n" + "="*80)
    print("AUDIT: main.js VARIABLE MAPPINGS")
    print("="*80)
    
    file_path = dashboard_dir / "js" / "main.js"
    content = file_path.read_text(encoding='utf-8')
    
    mappings = {
        'globalAgentData → realAgentData': 'window.globalAgentData' in content and 'window.realAgentData = window.globalAgentData' in content,
        'agentData → realAgentData': 'window.agentData' in content and 'window.realAgentData = window.agentData' in content,
        'strategicObservationsData → observations': 'window.strategicObservationsData' in content and 'window.observations = window.strategicObservationsData' in content,
        'recommendationsData → recommendations': 'window.recommendationsData' in content and 'window.recommendations = window.recommendationsData' in content,
    }
    
    print("\n   Variable Polyfill Mappings:")
    for mapping, exists in mappings.items():
        status = "✅" if exists else "❌ MISSING"
        print(f"      {status} {mapping}")
    
    return mappings

def generate_fix_report(data_findings, mismatches, mappings):
    """Generate a report of all fixes needed."""
    print("\n" + "="*80)
    print("FIX REPORT")
    print("="*80)
    
    fixes_needed = []
    
    # Data file fixes
    if data_findings.get('dashboardData') == 'const dashboardData':
        fixes_needed.append({
            'file': 'data/dashboard_data.js',
            'issue': 'Variable uses const instead of window',
            'fix': 'Change "const dashboardData" to "window.dashboardData"'
        })
    
    # Renderer column fixes
    for file, col in mismatches:
        fixes_needed.append({
            'file': f'js/renderers/{file}',
            'issue': f'Column reference "{col}" not in schema',
            'fix': f'Update to correct column name from schema'
        })
    
    # Mapping fixes
    for mapping, exists in mappings.items():
        if not exists:
            fixes_needed.append({
                'file': 'js/main.js',
                'issue': f'Missing polyfill mapping: {mapping}',
                'fix': f'Add mapping in checkDependencies()'
            })
    
    if fixes_needed:
        print(f"\n   {len(fixes_needed)} fixes needed:")
        for i, fix in enumerate(fixes_needed, 1):
            print(f"\n   {i}. {fix['file']}")
            print(f"      Issue: {fix['issue']}")
            print(f"      Fix: {fix['fix']}")
    else:
        print("\n   ✅ No fixes needed - all naming conventions are correct!")
    
    return fixes_needed

if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPLETE END-TO-END DASHBOARD NAMING AUDIT")
    print("="*80)
    
    # Step 1: Audit data files
    data_findings = audit_data_files()
    
    # Step 2: Audit renderers
    schema = data_findings.get('dashboardData_schema', [])
    mismatches = audit_renderers(schema)
    
    # Step 3: Audit main.js mappings
    mappings = audit_main_js()
    
    # Step 4: Generate fix report
    fixes = generate_fix_report(data_findings, mismatches, mappings)
    
    print("\n" + "="*80)
    print("AUDIT COMPLETE")
    print("="*80)
