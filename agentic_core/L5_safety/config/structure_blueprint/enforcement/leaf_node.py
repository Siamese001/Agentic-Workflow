"""
Leaf Node — Layer 2: Root .py prohibition for governed territories.

Territories with "allow_root_py": False must not contain .py files
in their root directory (excluding __init__.py).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (
    EnforcementResult,
    Violation,
    make_result,
)


def check(
    repo_root: Path,
    sovereign_territories: Mapping[str, Any],
) -> EnforcementResult:
    """Check ALL sovereign territories for Leaf Node Rule violations.

    Iterates every top-level territory and their nested subfolders.
    Any territory or subfolder with ``allow_root_py: False`` must not
    contain ``.py`` files in its root directory (excluding ``__init__.py``).
    """
    violations: list[Violation] = []
    stats = {
        "territories_checked": 0,
        "root_py_files_found": 0,
    }

    for territory_name, config in sovereign_territories.items():
        if not isinstance(config, Mapping):
            continue

        territory_path = repo_root / territory_name
        if not territory_path.is_dir():
            continue

        # Check top-level territory
        if config.get("allow_root_py") is False:
            _check_dir(territory_path, territory_name, violations, stats)

        # Check nested subfolders
        subfolders = config.get("subfolders")
        if isinstance(subfolders, Mapping):
            for sf_name, sf_config in subfolders.items():
                if not isinstance(sf_config, Mapping):
                    continue
                if sf_config.get("allow_root_py") is False:
                    sf_path = territory_path / sf_name
                    _check_dir(sf_path, f"{territory_name}/{sf_name}", violations, stats)

                # Also check second-level nested subfolders
                nested_sfs = sf_config.get("subfolders")
                if isinstance(nested_sfs, Mapping):
                    for nsf_name, nsf_config in nested_sfs.items():
                        if not isinstance(nsf_config, Mapping):
                            continue
                        if nsf_config.get("allow_root_py") is False:
                            nsf_path = territory_path / sf_name / nsf_name
                            _check_dir(
                                nsf_path,
                                f"{territory_name}/{sf_name}/{nsf_name}",
                                violations,
                                stats,
                            )

    return make_result("leaf_node", violations, stats)


def _check_dir(
    dir_path: Path,
    display_path: str,
    violations: list[Violation],
    stats: dict[str, int],
) -> None:
    """Scan a directory for root-level .py files (excluding __init__.py)."""
    if not dir_path.is_dir():
        return

    stats["territories_checked"] += 1

    try:
        for entry in os.scandir(dir_path):
            if entry.is_file() and entry.name.endswith(".py") and entry.name != "__init__.py":
                stats["root_py_files_found"] += 1
                violations.append(
                    Violation(
                        type="root_py_file",
                        path=f"{display_path}/{entry.name}",
                        severity="error",
                        detail=f"Python file '{entry.name}' found in root of '{display_path}' which has allow_root_py=False (Leaf Node Rule)",
                    ),
                )
    except OSError:
        pass
