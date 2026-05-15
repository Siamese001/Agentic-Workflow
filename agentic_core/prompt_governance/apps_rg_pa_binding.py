"""Prompt-Assembly binding for apps_rg `resume_generation` task class.

LEGACY_SHIM — Migrated to apps_rg/runtime/bindings/pa_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2D.

This shim re-exports from the new app-owned location for backward
compatibility during the W2 migration phase. Import from the new
location directly: apps_rg.runtime.bindings.pa_binding
"""
from __future__ import annotations

# Re-export from the new app-owned location
from apps_rg.runtime.bindings.pa_binding import (  # guardian: allow-layer-violation -- LEGACY_SHIM TEMPORARY_THIN_ADAPTER per apps-rg-golden-state-section-generation-a4f9e1 W2D
    APPS_RG_PA_CERT_REF,
    APPS_RG_TARGET_MODEL,
    APPS_RG_TARGET_PROVIDER,
    pa_compose_apps_rg,
    _build_u0_task_block,
    _build_c0_evidence_block,
    _build_user_instruction,
    _build_system_preamble,
    _component_hash,
)

__all__ = [
    "APPS_RG_PA_CERT_REF",
    "APPS_RG_TARGET_MODEL",
    "APPS_RG_TARGET_PROVIDER",
    "pa_compose_apps_rg",
    "_build_u0_task_block",
    "_build_c0_evidence_block",
    "_build_user_instruction",
    "_build_system_preamble",
    "_component_hash",
]
