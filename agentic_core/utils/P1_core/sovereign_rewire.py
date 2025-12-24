import os
import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# [REWIRE MAP] Mapping old "flat" paths to new "Depth-4" absolute paths
REWIRE_RULES = [
    (r"from agentic_core\.utils import", "from agentic_core.utils.P1_core import"),
    (r"from agentic_core\.memory import", "from agentic_core.memory.P1_core import"),
]

def rewire_synapses():
    print("[*] STARTING GLOBAL SYNAPTIC REWIRE...")
    fixed_count = 0

    # We scan everything: core, apps, and even the validator scripts
    for py_file in ROOT.rglob("*.py"):
        if "sovereign_rewire" in py_file.name: continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            original = content
            
            for pattern, replacement in REWIRE_RULES:
                content = re.sub(pattern, replacement, content)
            
            # Additional check: Fix "from .." relative imports that are now too shallow
            # This is a heuristic fix for files that moved into P1_core
            if "P1_core" in str(py_file):
                content = content.replace("from ..", "from agentic_core.")

            if content != original:
                py_file.write_text(content, encoding='utf-8')
                print(f"  [✓] Rewired: {py_file.relative_to(ROOT)}")
                fixed_count += 1
        except Exception as e:
            print(f"  [!] Failed {py_file.name}: {e}")

    print(f"\n[OK] REWIRE COMPLETE. {fixed_count} files reconnected to the Sovereign Brain.")

if __name__ == "__main__":
    rewire_synapses()
