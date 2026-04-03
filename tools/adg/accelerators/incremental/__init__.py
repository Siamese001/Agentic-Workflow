"""Lifecycle accelerator proxy module.

Delegates to the unified adg_lifecycle.py tool.
"""

from tools.adg.accelerators.incremental.proxy import (
    run_generate,
    run_maintain,
    run_status,
    run_sync,
    run_update,
)

__all__ = [
    "run_generate",
    "run_maintain",
    "run_status",
    "run_sync",
    "run_update",
]
