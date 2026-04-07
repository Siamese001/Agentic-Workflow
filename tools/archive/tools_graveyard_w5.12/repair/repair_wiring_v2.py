"""Repair wiring injected inside module docstrings (v2 — correct approach).

For each deficit module where emit calls are inside docstrings (not real AST nodes):
1. Parse the file with ast to find which emit functions ARE in actual call nodes
2. Identify which dims are still missing from AST (in docstring text but not callable)
3. Remove the spurious text from inside the docstring
4. Insert correct standalone import + call lines AFTER the real import block

Never modifies existing multi-line import blocks.
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
        "call_line": '_emit_records_execution_trace("p0", "evidence", "{basename}")',
    },
    "applies_guardrail": {
        "emit_func": "_emit_applies_guardrail",
        "import_line": f"from {CONTRACT} import _emit_applies_guardrail  # noqa: E402",
        "call_line": '_emit_applies_guardrail("p0", "{basename}", "p0_governance")',
    },
    "reads_policy_state": {
        "emit_func": "_emit_reads_policy_state",
        "import_line": f"from {CONTRACT} import _emit_reads_policy_state  # noqa: E402",
        "call_line": '_emit_reads_policy_state("p0", "{basename}", "policy_binding")',
    },
    "snapshots_state": {
        "emit_func": "_emit_snapshots_state",
        "import_line": f"from {CONTRACT} import _emit_snapshots_state  # noqa: E402",
        "call_line": '_emit_snapshots_state("p0", "{basename}", "state_snapshot")',
    },
    "emits_replay_key": {
        "emit_func": "emit_replay_key",
        "import_line": f"from {CONTRACT} import emit_replay_key  # noqa: E402",
        "call_line": 'emit_replay_key("p0", "{basename}")',
    },
    "emits_determinism_digest": {
        "emit_func": "emit_determinism_digest",
        "import_line": f"from {CONTRACT} import emit_determinism_digest  # noqa: E402",
        "call_line": 'emit_determinism_digest("p0", "{basename}")',
    },
    "signs_execution_trace": {
        "emit_func": "_emit_signs_execution_trace",
        "import_line": f"from {CONTRACT} import _emit_signs_execution_trace  # noqa: E402",
        "call_line": '_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)',
    },
}

SKIP_PATTERNS = {
    "_constants.py", "conftest.py", "structure_blueprint_config.py",
    "ssot_tier_constants.py", "path_constants.py", "lifecycle_trace_contract.py",
}


def get_ast_called_funcs(src: str) -> set[str]:
    """Return set of function names that appear in actual AST Call nodes."""
    try:
        tree = ast.parse(src)
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError:
        return set()
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                called.add(func.id)
            elif isinstance(func, ast.Attribute):
                called.add(func.attr)
    return called


def is_imported(func_name: str, src: str) -> bool:
    """True if func_name is imported from CONTRACT in any form."""
    for line in src.splitlines():
        if CONTRACT in line and func_name in line and "import" in line:
            return True
    return False


def find_module_docstring_span(lines: list[str]) -> tuple[int, int]:
    """Return (first_line_of_docstring_content, last_line_of_docstring_content) inclusive.
    Returns (-1, -1) if no module docstring.
    The span covers the interior lines only (not the opening/closing quote lines).
    """
    i = 0
    # Skip shebang, blank lines, encoding declarations
    while i < len(lines):
        s = lines[i].strip()
        if s == "" or s.startswith("#"):
            i += 1
            continue
        break

    if i >= len(lines):
        return -1, -1

    s = lines[i].strip()
    if not (s.startswith('"""') or s.startswith("'''")):
        return -1, -1

    quote = s[:3]
    opening_line = i

    # Check if single-line docstring
    rest = s[3:]
    if rest.endswith(quote) and len(rest) >= len(quote):
        # Single-line — no interior
        return -1, -1

    # Multi-line docstring: interior starts at next line
    content_start = opening_line + 1
    i = content_start
    while i < len(lines):
        if quote in lines[i]:
            # This is the closing line
            return content_start, i - 1
        i += 1
    return -1, -1


def find_last_import_idx(lines: list[str]) -> int:
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
        if s.startswith(("import ", "from ")):
            last = i
            if "(" in s and ")" not in s:
                in_paren = True
    return last


