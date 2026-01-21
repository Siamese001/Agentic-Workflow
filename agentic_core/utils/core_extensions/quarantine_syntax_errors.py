from __future__ import annotations

import ast

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
)

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR
quarantine: Any = ROOT / "quarantine_syntax_errors"


def quarantine_all_broken() -> Any:
    """Brief description of functionality and purpose."""
    print("[*] QUARANTINE: Scanning for all syntax-broken files...")
    QUARANTINE.mkdir(exist_ok=True)
    quarantined: Any = 0
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files

    for py_file in get_python_files(CORE):
        try:
            content: Any = py_file.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError:
            try:
                dest: Any = QUARANTINE / py_file.name
                counter: Any = 1
                while dest.exists():
                    dest: Any = QUARANTINE / f"{py_file.stem}_{counter}{py_file.suffix}"
                    counter += 1
                shutil.move(str(py_file), str(dest))
                print(f"  [✓] Quarantined: {py_file.relative_to(CORE)}")
                quarantined += 1
            except Exception as e:
                print(f"  [X] Failed to quarantine {py_file.name}: {e}")
        except Exception as e:
            print(f"  [!] Skipped {py_file.name}: {e}")
    print(f"\n[OK] QUARANTINE COMPLETE. {quarantined} broken files isolated.")
    print(f"    Files moved to: {QUARANTINE}")


if __name__ == "__main__":
    quarantine_all_broken()
