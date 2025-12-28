import os
from pathlib import Path

CORE = Path("C:/Git/Agentic-Workflow/agentic_core")

def flush_airlocks():
    print("[*] PERFORMING AIRLOCK FLUSH...")
    for init_file in CORE.rglob("__init__.py"):
        # We strip the 'heavy' logic to stop the auto-loading death spiral
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(f'"""Airlock: {init_file.parent.name}"""\n')
        print(f"  [✓] Flushed: {init_file.relative_to(CORE.parent)}")

if __name__ == "__main__":
    flush_airlocks()
