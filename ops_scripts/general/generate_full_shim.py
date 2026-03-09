"""Generate a complete monolith shim that re-exports ALL names from the modular package."""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

ROOT = get_validated_project_root()
MOD_DIR = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint"
TARGET = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint_config.py"


def collect_public_names() -> dict[str, list[str]]:
    by_module: dict[str, list[str]] = {}
    for f in sorted(MOD_DIR.glob("*.py")):
        if f.name == "__init__.py":
            continue
        src = f.read_text(encoding="utf-8")
        tree = ast.parse(src)
        names: list[str] = []
        for node in ast.iter_child_nodes(tree):
            name = None
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and not t.id.startswith("_"):
                        name = t.id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if not node.target.id.startswith("_"):
                    name = node.target.id
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    name = node.name
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    name = node.name
            if name and name not in names:
                names.append(name)
        by_module[f.stem] = sorted(set(names))
    return by_module


def generate_shim(by_module: dict[str, list[str]]) -> str:
    parts: list[str] = []
    parts.append('"""')
    parts.append("Structure Blueprint Config - Backward Compatible Shim.")
    parts.append("")
    parts.append("SSOT is now: agentic_core.L5_safety.config.structure_blueprint/")
    parts.append("This file re-exports all public names for backward compatibility.")
    parts.append("All 197+ existing importers will continue to work unchanged.")
    parts.append("")
    parts.append("DO NOT add new definitions here. Add them to the modular package instead.")
    parts.append('"""')
    parts.append("# noqa: F401 — re-exports for backward compatibility")
    parts.append("")
    parts.append("from __future__ import annotations")
    parts.append("")

    module_order = [
        "ssot",
        "territories",
        "classification",
        "semantics",
        "artifacts",
        "derived",
        "governance",
    ]
    all_names: list[str] = []

    for mod in module_order:
        names = by_module.get(mod, [])
        if not names:
            continue
        parts.append(f"from agentic_core.L5_safety.config.structure_blueprint.{mod} import (  # noqa: F401")
        for n in sorted(names):
            parts.append(f"    {n},")
            all_names.append(n)
        parts.append(")")
        parts.append("")

    # __all__
    parts.append("")
    parts.append("__all__ = [")
    for n in sorted(set(all_names)):
        parts.append(f'    "{n}",')
    parts.append("]")
    parts.append("")

    return "\n".join(parts)


def main() -> None:
    by_module = collect_public_names()
    total = sum(len(v) for v in by_module.values())
    print(f"Collected {total} public names across {len(by_module)} modules")

    shim = generate_shim(by_module)
    TARGET.write_text(shim, encoding="utf-8")
    print(f"Wrote shim: {len(shim.splitlines())} lines")

    ast.parse(shim)
    print("Syntax OK")


if __name__ == "__main__":
    main()
