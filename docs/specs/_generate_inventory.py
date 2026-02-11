"""AST-based inventory generator for execute_ssot.py.

Produces docs/specs/execute_ssot_inventory.json with deterministic symbol inventory.
Also inventories execute_ssot_entrypoint.py.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Simple static signals for writes_repo / side_effects detection
WRITE_SIGNALS = re.compile(
    r"""
    open\s*\(.*['"]w['"]       |  # open(...,'w')
    open\s*\(.*['"]a['"]       |  # open(...,'a')
    \.write_text\s*\(          |
    \.write_bytes\s*\(         |
    os\.remove\s*\(            |
    os\.replace\s*\(           |
    os\.rename\s*\(            |
    os\.chmod\s*\(             |
    shutil\.                   |
    Path\.unlink\s*\(          |
    \.unlink\s*\(              |
    \.touch\s*\(               |
    \.mkdir\s*\(               |
    subprocess\.run\s*\(       |
    subprocess\.call\s*\(      |
    json\.dump\s*\(            |
    os\.walk\s*\(              |
    spec\.loader\.exec_module  |
    importlib\.import_module   |
    sys\.path\.insert          |
    sys\.modules\[             |
    builtins\.input\s*=        |
    signal\.signal\s*\(        |
    atexit\.register\s*\(      |
    os\.environ\[              |
    os\.environ\.get           |
    logging\.basicConfig       |
    sys\.exit\s*\(
    """,
    re.VERBOSE,
)

SIDE_EFFECT_SIGNALS = re.compile(
    r"""
    print\s*\(                 |
    logger\.\w+\s*\(           |
    logging\.\w+\s*\(          |
    sys\.exit\s*\(             |
    raise\s                    |
    subprocess                 |
    os\.environ                |
    builtins\.                 |
    signal\.signal             |
    atexit\.register           |
    time\.sleep
    """,
    re.VERBOSE,
)


def _get_source_segment(source_lines: list[str], start: int, end: int) -> str:
    """Extract source segment from line range (1-indexed)."""
    return "\n".join(source_lines[start - 1 : end])


def _detect_writes(segment: str) -> bool | str:
    if WRITE_SIGNALS.search(segment):
        return True
    return "unknown"


def _detect_side_effects(segment: str) -> bool | str:
    if WRITE_SIGNALS.search(segment):
        return True
    if SIDE_EFFECT_SIGNALS.search(segment):
        return True
    return "unknown"


def inventory_file(filepath: Path, prefix: str = "") -> list[dict]:
    """Parse a single .py file and return inventory entries."""
    source = filepath.read_text(encoding="utf-8")
    source_lines = source.splitlines()
    tree = ast.parse(source, filename=str(filepath))

    entries: list[dict] = []

    for node in ast.iter_child_nodes(tree):
        # Module-level constants (assignments)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    end_lineno = getattr(node, "end_lineno", node.lineno)
                    segment = _get_source_segment(source_lines, node.lineno, end_lineno)
                    entries.append(
                        {
                            "kind": "constant",
                            "name": name,
                            "qualname": f"{prefix}{name}" if prefix else name,
                            "lineno": node.lineno,
                            "end_lineno": end_lineno,
                            "writes_repo": _detect_writes(segment),
                            "side_effects": _detect_side_effects(segment),
                        },
                    )

        # Module-level annotated assignments (e.g. AGENT_DEPENDENCIES: dict = {...})
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            end_lineno = getattr(node, "end_lineno", node.lineno)
            segment = _get_source_segment(source_lines, node.lineno, end_lineno)
            entries.append(
                {
                    "kind": "constant",
                    "name": name,
                    "qualname": f"{prefix}{name}" if prefix else name,
                    "lineno": node.lineno,
                    "end_lineno": end_lineno,
                    "writes_repo": _detect_writes(segment),
                    "side_effects": _detect_side_effects(segment),
                },
            )

        # Module-level functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_lineno = getattr(node, "end_lineno", node.lineno)
            segment = _get_source_segment(source_lines, node.lineno, end_lineno)
            entries.append(
                {
                    "kind": "function",
                    "name": node.name,
                    "qualname": f"{prefix}{node.name}" if prefix else node.name,
                    "lineno": node.lineno,
                    "end_lineno": end_lineno,
                    "writes_repo": _detect_writes(segment),
                    "side_effects": _detect_side_effects(segment),
                },
            )

        # Classes
        elif isinstance(node, ast.ClassDef):
            class_end = getattr(node, "end_lineno", node.lineno)
            class_segment = _get_source_segment(source_lines, node.lineno, class_end)
            class_qualname = f"{prefix}{node.name}" if prefix else node.name

            entries.append(
                {
                    "kind": "class",
                    "name": node.name,
                    "qualname": class_qualname,
                    "lineno": node.lineno,
                    "end_lineno": class_end,
                    "writes_repo": _detect_writes(class_segment),
                    "side_effects": _detect_side_effects(class_segment),
                },
            )

            # Methods within the class
            for item in ast.iter_child_nodes(node):
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_end = getattr(item, "end_lineno", item.lineno)
                    method_segment = _get_source_segment(
                        source_lines,
                        item.lineno,
                        method_end,
                    )
                    entries.append(
                        {
                            "kind": "method",
                            "name": item.name,
                            "qualname": f"{class_qualname}.{item.name}",
                            "lineno": item.lineno,
                            "end_lineno": method_end,
                            "writes_repo": _detect_writes(method_segment),
                            "side_effects": _detect_side_effects(method_segment),
                        },
                    )

    return entries


def main() -> None:
    ssot_file = REPO_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py"
    entrypoint_file = REPO_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot_entrypoint.py"

    inventory: list[dict] = []

    # Inventory execute_ssot.py
    inventory.extend(inventory_file(ssot_file, prefix="execute_ssot."))

    # Inventory execute_ssot_entrypoint.py
    inventory.extend(inventory_file(entrypoint_file, prefix="execute_ssot_entrypoint."))

    # Sort by file then line number for determinism
    inventory.sort(key=lambda e: (e["qualname"].split(".")[0], e["lineno"]))

    out_path = REPO_ROOT / "docs" / "specs" / "execute_ssot_inventory.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(inventory)} entries to {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
