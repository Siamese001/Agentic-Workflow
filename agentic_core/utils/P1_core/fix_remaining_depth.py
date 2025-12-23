"""Move remaining shallow files to proper depth."""
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

def move_remaining():
    """Move remaining depth 3 files to P1_core."""
    print("[*] MOVING REMAINING SHALLOW FILES...")
    moved = 0
    
    # Move knowledge/l5_consolidated.py
    knowledge_dir = CORE / "knowledge"
    if knowledge_dir.exists():
        stage = knowledge_dir / "P1_core"
        stage.mkdir(exist_ok=True)
        (stage / "__init__.py").write_text('"""Stage module."""\n')
        
        for f in knowledge_dir.glob("*.py"):
            if f.name != "__init__.py":
                target = stage / f.name
                if not target.exists():
                    shutil.move(str(f), str(target))
                    print(f"  [✓] Moved: {f.relative_to(CORE)}")
                    moved += 1
    
    # Move L1_cognition/thought_engine files (formerly L2_thought_nodes)
    thought_nodes = CORE / "L1_cognition" / "thought_engine"
    if thought_nodes.exists():
        stage = thought_nodes / "P1_core"
        stage.mkdir(exist_ok=True)
        (stage / "__init__.py").write_text('"""Stage module."""\n')
        
        for f in thought_nodes.glob("*.py"):
            if f.name != "__init__.py":
                target = stage / f.name
                if not target.exists():
                    shutil.move(str(f), str(target))
                    print(f"  [✓] Moved: {f.relative_to(CORE)}")
                    moved += 1
    
    print(f"\n[OK] Moved {moved} files")

if __name__ == "__main__":
    move_remaining()
