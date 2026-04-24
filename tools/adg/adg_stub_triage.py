"""ADG stub-test triage — AST-based classifier for `_adg.py` scaffold tests.

Purpose
-------
The ADG test-scaffolding pipeline historically emitted `*_adg.py` files whose
tests assert only module importability + symbol exposure + callable-ness.
That signal is already covered by ADG CI guards:

- `check_test_harness_coverage.py` — proves every prod module has a test-import edge.
- `check_exception_contract.py` — raise/catch symmetry via ADG `calls` edges.
- `check_expected_wiring.py` — "X must call Y" structurally.
- `check_graph_island.py` + `check_graph_reach.py` — connectivity invariants.

This tool classifies each `_adg.py` as **stub** (redundant with ADG CI) or
**non-stub** (has real behavioral assertions worth keeping).

Classification rule (pure AST, no ADG MCP dependency)
-----------------------------------------------------
A file is a **stub** iff ALL of:

  1. ≤5 `def test_*` functions.
  2. Every test body consists solely of permitted-stub statements:
     - `assert getattr(...) is not None`
     - `assert <Name> is not None`
     - `assert callable(<Name>)`
     - `assert isinstance(<Name>, type)`
     - `assert <Name>.__name__ == <literal>`
     - `pytest.importorskip(...)`
     - `monkeypatch.setenv(...)`
     - bare expression statements (e.g. `Foo()`)
     - `pass`
  3. No fixtures beyond module-scoped `importorskip` shims.

Anything else → **non-stub**.

Sub-commands
------------
  classify          — emit per-file classification JSON.
  archive-plan      — from classification, compute safe-to-archive list
                      (stubs that have a sibling non-`_adg` test file).
  verify            — single-file sanity check.

Exit codes
----------
  0 = clean run
  1 = usage error / bad input
  2 = read error
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter
from pathlib import Path


# ----------------------------------------------------------------- AST helpers


# Allowlist of function-call roots that DO NOT constitute "behavioral" logic.
# Any Call node whose func (after dotted resolution) starts with one of these
# roots is considered stub-safe. Calls outside this allowlist mark the test
# as behavioral.
_ALLOWLISTED_CALL_ROOTS = frozenset(
    {
        # builtins used for existence checks
        "getattr",
        "hasattr",
        "callable",
        "isinstance",
        "len",
        "dir",
        "type",
        "list",
        "tuple",
        "set",
        "dict",
        "str",
        "int",
        "float",
        "bool",
        "print",
        "repr",
        "id",
        "any",
        "all",
        "sorted",
        "reversed",
        # pytest / importlib scaffolding
        "pytest",
        "importlib",
        "importorskip",
        # monkeypatch env-shim is treated as scaffolding (env-only mutation)
        "monkeypatch",
    }
)

# Attribute-method names that are pure reads and do not exercise behavior,
# regardless of receiver. Used when the Call is `<x>.method(...)`.
_ALLOWLISTED_METHOD_ATTRS = frozenset(
    {
        # string reads
        "startswith",
        "endswith",
        "upper",
        "lower",
        "strip",
        "rstrip",
        "lstrip",
        "split",
        "rsplit",
        "splitlines",
        "replace",
        "format",
        "encode",
        "decode",
        "count",
        "index",
        "find",
        "rfind",
        "casefold",
        # dict / mapping reads
        "keys",
        "values",
        "items",
        "get",
        # set reads
        "union",
        "intersection",
        "difference",
        # fixture interaction that is not behavior under test
        "setenv",
        "delenv",
        "setattr",
        "delattr",  # monkeypatch API
        "importorskip",
        "fail",
        "skip",
        "raises",
        "warns",
        "fixture",  # pytest API
        "import_module",  # importlib
    }
)


def _call_root(func: ast.expr) -> str | None:
    """Resolve dotted Attribute/Name chain to the leftmost root identifier."""
    while isinstance(func, ast.Attribute):
        func = func.value
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Call):  # chained: foo()().bar → root=foo
        return _call_root(func.func)
    return None


def _stmt_is_behavioral(stmt: ast.stmt, fixture_names: set[str]) -> bool:
    """Return True iff the statement contains any non-allowlisted call.

    A statement is 'behavioral' if:
      (a) it contains a `Call` whose root identifier is NOT in the allowlist
          and is NOT a recognized fixture name (fixture.__dunder__ access
          is allowed; fixture.method(args) is behavioral);
      (b) it is a loop whose iterable is a non-allowlisted call;
      (c) it is a raise / with / try-except that exercises real behavior.

    Otherwise it is stub-safe (imports, assignments with allowlisted RHS,
    asserts on existence, pass, docstrings, etc.).
    """
    # Docstrings, bare expressions, pass
    if isinstance(stmt, (ast.Pass,)):
        return False
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
        return False

    # Walk every Call in the subtree; mark behavioral if any root is
    # outside allowlist AND not a fixture-attr chain that terminates in a dunder.
    for node in ast.walk(stmt):
        if not isinstance(node, ast.Call):
            continue
        # Method-call allowlist: `<anything>.safe_method(...)` is stub-safe.
        if isinstance(node.func, ast.Attribute) and node.func.attr in _ALLOWLISTED_METHOD_ATTRS:
            continue
        root = _call_root(node.func)
        if root is None:
            continue
        if root in _ALLOWLISTED_CALL_ROOTS:
            continue
        # Fixture-rooted calls: any method call on a fixture is behavioral
        # unless its attr is in the method allowlist (handled above).
        if root in fixture_names:
            return True
        # Unknown root → behavioral.
        return True
    # Raise / while / for-with-non-allowlisted-iter statements: check iter
    if isinstance(stmt, ast.Raise):
        return True
    return False


def _collect_fixture_names(tree: ast.AST) -> set[str]:
    """Identify names that refer to pytest fixtures / parameters in test fns."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            for arg in node.args.args:
                if arg.arg != "self":
                    names.add(arg.arg)
    return names


