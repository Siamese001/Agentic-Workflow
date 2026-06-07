"""Codemod: migrate exact-match hardcoded path literals to SSOT constants.

Part of W5-CODEMOD finishing the deferred SSOT-HARDCODING-W2 scope.

Strategy (conservative):
  1. AST walk: find ast.Constant string nodes where value matches a target
     literal EXACTLY (or exact + trailing slash).
  2. Skip docstring-first-statement nodes.
  3. Skip test / debug / SSOT-definition files.
  4. Use (lineno, col_offset, end_col_offset) for surgical text replacement
     that preserves all formatting.
  5. Inject a canonical import at the top of the file (after existing
     `from __future__` imports and other imports, in alphabetical order
     within the same import group).
  6. Avoid duplicate imports if the symbol is already imported.
  7. py_compile each modified file to reject syntax regressions.

Usage::

    python tools/migration/ssot_path_literal_migrator.py --dry-run
    python tools/migration/ssot_path_literal_migrator.py --apply

Exit codes:
  0  success (including --dry-run showing planned changes)
  1  at least one file failed to compile after rewrite (auto-reverted)
  2  invalid args
"""

from __future__ import annotations

import argparse
import ast
import py_compile
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# literal -> (canonical_symbol, canonical_module)
# Keys MUST stay as plain string literals, otherwise a re-run of this codemod
# on itself (if exclusion ever fails) produces a self-referential dict.
SSOT_MAP: dict[str, tuple[str, str]] = {
    "artifacts/adg": ("ADG_ARTIFACTS_DIR", "agentic_core.L0_routing.config.path_constants"),
    "artifacts/cursor": ("WINDSURF_ARTIFACTS_DIR", "agentic_core.L0_routing.config.path_constants"),
    "docs/archive/windsurf/legacy-tree/plans": ("WINDSURF_PLANS_DIR", "agentic_core.L0_routing.config.path_constants"),
    ".claude/governance/scripts/_legacy_windsurf": ("WINDSURF_SCRIPTS_DIR", "agentic_core.L0_routing.config.path_constants"),
    "docs/reports": ("DOCS_REPORTS_DIR", "agentic_core.L0_routing.config.path_constants"),
    "docs/architecture/adr": ("ADR_DIR", "agentic_core.L0_routing.config.path_constants"),
}

ROOTS = (
    "agentic_core",
    "apps_rg",
    "apps_shared",
    "apps_lic",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "apps_underwriting_ai",
    "tools",
    "ops_scripts",
    "system_learning",
    "infrastructure",
)

EXCLUDE_PATTERNS = (
    # Path-segment matches — accept either / or \ as separator AND allow
    # the segment to be at the start of the path (no leading separator).
    r"(^|[/\\])__pycache__[/\\]",
    r"(^|[/\\])archives?[/\\]",
    r"(^|[/\\])_archive[/\\]",
    r"(^|[/\\])tools[/\\]archive[/\\]",
    r"(^|[/\\])tests[/\\]",
    r"(^|[/\\])tools[/\\]debug[/\\]",
    r"(^|[/\\])tools[/\\]migration[/\\]",  # the migrator itself
    # SSOT definition — must keep its own literals
    r"path_constants\.py$",
    # Report-location validator is a CANONICAL SSOT validator — its literal
    # IS the authoritative spec. Leaving it as a literal avoids a circular
    # coupling where the validator imports the constant it validates.
    r"report_location_validator\.py$",
    # write-gateway allowed_paths is also policy spec; leave literal until
    # wave where the policy itself is SSOT'd.
    r"UniversalWriteGateway\.py$",
)


# ---------------------------------------------------------------------------
# AST analysis
# ---------------------------------------------------------------------------


def _is_docstring_node(tree: ast.Module, target_id: int) -> bool:
    """True if target_id is the id of a docstring first-statement Constant."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr):
                val = body[0].value
                if isinstance(val, ast.Constant) and isinstance(val.value, str) and id(val) == target_id:
                    return True
    return False


def _existing_imports(tree: ast.Module, module: str) -> tuple[ast.ImportFrom | None, frozenset[str]]:
    """Find an existing `from <module> import ...` node and its imported names."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            names = frozenset(a.name for a in node.names)
            return node, names
    return None, frozenset()


