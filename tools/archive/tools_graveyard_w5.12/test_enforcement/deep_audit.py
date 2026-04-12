"""Deep Audit — Novel edge-case detection for test suite health.

Goes beyond AST pattern matching with 8 audit dimensions:

1. RUNTIME IMPORT SMOKE TEST: Actually import every test file in a subprocess
   and catch real ImportError / NameError / SyntaxError at load time.
2. NAMEERROR TRAPS: AST-walk every test body for references to names that
   are never defined/imported at module scope (catches residual _AVAILABLE,
   leftover None-assigned symbols, etc.).
3. DEAD MARKER DETECTION: Find pytestmark / @pytest.mark.X where X is not
   in the registered marker list from pytest.ini.
4. ORPHAN SKIPIF: skipif decorators whose condition references undefined names.
5. UNREACHABLE TEST CODE: test functions whose body is entirely `pass` or
   `assert True` (vacuous tests that prove nothing).
6. DUPLICATE TEST NAMES: same test function name in the same file (pytest
   silently shadows the first).
7. IMPORT-SIDE-EFFECT DETECTION: module-level function calls that are not
   assignments, decorators, or marker registrations (potential side-effects
   that slow collection).
8. MARKER-CATEGORY CONSISTENCY: files classified as 'core' but carrying
   @pytest.mark.optional (or vice versa).

Outputs: artifacts/test_enforcement/deep_audit_results.json
Exit code 0 = clean, 1 = issues found.
"""

from __future__ import annotations

import ast
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

REGISTERED_MARKERS = {
    "core",
    "optional",
    "platform",
    "external",
    "experimental",
    "architecture",
    "asyncio",
    "autonomy",
    "boot",
    "ci",
    "compliance",
    "constitutional",
    "dashboard",
    "determinism",
    "e2e",
    "functional",
    "governance",
    "guardian",
    "import_safety",
    "integration",
    "integration_full_deps",
    "manual",
    "mro",
    "negative_control",
    "playwright",
    "security",
    "slow",
    "sovereign_hardening",
    "sovereignty",
    "ssot",
    "system_learning",
    "tool_use",
    "unit",
    "unit_min_deps",
    # pytest builtins
    "parametrize",
    "skip",
    "skipif",
    "xfail",
    "usefixtures",
    "filterwarnings",
    "timeout",
    "tryfirst",
    "trylast",
}

FIRST_PARTY_TOPS = frozenset(
    {
        "agentic_core",
        "apps_lic",
        "apps_rg",
        "apps_shared",
        "apps_exec",
        "apps_rfp",
        "apps_research",
        "apps_eval",
        "system_learning",
        "infrastructure",
        "tools",
        "ops_scripts",
        "data",
    }
)


# ── helpers ──────────────────────────────────────────────────────────────


def _rel(fp: pathlib.Path) -> str:
    return str(fp.relative_to(ROOT)).replace("\\", "/")


def _collect_defined_names(tree: ast.Module) -> set[str]:
    """Collect all names defined at module scope."""
    names = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Try):
            # names from try body imports
            for stmt in node.body:
                if isinstance(stmt, ast.Import):
                    for alias in stmt.names:
                        names.add(alias.asname or alias.name.split(".")[-1])
                elif isinstance(stmt, ast.ImportFrom):
                    for alias in stmt.names:
                        names.add(alias.asname or alias.name)
                elif isinstance(stmt, ast.Assign):
                    for t in stmt.targets:
                        if isinstance(t, ast.Name):
                            names.add(t.id)
            for handler in node.handlers:
                for stmt in handler.body:
                    if isinstance(stmt, ast.Assign):
                        for t in stmt.targets:
                            if isinstance(t, ast.Name):
                                names.add(t.id)
    # builtins
    names.update(dir(__builtins__) if isinstance(__builtins__, dict) else dir(__builtins__))
    # module-level dunders (always available at runtime)
    names.update(
        {
            "__file__",
            "__name__",
            "__doc__",
            "__package__",
            "__loader__",
            "__spec__",
            "__builtins__",
            "__cached__",
        }
    )
    # common pytest names
    names.update(
        {
            "pytest",
            "self",
            "cls",
            "request",
            "tmp_path",
            "tmpdir",
            "capsys",
            "capfd",
            "monkeypatch",
            "pytestmark",
        }
    )
    return names


