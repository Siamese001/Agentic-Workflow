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
import json
import sys
import warnings
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
)
from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR as _TESTS_DIR_STR,
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
PARTIAL_BREAK_BASELINE_PATH = ROOT / "artifacts" / "import_health" / "test_partial_break_baseline.json"

# Try to import ADG Query Bridge for ADG-powered import validation
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "adg"))
    from adg_query_bridge import ADGQueryBridge, FileMatch
    ADG_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"ADG Query Bridge unavailable, falling back to AST: {e}")
    ADG_AVAILABLE = False


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


def _load_partial_break_baseline() -> set[str]:
    """Load baseline of known-broken import keys (file::module)."""
    if not PARTIAL_BREAK_BASELINE_PATH.is_file():
        return set()
    try:
        data = json.loads(PARTIAL_BREAK_BASELINE_PATH.read_text(encoding="utf-8"))
        return set(data.get("broken_imports", []))
    except Exception:  # guardian: allow-broad-exception -- non-critical: baseline read failure falls back to empty set
        return set()


def _save_partial_break_baseline(broken: list[tuple[str, str]]) -> None:
    """Persist the current broken-import set as the new baseline."""
    PARTIAL_BREAK_BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted(f"{rel}::{mod}" for rel, mod in broken)
    data = {"schema_version": 1, "broken_import_count": len(keys), "broken_imports": keys}
    PARTIAL_BREAK_BASELINE_PATH.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )


def _collect_partially_broken(tree: ast.AST) -> list[str]:
    """Return list of project import modules that do NOT resolve on disk."""
    broken = []
    for mod in _extract_imports(tree):
        if _is_project_import(mod) and not _module_exists(mod):
            broken.append(mod)
    return broken


def scan_tests() -> tuple[list[str], list[str], list[tuple[str, str]]]:
    fully_orphaned: list[str] = []
    stale_mirrors: list[str] = []
    partial_breaks: list[tuple[str, str]] = []  # (rel_path, broken_module)
    # guardian: Parsing and encoding errors need separate handling strategies
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

        # Use ADG for import validation when available
        if ADG_AVAILABLE:
            try:
                fully_orphaned_check, stale_mirror_check = _scan_test_with_adg(fpath, tree, source, rel)
                if fully_orphaned_check:
                    fully_orphaned.append(rel)
                if stale_mirror_check:
                    stale_mirrors.append(rel)
            except Exception as e:
                warnings.warn(f"ADG test scan failed for {rel}, falling back to AST: {e}")
                fully_orphaned_check, stale_mirror_check = _scan_test_with_ast(fpath, tree, source, rel)
                if fully_orphaned_check:
                    fully_orphaned.append(rel)
                if stale_mirror_check:
                    stale_mirrors.append(rel)
        else:
            fully_orphaned_check, stale_mirror_check = _scan_test_with_ast(fpath, tree, source, rel)
            if fully_orphaned_check:
                fully_orphaned.append(rel)
            if stale_mirror_check:
                stale_mirrors.append(rel)

        # Guard 4: any broken project import (partial-break regression detection)
        for broken_mod in _collect_partially_broken(tree):
            partial_breaks.append((rel, broken_mod))

    return fully_orphaned, stale_mirrors, partial_breaks


def _scan_test_with_adg(fpath: Path, tree: ast.AST, source: str, rel: str) -> tuple[bool, bool]:
    """Scan test file using ADG for import validation."""
    try:
        bridge = ADGQueryBridge()

        # Guard 3: stale mirror test
        if _has_mirror_marker(source):
            targets = _extract_mirror_targets(tree)
            project_targets = [t for t in targets if _is_project_import(t)]
            if project_targets:
                # Check if targets exist in ADG
                missing_targets = []
                for target in project_targets:
                    # Check if module exists in ADG
                    importers = bridge.files_importing(target)
                    if not importers and not _module_exists(target):
                        missing_targets.append(target)

                if missing_targets and all(not _module_exists(t) for t in missing_targets):
                    return False, True  # stale mirror
            return False, False

        # Guard 1: fully orphaned (all project imports broken)
        imports = [m for m in _extract_imports(tree) if _is_project_import(m)]
        if imports:
            # Check if imports exist in ADG
            missing_imports = []
            for imp in imports:
                importers = bridge.files_importing(imp)
                if not importers and not _module_exists(imp):
                    missing_imports.append(imp)

            if missing_imports and all(not _module_exists(m) for m in missing_imports):
                return True, False  # fully orphaned

        return False, False

    except Exception as e:
        warnings.warn(f"ADG validation failed: {e}")
        # Fall back to AST
        return _scan_test_with_ast(fpath, tree, source, rel)


