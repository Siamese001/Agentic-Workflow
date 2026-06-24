"""apps_rg R1 cache adapters (lazy exports).

Keep this package import-light: ``python -m apps_rg`` imports
``apps_rg.cache.r1a_adapter`` during CLI setup, and the pre-U0 fallback path must
not pull Redis/UWG promotion dependencies before it can run.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "AppsRgR1BCacheAdapter": ("apps_rg.cache.r1b_adapter", "AppsRgR1BCacheAdapter"),
    "HistoricalIntentRecord": ("apps_rg.cache.r1b_models", "HistoricalIntentRecord"),
    "HistoricalOutputChunk": ("apps_rg.cache.r1b_models", "HistoricalOutputChunk"),
    "check_r1b_for_apps_rg": ("apps_rg.cache.r1b_adapter", "check_r1b_for_apps_rg"),
    "ingest_post_exit_after_run": ("apps_rg.cache.r1b_post_exit_ingest", "ingest_post_exit_after_run"),
    "PREFLIGHT_ORDER": ("apps_rg.cache.r1b_whole_run_preflight", "PREFLIGHT_ORDER"),
    "execute_whole_run_r1b_preflight": (
        "apps_rg.cache.r1b_whole_run_preflight",
        "execute_whole_run_r1b_preflight",
    ),
    "run_whole_run_cache_preflight": (
        "apps_rg.cache.whole_run_entrypoint_preflight",
        "run_whole_run_cache_preflight",
    ),
    "promote_and_project_r1b_cache": (
        "apps_rg.cache.r1b_uwg_promotion",
        "promote_and_project_r1b_cache",
    ),
    "promote_r1b_cache_via_uwg": (
        "apps_rg.cache.r1b_uwg_promotion",
        "promote_r1b_cache_via_uwg",
    ),
    "build_receipt_field_parity_matrix": (
        "apps_rg.cache.r1b_uwg_receipt_contract",
        "build_receipt_field_parity_matrix",
    ),
    "document_r1b_uwg_core_receipt_gaps": (
        "apps_rg.cache.r1b_uwg_receipt_contract",
        "document_r1b_uwg_core_receipt_gaps",
    ),
    "validate_commit_request_governance": (
        "apps_rg.cache.r1b_uwg_receipt_contract",
        "validate_commit_request_governance",
    ),
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_EXPORTS[name]
    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value


__all__ = list(_LAZY_EXPORTS)
