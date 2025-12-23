import os
import shutil
import re
from pathlib import Path

ROOT = Path.cwd()
CORE = ROOT / "agentic_core"

# [THE CORRECT MAP] Aligning Move Paths with Import Paths
MIGRATION_MAP = {
    "agentic_core/engines": "agentic_core/L2_execution/P3_engines",
    "agentic_core/interfaces": "agentic_core/L1_cognition/P1_interfaces",
    "agentic_core/security": "agentic_core/L5_safety/P4_security",
    "agentic_core/agentic_workflow": "agentic_core/L3_orchestration/P5_workflow"
}

def fix_alignment():
    print("[*] STARTING SOVEREIGN ALIGNMENT V2...")
    
    # 1. Physical Migration
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
                print(f"  [>] Migrated: {source} -> {target}")
            except OSError:
                print(f"  [!] Could not remove {source} (not empty)")
        else:
            print(f"  [-] Skipped: {source} (not found)")

    # 2. Correcting the Synaptic Break (Fixing the L2 vs L5 mistake)
    rewire = [
        # Fix the previous mistake: point imports to where agents ACTUALLY are
        (r"agentic_core\.L5_safety\.P1_red_team\.analysis", "agentic_core.L2_execution.P4_agents.analysis"),
        (r"from agentic_core\.agents", "from agentic_core.L2_execution.P4_agents"),
        
        # New Mappings
        (r"from agentic_core\.engines", "from agentic_core.L2_execution.P3_engines"),
        (r"from agentic_core\.interfaces", "from agentic_core.L1_cognition.P1_interfaces"),
        (r"from agentic_core\.security", "from agentic_core.L5_safety.P4_security"),
        (r"from agentic_core\.agentic_workflow", "from agentic_core.L3_orchestration.P5_workflow"),
    ]

    count = 0
    for py_file in ROOT.rglob("*.py"):
        if "legacy_code" in str(py_file) or ".venv" in str(py_file): 
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
                print(f"  [✓] Rewired: {py_file.relative_to(ROOT)}")
                count += 1
        except Exception as e:
            print(f"  [!] Failed to process {py_file}: {e}")

    print(f"\n[OK] ALIGNMENT V2 COMPLETE. {count} files rewired.")
    print("    [!] NEXT: Run 'python canon_validator_agentic_v2.py --target agentic_core'")

if __name__ == "__main__":
    fix_alignment()
