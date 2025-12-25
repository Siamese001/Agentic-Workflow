import os
import re
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
APPS = [ROOT / "apps_rg", ROOT / "apps_lic", ROOT / "apps_shared"]

# [THE BRIDGE MAP] Updating App imports to the new P1_core depth
# GRAVITY FIX: Removed direct imports from L1-L5 layers (utils cannot import upward)
REWIRE_MAP = [
    # Special sub-folders that got moved (utils can only reference peer utils/runtime)
    (r"from agentic_core\.utils\.", "from agentic_core.utils.P1_core."),
]

def rebuild_bridges():
    print("[*] REBUILDING APP-TO-CORE BRIDGES...")
    fixed_count = 0

    for app_dir in APPS:
        if not app_dir.exists(): continue
        for py_file in app_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original = content
                for pattern, sub in REWIRE_MAP:
                    content = re.sub(pattern, sub, content)
                
                if content != original:
                    py_file.write_text(content, encoding='utf-8')
                    print(f"  [✓] Bridged: {py_file.relative_to(ROOT)}")
                    fixed_count += 1
            except Exception as e:
                print(f"  [!] Failed {py_file.name}: {e}")

    print(f"\n[OK] BRIDGES REBUILT. {fixed_count} app-side files synced with the Sovereign Core.")

if __name__ == "__main__":
    rebuild_bridges()
