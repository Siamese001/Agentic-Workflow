"""Fix files where emit calls exist but imports are missing.

Strategy: For each file with a called-but-not-imported emit function,
add a standalone import line AFTER the last top-level import statement.
Never touch existing multi-line import blocks.
"""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

CONTRACT = "agentic_core.runtime.lifecycle_trace_contract"

EMIT_FUNCS = [
    "emit_replay_key",
    "emit_determinism_digest",
    "_emit_applies_guardrail",
    "_emit_snapshots_state",
    "_emit_signs_execution_trace",
    "_emit_records_execution_trace",
    "_emit_reads_policy_state",
]

SKIP_PATTERNS = {
    "_constants.py",
    "conftest.py",
    "structure_blueprint_config.py",
    "ssot_tier_constants.py",
    "path_constants.py",
    "lifecycle_trace_contract.py",
}


def is_func_imported(func: str, src: str) -> bool:
    """True if func is imported from lifecycle_trace_contract anywhere in src."""
    if CONTRACT not in src:
        return False
    for line in src.splitlines():
        if CONTRACT in line and func in line and "import" in line:
            return True
    return False


def find_last_import_line(lines: list[str]) -> int:
    """Return 0-based index of last top-level import line."""
    last = -1
    in_paren = False
    for i, line in enumerate(lines):
        s = line.strip()
        if in_paren:
            if ")" in s:
                in_paren = False
                last = i
            continue
        if s.startswith(("import ", "from ")):
            last = i
            if "(" in s and ")" not in s:
                in_paren = True
    return last


def fix_file(fp: Path) -> tuple[str, list[str]]:
    src = fp.read_text(encoding="utf-8")

    # Find called-but-not-imported funcs
    need_import = []
    for func in EMIT_FUNCS:
        if f"{func}(" in src and not is_func_imported(func, src):
            need_import.append(func)

    if not need_import:
        return "SKIP", []

    # Verify file currently parses (may have been broken by earlier repair)
    try:
        ast.parse(src)
        was_broken = False
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError:
        was_broken = True

    lines = src.split("\n")
    insert_after = find_last_import_line(lines)
    if insert_after < 0:
        insert_after = 0

    # Add standalone import lines (individual, not multi-line)
    new_lines = []
    for func in need_import:
        new_lines.append(f"from {CONTRACT} import {func}  # noqa: E402")

    # Insert after last import
    result = lines[: insert_after + 1] + new_lines + lines[insert_after + 1 :]
    new_src = "\n".join(result)

    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        ast.parse(new_src)
    except SyntaxError as e:
        return f"ERROR:{e}", []

    if APPLY:
        fp.write_text(new_src, encoding="utf-8")

    label = "FIXED(was_broken)" if was_broken else "FIXED"
    return label, need_import


def main():
    # Collect all Python files in deficit + also scan the repaired files directly
    targets = []
    # Scan all repaired files via git diff
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    changed = [l.strip() for l in result.stdout.splitlines() if l.strip().endswith(".py")]

    # Also include the deficit CSV
    import csv

    gaps = PROJECT_ROOT / "runtime_gaps" / "trace_deficit_modules.csv"
    if gaps.exists():
        for row in csv.DictReader(open(gaps)):
            p = row["source_file"]
            if p not in changed:
                changed.append(p)

    print(f"{'=' * 70}")
    print(f"  BROKEN IMPORT FIX v2  ({'APPLY' if APPLY else 'DRY RUN'})")
    print(f"  Scanning {len(changed)} files")
    print(f"{'=' * 70}")

    fixed = errors = skipped = 0
    for rel in sorted(changed):
        if any(pat in rel for pat in SKIP_PATTERNS):
            continue
        fp = PROJECT_ROOT / rel
        if not fp.exists():
            continue
        status, funcs = fix_file(fp)
        if status.startswith("FIXED"):
            print(f"  {status}: [{rel}]  +{funcs}")
            fixed += 1
        elif status.startswith("ERROR"):
            print(f"  ERROR: [{rel}]  {status}")
            errors += 1
        else:
            skipped += 1

    print(f"\n{'=' * 70}")
    print(f"  Fixed:   {fixed}")
    print(f"  Errors:  {errors}")
    print(f"  Skipped: {skipped}")


if __name__ == "__main__":
    main()
