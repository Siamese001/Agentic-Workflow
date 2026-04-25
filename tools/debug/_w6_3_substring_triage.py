"""W6.3 P0 triage: sub-classify C_SUBSTRING SSOT sites.

For each site, climb the AST parent chain to determine:
  LOG_MESSAGE       -- literal embedded in logger.* / logging.* / print() call
  TEMPLATE          -- inside f-string (JoinedStr) or .format() template
  ARGPARSE_HELP     -- inside argparse add_argument(help=...) / description= / epilog=
  RAISE_ARG         -- first arg of raise <Exc>(...) statement
  REGEX_PATTERN     -- first positional arg of re.compile(...) / re.match(...) / etc.
  PROSE_OUTPUT      -- appended to a prose-typed list (lines, out, doc, body, messages)
  ACCIDENTAL_CONCAT -- everything else (path construction, dict/list literals,
                       return values) -- candidates for f-string conversion
  EXEMPT_DOC        -- inside a docstring (skipped by W5 probe but recheck)

The 4 new categories (ARGPARSE_HELP, RAISE_ARG, REGEX_PATTERN, PROSE_OUTPUT)
were added 2026-04-24 per W7-P1 context-review finding that most previously
"ACCIDENTAL_CONCAT" sites were actually intentional documentation / error
text / regex / prose-output literals that should not be migrated.

Outputs:
  - Console summary table
  - docs/reports/w6_3_substring_triage_<date>.md with full per-site listing
"""

from __future__ import annotations

import ast
import datetime as _dt
import re
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    ADG_ARTIFACTS_DIR,
    ADR_DIR,
    DOCS_REPORTS_DIR,
    WINDSURF_ARTIFACTS_DIR,
    WINDSURF_PLANS_DIR,
    WINDSURF_SCRIPTS_DIR,
)

