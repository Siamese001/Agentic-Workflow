#!/usr/bin/env python3
"""R2 gate: YAML runtime-scanner mirrors ↔ path_constants.py frozensets.

Validates that the three YAML categories
    - sovereign_excluded_folders
    - global_excluded_dirs
    - discovery_excluded_territories
are byte-equal sets to the Python frozensets exported from
`agentic_core.L0_routing.config.path_constants`. Any drift fails the check.

Exit 0 on clean, 1 on drift.

Usage:
    python ops_scripts/ci/check_exclusion_consistency.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

YAML_PATH = REPO_ROOT / "config" / "excluded_paths.yaml"

CATEGORY_TO_CONSTANT = {
    "sovereign_excluded_folders": "SOVEREIGN_EXCLUDED_FOLDERS",
    "global_excluded_dirs": "GLOBAL_EXCLUDED_DIRS",
    "discovery_excluded_territories": "DISCOVERY_EXCLUDED_TERRITORIES",
}


def _load_yaml() -> dict:
    try:
        import yaml
    except ImportError:
        print("[exclusion_consistency] FAIL: PyYAML required (pip install pyyaml)", flush=True)
        sys.exit(2)
    if not YAML_PATH.exists():
        print(f"[exclusion_consistency] FAIL: {YAML_PATH} not found", flush=True)
        sys.exit(2)
    with YAML_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        print(f"[exclusion_consistency] FAIL: top-level YAML is not a mapping in {YAML_PATH}", flush=True)
        sys.exit(2)
    return data


def _load_python_constants() -> dict[str, frozenset[str]]:
    from agentic_core.L0_routing.config.path_constants import (
        DISCOVERY_EXCLUDED_TERRITORIES,
        GLOBAL_EXCLUDED_DIRS,
        SOVEREIGN_EXCLUDED_FOLDERS,
    )

    return {
        "SOVEREIGN_EXCLUDED_FOLDERS": SOVEREIGN_EXCLUDED_FOLDERS,
        "GLOBAL_EXCLUDED_DIRS": GLOBAL_EXCLUDED_DIRS,
        "DISCOVERY_EXCLUDED_TERRITORIES": DISCOVERY_EXCLUDED_TERRITORIES,
    }


def main() -> int:
    yaml_data = _load_yaml()
    py_consts = _load_python_constants()

    issues: list[str] = []

    for yaml_key, const_name in CATEGORY_TO_CONSTANT.items():
        yaml_entries_raw = yaml_data.get(yaml_key)
        if yaml_entries_raw is None:
            issues.append(f"YAML missing category '{yaml_key}' (mirror of path_constants.{const_name})")
            continue
        if not isinstance(yaml_entries_raw, list):
            issues.append(f"YAML category '{yaml_key}' must be a list, got {type(yaml_entries_raw).__name__}")
            continue
        yaml_set = frozenset(str(e) for e in yaml_entries_raw)
        py_set = py_consts[const_name]
        in_py_not_yaml = py_set - yaml_set
        in_yaml_not_py = yaml_set - py_set
        if in_py_not_yaml or in_yaml_not_py:
            msg = f"DRIFT: {yaml_key} vs path_constants.{const_name}"
            if in_py_not_yaml:
                msg += f"\n    in Python but not YAML: {sorted(in_py_not_yaml)}"
            if in_yaml_not_py:
                msg += f"\n    in YAML but not Python: {sorted(in_yaml_not_py)}"
            issues.append(msg)

    if issues:
        print("[exclusion_consistency] FAIL:", flush=True)
        for issue in issues:
            print(f"  - {issue}", flush=True)
        print(
            "\n  Fix: update EITHER config/excluded_paths.yaml OR "
            "agentic_core/L0_routing/config/path_constants.py so the Python "
            "frozensets and YAML mirror categories agree.",
            flush=True,
        )
        return 1

    n = sum(len(py_consts[c]) for c in py_consts)
    print(
        f"[exclusion_consistency] OK: {len(py_consts)} frozensets / {n} entries match YAML mirror.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
