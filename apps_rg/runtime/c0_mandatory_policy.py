"""apps_rg mandatory C0.2 (dense+sparse) and C0.3 (skills graph) binding policy."""

from __future__ import annotations

import os

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

# Canonical generated lanes requiring native C0.3 skills-graph proof when mandatory.
C03_MANDATORY_SECTIONS: frozenset[str] = frozenset(GENERATED_LANES)


def _env_off(name: str, *, default: str = "1") -> bool:
    raw = os.environ.get(name, default).strip().lower()
    return raw in ("0", "false", "no")


def apps_rg_c0_dense_sparse_mandatory() -> bool:
    """When true, whole-run/section C0 must complete BGE dense + sparse lanes (fail-closed)."""
    return not _env_off("APPS_RG_C0_DENSE_SPARSE_MANDATORY")


def apps_rg_c0_sparse_profile_enabled() -> bool:
    """Profile-level sparse lane toggle (tests may set false while keeping dense mandatory off)."""
    return not _env_off("APPS_RG_C0_SPARSE_ENABLED")


def apps_rg_c03_graph_mandatory() -> bool:
    """When true, generated lanes must emit native C0.3 skills-graph evidence."""
    return not _env_off("APPS_RG_C03_GRAPH_MANDATORY")


def is_c03_mandatory_section(section_id: str) -> bool:
    return section_id in C03_MANDATORY_SECTIONS


__all__ = [
    "C03_MANDATORY_SECTIONS",
    "apps_rg_c0_dense_sparse_mandatory",
    "apps_rg_c0_sparse_profile_enabled",
    "apps_rg_c03_graph_mandatory",
    "is_c03_mandatory_section",
]
