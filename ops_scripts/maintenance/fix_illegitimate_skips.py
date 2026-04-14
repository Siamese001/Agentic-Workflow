"""Rewrite illegitimate pytest skip sites in tests.

Strategy:
  - pytest.skip(msg) -> pytest.fail(msg) for illegitimate sites
  - pytest.importorskip(pkg) for mandatory deps -> explicit import + pytest.fail
  - legitimate environment or optional-dependency skips are preserved
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TESTS_DIR, get_validated_project_root


ROOT = get_validated_project_root()
TESTS = ROOT / TESTS_DIR
LEGITIMATE_REASONS_SUBSTRINGS = [
    "redis not running",
    "redis not",
    "playwright not installed",
    "playwright visual tests should be run separately",
    "ssot_orch_negctrl_tamper",
    "activate tamper",
    "read-only directory",
    "faiss-gpu",
]
NOT_IMPLEMENTED_SUBSTRINGS = ["not yet implemented", "method not implemented yet"]


def is_legitimate(reason: str) -> bool:
    lowered = reason.lower()
    return any(token in lowered for token in LEGITIMATE_REASONS_SUBSTRINGS)


def is_not_implemented(reason: str) -> bool:
    lowered = reason.lower()
    return any(token in lowered for token in NOT_IMPLEMENTED_SUBSTRINGS)


def rewrite_importorskip_line(line: str) -> str:
    match = re.search(r"importorskip\s*\(\s*['\"]([^'\"]+)['\"]", line)
    if not match:
        return line
    package_name = match.group(1)
    indent = " " * (len(line) - len(line.lstrip()))
    return (
        f"{indent}try:\n"
        f"{indent}    import {package_name}  # noqa: F401\n"
        f"{indent}except ImportError:\n"
        f'{indent}    pytest.fail("{package_name} is a mandatory dependency — install it")\n'
    )


def fix_file(path: Path, execute: bool) -> tuple[bool, int]:
    original = path.read_text(encoding="utf-8", errors="replace")
    lines = original.splitlines(keepends=True)
    try:
        tree = ast.parse(original)
    except SyntaxError:
        return False, 0

    illegitimate_lines: dict[int, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "importorskip":
            raw_args = [ast.unparse(arg) for arg in node.args]
            reason = raw_args[0].strip("\"'") if raw_args else "missing import"
            illegitimate_lines[node.lineno] = ("importorskip", reason)
            continue

        if (
            isinstance(func, ast.Attribute)
            and func.attr == "skip"
            and isinstance(func.value, ast.Name)
            and func.value.id == "pytest"
        ):
            raw_args = [ast.unparse(arg) for arg in node.args]
            reason = raw_args[0].strip("\"'") if raw_args else ""
            if not is_legitimate(reason):
                kind = "not_implemented" if is_not_implemented(reason) else "skip"
                illegitimate_lines[node.lineno] = (kind, reason)

    if not illegitimate_lines:
        return False, 0

    new_lines = list(lines)
    fixes = 0
    changed = False
    for lineno, (kind, _reason) in sorted(illegitimate_lines.items()):
        index = lineno - 1
        line = new_lines[index]
        if kind == "importorskip":
            rewritten = rewrite_importorskip_line(line)
        else:
            rewritten = line.replace("pytest.skip(", "pytest.fail(", 1)

        if rewritten != line:
            new_lines[index] = rewritten
            fixes += 1
            changed = True

    if changed and execute:
        path.write_text("".join(new_lines), encoding="utf-8")
    return changed, fixes


def main(execute: bool = False) -> int:
    total_files = 0
    total_fixes = 0
    for path in sorted(TESTS.rglob("test_*.py")):
        changed, fixes = fix_file(path, execute=execute)
        if changed:
            total_files += 1
            total_fixes += fixes
            rel = path.relative_to(ROOT)
            prefix = "FIXED" if execute else "[DRY-RUN] Would fix"
            print(f"{prefix} {fixes:3d} site(s)  {rel}")

    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"\nDONE ({mode}): {total_fixes} fixes across {total_files} files")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace illegitimate pytest skip patterns.")
    parser.add_argument("--execute", action="store_true", help="Write changes to disk. Default is dry-run.")
    raise SystemExit(main(execute=parser.parse_args().execute))
