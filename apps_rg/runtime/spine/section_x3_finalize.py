"""Section lane X3 + spine Exit — aggregate_x3 judge math then ExitEvalPipeline authority."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from agentic_core.L3_orchestration.exit_eval.v6.pipeline import ExitEvalPipeline
from apps_rg.runtime.executive_summary_certification import (
    executive_summary_x3_requires_failure,
)

SPINE_FEC_ARTIFACT = "final_evidence_contract.json"
LEGACY_FEC_BRIDGE_ALIAS = "final_evidence_contract_bridge.json"
LANE_X3_MIRROR_AUTHORITY_SCOPE = "apps_rg_lane_x3_mirror_not_core_exit_authority"
CORE_EXIT_AUTHORITY_SCOPE = "agentic_core_exit_disposition_receipt"
FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT = "final_materialized_acceptance_contract.json"
FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID = "x3_final_materialized_acceptance_contract"
FINAL_MATERIALIZED_BLOCK_X3_CODE = "X3_BLOCK_FINAL_MATERIALIZED_ACCEPTANCE"
_FINAL_MATERIALIZED_PERSISTED_FIELDS = frozenset(
    {
        "final_materialized_acceptance_contract_ref",
        "final_materialized_acceptance_ok",
        "final_materialized_acceptance_failure_gate",
        "final_materialized_acceptance_original_x3_code",
        "final_materialized_acceptance_original_pass",
        "final_materialized_acceptance_original_pass_",
        "final_materialized_acceptance_blocked",
        "blocked_by_gate",
    }
)
_FINAL_MATERIALIZED_FAILURE_FIELDS = frozenset(
    {
        "final_materialized_acceptance_failure_gate",
        "final_materialized_acceptance_original_x3_code",
        "final_materialized_acceptance_original_pass",
        "final_materialized_acceptance_original_pass_",
        "final_materialized_acceptance_blocked",
        "blocked_by_gate",
    }
)


def _write_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return doc if isinstance(doc, dict) else {}


def _load_json_any(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


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
    if (
        x3_doc.get("final_materialized_acceptance_ok") is False
        and str(x3_doc.get("final_materialized_acceptance_failure_gate") or "")
        == FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID
    ):
        return "failure"
    if executive_summary_x3_requires_failure(x3_doc):
        return "failure"
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


def _preserve_existing_final_materialized_fields(
    artifact_dir: Path,
    x3_doc: dict[str, Any],
) -> dict[str, Any]:
    existing = _load_json(artifact_dir / "x3_disposition.json")
    if not existing:
        return x3_doc
    for key in _FINAL_MATERIALIZED_PERSISTED_FIELDS:
        if (
            x3_doc.get("final_materialized_acceptance_ok") is True
            and key in _FINAL_MATERIALIZED_FAILURE_FIELDS
        ):
            continue
        if key in existing and key not in x3_doc:
            x3_doc[key] = existing[key]
    return x3_doc


def _apply_final_materialized_hard_gate(x3_doc: dict[str, Any]) -> dict[str, Any]:
    if (
        x3_doc.get("final_materialized_acceptance_ok") is not False
        or str(x3_doc.get("final_materialized_acceptance_failure_gate") or "")
        != FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID
    ):
        return x3_doc
    original_code = str(
        x3_doc.get("final_materialized_acceptance_original_x3_code")
        or x3_doc.get("x3_code")
        or ""
    )
    x3_doc.setdefault("final_materialized_acceptance_original_x3_code", original_code)
    if "pass" in x3_doc:
        x3_doc.setdefault("final_materialized_acceptance_original_pass", bool(x3_doc.get("pass")))
    if "pass_" in x3_doc:
        x3_doc.setdefault("final_materialized_acceptance_original_pass_", bool(x3_doc.get("pass_")))
    x3_doc["x3_code"] = FINAL_MATERIALIZED_BLOCK_X3_CODE
    x3_doc["pass"] = False
    x3_doc["pass_"] = False
    x3_doc["final_materialized_acceptance_blocked"] = True
    x3_doc["blocked_by_gate"] = FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID
    x3_doc["terminal_class"] = "failure"
    return x3_doc


def _final_materialized_text(artifact_dir: Path) -> tuple[str, str]:
    """Resolve the final display artifact used by the lane, independent of provider raw text."""
    command_output = artifact_dir / "command_output.txt"
    if command_output.is_file():
        text = _load_text(command_output).strip()
        if text:
            return text, command_output.name
    output_candidates = sorted(
        p for p in artifact_dir.glob("*_output.txt") if p.is_file()
    )
    for path in output_candidates:
        text = _load_text(path).strip()
        if text:
            return text, path.name
    l2 = _load_json(artifact_dir / "l2_output.json")
    for key in (
        "resume_display_text",
        "headline_line",
        "narrative_sentence",
        "summary_text",
    ):
        text = str(l2.get(key) or "").strip()
        if text:
            return text, "l2_output.json"
    bullets = l2.get("bullets")
    if isinstance(bullets, list) and bullets:
        lines = [
            str(row.get("bullet_text") or "").strip()
            for row in bullets
            if isinstance(row, dict) and str(row.get("bullet_text") or "").strip()
        ]
        if lines:
            return "\n".join(f"- {line}" for line in lines), "l2_output.json"
    competencies = l2.get("competencies")
    if isinstance(competencies, list) and competencies:
        labels = [
            str(row.get("label") or row.get("category") or "").strip()
            for row in competencies
            if isinstance(row, dict) and str(row.get("label") or row.get("category") or "").strip()
        ]
        if labels:
            return "\n".join(labels), "l2_output.json"
    return "", ""


def _final_claim_ledger_rows(artifact_dir: Path) -> list[dict[str, Any]]:
    doc = _load_json_any(artifact_dir / "claim_ledger.json")
    if isinstance(doc, list):
        return [dict(r) for r in doc if isinstance(r, dict)]
    l2 = _load_json(artifact_dir / "l2_output.json")
    rows = l2.get("claim_ledger")
    if isinstance(rows, list):
        return [dict(r) for r in rows if isinstance(r, dict)]
    return []


def _final_x1d_judge_rows(artifact_dir: Path) -> list[dict[str, Any]]:
    doc = _load_json(artifact_dir / "x1d_llm_judge_outputs.json")
    rows = doc.get("judges")
    if isinstance(rows, list):
        return [dict(r) for r in rows if isinstance(r, dict)]
    return []


def _x1d_model_backed_passes(judges: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for judge in judges:
        if judge.get("evaluator_mode") != "MODEL_BACKED":
            continue
        if judge.get("provider_status") not in {None, "MODEL_BACKED_PASS"}:
            continue
        if judge.get("pass") is False or judge.get("decisive_failure"):
            continue
        score = judge.get("normalized_score")
        threshold = judge.get("normalized_threshold")
        if score is not None and threshold is not None and float(score) < float(threshold):
            continue
        provider_key = str(judge.get("provider_key") or judge.get("judge_id") or "").strip()
        if provider_key:
            out.append(provider_key)
    return out


def build_final_materialized_acceptance_contract(
    artifact_dir: Path,
    *,
    section_id: str,
    x3: Any,
    x3_doc: dict[str, Any],
) -> dict[str, Any]:
    """Per-section final artifact contract: X3 can only certify what was actually materialized."""
    x2_doc = _load_json(artifact_dir / "x2_gate_outputs.json")
    gates = x2_doc.get("gates") if isinstance(x2_doc.get("gates"), list) else []
    failed_gate_ids = [
        str(g.get("gate_id") or "")
        for g in gates
        if isinstance(g, dict) and not bool(g.get("pass"))
    ]
    output_text, output_ref = _final_materialized_text(artifact_dir)
    x2_present = bool(gates)
    x2_all_pass = x2_present and not failed_gate_ids
    final_output_present = bool(output_text.strip())
    final_claim_ledger = _final_claim_ledger_rows(artifact_dir)
    final_x1d_judges = _final_x1d_judge_rows(artifact_dir)
    final_x1d_pass_keys = _x1d_model_backed_passes(final_x1d_judges)
    repair_ledger = _load_json(artifact_dir / "section_repair_ledger.json")
    terminal_class = _terminal_class_from_x3(x3, x3_doc)
    x3_authorizes = terminal_class in {"success", "success_with_review"}
    acceptance_ok = (not x3_authorizes) or (
        final_output_present and x2_present and x2_all_pass
    )
    contract = {
        "schema_version": "apps_rg.final_materialized_acceptance_contract.v1",
        "section_id": section_id,
        "gate_id": FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID,
        "pass": acceptance_ok,
        "terminal_class": terminal_class,
        "x3_authorizes": x3_authorizes,
        "final_materialized_output_ref": output_ref,
        "final_materialized_output_present": final_output_present,
        "final_materialized_output_char_count": len(output_text),
        "x2_gate_outputs_present": x2_present,
        "x2_all_pass": x2_all_pass,
        "failed_gate_ids": failed_gate_ids,
        "final_claim_ledger_present": bool(final_claim_ledger),
        "final_claim_ledger_row_count": len(final_claim_ledger),
        "x1d_judge_outputs_present": (artifact_dir / "x1d_llm_judge_outputs.json").is_file(),
        "x1d_judge_count": len(final_x1d_judges),
        "x1d_model_backed_pass_provider_keys": final_x1d_pass_keys,
        "x1d_all_model_backed_judges_pass": bool(final_x1d_judges)
        and len(final_x1d_pass_keys)
        == len([j for j in final_x1d_judges if j.get("evaluator_mode") == "MODEL_BACKED"]),
        "repair_ledger_present": bool(repair_ledger),
        "repair_ledger_authoritative_l2_source": str(
            repair_ledger.get("authoritative_l2_source") or ""
        ),
        "repair_ledger_authoritative_attempt": repair_ledger.get("authoritative_attempt"),
        "l2_output_present": (artifact_dir / "l2_output.json").is_file(),
        "acceptance_inputs": [
            "final_materialized_output",
            "claim_ledger",
            "x2_gate_outputs",
            "x1d_judge_outputs",
            "section_repair_ledger",
        ],
        "enforcement": (
            "X3_ALLOW or review-authorized section outcomes must be backed by final "
            "materialized display output and passing final X2 gates."
        ),
    }
    _write_json(artifact_dir / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT, contract)
    return contract


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
    x3_doc = _preserve_existing_final_materialized_fields(artifact_dir, x3_doc)
    x3_doc = _apply_final_materialized_hard_gate(x3_doc)
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

    base_x3_doc = _x3_to_doc(x3)
    final_contract = build_final_materialized_acceptance_contract(
        artifact_dir,
        section_id=section_id,
        x3=x3,
        x3_doc=base_x3_doc,
    )
    merged_extra = dict(x3_doc_extra or {})
    merged_extra.setdefault(
        "final_materialized_acceptance_contract_ref",
        FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT,
    )
    merged_extra.setdefault(
        "final_materialized_acceptance_ok",
        bool(final_contract.get("pass")),
    )
    if final_contract.get("x3_authorizes") and not final_contract.get("pass"):
        merged_extra.setdefault(
            "final_materialized_acceptance_failure_gate",
            FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID,
        )
    x3_doc = persist_section_x3_mirror(artifact_dir, x3, x3_doc_extra=merged_extra)

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
    "FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT",
    "FINAL_MATERIALIZED_ACCEPTANCE_GATE_ID",
    "FINAL_MATERIALIZED_BLOCK_X3_CODE",
    "LEGACY_FEC_BRIDGE_ALIAS",
    "CORE_EXIT_AUTHORITY_SCOPE",
    "LANE_X3_MIRROR_AUTHORITY_SCOPE",
    "SPINE_FEC_ARTIFACT",
    "build_final_materialized_acceptance_contract",
    "finalize_section_lane_x3",
    "finalize_section_spine_exit_after_sealed_l2",
    "lane_outcome_authorized_from_x3",
    "lane_x3_code_from_x3",
    "persist_section_x3_mirror",
    "refresh_section_exit_after_x3_change",
]
