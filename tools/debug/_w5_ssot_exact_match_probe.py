"""Classify the 123 SSOT hardcoding sites into safe vs unsafe for auto-migration.

SAFE categories (auto-migratable):
  A. Exact match: node.value == literal
  B. Path("...") / Path("...") / trailing-slash joins where literal is one arg

UNSAFE (skip, flag for manual review):
  C. Substring / concat / format-string fragment
  D. Inside docstrings
  E. Inside comments (not AST-visible anyway)
  F. In test/debug files where the literal is test data
"""

from __future__ import annotations
import ast
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

LITERALS = {
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
    r"\\__pycache__\\",
    r"\\archives?\\",
    r"\\_archive\\",
    r"\\tools\\archive\\",
    r"\\tests\\",
    r"\\tools\\debug\\",
    # the SSOT file itself
    r"path_constants\.py$",
)


def _is_docstring(node: ast.Constant, parent: ast.AST) -> bool:
    """True if node is the first statement of a module/class/function body."""
    for field in ("body",):
        body = getattr(parent, field, None)
        if not isinstance(body, list) or not body:
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and first.value is node:
            return True
    return False


def classify_file(path: Path) -> list[tuple[str, str, int, str, str]]:
    """Return list of (file, literal, line, category, context_snippet)."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    # Pre-compute parent map + docstring-first-statement set
    parents: dict[int, ast.AST] = {}
    docstring_nodes: set[int] = set()
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if getattr(node, "body", None):
                first = node.body[0]
                if (
                    isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)
                ):
                    docstring_nodes.add(id(first.value))

    lines = text.splitlines()
    results: list[tuple[str, str, int, str, str]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        val = node.value
        if len(val) > 200:
            continue
        for lit in LITERALS:
            if lit not in val:
                continue
            ln = getattr(node, "lineno", 0)
            context = lines[ln - 1].strip()[:120] if 1 <= ln <= len(lines) else ""
            # Categorize
            if id(node) in docstring_nodes:
                cat = "D_DOCSTRING"
            elif val == lit:
                cat = "A_EXACT"
            elif val == lit + "/":
                cat = "A_EXACT_TRAILING_SLASH"
            elif val.startswith(lit + "/"):
                # e.g. "artifacts/adg/cache/scan_result.json" — not safe auto-migrate
                cat = "C_PREFIX_PATH"
            elif val.endswith("/" + lit):
                cat = "C_SUFFIX"
            else:
                cat = "C_SUBSTRING"
            results.append((str(path), lit, ln, cat, context))
            break  # one literal per node
    return results


def main() -> int:
    by_cat: dict[str, int] = defaultdict(int)
    by_lit_cat: dict[tuple[str, str], int] = defaultdict(int)
    safe_sites: list[tuple[str, str, int, str, str]] = []

    for root in ROOTS:
        p = Path(root)
        if not p.exists():
            continue
        for py in p.rglob("*.py"):
            sp = str(py)
            if any(re.search(pat, sp) for pat in EXCLUDE):
                continue
            for row in classify_file(py):
                _, lit, _, cat, _ = row
                by_cat[cat] += 1
                by_lit_cat[(lit, cat)] += 1
                if cat.startswith("A_"):
                    safe_sites.append(row)

    print("Classification totals:")
    for cat, n in sorted(by_cat.items(), key=lambda t: -t[1]):
        print(f"  {n:>5}  {cat}")

    print("\nBy literal × category:")
    lits = sorted({lit for lit, _ in by_lit_cat})
    cats = sorted({cat for _, cat in by_lit_cat})
    header = f"{'literal':<30}" + "".join(f" {c[:18]:>20}" for c in cats)
    print(header)
    for lit in lits:
        row = f"{lit:<30}" + "".join(f" {by_lit_cat.get((lit, c), 0):>20}" for c in cats)
        print(row)

    print(f"\nSafe sites (A_*): {len(safe_sites)}")
    print("\nSafe site samples:")
    for row in safe_sites[:20]:
        print(f"  {row[0]}:{row[2]}  [{row[3]}]  lit={row[1]!r}")
        print(f"    {row[4]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
