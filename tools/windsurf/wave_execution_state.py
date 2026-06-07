"""Compat shim — moved to tools.plan_lifecycle.wave_execution_state (sunset; was tools/windsurf).

Re-exports the relocated module so legacy import paths keep working during the
decommission sunset window (plan cursor-naming-rename-w5-b4f1a9). Remove after W7.
"""
import sys as _sys
import warnings as _warnings

_warnings.warn(
    "tools.windsurf.wave_execution_state moved to tools.plan_lifecycle.wave_execution_state; update imports (sunset).",
    DeprecationWarning,
    stacklevel=2,
)
from tools.plan_lifecycle import wave_execution_state as _new  # noqa: E402

_sys.modules[__name__] = _new

if __name__ == "__main__":
    import runpy as _runpy

    _runpy.run_module("tools.plan_lifecycle.wave_execution_state", run_name="__main__")
