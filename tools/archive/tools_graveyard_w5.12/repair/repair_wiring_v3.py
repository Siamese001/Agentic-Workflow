"""Repair wiring injected inside module docstrings (v3 — minimal surgery).

STRATEGY:
- For each deficit file: parse AST to get list of called emit funcs
- Determine which dims are missing from AST (the actual problem)
- Remove ONLY the exact spurious lines from inside the docstring
  (match by exact content, not by broad pattern)
- Insert missing import + call after the last top-level import
"""

import ast
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAPS_CSV = PROJECT_ROOT / "runtime_gaps" / "trace_deficit_modules.csv"
APPLY = "--apply" in sys.argv

CONTRACT = "agentic_core.runtime.lifecycle_trace_contract"

DIM_CONFIG = {
    "records_execution_trace": {
        "emit_func": "_emit_records_execution_trace",
        "import_line": f"from {CONTRACT} import _emit_records_execution_trace  # noqa: E402",
        "call_template": '_emit_records_execution_trace("p0", "evidence", "BASENAME")',
    },
    "applies_guardrail": {
        "emit_func": "_emit_applies_guardrail",
        "import_line": f"from {CONTRACT} import _emit_applies_guardrail  # noqa: E402",
        "call_template": '_emit_applies_guardrail("p0", "BASENAME", "p0_governance")',
    },
    "reads_policy_state": {
        "emit_func": "_emit_reads_policy_state",
        "import_line": f"from {CONTRACT} import _emit_reads_policy_state  # noqa: E402",
        "call_template": '_emit_reads_policy_state("p0", "BASENAME", "policy_binding")',
    },
    "snapshots_state": {
        "emit_func": "_emit_snapshots_state",
        "import_line": f"from {CONTRACT} import _emit_snapshots_state  # noqa: E402",
        "call_template": '_emit_snapshots_state("p0", "BASENAME", "state_snapshot")',
    },
    "emits_replay_key": {
        "emit_func": "emit_replay_key",
        "import_line": f"from {CONTRACT} import emit_replay_key  # noqa: E402",
        "call_template": 'emit_replay_key("p0", "BASENAME")',
    },
    "emits_determinism_digest": {
        "emit_func": "emit_determinism_digest",
        "import_line": f"from {CONTRACT} import emit_determinism_digest  # noqa: E402",
        "call_template": 'emit_determinism_digest("p0", "BASENAME")',
    },
    "signs_execution_trace": {
        "emit_func": "_emit_signs_execution_trace",
        "import_line": f"from {CONTRACT} import _emit_signs_execution_trace  # noqa: E402",
        "call_template": '_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)',
    },
}

SKIP_PATTERNS = {
    "_constants.py",
    "conftest.py",
    "structure_blueprint_config.py",
    "ssot_tier_constants.py",
    "path_constants.py",
    "lifecycle_trace_contract.py",
}


def ast_called_funcs(src: str) -> set[str]:
    try:
        tree = ast.parse(src)
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError:
        return set()
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                called.add(f.id)
            elif isinstance(f, ast.Attribute):
                called.add(f.attr)
    return called


def is_imported(func: str, src: str) -> bool:
    for line in src.splitlines():
        if CONTRACT in line and "import" in line and func in line:
            return True
    return False


def find_docstring_interior(lines: list[str]) -> tuple[int, int]:
    """Return (first_content_line, last_content_line) of module docstring interior.
    Returns (-1, -1) if no multi-line docstring at top.
    """
    i = 0
    while i < len(lines) and (lines[i].strip() == "" or lines[i].strip().startswith("#!")):
        i += 1
    if i >= len(lines):
        return -1, -1
    s = lines[i].strip()
    if not (s.startswith('"""') or s.startswith("'''")):
        return -1, -1
    quote = s[:3]
    # Check if single-line
    rest = s[3:]
    if rest.endswith(quote) and len(rest) > len(quote):
        return -1, -1  # single line docstring, no interior to corrupt
    # Multi-line
    content_start = i + 1
    for j in range(content_start, len(lines)):
        if quote in lines[j]:
            # closing line at j; interior is content_start..j-1
            return content_start, j - 1
    return -1, -1


def find_last_import(lines: list[str]) -> int:
    """0-based index of the last top-level import line."""
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


