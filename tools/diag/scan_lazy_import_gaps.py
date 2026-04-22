"""Scan production code for lazy imports that defeat ADG static fan-in.

For every .py file under agentic_core/ and apps_*/ (excluding tests, archives,
tools), this:

1. Walks the AST and collects `ImportFrom` nodes appearing INSIDE function /
   async function / method bodies (lazy imports) — NOT at module top level.
2. Resolves the imported module name to a repo-relative path when possible.
3. Flags cases where the target appears in `_APPROVED_ADAPTER_PATHS` or the
   semantic-cache lazy-only set (from tools/generate/infra_wiring_views.py) —
   i.e., lazy callers of a module that ADG static-imports view may not see.
4. For each flagged target, reports: target module, count of lazy callers,
   count of static callers (naive grep of 'from <module>' at top level), and
   the ratio. A high lazy:static ratio = high ADG blind-spot risk.

Outputs a ranked report: targets where lazy imports dominate static imports
are the modules most likely to slip orphan-detection gates.

No mutations. Pure read-only AST scan.
"""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [REPO / "agentic_core"] + list(REPO.glob("apps_*"))
EXCLUDE_DIR_PARTS = {"__pycache__", "archives", "tests", "test_"}


def _iter_py_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for p in root.rglob("*.py"):
            if any(part in EXCLUDE_DIR_PARTS for part in p.parts):
                continue
            files.append(p)
    return files


def _module_to_path(mod: str) -> Path | None:
    """Resolve dotted module name to an existing .py file under repo."""
    if not mod:
        return None
    as_path = REPO / Path(*mod.split("."))
    if as_path.with_suffix(".py").is_file():
        return as_path.with_suffix(".py").relative_to(REPO)
    init = as_path / "__init__.py"
    if init.is_file():
        return init.relative_to(REPO)
    return None


def _find_lazy_imports(tree: ast.AST) -> list[tuple[str, int]]:
    """Return (module_name, lineno) for every ImportFrom inside a function body."""
    lazy: list[tuple[str, int]] = []
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for sub in ast.walk(func):
            if isinstance(sub, ast.ImportFrom) and sub.module:
                lazy.append((sub.module, sub.lineno))
    return lazy


def _find_top_level_imports(tree: ast.Module) -> set[str]:
    """Return every `from X import ...` module name at module top level."""
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def main() -> int:
    files = _iter_py_files()
    # target_path_rel -> list of (caller_path_rel, lineno)
    lazy_callers: dict[str, list[tuple[str, int]]] = defaultdict(list)
    static_callers: dict[str, set[str]] = defaultdict(set)

    from tqdm import tqdm  # noqa: PLC0415

    for f in tqdm(files, desc="AST scan", unit="file"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue
        caller_rel = str(f.relative_to(REPO)).replace("\\", "/")
        for mod, lineno in _find_lazy_imports(tree):
            resolved = _module_to_path(mod)
            if resolved is None:
                continue
            key = str(resolved).replace("\\", "/")
            lazy_callers[key].append((caller_rel, lineno))
        for mod in _find_top_level_imports(tree):
            resolved = _module_to_path(mod)
            if resolved is None:
                continue
            key = str(resolved).replace("\\", "/")
            static_callers[key].add(caller_rel)

    # Rank: blind-spot risk = lazy_count when static_count == 0, else lazy/static ratio.
    rows: list[tuple[str, int, int, float]] = []
    for target, calls in lazy_callers.items():
        lazy_count = len(calls)
        static_count = len(static_callers.get(target, set()))
        ratio = float("inf") if static_count == 0 else lazy_count / static_count
        rows.append((target, lazy_count, static_count, ratio))

    # Sort: orphan (static==0) first, then highest ratio.
    rows.sort(key=lambda r: (-(1 if r[2] == 0 else 0), -r[3], -r[1]))

    # Print
    print(f"\nScanned {len(files)} production .py files.")
    print(f"Found {len(rows)} modules imported lazily from inside function bodies.\n")
    print(f"{'LAZY':>5}  {'STATIC':>6}  {'RATIO':>7}  TARGET")
    print("-" * 100)
    orphans = []
    dominated = []
    for target, lazy, static, ratio in rows:
        status = "ORPHAN" if static == 0 else "OK   " if ratio <= 1 else "LAZY-DOM"
        r_str = "inf" if ratio == float("inf") else f"{ratio:5.2f}"
        print(f"{lazy:>5}  {static:>6}  {r_str:>7}  [{status}] {target}")
        if static == 0:
            orphans.append((target, lazy))
        elif ratio > 1:
            dominated.append((target, lazy, static))

    print("\n" + "=" * 100)
    print("HIGHEST-RISK (static-callers == 0 — would appear orphan in ADG imports view)")
    print("=" * 100)
    for target, lazy in orphans[:30]:
        callers = lazy_callers[target][:3]
        print(f"\n  {target}  ({lazy} lazy caller(s))")
        for c, ln in callers:
            print(f"    - {c}:{ln}")

    print("\n" + "=" * 100)
    print("LAZY-DOMINATED (ratio > 1 — ADG static fan-in understates real usage)")
    print("=" * 100)
    for target, lazy, static in dominated[:30]:
        print(f"  lazy={lazy:>3}  static={static:>2}  {target}")

    return 0 if not orphans else 1


if __name__ == "__main__":
    sys.exit(main())
