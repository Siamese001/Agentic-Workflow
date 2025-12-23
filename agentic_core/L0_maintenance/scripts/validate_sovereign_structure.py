"""
SOVEREIGN STRUCTURE VALIDATOR
Enforces the 3-level depth law for agentic architecture.
"""
import os
import sys

# --- THE IMPORT FIX ---
# We need to add the deep config path so Python can see the blueprint
BLUEPRINT_DIR = r"C:/Git/Agentic-Workflow/agentic_core/config/P1_core"
if BLUEPRINT_DIR not in sys.path:
    sys.path.append(BLUEPRINT_DIR)

try:
    from structure_blueprint import AGENTIC_CORE_REGISTRY, APP_TERRITORY_REGISTRY, TESTS_REGISTRY
except ImportError:
    print(f"❌ ERROR: Could not find structure_blueprint.py in {BLUEPRINT_DIR}")
    sys.exit(1)

def check_sovereign_law(root_path):
    violations = []

    # 1. Check Core (Forced Depth 3)
    # This validates that your Brain has all its specialized rooms
    core_path = os.path.join(root_path, "agentic_core")
    for l2, l3_list in AGENTIC_CORE_REGISTRY.items():
        for l3 in l3_list:
            path = os.path.join(core_path, l2, l3)
            if not os.path.exists(path):
                violations.append(f"MISSING CORE DEPTH: agentic_core/{l2}/{l3}")

    # 2. Check Apps (Forced Depth 3)
    # This ensures your territories haven't reverted to a flat structure
    for app, l2_dict in APP_TERRITORY_REGISTRY.items():
        for l2, l3_list in l2_dict.items():
            for l3 in l3_list:
                path = os.path.join(root_path, app, l2, l3)
                if not os.path.exists(path):
                    violations.append(f"MISSING APP DEPTH: {app}/{l2}/{l3}")

    # 3. Check Tests (Forced Depth 2/3 as defined)
    # Mirrors the code structure so the 'Judge' stays organized
    for l2, l3_list in TESTS_REGISTRY.items():
        for l3 in l3_list:
            path = os.path.join(root_path, "tests", l2, l3)
            if not os.path.exists(path):
                violations.append(f"MISSING TEST DEPTH: tests/{l2}/{l3}")

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