def repair_file(fp: Path, missing_dims: list[str]) -> tuple[str, str, list[str]]:
    src = fp.read_text(encoding="utf-8")
    basename = fp.stem

    # Which dims are missing from AST?
    called = ast_called_funcs(src)
    dims_to_fix = [d for d in missing_dims if DIM_CONFIG.get(d) and DIM_CONFIG[d]["emit_func"] not in called]

    if not dims_to_fix:
        return "SKIP", "all in AST", []

    lines = src.split("\n")

    # Build exact lines that were spuriously inserted inside the docstring
    spurious = set()
    for dim in dims_to_fix:
        cfg = DIM_CONFIG[dim]
        func = cfg["emit_func"]
        call = cfg["call_template"].replace("BASENAME", basename)
        imp_bare = cfg["import_line"].split("  #")[0].strip()
        imp_with_noqa = cfg["import_line"]
        spurious.add(call)
        spurious.add(imp_bare)
        spurious.add(imp_with_noqa)
        # Also the version with '# noqa: E402' already in the original import
        spurious.add(f"from {CONTRACT} import {func}  # noqa: E402")

    # Find docstring interior range
    doc_start, doc_end = find_docstring_interior(lines)

    # Remove matching lines from docstring interior (in reverse to preserve indices)
    if doc_start >= 0:
        new_lines = []
        skip_next_blank = False
        for i, line in enumerate(lines):
            if doc_start <= i <= doc_end:
                stripped = line.strip()
                if stripped in spurious:
                    skip_next_blank = True
                    continue
                if skip_next_blank and stripped == "":
                    skip_next_blank = False
                    continue
                skip_next_blank = False
                new_lines.append(line)
            else:
                new_lines.append(line)
        lines = new_lines

    # Now insert imports + calls after last import line
    insert_after = find_last_import(lines)
    if insert_after < 0:
        insert_after = 0

    current_src = "\n".join(lines)
    insert_lines = []
    for dim in dims_to_fix:
        cfg = DIM_CONFIG[dim]
        func = cfg["emit_func"]
        call = cfg["call_template"].replace("BASENAME", basename)
        if not is_imported(func, current_src):
            insert_lines.append(cfg["import_line"])
        insert_lines.append(call)

    if not insert_lines:
        return "SKIP", "nothing to insert", []

    to_insert = [""] + insert_lines + [""]
    result = lines[: insert_after + 1] + to_insert + lines[insert_after + 1 :]
    new_src = "\n".join(result)

    # Validate
    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        ast.parse(new_src)
    except SyntaxError as e:
        return "ERROR", f"syntax: {e}", []

    # Confirm dims now appear in AST
    new_called = ast_called_funcs(new_src)
    still_missing = [d for d in dims_to_fix if DIM_CONFIG[d]["emit_func"] not in new_called]
    if still_missing:
        return "ERROR", f"still missing from AST: {still_missing}", []

    if APPLY:
        fp.write_text(new_src, encoding="utf-8")

    return "REPAIRED", f"{len(dims_to_fix)} dims @ line {insert_after + 2}", dims_to_fix


def main():
    rows = list(csv.DictReader(open(GAPS_CSV)))
    print(f"{'=' * 70}")
    print(f"  WIRING REPAIR v3  ({'APPLY' if APPLY else 'DRY RUN'})")
    print(f"  {len(rows)} deficit modules")
    print(f"{'=' * 70}")

    stats = {"REPAIRED": 0, "SKIP": 0, "ERROR": 0}
    dim_stats = dict.fromkeys(DIM_CONFIG, 0)

    for row in rows:
        rel = row["source_file"]
        if any(pat in rel for pat in SKIP_PATTERNS):
            continue
        fp = PROJECT_ROOT / rel
        if not fp.exists():
            continue
        missing = row["missing_dimensions"].split("|")

        status, detail, dims_fixed = repair_file(fp, missing)
        stats[status] = stats.get(status, 0) + 1

        if status == "REPAIRED":
            print(f"  REPAIRED: {detail}  [{rel}]")
            for d in dims_fixed:
                dim_stats[d] = dim_stats.get(d, 0) + 1
        elif status == "ERROR":
            print(f"  ERROR: {detail}  [{rel}]")

    print(f"\n{'=' * 70}")
    print("  SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Repaired: {stats.get('REPAIRED', 0)}")
    print(f"  Skipped:  {stats.get('SKIP', 0)}")
    print(f"  Errors:   {stats.get('ERROR', 0)}")
    if stats.get("REPAIRED", 0) > 0:
        print("\n  Dims repaired:")
        for d, c in sorted(dim_stats.items(), key=lambda x: -x[1]):
            if c > 0:
                print(f"    {d}: +{c}")


if __name__ == "__main__":
    main()