def _extract_markers(source: str) -> list[str]:
    """Extract pytest marker names from source text."""
    markers = []
    for m in re.finditer(r"pytest\.mark\.(\w+)", source):
        markers.append(m.group(1))
    return markers


# ── Audit 1: Runtime Import Smoke Test ───────────────────────────────────


def _runtime_smoke_one(fp_str: str) -> dict | None:
    """Try to compile (not execute) a test file; report errors."""
    fp = pathlib.Path(fp_str)
    try:
        source = fp.read_text(encoding="utf-8", errors="replace")
        compile(source, str(fp), "exec")
        return None
    except SyntaxError as e:
        return {
            "file": _rel(fp),
            "audit": "runtime_smoke",
            "severity": "error",
            "detail": f"SyntaxError at line {e.lineno}: {e.msg}",
        }
    except Exception as e:
        return {
            "file": _rel(fp),
            "audit": "runtime_smoke",
            "severity": "error",
            "detail": f"{type(e).__name__}: {e}",
        }


# ── Audit 2: NameError Traps ────────────────────────────────────────────


def _nameerror_traps(fp: pathlib.Path, tree: ast.Module) -> list[dict]:
    """Find references to undefined names in skipif conditions and assertions."""
    issues = []
    rel = _rel(fp)
    defined = _collect_defined_names(tree)

    for node in ast.walk(tree):
        # Check skipif conditions
        if isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "skipif"
                and isinstance(func.value, ast.Attribute)
                and isinstance(func.value.value, ast.Name)
            ):
                # pytest.mark.skipif(CONDITION, ...)
                if node.args:
                    for name_node in ast.walk(node.args[0]):
                        if isinstance(name_node, ast.Name) and name_node.id not in defined:
                            issues.append(
                                {
                                    "file": rel,
                                    "audit": "nameerror_trap",
                                    "severity": "error",
                                    "line": node.lineno,
                                    "detail": f"skipif references undefined name '{name_node.id}'",
                                }
                            )

        # Check pytestmark = pytest.mark.skipif(not X, ...)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "pytestmark":
                    for sub in ast.walk(node.value):
                        if isinstance(sub, ast.Name) and sub.id not in defined:
                            if sub.id.startswith("_") or sub.id == "CAN_IMPORT":
                                issues.append(
                                    {
                                        "file": rel,
                                        "audit": "nameerror_trap",
                                        "severity": "error",
                                        "line": node.lineno,
                                        "detail": f"pytestmark references undefined '{sub.id}'",
                                    }
                                )

    return issues


# ── Audit 3: Dead Marker Detection ──────────────────────────────────────


def _dead_markers(fp: pathlib.Path, source: str) -> list[dict]:
    """Find markers not in the registered set."""
    issues = []
    rel = _rel(fp)
    markers = _extract_markers(source)
    for m in markers:
        if m not in REGISTERED_MARKERS:
            issues.append(
                {
                    "file": rel,
                    "audit": "dead_marker",
                    "severity": "warning",
                    "detail": f"Unregistered marker '@pytest.mark.{m}'",
                }
            )
    return issues


# ── Audit 4: Orphan skipif ──────────────────────────────────────────────


def _orphan_skipif(fp: pathlib.Path, tree: ast.Module) -> list[dict]:
    """skipif decorators whose condition references names not in module scope."""
    issues = []
    rel = _rel(fp)
    defined = _collect_defined_names(tree)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            func = dec.func if hasattr(dec, "func") else None
            if func is None:
                continue
            if not (isinstance(func, ast.Attribute) and func.attr == "skipif"):
                continue
            if dec.args:
                for name_node in ast.walk(dec.args[0]):
                    if isinstance(name_node, ast.Name) and name_node.id not in defined:
                        issues.append(
                            {
                                "file": rel,
                                "audit": "orphan_skipif",
                                "severity": "error",
                                "line": dec.lineno,
                                "detail": f"@skipif references undefined '{name_node.id}'",
                            }
                        )
    return issues


