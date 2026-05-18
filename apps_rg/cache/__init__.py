"""apps_rg R1 cache adapters (R1A exact + R1B ROLE_TARGET_RUN semantic cache)."""

from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter, check_r1b_for_apps_rg
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_post_exit_ingest import ingest_post_exit_after_run
from apps_rg.cache.r1b_whole_run_preflight import (
    PREFLIGHT_ORDER,
    execute_whole_run_r1b_preflight,
)
from apps_rg.cache.whole_run_entrypoint_preflight import (
    run_whole_run_cache_preflight,
)
from apps_rg.cache.r1b_uwg_promotion import (
    promote_and_project_r1b_cache,
    promote_r1b_cache_via_uwg,
)
from apps_rg.cache.r1b_uwg_receipt_contract import (
    build_receipt_field_parity_matrix,
    document_shim_core_gaps,
    validate_commit_request_governance,
)

__all__ = [
    "AppsRgR1BCacheAdapter",
    "HistoricalIntentRecord",
    "HistoricalOutputChunk",
    "check_r1b_for_apps_rg",
    "ingest_post_exit_after_run",
    "PREFLIGHT_ORDER",
    "execute_whole_run_r1b_preflight",
    "run_whole_run_cache_preflight",
    "promote_and_project_r1b_cache",
    "promote_r1b_cache_via_uwg",
    "build_receipt_field_parity_matrix",
    "document_shim_core_gaps",
    "validate_commit_request_governance",
]
