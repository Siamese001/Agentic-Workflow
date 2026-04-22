"""Summary helper: cross-reference lazy-import orphans against approved adapter registry.

Uses the full data from scan_lazy_import_gaps.py (re-runs AST scan) and then
cross-references against:

1. `_APPROVED_ADAPTER_PATHS` in tools/generate/infra_wiring_views.py
2. `_PROCESS_BOUNDARY_ADAPTERS` in same file
3. Layer inference from path prefix (L0/L5 are ×2.0 per canonical invariants §6)

Output: a short, actionable table of modules that are:
 - Orphan from ADG static-imports view (static_count == 0), AND
 - Lazy-imported by production code, AND
 - Either on an approved-adapter list OR on a critical layer (L0/L5/L3/L4).

These are the modules where an ADG "zero-caller" gate would either (a) fail
incorrectly if enrolled, or (b) fail to catch orphaning if enrolment is skipped.
"""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [REPO / "agentic_core"] + list(REPO.glob("apps_*"))
EXCLUDE_DIR_PARTS = {"__pycache__", "archives", "tests", "test_"}


def _approved_and_boundary() -> tuple[set[str], set[str]]:
    src = (REPO / "tools" / "generate" / "infra_wiring_views.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    approved: set[str] = set()
    boundary: set[str] = set()
    from tqdm import tqdm as _tqdm  # noqa: PLC0415 -- §16 progress bar

    for node in _tqdm(tree.body, desc="parse registry", unit="node", leave=False):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            tgt = node.targets[0]
            if isinstance(tgt, ast.Name) and tgt.id in (
                "_APPROVED_ADAPTER_PATHS",
                "_PROCESS_BOUNDARY_ADAPTERS",
            ):
                sink = approved if tgt.id == "_APPROVED_ADAPTER_PATHS" else boundary
                if isinstance(node.value, ast.Tuple | ast.List):
                    for el in node.value.elts:
                        if isinstance(el, ast.Constant) and isinstance(el.value, str):
                            sink.add(el.value.replace("\\", "/"))
    return approved, boundary


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
    if not mod:
        return None
    as_path = REPO / Path(*mod.split("."))
    if as_path.with_suffix(".py").is_file():
        return as_path.with_suffix(".py").relative_to(REPO)
    init = as_path / "__init__.py"
    if init.is_file():
        return init.relative_to(REPO)
    return None


def _layer_of(path: str) -> str:
    parts = path.split("/")
    for p in parts:
        if p.startswith("L") and len(p) >= 2 and p[1].isdigit():
            return p.split("_")[0]
        if p.startswith("apps_"):
            return p
    return "?"


def main() -> int:
    approved, boundary = _approved_and_boundary()
    files = _iter_py_files()
    lazy_callers: dict[str, list[str]] = defaultdict(list)
    static_callers: dict[str, set[str]] = defaultdict(set)

    from tqdm import tqdm  # noqa: PLC0415

    for f in tqdm(files, desc="AST scan", unit="file"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue
        caller = str(f.relative_to(REPO)).replace("\\", "/")
        # lazy
        for func in ast.walk(tree):
            if not isinstance(func, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for sub in ast.walk(func):
                if isinstance(sub, ast.ImportFrom) and sub.module:
                    r = _module_to_path(sub.module)
                    if r is not None:
                        lazy_callers[str(r).replace("\\", "/")].append(caller)
        # static
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                r = _module_to_path(node.module)
                if r is not None:
                    static_callers[str(r).replace("\\", "/")].add(caller)

    # Build analysis
    orphan_targets = [
        (t, len(lazy_callers[t])) for t in lazy_callers if len(static_callers.get(t, set())) == 0
    ]
    orphan_targets.sort(key=lambda r: -r[1])

    by_layer: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for t, lc in orphan_targets:
        by_layer[_layer_of(t)].append((t, lc))

    print("\n" + "=" * 100)
    print("LAZY-ONLY ORPHANS (static_imports_fanin == 0, lazy callers > 0)")
    print("=" * 100)
    print(f"Total: {len(orphan_targets)} modules across production code")
    print(f"Approved adapters hit lazy-only: {sum(1 for t, _ in orphan_targets if t in approved)}")
    print(f"Process-boundary exempt: {sum(1 for t, _ in orphan_targets if t in boundary)}")

    print("\nBy layer (orphan count — where ADG static fan-in is blind):")
    for layer in sorted(by_layer):
        print(f"  {layer:>12}: {len(by_layer[layer])} orphan target(s)")

    print("\n" + "=" * 100)
    print("CRITICAL: Orphans at L0 / L5 (×2.0 multiplier, highest blast radius)")
    print("=" * 100)
    for t, lc in orphan_targets:
        layer = _layer_of(t)
        if layer in ("L0", "L5"):
            flag = " [APPROVED]" if t in approved else " [PROCESS_BOUNDARY]" if t in boundary else ""
            callers = lazy_callers[t][:2]
            print(f"  {layer}  lazy={lc:>3}  {t}{flag}")
            for c in callers:
                print(f"         └─ caller: {c}")

    print("\n" + "=" * 100)
    print("APPROVED ADAPTERS with LAZY-ONLY callers (ADG zero-caller view lies)")
    print("=" * 100)
    for t, lc in orphan_targets:
        if t in approved:
            callers = lazy_callers[t][:3]
            print(f"  lazy={lc:>2}  {t}")
            for c in callers:
                print(f"         └─ {c}")

    print("\n" + "=" * 100)
    print("UNENROLLED ORPHANS at L4 (cache/state — same class as semcache bug)")
    print("=" * 100)
    for t, lc in orphan_targets:
        layer = _layer_of(t)
        if layer == "L4" and t not in approved and t not in boundary:
            callers = lazy_callers[t][:2]
            # Filter for "interesting" paths (utils/memory, utils/client, cache/)
            if any(seg in t for seg in ("utils/memory", "utils/client", "cache/", "utils/context", "store")):
                print(f"  lazy={lc:>2}  {t}")
                for c in callers:
                    print(f"         └─ {c}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
