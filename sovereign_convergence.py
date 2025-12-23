import os
import shutil
import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path.cwd()
CORE = ROOT / "agentic_core"

# [THE MAP] Legacy Folder -> Sovereign Destination (Depth 4)
# We use P/S prefixes because they are auto-authorized by your recent patch.
MIGRATION_MAP = {
    # Move 'agents' to Execution layer
    "agentic_core/agents": "agentic_core/L2_execution/P4_agents",
    
    # Move 'state' to L4 State layer
    "agentic_core/state": "agentic_core/L4_state/S1_store",
    
    # Move 'domain' to Cognition layer
    "agentic_core/domain": "agentic_core/L1_cognition/P2_domain",
    
    # Move 'infra' (if exists) to L3 Vitality
    "agentic_core/infra": "agentic_core/L3_orchestration/S3_vitality",
    
    # Move 'tools' to Execution layer
    "agentic_core/tools": "agentic_core/L2_execution/P2_tools"
}

def align_territory():
    print("[*] STARTING SOVEREIGN CONVERGENCE...")
    
    # 1. PHYSICAL MOVE
    for source, target in MIGRATION_MAP.items():
        src_path = ROOT / source
        dest_path = ROOT / target
        
        if src_path.exists():
            print(f"  [>] Migrating Drift: {source} -> {target}")
            dest_path.mkdir(parents=True, exist_ok=True)
            
            # Move all files from source to dest
            for item in src_path.iterdir():
                if item.is_file():
                    shutil.move(str(item), str(dest_path / item.name))
                elif item.is_dir():
                    # If it's a directory, move it whole
                    shutil.move(str(item), str(dest_path / item.name))
            
            # Remove the empty legacy shell
            try:
                src_path.rmdir()
                print(f"      [x] Removed legacy shell: {source}")
            except OSError:
                print(f"      [!] Warning: Could not remove {source} (not empty?)")
        else:
            print(f"  [-] Skipped: {source} (Not found)")

    # 2. IMPORT REFACTORING (The "Synaptic Rewiring")
    print("\n[*] REWIRING IMPORTS...")
    
    # Regex replacements for the moves above
    replacements = [
        (r"from agentic_core\.agents", "from agentic_core.L2_execution.P4_agents"),
        (r"import agentic_core\.agents", "import agentic_core.L2_execution.P4_agents"),
        
        (r"from agentic_core\.state", "from agentic_core.L4_state.S1_store"),
        (r"import agentic_core\.state", "import agentic_core.L4_state.S1_store"),
        
        (r"from agentic_core\.domain", "from agentic_core.L1_cognition.P2_domain"),
        (r"import agentic_core\.domain", "import agentic_core.L1_cognition.P2_domain"),
        
        (r"from agentic_core\.tools", "from agentic_core.L2_execution.P2_tools"),
    ]

    count = 0
    for py_file in ROOT.rglob("*.py"):
        if "legacy_code" in str(py_file) or "env" in str(py_file): 
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for old, new in replacements:
                content = re.sub(old, new, content)
            
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  [✓] Rewired: {py_file.relative_to(ROOT)}")
                count += 1
        except Exception as e:
            print(f"  [!] Failed to process {py_file}: {e}")

    print(f"\n[OK] CONVERGENCE COMPLETE. {count} files rewired.")
    print("    [!] NEXT: Run 'python canon_validator_agentic_v2.py --target agentic_core'")

if __name__ == "__main__":
    align_territory()
