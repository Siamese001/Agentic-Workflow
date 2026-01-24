from __future__ import annotations

"""Move remaining shallow files to proper depth."""
import shutil
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / "agentic_core"


def move_remaining() -> Any:
    """Move remaining depth 3 files to P1_core."""
    print("[*] MOVING REMAINING SHALLOW FILES...")
    moved: Any = 0
    knowledge_dir: Any = CORE / "knowledge"
    if knowledge_dir.exists():
        stage: Any = knowledge_dir / "P1_core"
        stage.mkdir(exist_ok=True)
        (stage / "__init__.py").write_text('"""Stage module."""\n')
        # Phase 6.8: Use ssot_discovery instead of glob
        from agentic_core.utils.ssot_discovery import get_python_files

        for f in get_python_files(knowledge_dir):
            if f.name != "__init__.py" and f.parent == knowledge_dir:
                target: Any = stage / f.name
                if not target.exists():
                    shutil.move(str(f), str(target))
                    print(f"  [✓] Moved: {f.relative_to(CORE)}")
                    moved += 1
    thought_nodes: Any = CORE / "L1_cognition" / "thought_engine"
    if thought_nodes.exists():
        stage: Any = thought_nodes / "P1_core"
        stage.mkdir(exist_ok=True)
        (stage / "__init__.py").write_text('"""Stage module."""\n')
        # Phase 6.8: Use ssot_discovery instead of glob
        from agentic_core.utils.ssot_discovery import get_python_files

        for f in get_python_files(thought_nodes):
            if f.name != "__init__.py" and f.parent == thought_nodes:
                target: Any = stage / f.name
                if not target.exists():
                    shutil.move(str(f), str(target))
                    print(f"  [✓] Moved: {f.relative_to(CORE)}")
                    moved += 1
    print(f"\n[OK] Moved {moved} files")


if __name__ == "__main__":
    move_remaining()
