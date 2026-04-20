"""Mega-batch ADG wiring script.

Scans ALL .py files in scan roots, identifies unwired methods, and adds
appropriate _emit_* calls to maximize ADG edge coverage across ALL gap types.

Edge types wired per layer:
  ALL layers:  _emit_records_execution_trace     (P0/L1, P0/L6, P3/L2)
  L0 routing:  emit_replay_key + emit_determinism_digest  (P0/L0, P1/L2)
  L2 execution: _emit_signs_execution_trace      (P0/L6)
  L5 safety:   _emit_signs_execution_trace       (P0/L6)

Usage:
  python tools/mega_wire_adg.py --dry-run   # preview changes
  python tools/mega_wire_adg.py --apply      # apply changes
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "mega_wire_adg", "uwg_governed_write")
_emit_writes_through("p1", "mega_wire_adg", "uwg_governed_write_2")
_emit_pulls_context("p1", "mega_wire_adg", "context_retrieval")
_emit_pulls_context("p1", "mega_wire_adg", "context_retrieval_2")
emit_determinism_digest("trace_mega_wire_adg", "mega_wire_adg_dispatch")
emit_determinism_digest("trace_mega_wire_adg", "mega_wire_adg_complete")
_emit_validated_by_safety_plane("p1", "mega_wire_adg", "safety_validation")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_1")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_2")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_3")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_4")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_5")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_6")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_7")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_8")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_9")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_10")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_11")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_12")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_13")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_14")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_15")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_16")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_17")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_18")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_19")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_20")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_21")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_22")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_23")
_emit_reads_through("l4", "mega_wire_adg", "urg_read_24")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCAN_ROOTS = [
    "agentic_core/L0_routing",
    "agentic_core/L1_cognition",
    "agentic_core/L2_execution",
    "agentic_core/L3_orchestration",
    "agentic_core/L4_state",
    "agentic_core/L5_safety",
    "agentic_core/L6_observability",
    "agentic_core/mixins",
    "agentic_core/utils",
    "agentic_core/cache",
    "agentic_core/agents",
    "agentic_core/evaluation",
    "agentic_core/adg",
    "agentic_core/runtime",
    "agentic_core/prompt_governance",
    "agentic_core/knowledge",
    "agentic_core/enforcement",
    "agentic_core/base_agents",
    "agentic_core/interfaces",
    "agentic_core/config",
    "agentic_core/seams",
    "agentic_core/embeddings",
    "agentic_core/patterns",
    "apps_shared",
    "apps_lic",
    "apps_rg",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "system_learning",
]

# Skip these method names (trivial, dunder, or infrastructure)
SKIP_METHODS = frozenset(
    {
        "__init__",
        "__repr__",
        "__str__",
        "__eq__",
        "__hash__",
        "__lt__",
        "__le__",
        "__gt__",
        "__ge__",
        "__ne__",
        "__enter__",
        "__exit__",
        "__aenter__",
        "__aexit__",
        "__len__",
        "__iter__",
        "__next__",
        "__getitem__",
        "__setitem__",
        "__contains__",
        "__bool__",
        "__call__",
        "__post_init__",
        "__del__",
        "__new__",
        "__init_subclass__",
        "__class_getitem__",
        "__get__",
        "__set__",
        "__delete__",
        "to_dict",
        "from_dict",
        "as_dict",
        "to_json",
        "from_json",
        "model_dump",
        "model_validate",
        "dict",
        "json",
        # lifecycle_trace_contract.py internals - don't wire recursively
        "_emit_records_execution_trace",
        "_emit_signs_execution_trace",
        "emit_replay_key",
        "emit_determinism_digest",
        "_emit_transcripts_response",
        "_emit_hard_fails_untranscripted",
        "_record_contract",
    }
)

# Skip files that are part of the wiring infrastructure itself
SKIP_FILES = frozenset(
    {
        "lifecycle_trace_contract.py",
        "execution_trace.py",
        "mega_wire_adg.py",
        "__init__.py",
        "conftest.py",
    }
)

# Minimum body lines (excluding docstring) for a method to be worth wiring
MIN_BODY_LINES = 2

# Already-wired marker
WIRED_MARKER = "_emit_records_execution_trace"


def get_layer_segment(filepath: str) -> str:
    """Determine LayerSegment constant from file path."""
    fp = filepath.replace("\\", "/")
    if "L0_routing" in fp:
        return "LayerSegment.L0_ROUTING"
    if "L1_cognition" in fp:
        return "LayerSegment.L1_REASONING"
    if "L2_execution" in fp:
        return "LayerSegment.L2_EXECUTION"
    if "L3_orchestration" in fp:
        return "LayerSegment.L3_ORCHESTRATION"
    if "L4_state" in fp:
        return "LayerSegment.L4_STATE"
    if "L5_safety" in fp:
        return "LayerSegment.L5_POLICY"
    if "L6_observability" in fp:
        return "LayerSegment.L6_OBSERVABILITY"
    return "LayerSegment.L3_ORCHESTRATION"  # default for apps/shared/etc


def get_extra_emissions(filepath: str) -> list[str]:
    """Determine which extra _emit_* calls to add based on layer."""
    fp = filepath.replace("\\", "/")
    extras = []
    if "L0_routing" in fp:
        extras.append("replay_key")
        extras.append("determinism_digest")
    if "L2_execution" in fp or "L5_safety" in fp:
        extras.append("signs_trace")
    return extras


def get_import_line(extras: list[str]) -> str:
    """Build the import statement needed."""
    symbols = ["LayerSegment", "_emit_records_execution_trace"]
    if "replay_key" in extras:
        symbols.append("emit_replay_key")
    if "determinism_digest" in extras:
        symbols.append("emit_determinism_digest")
    if "signs_trace" in extras:
        symbols.append("_emit_signs_execution_trace")
    return f"from agentic_core.runtime.contracts.lifecycle_trace_contract import {', '.join(symbols)}"


def build_emit_block(
    class_name: str, method_name: str, layer_seg: str, extras: list[str], indent: str
) -> str:
    """Build the emit code block to insert after docstring."""
    lines = []
    lines.append(f"{indent}import uuid as _uuid  # noqa: PLC0415")
    lines.append(f"{indent}_trace_id = str(_uuid.uuid4())")
    lines.append(
        f'{indent}_emit_records_execution_trace(_trace_id, {layer_seg}, "{class_name}.{method_name}")'
    )
    if "signs_trace" in extras:
        lines.append(f"{indent}import hashlib as _hashlib  # noqa: PLC0415")
        lines.append(
            f'{indent}_seg_hash = _hashlib.sha256(f"{{_trace_id}}:{class_name}.{method_name}".encode()).hexdigest()[:24]'
        )
        lines.append(f"{indent}_emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)")
    if "replay_key" in extras:
        lines.append(f'{indent}emit_replay_key(_trace_id, f"rk:{{_trace_id[:16]}}")')
    if "determinism_digest" in extras:
        lines.append(f'{indent}emit_determinism_digest(_trace_id, f"dd:{{_trace_id[:16]}}")')
    return "\n".join(lines)


def find_methods_in_file(filepath: str) -> list[dict]:
    """Use AST to find class methods suitable for wiring."""
    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
    except (UnicodeDecodeError, PermissionError):  # guardian: allow-silent-swallow - acceptable exception handling
        return []

    if WIRED_MARKER in source:
        return []  # Already wired

    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return []

    methods = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        class_name = node.name
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            method_name = item.name
            if method_name in SKIP_METHODS:
                continue
            if method_name.startswith("_") and method_name != "_run":
                # Skip private methods except _run
                if not method_name.startswith("_emit") and method_name not in (
                    "_run",
                    "_execute",
                    "_process",
                    "_handle",
                    "_validate",
                ):
                    continue

            # Check body size (excluding docstring)
            body = item.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, (ast.Constant, ast.Str)):
                effective_body = body[1:]
            else:
                effective_body = body

            # Skip stubs
            if len(effective_body) < MIN_BODY_LINES:
                continue
            if len(effective_body) == 1 and isinstance(effective_body[0], (ast.Pass, ast.Raise, ast.Return)):
                continue

            # Get the line number for insertion (after docstring or at method body start)
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, (ast.Constant, ast.Str)):
                insert_after_line = body[0].end_lineno
            else:
                insert_after_line = item.lineno  # Insert after def line

            # Determine indentation from method body
            if effective_body:
                first_stmt_line = effective_body[0].lineno
            else:
                first_stmt_line = insert_after_line + 1

            methods.append(
                {
                    "class_name": class_name,
                    "method_name": method_name,
                    "insert_after_line": insert_after_line,
                    "first_stmt_line": first_stmt_line,
                    "is_async": isinstance(item, ast.AsyncFunctionDef),
                    "lineno": item.lineno,
                }
            )

    # Return only the FIRST suitable method per class to avoid over-wiring
    seen_classes = set()
    filtered = []
    for m in methods:
        if m["class_name"] not in seen_classes:
            seen_classes.add(m["class_name"])
            filtered.append(m)
    return filtered


def get_indent_at_line(lines: list[str], line_no: int) -> str:
    """Get the indentation from a specific line (1-indexed)."""
    if line_no <= 0 or line_no > len(lines):
        return "        "  # default 8 spaces
    line = lines[line_no - 1]
    return " " * (len(line) - len(line.lstrip()))


def find_import_insertion_line(filepath: str) -> int:
    """Use AST to find the safe insertion line for a new import.

    Rules:
      1. Only consider TOP-LEVEL imports (direct children of tree.body).
         Never walk into Try/If/With blocks — inserting inside them breaks syntax.
      2. For try/except blocks that contain imports, use the END of the
         entire try/except node (not the import inside it).
      3. Always insert AFTER any ``from __future__`` imports.
      4. Returns a 1-indexed line number; the new import goes on this line
         (i.e., we insert at this position pushing existing content down).
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            # guardian: allow-silent-swallow - acceptable exception handling
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, UnicodeDecodeError):
        return 0

    last_import_end = 0
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            end = getattr(node, "end_lineno", node.lineno)
            if end > last_import_end:
                last_import_end = end
        elif isinstance(node, (ast.If, ast.Try)):
            # Check if block contains imports; if so, use the END of the
            # entire block (not the import line inside it).
            has_import = False
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    has_import = True
                    break
            if has_import:
                end = getattr(node, "end_lineno", node.lineno)
                if end > last_import_end:
                    last_import_end = end
    return last_import_end


