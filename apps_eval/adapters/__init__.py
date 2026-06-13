"""Narrow optional live adapters for product runtimes."""

from apps_eval.adapters.apps_lic import run_apps_lic_live
from apps_eval.adapters.apps_rg import run_apps_rg_live

__all__ = ["run_apps_lic_live", "run_apps_rg_live"]
