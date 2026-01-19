#!/usr/bin/env python3
"""
Compare modular dashboard data with monolithic backup data
Validates every cell to ensure data fidelity
"""

import json
import re
from pathlib import Path
from archives.location_violations.file_utils import safe_read_file, safe_write_file

def extract_monolithic_data():
    """Extract dashboard data from monolithic backup HTML"""
    backup_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard_backup.html")
    
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_path}")
        return None
    
    with open(backup_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the dashboardData JSON in the HTML (handles both formats)
    match = re.search(r'const dashboardData = (?:window\.dashboardData \|\| )?(\[.*?\]);', html_content, re.DOTALL)
    if not match:
        print("❌ Could not find dashboardData in monolithic HTML")
        return None
    
    data_str = match.group(1)
    data = json.loads(data_str)
    
    print(f"✅ Extracted {len(data)} rows from monolithic backup")
    return data

def load_modular_data():
    """Load modular dashboard data from JS file"""
    data_path = Path("agentic_core/L6_observability/dashboards/data/dashboard_data.js")
    
    if not data_path.exists():
        print(f"❌ Modular data file not found: {data_path}")
        return None
    
    with open(data_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Extract the JSON array from window.dashboardData
    match = re.search(r'window\.dashboardData = (\[.*?\]);', js_content, re.DOTALL)
    if not match:
        print("❌ Could not find dashboardData in modular JS")
        return None
    
    data_str = match.group(1)
    data = json.loads(data_str)
    
    print(f"✅ Loaded {len(data)} rows from modular data")
    return data

def compare_values(mono_val, mod_val, field_name):
    """Compare two values with appropriate tolerance"""
    # Handle None/null
    if mono_val is None and mod_val is None:
        return True, None
    if mono_val is None or mod_val is None:
        return False, f"One value is None: mono={mono_val}, mod={mod_val}"
    
    # String comparison
    if isinstance(mono_val, str) and isinstance(mod_val, str):
        return mono_val == mod_val, None if mono_val == mod_val else f"'{mono_val}' != '{mod_val}'"
    
    # Numeric comparison with tolerance
    try:
        mono_num = float(mono_val)
        mod_num = float(mod_val)
        tolerance = 0.1  # Allow 0.1% difference due to rounding
        diff = abs(mono_num - mod_num)
        if diff <= tolerance:
            return True, None
        else:
            return False, f"{mono_num} != {mod_num} (diff: {diff:.2f})"
    except (ValueError, TypeError):
        # Not numeric, do direct comparison
        match = mono_val == mod_val
        return match, None if match else f"{mono_val} != {mod_val}"

def compare_dashboards():
    """Compare monolithic and modular dashboard data cell-by-cell"""
    print("\n" + "="*70)
    print("DASHBOARD DATA COMPARISON: Monolithic vs Modular")
    print("="*70 + "\n")
    
    mono_data = extract_monolithic_data()
    mod_data = load_modular_data()
    
    if not mono_data or not mod_data:
        print("❌ Failed to load data for comparison")
        return False
    
    # Create dictionaries keyed by territory for easy lookup
    mono_dict = {row['Territory']: row for row in mono_data}
    mod_dict = {row['Territory']: row for row in mod_data}
    
    # Get all territories from both datasets
    all_territories = sorted(set(mono_dict.keys()) | set(mod_dict.keys()))
    
    print(f"📊 Comparing {len(all_territories)} territories\n")
    
    discrepancies = []
    matched_cells = 0
    total_cells = 0
    
    for territory in all_territories:
        if territory not in mono_dict:
            discrepancies.append(f"❌ Territory '{territory}' missing from monolithic")
            continue
        if territory not in mod_dict:
            discrepancies.append(f"❌ Territory '{territory}' missing from modular")
            continue
        
        mono_row = mono_dict[territory]
        mod_row = mod_dict[territory]
        
        # Get all fields from both rows
        all_fields = sorted(set(mono_row.keys()) | set(mod_row.keys()))
        
        for field in all_fields:
            if field == 'Territory':
                continue  # Skip territory name itself
            
            total_cells += 1
            
            mono_val = mono_row.get(field)
            mod_val = mod_row.get(field)
            
            match, error = compare_values(mono_val, mod_val, field)
            
            if match:
                matched_cells += 1
            else:
                discrepancies.append(f"❌ {territory} | {field}: {error}")
    
    # Print results
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70 + "\n")
    
    print(f"Total cells compared: {total_cells}")
    print(f"Matched cells: {matched_cells}")
    print(f"Discrepancies: {len(discrepancies)}")
    print(f"Match rate: {(matched_cells/total_cells*100):.1f}%\n")
    
    if discrepancies:
        print("DISCREPANCIES FOUND:\n")
        for disc in discrepancies[:50]:  # Show first 50
            print(f"  {disc}")
        if len(discrepancies) > 50:
            print(f"\n  ... and {len(discrepancies) - 50} more")
        print("\n❌ Data validation FAILED")
        return False
    else:
        print("✅ All cells match! Data fidelity confirmed.")
        return True

if __name__ == '__main__':
    success = compare_dashboards()
    exit(0 if success else 1)
