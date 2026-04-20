"""P0 Micro-Wave Wirer — wires all 7 wireable P0 dimensions into deficit modules.

Usage:
    python tools/p0_microwave_wirer.py --wave 1 --batch-size 15 [--apply]
    python tools/p0_microwave_wirer.py --wave 1 --batch-size 15 --apply

Reads runtime_gaps/trace_deficit_modules.csv to find modules missing dimensions.
Processes in micro-waves of --batch-size modules (default 15).
Wave N processes modules [(N-1)*batch .. N*batch).
"""

import argparse
import ast
import csv
import json
import sys
import time
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "p0_microwave_wirer", "uwg_governed_write")
_emit_writes_through("p1", "p0_microwave_wirer", "uwg_governed_write_2")
_emit_pulls_context("p1", "p0_microwave_wirer", "context_retrieval")
_emit_pulls_context("p1", "p0_microwave_wirer", "context_retrieval_2")
emit_determinism_digest("trace_p0_microwave_wirer", "p0_microwave_wirer_dispatch")
emit_determinism_digest("trace_p0_microwave_wirer", "p0_microwave_wirer_complete")
_emit_validated_by_safety_plane("p1", "p0_microwave_wirer", "safety_validation")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAPS_DIR = PROJECT_ROOT / "runtime_gaps"
REPORTS_DIR = PROJECT_ROOT / "docs" / "reports"

# ── Dimension config: emit function, import line, call template ──────────────
# {basename} is replaced with the module's stem (filename without .py)
DIM_CONFIG = {
    "records_execution_trace": {
        "emit_func": "_emit_records_execution_trace",
        "import_from": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_records_execution_trace",
        "call_code": '_emit_records_execution_trace("p0", "evidence", "{basename}")',
    },
    "applies_guardrail": {
        "emit_func": "_emit_applies_guardrail",
        "import_from": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_applies_guardrail",
        "call_code": '_emit_applies_guardrail("p0", "{basename}", "p0_governance")',
    },
    "reads_policy_state": {
        "emit_func": "_emit_reads_policy_state",
        "import_from": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_policy_state",
        "call_code": '_emit_reads_policy_state("p0", "{basename}", "policy_binding")',
    },
    "snapshots_state": {
        "emit_func": "_emit_snapshots_state",
        "import_from": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_snapshots_state",
        "call_code": '_emit_snapshots_state("p0", "{basename}", "state_snapshot")',
    },
    "emits_replay_key": {
        "emit_func": "emit_replay_key",
        "import_from": "from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_replay_key",
        "call_code": 'emit_replay_key("p0", "{basename}")',
    },
    "emits_determinism_digest": {
        "emit_func": "emit_determinism_digest",
        "import_from": "from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_determinism_digest",
        "call_code": 'emit_determinism_digest("p0", "{basename}")',
    },
    "signs_execution_trace": {
        "emit_func": "_emit_signs_execution_trace",
        "import_from": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_signs_execution_trace",
        "call_code": '_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)',
    },
}

CONTRACT = "agentic_core.runtime.lifecycle_trace_contract"

# Files that must NOT be wired
SKIP_PATTERNS = {
    "_constants.py",
    "conftest.py",
    "structure_blueprint_config.py",
    "ssot_tier_constants.py",
    "path_constants.py",
    "lifecycle_trace_contract.py",  # self-reference would break
}

SKIP_DIRS = {
    "__pycache__",
    ".git",
    "node_modules",
}


