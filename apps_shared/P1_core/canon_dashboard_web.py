from __future__ import annotations
"""
DEPRECATED: December 28, 2025
Flask web dashboard has been removed from the Canon Validator.

The validator now runs in pure CLI mode for better performance and reliability.
All dashboard code has been archived to: archives/deprecated_dashboard_2025-12-28/

Reason for deprecation:
- Threading conflicts causing validator hangs
- Flask server startup delays and port conflicts
- Unnecessary web server overhead for validation tasks
- Better suited for separate monitoring/visualization tools

For validation results, use the CLI output and generated reports.
"""

import warnings

warnings.warn(
    "canon_dashboard_web is deprecated and has been removed. "
    "Use CLI mode for validation. "
    "See archives/deprecated_dashboard_2025-12-28/ for legacy code.",
    DeprecationWarning,
    stacklevel=2
)

def run_server(*args, **kwargs):
    """Deprecated stub - raises error if called"""
    raise RuntimeError(
        "Flask dashboard server has been deprecated. "
        "The Canon Validator now runs in pure CLI mode. "
        "See archives/deprecated_dashboard_2025-12-28/ for legacy code."
    )

# Stub globals for backward compatibility
agents_global = []
metrics = None