LITERALS: dict[str, str] = {
    ADG_ARTIFACTS_DIR: "ADG_ARTIFACTS_DIR",
    WINDSURF_ARTIFACTS_DIR: "WINDSURF_ARTIFACTS_DIR",
    WINDSURF_PLANS_DIR: "WINDSURF_PLANS_DIR",
    WINDSURF_SCRIPTS_DIR: "WINDSURF_SCRIPTS_DIR",
    DOCS_REPORTS_DIR: "DOCS_REPORTS_DIR",
    ADR_DIR: "ADR_DIR",
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
EXCLUDE = (
    r"[\\/]__pycache__[\\/]",
    r"[\\/]archives?[\\/]",
    r"[\\/]_archive[\\/]",
    r"[\\/]tools[\\/]archive[\\/]",
    r"[\\/]tests[\\/]",
    r"[\\/]tools[\\/]debug[\\/]",
    r"path_constants\.py$",
)

LOGGER_CALL_PATTERN = re.compile(
    r"^(logger|logging|log|_log|_logger|LOG|Logger|self\.logger|self\._logger|self\.log)$"
)
LOGGER_METHODS = {"debug", "info", "warning", "warn", "error", "critical", "exception"}

# Kwarg names used in argparse.ArgumentParser / add_argument for user-facing
# documentation. Literal contents are user-visible; migrate-to-f-string would
# change what users see in --help output.
ARGPARSE_DOC_KWARGS = {"help", "description", "epilog", "metavar", "prog", "usage"}

# Function names (attribute tail) whose first positional arg is a regex
# pattern — migrating the literal would corrupt the regex.
RE_COMPILE_METHODS = {
    "compile",
    "match",
    "search",
    "fullmatch",
    "findall",
    "finditer",
    "split",
    "sub",
    "subn",
}

# List / collection names that, by convention, accumulate prose output
# (markdown, report lines, human-readable messages). A literal appended to
# one of these is documentation text, not a computed path.
PROSE_LIST_NAMES = {
    "lines",
    "lines_out",
    "out",
    "output",
    "doc",
    "docs",
    "body",
    "messages",
    "report",
    "report_lines",
    "rows",
    "md",
    "markdown",
    "text",
    "text_lines",
}


def _is_logger_call(call: ast.Call) -> bool:
    """True if call is logger.<level>(...) or logging.<level>(...) or print(...)."""
    func = call.func
    if isinstance(func, ast.Name) and func.id == "print":
        return True
    if isinstance(func, ast.Attribute) and func.attr in LOGGER_METHODS:
        # walk the value chain to a name like 'logger', 'self.logger', etc.
        node: ast.AST = func.value
        chain = []
        while isinstance(node, ast.Attribute):
            chain.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            chain.append(node.id)
        prefix = ".".join(reversed(chain))
        return bool(LOGGER_CALL_PATTERN.match(prefix))
    return False


def _is_format_call(call: ast.Call) -> bool:
    """True if call is <str>.format(...)."""
    func = call.func
    return isinstance(func, ast.Attribute) and func.attr == "format"


def _is_argparse_doc_kwarg(node: ast.Constant, parents: dict[int, ast.AST]) -> bool:
    """True if this constant is the value of an argparse help/description/... kwarg."""
    kw = parents.get(id(node))
    if not isinstance(kw, ast.keyword) or kw.arg not in ARGPARSE_DOC_KWARGS:
        return False
    return isinstance(parents.get(id(kw)), ast.Call)


def _is_raise_arg(node: ast.Constant, parents: dict[int, ast.AST]) -> bool:
    """True if node sits under a raise <ExcCls>(...) first positional arg."""
    # Walk up: Constant -> Call (exc instantiation) -> Raise
    cur: ast.AST | None = parents.get(id(node))
    depth = 0
    while cur is not None and depth < 5:
        if isinstance(cur, ast.Raise):
            return True
        cur = parents.get(id(cur))
        depth += 1
    return False


def _is_regex_pattern(node: ast.Constant, parents: dict[int, ast.AST]) -> bool:
    """True if node is the first positional arg of an re.<method>(...) call."""
    call = parents.get(id(node))
    if not isinstance(call, ast.Call):
        return False
    func = call.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr not in RE_COMPILE_METHODS:
        return False
    # func.value should reference the re module
    val = func.value
    if isinstance(val, ast.Name) and val.id == "re":
        # Check the constant is in positional args (not a kwarg)
        return any(arg is node for arg in call.args)
    return False


def _is_prose_append(node: ast.Constant, parents: dict[int, ast.AST]) -> bool:
    """True if node is an arg to <prose_list>.append(...) / extend(...)."""
    call = parents.get(id(node))
    if not isinstance(call, ast.Call):
        return False
    func = call.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr not in {"append", "extend", "insert"}:
        return False
    # func.value is the list being appended to; check its name
    val = func.value
    if isinstance(val, ast.Name) and val.id in PROSE_LIST_NAMES:
        return any(arg is node for arg in call.args)
    if isinstance(val, ast.Attribute) and val.attr in PROSE_LIST_NAMES:
        return any(arg is node for arg in call.args)
    return False


def _classify_site(node: ast.Constant, parents: dict[int, ast.AST]) -> str:
    """Walk parent chain to assign a category.

    Order of checks matters: the first matching category wins. Documentation-
    class categories (ARGPARSE_HELP, RAISE_ARG, REGEX_PATTERN, PROSE_OUTPUT)
    are checked before ACCIDENTAL_CONCAT so genuine refactoring targets are
    not over-counted.
    """
    # Immediate-parent context checks (cheap, no walk)
    if _is_argparse_doc_kwarg(node, parents):
        return "ARGPARSE_HELP"
    if _is_regex_pattern(node, parents):
        return "REGEX_PATTERN"
    if _is_prose_append(node, parents):
        return "PROSE_OUTPUT"
    if _is_raise_arg(node, parents):
        return "RAISE_ARG"

    # Multi-level walk for nested contexts
    cur: ast.AST | None = parents.get(id(node))
    depth = 0
    inside_joinedstr = False
    while cur is not None and depth < 10:
        if isinstance(cur, ast.JoinedStr):
            inside_joinedstr = True
        if isinstance(cur, ast.Call):
            if _is_logger_call(cur):
                return "LOG_MESSAGE"
            if _is_format_call(cur):
                return "TEMPLATE"
        cur = parents.get(id(cur))
        depth += 1
    if inside_joinedstr:
        return "TEMPLATE"
    return "ACCIDENTAL_CONCAT"


def _build_parents(tree: ast.AST) -> dict[int, ast.AST]:
    parents: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    return parents


def _docstring_node_ids(tree: ast.AST) -> set[int]:
    out: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if not body:
                continue
            first = body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                out.add(id(first.value))
    return out


def classify_file(path: Path) -> list[tuple[str, str, int, str, str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    parents = _build_parents(tree)
    docs = _docstring_node_ids(tree)
    lines = text.splitlines()
    out: list[tuple[str, str, int, str, str]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        val = node.value
        if len(val) > 400:
            continue
        for lit in LITERALS:
            if lit not in val:
                continue
            # Skip exact / prefix / suffix categories handled by W6.2 codemod
            if val == lit or val == lit + "/" or val.startswith(lit + "/") or val.endswith("/" + lit):
                break
            ln = getattr(node, "lineno", 0)
            ctx = lines[ln - 1].strip()[:140] if 1 <= ln <= len(lines) else ""
            if id(node) in docs:
                cat = "EXEMPT_DOC"
            else:
                cat = _classify_site(node, parents)
            out.append((str(path).replace("\\", "/"), lit, ln, cat, ctx))
            break
    return out


def main() -> int:
    sites: list[tuple[str, str, int, str, str]] = []
    for root in ROOTS:
        p = Path(root)
        if not p.exists():
            continue
        for py in p.rglob("*.py"):
            sp = str(py)
            if any(re.search(pat, sp) for pat in EXCLUDE):
                continue
            sites.extend(classify_file(py))

    by_cat: dict[str, int] = defaultdict(int)
    by_lit_cat: dict[tuple[str, str], int] = defaultdict(int)
    for _, lit, _, cat, _ in sites:
        by_cat[cat] += 1
        by_lit_cat[(lit, cat)] += 1

    print(f"Total C_SUBSTRING sites classified: {len(sites)}")
    print()
    print("By category:")
    for cat, n in sorted(by_cat.items(), key=lambda t: -t[1]):
        print(f"  {n:>4}  {cat}")
    print()
    print("By literal x category:")
    cats = sorted({c for _, c in by_lit_cat})
    print(f"  {'literal':<30}" + "".join(f" {c:>20}" for c in cats))
    for lit in sorted({lit for lit, _ in by_lit_cat}):
        row = f"  {lit:<30}" + "".join(f" {by_lit_cat.get((lit, c), 0):>20}" for c in cats)
        print(row)

    # Write detailed report
    report_dir = Path("docs/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    today = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d")
    report_path = report_dir / f"w6_3_substring_triage_{today}.md"
    lines_out: list[str] = []
    lines_out.append(f"# W6.3 C_SUBSTRING SSOT Triage — {today}")
    lines_out.append("")
    lines_out.append(f"Total sites classified: **{len(sites)}**")
    lines_out.append("")
    lines_out.append("## Category breakdown")
    lines_out.append("")
    lines_out.append("| Category | Count | Disposition |")
    lines_out.append("|---|---:|---|")
    dispo = {
        "LOG_MESSAGE": "Add to SSOT probe exemption allowlist",
        "TEMPLATE": "Convert to f-string with constant interpolation",
        "ACCIDENTAL_CONCAT": "Convert to f-string with constant interpolation",
        "EXEMPT_DOC": "Already exempt (docstring) — no action",
        "ARGPARSE_HELP": "Documentation (argparse help/description) — no migration",
        "RAISE_ARG": "Exception diagnostic text — no migration",
        "REGEX_PATTERN": "Regex pattern literal — migration would corrupt",
        "PROSE_OUTPUT": "Prose output (lines/body/markdown) — no migration",
    }
    for cat, n in sorted(by_cat.items(), key=lambda t: -t[1]):
        lines_out.append(f"| {cat} | {n} | {dispo.get(cat, '?')} |")
    lines_out.append("")
    lines_out.append("## Per-site detail")
    lines_out.append("")
    for cat in sorted(by_cat):
        lines_out.append(f"### {cat} ({by_cat[cat]} sites)")
        lines_out.append("")
        for fp, lit, ln, c, ctx in sites:
            if c != cat:
                continue
            lines_out.append(f"- `{fp}:{ln}` lit=`{lit}`")
            lines_out.append(f"  - context: `{ctx}`")
        lines_out.append("")
    report_path.write_text("\n".join(lines_out), encoding="utf-8")
    print()
    print(f"Report written: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
