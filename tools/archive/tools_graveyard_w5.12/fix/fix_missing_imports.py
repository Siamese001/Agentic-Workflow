"""Fix files where emit calls exist but imports were stripped by repair_docstring_wiring.

For each deficit file, ensure every called emit function is actually imported.
Uses the existing multi-line lifecycle_trace_contract import block if present,
otherwise adds individual imports.
"""
import ast
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAPS_CSV = PROJECT_ROOT / "runtime_gaps" / "trace_deficit_modules.csv"
APPLY = "--apply" in sys.argv

EMIT_FUNC_TO_IMPORT = {
    "emit_replay_key": "emit_replay_key",
    "emit_determinism_digest": "emit_determinism_digest",
    "_emit_applies_guardrail": "_emit_applies_guardrail",
    "_emit_snapshots_state": "_emit_snapshots_state",
    "_emit_signs_execution_trace": "_emit_signs_execution_trace",
    "_emit_records_execution_trace": "_emit_records_execution_trace",
    "_emit_reads_policy_state": "_emit_reads_policy_state",
}

SKIP_PATTERNS = {
    "_constants.py", "conftest.py", "structure_blueprint_config.py",
    "ssot_tier_constants.py", "path_constants.py", "lifecycle_trace_contract.py",
}

CONTRACT_MODULE = "agentic_core.runtime.lifecycle_trace_contract"


def is_imported(func_name: str, src: str) -> bool:
    """Check if func_name is imported from lifecycle_trace_contract in any form."""
    # Direct single-line import
    if f"import {func_name}" in src and CONTRACT_MODULE in src:
        # More precise check
        for line in src.splitlines():
            if CONTRACT_MODULE in line and func_name in line and "import" in line:
                return True
    return False


def fix_file(fp: Path) -> tuple[str, str, list[str]]:
    src = fp.read_text(encoding="utf-8")

    # Find which emit funcs are called but not imported
    missing_imports = []
    for func in EMIT_FUNC_TO_IMPORT:
        called = f"{func}(" in src
        imported = is_imported(func, src)
        if called and not imported:
            missing_imports.append(func)

    if not missing_imports:
        return "SKIP", "all imports present", []

    # Validate parse first
    try:
        ast.parse(src)
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError as e:
        return "ERROR", f"parse error: {e}", []

    lines = src.split("\n")

    # Strategy 1: if there's an existing multi-line import block from CONTRACT_MODULE,
    # add missing names into it (before the closing paren)
    contract_block_start = -1
    contract_block_end = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if f"from {CONTRACT_MODULE} import" in stripped and "(" in stripped:
            contract_block_start = i
            # Find closing paren
            for j in range(i, min(i + 50, len(lines))):
                if ")" in lines[j] and j != i:
                    contract_block_end = j
                    break
            break

    if contract_block_start >= 0 and contract_block_end >= 0:
        # Insert missing imports before the closing paren
        indent = "    "
        insert_at = contract_block_end
        for func in missing_imports:
            lines.insert(insert_at, f"{indent}{func},  # noqa: E402")
            insert_at += 1
    else:
        # Strategy 2: find end of import block and add individual import lines
        last_import = 0
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith(("import ", "from ")):
                last_import = i
        insert_at = last_import + 1
        for j, func in enumerate(missing_imports):
            lines.insert(insert_at + j,
                f"from {CONTRACT_MODULE} import {func}  # noqa: E402")

    new_src = "\n".join(lines)

    # Validate
    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        ast.parse(new_src)
    except SyntaxError as e:
        return "ERROR", f"post-fix syntax error: {e}", []

    if APPLY:
        fp.write_text(new_src, encoding="utf-8")

    return "FIXED", f"added imports for: {missing_imports}", missing_imports


def main():
    rows = list(csv.DictReader(open(GAPS_CSV)))
    print(f"{'=' * 70}")
    print(f"  MISSING IMPORT FIX  ({'APPLY' if APPLY else 'DRY RUN'})")
    print(f"{'=' * 70}")

    stats = {"FIXED": 0, "SKIP": 0, "ERROR": 0}

    for row in rows:
        rel = row["source_file"]
        if any(pat in rel for pat in SKIP_PATTERNS):
            continue
        fp = PROJECT_ROOT / rel
        if not fp.exists():
            continue

        status, detail, fixed = fix_file(fp)
        stats[status] = stats.get(status, 0) + 1
        if status == "FIXED":
            print(f"  FIXED: [{rel}]  {detail}")
        elif status == "ERROR":
            print(f"  ERROR: [{rel}]  {detail}")

    print(f"\n{'=' * 70}")
    print(f"  Fixed:   {stats.get('FIXED', 0)}")
    print(f"  Skipped: {stats.get('SKIP', 0)}")
    print(f"  Errors:  {stats.get('ERROR', 0)}")


if __name__ == "__main__":
    main()
