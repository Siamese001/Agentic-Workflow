from __future__ import annotations

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import shutil
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

root: Any = Path("C:/Git/Agentic-Workflow/agentic_core")
thoughts: Any = ROOT / "L1_cognition" / "thought_engine"
knowledge: Any = ROOT / "knowledge"


def harden_parallel_planes() -> Any:
    """Brief description of functionality and purpose."""
    print("[*] HARDENING PARALLEL EXECUTION PLANES...")
    if THOUGHTS.exists():
        stage_path: Any = THOUGHTS / "P1_reasoning"
        stage_path.mkdir(parents=True, exist_ok=True)
        (stage_path / "__init__.py").write_text(
            '"""L1_cognition.thought_engine.P1: Core Reasoning Nodes"""\n'
        )
        moved: Any = 0
        for item in THOUGHTS.iterdir():
            if item.is_file() and item.suffix == ".py" and (item.name != "__init__.py"):
                shutil.move(str(item), str(stage_path / item.name))
                print(f"  [>] Deep Thought Staged: {item.name} -> P1_reasoning")
                moved += 1
        print(f"  [✓] L1_cognition/thought_engine now Depth-4 compliant ({moved} files).")
    if not KNOWLEDGE.exists():
        print(f"  [!] Creating Knowledge Plane at {KNOWLEDGE.relative_to(ROOT.parent)}")
        KNOWLEDGE.mkdir(parents=True, exist_ok=True)
        (KNOWLEDGE / "__init__.py").write_text('"""Knowledge Plane: RAG & Memory"""\n')
        stage_path: Any = KNOWLEDGE / "P1_retrieval"
        stage_path.mkdir(parents=True, exist_ok=True)
        (stage_path / "__init__.py").write_text('"""Knowledge.P1: Retrieval Systems"""\n')
        print("  [✓] Knowledge Plane born and Depth-4 compliant.")


if __name__ == "__main__":
    harden_parallel_planes()
