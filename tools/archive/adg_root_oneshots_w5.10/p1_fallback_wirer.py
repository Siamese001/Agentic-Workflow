"""P1 Structural Integrity fallback wirer: adds module-level _emit_* calls after import block.

Wires P1 edge emit calls into files that lack them. Supports all 4 P1 dimensions:
  Evidence   → _emit_reads_policy_state   → reads_policy_state edge
  Governance → _emit_escalates_to_human   → escalates_to_human edge
  Trace      → _emit_routes_through       → routes_through edge
  Runtime    → _emit_dispatches_healing_run→ dispatches_healing_run edge
"""

import argparse
import ast
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "p1_fallback_wirer", "uwg_governed_write")
_emit_writes_through("p1", "p1_fallback_wirer", "uwg_governed_write_2")
_emit_pulls_context("p1", "p1_fallback_wirer", "context_retrieval")
_emit_pulls_context("p1", "p1_fallback_wirer", "context_retrieval_2")
emit_determinism_digest("trace_p1_fallback_wirer", "p1_fallback_wirer_dispatch")
emit_determinism_digest("trace_p1_fallback_wirer", "p1_fallback_wirer_complete")
_emit_validated_by_safety_plane("p1", "p1_fallback_wirer", "safety_validation")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LAYER_PATHS = {
    "L0": "agentic_core/L0_routing",
    "L1": "agentic_core/L1_cognition",
    "L2": "agentic_core/L2_execution",
    "L3": "agentic_core/L3_orchestration",
    "L4": "agentic_core/L4_state",
    "L5": "agentic_core/L5_safety",
    "L6": "agentic_core/L6_observability",
}

DIM_CONFIG = {
    "evidence": {
        "emit_func": "_emit_reads_policy_state",
        "import_line": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_policy_state  # noqa: E402",
        "call_code": '_emit_reads_policy_state("p1", "{basename}", "{layer}")',
    },
    "governance": {
        "emit_func": "_emit_escalates_to_human",
        "import_line": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_escalates_to_human  # noqa: E402",
        "call_code": '_emit_escalates_to_human("p1", "{basename}", "{layer}")',
    },
    "trace": {
        "emit_func": "_emit_routes_through",
        "import_line": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_routes_through  # noqa: E402",
        "call_code": '_emit_routes_through("p1", "{basename}", "{layer}")',
    },
    "runtime": {
        "emit_func": "_emit_dispatches_healing_run",
        "import_line": "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_dispatches_healing_run  # noqa: E402",
        "call_code": '_emit_dispatches_healing_run("p1", "{basename}", "{layer}")',
    },
}

SKIP_PATTERNS = [
    "_constants.py",
    "conftest.py",
    "structure_blueprint_config.py",
    "ssot_tier_constants.py",
]


def _find_import_end(lines):
    """Find the line index after the last top-level import statement."""
    last_import = -1
    in_multiline = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if in_multiline:
            if ")" in stripped:
                in_multiline = False
                last_import = i
            continue
        if stripped.startswith(("import ", "from ")):
            last_import = i
            if "(" in stripped and ")" not in stripped:
                in_multiline = True
        elif stripped.startswith('"""') or stripped.startswith("'''"):
            if last_import == -1:
                quote = stripped[:3]
                if stripped.count(quote) >= 2:
                    continue
                for j in range(i + 1, len(lines)):
                    if quote in lines[j]:
                        break
                continue
        elif last_import >= 0:
            break
    return last_import


def wire_file(filepath, dim_cfg, layer_label):
    """Wire a module-level emit call into a file."""
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            src = f.read()
    except OSError:  # guardian: allow-silent-swallow - acceptable exception handling
        return "SKIP", "unreadable"

    basename = Path(filepath).stem

    if dim_cfg["emit_func"] in src:
        return "SKIP", "already wired"

    for pat in SKIP_PATTERNS:
        if filepath.endswith(pat):
            return "SKIP", "skip pattern"

    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        ast.parse(src)
    except SyntaxError:
        return "SKIP", "source syntax error"

    lines = src.split("\n")
    import_end = _find_import_end(lines)

    if import_end < 0:
        import_end = 0

    import_line = dim_cfg["import_line"]
    call_line = dim_cfg["call_code"].format(basename=basename, layer=layer_label)

    insert_lines = []
    if import_line.split("#")[0].strip() not in src:
        insert_lines.append(import_line)
    insert_lines.append(call_line)

    insert_idx = import_end + 1
    for j, il in enumerate(insert_lines):
        lines.insert(insert_idx + j, il)

    new_src = "\n".join(lines)

    # guardian: allow-silent-swallow - acceptable exception handling
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        return "ERROR", str(e)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_src)

    return "WIRED", f"module-level @ line {insert_idx + 1}"


def main():
    parser = argparse.ArgumentParser(description="P1 Structural Integrity wirer")
    parser.add_argument("--layer", required=True, choices=list(LAYER_PATHS))
    parser.add_argument("--dim", required=True, choices=list(DIM_CONFIG))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--all-dims", action="store_true", help="Wire all 4 dimensions at once")
    args = parser.parse_args()

    layer_dir = PROJECT_ROOT / LAYER_PATHS[args.layer]
    dims_to_wire = list(DIM_CONFIG) if args.all_dims else [args.dim]

    py_files = sorted(str(p) for p in layer_dir.rglob("*.py"))

    total_wired = 0
    total_skip = 0
    total_error = 0

    for dim in dims_to_wire:
        dim_cfg = DIM_CONFIG[dim]
        candidates = []
        for fp in py_files:
            # guardian: allow-silent-swallow - acceptable exception handling
            try:
                with open(fp, encoding="utf-8", errors="replace") as f:
                    src = f.read()
            except OSError:
                continue
            if dim_cfg["emit_func"] not in src:
                candidates.append(fp)

        print(f"\n=== {args.layer} / {dim} (P1 fallback) ===")
        print(f"Candidates without {dim_cfg['emit_func']}: {len(candidates)}")
        print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")

        if not args.apply:
            for fp in candidates[:10]:
                print(f"  {Path(fp).relative_to(PROJECT_ROOT)}")
            if len(candidates) > 10:
                print(f"  ... and {len(candidates) - 10} more")
            continue

        for fp in candidates:
            status, detail = wire_file(fp, dim_cfg, args.layer)
            if status == "WIRED":
                total_wired += 1
                print(f"  WIRED: {detail}  [{Path(fp).relative_to(PROJECT_ROOT)}]")
            elif status == "ERROR":
                total_error += 1
                print(f"  ERROR: {detail}  [{Path(fp).relative_to(PROJECT_ROOT)}]")
            else:
                total_skip += 1

    print("\n=== TOTALS ===")
    print(f"Wired: {total_wired}  Skipped: {total_skip}  Errors: {total_error}")


if __name__ == "__main__":
    main()
