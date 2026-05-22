"""apps_rg Exit compat shim is importable (product path unchanged)."""

from __future__ import annotations

from apps_rg.runtime.bindings import exit_binding as apps_rg_exit_binding


def test_apps_rg_exit_shim_exports_finalize() -> None:
    assert hasattr(apps_rg_exit_binding, "exit_finalize_apps_rg")
    assert callable(apps_rg_exit_binding.exit_finalize_apps_rg)
