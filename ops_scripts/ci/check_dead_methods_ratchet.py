#!/usr/bin/env python3
"""Gate A3B — dead class methods inside live modules (AST-assisted).

Rationale
---------
A3 (``check_dead_symbols_ratchet.py``) only tracks module-level symbols
in the ADG. Class methods are NOT separate ADG nodes, so dead public
methods on a class that IS imported (class symbol has fan-in > 0) slip
past every existing wiring gate.

A3B fills that gap with a lightweight AST scan:

    1. For every production Python file whose module has fan-in > 0 in
       the ADG (class is reachable from the graph), parse the file.
    2. Collect every ``def <name>`` inside every ``class`` block whose
       class name appears as an ADG symbol with live inbound relations.
    3. Build a repo-wide text index of method-call sites:
         * ``.method_name(``   (attribute call)
         * ``["method_name"]`` (getattr-style)
         * ``"method_name"``   (reflection lookup)
    4. A method is dead if:
         * name does not start with ``_`` (public)
         * name is not a dunder (``__init__``, ``__enter__``, ...)
         * name does not match an inherited-framework signature
           (``setUp``, ``asyncSetUp``, ``get_context_size``, etc.)
         * NOT found anywhere in the callsite index
         * NOT decorated with ``@abstractmethod`` / ``@pytest.fixture`` /
           ``@property`` (properties are accessed by attribute, which
           shows up as ``.name`` without the trailing ``(``, included
           in the index)

Tier
    R (ratchet). Baseline seeds via ``--seed``. Monotone auto-tighten +
    R->B promotion inherited from W1 harness.

False-positive posture
    The text-index scan is intentionally permissive — any match,
    anywhere in the codebase, keeps the method alive. Misses are
    therefore conservative (favor false-negative over false-positive).
    Dynamic dispatch via ``getattr(obj, varname)`` or dict-of-methods
    tables won't resolve — those should be added to the config
    ``config/wiring_dynamic_dispatch_anchors.yaml`` at file granularity.
"""

from __future__ import annotations

import ast
import fnmatch
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
    connect_snapshot,
    latest_snapshot,
)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

PRODUCTION_ROOTS = (
    "agentic_core/",
    "apps_eval/",
    "apps_exec/",
    "apps_lic/",
    "apps_research/",
    "apps_rfp/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "system_learning/",
    "infrastructure/",
)
EXCLUDE_PREFIXES = (
    "tests/",
    "tools/archive/",
    "tools/bench/",
    "tools/debug/",
    "tools/diag/",
    "archives/",
)

# Framework / protocol method names that are valid to keep even without
# an explicit call site.
FRAMEWORK_METHODS = frozenset({
    # unittest
    "setUp", "tearDown", "setUpClass", "tearDownClass",
    "asyncSetUp", "asyncTearDown",
    # pytest fixture targets for classes
    "setup_method", "teardown_method",
    # Django / FastAPI / Flask lifecycle
    "dispatch", "get_queryset", "get_context_data",
    # context-manager protocol
    "__enter__", "__exit__", "__aenter__", "__aexit__",
    # async iterator
    "__aiter__", "__anext__",
    # dataclass / __init_subclass__
    "__init_subclass__", "__post_init__",
    # Pydantic v2
    "model_post_init", "model_dump", "model_dump_json",
    # typing Protocol
    "__class_getitem__",
})

ANCHORS_FILE = REPO_ROOT / "config" / "wiring_dynamic_dispatch_anchors.yaml"


def load_dynamic_anchor_patterns(path: Path | None = None) -> list[str]:
    """Return patterns (fnmatch) from the anchors YAML (W4 shared config)."""
    src = path or ANCHORS_FILE
    if not src.exists() or yaml is None:
        return []
    try:
        data = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    if not isinstance(data, dict):
        return []
    patterns: list[str] = []
    for entry in data.get("anchors", []) or []:
        if isinstance(entry, dict):
            pat = entry.get("pattern")
            if isinstance(pat, str) and pat:
                patterns.append(pat)
    return patterns


def _is_skipped_decorator(dec: ast.expr) -> bool:
    """Return True for decorators that legitimately justify zero callers."""
    name = None
    if isinstance(dec, ast.Name):
        name = dec.id
    elif isinstance(dec, ast.Attribute):
        name = dec.attr
    elif isinstance(dec, ast.Call):
        if isinstance(dec.func, ast.Name):
            name = dec.func.id
        elif isinstance(dec.func, ast.Attribute):
            name = dec.func.attr
    return name in {
        "abstractmethod",
        "abstractclassmethod",
        "abstractstaticmethod",
        "property",
        "cached_property",
        "fixture",
        "pytest_fixture",
        "overload",
        "singledispatch",
        "singledispatchmethod",
    }


