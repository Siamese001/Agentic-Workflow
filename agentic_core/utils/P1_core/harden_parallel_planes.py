import os
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow/agentic_core")
THOUGHTS = ROOT / "L1_cognition" / "thought_engine"
KNOWLEDGE = ROOT / "knowledge" # You mentioned this didn't exist, let's birth it correctly

def harden_parallel_planes():
    print("[*] HARDENING PARALLEL EXECUTION PLANES...")

    # 1. Properly Stage L1_cognition/thought_engine (formerly L2_thought_nodes)
    if THOUGHTS.exists():
        # Move any files sitting directly in thought_engine to a P1 stage
        stage_path = THOUGHTS / "P1_reasoning"
        stage_path.mkdir(parents=True, exist_ok=True)
        (stage_path / "__init__.py").write_text('"""L1_cognition.thought_engine.P1: Core Reasoning Nodes"""\n')
        
        moved = 0
        for item in THOUGHTS.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                shutil.move(str(item), str(stage_path / item.name))
                print(f"  [>] Deep Thought Staged: {item.name} -> P1_reasoning")
                moved += 1
        print(f"  [✓] L1_cognition/thought_engine now Depth-4 compliant ({moved} files).")

    # 2. Birth the Knowledge Layer (if that's the intended Level 0 path)
    if not KNOWLEDGE.exists():
        print(f"  [!] Creating Knowledge Plane at {KNOWLEDGE.relative_to(ROOT.parent)}")
        KNOWLEDGE.mkdir(parents=True, exist_ok=True)
        (KNOWLEDGE / "__init__.py").write_text('"""Knowledge Plane: RAG & Memory"""\n')
        
        # Create the mandatory Stage
        stage_path = KNOWLEDGE / "P1_retrieval"
        stage_path.mkdir(parents=True, exist_ok=True)
        (stage_path / "__init__.py").write_text('"""Knowledge.P1: Retrieval Systems"""\n')
        print("  [✓] Knowledge Plane born and Depth-4 compliant.")

if __name__ == "__main__":
    harden_parallel_planes()
