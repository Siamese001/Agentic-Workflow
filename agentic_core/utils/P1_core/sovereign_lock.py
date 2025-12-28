import os
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
CORE = ROOT / "agentic_core"

def enforce_gravity():
    """Ensures no file in agentic_core reaches 'down' into apps."""
    print("[*] ENFORCING GRAVITY...")
    violations = 0
    forbidden = ["apps_rg", "apps_lic", "apps_shared"]

    for py_file in CORE.rglob("*.py"):
        if py_file.name == "__init__.py": continue
        
        content = py_file.read_text(encoding='utf-8')
        for f in forbidden:
            if f in content:
                # Regex to find actual import statements, not just mentions
                if re.search(fr"^(import\s+{f}|from\s+{f})", content, re.M):
                    print(f"  [X] GRAVITY BREACH: {py_file.relative_to(ROOT)} imports {f}!")
                    violations += 1
    return violations

def enforce_depth():
    """Ensures every file is EXACTLY at Depth 4. No shallower, no deeper."""
    print("[*] ENFORCING ABSOLUTE DEPTH-4 MANDATE...")
    violations = 0
    
    for py_file in CORE.rglob("*.py"):
        if py_file.name == "__init__.py": continue
        
        # Parts relative to agentic_core
        # Target: Layer/Stage/File.py (Length 3)
        parts = py_file.relative_to(CORE).parts
        
        if len(parts) != 3:
            # We found a 'Tunnel' (too deep) or a 'Shallow' (too high)
            depth_status = "SHALLOW" if len(parts) < 3 else "TUNNEL"
            print(f"  [X] {depth_status} VIOLATION: {py_file.relative_to(ROOT)}")
            print(f"      Actual: {len(parts)+1} | Required: 4")
            violations += 1
            
    return violations

def check_airlocks():
    """Ensures __init__.py files are minimal (under 50 lines)."""
    print("[*] CHECKING AIRLOCK HYGIENE...")
    violations = 0
    
    for init_file in CORE.rglob("__init__.py"):
        lines = init_file.read_text(encoding='utf-8').splitlines()
        if len(lines) > 50:
            print(f"  [X] HEAVY AIRLOCK: {init_file.relative_to(ROOT)} has {len(lines)} lines. Keep it lean!")
            violations += 1
    return violations

if __name__ == "__main__":
    v1 = enforce_gravity()
    v2 = enforce_depth()
    v3 = check_airlocks()
    
    total = v1 + v2 + v3
    if total > 0:
        print(f"\n[BLOCK] {total} Sovereignty Violations detected. Fix these before committing.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Sovereign Core is locked and compliant. Move forward.")
        sys.exit(0)
