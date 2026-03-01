"""
agentic_core/enforcement/sealed_interface_check.py

AST-based enforcement: blocks apps_* from importing sealed interface
implementation modules (_impl pattern) and direct L* layer imports.

Runs as CI gate and can be invoked as:
    python -m agentic_core.enforcement.sealed_interface_check

EXIT CODES:
    0 — no violations found
    1 — violations found (prints details)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_ROOTS = [
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_shared",
]

FORBIDDEN_IMPORT_PATTERNS = [
    "agentic_core.interfaces._",  # _impl and other private submodules
]

FORBIDDEN_LAYER_PREFIXES = [
    "agentic_core.L0_",
    "agentic_core.L1_",
    "agentic_core.L2_",
    "agentic_core.L3_",
    "agentic_core.L4_",
    "agentic_core.L5_",
    "agentic_core.L6_",
]


def _get_import_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
    return modules


def check_file(path: Path) -> list[str]:
    """Return list of violation strings for a single file."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [f"SYNTAX_ERROR: {path}: {exc}"]

    violations: list[str] = []
    rel = path.relative_to(REPO_ROOT)

    for module in _get_import_modules(tree):
        for pat in FORBIDDEN_IMPORT_PATTERNS:
            if module.startswith(pat):
                violations.append(
                    f"SEALED_IMPL_BYPASS: {rel} imports '{module}' "
                    f"(sealed implementation modules are forbidden in apps_*)"
                )
        for prefix in FORBIDDEN_LAYER_PREFIXES:
            if module.startswith(prefix):
                violations.append(
                    f"DIRECT_LAYER_IMPORT: {rel} imports '{module}' (use agentic_core.interfaces.* instead)"
                )

    return violations


def run_check(apps_roots: list[Path] = APPS_ROOTS) -> list[str]:
    """Scan all apps_* Python files and return all violations."""
    all_violations: list[str] = []
    for root in apps_roots:
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            all_violations.extend(check_file(py_file))
    return all_violations


def main() -> int:
    violations = run_check()
    if violations:
        print(f"FAIL: {len(violations)} sovereignty violation(s) found:")
        for v in violations:
            print(f"  {v}")
        return 1
    total = sum(len(list(r.rglob("*.py"))) for r in APPS_ROOTS if r.exists())
    print(f"OK: sealed interface check passed ({total} files scanned, 0 violations)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