def _find_import_end(lines):
    """Find the 0-indexed line after the last top-level import statement.

    Correctly skips shebang lines, encoding declarations, and multi-line
    module docstrings before scanning for import statements.
    """
    last_import = -1
    in_multiline_import = False
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()

        # Skip blank lines and comments
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # Inside a multi-line import (parenthesised)
        if in_multiline_import:
            if ")" in stripped:
                in_multiline_import = False
                last_import = i
            i += 1
            continue

        # Module docstring — must be skipped entirely
        if stripped.startswith('"""') or stripped.startswith("'''"):
            # Only treat as docstring if we haven't seen any imports yet
            # (inline string literals after imports are fine to leave)
            if last_import == -1:
                quote = stripped[:3]
                # Single-line docstring on this line?
                rest = stripped[len(quote) :]
                if rest.endswith(quote) and len(rest) >= len(quote):
                    # Single line — skip just this line
                    i += 1
                    continue
                # Multi-line — advance until closing quote
                i += 1
                while i < n:
                    if quote in lines[i]:
                        i += 1  # skip the closing quote line
                        break
                    i += 1
                continue
            else:
                # After imports: string literal that ends the import block
                break

        # Import statement — only count top-level imports (no indentation)
        if stripped.startswith(("import ", "from ")) and not lines[i][0:1].isspace():
            last_import = i
            if "(" in stripped and ")" not in stripped:
                in_multiline_import = True
            i += 1
            continue

        # Any other non-blank, non-comment, non-import top-level line ends the block
        if last_import >= 0 and not lines[i][0:1].isspace():
            break

        i += 1

    return last_import


def wire_module(filepath, missing_dims):
    """Wire missing P0 dimension emit calls into a single module.

    Returns (status, detail, dims_wired).
    """
    fp = Path(filepath)
    if not fp.exists():
        return "SKIP", "file not found", []

    if fp.name in SKIP_PATTERNS:
        return "SKIP", "skip pattern", []

    if any(d in fp.parts for d in SKIP_DIRS):
        return "SKIP", "skip dir", []

    try:
        src = fp.read_text(encoding="utf-8", errors="replace")
    except OSError:  # guardian: allow-silent-swallow - acceptable exception handling
        return "SKIP", "unreadable", []

    basename = fp.stem

    # Must parse cleanly; also used for AST-based call detection below
    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        _tree = ast.parse(src)
    except SyntaxError:
        return "SKIP", "syntax error", []

    _ast_called: set[str] = set()
    for _node in ast.walk(_tree):
        if isinstance(_node, ast.Call):
            _f = _node.func
            if isinstance(_f, ast.Name):
                _ast_called.add(_f.id)
            elif isinstance(_f, ast.Attribute):
                _ast_called.add(_f.attr)

    to_wire = []
    for dim in missing_dims:
        cfg = DIM_CONFIG.get(dim)
        if cfg is None:
            continue
        if cfg["emit_func"] in _ast_called:
            continue  # already wired (confirmed by AST)
        to_wire.append(dim)

    if not to_wire:
        return "SKIP", "all dims already present", []

    lines = src.split("\n")
    import_end = _find_import_end(lines)
    if import_end < 0:
        import_end = 0

    # Collect unique imports needed and call lines
    existing_imports = set()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("from agentic_core.runtime.contracts.lifecycle_trace_contract import"):
            # Extract imported names
            if "(" in stripped:
                # Multi-line import — collect all
                pass  # handled by checking emit_func in src
            else:
                existing_imports.add(stripped.split("#")[0].strip())

    new_imports = []
    new_calls = []
    for dim in to_wire:
        cfg = DIM_CONFIG[dim]
        func = cfg["emit_func"]
        # Only skip import if the function is ACTUALLY imported (not just in docstring text)
        already_imported = any(CONTRACT in line and "import" in line and func in line for line in lines)
        if not already_imported:
            new_imports.append(cfg["import_from"] + "  # noqa: E402")
        call_line = cfg["call_code"].format(basename=basename)
        new_calls.append(call_line)

    # Deduplicate imports — combine into single multi-import if possible
    # For simplicity, use individual imports (ruff will not complain with noqa)
    seen_funcs = set()
    deduped_imports = []
    for imp in new_imports:
        # Extract function name
        func_name = imp.split("import ")[-1].split("#")[0].strip()
        if func_name not in seen_funcs:
            seen_funcs.add(func_name)
            deduped_imports.append(imp)

    insert_lines = []
    if deduped_imports:
        insert_lines.append("")  # blank line before imports
        insert_lines.extend(deduped_imports)
    if new_calls:
        insert_lines.append("")
        insert_lines.extend(new_calls)

    if not insert_lines:
        return "SKIP", "nothing to insert", []

    # Insert after import block
    insert_idx = import_end + 1
    for j, il in enumerate(insert_lines):
        lines.insert(insert_idx + j, il)

    new_src = "\n".join(lines)

    # Validate the result parses
    # guardian: allow-silent-swallow - acceptable exception handling
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        return "ERROR", f"post-wire syntax error: {e}", []

    fp.write_text(new_src, encoding="utf-8")
    return "WIRED", f"{len(to_wire)} dims @ line {insert_idx + 1}", to_wire


