"""
TEST STRUCTURE ALIGNMENT
Ensures all test directories have __init__.py for Python package recognition.
"""
import os
import sys

# --- THE BLUEPRINT IMPORT ---
BLUEPRINT_DIR = r"C:/Git/Agentic-Workflow/agentic_core/config/P1_core"
if BLUEPRINT_DIR not in sys.path:
    sys.path.append(BLUEPRINT_DIR)

try:
    from structure_blueprint import TESTS_REGISTRY
except ImportError:
    print(f"❌ ERROR: Could not find structure_blueprint.py in {BLUEPRINT_DIR}")
    sys.exit(1)

def align_tests_structure(root_path):
    print(f"--- ALIGNING TESTS WITH SOVEREIGN LAW ---")
    tests_root = os.path.join(root_path, "tests")

    for category, sub_folders in TESTS_REGISTRY.items():
        category_path = os.path.join(tests_root, category)
        
        # Ensure Level 2 (unit, integration, fixtures)
        ensure_dir_structure(category_path)

        for sub in sub_folders:
            # Ensure Level 3 (agentic_core, apps_rg, workflow_tests, etc.)
            sub_path = os.path.join(category_path, sub)
            ensure_dir_structure(sub_path)
            
            # Special Case: If it's a code-mirror (like agentic_core), 
            # we want to go even deeper to match the L2 departments.
            if sub in ["agentic_core", "apps_rg", "apps_lic", "apps_shared"]:
                # You can add logic here to mirror L2 folders if you want 
                # maximum precision (e.g., tests/unit/agentic_core/L1_cognition)
                pass

def ensure_dir_structure(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"✅ CREATED: {path}")
    
    # Python needs __init__.py to recognize the directory as a package
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# Sovereign Test Module\n")
        print(f"✅ ADDED __init__.py: {path}")
            
    # Git needs .gitkeep to track the folder if it's empty
    gitkeep = os.path.join(path, ".gitkeep")
    if not os.path.exists(gitkeep):
        with open(gitkeep, 'w') as f:
            f.write("")

if __name__ == "__main__":
    PROJECT_ROOT = "C:/Git/Agentic-Workflow"
    align_tests_structure(PROJECT_ROOT)
    print("\n✅ TEST ALIGNMENT COMPLETE. Run your Gatekeeper to confirm.")
