"""
Territory Diff — Layers 1 + 7: Bidirectional territory auto-diff + strict subfolder enforcement.

Compares SOVEREIGN_TERRITORIES against filesystem reality for all governed territories.
Detects undeclared subfolders, missing required subfolders, and warns on missing optional ones.
"""

from __future__ import annotations

import json as _json
import os
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (
    EnforcementResult,
    Violation,
    make_result,
)

EXCLUDED_DIRS: frozenset[str] = frozenset(
    {"__pycache__", ".git", ".venv", "venv", "node_modules", ".nox", ".pytest_cache"},
)

_OPTIONAL_BASELINE_PATH = Path(__file__).resolve().parent / "missing_optional_baseline.json"


def _load_optional_baseline() -> int:
    """Load the missing-optional ceiling from the baseline file."""
    if not _OPTIONAL_BASELINE_PATH.is_file():
        return 0
    data = _json.loads(_OPTIONAL_BASELINE_PATH.read_text(encoding="utf-8"))
    return int(data.get("ceiling", 0))


_OPTIONAL_CEILING = _load_optional_baseline()


def check(
    repo_root: Path,
    sovereign_territories: Mapping[str, Any],
) -> EnforcementResult:
    """Check ALL sovereign territories for subfolder drift.

    Iterates every top-level territory in SOVEREIGN_TERRITORIES.
    For territories with nested ``subfolders`` dicts (e.g. agentic_core),
    recursively checks those as well.
    """
    violations: list[Violation] = []
    stats = {
        "territories_checked": 0,
        "undeclared_count": 0,
        "missing_required_count": 0,
        "missing_optional_count": 0,
    }

    for territory_name, config in sovereign_territories.items():
        if not isinstance(config, Mapping):
            continue

        # Schema policy: list/tuple subfolders must not coexist with
        # required_subfolders/optional_subfolders (use dict instead).
        _check_schema_policy(territory_name, config, violations)

        territory_path = repo_root / territory_name
        if not territory_path.is_dir():
            continue

        # Check this territory's own subfolder declarations
        _check_one_territory(
            territory_path,
            territory_name,
            config,
            violations,
            stats,
        )

        # For territories with nested subfolders (e.g. agentic_core has
        # L0_routing, config, mixins, etc. each with their own subfolders),
        # recurse into those.
        subfolders_dict = _get_mapping(config, "subfolders")
        if subfolders_dict:
            for sf_name, sf_config in subfolders_dict.items():
                if not isinstance(sf_config, Mapping):
                    continue
                sf_path = territory_path / sf_name
                if not sf_path.is_dir():
                    continue
                _check_one_territory(
                    sf_path,
                    f"{territory_name}/{sf_name}",
                    sf_config,
                    violations,
                    stats,
                )

    # Ceiling enforcement: missing-optional count must not exceed baseline ceiling
    stats["missing_optional_ceiling"] = _OPTIONAL_CEILING
    if _OPTIONAL_CEILING > 0 and stats["missing_optional_count"] > _OPTIONAL_CEILING:
        violations.append(
            Violation(
                type="optional_ceiling_breach",
                path="missing_optional_baseline.json",
                severity="error",
                detail=(
                    f"Missing-optional count ({stats['missing_optional_count']}) exceeds "
                    f"baseline ceiling ({_OPTIONAL_CEILING}). "
                    "Update missing_optional_baseline.json with --acknowledge-optional-growth."
                ),
            ),
        )

    return make_result("territory_diff", violations, stats)


