"""Product output format and fail-closed runtime policy (integrated ``python -m apps_rg``)."""

from __future__ import annotations

import json
import os
from pathlib import Path


def docx_output_required() -> bool:
    """When False (default), gates and package X3 do not require DOCX artifacts."""
    raw = os.environ.get("APPS_RG_DOCX_OUTPUT_REQUIRED", "").strip().lower()
    return raw in ("1", "true", "yes", "on")


def _env_on(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def is_apps_rg_test_harness() -> bool:
    """Pytest/offline helpers only — not ``python -m apps_rg`` product runs."""
    return _env_on("APPS_RG_TEST_HARNESS")


def product_fail_closed_runtime() -> bool:
    """Live Qwen, BGE, judges required; no pseudo/mock substitutes on product path.

    Default strict for every ``python -m apps_rg`` invocation. Opt-out only via
    ``APPS_RG_ALLOW_PRODUCT_SHORTCUTS=1`` or ``APPS_RG_TEST_HARNESS=1``.
    """
    if is_apps_rg_test_harness():
        return False
    if _env_on("APPS_RG_ALLOW_PRODUCT_SHORTCUTS"):
        return False
    return True


def require_live_bge_embeddings() -> bool:
    """BGE-M3 must embed; no pseudo_digest on product / mandatory C0 paths."""
    if is_apps_rg_test_harness():
        return False
    if product_fail_closed_runtime():
        return True
    from apps_rg.runtime.c0_mandatory_policy import apps_rg_c0_dense_sparse_mandatory

    return apps_rg_c0_dense_sparse_mandatory()


PRODUCT_QUALITY_PASS = "PASS"
RUNTIME_REAL_LLM = "REAL_LLM"
PHASE1_PRIOR_LANE_FAILED_BLOCKER = "PHASE1_PRIOR_LANE_FAILED"


def product_pass_allows_c02_write(
    write_receipt: dict | object | None,
    *,
    index_maintenance_bound: bool = False,
) -> tuple[bool, str]:
    """Same-run Chroma write does not satisfy product PASS without pre-run index receipt."""
    from apps_rg.runtime.c02_chroma_lifecycle import (
        C02_CHROMA_WRITE_ATTEMPTED,
        same_run_write_blocks_product_pass,
    )

    wr = write_receipt if isinstance(write_receipt, dict) else {}
    if not same_run_write_blocks_product_pass(wr):
        return True, "ok"
    if str(wr.get("status") or "") != C02_CHROMA_WRITE_ATTEMPTED:
        return True, "ok"
    if index_maintenance_bound:
        return True, "pre_run_index_bound"
    return False, "same_run_c02_chroma_write_not_product_proof"


def lane_run_dir_meets_product_bar(run_dir: Path) -> tuple[bool, str]:
    """True when run_dir l2+x3 evidence meets product lane bar (REAL_LLM + PASS + X3 allow family)."""
    from apps_rg.runtime.c02_chroma_lifecycle import index_build_receipt_bound
    from apps_rg.runtime.runtime_proof_layout import _is_accepted_real_llm_qwen_bundle
    from apps_rg.runtime.validators.companion_bullet_finalization import COMPANION_FINALIZED_X3_CODES

    room_receipt = run_dir / "c0_evidence_room_receipt.json"
    if room_receipt.is_file():
        try:
            room = json.loads(room_receipt.read_text(encoding="utf-8"))
            bridge = room.get("bridge_doc") or {}
            c0_room = bridge.get("c0_evidence_room") or {}
            c02 = c0_room.get("c02") or {}
            write_block = c02.get("c02_chroma_write") or {}
            ok_write, write_reason = product_pass_allows_c02_write(
                write_block,
                index_maintenance_bound=index_build_receipt_bound(run_dir),
            )
            if not ok_write:
                return False, write_reason
            ingest = c02.get("fact_vectors_ingest") or {}
            if str(ingest.get("status") or "") == "PASS" and product_fail_closed_runtime():
                ok_ing, ing_reason = product_pass_allows_c02_write(
                    {
                        "status": "ATTEMPTED",
                        "attempted": True,
                        "upserted_count": ingest.get("upserted_count"),
                    },
                    index_maintenance_bound=index_build_receipt_bound(run_dir),
                )
                if not ok_ing:
                    return False, ing_reason
        except (json.JSONDecodeError, OSError):  # guardian: allow-silent-swallow -- P2 burndown: optional ingest receipt probe
            pass

    run_posix = run_dir.as_posix()
    if "phase0_synthetic" in run_posix:
        return False, "phase0_synthetic_stub_not_product_lane"

    if not _is_accepted_real_llm_qwen_bundle(run_dir):
        return False, "not_accepted_real_llm_qwen_bundle"

    l2_path = run_dir / "l2_output.json"
    if not l2_path.is_file():
        return False, "missing_l2_output"
    try:
        l2 = json.loads(l2_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, f"l2_unreadable:{type(exc).__name__}"

    if str(l2.get("runtime_generation_status") or "") != RUNTIME_REAL_LLM:
        return False, f"runtime_not_REAL_LLM:{l2.get('runtime_generation_status')}"
    pq = str(l2.get("product_quality_status") or "")
    if pq.startswith("PHASE0"):
        return False, f"product_quality_phase0_stub:{pq}"
    if pq != PRODUCT_QUALITY_PASS:
        return False, f"product_quality_not_PASS:{pq}"

    x3_path = run_dir / "x3_disposition.json"
    if not x3_path.is_file():
        return False, "missing_x3_disposition"
    try:
        x3 = json.loads(x3_path.read_text(encoding="utf-8"))
        x3_code = str(x3.get("x3_code") or x3.get("x3_disposition") or "UNKNOWN")
    except (json.JSONDecodeError, OSError):
        return False, "x3_unreadable"
    if x3_code not in COMPANION_FINALIZED_X3_CODES:
        return False, f"x3_not_allow:{x3_code}"
    return True, "ok"


def phase1_dispatch_hard_failed(dispatch_result: dict | object | None) -> bool:
    """True when lane CLI dispatch reported fault or error exit."""
    res = dispatch_result if isinstance(dispatch_result, dict) else {}
    if str(res.get("fault") or "").strip():
        return True
    return str(res.get("exit_status") or "").strip().lower() == "error"


__all__ = [
    "PHASE1_PRIOR_LANE_FAILED_BLOCKER",
    "PRODUCT_QUALITY_PASS",
    "RUNTIME_REAL_LLM",
    "docx_output_required",
    "is_apps_rg_test_harness",
    "lane_run_dir_meets_product_bar",
    "phase1_dispatch_hard_failed",
    "product_fail_closed_runtime",
    "product_pass_allows_c02_write",
    "require_live_bge_embeddings",
]
