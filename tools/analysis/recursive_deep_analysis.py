#!/usr/bin/env python3
"""
Recursive deep analysis tool.
For every file in every subfolder of a target directory:
  - Reports file path, size, line count, function/class count
  - Identifies root-level files that violate no-root-files rule
  - Pulls ADG dead code signals per file (unused_import, dead_imports,
    unreachable_after_raise, duplicate_method)
  - Classifies each file as: DEAD | MISPLACED | OVERSIZED | CLEAN
  - Produces a flat per-file report + per-folder summary
"""

import ast
import json
import os
import sqlite3
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# ADG helpers
# ---------------------------------------------------------------------------

def _build_adg_index(db_path: str, target_dir: str) -> dict[str, dict[str, list]]:
    """
    Single-pass: load all dead-code edges whose source file is inside
    target_dir.  Returns dict keyed by source_file path.
    """
    index: dict[str, dict[str, list]] = {}

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    relation_types = [
        "unused_import",
        "dead_imports",
        "unreachable_after_raise",
        "duplicate_method",
    ]

    for rel in relation_types:
        cur.execute(
            """
            SELECT e.source_file, e.line_no, e.symbol, n_dst.adg_name
            FROM edges e
            JOIN nodes n_src ON e.src_id = n_src.id
            LEFT JOIN nodes n_dst ON e.dst_id = n_dst.id
            WHERE e.relation_type = ?
              AND n_src.resolved_path LIKE ?
            ORDER BY e.source_file, e.line_no
            """,
            (rel, f"%{target_dir}%"),
        )
        for source_file, line_no, symbol, dst_name in cur.fetchall():
            if source_file not in index:
                index[source_file] = {r: [] for r in relation_types}
            index[source_file][rel].append(
                {"line": line_no, "symbol": symbol or dst_name or ""}
            )

    conn.close()
    return index


# ---------------------------------------------------------------------------
# Per-file AST analysis
# ---------------------------------------------------------------------------

