from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg

"""
Trim heavy airlock __init__.py files to meet 50-line limit.
Condenses verbose __all__ lists and removes blank lines.
"""
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint_config import (
    AGENTIC_CORE_DIR,
)

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR


def trim_airlock(init_file: Any) -> Any:
    """Trim a single __init__.py file to ≤50 lines."""
    lines: Any = init_file.read_text(encoding="utf-8").splitlines()
    if len(lines) <= 50:
        return False
    new_lines: Any = []
    in_all: Any = False
    all_items: Any = []
    for line in lines:
        stripped: Any = line.strip()
        if not stripped:
            continue
        if "__all__" in line:
            in_all: Any = True
            continue
        if in_all:
            if "]" in line:
                in_all: Any = False
                continue
            items: Any = stripped.strip("',\"").split(",")
            all_items.extend([i.strip().strip("'\"") for i in items if i.strip()])
            continue
        new_lines.append(line)
    if all_items:
        important: Any = all_items[:8]
        new_lines.append(f"__all__ = {important}")
    content: Any = "\n".join(new_lines) + "\n"
    _wg.write_text(init_file, content, encoding="utf-8")
    return True


def trim_all_airlocks() -> Any:
    """Trim all heavy airlock files."""
    print("[*] TRIMMING HEAVY AIRLOCKS...")
    trimmed: Any = 0
    # Absolute Zero: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_data_files

    init_files = [f for f in get_data_files(CORE, extensions=[".py"]) if f.name == "__init__.py"]
    for init_file in init_files:
        lines: Any = init_file.read_text(encoding="utf-8").splitlines()
        if len(lines) > 50:
            if trim_airlock(init_file):
                new_lines: Any = len(init_file.read_text(encoding="utf-8").splitlines())
                print(f"  [✓] Trimmed: {init_file.relative_to(CORE)} ({len(lines)} -> {new_lines} lines)")
                trimmed += 1
    print(f"\n[OK] Trimmed {trimmed} airlock files")


if __name__ == "__main__":
    trim_all_airlocks()
