"""Codemod: migrate prefix-path hardcoded literals to f-string SSOT interpolation.

Companion to `ssot_path_literal_migrator.py` (which handles EXACT matches).
This handles the PREFIX case: ``"artifacts/adg/cache/scan.json"`` becomes
``f"{ADG_ARTIFACTS_DIR}/cache/scan.json"``.

W6.2 deferred-scope closure. Default scope is W6.2a (artifacts/adg/ only — 53
sites in the W5 probe). Use ``--only-literal`` to scope to the other waves.

Strategy:
  1. AST walk: ``ast.Constant`` string node where ``val.startswith(lit + "/")``
     for some SSOT literal AND ``val != lit`` AND ``val != lit + "/"`` (those
     are EXACT, owned by the other migrator).
  2. Skip docstring-first-statement nodes.
  3. Skip files with FORBIDDEN suffix characters: ``{``, ``}``, or the
     literal's outer quote character. f-string syntax requires that.
  4. Replace ``"<lit>/<rest>"`` (incl. quote chars) with
     ``f"{<SYMBOL>}/<rest>"``, preserving the original outer quote style.
  5. Inject ``from agentic_core.L0_routing.config.path_constants import <SYM>``
     using the same comment-preserving merge logic as the EXACT migrator.
  6. py_compile each modified file; auto-revert on failure.
  7. Preserve CRLF/LF.

Usage::

    python tools/migration/ssot_prefix_path_migrator.py --dry-run
    python tools/migration/ssot_prefix_path_migrator.py --apply --only-literal artifacts/adg

Exit codes:
  0  success (incl. --dry-run with no failures)
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
SSOT_MAP: dict[str, tuple[str, str]] = {
    "artifacts/adg": ("ADG_ARTIFACTS_DIR", "agentic_core.L0_routing.config.path_constants"),
    "artifacts/governance": ("WINDSURF_ARTIFACTS_DIR", "agentic_core.L0_routing.config.path_constants"),
    "docs/archive/windsurf/legacy-tree/plans": ("WINDSURF_PLANS_DIR", "agentic_core.L0_routing.config.path_constants"),
    ".claude/governance/scripts": ("GOVERNANCE_SCRIPTS_DIR", "agentic_core.L0_routing.config.path_constants"),
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
    "apps_underwriting_ai",
    "tools",
    "ops_scripts",
    "system_learning",
    "infrastructure",
)

EXCLUDE_PATTERNS = (
    r"(^|[/\\])__pycache__[/\\]",
    r"(^|[/\\])archives?[/\\]",
    r"(^|[/\\])_archive[/\\]",
    r"(^|[/\\])tools[/\\]archive[/\\]",
    r"(^|[/\\])tests[/\\]",
    r"(^|[/\\])tools[/\\]debug[/\\]",
    r"(^|[/\\])tools[/\\]migration[/\\]",
    r"path_constants\.py$",
    r"report_location_validator\.py$",
    r"UniversalWriteGateway\.py$",
)

# Reject a site if the suffix-after-prefix contains any of these chars; an
# f-string with these would either break (`{`/`}`) or require re-quoting
# (the outer-quote char). We treat these as out-of-scope for auto-migration
# and leave them for manual review.
FORBIDDEN_SUFFIX_CHARS = "{}"


# ---------------------------------------------------------------------------
# AST analysis
# ---------------------------------------------------------------------------


def _is_docstring_node(tree: ast.Module, target_id: int) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr):
                val = body[0].value
                if isinstance(val, ast.Constant) and isinstance(val.value, str) and id(val) == target_id:
                    return True
    return False


def _existing_imports(tree: ast.Module, module: str) -> tuple[ast.ImportFrom | None, frozenset[str]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            names = frozenset(a.name for a in node.names)
            return node, names
    return None, frozenset()


def _find_sites(path: Path) -> list[dict]:
    """Return list of safe-to-migrate prefix sites with replacement coords."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    src_lines = text.splitlines(keepends=False)
    sites: list[dict] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        val = node.value
        if _is_docstring_node(tree, id(node)):
            continue
        if getattr(node, "lineno", None) is None:
            continue
        # Only handle single-line literals (lineno == end_lineno). Multi-line
        # string literals would require coordinate gymnastics not worth it
        # for the marginal site count.
        if getattr(node, "end_lineno", node.lineno) != node.lineno:
            continue
        for lit, (sym, module) in SSOT_MAP.items():
            # PREFIX only: starts with lit + "/", AND is longer than lit + "/"
            if not val.startswith(lit + "/"):
                continue
            if val == lit + "/":
                # EXACT_TRAILING — owned by the other migrator
                continue
            suffix = val[len(lit) :]  # includes the leading "/"
            # Reject f-string-incompatible suffix characters
            if any(c in suffix for c in FORBIDDEN_SUFFIX_CHARS):
                continue
            # Inspect the source text to detect outer quote and reject
            # raw / bytes / formatted-string / multi-segment-concat cases.
            line_text = src_lines[node.lineno - 1] if node.lineno - 1 < len(src_lines) else ""
            seg = line_text[node.col_offset : node.end_col_offset]
            if not seg or seg[0] not in ("'", '"'):
                # Could be inside an f-string segment, a parenthesized literal
                # spanning weird coords, or a string-prefix (r, b, u, rb).
                # All of these are out of scope for the auto codemod.
                continue
            quote = seg[0]
            # The outer-quote char must not appear in the suffix (otherwise
            # the rewrite would need to escape or re-quote — out of scope).
            if quote in suffix:
                continue
            # Multi-segment string concatenation (auto-concatenated adjacent
            # literals) ends/starts oddly. Defensive: require seg endswith quote.
            if not seg.endswith(quote):
                continue
            # Length sanity: seg should be exactly quote + val + quote.
            # If Python evaluated escapes (e.g. \\, \n in the literal), the
            # raw seg can be longer than 2 + len(val); we accept anything that
            # starts/ends with the same quote, but compute the replacement
            # using the seg bounds rather than the val length.
            sites.append(
                {
                    "literal": val,
                    "suffix": suffix,
                    "symbol": sym,
                    "module": module,
                    "lineno": node.lineno,
                    "col": node.col_offset,
                    "end_col": node.end_col_offset,
                    "quote": quote,
                }
            )
            break  # one literal per node
    return sites


