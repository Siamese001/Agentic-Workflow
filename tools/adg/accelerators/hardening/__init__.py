"""Hardening accelerator proxy module.

Delegates to the unified adg_harden.py tool.
"""

from tools.adg.accelerators.hardening.proxy import (
    run_hardening_check,
    run_p0_hardening,
    run_p1_hardening,
    run_p2_hardening,
)

__all__ = [
    "run_hardening_check",
    "run_p0_hardening",
    "run_p1_hardening",
    "run_p2_hardening",
]