def collect_class_methods(
    file_path: Path,
) -> list[tuple[str, str, int]]:
    """Return (class_name, method_name, lineno) for every public method
    defined inside a top-level class in this file."""
    try:
        src = file_path.read_text(encoding="utf-8")
    except OSError:
        return []
    try:
        tree = ast.parse(src, filename=str(file_path))
    except SyntaxError:
        return []
    results: list[tuple[str, str, int]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for child in node.body:
            if not isinstance(
                child, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue
            if any(_is_skipped_decorator(d) for d in child.decorator_list):
                continue
            name = child.name
            if name.startswith("_"):
                continue
            if name in FRAMEWORK_METHODS:
                continue
            results.append((node.name, name, child.lineno))
    return results


_METHOD_REFERENCE_RE = re.compile(
    r"(?:\.|[\"'])([a-z][a-zA-Z0-9_]*)\b"
)


def build_method_name_index(
    python_files: list[Path],
) -> set[str]:
    """Return the set of method names referenced ANYWHERE in the scan set.

    Includes occurrences in:
      * ``.method_name(``   attribute access / call
      * ``"method_name"`` and ``'method_name'`` string literals
      * bracket lookups ``["method_name"]``
    """
    found: set[str] = set()
    for fp in python_files:
        try:
            text = fp.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in _METHOD_REFERENCE_RE.finditer(text):
            found.add(m.group(1))
    return found


def _get_live_module_paths(conn) -> set[str]:
    """Return the set of production module paths that have fan-in > 0."""
    live: set[str] = set()
    for (rp,) in conn.execute(
        """
        SELECT DISTINCT dst.resolved_path
          FROM edges e
          JOIN nodes dst ON dst.id = e.dst_id
          JOIN nodes src ON src.id = e.src_id
         WHERE e.relation_type = 'imports'
           AND dst.resolved_path IS NOT NULL
           AND src.resolved_path IS NOT NULL
           AND src.resolved_path != dst.resolved_path
        """
    ):
        live.add(rp)
    return live


def _get_live_class_names(conn) -> set[str]:
    """Return the set of class-shaped symbol names with live inbound edges."""
    rows = conn.execute(
        """
        SELECT n.adg_name
          FROM nodes n
          JOIN edges e ON e.dst_id = n.id
         WHERE n.entity_type = 'symbol'
           AND n.adg_name LIKE 'ADG::Symbol::%'
           AND e.relation_type
                IN ('imports','instantiates','resolves_callsite')
         GROUP BY n.adg_name
        """
    ).fetchall()
    names: set[str] = set()
    for (adg_name,) in rows:
        tail = adg_name[len("ADG::Symbol::"):]
        last = tail.rsplit(".", 1)[-1]
        if last and last[0].isupper() and not last.startswith("_"):
            names.add(last)
    return names


def _production_py_files() -> list[Path]:
    files: list[Path] = []
    for root in PRODUCTION_ROOTS:
        base = REPO_ROOT / root.rstrip("/")
        if not base.exists():
            continue
        for fp in base.rglob("*.py"):
            rel = fp.relative_to(REPO_ROOT).as_posix()
            if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            files.append(fp)
    return files


def _all_scanable_py_files() -> list[Path]:
    """Production + tests for building the callsite name index."""
    files = _production_py_files()
    tests = REPO_ROOT / "tests"
    if tests.exists():
        for fp in tests.rglob("*.py"):
            files.append(fp)
    return files


class DeadMethodsRatchetGate(WiringGate):
    gate_id = "A3B_dead_methods_in_live_classes_ratchet"
    tier = "R"
    baseline_filename = "wiring_dead_methods_ratchet.json"

    def run(self, conn) -> list[Violation]:
        live_modules = _get_live_module_paths(conn)
        live_classes = _get_live_class_names(conn)
        anchor_patterns = load_dynamic_anchor_patterns()
        prod_files = _production_py_files()
        # Build name index over PROD + TESTS so tests keep methods alive.
        name_index = build_method_name_index(_all_scanable_py_files())

        violations: list[Violation] = []
        for fp in prod_files:
            rel = fp.relative_to(REPO_ROOT).as_posix()
            if rel not in live_modules:
                continue
            if any(fnmatch.fnmatch(rel, p) for p in anchor_patterns):
                continue
            methods = collect_class_methods(fp)
            for cls_name, method, lineno in methods:
                if cls_name not in live_classes:
                    continue
                if method in name_index:
                    continue
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=f"{rel}:{lineno}::{cls_name}.{method}",
                        rule="method_zero_callsites_in_live_class",
                        detail=(
                            "public method of a live class has zero "
                            "static callsite references (AST + text scan)"
                        ),
                        extra={
                            "class": cls_name,
                            "method": method,
                            "module": rel,
                            "line": lineno,
                        },
                    )
                )
        return violations


def main() -> int:
    gate = DeadMethodsRatchetGate()
    if "--seed" in sys.argv:
        conn = connect_snapshot(latest_snapshot())
        try:
            raw = gate.run(conn)
        finally:
            conn.close()
        gate.seed_baseline(len(raw))
        print(f"[{gate.gate_id}] baseline seeded: count={len(raw)}")
        return 0
    result = gate.execute()
    if result.baseline_count is not None:
        print(
            f"[{gate.gate_id}] current={len(result.violations)} "
            f"baseline={result.baseline_count}"
        )
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
