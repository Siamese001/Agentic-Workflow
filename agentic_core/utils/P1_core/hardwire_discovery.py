import os
import re
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow/agentic_core")

# THE MAP: Redirecting legacy discovery paths to the new P1_core reality
PATH_REDIRECTS = {
    r"from agentic_core\.agents": "from agentic_core.L2_execution.P4_agents",
    r"from agentic_core\.interfaces": "from agentic_core.L1_cognition.P1_interfaces",
    r"from L4_state": "from agentic_core.L4_state.P1_core",
    r"from core import": "from agentic_core.L1_cognition.P1_core import",
    r"import canon_agents_core": "from agentic_core.L2_execution.P4_agents import base as canon_agents_core",
}

def hardwire_discovery():
    print("[*] HARDWIRING DISCOVERY SYNAPSES...")
    fixed = 0
    
    for py_file in ROOT.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            original = content
            
            # 1. Apply the redirects
            for old, new in PATH_REDIRECTS.items():
                content = re.sub(old, new, content)
            
            # 2. Fix the "Missing Enum" ghost (Common in _types.py files)
            if "_types.py" in py_file.name and "Enum" in content and "from enum import Enum" not in content:
                content = "from enum import Enum\n" + content
            
            if content != original:
                py_file.write_text(content, encoding='utf-8')
                print(f"  [✓] Synapse Anchored: {py_file.relative_to(ROOT)}")
                fixed += 1
        except Exception as e:
            pass

    print(f"\n[OK] DISCOVERY FIXED. {fixed} files anchored.")

if __name__ == "__main__":
    hardwire_discovery()
