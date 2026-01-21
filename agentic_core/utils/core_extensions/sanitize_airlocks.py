from __future__ import annotations

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
)

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR


def sanitize_file(file_path: Any) -> Any:
    """Checks for common syntax errors and forces closure of brackets."""
    with open(file_path, encoding="utf-8") as f:
        lines: Any = f.readlines()
    modified: Any = False
    new_lines: Any = []
    for line in lines:
        if "\\" in line and (not line.strip().endswith("\\")):
            parts: Any = line.split("\\")
            line: Any = parts[0] + "\\" + "\n"
            modified: Any = True
        new_lines.append(line)
    content: Any = "".join(new_lines)
    for opening, closing in [("{", "}"), ("[", "]"), ("(", ")")]:
        if content.count(opening) > content.count(closing):
            print(f"  [!] Closing unsealed {opening} in {file_path.name}")
            content += f"\n{closing}\n"
            modified: Any = True
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def run_sanitizer() -> Any:
    """Brief description of functionality and purpose."""
    print("[*] SOVEREIGN SANITIZER: Flushing the Synaptic Loops...")
    count: Any = 0
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files

    targets: Any = [
        f for f in get_python_files(CORE) if f.name == "__init__.py" or "_impl" in f.name
    ]
    for target in targets:
        try:
            if sanitize_file(target):
                print(f"  [✓] Sanitized: {target.relative_to(CORE)}")
                count += 1
        except Exception as e:
            print(f"  [X] Failed to sanitize {target.name}: {e}")
    print(f"\n[OK] SANITIZATION COMPLETE. {count} files flushed.")
    print("[!] ACTION: You can now restart the validator without the 'Resilient Mutation' loop.")


if __name__ == "__main__":
    run_sanitizer()
