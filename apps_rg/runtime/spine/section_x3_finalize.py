"""Section lane X3 + spine Exit — aggregate_x3 judge math then ExitEvalPipeline authority."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from agentic_core.L3_orchestration.exit_eval.v6.pipeline import ExitEvalPipeline

SPINE_FEC_ARTIFACT = "final_evidence_contract.json"
LEGACY_FEC_BRIDGE_ALIAS = "final_evidence_contract_bridge.json"


def _write_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _x3_to_doc(x3: Any) -> dict[str, Any]:
    if hasattr(x3, "to_dict"):
        return dict(x3.to_dict())
    if isinstance(x3, dict):
        return dict(x3)
    return dict(x3)


def _terminal_class_from_x3(x3: Any, x3_doc: dict[str, Any]) -> str:
    if hasattr(x3, "pass_"):
        return "success" if bool(x3.pass_) else "failure"
    if x3_doc.get("pass") is True or x3_doc.get("pass_") is True:
        return "success"
    code = str(x3_doc.get("x3_code") or getattr(x3, "x3_code", "") or "")
    if code.startswith("X3_ALLOW") or code in {"EXIT_OK", "EXIT_PARTIAL", "X3C", "X3D"}:
        return "success"
    return "failure"


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
    _write_json(artifact_dir / "x3_disposition.json", x3_doc)
    return x3_doc


def refresh_section_exit_after_x3_change(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x3_doc: dict[str, Any],
) -> None:
    """Re-run ExitEvalPipeline + exit receipts when x3 mirror changed after initial finalize."""
    run_id = str(runtime_payload.get("run_id") or "")
    request_id = str(runtime_payload.get("request_id") or run_id)
    receipts: dict[str, Any] = {
        "run_id": run_id,
        "request_id": request_id,
        "section_id": section_id,
        "x3_disposition": x3_doc,
        "x3_code": str(x3_doc.get("x3_code") or "UNKNOWN"),
        "terminal_class": "success" if x3_doc.get("pass") or x3_doc.get("pass_") else "failure",
        "app_name": "apps_rg",
        "spine_mode": "section_spine_run",
        "x3_refresh": True,
    }
    exit_result = ExitEvalPipeline(app_name="apps_rg").run(receipts)
    runtime_payload["spine_exit_eval_disposition"] = str(
        getattr(getattr(exit_result, "disposition", None), "value", exit_result)
    )
    from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2

    finalize_section_exit_after_l2(artifact_dir, section_id, runtime_payload)


def finalize_section_lane_x3(
    *,
    artifact_dir: Path,
    section_id: str,
    runtime_payload: dict[str, Any],
    aggregate_x3_fn: Callable[..., Any] | None = None,
    x3_result: Any | None = None,
    x3_doc_extra: dict[str, Any] | None = None,
    skip_exit_receipts: bool = False,
    **aggregate_kwargs: Any,
) -> Any:
    """Run lane aggregate_x3, mirror to x3_disposition.json, spine ExitEvalPipeline, exit receipt."""
    if x3_result is not None:
        x3 = x3_result
    elif aggregate_x3_fn is not None:
        x3 = aggregate_x3_fn(**aggregate_kwargs)
    else:
        raise ValueError("finalize_section_lane_x3 requires aggregate_x3_fn or x3_result")

    x3_doc = persist_section_x3_mirror(artifact_dir, x3, x3_doc_extra=x3_doc_extra)

    if skip_exit_receipts:
        return x3

    run_id = str(runtime_payload.get("run_id") or "")
    request_id = str(runtime_payload.get("request_id") or run_id)
    receipts: dict[str, Any] = {
        "run_id": run_id,
        "request_id": request_id,
        "section_id": section_id,
        "x3_disposition": x3_doc,
        "x3_code": str(x3_doc.get("x3_code") or getattr(x3, "x3_code", "UNKNOWN")),
        "terminal_class": _terminal_class_from_x3(x3, x3_doc),
        "app_name": "apps_rg",
        "spine_mode": "section_spine_run",
    }
    exit_result = ExitEvalPipeline(app_name="apps_rg").run(receipts)
    runtime_payload["spine_exit_eval_disposition"] = str(
        getattr(getattr(exit_result, "disposition", None), "value", exit_result)
    )

    from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2

    finalize_section_exit_after_l2(artifact_dir, section_id, runtime_payload)
    return x3


__all__ = [
    "LEGACY_FEC_BRIDGE_ALIAS",
    "SPINE_FEC_ARTIFACT",
    "finalize_section_lane_x3",
    "persist_section_x3_mirror",
    "refresh_section_exit_after_x3_change",
]
