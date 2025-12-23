import os
import ast
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

def audit_gravity():
    print("[*] STARTING FINAL GRAVITY AUDIT...")
    leaks = []

    # Scan all Python files in the Sovereign Core
    for py_file in CORE.rglob("*.py"):
        if py_file.name == "__init__.py" or "legacy" in str(py_file):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                # Check for 'import apps_rg...'
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(x in alias.name for x in ["apps_rg", "apps_lic", "apps_shared"]):
                            leaks.append((py_file.relative_to(ROOT), f"Direct: {alias.name}"))
                
                # Check for 'from apps_rg import ...'
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(x in node.module for x in ["apps_rg", "apps_lic", "apps_shared"]):
                        leaks.append((py_file.relative_to(ROOT), f"From: {node.module}"))
        
        except Exception as e:
            print(f"  [!] Audit Failed for {py_file.name}: {e}")

    if not leaks:
        print("\n[SUCCESS] Gravity is 100% Pure. No downstream leaks detected.")
    else:
        print(f"\n[!] ALERT: Found {len(leaks)} Gravity Violations:")
        for file, reason in leaks:
            print(f"  [X] {file} -> {reason}")
    
    return leaks

if __name__ == "__main__":
    audit_gravity()
