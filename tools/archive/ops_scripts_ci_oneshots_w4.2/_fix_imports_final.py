"""
Final idempotent import fixer:
1. Deduplicates entries in path_constants import blocks
2. Adds any missing constants that are used as ast.Name nodes
3. Fixes double-path: AGENTIC_CORE_DIR / L*_DIR -> L*_DIR
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAYER_DIRS = {
    "L0_ROUTING_DIR",
    "L1_COGNITION_DIR",
    "L2_EXECUTION_DIR",
    "L3_ORCHESTRATION_DIR",
    "L4_STATE_DIR",
    "L5_SAFETY_DIR",
    "L6_OBSERVABILITY_DIR",
}
ALL_CONSTANTS = {
    "AGENTIC_CORE_DIR",
    "APPS_LIC_DIR",
    "APPS_RG_DIR",
    "APPS_SHARED_DIR",
    "SYSTEM_LEARNING_DIR",
    "TOOLS_DIR",
    "TESTS_DIR",
    "OPS_SCRIPTS_DIR",
    "L0_ROUTING_DIR",
    "L1_COGNITION_DIR",
    "L2_EXECUTION_DIR",
    "L3_ORCHESTRATION_DIR",
    "L4_STATE_DIR",
    "L5_SAFETY_DIR",
    "L6_OBSERVABILITY_DIR",
    "ARCHIVES_DIR",
}
IMPORT_BLOCK_RE = re.compile(
    "from agentic_core\\.L0_routing\\.config\\.path_constants import \\(([^)]*)\\)", re.DOTALL
)


def normalize_import_block(src: str, used_constants: set[str]) -> str:
    """Rebuild import block with deduped, sorted constants that are actually used."""
    m = IMPORT_BLOCK_RE.search(src)
    if not m:
        if not used_constants:
            return src
        new_block = (
            "from agentic_core.L0_routing.config.path_constants import (\n    "
            + ",\n    ".join(sorted(used_constants))
            + ",\n)"
        )
        lines = src.splitlines(keepends=True)
        insert_after = 0
        paren_depth = 0
        in_import = False
        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                in_import = True
            if in_import:
                paren_depth += line.count("(") - line.count(")")
                if paren_depth <= 0:
                    insert_after = i + 1
                    in_import = False
                    paren_depth = 0
        lines.insert(insert_after, "\n" + new_block + "\n")
        return "".join(lines)
    body = m.group(1)
    existing = set(re.findall("\\b([A-Z][A-Z_]{2,})\\b", body)) & ALL_CONSTANTS
    final = (existing | used_constants) & ALL_CONSTANTS
    final = final & used_constants
    final = final | existing - LAYER_DIRS
    new_body = "\n    " + ",\n    ".join(sorted(final)) + ",\n"
    new_block = "from agentic_core.L0_routing.config.path_constants import (" + new_body + ")"
    return src[: m.start()] + new_block + src[m.end() :]


def fix_double_paths(src: str) -> str:
    for layer_const in LAYER_DIRS:
        # guardian: allow-path-string
        pattern = re.compile("\\bAGENTIC_CORE_DIR\\s*/\\s*" + re.escape(layer_const) + "\\b")
        src = pattern.sub(layer_const, src)
    return src


def process_file(fp: Path) -> tuple[bool, str]:
    src = fp.read_text(encoding="utf-8")
    original = src
    src = fix_double_paths(src)
    try:
        tree = ast.parse(src)
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        return (False, f"SyntaxError: {e}")
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id in ALL_CONSTANTS}
    src = normalize_import_block(src, used)
    try:
        ast.parse(src)
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        return (False, f"SyntaxError after fix: {e}")
    if src != original:
        fp.write_text(src, encoding="utf-8")
        return (True, "fixed")
    return (True, "ok")


def audit(fp: Path) -> list[str]:
    """Return list of issues for this file."""
    issues = []
    try:
        src = fp.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise
        return [f"parse error: {e}"]
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left_has_agentic = any(
                isinstance(c, ast.Name) and c.id == "AGENTIC_CORE_DIR" for c in ast.walk(node.left)
            )
            right_name = node.right.id if isinstance(node.right, ast.Name) else ""
            if left_has_agentic and right_name in LAYER_DIRS:
                issues.append(f"double-path L{node.lineno}: AGENTIC_CORE_DIR / {right_name}")
    m = re.search(
        "from agentic_core\\.L0_routing\\.config\\.path_constants import \\(([^)]*)\\)", src, re.DOTALL
    )
    imported = set(re.findall("\\b([A-Z][A-Z_]{2,})\\b", m.group(1)) if m else []) & ALL_CONSTANTS
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id in ALL_CONSTANTS}
    missing = (used & ALL_CONSTANTS) - imported
    if missing:
        issues.append(f"missing imports: {sorted(missing)}")
    if m:
        names = re.findall("\\b([A-Z][A-Z_]{2,})\\b", m.group(1))
        dupes = {n for n in names if names.count(n) > 1}
        if dupes:
            issues.append(f"duplicate imports: {sorted(dupes)}")
    return issues


def main():
    test_files = sorted((ROOT / TESTS_DIR).rglob("*.py"))
    test_files = [f for f in test_files if "__pycache__" not in str(f)]
    fixed = errors = 0
    for fp in test_files:
        ok, msg = process_file(fp)
        if not ok:
            errors += 1
            print(f"ERROR: {fp.relative_to(ROOT)}: {msg}")
        elif msg == "fixed":
            fixed += 1
    print(f"Pass 1: {fixed} fixed, {errors} errors")
    all_issues = {}
    for fp in test_files:
        issues = audit(fp)
        if issues:
            all_issues[str(fp.relative_to(ROOT))] = issues
    print(f"Pass 2 audit: {len(all_issues)} files with issues")
    for f, issues in sorted(all_issues.items()):
        for issue in issues:
            print(f"  {f}: {issue}")
    if not all_issues:
        print("\nALL CHECKS PASSED - 100% clean")


if __name__ == "__main__":
    main()
