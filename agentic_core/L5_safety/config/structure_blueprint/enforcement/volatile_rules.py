"""
Volatile Rules — Layer 3: Import isolation for volatile territories.

Volatile territories (artifacts, .backup) must NOT be imported by non-volatile code.
This prevents coupling production logic to transient build outputs.
"""

from __future__ import annotations

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


def check(
    root: Path,
    territories: Mapping[str, Any],
    import_graph: ImportGraph,
) -> EnforcementResult:
    """Check that non-volatile code does not import from volatile territories."""
    violations: list[Violation] = []
    stats = {
        "volatile_territories": 0,
        "inbound_violations": 0,
    }

    # Identify volatile territory names
    volatile_names: set[str] = set()
    for name, config in territories.items():
        if isinstance(config, Mapping) and config.get("volatile"):
            volatile_names.add(name)
            stats["volatile_territories"] += 1

    if not volatile_names:
        return make_result("volatile_rules", violations, stats)

    # Build set of module prefixes that are volatile
    volatile_prefixes = tuple(f"{v}." for v in volatile_names) + tuple(f"{v}/" for v in volatile_names)

    # For each file in the import graph, check if it imports from a volatile territory
    for source_rel in import_graph.all_files():
        source_fwd = source_rel.replace("\\", "/")

        # Is the source itself in a volatile territory?
        # guardian: allow-path-string
        source_volatile = any(source_fwd.startswith(v + "/") for v in volatile_names)
        if source_volatile:
            continue

        for edge in import_graph.edges_from(source_rel):
            target_mod = edge.target_module

            # Does the target reference a volatile territory?
            target_volatile = any(target_mod.startswith(p) for p in volatile_prefixes) or (
                target_mod in volatile_names
            )

            if target_volatile:
                stats["inbound_violations"] += 1
                violations.append(
                    Violation(
                        type="volatile_import",
                        path=source_fwd,
                        severity="error",
                        detail=(
                            f"Non-volatile file '{source_fwd}' imports from volatile "
                            f"territory '{target_mod}' — violates import isolation (AD-7)"
                        ),
                    ),
                )

    return make_result("volatile_rules", violations, stats)