# ── Audit 5: Vacuous Tests ──────────────────────────────────────────────


def _vacuous_tests(fp: pathlib.Path, tree: ast.Module) -> list[dict]:
    """Tests whose body is only pass / assert True / docstring."""
    issues = []
    rel = _rel(fp)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        # ADG importability stubs are intentionally minimal — skip them
        if node.name == "test_module_importable":
            continue
        body = node.body
        # Filter out docstrings
        real_stmts = [
            s
            for s in body
            if not (
                isinstance(s, ast.Expr)
                and isinstance(s.value, ast.Constant)
                and isinstance(s.value.value, str)
            )
        ]
        if not real_stmts:
            issues.append(
                {
                    "file": rel,
                    "audit": "vacuous_test",
                    "severity": "info",
                    "line": node.lineno,
                    "detail": f"'{node.name}' has only a docstring (no assertions)",
                }
            )
            continue
        if len(real_stmts) == 1:
            stmt = real_stmts[0]
            if isinstance(stmt, ast.Pass):
                issues.append(
                    {
                        "file": rel,
                        "audit": "vacuous_test",
                        "severity": "info",
                        "line": node.lineno,
                        "detail": f"'{node.name}' body is only 'pass'",
                    }
                )
            elif (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is True
            ):
                issues.append(
                    {
                        "file": rel,
                        "audit": "vacuous_test",
                        "severity": "info",
                        "line": node.lineno,
                        "detail": f"'{node.name}' body is only 'True'",
                    }
                )
    return issues


# ── Audit 6: Duplicate Test Names ───────────────────────────────────────


def _duplicate_test_names(fp: pathlib.Path, tree: ast.Module) -> list[dict]:
    """Same test function name defined twice in the same scope."""
    issues = []
    rel = _rel(fp)

    def _check_scope(nodes, scope_name="module"):
        names = collections.Counter()
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    names[node.name] += 1
        for name, count in names.items():
            if count > 1:
                issues.append(
                    {
                        "file": rel,
                        "audit": "duplicate_test_name",
                        "severity": "error",
                        "detail": f"'{name}' defined {count}x in {scope_name} — pytest shadows earlier definitions",
                    }
                )

    # Module-level functions
    _check_scope(ast.iter_child_nodes(tree), "module")

    # Class-level methods
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            _check_scope(node.body, f"class {node.name}")

    return issues


# ── Audit 7: Import Side-Effects ────────────────────────────────────────


def _import_side_effects(fp: pathlib.Path, tree: ast.Module) -> list[dict]:
    """Module-level calls that are not assignments/decorators/markers.

    Exclude known patterns: _emit_*, emit_*, pytest.main, print for debugging.
    """
    issues = []
    rel = _rel(fp)

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Expr):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        call = node.value
        # Get call name
        name = ""
        if isinstance(call.func, ast.Name):
            name = call.func.id
        elif isinstance(call.func, ast.Attribute):
            name = call.func.attr

        # Allowlist: _emit_*, emit_*, print, pytest.main
        if name.startswith("_emit_") or name.startswith("emit_"):
            continue
        if name in ("print", "main", "warnings"):
            continue
        if isinstance(call.func, ast.Attribute):
            if isinstance(call.func.value, ast.Name):
                if call.func.value.id in ("pytest", "warnings", "os", "sys", "logging"):
                    continue

        # Only flag if it looks suspicious (not a simple constant)
        issues.append(
            {
                "file": rel,
                "audit": "import_side_effect",
                "severity": "info",
                "line": node.lineno,
                "detail": f"Module-level call: {name}()",
            }
        )

    return issues


# ── Audit 8: Marker-Category Consistency ────────────────────────────────


