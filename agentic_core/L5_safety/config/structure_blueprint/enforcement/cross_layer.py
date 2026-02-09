"""
Cross-Layer Import Law — Layer 6: AST graph-based import boundary enforcement.

Enforces:
1. core/ must use stdlib only (no agentic_core.* imports).
2. utils/ must not import from mixins/.
3. config/ must not import from execution layers (L2, L3).
4. No imports FROM volatile territories by non-volatile code (delegated to volatile_rules).

Emits graph depth metrics for audit-grade reporting.
"""

from __future__ import annotations

import json as _json
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L5_safety.config.structure_blueprint.enforcement.import_graph import (
    ImportGraph,
)
from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (
    EnforcementResult,
    Violation,
    make_result,
)

# ── Cross-layer rules ──

# core/ must only import stdlib — no agentic_core.* imports allowed
CORE_FORBIDDEN_PREFIX = "agentic_core."

# utils/ must not import from mixins/
UTILS_FORBIDDEN_IMPORTS = ("agentic_core.mixins.",)

# config/ must not import from execution layers
CONFIG_FORBIDDEN_IMPORTS = (
    "agentic_core.L2_execution.",
    "agentic_core.L3_orchestration.",
)

# Known cross-layer debt: loaded from known_debt_baseline.json.
# Growth forbidden without explicit baseline update.
_BASELINE_PATH = Path(__file__).resolve().parent / "known_debt_baseline.json"


def _load_known_debt_baseline() -> tuple[frozenset[tuple[str, str]], int]:
    """Load known-debt entries and ceiling from the baseline file.

    Returns (frozenset of (source, target) pairs, ceiling int).
    """
    if not _BASELINE_PATH.is_file():
        return frozenset(), 0
    data = _json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
    ceiling = int(data.get("ceiling", 0))
    entries: set[tuple[str, str]] = set()
    for entry in data.get("entries", []):
        entries.add((entry["source"], entry["target"]))
    return frozenset(entries), ceiling


KNOWN_CROSS_LAYER_DEBT, _DEBT_CEILING = _load_known_debt_baseline()


def check(
    root: Path,
    territories: Mapping[str, Any],
    import_graph: ImportGraph,
) -> EnforcementResult:
    """Check cross-layer import boundaries using the ImportGraph."""
    violations: list[Violation] = []
    stats = {
        "total_edges": 0,
        "internal_edges": 0,
        "cross_layer_edges_analyzed": 0,
        "core_stdlib_violations": 0,
        "utils_mixin_violations": 0,
        "config_execution_violations": 0,
    }

    stats["known_debt_items"] = len(KNOWN_CROSS_LAYER_DEBT)
    stats["debt_ceiling"] = _DEBT_CEILING

    # Count total and internal edges
    for source_rel in import_graph.all_files():
        for edge in import_graph.edges_from(source_rel):
            stats["total_edges"] += 1
            if edge.target_module.startswith("agentic_core."):
                stats["internal_edges"] += 1

    # Rule 1: core/ stdlib-only
    _check_core_stdlib(root, import_graph, violations, stats)

    # Rule 2: utils/ must not import mixins/
    _check_utils_purity(root, import_graph, violations, stats)

    # Rule 3: config/ must not import execution layers
    _check_config_independence(root, import_graph, violations, stats)

    # Ceiling enforcement: warning count must not exceed baseline ceiling
    warning_count = sum(1 for v in violations if v["severity"] == "warning")
    stats["warning_count"] = warning_count
    if warning_count > _DEBT_CEILING:
        violations.append(
            Violation(
                type="debt_ceiling_breach",
                path="known_debt_baseline.json",
                severity="error",
                detail=(
                    f"Known-debt warning count ({warning_count}) exceeds "
                    f"baseline ceiling ({_DEBT_CEILING}). "
                    "Update known_debt_baseline.json with --acknowledge-debt."
                ),
            ),
        )

    return make_result("cross_layer", violations, stats)


def _check_core_stdlib(
    root: Path,
    import_graph: ImportGraph,
    violations: list[Violation],
    stats: dict[str, int],
) -> None:
    """core/ files must not import any agentic_core.* modules."""
    core_prefix = "agentic_core/core/"
    for source_rel in import_graph.all_files():
        source_fwd = source_rel.replace("\\", "/")
        if not source_fwd.startswith(core_prefix):
            continue

        for edge in import_graph.edges_from(source_rel):
            stats["cross_layer_edges_analyzed"] += 1
            if edge.target_module.startswith(CORE_FORBIDDEN_PREFIX):
                stats["core_stdlib_violations"] += 1
                violations.append(
                    Violation(
                        type="core_stdlib_violation",
                        path=source_fwd,
                        severity="error",
                        detail=(
                            f"core/ file '{source_fwd}' imports '{edge.target_module}' "
                            f"(line {edge.lineno}) — core/ must use stdlib only"
                        ),
                    ),
                )


def _check_utils_purity(
    root: Path,
    import_graph: ImportGraph,
    violations: list[Violation],
    stats: dict[str, int],
) -> None:
    """utils/ files must not import from mixins/."""
    utils_prefix = "agentic_core/utils/"
    for source_rel in import_graph.all_files():
        source_fwd = source_rel.replace("\\", "/")
        if not source_fwd.startswith(utils_prefix):
            continue

        for edge in import_graph.edges_from(source_rel):
            stats["cross_layer_edges_analyzed"] += 1
            for forbidden in UTILS_FORBIDDEN_IMPORTS:
                if edge.target_module.startswith(forbidden):
                    stats["utils_mixin_violations"] += 1
                    violations.append(
                        Violation(
                            type="utils_mixin_violation",
                            path=source_fwd,
                            severity="error",
                            detail=(
                                f"utils/ file '{source_fwd}' imports '{edge.target_module}' "
                                f"(line {edge.lineno}) — utils/ must not import from mixins/"
                            ),
                        ),
                    )


def _check_config_independence(
    root: Path,
    import_graph: ImportGraph,
    violations: list[Violation],
    stats: dict[str, int],
) -> None:
    """config/ files must not import from execution layers (L2, L3)."""
    config_prefix = "agentic_core/config/"
    for source_rel in import_graph.all_files():
        source_fwd = source_rel.replace("\\", "/")
        if not source_fwd.startswith(config_prefix):
            continue

        for edge in import_graph.edges_from(source_rel):
            stats["cross_layer_edges_analyzed"] += 1
            for forbidden in CONFIG_FORBIDDEN_IMPORTS:
                if edge.target_module.startswith(forbidden):
                    is_known_debt = (source_fwd, edge.target_module) in KNOWN_CROSS_LAYER_DEBT
                    severity = "warning" if is_known_debt else "error"
                    stats["config_execution_violations"] += 1
                    violations.append(
                        Violation(
                            type="config_execution_violation",
                            path=source_fwd,
                            severity=severity,
                            detail=(
                                f"config/ file '{source_fwd}' imports '{edge.target_module}' "
                                f"(line {edge.lineno}) — config/ must not import execution layers"
                                + (" [KNOWN DEBT: lazy import inside try/except]" if is_known_debt else "")
                            ),
                        ),
                    )
