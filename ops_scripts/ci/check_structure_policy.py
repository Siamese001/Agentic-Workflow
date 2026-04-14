"""
Structure Policy CI Gate — YAML-only enforcement.

Reads config/structure_blueprint/structure_policy.yaml and validates the
repository directory structure.  Returns exit code 0 on pass, 1 on failure.

Replaces ~5,000 lines of Python enforcement in the old structure_blueprint
package (_verify.py, _simulate_verify.py, sovereign_kernel.py, governance.py,
enforcement/).

Usage:
    python ops_scripts/ci/check_structure_policy.py [--verbose]
"""

from __future__ import annotations

import fnmatch
import sys
from pathlib import Path
from typing import Any
from tqdm import tqdm

_ROOT = Path(__file__).resolve().parents[2]

try:
    import yaml
except ImportError:
    sys.exit("[FATAL] PyYAML not installed — run: pip install pyyaml")


def _load_policy(policy_path: Path | None = None) -> dict[str, Any]:
    """Load and return the structure policy YAML."""
    if policy_path is None:
        policy_path = _ROOT / "config" / "structure_blueprint" / "structure_policy.yaml"
    with open(policy_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _check_root_dirs(policy: dict[str, Any], verbose: bool = False) -> list[str]:
    """Validate that only allowed directories exist at the repo root."""
    allowed = set(policy.get("root_directories", []))
    excluded = set(policy.get("excluded_directories", []))
    forbidden = set(policy.get("forbidden_root_directories", []))
    violations: list[str] = []

    for item in tqdm(sorted(_ROOT.iterdir()), desc="Processing", unit="item"):
        if not item.is_dir():
            continue
        name = item.name
        if name in excluded:
            continue
        if name in forbidden:
            violations.append(f"FORBIDDEN root dir: {name}/")
        elif name not in allowed and not name.startswith("apps_"):
            violations.append(f"UNKNOWN root dir: {name}/ (not in root_directories whitelist)")
        elif verbose:
            print(f"  OK  {name}/")

    return violations


def _check_root_files(policy: dict[str, Any], verbose: bool = False) -> list[str]:
    """Validate that root-level files match allowed patterns."""
    patterns = policy.get("root_file_patterns", [])
    violations: list[str] = []

    for item in sorted(_ROOT.iterdir()):
        if item.is_dir():
            continue
        name = item.name
        if any(fnmatch.fnmatch(name, p) for p in patterns):
            if verbose:
                print(f"  OK  {name}")
        else:
            violations.append(f"DISALLOWED root file: {name}")

    return violations


def _check_flat_dirs(policy: dict[str, Any], verbose: bool = False) -> list[str]:
    """Validate that flat directories contain no subdirectories."""
    flat_names = set(policy.get("flat_directories", []))
    excluded = set(policy.get("excluded_directories", []))
    violations: list[str] = []

    for flat_dir in tqdm(sorted(_ROOT.rglob("*")), desc="Processing", unit="item"):
        if not flat_dir.is_dir():
            continue
        if flat_dir.name not in flat_names:
            continue
        # Check if any of its ancestors are excluded
        if any(p.name in excluded for p in flat_dir.parents):
            continue
        has_violation = False
        for child in flat_dir.iterdir():
            if child.is_dir() and child.name not in excluded:
                has_violation = True
                violations.append(
                    f"FLAT violation: {child.relative_to(_ROOT)}/ "
                    f"(subdirectory inside flat dir '{flat_dir.name}/')"
                )
        if verbose and not has_violation:
            print(f"  OK  {flat_dir.relative_to(_ROOT)}/ (flat)")

    return violations


def _check_layer_structure(policy: dict[str, Any], verbose: bool = False) -> list[str]:
    """Validate agentic_core layer structure."""
    core = _ROOT / "agentic_core"
    if not core.is_dir():
        return ["agentic_core/ directory not found"]

    layer_roots = set(policy.get("layer_roots", []))
    violations: list[str] = []

    present_layers = {d.name for d in core.iterdir() if d.is_dir() and d.name.startswith("L")}
    missing = layer_roots - present_layers
    for m in sorted(missing):
        violations.append(f"MISSING layer root: agentic_core/{m}/")

    if verbose and not missing:
        print(f"  OK  all {len(layer_roots)} layer roots present")

    return violations


def _check_forbidden_root_dirs(policy: dict[str, Any], verbose: bool = False) -> list[str]:
    """Validate no forbidden directories exist at root."""
    forbidden = set(policy.get("forbidden_root_directories", []))
    violations: list[str] = []

    for name in sorted(forbidden):
        if (_ROOT / name).is_dir():
            violations.append(f"FORBIDDEN dir exists: {name}/ (must be removed or archived)")
        elif verbose:
            print(f"  OK  {name}/ not present")

    return violations


def main(verbose: bool = False) -> int:
    """Run all structure policy checks. Returns 0 on success, 1 on failure."""
    policy = _load_policy()

    all_violations: list[str] = []

    checks = [
        ("Root directories", _check_root_dirs),
        ("Root files", _check_root_files),
        ("Flat directories", _check_flat_dirs),
        ("Layer structure", _check_layer_structure),
        ("Forbidden directories", _check_forbidden_root_dirs),
    ]

    for label, check_fn in checks:
        if verbose:
            print(f"\n--- {label} ---")
        violations = check_fn(policy, verbose=verbose)
        all_violations.extend(violations)

    if all_violations:
        print(f"\n[FAIL] Structure policy: {len(all_violations)} violation(s)")
        for v in all_violations:
            print(f"  - {v}")
        return 1

    print("[PASS] Structure policy: all checks passed")
    return 0


if __name__ == "__main__":
    _verbose = "--verbose" in sys.argv or "-v" in sys.argv
    sys.exit(main(verbose=_verbose))