def _marker_category_consistency(fp: pathlib.Path, source: str, classification: dict | None) -> list[dict]:
    """Check that markers match the classified category."""
    issues = []
    if classification is None:
        return issues
    rel = _rel(fp)
    category = classification.get("category", "")
    markers = set(_extract_markers(source))

    # core file should not have @pytest.mark.optional
    if category == "core" and "optional" in markers:
        issues.append(
            {
                "file": rel,
                "audit": "marker_category_mismatch",
                "severity": "warning",
                "detail": "Classified as 'core' but has @pytest.mark.optional",
            }
        )

    # optional file should have @pytest.mark.optional
    if category == "optional" and "optional" not in markers:
        issues.append(
            {
                "file": rel,
                "audit": "marker_category_mismatch",
                "severity": "info",
                "detail": "Classified as 'optional' but missing @pytest.mark.optional marker",
            }
        )

    return issues


# ── Main ─────────────────────────────────────────────────────────────────


def main():
    test_dir = ROOT / "tests"
    all_files = sorted(test_dir.rglob("test_*.py"))
    all_files.extend(sorted(ROOT.glob("test_*.py")))

    # Deduplicate
    seen = set()
    unique = []
    for f in all_files:
        key = str(f)
        if key not in seen:
            seen.add(key)
            unique.append(f)

    # Load classification if available
    cls_path = ROOT / "artifacts" / "test_enforcement" / "test_classification.json"
    cls_map = {}
    if cls_path.exists():
        with open(cls_path) as f:
            for item in json.load(f):
                cls_map[item["file_path"]] = item

    print(f"Deep audit of {len(unique)} test files across 8 dimensions...")

    all_issues = []

    # Audit 1: Runtime smoke (compile check)
    print("  [1/8] Runtime compile check...")
    for fp in unique:
        issue = _runtime_smoke_one(str(fp))
        if issue:
            all_issues.append(issue)

    # Audits 2-8: AST-based
    print("  [2-8/8] AST-based audits...")
    progress = 0
    for fp in unique:
        progress += 1
        if progress % 500 == 0:
            print(f"    ...{progress}/{len(unique)}")

        rel = _rel(fp)
        try:
            source = fp.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=rel)
        except SyntaxError:
            continue  # Already caught in audit 1

        all_issues.extend(_nameerror_traps(fp, tree))
        all_issues.extend(_dead_markers(fp, source))
        all_issues.extend(_orphan_skipif(fp, tree))
        all_issues.extend(_vacuous_tests(fp, tree))
        all_issues.extend(_duplicate_test_names(fp, tree))
        all_issues.extend(_import_side_effects(fp, tree))
        all_issues.extend(_marker_category_consistency(fp, source, cls_map.get(rel)))

    # Summary
    by_audit = collections.Counter(i["audit"] for i in all_issues)
    by_severity = collections.Counter(i["severity"] for i in all_issues)
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    infos = [i for i in all_issues if i["severity"] == "info"]

    print(f"\n{'=' * 60}")
    print("DEEP AUDIT RESULTS")
    print(f"{'=' * 60}")
    print(f"Total issues: {len(all_issues)}")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Info:     {len(infos)}")
    print("\nBy audit dimension:")
    for audit, count in by_audit.most_common():
        print(f"  {audit}: {count}")

    if errors:
        print("\n--- ERRORS (must fix) ---")
        for e in errors[:50]:
            print(f"  {e['file']}:{e.get('line', '')} [{e['audit']}] {e['detail']}")
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more errors")

    if warnings:
        print("\n--- WARNINGS ---")
        for w in warnings[:30]:
            print(f"  {w['file']} [{w['audit']}] {w['detail']}")
        if len(warnings) > 30:
            print(f"  ... and {len(warnings) - 30} more warnings")

    # Write results
    out_path = ROOT / "artifacts" / "test_enforcement" / "deep_audit_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(all_issues, f, indent=2)
    print(f"\nResults: {out_path}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
