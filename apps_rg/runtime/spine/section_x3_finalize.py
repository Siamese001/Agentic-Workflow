"""Section lane X3 + spine Exit — aggregate_x3 judge math then ExitEvalPipeline authority."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from agentic_core.L3_orchestration.exit_eval.v6.pipeline import ExitEvalPipeline

SPINE_FEC_ARTIFACT = "final_evidence_contract.json"
LEGACY_FEC_BRIDGE_ALIAS = "final_evidence_contract_bridge.json"
LANE_X3_MIRROR_AUTHORITY_SCOPE = "apps_rg_lane_x3_mirror_not_core_exit_authority"
CORE_EXIT_AUTHORITY_SCOPE = "agentic_core_exit_disposition_receipt"


def _write_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _x3_to_doc(x3: Any) -> dict[str, Any]:
    if hasattr(x3, "to_dict"):
        return dict(x3.to_dict())
    if isinstance(x3, dict):
        return dict(x3)
    if hasattr(x3, "pass_") or hasattr(x3, "x3_code"):
        out: dict[str, Any] = {}
        if hasattr(x3, "x3_code"):
            out["x3_code"] = getattr(x3, "x3_code", "")
        if hasattr(x3, "pass_"):
            out["pass_"] = bool(getattr(x3, "pass_", False))
            out["pass"] = out["pass_"]
        return out
    return {}


_SOFT_FAIL_REVIEW_X3_CODES = frozenset({"X3_REVIEW_JUDGE_SOFT_FAIL", "X3_REVIEW"})


def _terminal_class_from_x3(x3: Any, x3_doc: dict[str, Any]) -> str:
    """Map an x3 disposition to dispatch terminal class.

    Author-Gate decision dec_19e6e344d5db19589 (architecture_choice, 2026-05-28, confidence=0.78):
    treat ``X3_REVIEW_JUDGE_SOFT_FAIL`` as ``success_with_review`` so a borderline judge score
    (e.g. Claude 3.8 vs 4.0 threshold) no longer cascade-blocks every downstream lane. The final
    review packet flags the soft-fail; downstream lanes continue to run, mirroring the semantic
    of REVIEW vs BLOCK. Hard failures (X3_BLOCK, fault) still produce ``failure`` and cascade.
    """
    code = str(x3_doc.get("x3_code") or getattr(x3, "x3_code", "") or "")
    if hasattr(x3, "pass_"):
        if bool(x3.pass_):
            return "success"
        if code in _SOFT_FAIL_REVIEW_X3_CODES:
            return "success_with_review"
        return "failure"
    if x3_doc.get("pass") is True or x3_doc.get("pass_") is True:
        return "success"
    if code.startswith("X3_ALLOW") or code in {"EXIT_OK", "EXIT_PARTIAL", "X3C", "X3D"}:
        return "success"
    if code in _SOFT_FAIL_REVIEW_X3_CODES:
        return "success_with_review"
    return "failure"


def lane_outcome_authorized_from_x3(x3: Any) -> bool:
    """CLI dispatch outcome: True when lane X3 mirror authorizes (dict or dataclass).

    ``success_with_review`` counts as authorized at the dispatch boundary (downstream lanes
    proceed) per Author-Gate decision dec_19e6e344d5db19589. The review status is preserved
    in ``x3_disposition.json`` for the final review packet.
    """
    x3_doc = _x3_to_doc(x3)
    return _terminal_class_from_x3(x3, x3_doc) in {"success", "success_with_review"}


def lane_x3_code_from_x3(x3: Any) -> str:
    """Resolve x3_code for dispatch receipts from dict or dataclass lane x3."""
    x3_doc = _x3_to_doc(x3)
    return str(x3_doc.get("x3_code") or getattr(x3, "x3_code", "") or "")


def persist_section_x3_mirror(
    artifact_dir: Path,
    x3: Any,
    *,
    x3_doc_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Rewrite ``x3_disposition.json`` after post-aggregate mutations (e.g. clarify, proof bundle)."""
    x3_doc = _x3_to_doc(x3)
    if x3_doc_extra:
        x3_doc.update(x3_doc_extra)
    x3_doc.setdefault("authority_scope", LANE_X3_MIRROR_AUTHORITY_SCOPE)
    x3_doc.setdefault("artifact_authority_scope", LANE_X3_MIRROR_AUTHORITY_SCOPE)
    x3_doc.setdefault("section_x3_mirror_only", True)
    x3_doc.setdefault("core_exit_authority_ref", "exit_disposition_receipt.json")
    x3_doc.setdefault("core_exit_authority_scope", CORE_EXIT_AUTHORITY_SCOPE)
    _write_json(artifact_dir / "x3_disposition.json", x3_doc)
    return x3_doc