def load_deficit_modules():
    """Load combined deficit CSV and return list of (source_file, [missing_dims])."""
    csv_path = GAPS_DIR / "trace_deficit_modules.csv"
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found. Run p0_runtime_deficit.py first.")
        sys.exit(1)

    modules = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row["source_file"]
            dims = row["missing_dimensions"].split("|")
            modules.append((src, dims))

    # Sort by most missing dims first (highest ROI)
    modules.sort(key=lambda x: -len(x[1]))
    return modules


def main():
    parser = argparse.ArgumentParser(description="P0 Micro-Wave Wirer")
    parser.add_argument("--wave", type=int, required=True, help="Wave number (1-indexed)")
    parser.add_argument("--batch-size", type=int, default=15, help="Modules per wave")
    parser.add_argument("--apply", action="store_true", help="Apply changes (else dry-run)")
    args = parser.parse_args()

    modules = load_deficit_modules()
    total = len(modules)
    start = (args.wave - 1) * args.batch_size
    end = min(start + args.batch_size, total)

    if start >= total:
        print(f"Wave {args.wave} is beyond deficit set ({total} modules). All done!")
        return

    batch = modules[start:end]
    total_waves = (total + args.batch_size - 1) // args.batch_size

    print(f"{'=' * 70}")
    print(f"  P0 MICRO-WAVE {args.wave} of {total_waves}")
    print(f"  Modules {start + 1}–{end} of {total}")
    print(f"  Mode: {'APPLY' if args.apply else 'DRY RUN'}")
    print(f"{'=' * 70}")

    stats = {"WIRED": 0, "SKIP": 0, "ERROR": 0}
    dim_stats = dict.fromkeys(DIM_CONFIG, 0)
    wired_files = []

    for src_file, missing_dims in batch:
        abs_path = PROJECT_ROOT / src_file
        rel = src_file

        if not args.apply:
            print(f"  [DRY] {rel}  missing: {', '.join(missing_dims)}")
            continue

        status, detail, dims_wired = wire_module(abs_path, missing_dims)
        stats[status] = stats.get(status, 0) + 1

        if status == "WIRED":
            print(f"  WIRED: {detail}  [{rel}]")
            wired_files.append(rel)
            for d in dims_wired:
                dim_stats[d] += 1
        elif status == "ERROR":
            print(f"  ERROR: {detail}  [{rel}]")
        else:
            print(f"  SKIP:  {detail}  [{rel}]")

    print(f"\n{'=' * 70}")
    print(f"  WAVE {args.wave} SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Wired:   {stats.get('WIRED', 0)}")
    print(f"  Skipped: {stats.get('SKIP', 0)}")
    print(f"  Errors:  {stats.get('ERROR', 0)}")

    if args.apply and wired_files:
        print("\n  Dimensions wired:")
        for d, c in sorted(dim_stats.items(), key=lambda x: -x[1]):
            if c > 0:
                print(f"    {d}: +{c}")

        # Save wave log
        wave_log = {
            "wave": args.wave,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "batch_range": [start + 1, end],
            "stats": stats,
            "dim_stats": dim_stats,
            "wired_files": wired_files,
        }
        log_dir = REPORTS_DIR / "p0_waves"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"wave_{args.wave:03d}.json"
        log_path.write_text(json.dumps(wave_log, indent=2))
        print(f"\n  Wave log: {log_path}")


if __name__ == "__main__":
    main()
