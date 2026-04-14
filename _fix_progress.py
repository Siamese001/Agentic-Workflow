"""Auto-fix §16 progress bar violations: wrap for-loops with tqdm."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def get_violations() -> dict[str, list[tuple[int, bool]]]:
    """Run check and parse output. Returns {filepath: [(lineno, is_func_violation)]}."""
    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_query_progress_bar.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    violations: dict[str, list[tuple[int, bool]]] = {}
    for raw in result.stdout.splitlines():
        raw = raw.strip().lstrip("- ").strip()
        m = re.match(r"^(.+?\.py):(\d+):", raw.replace("\\", "/"))
        if m:
            fp = m.group(1)
            ln = int(m.group(2))
            is_func = "Function '" in raw[m.end() :]
            violations.setdefault(fp, []).append((ln, is_func))
    return violations


def find_last_import_pos(lines: list[str]) -> int:
    """Return 0-indexed position AFTER the last import line."""
    pos = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith(("from __future__", "import ", "from ")):
            pos = i + 1
    return pos


def wrap_for_line(line: str) -> str | None:
    """Wrap the iterable of a for-loop line with tqdm. Returns new line or None."""
    if "tqdm(" in line:
        return None

    # Match: (indent)(async )?for (vars) in (iterable):( optional comment)
    m = re.match(
        r"^(\s*)(async\s+)?for\s+(.+?)\s+in\s+(.+?)(\s*:)(\s*(?:#.*)?)$",
        line.rstrip("\n"),
        re.DOTALL,
    )
    if not m:
        return None

    indent = m.group(1)
    async_ = m.group(2) or ""
    var = m.group(3)
    iterable = m.group(4).strip()
    colon = m.group(5)
    comment = m.group(6)

    if iterable.startswith("tqdm("):
        return None

    return f'{indent}{async_}for {var} in tqdm({iterable}, desc="Processing", unit="item"){colon}{comment}\n'


def find_first_for_loop_in_func(source: str, func_lineno: int) -> int | None:
    """Return the line number of the first for-loop inside the function at func_lineno."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno == func_lineno:
                for child in ast.walk(node):
                    if isinstance(child, ast.For) and child.lineno != func_lineno:
                        return child.lineno
    return None


def fix_file(filepath: str, violations: list[tuple[int, bool]]) -> int:
    """Apply fixes to a file. Returns number of loops fixed."""
    full_path = ROOT / filepath
    if not full_path.exists():
        print(f"  SKIP (not found): {filepath}")
        return 0

    source = full_path.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    needs_import = "tqdm" not in source

    # Resolve function violations → for-loop line numbers
    resolved: set[int] = set()
    for ln, is_func in violations:
        if is_func:
            actual = find_first_for_loop_in_func(source, ln)
            if actual:
                resolved.add(actual)
            else:
                print(f"  WARN: no for-loop found inside function at line {ln}")
        else:
            resolved.add(ln)

    fixed = 0
    for ln in sorted(resolved, reverse=True):
        if ln < 1 or ln > len(lines):
            continue
        new_line = wrap_for_line(lines[ln - 1])
        if new_line:
            lines[ln - 1] = new_line
            fixed += 1
        else:
            print(f"  WARN: could not parse for-loop at line {ln}: {lines[ln - 1].strip()[:60]}")

    if fixed == 0:
        return 0

    if needs_import:
        insert_pos = find_last_import_pos(lines)
        lines.insert(insert_pos, "from tqdm import tqdm\n")

    full_path.write_text("".join(lines), encoding="utf-8")
    return fixed


def main() -> None:
    print("Collecting §16 violations...")
    violations = get_violations()
    total = sum(len(v) for v in violations.values())
    print(f"Found {total} violations across {len(violations)} files\n")

    total_fixed = 0
    for fp, vlist in sorted(violations.items()):
        n = fix_file(fp, vlist)
        if n:
            print(f"  Fixed {n}/{len(vlist)} in {fp}")
            total_fixed += n
        else:
            print(f"  No change: {fp}")

    print(f"\nTotal loops fixed: {total_fixed}")
    print("Re-running check to verify remaining violations...")

    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_query_progress_bar.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    remaining = sum(1 for line in result.stdout.splitlines() if re.match(r"^\s*-\s+.+\.py:\d+:", line))
    if remaining == 0:
        print("[PASS] No remaining violations.")
    else:
        print(f"[WARN] {remaining} violations remain — check output above for details.")
        print(result.stdout[-3000:])


if __name__ == "__main__":
    main()