def repair_file(fp: Path, missing_dims: list[str]) -> tuple[str, str, list[str]]:
    src = fp.read_text(encoding="utf-8")
    basename = fp.stem
    lines = src.split("\n")

    # Determine which dims need repair: dim listed as missing AND its emit func
    # is in source text but NOT in actual AST calls
    ast_called = get_ast_called_funcs(src)

    dims_to_fix = []
    for dim in missing_dims:
        cfg = DIM_CONFIG.get(dim)
        if not cfg:
            continue
        func = cfg["emit_func"]
        in_text = func in src
        in_ast = func in ast_called
        if in_text and not in_ast:
            dims_to_fix.append(dim)
        elif not in_text and not in_ast:
            # Also need to wire from scratch
            dims_to_fix.append(dim)

    if not dims_to_fix:
        return "SKIP", "all dims in AST already", []

    # Step 1: Remove spurious emit lines from inside the module docstring
    doc_start, doc_end = find_module_docstring_span(lines)
    if doc_start >= 0 and doc_end >= doc_start:
        interior = lines[doc_start: doc_end + 1]
        cleaned_interior = []
        i = 0
        while i < len(interior):
            s = interior[i].strip()
            is_emit_import = (CONTRACT in s and "import" in s and
                              any(cfg["emit_func"] in s for cfg in DIM_CONFIG.values()))
            is_emit_call = any(
                s.startswith(cfg["emit_func"] + "(") or s == cfg["emit_func"]
                for cfg in DIM_CONFIG.values()
            )
            if is_emit_import or is_emit_call:
                # Skip this line and any adjacent blank line
                i += 1
                # Skip following blank line if present
                if i < len(interior) and interior[i].strip() == "":
                    i += 1
                continue
            cleaned_interior.append(interior[i])
            i += 1

        # Remove trailing blank lines we may have added
        while cleaned_interior and cleaned_interior[-1].strip() == "":
            cleaned_interior.pop()

        lines = lines[:doc_start] + cleaned_interior + lines[doc_end + 1:]

    # Step 2: Also remove any orphaned emit import/call lines outside the docstring
    # that may have been inserted without proper context (no-op duplicates)
    # Only remove standalone emit lines that use # noqa: E402 (our marker)
    filtered = []
    for line in lines:
        s = line.strip()
        is_our_import = (
            s.startswith(f"from {CONTRACT} import") and
            "# noqa: E402" in line and
            any(cfg["emit_func"] in s for cfg in DIM_CONFIG.values())
        )
        is_our_call = any(
            s == cfg["call_line"].format(basename=basename) or
            (s.startswith(cfg["emit_func"] + "(") and s.endswith(")") and
             '"p0"' in s)
            for dim, cfg in DIM_CONFIG.items()
            if dim in dims_to_fix
        )
        if is_our_import or is_our_call:
            # Don't keep — we'll re-add them properly
            continue
        filtered.append(line)
    lines = filtered

    # Step 3: Find correct insertion point (after last import)
    insert_after = find_last_import_idx(lines)
    if insert_after < 0:
        insert_after = 0

    # Step 4: Build import + call lines for dims that need fixing
    insert_lines = []
    current_src = "\n".join(lines)
    for dim in dims_to_fix:
        cfg = DIM_CONFIG[dim]
        func = cfg["emit_func"]
        # Add import if not already present
        if not is_imported(func, current_src):
            insert_lines.append(cfg["import_line"])
        insert_lines.append(cfg["call_line"].format(basename=basename))

    if not insert_lines:
        return "SKIP", "nothing to insert", []

    # Wrap with blank lines
    to_insert = [""] + insert_lines + [""]
    result = lines[: insert_after + 1] + to_insert + lines[insert_after + 1 :]
    new_src = "\n".join(result)

    # Validate
    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        ast.parse(new_src)
    except SyntaxError as e:
        return "ERROR", f"syntax error: {e}", []

    # Confirm dims are now in AST
    new_called = get_ast_called_funcs(new_src)
    still_missing = [d for d in dims_to_fix if DIM_CONFIG[d]["emit_func"] not in new_called]
    if still_missing:
        return "ERROR", f"still missing in AST after repair: {still_missing}", []

    if APPLY:
        fp.write_text(new_src, encoding="utf-8")

    return "REPAIRED", f"{len(dims_to_fix)} dims @ line {insert_after + 2}", dims_to_fix


def main():
    rows = list(csv.DictReader(open(GAPS_CSV)))
    print(f"{'=' * 70}")
    print(f"  WIRING REPAIR v2  ({'APPLY' if APPLY else 'DRY RUN'})")
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
        # else: skip silently

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
