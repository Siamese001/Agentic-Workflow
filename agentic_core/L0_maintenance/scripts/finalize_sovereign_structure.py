"""
SOVEREIGN STRUCTURE FINALIZER
Creates all missing directories to enforce the 3-level depth law.
"""
import os
import sys

# --- THE IMPORT FIX ---
BLUEPRINT_DIR = r"C:/Git/Agentic-Workflow/agentic_core/config/P1_core"
if BLUEPRINT_DIR not in sys.path:
    sys.path.append(BLUEPRINT_DIR)

try:
    from structure_blueprint import AGENTIC_CORE_REGISTRY, APP_TERRITORY_REGISTRY, TESTS_REGISTRY
except ImportError:
    print(f"❌ ERROR: Could not find structure_blueprint.py")
    sys.exit(1)

def finalize_structure(root_path):
    print(f"--- FINALIZING SOVEREIGN STRUCTURE ---")
    
    # 1. Force Core Depth (already mostly done, but let's be sure)
    for l2, l3_list in AGENTIC_CORE_REGISTRY.items():
        for l3 in l3_list:
            path = os.path.join(root_path, "agentic_core", l2, l3)
            ensure_dir(path)

    # 2. Force App Depth (Fixes your 9 app violations)
    for app, l2_dict in APP_TERRITORY_REGISTRY.items():
        for l2, l3_list in l2_dict.items():
            for l3 in l3_list:
                path = os.path.join(root_path, app, l2, l3)
                ensure_dir(path)

    # 3. Force Test Depth (Fixes your 7 test violations)
    for l2, l3_list in TESTS_REGISTRY.items():
        for l3 in l3_list:
            path = os.path.join(root_path, "tests", l2, l3)
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
