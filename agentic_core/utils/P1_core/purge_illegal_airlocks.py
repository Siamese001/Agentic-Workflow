import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

ROOT_DIR = Path("C:/Git/Agentic-Workflow/agentic_core")

def purge_illegal_airlocks():
    print("[*] SOVEREIGN DEEP-CLEAN: Purging Illegal Airlocks...")
    deleted_count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file == "__init__.py":
                full_path = Path(root) / file
                rel_path = full_path.relative_to(ROOT_DIR)
                parts = rel_path.parts
                
                # Depth 1: agentic_core/__init__.py (Allowed)
                # Depth 2: agentic_core/Layer/__init__.py (Allowed)
                # Depth 3: agentic_core/Layer/Stage/__init__.py (Allowed)
                # Depth 4+: Anything deeper or at odd levels is a violation
                
                depth = len(parts)
                
                # In our Depth-4 mandate (Layer/Stage/File):
                # Parts: ('Layer', '__init__.py') -> Depth 2 (Legal)
                # Parts: ('Layer', 'Stage', '__init__.py') -> Depth 3 (Legal)
                
                if depth > 3 or (depth == 1 and rel_path.name == "__init__.py"):
                    # This captures the Depth 3 violations (knowledge/__init__.py) 
                    # and Depth 5+ (L1_cognition/P1_core/P1_retrieve/__init__.py)
                    try:
                        os.remove(full_path)
                        print(f"  [X] Purged: {rel_path}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"  [!] Failed to delete {rel_path}: {e}")

    print(f"\n[OK] DEEP-CLEAN COMPLETE. {deleted_count} illegal airlocks removed.")

if __name__ == "__main__":
    purge_illegal_airlocks()