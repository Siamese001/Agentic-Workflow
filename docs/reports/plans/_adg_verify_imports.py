#!/usr/bin/env python3
"""Verify all 7 formerly-violating files now import from L0 path_constants correctly."""
import sys, importlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

MODULES = [
    "agentic_core.L0_routing.scripts.bulk_hierarchy_heal_util",
    "agentic_core.L0_routing.scripts.flatten_scripts_directory_util",
    "agentic_core.L0_routing.scripts.populate_ssot_folders_util",
    "agentic_core.L0_routing.scripts.validate_sovereign_structure_util",
    "agentic_core.L0_routing.utils.fix_all_tunnels_util",
    "agentic_core.L1_cognition.utils.constants_util",
    "agentic_core.L2_execution.enforcement.sovereign_filesystem_mcp",
]

all_ok = True
for modname in MODULES:
    try:
        mod = importlib.import_module(modname)
        print(f"  OK  {modname}")
    except Exception as e:
        print(f"  FAIL {modname}: {e}")
        all_ok = False

print()
print("=== path_constants has all needed symbols? ===")
from agentic_core.L0_routing.config import path_constants as pc
needed = [
    "DEPTH_RULES", "PROJECT_ROOT_WHITELIST", "CORE_SUBFOLDER_MAP",
    "APPS_LIC_SUBFOLDER_MAP", "APPS_RG_SUBFOLDER_MAP", "APPS_SHARED_SUBFOLDER_MAP",
    "SOVEREIGN_EXCLUDED_FOLDERS",
]
for sym in needed:
    ok = hasattr(pc, sym)
    print(f"  {'OK' if ok else 'MISSING'} {sym}")
    if not ok:
        all_ok = False

print()
print("RESULT:", "ALL OK" if all_ok else "FAILURES DETECTED")
