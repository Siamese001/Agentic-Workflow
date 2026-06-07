"""Compat shim — moved to tools.plan_lifecycle._plan_wave_table_updater (sunset; was tools/windsurf).

Re-exports the relocated module so legacy import paths keep working during the
decommission sunset window (plan cursor-naming-rename-w5-b4f1a9). Remove after W7.
"""
import sys as _sys
import warnings as _warnings

_warnings.warn(
    "tools.windsurf._plan_wave_table_updater moved to tools.plan_lifecycle._plan_wave_table_updater; update imports (sunset).",
    DeprecationWarning,
    stacklevel=2,
)
from tools.plan_lifecycle import _plan_wave_table_updater as _new  # noqa: E402

_sys.modules[__name__] = _new

if __name__ == "__main__":
    import runpy as _runpy

    _runpy.run_module("tools.plan_lifecycle._plan_wave_table_updater", run_name="__main__")