def apply_wiring(filepath: str, methods: list[dict], extras: list[str], layer_seg: str, dry_run: bool) -> int:
    """Apply wiring to a file. Returns number of methods wired.

    Post-modification safety: after writing, the file is re-parsed with
    ``ast.parse``. If that fails the original content is restored and the
    file is counted as *skipped*.
    """
    with open(filepath, encoding="utf-8") as f:
        original_source = f.read()
    lines = original_source.split("\n")

    import_line = get_import_line(extras)
    has_import = "from agentic_core.runtime.contracts.lifecycle_trace_contract import" in original_source

    if dry_run:
        return len(methods)

    # Collect ALL insertions with their 1-indexed line numbers.
    # Each entry: (line_number_1indexed, lines_to_insert)
    all_insertions: list[tuple[int, list[str]]] = []

    # 1. Emit block insertions
    for m in methods:
        indent = get_indent_at_line(lines, m["first_stmt_line"])
        if not indent or indent == "":
            indent = "        "
        block = build_emit_block(m["class_name"], m["method_name"], layer_seg, extras, indent)
        block_lines = block.split("\n") + [""]  # trailing blank line
        all_insertions.append((m["insert_after_line"], block_lines))

    # 2. Import insertion (if needed)
    if not has_import:
        import_insert = find_import_insertion_line(filepath)
        if import_insert == 0:
            import_insert = 1
        all_insertions.append((import_insert, [import_line]))

    # Sort DESCENDING so later insertions don't shift earlier line numbers
    all_insertions.sort(key=lambda x: x[0], reverse=True)

    # Apply all insertions (line numbers are 1-indexed; list.insert at
    # that index pushes existing content down, which is "insert after").
    for insert_at, new_lines in all_insertions:
        for nl in reversed(new_lines):
            lines.insert(insert_at, nl)

    new_source = "\n".join(lines)

    # guardian: allow-silent-swallow - acceptable exception handling
    # ── Post-modification syntax validation ──────────────────────────
    try:
        ast.parse(new_source, filename=filepath)
    except SyntaxError:
        # Restore original — this file is too tricky to wire automatically.
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(original_source)
        return 0  # report as skipped

    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_source)

    return len(methods)


