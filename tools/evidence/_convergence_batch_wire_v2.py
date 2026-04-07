"""Batch wire convergence blocker modules with scanner-visible calls (v2).

Uses AST parsing to find the correct module-level insertion point,
avoiding the indentation bugs of v1.

Strategy:
1. Parse the file as AST to find the last top-level import statement line
2. Insert import + call lines AFTER that point, at column 0
3. For modules needing emit_determinism_digest(): add import + call
4. For modules needing record_execution_trace(): add import + call
"""
from __future__ import annotations

import ast
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT_JSON = os.path.join(ROOT, "artifacts", "adg", "_convergence_wiring_audit.json")

with open(AUDIT_JSON) as f:
    audit = json.load(f)

digest_needs = set(audit["digest_needs_call"])
trace_needs = set(audit["trace_needs_call"])
all_modules = digest_needs | trace_needs

stats = {
    "digest_added": 0,
    "trace_added": 0,
    "import_added": 0,
    "skipped": 0,
    "errors": [],
}


def find_last_import_line(source: str) -> int:
    """Find the 1-indexed line number of the last top-level import statement.

    Returns 0 if no imports found (insert at top after docstring).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
        return 0

    last_import_line = 0
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # end_lineno gives the last line of multi-line imports
            end = getattr(node, "end_lineno", node.lineno)
            if end > last_import_line:
                last_import_line = end
    return last_import_line


def find_existing_lifecycle_import_line(lines: list[str]) -> int | None:
    """Find if there's already an import from lifecycle_trace_contract.

    Returns 0-indexed line number of the 'from agentic_core.runtime.contracts.lifecycle_trace_contract import'
    line, or None.
    """
    for i, line in enumerate(lines):
        if "from agentic_core.runtime.contracts.lifecycle_trace_contract import" in line:
            return i
    return None


def get_module_short_name(module_path: str) -> str:
    return os.path.basename(module_path).replace(".py", "")


def wire_module(module_rel: str) -> None:
    fpath = os.path.join(ROOT, module_rel)
    if not os.path.exists(fpath):
        stats["errors"].append(f"MISSING: {module_rel}")
        return

    with open(fpath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    original = content
    short_name = get_module_short_name(module_rel)
    needs_digest = module_rel in digest_needs
    needs_trace = module_rel in trace_needs

    # Check existing state
    has_digest_call = bool(re.search(r"(?<!\w)emit_determinism_digest\s*\(", content))
    has_trace_call = bool(re.search(r"(?<!\w)record_execution_trace\s*\(", content))

    # Determine what symbols we need to import
    symbols_to_import = []
    if needs_digest and not has_digest_call:
        symbols_to_import.append("emit_determinism_digest")
    if needs_trace and not has_trace_call:
        symbols_to_import.append("record_execution_trace")

    if not symbols_to_import:
        stats["skipped"] += 1
        return

    lines = content.split("\n")

    # Find the last top-level import line using AST
    last_import_line_1idx = find_last_import_line(content)

    # Check if there's already an import from lifecycle_trace_contract
    existing_import_idx = find_existing_lifecycle_import_line(lines)

    # Build the import block and call block
    import_symbols = ", ".join(symbols_to_import)

    call_lines = []
    if needs_digest and not has_digest_call:
        call_lines.append(f'emit_determinism_digest("{short_name}", "{short_name}_digest")')
        stats["digest_added"] += 1
    if needs_trace and not has_trace_call:
        call_lines.append(f'record_execution_trace("{short_name}", "{short_name}_trace")')
        stats["trace_added"] += 1

    if existing_import_idx is not None:
        # There's already an import from lifecycle_trace_contract
        # We need to add our symbols to it
        # Find the closing paren of the existing import
        idx = existing_import_idx
        if "(" in lines[idx]:
            # Multi-line import, find the closing )
            close_idx = idx
            while close_idx < len(lines) and ")" not in lines[close_idx]:
                close_idx += 1
            # Insert our symbols before the closing )
            for sym in symbols_to_import:
                if sym not in content:
                    insert_line = f"    {sym},"
                    lines.insert(close_idx, insert_line)
                    close_idx += 1
                    stats["import_added"] += 1
        else:
            # Single-line import like: from ... import something
            # Convert to multi-line and add our symbols
            old_line = lines[idx]
            match = re.match(r"(from .+ import )(.*)", old_line)
            if match:
                prefix = match.group(1)
                existing = match.group(2).strip().rstrip(",")
                new_lines = [f"{prefix}("]
                new_lines.append(f"    {existing},")
                for sym in symbols_to_import:
                    if sym not in content:
                        new_lines.append(f"    {sym},")
                        stats["import_added"] += 1
                new_lines.append(")")
                lines[idx:idx + 1] = new_lines

        # Re-find the last import line after modification
        new_content = "\n".join(lines)
        last_import_line_1idx = find_last_import_line(new_content)

        # Insert calls after the last import line
        insert_at = last_import_line_1idx  # 0-indexed position after last import
        # Add a blank line separator then calls
        insert_block = [""] + call_lines + [""]
        for i, cl in enumerate(insert_block):
            lines.insert(insert_at + i, cl)
    else:
        # No existing import — add a new import block after the last import
        import_block = []
        if len(symbols_to_import) == 1:
            import_block.append(
                f"from agentic_core.runtime.contracts.lifecycle_trace_contract import {symbols_to_import[0]}",
            )
        else:
            import_block.append("from agentic_core.runtime.contracts.lifecycle_trace_contract import (")
            for sym in symbols_to_import:
                import_block.append(f"    {sym},")
            import_block.append(")")
        stats["import_added"] += 1

        # Insert: blank line, import, blank line, calls, blank line
        insert_at = last_import_line_1idx  # 0-indexed position after last import
        insert_block = [""] + import_block + [""] + call_lines + [""]
        for i, cl in enumerate(insert_block):
            lines.insert(insert_at + i, cl)

    content = "\n".join(lines)

    if content != original:
        # Verify it still parses as valid Python
        try:
            ast.parse(content)
        except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
            stats["errors"].append(f"SYNTAX ERROR in {module_rel}: {e}")
            # Don't write broken file
            return

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        stats["skipped"] += 1


def main() -> None:
    print(f"Wiring {len(all_modules)} modules...")
    print(f"  - {len(digest_needs)} need emit_determinism_digest() call")
    print(f"  - {len(trace_needs)} need record_execution_trace() call")
    print()

    for module_rel in sorted(all_modules):
        try:
            wire_module(module_rel)
            print(f"  OK {module_rel}")
        except Exception as e:
            stats["errors"].append(f"ERROR: {module_rel}: {e}")
            print(f"  FAIL {module_rel}: {e}")

    print()
    print("=" * 70)
    print("WIRING SUMMARY")
    print("=" * 70)
    print(f"  emit_determinism_digest() calls added: {stats['digest_added']}")
    print(f"  record_execution_trace() calls added: {stats['trace_added']}")
    print(f"  Import statements added: {stats['import_added']}")
    print(f"  Modules unchanged: {stats['skipped']}")
    if stats["errors"]:
        print(f"  Errors: {len(stats['errors'])}")
        for e in stats["errors"]:
            print(f"    {e}")

    out_path = os.path.join(ROOT, "artifacts", "adg", "_convergence_wiring_result_v2.json")
    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
