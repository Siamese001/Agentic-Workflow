from __future__ import annotations
"""
DEPRECATED: December 28, 2025
Dashboard functionality has been removed from the Canon Validator.

The validator now runs in pure CLI mode for better performance and reliability.
All dashboard code has been archived to: archives/deprecated_dashboard_2025-12-28/

Reason for deprecation:
- Threading conflicts causing validator hangs
- Unnecessary complexity for core validation tasks
- Flask dependency overhead
- Better suited for separate monitoring tools

For validation results, use the CLI output and generated reports.
"""

import warnings

warnings.warn(
    "canon_dashboard is deprecated and has been removed. "
    "Use CLI mode for validation. "
    "See archives/deprecated_dashboard_2025-12-28/ for legacy code.",
    DeprecationWarning,
    stacklevel=2
)

class CanonDashboard:
    """Deprecated stub - raises error if instantiated"""
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "CanonDashboard has been deprecated. "
            "The Canon Validator now runs in pure CLI mode. "
            "See archives/deprecated_dashboard_2025-12-28/ for legacy code."
        )

class DashboardMetrics:
    """Deprecated stub - raises error if instantiated"""
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "DashboardMetrics has been deprecated. "
            "The Canon Validator now runs in pure CLI mode. "
            "See archives/deprecated_dashboard_2025-12-28/ for legacy code."
        )