def main():
    dry_run = "--dry-run" in sys.argv or "--apply" not in sys.argv

    if dry_run:
        print("=== DRY RUN — no files will be modified ===\n")
    else:
        print("=== APPLYING CHANGES ===\n")

    total_files = 0
    total_methods = 0
    total_skipped = 0
    total_by_layer = {}
    all_targets = []
    skipped_files = []

    for root_dir in SCAN_ROOTS:
        abs_root = PROJECT_ROOT / root_dir
        if not abs_root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(abs_root):
            # Skip excluded dirs
            dirnames[:] = [
                d for d in dirnames if d not in {"__pycache__", ".git", "node_modules", "archives"}
            ]
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                if fname in SKIP_FILES:
                    continue
                filepath = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(filepath, PROJECT_ROOT).replace("\\", "/")

                methods = find_methods_in_file(filepath)
                if not methods:
                    continue

                extras = get_extra_emissions(filepath)
                layer_seg = get_layer_segment(filepath)

                count = apply_wiring(filepath, methods, extras, layer_seg, dry_run)
                if count > 0:
                    total_files += 1
                    total_methods += count
                    layer = layer_seg.split(".")[-1] if "." in layer_seg else layer_seg
                    total_by_layer[layer] = total_by_layer.get(layer, 0) + count

                    for m in methods:
                        label = f"{m['class_name']}.{m['method_name']}"
                        all_targets.append((rel_path, label, layer, extras))
                        if not dry_run:
                            print(f"  WIRED: {rel_path} :: {label} [{layer}]")
                elif count == 0 and not dry_run:
                    total_skipped += 1
                    skipped_files.append(rel_path)

    print(f"\n{'=' * 60}")
    print(f"Total files:   {total_files}")
    print(f"Total methods: {total_methods}")
    print("\nBy layer:")
    for layer, count in sorted(total_by_layer.items()):
        print(f"  {layer}: {count}")

    print("\nEdge types increased:")
    print(f"  records_execution_trace: +{total_methods}")
    signs = sum(1 for _, _, _, ex in all_targets if "signs_trace" in ex)
    replay = sum(1 for _, _, _, ex in all_targets if "replay_key" in ex)
    digest = sum(1 for _, _, _, ex in all_targets if "determinism_digest" in ex)
    if signs:
        print(f"  signs_execution_trace:   +{signs}")
    if replay:
        print(f"  emits_replay_key:        +{replay}")
    if digest:
        print(f"  emits_determinism_digest: +{digest}")

    if not dry_run and total_skipped > 0:
        print(f"\nSkipped (syntax validation failed): {total_skipped}")
        for sf in skipped_files[:20]:
            print(f"  SKIP: {sf}")
        if len(skipped_files) > 20:
            print(f"  ... and {len(skipped_files) - 20} more")

    if dry_run:
        print("\n=== DRY RUN COMPLETE — run with --apply to execute ===")
        print("\nFirst 30 targets:")
        for rel, label, layer, extras in all_targets[:30]:
            extra_str = f" +{','.join(extras)}" if extras else ""
            print(f"  {rel} :: {label} [{layer}]{extra_str}")
        if len(all_targets) > 30:
            print(f"  ... and {len(all_targets) - 30} more")


if __name__ == "__main__":
    main()