def _run_section_spine_exit_eval(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x3_doc: dict[str, Any],
    x3: Any | None = None,
    receipts_extra: dict[str, Any] | None = None,
) -> None:
    """ExitEvalPipeline + section exit receipts — requires ``sealed_l2_artifact.json`` on disk."""
    run_id = str(runtime_payload.get("run_id") or "")
    request_id = str(runtime_payload.get("request_id") or run_id)
    receipts: dict[str, Any] = {
        "run_id": run_id,
        "request_id": request_id,
        "section_id": section_id,
        "x3_disposition": x3_doc,
        "x3_code": str(x3_doc.get("x3_code") or getattr(x3, "x3_code", "UNKNOWN")),
        "terminal_class": _terminal_class_from_x3(x3, x3_doc),
        "x3_authority_scope": LANE_X3_MIRROR_AUTHORITY_SCOPE,
        "core_exit_authority_scope": CORE_EXIT_AUTHORITY_SCOPE,
        "app_name": "apps_rg",
        "spine_mode": "section_spine_run",
    }
    if receipts_extra:
        receipts.update(receipts_extra)
    exit_result = ExitEvalPipeline().run(receipts)
    runtime_payload["spine_exit_eval_disposition"] = str(
        getattr(getattr(exit_result, "disposition", None), "value", exit_result)
    )
    runtime_payload["x3_authority_scope"] = LANE_X3_MIRROR_AUTHORITY_SCOPE
    runtime_payload["canonical_exit_authority_scope"] = CORE_EXIT_AUTHORITY_SCOPE
    from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2
    from apps_rg.runtime.spine.spine_span_emit import emit_spine_span_event

    finalize_section_exit_after_l2(artifact_dir, section_id, runtime_payload)
    emit_spine_span_event(
        artifact_dir,
        layer_key="EXIT",
        binding_seam="apps_rg/runtime/spine/section_x3_finalize.py",
        product_visible=bool(runtime_payload.get("product_visible", True)),
        extra={"x3_code": receipts.get("x3_code")},
    )


def finalize_section_spine_exit_after_sealed_l2(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
) -> None:
    """Run spine exit authority after ``finalize_section_l2_after_output`` sealed L2."""
    x3_path = artifact_dir / "x3_disposition.json"
    if not x3_path.is_file():
        return
    try:
        x3_doc = json.loads(x3_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(x3_doc, dict):
        return
    _run_section_spine_exit_eval(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
        x3_doc=x3_doc,
    )


def refresh_section_exit_after_x3_change(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x3_doc: dict[str, Any],
) -> None:
    """Re-run ExitEvalPipeline + exit receipts when x3 mirror changed after initial finalize."""
    _run_section_spine_exit_eval(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
        x3_doc=x3_doc,
        receipts_extra={"x3_refresh": True},
    )


def finalize_section_lane_x3(
    *,
    artifact_dir: Path,
    section_id: str,
    runtime_payload: dict[str, Any],
    aggregate_x3_fn: Callable[..., Any] | None = None,
    x3_result: Any | None = None,
    x3_doc_extra: dict[str, Any] | None = None,
    skip_exit_receipts: bool = True,
    **aggregate_kwargs: Any,
) -> Any:
    """Run lane aggregate_x3 and mirror to x3_disposition.json.

    Exit authority runs after sealed L2 via ``finalize_section_spine_exit_after_sealed_l2``
    (hooked from ``finalize_section_l2_after_output``). Set ``skip_exit_receipts=False`` only
    when sealed L2 already exists (tests).
    """
    if x3_result is not None:
        x3 = x3_result
    elif aggregate_x3_fn is not None:
        x3 = aggregate_x3_fn(**aggregate_kwargs)
    else:
        raise ValueError("finalize_section_lane_x3 requires aggregate_x3_fn or x3_result")

    x3_doc = persist_section_x3_mirror(artifact_dir, x3, x3_doc_extra=x3_doc_extra)

    if skip_exit_receipts:
        return x3

    _run_section_spine_exit_eval(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
        x3_doc=x3_doc,
        x3=x3,
    )
    return x3


__all__ = [
    "LEGACY_FEC_BRIDGE_ALIAS",
    "CORE_EXIT_AUTHORITY_SCOPE",
    "LANE_X3_MIRROR_AUTHORITY_SCOPE",
    "SPINE_FEC_ARTIFACT",
    "finalize_section_lane_x3",
    "finalize_section_spine_exit_after_sealed_l2",
    "lane_outcome_authorized_from_x3",
    "lane_x3_code_from_x3",
    "persist_section_x3_mirror",
    "refresh_section_exit_after_x3_change",
]
