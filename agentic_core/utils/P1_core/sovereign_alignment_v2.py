import os
import shutil
import re
from pathlib import Path

ROOT = Path.cwd()
CORE = ROOT / "agentic_core"

# [THE CORRECTED MAP] Aligning Physical Move Paths with Import Rewiring
MIGRATION_MAP = {
    "agentic_core/engines": "agentic_core/L2_execution/P3_engines",
    "agentic_core/interfaces": "agentic_core/L1_cognition/P1_interfaces",
    "agentic_core/security": "agentic_core/L5_safety/P4_security",
    "agentic_core/agentic_workflow": "agentic_core/L3_orchestration/P5_workflow"
}

def flush_and_align():
    print("[*] STARTING SOVEREIGN ALIGNMENT V2 & CIRCULAR FLUSH...")
    
    # 1. Physical Migration of the remaining Depth 2/3 folders
    for source, target in MIGRATION_MAP.items():
        src_path = ROOT / source
        dest_path = ROOT / target
        if src_path.exists():
            dest_path.mkdir(parents=True, exist_ok=True)
            for item in src_path.iterdir():
                dest_item = dest_path / item.name
                if dest_item.exists():
                    print(f"      [!] Skipping {item.name} (already exists at destination)")
                    continue
                shutil.move(str(item), str(dest_item))
            try:
                src_path.rmdir()
                print(f"  [>] Migrated Drift: {source} -> {target}")
            except OSError:
                print(f"  [!] Could not remove {source} (not empty)")
        else:
            print(f"  [-] Skipped: {source} (not found)")

    # 2. The Circular Flush: Stripping __init__.py files to break loops
    print("\n[*] FLUSHING __init__.py FILES...")
    flush_count = 0
    for init_file in CORE.rglob("__init__.py"):
        print(f"  [!] Flushing: {init_file.relative_to(ROOT)}")
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(f'"""Sovereign Layer: {init_file.parent.name}"""\n')
        flush_count += 1
    print(f"  [OK] Flushed {flush_count} __init__.py files")

    # 3. Correcting the Synaptic Break
    print("\n[*] REWIRING IMPORTS...")
    rewire = [
        # FIX PREVIOUS MISTAKE: Analysis/Agents live in L2, not L5
        (r"agentic_core\.L5_safety\.P1_red_team\.analysis", "agentic_core.L2_execution.tool_registry.analysis"),
        
        # NEW MAPPINGS for the folders we just moved
    ]

    count = 0
    for py_file in ROOT.rglob("*.py"):
        if any(p in str(py_file) for p in ["legacy_code", ".venv", "data"]): 
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            for old, new in rewire:
                new_content = re.sub(old, new, new_content)
            
            if new_content != content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  [✓] Rewired: {py_file.name}")
                count += 1
        except Exception as e:
            print(f"  [!] Failed to process {py_file}: {e}")

    print(f"\n[OK] CONVERGENCE V2 COMPLETE. {count} files rewired.")
    print("    [!] NEXT: Run 'python canon_validator_agentic_v2.py --target agentic_core'")

if __name__ == "__main__":
    flush_and_align()
