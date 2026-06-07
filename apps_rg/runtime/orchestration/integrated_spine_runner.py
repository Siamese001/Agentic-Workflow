"""apps_rg boundary for the integrated single-action spine runner."""

from __future__ import annotations

from importlib import import_module
from typing import Any


def run_integrated_single_action_spine(*args: Any, **kwargs: Any) -> Any:
    """Delegate to the current integrated spine runner behind an app-owned seam."""
    mod = import_module(
        "agentic_core.runtime.entrypoints.integrated_single_action_spine_run"
    )
    runner = getattr(mod, "run_integrated_single_action_spine")
    return runner(*args, **kwargs)


__all__ = ["run_integrated_single_action_spine"]
