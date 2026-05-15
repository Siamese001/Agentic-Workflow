"""LEGACY_SHIM — MIGRATED to apps_rg/runtime/bindings/exit_binding.py

Per plan apps-rg-golden-state-section-generation-a4f9e1 W2F.

This shim re-exports from the new canonical location.
It is a TEMPORARY compatibility shim for existing callers.
Do not modify; the canonical implementation lives in apps_rg.
"""
from __future__ import annotations

# Re-export all public API from the migrated location
from apps_rg.runtime.bindings.exit_binding import (  # guardian: allow-layer-violation -- LEGACY_SHIM TEMPORARY_THIN_ADAPTER per apps-rg-golden-state-section-generation-a4f9e1 W2F
    APPS_RG_EXIT_CERT_REF,
    ExitBindingResult,
    build_apps_rg_exit_harness,
    exit_finalize_apps_rg,
    extract_apps_rg_exit_gate_policy,
)

# Also re-export key internal helpers used by dispatch for compatibility
from apps_rg.runtime.bindings.exit_binding import (  # guardian: allow-layer-violation -- LEGACY_SHIM continuation re-export from same apps_rg exit_binding module
    _resolve_repo_root,
    _safe_run_dirname,
)

__all__ = [
    "APPS_RG_EXIT_CERT_REF",
    "ExitBindingResult",
    "build_apps_rg_exit_harness",
    "exit_finalize_apps_rg",
    "extract_apps_rg_exit_gate_policy",
]
