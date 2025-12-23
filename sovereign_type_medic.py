import os
import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# [TYPE MAPPING] Cleaning up the "Shouting" types to standard Python lowercase
TYPE_FIXES = [
    (r":\s*STR\b", ": str"),
    (r":\s*FLOAT\b", ": float"),
    (r":\s*BOOL\b", ": bool"),
    (r"->\s*STR\b", "-> str"),
    (r"->\s*FLOAT\b", "-> float"),
    (r"->\s*BOOL\b", "-> bool"),
]

# [PEER IMPORT ALIGNMENT] Forcing relative peer imports to Absolute Sovereign Paths
# This specifically fixes the "name not defined" issues for cross-file types
IMPORT_ALIGNMENTS = [
    # Example: Fixes CapabilityAnalyzer looking for its Gap types
    (r"from \.capability_analyzer_types import", "from agentic_core.L1_cognition.planning.capability_analyzer_types import"),
    # Fixes Health Metrics in L3
    (r"from \.autonomic_monitor_types import", "from agentic_core.L3_orchestration.health.autonomic_monitor_types import"),
    # Fixes Permissions in L3
    (r"from \.agent_permissions_types import", "from agentic_core.L3_orchestration.security.agent_permissions_types import"),
]

def run_type_medic():
    print("[*] SOVEREIGN TYPE MEDIC: Initiating Clean Sweep...")
    modified_files = 0

    for py_file in CORE.rglob("*.py"):
        if py_file.name == "__init__.py" or "legacy" in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            
            # 1. Apply Type Hint Fixes
            for pattern, sub in TYPE_FIXES:
                content = re.sub(pattern, sub, content)

            # 2. Apply Import Alignments
            for pattern, sub in IMPORT_ALIGNMENTS:
                content = re.sub(pattern, sub, content)

            if content != original:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  [✓] Healed: {py_file.relative_to(CORE)}")
                modified_files += 1

        except Exception as e:
            print(f"  [!] Failed to treat {py_file.name}: {e}")

    print(f"\n[OK] MEDIC COMPLETE. {modified_files} files sanitized.")
    print("    [!] NEXT: Run 'python mission_start.py' to verify the full chain.")

if __name__ == "__main__":
    run_type_medic()
