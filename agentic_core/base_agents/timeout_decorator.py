"""
Shim module: re-exports timeout decorator from canonical location.

67 files across L0–L6 import from ``agentic_core.base_agents.timeout_decorator``.
The actual implementation lives in ``agentic_core.L0_maintenance.utils.timeout_decorator_util``.

This shim exists solely to satisfy those imports without a 67-file mass-rename.
New code SHOULD import directly from the canonical location.

Canonical source: agentic_core/L0_maintenance/utils/timeout_decorator_util.py
Created: 2026-02-08 — Phantom-import resolution (Issue #5)
"""

from agentic_core.L0_maintenance.utils.timeout_decorator_util import timeout  # noqa: F401

__all__ = [
    "timeout",
]
