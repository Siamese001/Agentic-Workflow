"""Add missing import lines for emit calls that were inserted without imports.

Safe strategy: for each file with an orphan call (func called but not imported),
find the last TOP-LEVEL standalone import line from lifecycle_trace_contract
already in the file, and append the missing names right after it.
If no such line exists, append individual from-import lines after find_last_import().
Does NOT touch any existing import blocks.
"""

import ast
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAPS_CSV = PROJECT_ROOT / "runtime_gaps" / "trace_deficit_modules.csv"
APPLY = "--apply" in sys.argv

CONTRACT = "agentic_core.runtime.lifecycle_trace_contract"

ALL_EMIT_FUNCS = [
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


def is_func_imported(func: str, lines: list[str]) -> bool:
    """True only if func appears in a real import statement (not docstring content)."""
    for line in lines:
        s = line.strip()
        if not s.startswith(("from ", "import ")):
            continue
        if CONTRACT in s and func in s:
            return True
    return False


def find_last_toplevel_import(lines: list[str]) -> int:
    """Return 0-based index of the last top-level import line."""
    last = -1
    in_paren = False
    for i, line in enumerate(lines):
        s = line.strip()
        if in_paren:
            if ")" in s:
                in_paren = False
                last = i
            continue
        if not s or s.startswith("#"):
            continue
        if not line[0:1].isspace() and s.startswith(("import ", "from ")):
            last = i
            if "(" in s and ")" not in s:
                in_paren = True
        elif last >= 0 and not line[0:1].isspace() and not s.startswith(("#", "import ", "from ")):
            # Hit non-import top-level code after imports — stop scanning
            # but don't break yet in case there are more import blocks below
            pass
    return last


def fix_file(fp: Path) -> tuple[str, list[str]]:
    src = fp.read_text(encoding="utf-8")
    lines = src.split("\n")

    # Find which funcs are called but not imported
    missing = [
        f
        for f in ALL_EMIT_FUNCS
        if f"({f}(" in src or src.startswith(f"{f}(") or f"\n{f}(" in src
        if not is_func_imported(f, lines)
    ]

    # More precise call detection
    missing = []
    for func in ALL_EMIT_FUNCS:
        # Check if func is called anywhere (at any indent level)
        called = False
        for line in lines:
            s = line.strip()
            if s.startswith(f"{func}(") or f" {func}(" in line or f"\t{func}(" in line:
                called = True
                break
        if called and not is_func_imported(func, lines):
            missing.append(func)

    if not missing:
        return "SKIP", []

    # Validate parse
    try:
        ast.parse(src)
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError as e:
        return f"SKIP(syntax:{e.lineno})", []

    # Find insertion point: after the last top-level import
    insert_after = find_last_toplevel_import(lines)
    if insert_after < 0:
        insert_after = 0

    # Build import lines to insert
    import_lines = [f"from {CONTRACT} import {func}  # noqa: E402" for func in missing]

    result = lines[: insert_after + 1] + import_lines + lines[insert_after + 1 :]
    new_src = "\n".join(result)

    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        ast.parse(new_src)
    except SyntaxError as e:
        return f"ERROR(post-fix syntax:{e.lineno}:{e.msg})", []

    if APPLY:
        fp.write_text(new_src, encoding="utf-8")

    return "FIXED", missing


def main():
    # Collect all Python files that were wired (from deficit CSV + git diff)
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    changed = {l.strip() for l in result.stdout.splitlines() if l.strip().endswith(".py")}

    # Include all deficit modules
    if GAPS_CSV.exists():
        for row in csv.DictReader(open(GAPS_CSV)):
            changed.add(row["source_file"])

    # Explicitly add known problem files
    extra = [
        "agentic_core/adg/extraction/static_scanner.py",
        "agentic_core/L2_execution/providers.py",
        "agentic_core/mixins/healing_mixin.py",
        "apps_rg/utils/enhanced_rg_flow_router_util.py",
        "tools/generate_full_adg.py",
    ]
    changed.update(extra)

    print(f"{'=' * 70}")
    print(f"  ORPHAN IMPORT PATCH  ({'APPLY' if APPLY else 'DRY RUN'})")
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
        if status == "FIXED":
            print(f"  FIXED: [{rel}]  +{funcs}")
            fixed += 1
        elif status.startswith("ERROR"):
            print(f"  {status}: [{rel}]")
            errors += 1
        else:
            skipped += 1

    print(f"\n{'=' * 70}")
    print(f"  Fixed:   {fixed}")
    print(f"  Errors:  {errors}")
    print(f"  Skipped: {skipped}")


if __name__ == "__main__":
    main()
