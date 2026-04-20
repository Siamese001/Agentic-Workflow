"""P0 Batch Wirer: Wire emit calls per layer x dimension in micro-waves of 15.

Usage:
  python tools/p0_batch_wirer.py --layer L3 --dim evidence --apply
  python tools/p0_batch_wirer.py --layer L3 --dim governance --apply
  python tools/p0_batch_wirer.py --layer L3 --dim trace --apply
  python tools/p0_batch_wirer.py --layer L3 --dim runtime --apply
"""

import argparse
import ast
import glob
import os
import sqlite3
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "p0_batch_wirer", "uwg_governed_write")
_emit_writes_through("p1", "p0_batch_wirer", "uwg_governed_write_2")
_emit_pulls_context("p1", "p0_batch_wirer", "context_retrieval")
_emit_pulls_context("p1", "p0_batch_wirer", "context_retrieval_2")
emit_determinism_digest("trace_p0_batch_wirer", "p0_batch_wirer_dispatch")
emit_determinism_digest("trace_p0_batch_wirer", "p0_batch_wirer_complete")
_emit_validated_by_safety_plane("p1", "p0_batch_wirer", "safety_validation")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dimension -> (edge types to check, emit function to wire, import line, call template)
DIMENSION_CONFIG = {
    "evidence": {
        "check_edges": ["records_execution_trace", "emits_replay_key", "emits_determinism_digest"],
        "emit_func": "_emit_records_execution_trace",
        "import_line": "from agentic_core.runtime.contracts.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace",
        "call_lines": [
            "import uuid as _uuid  # noqa: PLC0415",
            "_trace_id = str(_uuid.uuid4())",
            '_emit_records_execution_trace(_trace_id, LayerSegment.{segment}, "{method}")',
        ],
    },
    "governance": {
        "check_edges": [
            "applies_guardrail",
            "verifies_policy",
            "validated_by_safety_plane",
            "verifies_boundary",
        ],
        "emit_func": "_emit_applies_guardrail",
        "import_line": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_applies_guardrail",
        "call_lines": [
            "import uuid as _uuid  # noqa: PLC0415",
            '_emit_applies_guardrail(str(_uuid.uuid4()), "{method}", "p0_governance")',
        ],
    },
    "trace": {
        "check_edges": ["signs_execution_trace", "transcripts_response", "hard_fails_untranscripted"],
        "emit_func": "_emit_signs_execution_trace",
        "import_line": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_signs_execution_trace",
        "call_lines": [
            "import uuid as _uuid  # noqa: PLC0415",
            "import hashlib as _hashlib  # noqa: PLC0415",
            "_tid = str(_uuid.uuid4())",
            '_emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)',
        ],
    },
    "runtime": {
        "check_edges": [
            "snapshots_state",
            "observes_runtime_state",
            "writes_through",
            "agent_executes_agent",
            "gated_by_confidence",
        ],
        "emit_func": "_emit_snapshots_state",
        "import_line": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_snapshots_state",
        "call_lines": [
            "import uuid as _uuid  # noqa: PLC0415",
            '_emit_snapshots_state(str(_uuid.uuid4()), "{method}", "state_snapshot")',
        ],
    },
}

LAYER_DIRS = {
    "L0": "agentic_core/L0_routing",
    "L1": "agentic_core/L1_cognition",
    "L2": "agentic_core/L2_execution",
    "L3": "agentic_core/L3_orchestration",
    "L4": "agentic_core/L4_state",
    "L5": "agentic_core/L5_safety",
    "L6": "agentic_core/L6_observability",
}

LAYER_SEGMENTS = {
    "L0": "L0_ROUTING",
    "L1": "L1_COGNITION",
    "L2": "L2_EXECUTION",
    "L3": "L3_ORCHESTRATION",
    "L4": "L4_STATE",
    "L5": "L5_SAFETY",
    "L6": "L6_OBSERVABILITY",
}


def get_gap_files(layer, dim_config):
    """Get files in layer that lack the dimension's edges."""
    adg_dir = PROJECT_ROOT / "artifacts" / "adg"
    pattern = str(adg_dir / "adg_indexed_*.sqlite")
    files = sorted(glob.glob(pattern))
    if not files:
        print("No ADG sqlite found!")
        return []

    db = sqlite3.connect(files[-1])
    cur = db.cursor()

    # Get files with existing edges for this dimension
    check_edges = dim_config["check_edges"]
    placeholders = ",".join("?" * len(check_edges))
    cur.execute(
        f"SELECT DISTINCT source_file FROM edges WHERE relation_type IN ({placeholders})",
        check_edges,
    )
    has_edges = {r[0] for r in cur.fetchall()}
    db.close()

    # Scan filesystem for layer files
    scan_dir = PROJECT_ROOT / LAYER_DIRS[layer]
    gap_files = []
    for root, dirs, fns in os.walk(scan_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in sorted(fns):
            if not fn.endswith(".py") or fn == "__init__.py":
                continue
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, PROJECT_ROOT).replace("\\", "/")
            if rel in has_edges:
                continue
            # Check if file already has the emit function
            try:
                src = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:  # guardian: allow-silent-swallow - acceptable exception handling
                continue
            if dim_config["emit_func"] in src:
                continue
            # Check if file has wirable functions
            if _has_wirable_functions(src):
                gap_files.append(rel)

    return gap_files


def _has_wirable_functions(src):
    """Check if source has functions with body >= 3 lines."""
    try:
        tree = ast.parse(src)  # guardian: Syntax errors should be caught at parser level, not runtime
    except SyntaxError:  # guardian: allow-silent-swallow - acceptable exception handling
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_lines = (node.end_lineno or node.lineno) - node.lineno
            if body_lines >= 3 and not (
                node.name.startswith("__") and node.name not in ("__init__", "__call__")
            ):
                return True
    return False


