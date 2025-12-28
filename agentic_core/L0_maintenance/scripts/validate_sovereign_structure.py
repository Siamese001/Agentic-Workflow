"""
SOVEREIGN STRUCTURE VALIDATOR
Enforces the 3-level depth law for agentic architecture.
"""
import os
import sys

BLUEPRINT_DIR = r"C:/Git/Agentic-Workflow/agentic_core/config/P1_core"
# Path append no longer needed - using absolute import

try:
    from agentic_core.config.blueprint_sovereign.structure_blueprint import (
        APPS_LIC_SUBFOLDER_MAP,
        APPS_RG_SUBFOLDER_MAP,
        APPS_SHARED_SUBFOLDER_MAP,
        CORE_SUBFOLDER_MAP,
        TESTS_SUBFOLDER_MAP,
    )
except ImportError:
    print(f"❌ ERROR: Could not find structure_blueprint.py in {BLUEPRINT_DIR}")
    sys.exit(1)

def check_sovereign_law(root_path):
    violations = []

    # 1. Check Core (Depth 4: agentic_core/L1/L2/file)
    core_path = os.path.join(root_path, "agentic_core")
    for l1, l2_list in CORE_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(core_path, l1, l2)
            if not os.path.exists(path):
                violations.append(f"MISSING CORE DEPTH: agentic_core/{l1}/{l2}")

    # 2. Check Apps (Depth 3: apps_*/L1/L2/file)
    for l1, l2_list in APPS_RG_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "apps_rg", l1, l2)
            if not os.path.exists(path):
                violations.append(f"MISSING APP DEPTH: apps_rg/{l1}/{l2}")
    
    for l1, l2_list in APPS_LIC_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "apps_lic", l1, l2)
            if not os.path.exists(path):
                violations.append(f"MISSING APP DEPTH: apps_lic/{l1}/{l2}")
    
    for l1, l2_list in APPS_SHARED_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "apps_shared", l1, l2)
            if not os.path.exists(path):
                violations.append(f"MISSING APP DEPTH: apps_shared/{l1}/{l2}")

    # 3. Check Tests (Depth 3: tests/L1/L2/file)
    for l1, l2_list in TESTS_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "tests", l1, l2)
            if not os.path.exists(path):
                violations.append(f"MISSING TEST DEPTH: tests/{l1}/{l2}")

    # --- THE VERDICT ---
    if not violations:
        print("\n✅ SOVEREIGN LAW ENFORCED: Your structure is perfect.")
        return 0
    else:
        print(f"\n❌ SOVEREIGN VIOLATIONS FOUND ({len(violations)}):")
        for v in violations:
            print(f"  - {v}")
        return 1

if __name__ == "__main__":
    PROJECT_ROOT = "C:/Git/Agentic-Workflow"
    print(f"--- Auditing Sovereign Structure for {PROJECT_ROOT} ---")
    exit_code = check_sovereign_law(PROJECT_ROOT)
    sys.exit(exit_code)
