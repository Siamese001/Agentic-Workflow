"""CI gate: opt-in enforcement that @requires_sealed_return classes return SealedL2Artifact.

Plan: `.windsurf/plans/l2-execute-v2-agent-conformance-c8e4f1.md` §W5.
Closes G-V8 from plan §5.

The gate is OPT-IN: it only inspects Python classes that carry the marker
attribute ``__l2v2_requires_sealed_return__ = True`` (set by the
``@requires_sealed_return`` decorator from
``agentic_core.L2_execution.enforcement.agent_seal_helper``).

Legacy agents without the marker are NOT inspected — this plan does not
retroactively fail 88 existing agents. W6 migrates 2 exemplars to opt in.

The gate uses AST inspection (not import) so it can run on files that have
heavy import-time side effects (e.g. ChromaDB init) without triggering them.

Exit codes:
    0 — all inspected classes conform
    1 — at least one conformance violation
    2 — internal error (unreadable file, etc.)
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterator

MARKER_DECORATOR_NAME = "requires_sealed_return"
MARKER_ATTR_NAME = "__l2v2_requires_sealed_return__"
SEALED_RETURN_TYPE = "SealedL2Artifact"

# Directories to scan for Python agent files.
SCAN_ROOTS = (
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
)


def _iter_python_files(root: Path) -> Iterator[Path]:
    for p in root.rglob("*.py"):
        # Skip archives, caches, tests — the gate only checks production agents.
        parts = set(p.parts)
        if "archives" in parts or "__pycache__" in parts or "tests" in parts:
            continue
        yield p


def _class_has_marker(cls: ast.ClassDef) -> bool:
    """Detect either the @requires_sealed_return decorator or the __l2v2_... attr."""
    # Decorator form: @requires_sealed_return
    for dec in cls.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == MARKER_DECORATOR_NAME:
            return True
        if isinstance(dec, ast.Attribute) and dec.attr == MARKER_DECORATOR_NAME:
            return True
    # Body form: __l2v2_requires_sealed_return__ = True
    for stmt in cls.body:
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name) and t.id == MARKER_ATTR_NAME:
                    if isinstance(stmt.value, ast.Constant) and stmt.value.value is True:
                        return True
    return False


def _return_annotation_mentions_sealed(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True if the function's return annotation contains SealedL2Artifact."""
    if func.returns is None:
        return False
    src = ast.unparse(func.returns)
    return SEALED_RETURN_TYPE in src


def _check_class(cls: ast.ClassDef, file_path: Path) -> list[str]:
    """Return a list of violation strings for this class."""
    violations: list[str] = []
    for stmt in cls.body:
        if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Skip private / dunder / properties / __init__
        if stmt.name.startswith("_"):
            continue
        # Skip methods explicitly marked as gate-exempt
        exempt = any(
            (isinstance(d, ast.Name) and d.id == "sealed_exempt")
            or (isinstance(d, ast.Attribute) and d.attr == "sealed_exempt")
            for d in stmt.decorator_list
        )
        if exempt:
            continue
        if not _return_annotation_mentions_sealed(stmt):
            violations.append(
                f"{file_path}:{stmt.lineno}: {cls.name}.{stmt.name} "
                f"return type missing {SEALED_RETURN_TYPE}"
            )
    return violations


def scan_file(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        # Gate is informative, not destructive: record and move on.
        return [f"{path}: parse_error {exc!r}"]
    results: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and _class_has_marker(node):
            results.extend(_check_class(node, path))
    return results


def scan_repo(repo_root: Path) -> list[str]:
    all_violations: list[str] = []
    for top in SCAN_ROOTS:
        root = repo_root / top
        if not root.exists():
            continue
        for f in _iter_python_files(root):
            all_violations.extend(scan_file(f))
    return all_violations


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    repo_root = Path(argv[0]).resolve() if argv else Path.cwd().resolve()
    if not repo_root.exists():
        sys.stderr.write(f"[check_agent_sealed_return] repo root not found: {repo_root}\n")
        return 2
    violations = scan_repo(repo_root)
    if not violations:
        print("[check_agent_sealed_return] OK — 0 violations in opt-in marked classes")
        return 0
    print(f"[check_agent_sealed_return] FAIL — {len(violations)} violation(s)")
    for v in violations:
        print(f"  {v}")
    print(
        "\nOnly classes decorated with @requires_sealed_return (or carrying "
        f"{MARKER_ATTR_NAME} = True) are inspected. Legacy agents unaffected."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
