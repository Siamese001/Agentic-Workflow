"""apps_rg import-boundary ratchet.

Existing concrete core imports are allowed only if listed in the baseline.
New imports fail immediately.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG_ROOT = REPO_ROOT / "apps_rg"
BASELINE_PATH = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "apps_rg"
    / "apps_rg_forbidden_core_import_baseline.json"
)

BOUNDARY_MESSAGE = (
    "apps_rg must bind to spine contracts, not concrete agentic_core "
    "implementation internals."
)

FORBIDDEN_PREFIXES = (
    "agentic_core.runtime.entrypoints",
    "agentic_core.runtime.entry",
    "agentic_core.L0_routing",
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
    "agentic_core.runtime.exit",
    "agentic_core.runtime.judges",
    "agentic_core.runtime.l6",
)


def _production_py_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(APPS_RG_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if "tests" in path.parts or path.name.startswith("test_"):
            continue
        files.append(path)
    return files


def _scan_file(path: Path) -> list[dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    rel = path.relative_to(REPO_ROOT).as_posix()
    violations: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                violations.extend(_violation_for(rel, node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            violations.extend(_violation_for(rel, node.lineno, node.module or ""))

    return violations


def _violation_for(rel: str, line: int, imported: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for prefix in FORBIDDEN_PREFIXES:
        if imported == prefix or imported.startswith(prefix + "."):
            found.append(
                {
                    "file": rel,
                    "line": line,
                    "import": imported,
                    "forbidden_prefix": prefix,
                }
            )
    return found


def _key(v: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(v["file"]),
        str(v["import"]),
        str(v["forbidden_prefix"]),
    )


def _load_baseline() -> set[tuple[str, str, str]]:
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {_key(v) for v in data.get("violations", [])}


def test_no_new_concrete_agentic_core_imports_from_apps_rg_production() -> None:
    baseline = _load_baseline()
    current: list[dict[str, Any]] = []
    for path in _production_py_files():
        current.extend(_scan_file(path))

    new_violations = [v for v in current if _key(v) not in baseline]
    assert not new_violations, (
        BOUNDARY_MESSAGE
        + "\nNew forbidden imports:\n"
        + "\n".join(
            f"{v['file']}:{v['line']}: {v['import']} "
            f"(prefix {v['forbidden_prefix']})"
            for v in new_violations
        )
    )
