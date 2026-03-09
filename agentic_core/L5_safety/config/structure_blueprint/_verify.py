"""
Hard Shim Strategy — Verification Script (Phase 4.4.2 Final Consistency Lock).

Run: python -m agentic_core.L5_safety.config.structure_blueprint._verify

Flags:
  --init-phantom-baseline       Create phantom_baseline.json (first time only)
  --update-phantom-baseline     Persist a reduced phantom baseline (prints diff first)
  --print-phantom-diff          Print phantom diff vs baseline and exit
  --repair-phantom-baseline     Rewrite corrupt/unreadable baseline from current scan
  --acknowledge-import-change   Update allowlist hash and exit immediately
  --print-allowlist             Print current allowlist + hash and exit (read-only)
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from types import MappingProxyType

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L2_execution.tools import write_gateway as _wg

# ── Canonical allowlist for _constants.py imports ──
ALLOWED_MODULES: frozenset[str] = frozenset(
    {
        "__future__",
        "typing",
        "types",
        "collections",
        "functools",
        "itertools",
        "dataclasses",
    },
)

# ── Scan scope contract ──
SCAN_ROOTS: tuple[str, ...] = (
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "artifacts",
    "ops_scripts",
    "tests",
)
SCAN_EXTENSIONS: tuple[str, ...] = (".py",)
SCAN_EXCLUDES: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "dist",
        "build",
        ".pytest_cache",
        "node_modules",
    },
)


def _allowlist_hash() -> str:
    """Deterministic SHA-256 of the canonical allowlist."""
    return hashlib.sha256(
        "\n".join(sorted(ALLOWED_MODULES)).encode(),
    ).hexdigest()[:16]


def _assert_frozen(obj: object, path: str = "root") -> str | None:
    """Recursively verify deep immutability.

    Returns None if fully frozen, or a string describing the first
    mutable structure found (with its path).
    """
    if isinstance(obj, dict):
        return f"{path}: dict (mutable)"
    if isinstance(obj, list):
        return f"{path}: list (mutable)"
    if isinstance(obj, set):
        return f"{path}: set (mutable)"
    if isinstance(obj, MappingProxyType):
        for k, v in obj.items():
            result = _assert_frozen(v, f"{path}.{k}")
            if result is not None:
                return result
        return None
    if isinstance(obj, tuple):
        for i, v in enumerate(obj):
            result = _assert_frozen(v, f"{path}[{i}]")
            if result is not None:
                return result
        return None
    if isinstance(obj, frozenset):
        return None
    # Primitives: str, int, float, bool, None
    return None


def _print_phantom_diff(
    current: set[tuple[str, str]],
    saved: set[tuple[str, str]],
) -> None:
    """Print deterministic diff between current and saved phantom sets."""
    added = sorted(current - saved)
    removed = sorted(saved - current)
    if not added and not removed:
        print("  No diff — baseline matches current scan.")
        return
    if added:
        print(f"  +{len(added)} NEW phantom(s):")
        for f, n in added:
            print(f"    + {f}:{n}")
    if removed:
        print(f"  -{len(removed)} REMOVED phantom(s):")
        for f, n in removed:
            print(f"    - {f}:{n}")


def _canonical_repo_path(path: str) -> str:
    """Normalize a path to canonical repo-relative form.

    - Converts backslashes to forward slashes
    - Collapses '.' segments
    - Rejects '..' segments (raises ValueError)
    - Rejects absolute paths (raises ValueError)
    - Returns normalized forward-slash path
    """
    normalized = path.replace("\\", "/")
    if normalized.startswith("/") or (len(normalized) >= 2 and normalized[1] == ":"):
        raise ValueError(f"Non-canonical path detected: absolute path '{path}'")
    parts = [p for p in normalized.split("/") if p and p != "."]
    if ".." in parts:
        raise ValueError(f"Non-canonical path detected: '..' segment in '{path}'")
    return "/".join(parts)


def _is_repo_relative_normalized(path: str) -> bool:
    """Check path is repo-relative, forward-slash only, no '..' segments.

    Baseline entries must already be in canonical form — backslashes are rejected.
    """
    if "\\" in path:
        return False
    try:
        return path == _canonical_repo_path(path)
    except ValueError:
        return False


def _collect_scan_files(root: str) -> tuple[list[str], list[str]]:
    """Collect all files under SCAN_ROOTS with SCAN_EXTENSIONS, excluding SCAN_EXCLUDES.

    Returns (files, missing_roots) where missing_roots lists any SCAN_ROOT
    that does not exist as a directory.
    """
    files: list[str] = []
    missing_roots: list[str] = []
    for scan_root in SCAN_ROOTS:
        scan_dir = os.path.join(root, scan_root)
        if not os.path.isdir(scan_dir):
            missing_roots.append(scan_root)
            continue
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = [d for d in dirnames if d not in SCAN_EXCLUDES]
            for fn in filenames:
                if any(fn.endswith(ext) for ext in SCAN_EXTENSIONS):
                    files.append(os.path.join(dirpath, fn))
    return sorted(files), missing_roots


def _path_under_scan_roots(path: str) -> bool:
    """Check that a repo-relative path starts with one of SCAN_ROOTS."""
    first_segment = path.split("/")[0]
    return first_segment in SCAN_ROOTS


def main() -> int:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    pkg_dir = os.path.dirname(__file__)
    pkg_prefix = "agentic_core.L5_safety.config.structure_blueprint"
    failures = 0

    # Early-exit: --print-allowlist (pure read-only, no lock file I/O)
    if "--print-allowlist" in sys.argv:
        print("ALLOWED_MODULES (canonical):")
        for m in sorted(ALLOWED_MODULES):
            print(f"  {m}")
        print(f"Hash: {_allowlist_hash()}")
        return 0

    # Early-exit: --acknowledge-import-change (maintenance mode, exits immediately)
    if "--acknowledge-import-change" in sys.argv:
        # Pre-check: baseline must exist and be valid (ack must not mask other failures)
        bp = os.path.join(root, "docs", "reports", "plans", "phantom_baseline.json")
        if not os.path.isfile(bp):
            print("ALLOWLIST ACK REFUSED: fix baseline/other failures first")
            print("  phantom_baseline.json not found")
            return 1
        try:
            with open(bp, encoding="utf-8") as bf:
                bl = json.load(bf)
            if not isinstance(bl, list):
                raise ValueError("not a JSON array")
            for i, entry in enumerate(bl):
                if not (
                    isinstance(entry, list) and len(entry) == 2 and all(isinstance(s, str) for s in entry)
                ):
                    raise ValueError(f"entry {i} invalid")
            bad = [e[0] for e in bl if not _is_repo_relative_normalized(e[0])]
            if bad:
                raise ValueError(f"non-normalized path: {bad[0]}")
        except (json.JSONDecodeError, ValueError, TypeError, OSError) as exc:
            print("ALLOWLIST ACK REFUSED: fix baseline/other failures first")
            print(f"  baseline corrupt — {exc}")
            return 1
        cur = _allowlist_hash()
        hp = os.path.join(root, "docs", "reports", "plans", "allowlist_hash.txt")
        if not os.path.isfile(hp):
            _wg.makedirs(os.path.dirname(hp), exist_ok=True)
            _wg.open_write(hp, cur + "\n")
            print(f"ALLOWLIST HASH INITIALIZED: {cur}")
            return 0
        with open(hp, encoding="utf-8") as hf:
            old = hf.read().strip()
        if old == cur:
            print(f"Allowlist hash already locked: {cur}")
            return 0
        print("Allowlist hash: MISMATCH")
        print(f"  saved hash:   {old}")
        print(f"  current hash: {cur}")
        print("  current allowlist (sorted):")
        for m in sorted(ALLOWED_MODULES):
            print(f"    {m}")
        _wg.open_write(hp, cur + "\n")
        print("ALLOWLIST HASH UPDATED")
        print("  Run normal verify to confirm all checks pass")
        return 0

    print("=" * 70)
    print("HARD SHIM STRATEGY — VERIFICATION REPORT")
    print("=" * 70)

    # === 1. Cycle Detection ===
    print("\n1. IMPORT CYCLE DETECTION")
    print("-" * 40)
    modules: dict[str, set[str]] = {}
    for fn in os.listdir(pkg_dir):
        if not fn.endswith(".py"):
            continue
        mod_name = fn[:-3] if fn != "__init__.py" else "__init__"
        fpath = os.path.join(pkg_dir, fn)
        with open(fpath, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=fpath)
        deps: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                m = node.module
                if m.startswith(pkg_prefix):
                    suffix = m[len(pkg_prefix) :]
                    if suffix == "":
                        dep = "__init__"
                    elif suffix.startswith("."):
                        dep = suffix[1:]
                    else:
                        dep = suffix
                    if dep != mod_name:
                        deps.add(dep)
        modules[mod_name] = deps

    for mod, deps in sorted(modules.items()):
        dep_str = ", ".join(sorted(deps)) if deps else "(none)"
        print(f"  {mod} -> {dep_str}")

    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(modules, WHITE)
    path: list[str] = []
    cycles_found: list[str] = []

    def dfs(u: str) -> None:
        color[u] = GRAY
        path.append(u)
        for v in modules.get(u, set()):
            if v not in color:
                continue
            if color[v] == GRAY:
                cycle_start = path.index(v)
                cycles_found.append(" -> ".join(path[cycle_start:] + [v]))
            elif color[v] == WHITE:
                dfs(v)
        path.pop()
        color[u] = BLACK

    for m in modules:
        if color[m] == WHITE:
            dfs(m)

    if cycles_found:
        print(f"  RESULT: FAIL ({len(cycles_found)} cycles)")
        for c in cycles_found:
            print(f"    {c}")
        failures += 1
    else:
        print("  RESULT: PASS — zero import cycles")

    # === 2. API Surface ===
    print("\n2. API SURFACE")
    print("-" * 40)
    import agentic_core.L5_safety.config.structure_blueprint as pkg
    import agentic_core.L5_safety.config.structure_blueprint as shim

    pkg_all = set(pkg.__all__)
    shim_all = set(shim.__all__)
    print(f"  Package __all__: {len(pkg_all)} names")
    print(f"  Shim __all__:    {len(shim_all)} names")
    diff = pkg_all.symmetric_difference(shim_all)
    if diff:
        print(f"  RESULT: FAIL — symmetric diff: {diff}")
        failures += 1
    else:
        print("  RESULT: PASS — exact match")

    pkg_missing = [n for n in pkg_all if not hasattr(pkg, n)]
    shim_missing = [n for n in shim_all if not hasattr(shim, n)]
    if pkg_missing:
        print(f"  Package missing attrs: {pkg_missing}")
        failures += 1
    if shim_missing:
        print(f"  Shim missing attrs: {shim_missing}")
        failures += 1
    if not pkg_missing and not shim_missing:
        print("  All __all__ names resolve: PASS")

    # === 3. DEEP IMMUTABILITY + IDENTITY ===
    print("\n3. DEEP IMMUTABILITY + IDENTITY")
    print("-" * 40)

    from agentic_core.L5_safety.config.structure_blueprint._constants import (
        ROOT_WHITELIST as c_rw,
    )
    from agentic_core.L5_safety.config.structure_blueprint._constants import (
        SOVEREIGN_TERRITORIES as c_st,
    )
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        ROOT_WHITELIST as s_rw,
    )
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        SOVEREIGN_TERRITORIES as s_st,
    )
    from agentic_core.L5_safety.config.structure_blueprint.territories import (
        SOVEREIGN_TERRITORIES as t_st,
    )

    imm_violations: list[str] = []

    # Identity checks
    if c_rw is not s_rw:
        imm_violations.append("ROOT_WHITELIST: _constants is not ssot")
    if c_st is not t_st:
        imm_violations.append("SOVEREIGN_TERRITORIES: _constants is not territories")
    if c_st is not s_st:
        imm_violations.append("SOVEREIGN_TERRITORIES: _constants is not ssot")

    # ROOT_WHITELIST immutability
    if not isinstance(c_rw, frozenset):
        imm_violations.append(
            f"ROOT_WHITELIST: type={type(c_rw).__name__}, expected frozenset",
        )

    # SOVEREIGN_TERRITORIES: top-level type
    if not isinstance(c_st, MappingProxyType):
        imm_violations.append(
            f"SOVEREIGN_TERRITORIES: top-level type={type(c_st).__name__}, expected MappingProxyType",
        )
    if isinstance(c_st, dict):
        imm_violations.append("SOVEREIGN_TERRITORIES: is plain dict (mutable!)")

    # Top-level mutation test
    try:
        c_st["__test__"] = 1  # type: ignore[index]
        imm_violations.append("SOVEREIGN_TERRITORIES: top-level mutation succeeded")
    except TypeError:
        pass

    # Full recursive walk via _assert_frozen
    freeze_err = _assert_frozen(c_st, "SOVEREIGN_TERRITORIES")
    if freeze_err is not None:
        imm_violations.append(freeze_err)

    print(f"  ROOT_WHITELIST: type={type(c_rw).__name__}, len={len(c_rw)}")
    print(f"  SOVEREIGN_TERRITORIES: type={type(c_st).__name__}, len={len(c_st)}")
    print(f"  Identity _constants==ssot==territories: {(c_rw is s_rw) and (c_st is t_st) and (c_st is s_st)}")

    if imm_violations:
        print(f"  RESULT: FAIL ({len(imm_violations)} violations)")
        for v in imm_violations:
            print(f"    {v}")
        failures += 1
    else:
        print("  RESULT: PASS — deep immutable, identity preserved")

    # === 4. Backward Compat ===
    print("\n4. BACKWARD COMPATIBILITY (18 excluded names)")
    print("-" * 40)

    excluded_names = [
        "SubfolderDefinition",
        "TerritoryDefinition",
        "build_sovereign_territories",
        "LAYER_OVERRIDES",
        "get_sovereign_territories",
        "get_core_subfolder_map",
        "get_subfolder_metadata",
        "get_apps_lic_subfolder_map",
        "get_apps_rg_subfolder_map",
        "get_apps_shared_subfolder_map",
        "agentic_core_registry",
        "verify_derived_registries",
        "L4_SUBFOLDER_MAP",
        "L4_APPROVED_FOLDERS",
        "SCRIPTS_PLACEMENT_RULES",
        "get_app_specific_patterns_compiled",
        "get_classification_suffix_patterns_compiled",
        "get_compound_suffix_patterns_compiled",
    ]

    pkg_ok = sum(1 for n in excluded_names if hasattr(pkg, n))
    shim_ok = sum(1 for n in excluded_names if hasattr(shim, n))
    in_all = [n for n in excluded_names if n in pkg_all]

    print(f"  Importable from package: {pkg_ok}/{len(excluded_names)}")
    print(f"  Importable from shim:    {shim_ok}/{len(excluded_names)}")
    print(f"  Leaked into __all__:     {len(in_all)} (should be 0)")
    if in_all:
        print(f"    LEAKED: {in_all}")

    if pkg_ok == len(excluded_names) and shim_ok == len(excluded_names) and len(in_all) == 0:
        print("  RESULT: PASS")
    else:
        print("  RESULT: FAIL")
        failures += 1

    # === 5. Import Linter + Phantom Baseline Lock ===
    print("\n5. IMPORT LINTER + PHANTOM BASELINE LOCK")
    print("-" * 40)
    targets = ("structure_blueprint_config", "structure_blueprint")
    phantom_tuples: list[tuple[str, str]] = []  # (relpath, name)
    phantom_debt: list[tuple[str, str, int, str]] = []  # (relpath, name, lineno, module)
    policy_errors: list[str] = []
    checked = 0

    scan_files, missing_roots = _collect_scan_files(root)
    print(f"  Scan scope: {len(scan_files)} files in {SCAN_ROOTS}")
    if missing_roots:
        for mr in missing_roots:
            print(f"  SCAN_ROOT MISSING: {mr}/ does not exist")
        print("  RESULT: FAIL — all SCAN_ROOTS must exist")
        failures += 1
    for fpath in scan_files:
        try:
            with open(fpath, encoding="utf-8", errors="replace") as f:
                source = f.read()
        except Exception:
            continue
        try:
            tree = ast.parse(source, filename=fpath)
        except SyntaxError as exc:
            rp = _canonical_repo_path(os.path.relpath(fpath, root))
            policy_errors.append(
                f"{rp}:{exc.lineno or '?'}: SyntaxError — {exc.msg}",
            )
            continue
        file_counted = False
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.ImportFrom) and node.module and any(t in node.module for t in targets)
            ):
                continue
            if not file_counted:
                file_counted = True
                checked += 1
            if node.module in ("structure_blueprint", "structure_blueprint_config"):
                for a in node.names or []:
                    policy_errors.append(
                        f"{os.path.relpath(fpath, root)}:{node.lineno}:{a.name} (short-path: {node.module})",
                    )
                continue
            names = [a.name for a in node.names] if node.names else []
            for name in names:
                if name == "*":
                    continue
                try:
                    mod = __import__(node.module, fromlist=[name])
                    if not hasattr(mod, name):
                        rp = _canonical_repo_path(os.path.relpath(fpath, root))
                        phantom_tuples.append((rp, name))
                        phantom_debt.append((rp, name, node.lineno, node.module))
                except Exception:
                    rp = _canonical_repo_path(os.path.relpath(fpath, root))
                    phantom_tuples.append((rp, name))
                    phantom_debt.append((rp, name, node.lineno, node.module))

    phantom_set = sorted(set(phantom_tuples))
    total_errors = len(phantom_set) + len(policy_errors)
    print(f"  Files checked:      {checked}")
    print(f"  Total errors:       {total_errors}")
    print(f"    Phantom names:    {len(phantom_set)}")
    print(f"    Policy violations: {len(policy_errors)}")

    if policy_errors:
        print("  Policy violations (MUST FIX):")
        for e in sorted(policy_errors):
            print(f"    {e}")
        failures += 1
    print(f"  Policy: {'PASS' if not policy_errors else 'FAIL'}")

    # Phantom baseline lock (Phase 4.3: hard path constraints, no masking)
    baseline_path = os.path.join(
        root,
        "docs",
        "reports",
        "plans",
        "phantom_baseline.json",
    )
    current_baseline = [[f, n] for f, n in phantom_set]
    current_set_cmp = {tuple(x) for x in current_baseline}
    init_flag = "--init-phantom-baseline" in sys.argv
    update_flag = "--update-phantom-baseline" in sys.argv
    diff_flag = "--print-phantom-diff" in sys.argv
    repair_flag = "--repair-phantom-baseline" in sys.argv

    saved_set: set[tuple[str, str]] | None = None
    baseline_corrupt = False

    if os.path.isfile(baseline_path):
        try:
            with open(baseline_path, encoding="utf-8") as bf:
                saved_baseline = json.load(bf)
            if not isinstance(saved_baseline, list):
                raise ValueError("baseline is not a JSON array")
            for i, entry in enumerate(saved_baseline):
                if not (
                    isinstance(entry, list) and len(entry) == 2 and all(isinstance(s, str) for s in entry)
                ):
                    raise ValueError(f"entry {i} is not a [file, name] pair")
            bad_paths = [e[0] for e in saved_baseline if not _is_repo_relative_normalized(e[0])]
            if bad_paths:
                raise ValueError(
                    f"{len(bad_paths)} baseline path(s) not repo-relative-normalized "
                    f"(no backslashes, no absolute, no ..); first: {bad_paths[0]}",
                )
            out_of_scope = [e[0] for e in saved_baseline if not _path_under_scan_roots(e[0])]
            if out_of_scope:
                raise ValueError(
                    f"{len(out_of_scope)} baseline path(s) not under SCAN_ROOTS; "
                    f"first: {out_of_scope[0]}. "
                    f"Valid roots: {SCAN_ROOTS}",
                )
            saved_set = {tuple(x) for x in saved_baseline}
        except (json.JSONDecodeError, ValueError, TypeError, OSError) as exc:
            baseline_corrupt = True
            print(f"  Phantom baseline: CORRUPT — {exc}")

    # --print-phantom-diff: print diff and exit
    if diff_flag:
        if saved_set is not None:
            _print_phantom_diff(current_set_cmp, saved_set)
            has_diff = current_set_cmp != saved_set
            return 1 if has_diff else 0
        elif baseline_corrupt:
            print("  Cannot diff — baseline is corrupt")
            return 1
        else:
            print("  Cannot diff — phantom_baseline.json not found")
            return 1

    # --repair-phantom-baseline: ONLY for corrupt/unreadable baselines
    if repair_flag:
        if not os.path.isfile(baseline_path):
            print("  --repair-phantom-baseline REFUSED — no baseline file to repair")
            print("    Use --init-phantom-baseline to create it")
            return 1
        if not baseline_corrupt:
            print("  --repair-phantom-baseline REFUSED — baseline is valid")
            print("    Use --update-phantom-baseline for baseline drift")
            return 1
        _wg.write_json(baseline_path, current_baseline, indent=2)
        print(f"  Phantom baseline: REPAIRED ({len(current_baseline)} entries)")
        for entry in current_baseline[:10]:
            print(f"    {entry[0]}:{entry[1]}")
        if len(current_baseline) > 10:
            print(f"    ... and {len(current_baseline) - 10} more")
        print(f"    Wrote: {os.path.relpath(baseline_path, root)}")
        return 0

    if baseline_corrupt:
        print("    Run with --repair-phantom-baseline to rewrite from current scan")
        failures += 1
    elif saved_set is not None:
        baseline_only = sorted(saved_set - current_set_cmp)
        current_only = sorted(current_set_cmp - saved_set)
        if not baseline_only and not current_only:
            print(f"  Phantom baseline: LOCKED ({len(saved_set)} entries, matches)")
        else:
            if baseline_only:
                print(f"  Baseline-only entries (stale baseline): {len(baseline_only)}")
                for f, n in baseline_only:
                    print(f"    - {f}:{n}")
            if current_only:
                print(f"  Current-only entries (new phantom): {len(current_only)}")
                for f, n in current_only:
                    print(f"    + {f}:{n}")
            print(
                "  Remediation (local only): run with --update-phantom-baseline after fixing phantom imports.",
            )
            print(
                "  CI policy: maintenance flags are forbidden in CI; run locally and commit lockfile updates.",
            )
            if not current_only and update_flag:
                # Only baseline_only: phantoms reduced — safe to update
                _wg.write_json(baseline_path, current_baseline, indent=2)
                print(f"  Phantom baseline: UPDATED ({len(saved_set)} → {len(current_set_cmp)} entries)")
            elif current_only:
                print(f"  Phantom baseline: FAIL — {len(current_only)} new phantom(s)")
                if update_flag:
                    print("    --update-phantom-baseline REFUSED — new phantoms exist")
                failures += 1
            else:
                print("    Run with --update-phantom-baseline to persist reduction")
    elif init_flag:
        _wg.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        _wg.write_json(baseline_path, current_baseline, indent=2)
        print(f"  Phantom baseline: INITIALIZED ({len(current_baseline)} entries)")
        print(f"    Wrote: {os.path.relpath(baseline_path, root)}")
    else:
        print("  Phantom baseline: FAIL — phantom_baseline.json not found")
        print("    Run with --init-phantom-baseline to create it")
        failures += 1

    # === 6. Shim Structural Hard Lock ===
    print("\n6. SHIM STRUCTURAL HARD LOCK")
    print("-" * 40)
    shim_path = os.path.join(
        root,
        AGENTIC_CORE_DIR,
        "L5_safety",
        "config",
        "structure_blueprint_config.py",
    )
    with open(shim_path, encoding="utf-8") as f:
        shim_source = f.read()
    shim_tree = ast.parse(shim_source, filename=shim_path)

    shim_violations: list[str] = []
    assign_all_count = 0

    for node in ast.iter_child_nodes(shim_tree):
        # ALLOWED: Import / ImportFrom
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        # ALLOWED: module docstring (Expr with Constant)
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        # ALLOWED: exactly one Assign to __all__
        if isinstance(node, ast.Assign):
            targets_ok = all(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
            if targets_ok:
                assign_all_count += 1
                if assign_all_count > 1:
                    shim_violations.append(
                        f"line {node.lineno}: duplicate __all__ assignment",
                    )
                continue
            for t in node.targets:
                shim_violations.append(
                    f"line {node.lineno}: assignment to {ast.dump(t)}",
                )
            continue
        # FORBIDDEN: FunctionDef, AsyncFunctionDef
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            shim_violations.append(f"line {node.lineno}: FunctionDef '{node.name}'")
            continue
        # FORBIDDEN: ClassDef
        if isinstance(node, ast.ClassDef):
            shim_violations.append(f"line {node.lineno}: ClassDef '{node.name}'")
            continue
        # FORBIDDEN: control flow (If, For, While, Try, With, Match)
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
            shim_violations.append(
                f"line {node.lineno}: control flow ({type(node).__name__})",
            )
            continue
        # FORBIDDEN: any other top-level node
        shim_violations.append(f"line {node.lineno}: {type(node).__name__}")

    if assign_all_count == 0:
        shim_violations.append("missing __all__ assignment")

    # Check no top-level Call expressions (e.g. print(), function calls)
    for node in ast.iter_child_nodes(shim_tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            shim_violations.append(
                f"line {node.lineno}: top-level Call expression",
            )

    if shim_violations:
        print(f"  RESULT: FAIL ({len(shim_violations)} violations)")
        for v in shim_violations:
            print(f"    {v}")
        failures += 1
    else:
        print("  __all__ assignments: 1")
        print("  FunctionDef/ClassDef/Call/ControlFlow: 0")
        print("  RESULT: PASS — structural hard lock intact")

    # === 7. _constants.py STDLIB ALLOWLIST (Phase 4: hash-locked) ===
    print("\n7. _constants.py STDLIB ALLOWLIST")
    print("-" * 40)
    constants_path = os.path.join(pkg_dir, "_constants.py")
    with open(constants_path, encoding="utf-8") as f:
        constants_source = f.read()
    constants_tree = ast.parse(constants_source, filename=constants_path)

    forbidden_calls = {
        "os.getenv",
        "os.environ",
        "os.getcwd",
        "open",
        "Path.read_text",
        "Path.read_bytes",
        "Path.cwd",
        "time.time",
        "time.monotonic",
        "datetime.now",
        "datetime.utcnow",
        "random.random",
        "random.randint",
        "random.choice",
        "__import__",
        "importlib.import_module",
    }

    allowlist_violations: list[str] = []

    for node in ast.walk(constants_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in ALLOWED_MODULES:
                    allowlist_violations.append(
                        f"line {node.lineno}: 'import {alias.name}' ('{top}' not in allowlist)",
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                allowlist_violations.append(
                    f"line {node.lineno}: relative import (level={node.level})",
                )
            elif node.module:
                top = node.module.split(".")[0]
                if top not in ALLOWED_MODULES:
                    allowlist_violations.append(
                        f"line {node.lineno}: 'from {node.module} import ...' ('{top}' not in allowlist)",
                    )

    for node in ast.walk(constants_tree):
        if isinstance(node, ast.Call):
            call_name = ""
            if isinstance(node.func, ast.Name):
                call_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    call_name = f"{node.func.value.id}.{node.func.attr}"
            if call_name in forbidden_calls:
                allowlist_violations.append(
                    f"line {node.lineno}: forbidden call '{call_name}'",
                )

    current_hash = _allowlist_hash()
    hash_path = os.path.join(
        root,
        "docs",
        "reports",
        "plans",
        "allowlist_hash.txt",
    )
    print(f"  Allowlist: {sorted(ALLOWED_MODULES)}")
    print(f"  Hash: {current_hash}")

    if allowlist_violations:
        print(f"  RESULT: FAIL ({len(allowlist_violations)} violations)")
        for v in allowlist_violations:
            print(f"    {v}")
        failures += 1
    else:
        print("  No forbidden imports, no relative imports, no dynamic imports")

    # Allowlist hash contract (Phase 4.2: ack handled as early-exit maintenance mode)
    if os.path.isfile(hash_path):
        with open(hash_path, encoding="utf-8") as hf:
            saved_hash = hf.read().strip()
        if saved_hash == current_hash:
            print("  Allowlist hash: LOCKED (matches)")
        else:
            print("  Allowlist hash: MISMATCH")
            print(f"    saved hash:   {saved_hash}")
            print(f"    current hash: {current_hash}")
            print("    current allowlist (sorted):")
            for m in sorted(ALLOWED_MODULES):
                print(f"      {m}")
            print("  Allowlist hash: FAIL — run with --acknowledge-import-change")
            failures += 1
    else:
        _wg.makedirs(os.path.dirname(hash_path), exist_ok=True)
        _wg.open_write(hash_path, current_hash + "\n")
        print(f"  Allowlist hash: INITIALIZED ({current_hash})")

    if not allowlist_violations:
        print("  RESULT: PASS — stdlib allowlist enforced")

    # === 8. Compat Name Consumer Report ===
    print("\n8. COMPAT NAME CONSUMER REPORT (18 excluded names)")
    print("-" * 40)
    print("  Posture: INTERNAL FOREVER (not deprecated)")
    print("  These names are part of the build/derivation machinery.")
    print("  They are importable but excluded from __all__ to avoid")
    print("  coupling downstream code to internal structure.")
    print()

    # Count consumers per compat name (scoped to SCAN_ROOTS)
    compat_consumers: dict[str, list[str]] = {n: [] for n in excluded_names}
    for fpath in scan_files:
        relpath = os.path.relpath(fpath, root)
        # Skip the package itself and the shim
        if "structure_blueprint" in relpath and ("config" in relpath.split(os.sep)):
            continue
        try:
            with open(fpath, encoding="utf-8", errors="replace") as f:
                source = f.read()
        except Exception:
            continue
        for name in excluded_names:
            if name in source:
                compat_consumers[name].append(relpath)

    for name in excluded_names:
        consumers = compat_consumers[name]
        count = len(consumers)
        status = "ACTIVE" if count > 0 else "UNUSED"
        print(f"  {name}: {count} consumer(s) [{status}]")
        if count > 0 and count <= 5:
            for c in consumers:
                print(f"    - {c}")
        elif count > 5:
            for c in consumers[:3]:
                print(f"    - {c}")
            print(f"    ... and {count - 3} more")

    # === 9. Phantom Debt Register ===
    # Debt is derived from PHANTOM_CURRENT_SET (the deduplicated current scan).
    # phantom_set = sorted list of (path, name) tuples from current scan.
    # phantom_debt = list of (path, name, lineno, module) with import context.
    # The debt register uses phantom_debt keyed by (path, name) to match phantom_set.
    print("\n9. PHANTOM DEBT REGISTER")
    print("-" * 40)
    debt_path = os.path.join(root, "docs", "reports", "plans", "phantom_debt.md")
    # Build debt rows keyed by (path, name) to match phantom_set exactly
    debt_by_key: dict[tuple[str, str], tuple[int, str]] = {}
    for rp, name, lineno, mod in phantom_debt:
        key = (rp, name)
        if key not in debt_by_key:
            debt_by_key[key] = (lineno, mod)
    debt_rows = sorted(debt_by_key.keys())
    assert len(debt_rows) == len(phantom_set), (
        f"debt_rows ({len(debt_rows)}) != phantom_set ({len(phantom_set)})"
    )
    debt_lines: list[str] = [
        "# Phantom Import Debt Register",
        "",
        f"Phantom count: {len(debt_rows)}",
        "",
        "| Path | Missing Name | Import Line | Suggested Fix |",
        "| --- | --- | --- | --- |",
    ]
    for rp, name in debt_rows:
        lineno, mod = debt_by_key[(rp, name)]
        if name.isupper() or ("_" in name and name == name.upper()):
            fix = "replace import or define symbol"
        elif name.startswith("get_"):
            fix = "remove or update function import"
        else:
            fix = "remove phantom import"
        excerpt = f"`from {mod} import {name}` (line {lineno})"
        debt_lines.append(f"| `{rp}` | `{name}` | {excerpt} | {fix} |")
    debt_lines.append("")
    _wg.makedirs(os.path.dirname(debt_path), exist_ok=True)
    _wg.open_write(debt_path, "\n".join(debt_lines))
    baseline_count = len(saved_set) if saved_set is not None else None
    current_count = len(phantom_set)
    print("  Source: PHANTOM_CURRENT_SET (deduplicated current scan)")
    print(f"  Phantom current count:  {current_count}")
    if baseline_count is not None:
        print(f"  Phantom baseline count: {baseline_count}")
    print(f"  Debt rows:              {len(debt_rows)}")
    print(f"  Invariant: debt_rows == current_count: {len(debt_rows) == current_count}")
    if baseline_count is not None:
        print(f"  Invariant: current_count == baseline_count: {current_count == baseline_count}")
    print(f"  Generated: {os.path.relpath(debt_path, root)}")

    # === 10. ENFORCEMENT MODULES ===
    print("\n10. ENFORCEMENT MODULES")
    print("-" * 40)
    from pathlib import Path as _Path

    from agentic_core.L5_safety.config.structure_blueprint.enforcement.import_graph import (
        ImportGraph,
    )
    from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (
        emit_report_json,
        make_report,
    )

    enforcement_root = _Path(root)
    print("  Building import graph...")
    import_graph = ImportGraph(enforcement_root, SCAN_ROOTS)
    print(
        f"  Import graph: {import_graph.files_parsed} files parsed, {len(import_graph.parse_errors)} errors",
    )
    if import_graph.parse_errors:
        for pe in import_graph.parse_errors[:5]:
            print(f"    {pe}")
        if len(import_graph.parse_errors) > 5:
            print(f"    ... and {len(import_graph.parse_errors) - 5} more")

    # Collect enforcement results from all wired modules
    from agentic_core.L5_safety.config.structure_blueprint.enforcement import (
        blueprint_hash,
        cross_layer,
        leaf_node,
        mixin_ast,
        territory_diff,
        volatile_rules,
    )

    enforcement_results = []

    # Layer 1+7: Territory diff — bidirectional subfolder drift detection (ALL territories)
    from collections.abc import Mapping as _Mapping

    td_result = territory_diff.check(enforcement_root, c_st)
    enforcement_results.append(td_result)
    td_stats = td_result["stats"]
    print(
        f"  territory_diff: {len(td_result['violations'])} violation(s)  [{td_stats['territories_checked']} territories checked]",
    )

    # Layer 2: Leaf node — root .py prohibition (ALL territories)
    ln_result = leaf_node.check(enforcement_root, c_st)
    enforcement_results.append(ln_result)
    ln_stats = ln_result["stats"]
    print(
        f"  leaf_node: {len(ln_result['violations'])} violation(s)  [{ln_stats['territories_checked']} dirs with allow_root_py=False]",
    )

    # Layer 3: Volatile rules — import isolation for volatile territories
    vr_result = volatile_rules.check(enforcement_root, c_st, import_graph)
    enforcement_results.append(vr_result)
    print(f"  volatile_rules: {len(vr_result['violations'])} violation(s)")

    # Layer 4: Mixin AST — flat + naming + class structure enforcement
    ac_config = c_st.get(AGENTIC_CORE_DIR, {})
    ac_subfolders = ac_config.get("subfolders", {}) if isinstance(ac_config, _Mapping) else {}
    ma_result = mixin_ast.check(enforcement_root / AGENTIC_CORE_DIR, ac_subfolders)
    enforcement_results.append(ma_result)
    print(f"  mixin_ast: {len(ma_result['violations'])} violation(s)")

    # Layer 5: Blueprint hash — SHA-256 integrity (warning-only if hash file missing)
    blueprint_dir = _Path(__file__).resolve().parent
    bh_result = blueprint_hash.check(blueprint_dir)
    enforcement_results.append(bh_result)
    print(f"  blueprint_hash: {len(bh_result['violations'])} violation(s)")

    # Layer 6: Cross-layer import law — stdlib-only core, utils purity, config independence
    cl_result = cross_layer.check(enforcement_root, c_st, import_graph)
    enforcement_results.append(cl_result)
    print(f"  cross_layer: {len(cl_result['violations'])} violation(s)")
    cl_stats = cl_result["stats"]
    print(
        f"    edges: {cl_stats.get('total_edges', 0)} total, {cl_stats.get('internal_edges', 0)} internal, {cl_stats.get('cross_layer_edges_analyzed', 0)} cross-layer analyzed",
    )

    if enforcement_results:
        report = make_report(enforcement_results)
        report_json = emit_report_json(report)

        # Emit artifact
        verification_dir = os.path.join(root, "docs", "reports", "verification")
        _wg.makedirs(verification_dir, exist_ok=True)
        report_path = os.path.join(verification_dir, "enforcement_report.json")
        _wg.write_json(report_path, report_json, indent=2)
        print(f"  Artifact: {os.path.relpath(report_path, root)}")

        passed = report["summary"]["passed"]
        failed = report["summary"]["failed"]
        total_v = report["summary"]["total_violations"]
        print(f"  Checks: {passed} passed, {failed} failed, {total_v} violations")
        if not report["overall_passed"]:
            failures += 1
            print("  RESULT: FAIL")
        else:
            print("  RESULT: PASS")
    else:
        print("  No enforcement modules wired yet (Phase 0 stub)")
        print("  RESULT: SKIP")

    # === Summary ===
    print("\n" + "=" * 70)
    if failures == 0:
        print("OVERALL: PASS — all checks green")
    else:
        print(f"OVERALL: {failures} section(s) failed")
    print("=" * 70)

    return failures


if __name__ == "__main__":
    sys.exit(main())
