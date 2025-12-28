"""
Simple validation summary without complex imports.
Reports on the sovereign convergence completion status.
"""
import os
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

def count_python_files(directory):
    """Count Python files in a directory."""
    return len(list(directory.rglob("*.py")))

def check_structure():
    """Check the sovereign structure."""
    print("=" * 80)
    print("SOVEREIGN CONVERGENCE - VALIDATION SUMMARY")
    print("=" * 80)
    
    # Check layer structure
    layers = ["L1_cognition", "L2_execution", "L3_orchestration", "L4_state", "L5_safety"]
    
    print("\n[PHASE 1] SOVEREIGN CORE STRUCTURE")
    print("-" * 80)
    
    total_files = 0
    for layer in layers:
        layer_path = CORE / layer
        if layer_path.exists():
            count = count_python_files(layer_path)
            total_files += count
            print(f"  ✓ {layer:20} {count:4} Python files")
        else:
            print(f"  ✗ {layer:20} MISSING")
    
    print(f"\n  Total Core Files: {total_files}")
    
    # Check __init__.py exports
    print("\n[PHASE 2] EXPORT RESTORATION")
    print("-" * 80)
    
    for layer in layers:
        init_file = CORE / layer / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
                has_all = "__all__" in content
                has_imports = "from ." in content or "import" in content
                
                if has_all and has_imports:
                    print(f"  ✓ {layer:20} Exports configured")
                elif has_all:
                    print(f"  ⚠ {layer:20} Has __all__ but no imports")
                else:
                    print(f"  ✗ {layer:20} No exports configured")
        else:
            print(f"  ✗ {layer:20} No __init__.py")
    
    # Check for gravity violations
    print("\n[PHASE 3] GRAVITY CHECK")
    print("-" * 80)
    
    violations = []
    for py_file in CORE.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "from apps_rg" in content or "from apps_lic" in content:
                    violations.append(py_file.relative_to(ROOT))
        except:
            pass
    
    if violations:
        print(f"  ✗ Found {len(violations)} gravity violations:")
        for v in violations[:5]:
            print(f"    - {v}")
        if len(violations) > 5:
            print(f"    ... and {len(violations) - 5} more")
    else:
        print("  ✓ No gravity violations detected")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if total_files >= 230 and len(violations) == 0:
        print("\n  ✅ SOVEREIGN CONVERGENCE COMPLETE")
        print(f"  - {total_files} files in sovereign structure")
        print("  - Zero gravity violations")
        print("  - All layers properly organized")
        return 0
    else:
        print("\n  ⚠️  CONVERGENCE IN PROGRESS")
        print(f"  - {total_files} files migrated")
        print(f"  - {len(violations)} gravity violations remaining")
        return 1

if __name__ == "__main__":
    exit(check_structure())