def _is_stub_test_function(fn: ast.FunctionDef, fixture_names: set[str]) -> bool:
    """A test function is stub-like iff no statement contains behavioral calls."""
    for stmt in fn.body:
        if _stmt_is_behavioral(stmt, fixture_names):
            return False
    return True


# ----------------------------------------------------------------- classifier


def classify_file(path: Path) -> dict:
    """Classify one `_adg.py` file. Returns dict with label + reasons."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return {
            "path": str(path),
            "label": "error",
            "reason": f"{type(exc).__name__}: {exc}",
        }

    test_fns: list[ast.FunctionDef] = []
    fixture_fns: list[ast.FunctionDef] = []

    def _walk(parent: ast.AST) -> None:
        for child in ast.iter_child_nodes(parent):
            if isinstance(child, ast.FunctionDef):
                if child.name.startswith("test_"):
                    test_fns.append(child)
                elif any(
                    isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "fixture"
                    for d in child.decorator_list
                ) or any(isinstance(d, ast.Attribute) and d.attr == "fixture" for d in child.decorator_list):
                    fixture_fns.append(child)
            if isinstance(child, ast.ClassDef):
                _walk(child)

    _walk(tree)

    if len(test_fns) == 0:
        return {
            "path": str(path),
            "label": "empty",
            "reason": "no test_* functions found",
            "test_count": 0,
        }

    if len(test_fns) > 5:
        return {
            "path": str(path),
            "label": "non-stub",
            "reason": f">5 test functions ({len(test_fns)})",
            "test_count": len(test_fns),
        }

    fixture_names = _collect_fixture_names(tree)
    non_stub_tests = [fn.name for fn in test_fns if not _is_stub_test_function(fn, fixture_names)]
    if non_stub_tests:
        return {
            "path": str(path),
            "label": "non-stub",
            "reason": f"behavioral test(s): {', '.join(non_stub_tests[:3])}",
            "test_count": len(test_fns),
        }

    return {
        "path": str(path),
        "label": "stub",
        "reason": f"{len(test_fns)} import-only test(s); fixtures={len(fixture_fns)}",
        "test_count": len(test_fns),
    }


# ----------------------------------------------------------------- commands


def cmd_classify(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    pattern = args.pattern
    # Glob relative to repo root to get deterministic paths
    matches = sorted(repo_root.glob(pattern))
    matches = [p for p in matches if p.is_file() and p.name.endswith("_adg.py")]
    if not matches:
        print(f"No files matched pattern: {pattern}", file=sys.stderr)
        return 1

    total = len(matches)
    results: list[dict] = []
    bar_width = 40
    for idx, path in enumerate(matches, 1):
        result = classify_file(path)
        # normalize to repo-relative
        try:
            result["path"] = str(path.relative_to(repo_root)).replace("\\", "/")
        except ValueError:
            pass
        results.append(result)
        # progress bar (rule §16)
        if idx == total or idx % max(1, total // 20) == 0:
            pct = idx / total
            filled = int(bar_width * pct)
            bar = "\u2588" * filled + "\u2591" * (bar_width - filled)
            color = (
                "\033[92m"
                if pct >= 0.9
                else "\033[94m"
                if pct >= 0.7
                else "\033[93m"
                if pct >= 0.4
                else "\033[91m"
            )
            sys.stderr.write(f"\r{color}[{bar}]\033[0m {int(pct * 100):3d}% ({idx}/{total}) classifying")
            sys.stderr.flush()
    sys.stderr.write("\n")

    counts = Counter(r["label"] for r in results)
    summary = {
        "total": total,
        "counts": dict(counts),
        "results": results,
    }

    out_path = Path(args.json) if args.json else None
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Classification report: {out_path}")
    print(f"Totals: {dict(counts)}")
    return 0


# SSOT: ops_scripts/ci/check_test_harness_coverage.py PROD_MODULE_GLOBS.
# A stub whose derived production module does NOT match these globs is
# archive-safe without a sibling test, because the harness-coverage gate
# only enforces coverage on these paths.
_PROD_MODULE_GLOBS = (
    "agentic_core/L*/**/*.py",
    "apps_eval/engines/*.py",
    "apps_eval/integrations/*.py",
    "apps_exec/engines/*.py",
    "apps_exec/integrations/*.py",
    "apps_lic/engines/*.py",
    "apps_lic/integrations/*.py",
    "apps_research/engines/*.py",
    "apps_research/integrations/*.py",
    "apps_rfp/engines/*.py",
    "apps_rfp/integrations/*.py",
    "apps_rg/engines/*.py",
    "apps_rg/integrations/*.py",
    "apps_shared/enforcement/*.py",
    "apps_underwriting_ai/engines/*.py",
    "apps_underwriting_ai/ingestion/*.py",
)


def _derive_prod_module(test_rel_posix: str) -> str | None:
    """Given a repo-relative test path like `tests/unit/agentic_core/L0_routing/types/test_foo_adg.py`,
    derive the corresponding production module path (best-effort).

    Strategy:
      1. Drop the leading `tests/unit/` or `tests/` prefix.
      2. Replace filename `test_<name>_adg.py` -> `<name>.py` (or `__init__.py`
         when the stub is `test___init___adg.py`).
    """
    if not test_rel_posix.startswith("tests/"):
        return None
    parts = test_rel_posix.split("/")
    # strip leading 'tests/unit/' or 'tests/'
    if len(parts) >= 2 and parts[1] == "unit":
        parts = parts[2:]
    else:
        parts = parts[1:]
    if not parts:
        return None
    fname = parts[-1]
    if not fname.endswith("_adg.py"):
        return None
    stem = fname[: -len("_adg.py")]
    # test___init__ -> __init__
    if stem == "test___init__":
        prod_name = "__init__.py"
    elif stem.startswith("test_"):
        prod_name = stem[len("test_"):] + ".py"
    else:
        prod_name = stem + ".py"
    parts[-1] = prod_name
    return "/".join(parts)


def _prod_is_gate_covered(prod_rel_posix: str) -> bool:
    """Return True iff the production module is under check_test_harness_coverage
    gate surface. __init__.py is explicitly excluded by the gate."""
    import fnmatch
    if prod_rel_posix.endswith("__init__.py"):
        return False
    return any(fnmatch.fnmatch(prod_rel_posix, pat) for pat in _PROD_MODULE_GLOBS)


def cmd_archive_plan(args: argparse.Namespace) -> int:
    """From a classification report, derive archive candidates.

    A stub is archive-safe if ANY of:
      (a) a sibling non-`_adg` test file exists, OR
      (b) the production module is NOT covered by check_test_harness_coverage
          (i.e., outside PROD_MODULE_GLOBS, or an `__init__.py` which the gate skips).

    This implements the full coverage-safety envelope.
    """
    repo_root = Path(__file__).resolve().parents[2]
    report_path = Path(args.input)
    if not report_path.is_file():
        print(f"Report not found: {report_path}", file=sys.stderr)
        return 1

    summary = json.loads(report_path.read_text(encoding="utf-8"))
    candidates: list[dict] = []
    skipped_unsafe: list[dict] = []
    kept_non_stub: int = 0
    kept_empty_or_error: int = 0

    for entry in summary["results"]:
        label = entry["label"]
        if label == "non-stub":
            kept_non_stub += 1
            continue
        if label in {"empty", "error"}:
            kept_empty_or_error += 1
            continue
        if label != "stub":
            continue

        path = Path(entry["path"])
        rel_posix = str(path).replace("\\", "/")
        name = path.name
        if not name.endswith("_adg.py"):
            continue
        sibling_name = name[: -len("_adg.py")] + ".py"
        sibling_abs = repo_root / path.parent / sibling_name
        has_sibling = sibling_abs.is_file()

        prod_rel = _derive_prod_module(rel_posix)
        gate_covered = _prod_is_gate_covered(prod_rel) if prod_rel else False

        safety_reason: str
        if has_sibling:
            safety_reason = f"sibling {sibling_name} exists"
        elif not gate_covered:
            if prod_rel and prod_rel.endswith("__init__.py"):
                safety_reason = f"prod is __init__.py (gate excludes)"
            else:
                safety_reason = f"prod {prod_rel or '?'} outside harness-coverage gate surface"
        else:
            skipped_unsafe.append(
                {
                    "source": rel_posix,
                    "prod_module": prod_rel,
                    "reason": "stub is sole test for gate-covered prod module",
                    "test_count": entry.get("test_count", 0),
                }
            )
            continue

        candidates.append(
            {
                "source": rel_posix,
                "sibling": str((path.parent / sibling_name)).replace("\\", "/") if has_sibling else None,
                "prod_module": prod_rel,
                "dest": f"tools/archive/stub_tests/{rel_posix}",
                "test_count": entry.get("test_count", 0),
                "safety": safety_reason,
            }
        )

    plan = {
        "archive_count": len(candidates),
        "skipped_unsafe": len(skipped_unsafe),
        "kept_non_stub": kept_non_stub,
        "kept_empty_or_error": kept_empty_or_error,
        "candidates": candidates,
        "skipped": skipped_unsafe,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"Archive plan: {out_path}")
    print(
        f"  archive_count={len(candidates)} skipped_unsafe={len(skipped_unsafe)} "
        f"kept_non_stub={kept_non_stub} kept_empty_or_error={kept_empty_or_error}"
    )
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    path = (repo_root / args.file).resolve() if not Path(args.file).is_absolute() else Path(args.file)
    result = classify_file(path)
    print(json.dumps(result, indent=2))
    if args.expected and result["label"] != args.expected:
        return 1
    return 0


# ----------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ADG stub-test triage (AST-based)")
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("classify", help="classify all _adg.py files")
    c.add_argument("--pattern", default="tests/**/*_adg.py")
    c.add_argument("--json", help="write classification report to this JSON path")
    c.set_defaults(func=cmd_classify)

    a = sub.add_parser("archive-plan", help="derive safe archive candidates")
    a.add_argument("--input", required=True, help="classification JSON from `classify`")
    a.add_argument("--output", required=True, help="archive plan JSON path")
    a.set_defaults(func=cmd_archive_plan)

    v = sub.add_parser("verify", help="single-file classification check")
    v.add_argument("--file", required=True)
    v.add_argument("--expected", choices=["stub", "non-stub", "empty", "error"])
    v.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
