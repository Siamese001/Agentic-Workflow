"""
Apply extracted migration fragments to modular structure_blueprint files.

Reads each _migrate_*.py.fragment, adds needed imports, and appends to
the corresponding modular file.
"""

from __future__ import annotations

import os
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR


def _resolve_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / AGENTIC_CORE_DIR).exists():
            return candidate
    return Path(__file__).resolve().parents[2]


def _atomic_write(path: Path, content: str) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


ROOT = _resolve_root()
MOD_DIR = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint"
FRAG_DIR = ROOT / "data" / "freeze_reports"
EXTRA_IMPORTS: dict[str, list[str]] = {
    "ssot": ["import os", "import re", "from re import Pattern"],
    "artifacts": [],
    "semantics": [],
}
SEPARATOR = "\n\n# ============================================================================\n# MIGRATED FROM MONOLITH (structure_blueprint_config.py) — 2026-02-08\n# ============================================================================\n\n"


def add_imports_if_missing(content: str, imports: list[str]) -> str:
    """Add import lines after the existing imports if not already present."""
    lines = content.splitlines(True)
    last_import_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")) and (not stripped.startswith("from agentic_core")):
            last_import_idx = i
    existing = content
    missing = [imp for imp in imports if imp not in existing]
    if not missing:
        return content
    for imp in missing:
        lines.insert(last_import_idx + 1, imp + "\n")
        last_import_idx += 1
    return "".join(lines)


def append_fragment(module_name: str) -> None:
    """Append a migration fragment to its target modular file."""
    frag_path = FRAG_DIR / f"_migrate_{module_name}.py.fragment"
    target_path = MOD_DIR / f"{module_name}.py"
    if not FRAG_DIR.exists():
        print(f"  SKIP: fragment directory missing: {FRAG_DIR}")
        return
    if not frag_path.exists():
        print(f"  SKIP: {frag_path} not found")
        return
    if not target_path.exists():
        print(f"  SKIP: {target_path} not found (create it first)")
        return
    fragment = frag_path.read_text(encoding="utf-8")
    existing = target_path.read_text(encoding="utf-8")
    first_line = ""
    for line in fragment.splitlines():
        stripped = line.strip()
        if stripped and (not stripped.startswith("#")):
            first_line = stripped
            break
    if first_line and first_line in existing:
        print(f"  SKIP: {module_name}.py already contains fragment (idempotent)")
        return
    extra = EXTRA_IMPORTS.get(module_name, [])
    if extra:
        existing = add_imports_if_missing(existing, extra)
    result = existing.rstrip("\n") + SEPARATOR + fragment
    target_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(target_path, result)
    print(f"  OK: Appended {len(fragment)} chars to {module_name}.py")


def main() -> None:
    print("Applying migration fragments...")
    for module in ["ssot", "artifacts", "semantics"]:
        print(f"\n--- {module}.py ---")
        append_fragment(module)
    print("\n=== DONE ===")
    print("governance.py was already created as a new file.")
    print("Next: Update __init__.py and create monolith shim.")


if __name__ == "__main__":
    main()