# ---------------------------------------------------------------------------
# Text rewrite
# ---------------------------------------------------------------------------


def _rewrite_prefix(line: str, col: int, end_col: int, symbol: str, suffix: str, quote: str) -> str:
    """Replace `quote + literal + quote` with `f"{symbol}<suffix>"` (preserve quote style)."""
    before = line[:col]
    after = line[end_col:]
    new = f"f{quote}{{{symbol}}}{suffix}{quote}"
    return before + new + after


def _inject_import(text: str, tree: ast.Module, module: str, symbol: str) -> str:
    existing_node, existing_names = _existing_imports(tree, module)
    if symbol in existing_names:
        return text

    lines = text.splitlines(keepends=True)

    if existing_node is not None:
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

    last_import_lineno = 0
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            last_import_lineno = max(
                last_import_lineno,
                getattr(node, "end_lineno", node.lineno) or node.lineno,
            )
    new_import_line = f"from {module} import {symbol}\n"
    insert_at = last_import_lineno
    lines.insert(insert_at, new_import_line)
    return "".join(lines)


def _read_preserve_newlines(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
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
    if not sites:
        return True, []
    messages = []
    original_text, newline = _read_preserve_newlines(path)
    try:
        ast.parse(original_text)
    except SyntaxError as exc:
        return False, [f"{path}: SYNTAX ERROR pre-migration: {exc}"]

    by_line: dict[int, list[dict]] = defaultdict(list)
    for s in sites:
        by_line[s["lineno"]].append(s)

    lines = original_text.splitlines(keepends=True)
    for ln in sorted(by_line, reverse=True):
        line_sites = sorted(by_line[ln], key=lambda s: -s["col"])
        line_text = lines[ln - 1]
        trail = ""
        if line_text.endswith("\r\n"):
            trail, line_text = "\r\n", line_text[:-2]
        elif line_text.endswith("\n"):
            trail, line_text = "\n", line_text[:-1]
        for s in line_sites:
            line_text = _rewrite_prefix(
                line_text,
                s["col"],
                s["end_col"],
                s["symbol"],
                s["suffix"],
                s["quote"],
            )
            messages.append(f'{path}:{ln}  {s["literal"]!r} -> f"{{{s["symbol"]}}}{s["suffix"]}"')
        lines[ln - 1] = line_text + trail

    new_text = "".join(lines)

    needed: set[tuple[str, str]] = {(s["module"], s["symbol"]) for s in sites}
    try:
        new_tree = ast.parse(new_text)
    except SyntaxError as exc:
        return False, [f"{path}: rewrite produced syntax error: {exc}"]
    for module, symbol in sorted(needed):
        new_text = _inject_import(new_text, new_tree, module, symbol)
        try:
            new_tree = ast.parse(new_text)
        except SyntaxError as exc:
            return False, [f"{path}: import injection produced syntax error: {exc}"]

    if dry_run:
        messages.append(f"  (dry-run) {len(sites)} site(s) queued in {path}")
        return True, messages

    original_bytes = path.read_bytes()
    tmp_dir = Path(tempfile.mkdtemp(prefix="_ssot_prefix_codemod_"))
    try:
        _write_preserve_newlines(path, new_text, newline)
        cfile = tmp_dir / (path.stem + ".verify.pyc")
        py_compile.compile(str(path), cfile=str(cfile), doraise=True)
    except (py_compile.PyCompileError, SyntaxError, OSError) as exc:
        path.write_bytes(original_bytes)
        return False, [f"{path}: post-rewrite compile failed, reverted: {exc}"]
    finally:
        import shutil  # noqa: PLC0415

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
        help="restrict to one literal (repeatable). Default: artifacts/adg only.",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("must pass --dry-run or --apply", file=sys.stderr)
        return 2

    global SSOT_MAP  # noqa: PLW0603
    if args.only_literal:
        SSOT_MAP = {k: v for k, v in SSOT_MAP.items() if k in args.only_literal}
        if not SSOT_MAP:
            print(f"no literals match {args.only_literal}", file=sys.stderr)
            return 2
    else:
        # Default scope: W6.2a only (artifacts/adg/) — biggest single bucket
        SSOT_MAP = {k: v for k, v in SSOT_MAP.items() if k == "artifacts/adg"}

    print(f"scope: {sorted(SSOT_MAP.keys())}")

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
    print(f"plan: migrate {total_sites} prefix site(s) across {len(all_sites)} file(s)")

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