def _find_sites(path: Path) -> list[dict]:
    """Return list of safe-to-migrate sites in this file, with replacement coords."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    sites: list[dict] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        val = node.value
        # Skip docstrings
        if _is_docstring_node(tree, id(node)):
            continue
        for lit, (sym, module) in SSOT_MAP.items():
            if val == lit:
                kind = "EXACT"
            elif val == lit + "/":
                kind = "EXACT_TRAILING"
            else:
                continue
            # Only migrate when node has positions (py3.8+)
            if getattr(node, "lineno", None) is None:
                continue
            sites.append(
                {
                    "literal": val,
                    "symbol": sym,
                    "module": module,
                    "kind": kind,
                    "lineno": node.lineno,
                    "col": node.col_offset,
                    "end_col": node.end_col_offset,
                    "end_lineno": getattr(node, "end_lineno", node.lineno),
                }
            )
            break  # one literal per node
    return sites


# ---------------------------------------------------------------------------
# Text rewrite
# ---------------------------------------------------------------------------


def _rewrite_literal(line: str, col: int, end_col: int, replacement: str, kind: str) -> str:
    """Replace the string literal between col..end_col with `replacement`.

    For EXACT_TRAILING (literal ends with '/'), the replacement becomes
    f"{symbol} + '/'" so the resulting value matches. For EXACT, just
    the symbol name.
    """
    before = line[:col]
    after = line[end_col:]
    if kind == "EXACT_TRAILING":
        new = f'{replacement} + "/"'
    else:
        new = replacement
    return before + new + after


def _inject_import(text: str, tree: ast.Module, module: str, symbol: str) -> str:
    """Add `from <module> import <symbol>`, merging into an existing import
    of the same module, or inserting after the last top-level import.
    """
    existing_node, existing_names = _existing_imports(tree, module)
    if symbol in existing_names:
        return text  # already imported

    lines = text.splitlines(keepends=True)

    if existing_node is not None:
        # Merge symbol into the existing ImportFrom — but only if the
        # existing block has no inline comments (e.g. `# review: ...`
        # or `# type: ignore`). Rebuilding would silently strip them, which
        # is a constitutional violation for guardian annotations and loses
        # type-checker hints for the rest. If any comment is present, fall
        # through to the "no existing import" branch and ADD a new line.
        start = existing_node.lineno - 1
        end = getattr(existing_node, "end_lineno", existing_node.lineno) - 1
        block_lines = lines[start : end + 1]
        has_inline_comment = any("#" in bl for bl in block_lines)
        if not has_inline_comment:
            new_names = sorted({*existing_names, symbol})
            if len(new_names) == 1:
                replacement = f"from {module} import {new_names[0]}\n"
            else:
                body = ",\n    ".join(new_names)
                replacement = f"from {module} import (\n    {body},\n)\n"
            lines[start : end + 1] = [replacement]
            return "".join(lines)
        # else: keep the commented block intact and add a separate import below

    # No existing import — insert after the last top-level import
    last_import_lineno = 0
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            last_import_lineno = max(
                last_import_lineno,
                getattr(node, "end_lineno", node.lineno) or node.lineno,
            )
    new_import_line = f"from {module} import {symbol}\n"
    insert_at = last_import_lineno  # 1-indexed; insert AFTER this line
    lines.insert(insert_at, new_import_line)
    return "".join(lines)


def _read_preserve_newlines(path: Path) -> tuple[str, str]:
    """Read file bytes, detect dominant newline, return (text, newline).

    Python's text mode on Windows silently converts CRLF->LF; writing back
    re-writes everything and trips a full-file diff. Using binary I/O with
    explicit newline detection keeps the diff minimal.
    """
    data = path.read_bytes()
    # Detect newline: prefer CRLF if any CRLF present, else LF.
    newline = "\r\n" if b"\r\n" in data else "\n"
    text = data.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return text, newline


def _write_preserve_newlines(path: Path, text: str, newline: str) -> None:
    if newline == "\r\n":
        out = text.replace("\r\n", "\n").replace("\n", "\r\n")
    else:
        out = text
    path.write_bytes(out.encode("utf-8"))


def _apply_file(path: Path, sites: list[dict], dry_run: bool) -> tuple[bool, list[str]]:
    """Apply migrations to one file. Returns (success, messages)."""
    if not sites:
        return True, []

    messages = []
    original_text, newline = _read_preserve_newlines(path)
    try:
        tree = ast.parse(original_text)
    except SyntaxError as exc:
        return False, [f"{path}: SYNTAX ERROR pre-migration: {exc}"]

    # Group sites by line; rewrite from rightmost column first per line so
    # earlier col_offsets on the same line remain valid.
    by_line: dict[int, list[dict]] = defaultdict(list)
    for s in sites:
        by_line[s["lineno"]].append(s)

    lines = original_text.splitlines(keepends=True)
    for ln in sorted(by_line, reverse=True):
        line_sites = sorted(by_line[ln], key=lambda s: -s["col"])
        line_text = lines[ln - 1]
        # Strip trailing newline for rewrite, re-append
        trail = ""
        if line_text.endswith("\r\n"):
            trail, line_text = "\r\n", line_text[:-2]
        elif line_text.endswith("\n"):
            trail, line_text = "\n", line_text[:-1]
        for s in line_sites:
            line_text = _rewrite_literal(
                line_text,
                s["col"],
                s["end_col"],
                s["symbol"],
                s["kind"],
            )
            messages.append(f"{path}:{ln}  {s['literal']!r} [{s['kind']}] -> {s['symbol']}")
        lines[ln - 1] = line_text + trail

    new_text = "".join(lines)

    # Inject imports — one per distinct (module, symbol)
    needed: set[tuple[str, str]] = {(s["module"], s["symbol"]) for s in sites}
    # Re-parse with rewrites to get an accurate tree for import placement
    try:
        new_tree = ast.parse(new_text)
    except SyntaxError as exc:
        return False, [f"{path}: rewrite produced syntax error: {exc}"]
    for module, symbol in sorted(needed):
        new_text = _inject_import(new_text, new_tree, module, symbol)
        # Re-parse after each injection (import positions shift)
        try:
            new_tree = ast.parse(new_text)
        except SyntaxError as exc:
            return False, [f"{path}: import injection produced syntax error: {exc}"]

    if dry_run:
        messages.append(f"  (dry-run) {len(sites)} site(s) queued in {path}")
        return True, messages

    # Write + py_compile verify; revert on failure.
    # Windows note: NamedTemporaryFile holds the file open, so py_compile's
    # atomic-rename step fails with WinError 5. Use a dedicated temp dir and
    # a non-conflicting pyc path instead.
    original_bytes = path.read_bytes()
    tmp_dir = Path(tempfile.mkdtemp(prefix="_ssot_codemod_"))
    try:
        _write_preserve_newlines(path, new_text, newline)
        cfile = tmp_dir / (path.stem + ".verify.pyc")
        py_compile.compile(str(path), cfile=str(cfile), doraise=True)
    except (py_compile.PyCompileError, SyntaxError, OSError) as exc:
        path.write_bytes(original_bytes)
        return False, [f"{path}: post-rewrite compile failed, reverted: {exc}"]
    finally:
        import shutil  # noqa: PLC0415 -- local: only needed on the write path

        shutil.rmtree(tmp_dir, ignore_errors=True)
    messages.append(f"  WROTE {path}  ({len(sites)} site(s))")
    return True, messages


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    parser.add_argument("--apply", action="store_true", help="write changes to disk")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="max number of files to migrate (0 = all)",
    )
    parser.add_argument(
        "--only-literal",
        action="append",
        default=[],
        help="restrict to one literal (repeatable). e.g. --only-literal artifacts/adg",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("must pass --dry-run or --apply", file=sys.stderr)
        return 2

    # Filter SSOT_MAP if requested
    global SSOT_MAP  # noqa: PLW0603 -- simple CLI toggle
    if args.only_literal:
        SSOT_MAP = {k: v for k, v in SSOT_MAP.items() if k in args.only_literal}
        if not SSOT_MAP:
            print(f"no literals match {args.only_literal}", file=sys.stderr)
            return 2

    all_sites: dict[Path, list[dict]] = {}
    for root in ROOTS:
        r = Path(root)
        if not r.exists():
            continue
        for py in r.rglob("*.py"):
            sp = str(py)
            if any(re.search(pat, sp) for pat in EXCLUDE_PATTERNS):
                continue
            sites = _find_sites(py)
            if sites:
                all_sites[py] = sites

    if args.limit:
        keep = list(all_sites)[: args.limit]
        all_sites = {p: all_sites[p] for p in keep}

    total_sites = sum(len(v) for v in all_sites.values())
    print(f"plan: migrate {total_sites} site(s) across {len(all_sites)} file(s)")

    failures: list[str] = []
    applied = 0
    for path, sites in all_sites.items():
        ok, msgs = _apply_file(path, sites, dry_run=args.dry_run)
        for m in msgs:
            print(m)
        if ok:
            if not args.dry_run:
                applied += 1
        else:
            failures.extend(msgs)

    print(f"\nresult: applied={applied} failures={len(failures)}")
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
