"""Integrations package for apps_rg — DECLARATIVE INGRESS-ONLY.

AG-RGGOV-8: This package contains NO runtime execution authority.
All runtime hops have been quarantined. apps_rg is declarative-only.

See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19
"""

# Package is intentionally minimal — all runtime authority removed per AG-RGGOV-8
# Previous exports (ExecutionAdapter, ObservabilityAdapter) quarantined.

__all__ = []
# 