"""apps_lic canonical product dispatch."""

from apps_lic.runtime.dispatch.canonical_dispatch import (
    ROUTE_FAMILY_R3R4,
    ROUTE_FAMILY_R4,
    ROUTE_FAMILY_R5,
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.runtime.dispatch.spine_run_result import SpineRunResult

__all__ = [
    "ROUTE_FAMILY_R3R4",
    "ROUTE_FAMILY_R4",
    "ROUTE_FAMILY_R5",
    "SpineRunResult",
    "build_cli_ingress_raw",
    "run_canonical_apps_lic_spine",
]
