"""L7 route-family coverage subpackage.

Emits a typed coverage matrix declaring which agentic_core route families
have a real-runtime, structural-only, fixture-only, or missing
L7_AUDITABILITY surface. The matrix is intentionally honest — it never
claims CERTIFIED for a family that lacks its own HOW trace, Fort Knox
evidence, manifest binding, spine-proof binding, and verifier.

This subpackage is non-mutating and non-routing. It is a pure projection
over the artifacts already on disk for the current run plus a static
catalog of known route-family entrypoints.
"""

from agentic_core.L7_auditability.coverage.route_family_l7_coverage import (
    ROUTE_FAMILIES,
    L7_ROUTE_FAMILY_COVERAGE_FILENAME,
    build_l7_route_family_coverage,
)

__all__ = [
    "ROUTE_FAMILIES",
    "L7_ROUTE_FAMILY_COVERAGE_FILENAME",
    "build_l7_route_family_coverage",
]
