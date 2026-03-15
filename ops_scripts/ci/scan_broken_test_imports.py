"""CI Guard 1+3: Broken test import scanner + stale mirror test detector.

Fails CI if:
  - Any test file has ALL imports broken (fully orphaned / Cat B)
  - Any GENERATED_MIRROR_TEST file has an unresolvable importlib target

Exit codes:
  0 = clean
  1 = violations found

Usage:
    python ops_scripts/ci/scan_broken_test_imports.py
    python ops_scripts/ci/scan_broken_test_imports.py --threshold 0
"""

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR as _TESTS_DIR_STR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = ROOT / _TESTS_DIR_STR
PROJECT_PREFIXES = (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    OPS_SCRIPTS_DIR,
)
EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
FULLY_ORPHANED_THRESHOLD = 0
STALE_MIRROR_THRESHOLD = 0


def _module_exists(mod: str) -> bool:
    parts = mod.split(".")
    r = ROOT
    if (r / Path(*parts) / "__init__.py").exists():
        return True
    if len(parts) > 1 and (r / Path(*parts[:-1]) / (parts[-1] + ".py")).exists():
        return True
    if len(parts) == 1 and (r / (parts[0] + ".py")).exists():
        return True
    return False


def _extract_imports(tree: ast.Module) -> list[str]:
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.append(node.module)
    return mods


def _extract_mirror_targets(tree: ast.Module) -> list[str]:
    targets = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "import_module":
                if node.args and isinstance(node.args[0], ast.Constant):
                    targets.append(str(node.args[0].value))
    return targets


def _has_mirror_marker(source: str) -> bool:
    return "GENERATED_MIRROR_TEST" in source


def _is_project_import(mod: str) -> bool:
    return any(mod.startswith(p) for p in PROJECT_PREFIXES)


def scan_tests() -> tuple[list[str], list[str]]:
    fully_orphaned: list[str] = []
    stale_mirrors: list[str] = []

    for fpath in TESTS_DIR.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in fpath.parts):
            continue
        if not fpath.name.startswith("test_"):
            continue

        try:
            source = fpath.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue

        rel = str(fpath.relative_to(ROOT)).replace("\\", "/")

        # Guard 3: stale mirror test
        if _has_mirror_marker(source):
            targets = _extract_mirror_targets(tree)
            project_targets = [t for t in targets if _is_project_import(t)]
            if project_targets and all(not _module_exists(t) for t in project_targets):
                stale_mirrors.append(rel)
            continue

        # Guard 1: fully orphaned (all project imports broken)
        imports = [m for m in _extract_imports(tree) if _is_project_import(m)]
        if imports and all(not _module_exists(m) for m in imports):
            fully_orphaned.append(rel)

    return fully_orphaned, stale_mirrors


def main() -> int:
    fully_orphaned, stale_mirrors = scan_tests()

    violations = 0

    print(f"Broken import scan: fully_orphaned={len(fully_orphaned)}  threshold={FULLY_ORPHANED_THRESHOLD}")
    if len(fully_orphaned) > FULLY_ORPHANED_THRESHOLD:
        print(
            f"FAIL: {len(fully_orphaned)} fully-orphaned test files (threshold={FULLY_ORPHANED_THRESHOLD}):"
        )
        for f in sorted(fully_orphaned)[:30]:
            print(f"  {f}")
        violations += len(fully_orphaned)
    else:
        print(f"OK: fully_orphaned={len(fully_orphaned)} <= {FULLY_ORPHANED_THRESHOLD}")

    print(f"Stale mirror scan: stale_mirrors={len(stale_mirrors)}  threshold={STALE_MIRROR_THRESHOLD}")
    if len(stale_mirrors) > STALE_MIRROR_THRESHOLD:
        print(
            f"FAIL: {len(stale_mirrors)} stale GENERATED_MIRROR_TEST files (threshold={STALE_MIRROR_THRESHOLD}):"
        )
        for f in sorted(stale_mirrors)[:20]:
            print(f"  {f}")
        violations += len(stale_mirrors)
    else:
        print(f"OK: stale_mirrors={len(stale_mirrors)} <= {STALE_MIRROR_THRESHOLD}")

    return 0 if violations == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
