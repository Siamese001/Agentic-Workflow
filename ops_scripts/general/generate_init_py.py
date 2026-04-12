"""Generate the new __init__.py for the modular structure_blueprint package."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOD_DIR = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint"


def collect_public_names() -> dict[str, list[str]]:
    """Collect all public names from each modular file using AST."""
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
                    if isinstance(t, ast.Name) and (not t.id.startswith("_")):
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
            if name:
                names.append(name)
        by_module[f.stem] = sorted(set(names))
    return by_module


def generate_init(by_module: dict[str, list[str]]) -> str:
    """Generate __init__.py content."""
    parts: list[str] = []
    parts.append('"""')
    parts.append("Structure Blueprint Package - Modular SSOT (2026-02-08).")
    parts.append("")
    parts.append("This package is the Single Source of Truth for all structural configuration.")
    parts.append("The monolithic structure_blueprint_config.py is a backward-compatible shim")
    parts.append("that re-exports everything from this package.")
    parts.append("")
    parts.append("Modules:")
    parts.append("  ssot.py           - Core constants, path utilities, whitelists, flat enforcement")
    parts.append("  territories.py    - SOVEREIGN_TERRITORIES definition")
    parts.append("  classification.py - Suffix patterns, folder purity, naming rules")
    parts.append("  semantics.py      - AST signals, keyword affinity, agent/placement registries")
    parts.append("  artifacts.py      - File patterns, artifact routing, subfolder metadata")
    parts.append("  derived.py        - Derived registries (computed from territories)")
    parts.append("  governance.py     - Healing, mission, gravity, MCP operational config")
    parts.append('"""')
    parts.append("")
    parts.append("from __future__ import annotations")
    parts.append("")
    parts.append("# HOT imports - always loaded (ssot.py is minimal-cost)")
    parts.append("from agentic_core.L5_safety.config.structure_blueprint.ssot import (")
    for n in sorted(by_module.get("ssot", [])):
        parts.append(f"    {n},")
    parts.append(")")
    parts.append("")
    parts.append("# Territories - loaded eagerly (needed by most consumers)")
    parts.append("from agentic_core.L5_safety.config.structure_blueprint.territories import (")
    for n in sorted(by_module.get("territories", [])):
        parts.append(f"    {n},")
    parts.append(")")
    parts.append("")
    parts.append("")
    lazy_modules = ["classification", "semantics", "artifacts", "derived", "governance"]
    parts.append("# COLD imports - lazy loaded via __getattr__")
    parts.append("def __getattr__(name: str):")
    parts.append('    """Lazy load cold module exports on first access."""')
    for mod in lazy_modules:
        mod_names = by_module.get(mod, [])
        if not mod_names:
            continue
        names_set = "{" + ", ".join(f'"{n}"' for n in sorted(mod_names)) + "}"
        parts.append(f"    if name in {names_set}:")
        parts.append(f"        from agentic_core.L5_safety.config.structure_blueprint import {mod}")
        parts.append(f"        return getattr({mod}, name)")
        parts.append("")
    parts.append("    # ROOT_WHITELIST is lazy-computed from SOVEREIGN_TERRITORIES")
    parts.append('    if name == "ROOT_WHITELIST":')
    parts.append(
        "        from agentic_core.L5_safety.config.structure_blueprint.ssot import _get_root_whitelist"
    )
    parts.append("        return _get_root_whitelist()")
    parts.append("")
    parts.append('    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")')
    parts.append("")
    all_names: list[str] = []
    for mod_names in by_module.values():
        all_names.extend(mod_names)
    all_names = sorted(set(all_names))
    parts.append("")
    parts.append("__all__ = [")
    for n in all_names:
        parts.append(f'    "{n}",')
    parts.append("]")
    parts.append("")
    return "\n".join(parts)


def main() -> None:
    by_module = collect_public_names()
    total = sum(len(v) for v in by_module.values())
    print(f"Collected {total} public names across {len(by_module)} modules")
    content = generate_init(by_module)
    target = MOD_DIR / "__init__.py"
    target.write_text(content, encoding="utf-8")
    print(f"Wrote {target} ({len(content)} chars, {len(content.splitlines())} lines)")
    ast.parse(content)
    print("Syntax OK")


if __name__ == "__main__":
    main()