def _scan_test_with_ast(fpath: Path, tree: ast.AST, source: str, rel: str) -> tuple[bool, bool]:
    """Original AST-based test scanning as fallback."""
    # Guard 3: stale mirror test
    if _has_mirror_marker(source):
        targets = _extract_mirror_targets(tree)
        project_targets = [t for t in targets if _is_project_import(t)]
        if project_targets and all(not _module_exists(t) for t in project_targets):
            return False, True  # stale mirror

    # Guard 1: fully orphaned (all project imports broken)
    imports = [m for m in _extract_imports(tree) if _is_project_import(m)]
    if imports and all(not _module_exists(m) for m in imports):
        return True, False  # fully orphaned

    return False, False


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Broken test import scanner (Guards 1+3+4)")
    parser.add_argument(
        "--update-test-baseline",
        action="store_true",
        help="Advance the Guard 4 partial-break baseline to the current state (use after intentional fixes)",
    )
    parser.add_argument("--threshold", type=int, default=None, help="Override FULLY_ORPHANED_THRESHOLD")
    args = parser.parse_args()

    fully_orphaned, stale_mirrors, partial_breaks = scan_tests()

    violations = 0

    print(f"Broken import scan: fully_orphaned={len(fully_orphaned)}  threshold={FULLY_ORPHANED_THRESHOLD}")
    if len(fully_orphaned) > FULLY_ORPHANED_THRESHOLD:
        print(
            f"FAIL: {len(fully_orphaned)} fully-orphaned test files (threshold={FULLY_ORPHANED_THRESHOLD}):",
        )
        for f in sorted(fully_orphaned)[:30]:
            print(f"  {f}")
        violations += len(fully_orphaned)
    else:
        print(f"OK: fully_orphaned={len(fully_orphaned)} <= {FULLY_ORPHANED_THRESHOLD}")

    print(f"Stale mirror scan: stale_mirrors={len(stale_mirrors)}  threshold={STALE_MIRROR_THRESHOLD}")
    if len(stale_mirrors) > STALE_MIRROR_THRESHOLD:
        print(
            f"FAIL: {len(stale_mirrors)} stale GENERATED_MIRROR_TEST files (threshold={STALE_MIRROR_THRESHOLD}):",
        )
        for f in sorted(stale_mirrors)[:20]:
            print(f"  {f}")
        violations += len(stale_mirrors)
    else:
        print(f"OK: stale_mirrors={len(stale_mirrors)} <= {STALE_MIRROR_THRESHOLD}")

    # Guard 4: partial-break regression detection (baseline-drift)
    if args.update_test_baseline:
        _save_partial_break_baseline(partial_breaks)
        print(f"[Guard 4] Baseline updated: {len(partial_breaks)} broken import(s) recorded")
        print(f"[Guard 4] Baseline path: {PARTIAL_BREAK_BASELINE_PATH}")
        return 0 if violations == 0 else 1

    baseline = _load_partial_break_baseline()
    current_keys = {f"{rel}::{mod}" for rel, mod in partial_breaks}
    new_breaks = sorted(current_keys - baseline)
    fixed_breaks = sorted(baseline - current_keys)

    print(f"Partial-break scan (Guard 4): total={len(partial_breaks)}  baseline={len(baseline)}  new={len(new_breaks)}  fixed={len(fixed_breaks)}")
    if new_breaks:
        print(f"FAIL: {len(new_breaks)} new broken project import(s) in tests (not in baseline):")
        for entry in new_breaks[:30]:
            print(f"  {entry}")
        print("  Fix the broken imports, then run: python ops_scripts/ci/scan_broken_test_imports.py --update-test-baseline")
        violations += len(new_breaks)
    else:
        print("OK: no new broken imports in tests")
    if fixed_breaks:
        print(f"  [{len(fixed_breaks)} previously-broken import(s) now resolve \u2014 run --update-test-baseline to shrink the baseline]")

    return 0 if violations == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