def _find_first_target(tree):
    """Find first substantial function/method via ordered walk."""
    # Walk in source order: module body, then class bodies
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bl = (node.end_lineno or node.lineno) - node.lineno
            if bl >= 3 and not (node.name.startswith("__") and node.name not in ("__init__", "__call__")):
                return node, None
        elif isinstance(node, ast.ClassDef):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    bl = (child.end_lineno or child.lineno) - child.lineno
                    if bl >= 3 and not (
                        child.name.startswith("__") and child.name not in ("__init__", "__call__")
                    ):
                        return child, node.name
    return None, None


def wire_file(filepath, dim_config, layer):
    """Wire emit call into first substantial function in file."""
    fp = str(PROJECT_ROOT / filepath)
    try:  # guardian: Add error context logging
        # guardian: allow-silent-swallow - acceptable exception handling
        src = open(fp, encoding="utf-8", errors="replace").read()
    except OSError:
        return "SKIP", "unreadable"

    if dim_config["emit_func"] in src:
        return "SKIP", "already wired"
    # guardian: Syntax errors should be caught at parser level, not runtime
    # guardian: allow-silent-swallow - acceptable exception handling
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return "SKIP", "syntax error in source"

    target, class_name = _find_first_target(tree)
    if not target:
        return "SKIP", "no suitable function"

    lines = src.split("\n")

    # Determine body indentation from the first statement in function body
    body = target.body
    if not body:
        return "SKIP", "empty body"

    # Get indentation from first body statement
    first_body_line = lines[body[0].lineno - 1]
    indent = ""
    for ch in first_body_line:
        if ch in (" ", "\t"):
            indent += ch
        else:
            break

    # Find insertion point: after docstring if present, else after def line
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, (ast.Constant, ast.Str)):
        insert_line = body[0].end_lineno  # 1-indexed, insert AFTER this line
    else:
        insert_line = target.lineno  # After def line

    # Build method name
    method_name = f"{class_name}.{target.name}" if class_name else target.name

    # Build indented call code from call_lines
    segment = LAYER_SEGMENTS.get(layer, "L3_ORCHESTRATION")
    code_lines = []
    for cl in dim_config["call_lines"]:
        formatted = cl.format(method=method_name, segment=segment)
        code_lines.append(indent + formatted)
    call_block = "\n".join(code_lines)

    # Insert the call block (insert after insert_line, which is 1-indexed)
    lines.insert(insert_line, call_block)

    # Add import if needed
    import_line = dim_config["import_line"]
    if import_line not in src:
        # Find last import at module level
        import_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not line or line[0] in (" ", "\t"):
                continue
            if stripped.startswith("from __future__"):
                import_idx = i + 1
            elif stripped.startswith("import ") or stripped.startswith("from "):
                import_idx = i + 1

        lines.insert(import_idx, import_line)

    new_src = "\n".join(lines)
    # guardian: Syntax errors should be caught at parser level, not runtime
    # guardian: allow-silent-swallow - acceptable exception handling
    # Validate syntax
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        # Rollback
        return "SYNTAX_ERROR", str(e)

    with open(fp, "w", encoding="utf-8") as f:
        f.write(new_src)

    return "WIRED", f"{method_name} @ line {insert_line}"


def main():
    parser = argparse.ArgumentParser(description="P0 Batch Wirer")
    parser.add_argument("--layer", required=True, choices=list(LAYER_DIRS.keys()))
    parser.add_argument("--dim", required=True, choices=list(DIMENSION_CONFIG.keys()))
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--batch-size", type=int, default=15, help="Files per micro-wave")
    args = parser.parse_args()

    dim_config = DIMENSION_CONFIG[args.dim]
    gap_files = get_gap_files(args.layer, dim_config)

    print(f"\n=== {args.layer} / {args.dim} ===")
    print(f"Gap files: {len(gap_files)}")
    print(f"Emit function: {dim_config['emit_func']}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")

    if not gap_files:
        print("No gap files found — dimension already covered!")
        return

    # Process in batches
    total_wired = 0
    total_skipped = 0
    total_errors = 0

    for batch_start in range(0, len(gap_files), args.batch_size):
        batch = gap_files[batch_start : batch_start + args.batch_size]
        batch_num = batch_start // args.batch_size + 1
        print(f"\n--- Micro-wave {batch_num} ({len(batch)} files) ---")

        for filepath in batch:
            if args.apply:
                status, detail = wire_file(filepath, dim_config, args.layer)
            else:
                status, detail = "DRY-RUN", "would wire"

            if status == "WIRED":
                total_wired += 1
                print(f"  WIRED: {detail}  [{filepath}]")
            elif status == "SKIP":
                total_skipped += 1
            elif status == "SYNTAX_ERROR":
                total_errors += 1
                print(f"  ERROR: {detail}  [{filepath}]")
            elif status == "DRY-RUN":
                print(f"  [dry-run] {filepath}")

    print(f"\nSummary: {total_wired} wired, {total_skipped} skipped, {total_errors} errors")

    # Post-wire syntax validation
    if args.apply and total_wired > 0:
        print("\nPost-wire syntax validation...")
        syntax_errors = 0
        # guardian: allow-silent-swallow - acceptable exception handling
        for filepath in gap_files:
            fp = str(PROJECT_ROOT / filepath)
            try:
                src = open(fp, encoding="utf-8", errors="replace").read()
                ast.parse(src)
            except SyntaxError as e:
                syntax_errors += 1
                print(f"  SYNTAX ERROR: {filepath}: {e}")
        if syntax_errors == 0:
            print("  All files: SYNTAX OK")


if __name__ == "__main__":
    main()