def _check_one_territory(
    territory_path: Path,
    display_name: str,
    config: Mapping[str, Any],
    violations: list[Violation],
    stats: dict[str, int],
) -> None:
    """Check a single territory directory against its declared subfolders."""
    declared_required = set(_get_list(config, "required_subfolders"))
    declared_optional = set(_get_list(config, "optional_subfolders"))

    # Subfolders can be a Mapping (dict → keys are subfolder names) or
    # a sequence (list/tuple of subfolder name strings).  Both are valid
    # blueprint schemas; after _deep_freeze, lists become tuples.
    subfolders_val = config.get("subfolders")
    if isinstance(subfolders_val, Mapping) and subfolders_val:
        if not declared_required and not declared_optional:
            declared_optional = set(subfolders_val.keys())
    elif isinstance(subfolders_val, (tuple, list)) and subfolders_val:
        if not declared_required and not declared_optional:
            declared_optional = set(subfolders_val)

    declared_all = declared_required | declared_optional

    if not declared_all:
        return

    stats["territories_checked"] += 1

    actual = set()
    try:
        for entry in os.scandir(territory_path):
            if entry.is_dir() and entry.name not in EXCLUDED_DIRS:
                actual.add(entry.name)
    except OSError:
        return

    undeclared = actual - declared_all
    missing_required = declared_required - actual
    missing_optional = declared_optional - actual

    strict = bool(_get_scalar(config, "strict_subfolder_enforcement", False))

    for d in sorted(undeclared):
        stats["undeclared_count"] += 1
        violations.append(
            Violation(
                type="undeclared_subfolder",
                path=f"{display_name}/{d}",
                severity="error" if strict else "warning",
                detail=f"Subfolder '{d}' exists on disk but is not declared in blueprint for '{display_name}'",
            ),
        )

    for d in sorted(missing_required):
        stats["missing_required_count"] += 1
        violations.append(
            Violation(
                type="missing_required_subfolder",
                path=f"{display_name}/{d}",
                severity="error",
                detail=f"Required subfolder '{d}' is declared in blueprint but missing on disk for '{display_name}'",
            ),
        )

    for d in sorted(missing_optional):
        stats["missing_optional_count"] += 1
        violations.append(
            Violation(
                type="missing_optional_subfolder",
                path=f"{display_name}/{d}",
                severity="warning",
                detail=f"Optional subfolder '{d}' is declared in blueprint but missing on disk for '{display_name}'",
            ),
        )


def _check_schema_policy(
    territory_name: str,
    config: Mapping[str, Any],
    violations: list[Violation],
) -> None:
    """Warn if a territory uses list/tuple subfolders alongside required/optional semantics.

    Policy A: list/tuple subfolders are allowed ONLY when all entries are
    optional and no per-subfolder metadata is required.  If required_subfolders
    or optional_subfolders are also declared, the territory MUST use a dict
    schema so each subfolder can carry purpose and classification.
    """
    subfolders_val = config.get("subfolders")
    is_sequence = isinstance(subfolders_val, (tuple, list))
    has_req = bool(config.get("required_subfolders"))
    has_opt = bool(config.get("optional_subfolders"))

    if is_sequence and (has_req or has_opt):
        violations.append(
            Violation(
                type="schema_policy_violation",
                path=territory_name,
                severity="warning",
                detail=(
                    f"Territory '{territory_name}' uses list/tuple subfolders but also "
                    "declares required_subfolders or optional_subfolders. "
                    "Migrate to dict-based subfolder schema for explicit intent metadata."
                ),
            ),
        )

    if is_sequence and subfolders_val:
        for name in subfolders_val:
            if not isinstance(name, str):
                continue
            # list/tuple entries have no purpose — flag if territory is not
            # marked as relaxed enforcement.
            if not config.get("enforcement_level") == "relaxed":
                pass  # Acceptable under Policy A (all-optional, no metadata)


# ── Helpers for frozen MappingProxy access ──


def _get_list(config: Mapping[str, Any], key: str) -> tuple[str, ...]:
    """Extract a list/tuple value from a possibly-frozen config."""
    val = config.get(key)
    if val is None:
        return ()
    if isinstance(val, (list, tuple)):
        return tuple(val)
    return ()


def _get_mapping(config: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    """Extract a mapping value from a possibly-frozen config."""
    val = config.get(key)
    if val is None:
        return {}
    if isinstance(val, Mapping):
        return val
    return {}


def _get_scalar(config: Mapping[str, Any], key: str, default: Any = None) -> Any:
    """Extract a scalar value from a possibly-frozen config."""
    return config.get(key, default)
