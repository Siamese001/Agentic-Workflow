#!/usr/bin/env python3
"""Debug script to check path resolution."""

from pathlib import Path
import sys

# Simulate the same path resolution as the test
test_file = Path("tests/e2e/ops_scripts/test_mission_script_integrity.py")
if test_file.exists():
    project_root = test_file.resolve().parent.parent.parent
    print(f"Test file: {test_file.resolve()}")
    print(f"Project root: {project_root}")
    
    target_zones = [project_root / "apps_rg", project_root / "apps_lic"]
    print(f"Target zones: {target_zones}")
    
    existing_zones = [z for z in target_zones if z.exists()]
    print(f"Existing zones: {existing_zones}")
    
    zone_names = [str(z.name) for z in existing_zones]
    print(f"Zone names: {zone_names}")
    print(f"Count: {len(existing_zones)}")
else:
    print("Test file not found")
