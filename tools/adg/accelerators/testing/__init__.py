"""Testing accelerator proxy module.

Delegates to the unified adg_test.py tool.
"""

from tools.adg.accelerators.testing.proxy import (
    run_gap_analysis,
    run_preflight,
    run_scope_analysis,
    run_test_check,
)

__all__ = [
    "run_gap_analysis",
    "run_preflight",
    "run_scope_analysis",
    "run_test_check",
]
