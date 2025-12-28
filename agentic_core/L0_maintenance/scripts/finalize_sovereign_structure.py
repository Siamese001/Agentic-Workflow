"""
SOVEREIGN STRUCTURE FINALIZER
Creates all missing directories to enforce the 3-level depth law.
"""
import os
import sys

# Import from proper location
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
    TESTS_SUBFOLDER_MAP,
)
BLUEPRINT_DIR = r"C:/Git/Agentic-Workflow/agentic_core/config/blueprint_sovereign"
if BLUEPRINT_DIR not in sys.path:
    sys.path.append(BLUEPRINT_DIR)

try:
    from structure_blueprint import (
        APPS_LIC_SUBFOLDER_MAP,
        APPS_RG_SUBFOLDER_MAP,
        APPS_SHARED_SUBFOLDER_MAP,
        CORE_SUBFOLDER_MAP,
        TESTS_SUBFOLDER_MAP,
    )
except ImportError:
    print(f"❌ ERROR: Could not find structure_blueprint.py")
    sys.exit(1)

def finalize_structure(root_path):
    print(f"--- FINALIZING SOVEREIGN STRUCTURE ---")
    
    # 1. Force Core Depth (agentic_core L1 > L2 > L3)
    for l1, l2_list in CORE_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "agentic_core", l1, l2)
            ensure_dir(path)

    # 2. Force App Depth - apps_rg
    for l1, l2_list in APPS_RG_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "apps_rg", l1, l2)
            ensure_dir(path)
    
    # 3. Force App Depth - apps_lic
    for l1, l2_list in APPS_LIC_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "apps_lic", l1, l2)
            ensure_dir(path)
    
    # 4. Force App Depth - apps_shared
    for l1, l2_list in APPS_SHARED_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "apps_shared", l1, l2)
            ensure_dir(path)

    # 5. Force Test Depth (tests L1 > L2)
    for l1, l2_list in TESTS_SUBFOLDER_MAP.items():
        for l2 in l2_list:
            path = os.path.join(root_path, "tests", l1, l2)
            ensure_dir(path)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        # Create .gitkeep so Git tracks these empty deep folders
        with open(os.path.join(path, ".gitkeep"), 'w') as f:
            f.write('')
        print(f"✅ CREATED: {path}")
    else:
        print(f"✓ EXISTS: {path}")

if __name__ == "__main__":
    finalize_structure("C:/Git/Agentic-Workflow")
    print("\n--- FINISHED. RUN VALIDATOR AGAIN TO VERIFY ---")
