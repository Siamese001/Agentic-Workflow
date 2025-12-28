import os
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow/agentic_core")

def collapse_tunnels():
    print("[*] COLLAPSING DIRECTORY TUNNELS...")
    
    for root, dirs, files in os.walk(ROOT, topdown=False):
        for name in dirs:
            # If a folder contains a subfolder with the EXACT same name
            # e.g., P2_inspect/P2_inspect
            parent_path = Path(root) / name
            child_path = parent_path / name
            
            if child_path.exists() and child_path.is_dir():
                print(f"  [!] Found Tunnel: {parent_path.name}/{child_path.name}")
                
                # Move everything from child to parent
                for item in child_path.iterdir():
                    shutil.move(str(item), str(parent_path / item.name))
                
                # Delete the now-empty child
                child_path.rmdir()
                print(f"  [✓] Tunnel Collapsed.")

if __name__ == "__main__":
    collapse_tunnels()