def _ast_stats(path: Path) -> dict[str, Any]:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=str(path))
        functions = [
            n.name
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        imports = [
            n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
        ]
        lines = src.splitlines()
        # count non-blank, non-comment lines as "code lines"
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        return {
            "total_lines": len(lines),
            "code_lines": len(code_lines),
            "functions": functions,
            "classes": classes,
            "import_count": len(imports),
            "parse_error": None,
        }
    except SyntaxError as exc:
        return {
            "total_lines": 0,
            "code_lines": 0,
            "functions": [],
            "classes": [],
            "import_count": 0,
            "parse_error": str(exc),
        }


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

FUTURE_IMPORT = "from __future__ import annotations"

_SYNTHETIC_PREFIXES = ("_emit_", "_trace_", "_adg_")


def _is_synthetic_symbol(sym: str) -> bool:
    return any(sym.startswith(p) for p in _SYNTHETIC_PREFIXES)


def _filter_genuine_unused(entries: list[dict]) -> list[dict]:
    """Strip known false-positives from unused_import list."""
    genuine = []
    for e in entries:
        sym = e.get("symbol", "")
        # future imports
        if sym in ("annotations", "__future__"):
            continue
        # synthetic/emitted instrumentation
        if _is_synthetic_symbol(sym):
            continue
        genuine.append(e)
    return genuine


def classify_file(
    rel_path: str,
    stats: dict,
    adg: dict[str, list],
    depth: int,
) -> dict[str, Any]:
    """Return a file record with flags."""
    genuine_unused = _filter_genuine_unused(adg.get("unused_import", []))
    genuine_dead = adg.get("dead_imports", [])
    unreachable = adg.get("unreachable_after_raise", [])
    duplicates = adg.get("duplicate_method", [])

    is_init = Path(rel_path).name == "__init__.py"
    # __init__.py exports are intentional — skip unused_import flags
    if is_init:
        genuine_unused = []

    issues = []
    if genuine_unused:
        issues.append(f"UNUSED_IMPORTS({len(genuine_unused)})")
    if genuine_dead:
        issues.append(f"DEAD_IMPORTS({len(genuine_dead)})")
    if unreachable:
        issues.append(f"UNREACHABLE({len(unreachable)})")
    if duplicates:
        issues.append(f"DUPLICATE_METHODS({len(duplicates)})")
    if stats.get("parse_error"):
        issues.append("PARSE_ERROR")

    # root-level violation: file sits at depth==1 (direct child of target root)
    # and is not __init__.py
    root_violation = depth == 1 and not is_init

    classification = "CLEAN"
    if issues:
        classification = "DEAD_CODE"
    if root_violation and (stats.get("code_lines", 0) > 5 or stats.get("functions")):
        classification = "MISPLACED" if not issues else "MISPLACED+DEAD"

    return {
        "path": rel_path,
        "depth": depth,
        "size_bytes": stats.get("size_bytes", 0),
        "total_lines": stats.get("total_lines", 0),
        "code_lines": stats.get("code_lines", 0),
        "functions": stats.get("functions", []),
        "classes": stats.get("classes", []),
        "import_count": stats.get("import_count", 0),
        "parse_error": stats.get("parse_error"),
        "root_violation": root_violation,
        "issues": issues,
        "classification": classification,
        "adg_unused_imports": genuine_unused,
        "adg_dead_imports": genuine_dead,
        "adg_unreachable": unreachable,
        "adg_duplicate_methods": duplicates,
    }


# ---------------------------------------------------------------------------
# Recursive walker
# ---------------------------------------------------------------------------

def walk_directory(
    root: Path,
    target_dir: str,
    adg_index: dict[str, dict[str, list]],
) -> list[dict]:
    """Walk root recursively; return a flat list of per-file records."""
    records = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip pycache
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]

        current = Path(dirpath)
        # depth relative to root
        try:
            depth = len(current.relative_to(root).parts) + 1
        except ValueError:
            depth = 1

        for fname in sorted(filenames):
            fpath = current / fname
            # relative to repo root for ADG key matching
            try:
                rel_from_repo = str(fpath.relative_to(Path.cwd())).replace("\\", "/")
            except ValueError:
                rel_from_repo = str(fpath).replace("\\", "/")

            # relative to target root for display
            try:
                rel_display = str(fpath.relative_to(root.parent)).replace("\\", "/")
            except ValueError:
                rel_display = rel_from_repo

            stats: dict[str, Any] = {"size_bytes": fpath.stat().st_size}

            if fname.endswith(".py"):
                stats.update(_ast_stats(fpath))
            else:
                # non-Python: just size/lines
                try:
                    lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
                    stats["total_lines"] = len(lines)
                    stats["code_lines"] = len([l for l in lines if l.strip()])
                except Exception:
                    stats["total_lines"] = 0
                    stats["code_lines"] = 0
                stats["functions"] = []
                stats["classes"] = []
                stats["import_count"] = 0
                stats["parse_error"] = None

            adg_data = adg_index.get(rel_from_repo, {})
            record = classify_file(rel_display, stats, adg_data, depth)
            records.append(record)

    return records


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def build_summary(records: list[dict], target_dir: str) -> dict[str, Any]:
    folder_stats: dict[str, dict] = {}

    for r in records:
        folder = str(Path(r["path"]).parent)
        if folder not in folder_stats:
            folder_stats[folder] = {
                "files": 0,
                "total_lines": 0,
                "root_violations": [],
                "dead_code_files": [],
                "misplaced_files": [],
                "clean_files": 0,
            }
        s = folder_stats[folder]
        s["files"] += 1
        s["total_lines"] += r.get("total_lines", 0)
        if r["root_violation"]:
            s["root_violations"].append(r["path"])
        if "DEAD" in r["classification"]:
            s["dead_code_files"].append(r["path"])
        if "MISPLACED" in r["classification"]:
            s["misplaced_files"].append(r["path"])
        if r["classification"] == "CLEAN":
            s["clean_files"] += 1

    total_files = len(records)
    total_issues = sum(1 for r in records if r["issues"])
    total_root_violations = sum(1 for r in records if r["root_violation"])
    total_dead = sum(1 for r in records if "DEAD" in r["classification"])
    total_misplaced = sum(1 for r in records if "MISPLACED" in r["classification"])

    return {
        "target_dir": target_dir,
        "total_files": total_files,
        "total_with_issues": total_issues,
        "total_root_violations": total_root_violations,
        "total_dead_code_files": total_dead,
        "total_misplaced_files": total_misplaced,
        "folder_breakdown": folder_stats,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def analyze(target_dir: str, db_path: str, output_path: str) -> None:
    root = Path(target_dir)
    if not root.exists():
        print(f"ERROR: {target_dir} does not exist")
        return

    print(f"\n{'='*72}")
    print(f"  DEEP RECURSIVE ANALYSIS: {target_dir}")
    print(f"{'='*72}")

    print("  [1/4] Building ADG dead-code index...")
    adg_index = _build_adg_index(db_path, target_dir)
    print(f"        {len(adg_index)} files have ADG signals")

    print("  [2/4] Walking directory tree recursively...")
    records = walk_directory(root, target_dir, adg_index)
    print(f"        {len(records)} files scanned")

    print("  [3/4] Building summary...")
    summary = build_summary(records, target_dir)

    print(f"\n  RESULTS:")
    print(f"    Total files            : {summary['total_files']}")
    print(f"    Files with issues      : {summary['total_with_issues']}")
    print(f"    Root-level violations  : {summary['total_root_violations']}")
    print(f"    Dead code files        : {summary['total_dead_code_files']}")
    print(f"    Misplaced files        : {summary['total_misplaced_files']}")

    # Print per-folder breakdown
    print(f"\n  PER-FOLDER BREAKDOWN:")
    for folder, fs in sorted(summary["folder_breakdown"].items()):
        issues_count = len(fs["root_violations"]) + len(fs["dead_code_files"])
        marker = "  !" if issues_count else "   "
        print(f"{marker} {folder}/ — {fs['files']} files, {fs['total_lines']} lines", end="")
        if fs["root_violations"]:
            print(f", ROOT_VIOLATIONS={len(fs['root_violations'])}", end="")
        if fs["dead_code_files"]:
            print(f", DEAD_CODE={len(fs['dead_code_files'])}", end="")
        if fs["misplaced_files"]:
            print(f", MISPLACED={len(fs['misplaced_files'])}", end="")
        print()

    print(f"\n  [4/4] Writing report to {output_path}")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "files": records}, f, indent=2)
    print(f"  Done.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print(
            "Usage: python recursive_deep_analysis.py <target_dir> <adg_db> <output_json>"
        )
        sys.exit(1)

    analyze(sys.argv[1], sys.argv[2], sys.argv[3])
