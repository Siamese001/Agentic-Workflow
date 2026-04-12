#!/usr/bin/env python3
"""
Strip systematically-injected dead constant imports from Python files.

Targets the pattern:
    from <module> import (
        SYMBOL_A,
        SYMBOL_B,
        ...
    )

where all or some of the listed symbols are confirmed dead/unused by ADG.

Usage:
    python tools/fix/strip_dead_constants_imports.py \
        --reports path/to/deep_analysis_X.json [path/to/deep_analysis_Y.json ...] \
        --subdirs ops_scripts/ci [ops_scripts/general ...] \
        --symbols BATCH_SIZE,BUFFER_SIZE,DEFAULT_SLEEP,DEFAULT_TIMEOUT,MAX_DEPTH,MAX_FILES,MAX_RETRIES,THRESHOLD \
        [--dry-run]
"""

import argparse
import ast
import json
import pathlib
import re
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_targets(
    report_paths: list[str],
    subdirs: list[str],
    target_symbols: set[str],
) -> dict[str, set[str]]:
    """
    Returns {abs_file_path: {symbol, ...}} for all symbols that are
    dead/unused AND are in target_symbols AND the file is under one of subdirs.
    """
    result: dict[str, set[str]] = {}

    for rp in report_paths:
        report_file = pathlib.Path(rp)
        if not report_file.exists():
            print(f"  WARNING: Report file not found: {rp} — SKIPPING", file=sys.stderr)
            continue

        try:
            data = json.loads(report_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  ERROR: Failed to parse JSON in {rp}: {e} — SKIPPING", file=sys.stderr)
            continue
        except OSError as e:
            print(f"  ERROR: Failed to read {rp}: {e} — SKIPPING", file=sys.stderr)
            continue
        for fdata in data["files"]:
            fpath = fdata["path"].replace("\\", "/")

            # Check subdir filter
            if subdirs:
                match = any(
                    fpath.startswith(sd.replace("\\", "/"))
                    or ("/" + sd.replace("\\", "/") + "/") in ("/" + fpath)
                    for sd in subdirs
                )
                if not match:
                    continue

            dead_symbols: set[str] = set()
            for item in fdata.get("adg_dead_imports", []):
                sym = item["symbol"].split(".")[-1]
                if sym in target_symbols:
                    dead_symbols.add(sym)
            for item in fdata.get("adg_unused_imports", []):
                sym = item["symbol"]
                if sym in target_symbols:
                    dead_symbols.add(sym)

            if dead_symbols:
                abs_path = str(pathlib.Path(fdata["path"]).resolve())
                result[abs_path] = dead_symbols

    return result


def _strip_symbols_from_file(
    filepath: str,
    symbols_to_remove: set[str],
    dry_run: bool,
) -> Optional[str]:
    """
    Parse the file and remove `symbols_to_remove` from any import statements
    that contain them.  Returns a diff summary string, or None if no changes.
    """
    try:
        src = pathlib.Path(filepath).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"  ERROR: Failed to read {filepath}: {e} — SKIPPING", file=sys.stderr)
        return None
    lines = src.splitlines(keepends=True)

    # Strategy: find all import blocks that contain at least one target symbol,
    # then rebuild those blocks with those symbols removed.
    # We work with the raw text to preserve formatting of everything else.

    new_lines: list[str | None] = list(lines)
    changed = False
    log_entries: list[str] = []

    i = 0
    while i < len(new_lines):
        line = new_lines[i]
        if line is None:
            i += 1
            continue

        # Single-line import: from X import A, B, C
        single_match = re.match(
            r"^(\s*from\s+\S+\s+import\s+)(.*?)(\s*)$",
            str(line).rstrip("\n\r"),
        )
        if single_match and "(" not in line:
            prefix = single_match.group(1)
            names_part = single_match.group(2)
            # Strip trailing comments
            names_part = names_part.split("#")[0].strip()
            # Split by comma
            names = [n.strip() for n in names_part.split(",") if n.strip()]
            kept = [n for n in names if n not in symbols_to_remove]
            removed = [n for n in names if n in symbols_to_remove]
            if removed:
                if kept:
                    # Rebuild single-line import with remaining names
                    eol = "\n" if line.endswith("\n") else ""
                    new_lines[i] = prefix + ", ".join(kept) + eol
                else:
                    # All removed — delete the entire line
                    new_lines[i] = None
                changed = True
                log_entries.append(f"  L{i + 1}: removed {removed} (single-line)")
            i += 1
            continue

        # Multi-line import start: from X import (
        multi_start = re.match(r"^(\s*from\s+\S+\s+import\s*\()", line)
        if multi_start:
            # Collect all lines until the closing ')'
            block_start = i
            block_lines = [line]
            j = i + 1
            while j < len(new_lines):
                next_line = new_lines[j]
                if next_line is not None and ")" in next_line:
                    block_lines.append(next_line)
                    break
                if next_line is not None:
                    block_lines.append(next_line)
                j += 1
            block_end = j

            # Parse out the symbol lines
            import_prefix_line = block_lines[0]  # "from X import ("
            closing_line = block_lines[-1]  # ")"

            # Find which lines are symbol lines and which to keep
            symbol_lines = block_lines[1:-1]
            kept_symbol_lines = []
            removed_syms = []
            for sl in symbol_lines:
                if sl is None:
                    continue
                # Extract symbol name (strip whitespace and trailing comma/comment)
                stripped = str(sl).strip().rstrip(",").split("#")[0].strip()
                if stripped in symbols_to_remove:
                    removed_syms.append(stripped)
                else:
                    kept_symbol_lines.append(sl)

            if removed_syms:
                changed = True
                log_entries.append(f"  L{i + 1}: removed {removed_syms} from multi-line import")

                if not kept_symbol_lines:
                    # All symbols in this import block were removed — delete entire block
                    for k in range(block_start, block_end + 1):
                        new_lines[k] = None
                else:
                    # Rebuild block with only kept symbols
                    # Replace lines in-place
                    new_lines[block_start] = import_prefix_line
                    # Fill symbol lines
                    sym_idx = block_start + 1
                    for sl in kept_symbol_lines:
                        new_lines[sym_idx] = sl
                        sym_idx += 1
                    # Place closing paren
                    new_lines[sym_idx] = closing_line
                    sym_idx += 1
                    # Null out any leftover lines from the original block
                    while sym_idx <= block_end:
                        new_lines[sym_idx] = None
                        sym_idx += 1

            i = block_end + 1
            continue

        i += 1

    if not changed:
        return None

    # Build new source
    new_src = "".join(l for l in new_lines if l is not None)

    # Validate the result parses
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        print(f"  SYNTAX ERROR after strip in {filepath}: {e} — SKIPPING", file=sys.stderr)
        return None

    summary = "\n".join(log_entries)

    if not dry_run:
        try:
            pathlib.Path(filepath).write_text(new_src, encoding="utf-8")
        except OSError as e:
            print(f"  ERROR: Failed to write {filepath}: {e} — SKIPPING", file=sys.stderr)
            return None

    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Strip dead constant imports from Python files")
    parser.add_argument(
        "--reports", nargs="+", required=True, help="Path(s) to deep_analysis_*.json report files"
    )
    parser.add_argument(
        "--subdirs", nargs="*", default=[], help="Restrict to files under these subdirectories"
    )
    parser.add_argument("--symbols", required=True, help="Comma-separated list of symbols to strip")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be done without modifying files"
    )
    parser.add_argument("--log", default=None, help="Path to write JSON change log")
    args = parser.parse_args()

    target_symbols = {s.strip() for s in args.symbols.split(",") if s.strip()}
    print(f"Target symbols: {sorted(target_symbols)}")
    print(f"Reports: {args.reports}")
    print(f"Subdirs filter: {args.subdirs or '(all)'}")
    print(f"Dry run: {args.dry_run}")
    print()

    targets = _collect_targets(args.reports, args.subdirs, target_symbols)
    print(f"Files to process: {len(targets)}")
    print()

    change_log = []
    files_changed = 0
    files_skipped = 0
    files_no_change = 0

    for filepath, symbols in sorted(targets.items()):
        if not pathlib.Path(filepath).exists():
            print(f"  SKIP (not found): {filepath}")
            files_skipped += 1
            continue

        summary = _strip_symbols_from_file(filepath, symbols, dry_run=args.dry_run)
        if summary is None:
            files_no_change += 1
            continue

        rel = str(pathlib.Path(filepath).relative_to(pathlib.Path.cwd()))
        action = "DRY-RUN" if args.dry_run else "CHANGED"
        print(f"[{action}] {rel}")
        print(summary)
        files_changed += 1
        change_log.append({"file": rel, "symbols_removed": sorted(symbols), "details": summary})

    print()
    print(f"Summary: {files_changed} changed, {files_no_change} no-change, {files_skipped} skipped")

    if args.log:
        pathlib.Path(args.log).write_text(
            json.dumps(change_log, indent=2),
            encoding="utf-8",
        )
        print(f"Change log written to: {args.log}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
