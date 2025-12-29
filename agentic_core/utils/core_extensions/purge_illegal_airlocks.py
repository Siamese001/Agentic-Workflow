"""
Purge illegal __init__.py airlocks using SSOT depth requirements.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
from pathlib import Path

from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY

ROOT_DIR = Path("C:/Git/Agentic-Workflow/agentic_core")

# [SSOT] Get required depth for agentic_core from SOVEREIGN_REGISTRY
REQUIRED_DEPTH = SOVEREIGN_REGISTRY["agentic_core"]["depth"]

def purge_illegal_airlocks():
    print(f"[*] SOVEREIGN DEEP-CLEAN: Purging Illegal Airlocks (SSOT depth: {REQUIRED_DEPTH})...")
    deleted_count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file == "__init__.py":
                full_path = Path(root) / file
                rel_path = full_path.relative_to(ROOT_DIR)
                parts = rel_path.parts
                
                # [SSOT] __init__.py allowed at:
                # Depth 1: agentic_core/__init__.py (Allowed)
                # Depth 2: agentic_core/Layer/__init__.py (Allowed)
                # Depth 3: agentic_core/Layer/Stage/__init__.py (Allowed)
                # Depth > REQUIRED_DEPTH - 1: Violation
                
                depth = len(parts)
                
                # [SSOT] In our Depth-{REQUIRED_DEPTH} mandate (Layer/Stage/File):
                # Parts: ('Layer', '__init__.py') -> Depth 2 (Legal)
                # Parts: ('Layer', 'Stage', '__init__.py') -> Depth 3 (Legal)
                
                if depth > REQUIRED_DEPTH - 1 or (depth == 1 and rel_path.name == "__init__.py"):
                    try:
                        os.remove(full_path)
                        print(f"  [X] Purged: {rel_path}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"  [!] Failed to delete {rel_path}: {e}")

    print(f"\n[OK] DEEP-CLEAN COMPLETE. {deleted_count} illegal airlocks removed.")

if __name__ == "__main__":
    purge_illegal_airlocks()