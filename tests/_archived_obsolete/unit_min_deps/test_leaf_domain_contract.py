"""
LEAF_DOMAIN contract enforcement.

Deterministic filesystem scan. No heuristics.
Guardian hard gate per LEAF_DOMAINS_NO_LCD in ssot.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)

pytestmark = [pytest.mark.unit_min_deps]

# ---------------------------------------------------------------------------

# Test functions


def test_leaf_domains_no_lcd():
    """LEAF_DOMAINs must not contain illegal subdirectories."""
    ROOT = Path(__file__).resolve().parents[2]
    AGENTIC_CORE = ROOT / AGENTIC_CORE_DIR

    # Load blueprint to get LEAF_DOMAINS
    from agentic_core.L5_safety.config.structure_blueprint.territories import (
        get_all_territories,
    )

    territories = get_all_territories()
    ac = territories.get(AGENTIC_CORE_DIR, {})
    leaf_domains = ac.get("leaf_domains", [])

    violations = []
    for domain in leaf_domains:
        domain_path = AGENTIC_CORE / domain
        if not domain_path.exists():
            continue

        # Scan for illegal subdirectories
        for entry in domain_path.iterdir():
            if entry.is_dir() and not entry.name.startswith("_"):
                # Check if this subdirectory is declared in blueprint
                declared_subfolders = _get_declared_subfolders(domain)
                if entry.name not in declared_subfolders:
                    violations.append(f"{domain}/{entry.name}: illegal subdirectory in LEAF_DOMAIN")

    assert len(violations) == 0, f"LEAF_DOMAIN violations found: {violations}"


def _get_declared_subfolders(domain: str) -> set[str]:
    """Get subfolders declared in the blueprint for a LEAF_DOMAIN."""
    # Import here to avoid circular deps at module level
    try:
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            get_all_territories,
        )

        territories = get_all_territories()
        ac = territories.get(AGENTIC_CORE_DIR, {})
        subfolders_def = ac.get("subfolders", {})
        domain_def = subfolders_def.get(domain, {})
        declared = set()
        # Check for subfolders key
        if "subfolders" in domain_def:
            declared.update(domain_def["subfolders"])
        return declared
    except Exception:
        # If blueprint can't be loaded, return empty set
        return set()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
