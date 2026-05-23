"""Shared L6 shadow handoff packet (offline / post-run artifact; no runtime approval authority)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


L6_PACKET_TYPE = "L6_SHADOW_HANDOFF_PACKET"
L6_PACKET_VERSION = "1"

BULLET_LANE_IDS = frozenset({"unify_bullets", "ibm_bullets"})

UNIFY_REWRITE_POLICY_ID = "unify_bullets_rewrite_policy_v1"
IBM_REWRITE_POLICY_ID = "ibm_bullets_rewrite_policy_v1"


def repo_rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _iso_mtime(path: Path) -> str:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def summarize_x2(x2blob: Mapping[str, Any]) -> dict[str, Any]:
    gates = x2blob.get("gates")
    tg = (
        x2blob.get("total_x2_gates")
        if isinstance(x2blob.get("total_x2_gates"), int)
        else (len(gates) if isinstance(gates, list) else 0)
    )
    failed_ids: list[str] = []
    if isinstance(x2blob.get("failed_gates"), list):
        failed_ids = [str(x) for x in x2blob["failed_gates"]]
    elif isinstance(gates, list):
        failed_ids = [str(g["gate_id"]) for g in gates if isinstance(g, dict) and g.get("pass") is False]
    xf = x2blob.get("x2_failed")
    if xf is None and isinstance(gates, list):
        xf = sum(1 for g in gates if isinstance(g, dict) and not g.get("pass"))
    xp = x2blob.get("x2_passed")
    if xp is None and isinstance(gates, list):
        xp = sum(1 for g in gates if isinstance(g, dict) and g.get("pass"))
    return {
        "x2_total": int(tg),
        "x2_passed": int(xp) if isinstance(xp, int) else 0,
        "x2_failed": int(xf) if isinstance(xf, int) else len(failed_ids),
        "failed_gate_ids": failed_ids,
    }


def summarize_x1d(x1blob: Mapping[str, Any]) -> dict[str, Any]:
    judges_raw = x1blob.get("judges")
    judges: list[dict[str, Any]] = judges_raw if isinstance(judges_raw, list) else []
    statuses: dict[str, str] = {}
    judge_scores: dict[str, Any] = {}
    judge_thresholds: dict[str, Any] = {}
    normalized_scores: dict[str, Any] = {}
    normalized_thresholds: dict[str, Any] = {}
    decisive_failures: list[str] = []
    soft_failed_judges: list[str] = []
    blocked_judges: list[str] = []
    mocked_judges: list[str] = []

    for j in judges:
        if not isinstance(j, dict):
            continue
        pk = str(j.get("provider_key") or j.get("judge_id") or "")
        st = str(j.get("provider_status") or "")
        statuses[pk or str(j.get("judge_id"))] = st
        judge_scores[pk or str(j.get("judge_id"))] = j.get("score")
        judge_thresholds[pk or str(j.get("judge_id"))] = j.get("threshold")
        normalized_scores[pk or str(j.get("judge_id"))] = j.get("normalized_score")
        normalized_thresholds[pk or str(j.get("judge_id"))] = j.get("normalized_threshold")
        if j.get("decisive_failure"):
            jid = str(j.get("judge_id") or pk)
            decisive_failures.append(jid)
        if _is_blocked_judge_row(j):
            if pk:
                blocked_judges.append(pk)
        if _is_mocked_judge_row(j):
            if pk:
                mocked_judges.append(pk)
        if _is_soft_failed_judge_row(j):
            if pk:
                soft_failed_judges.append(pk)

    blocked_judges = sorted(set(blocked_judges))
    mocked_judges = sorted(set(mocked_judges))
    soft_failed_judges = sorted(set(soft_failed_judges))

    return {
        "judge_provider_statuses": statuses,
        "judge_scores": judge_scores,
        "judge_thresholds": judge_thresholds,
        "normalized_scores": normalized_scores,
        "normalized_thresholds": normalized_thresholds,
        "decisive_failures": decisive_failures,
        "soft_failed_judges": soft_failed_judges,
        "blocked_judges": blocked_judges,
        "mocked_judges": mocked_judges,
    }


def _is_blocked_judge_row(j: Mapping[str, Any]) -> bool:
    if bool(j.get("provider_blocked")):
        return True
    st = str(j.get("provider_status") or "")
    return "BLOCKED" in st.upper()


def _is_mocked_judge_row(j: Mapping[str, Any]) -> bool:
    mode = str(j.get("evaluator_mode") or "").upper()
    if "MOCK" in mode:
        return True
    st = str(j.get("provider_status") or "").upper()
    return "MOCK" in st


def _is_soft_failed_judge_row(j: Mapping[str, Any]) -> bool:
    if j.get("pass") is True:
        return False
    if j.get("decisive_failure"):
        return False
    st = str(j.get("provider_status") or "")
    return st.startswith("MODEL_BACKED_FAIL")


def summarize_x3(x3blob: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "x3_code": x3blob.get("x3_code"),
        "authorization_scope": x3blob.get("authorization_scope"),
        "proceed_to_runtime": x3blob.get("proceed_to_runtime"),
        "pass": x3blob.get("pass"),
        "decisive_reason": x3blob.get("decisive_reason"),
        "review_reason": x3blob.get("review_reason"),
    }


def build_generator_metadata(
    *,
    provider_request: Mapping[str, Any] | None,
    l2_output: Mapping[str, Any],
    prompt_id: str,
    artifact_dir: Path,
    repo_root: Path,
) -> dict[str, Any]:
    pr = provider_request or {}
    l2ph = l2_output.get("prompt_hash")
    pr_hash = pr.get("prompt_hash")
    return {
        "generator_provider": str(pr.get("provider_requested") or "unknown"),
        "generator_model": str(pr.get("model") or l2_output.get("model") or ""),
        "prompt_id": str(l2_output.get("prompt_id") or prompt_id),
        "prompt_hash": str(l2ph or pr_hash or ""),
        "temperature": pr.get("temperature"),
        "max_tokens": pr.get("max_tokens"),
        "provider_request_ref": repo_rel(repo_root, artifact_dir / "provider_request.json"),
        "provider_response_ref": repo_rel(repo_root, artifact_dir / "provider_response.json")
        if (artifact_dir / "provider_response.json").is_file()
        else None,
    }


def _bullet_output_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_bullet_rewrite_map(l2: Mapping[str, Any], *, section_id: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    bullets = l2.get("bullets")
    if not isinstance(bullets, list):
        return [], {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    counts = {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    out: list[dict[str, Any]] = []
    for b in bullets:
        if not isinstance(b, dict):
            continue
        bid = str(b.get("bullet_id") or "")
        intensity = str(b.get("rewrite_intensity") or "").upper()
        if intensity in counts:
            counts[intensity] += 1
        text = str(b.get("bullet_text") or "")
        sf = b.get("source_fact_ids")
        if not isinstance(sf, list):
            sf = [bid] if bid else []
        protected = intensity == "LIGHT_PROTECTED"
        metrics_preserved = bool(b.get("has_metric"))
        out.append(
            {
                "bullet_id": bid,
                "rewrite_intensity": intensity,
                "protected": protected,
                "source_fact_ids": [str(x) for x in sf],
                "metrics_preserved": metrics_preserved,
                "source_bullet_hash": None,
                "output_bullet_hash": _bullet_output_hash(text),
                "output_text_ref": None,
            }
        )
    return out, counts


def build_l6_shadow_handoff_dict(
    *,
    artifact_dir: Path,
    repo_root: Path,
    section_id: str,
    prompt_id: str,
    temperature: float | None,
    max_tokens: int | None,
    runtime_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the full L6 shadow handoff JSON from artifacts on disk (dispatch tail)."""
    ad = artifact_dir.resolve()
    rr = repo_root.resolve()

    from apps_rg.runtime.spine.governed_l6_shadow_compose import (
        assert_l6_shadow_ingest_preconditions,
        build_governed_l6_handoff_envelope,
        governed_l6_shadow_enabled,
        GOVERNED_L6_SHADOW_MODE_SECTION,
    )

    assert_l6_shadow_ingest_preconditions(
        ad,
        section_id=section_id,
        runtime_payload=dict(runtime_payload) if runtime_payload is not None else None,
    )

    l2_path = ad / "l2_output.json"
    x1_path = ad / "x1d_llm_judge_outputs.json"
    x2_path = ad / "x2_gate_outputs.json"
    x3_path = ad / "x3_disposition.json"
    pr_path = ad / "provider_request.json"

    l2 = _load_json(l2_path)
    x1 = _load_json(x1_path)
    x2 = _load_json(x2_path)
    x3 = _load_json(x3_path)
    pr_blob: dict[str, Any] = {}
    if pr_path.is_file():
        pr_raw = _load_json(pr_path)
        if isinstance(pr_raw, dict):
            pr_blob = pr_raw

    if temperature is None and pr_blob.get("temperature") is not None:
        try:
            temperature = float(pr_blob["temperature"])  # type: ignore[arg-type]
        except (ValueError, TypeError):
            temperature = None
    if max_tokens is None and pr_blob.get("max_tokens") is not None:
        try:
            max_tokens = int(pr_blob["max_tokens"])  # type: ignore[arg-type]
        except (ValueError, TypeError):
            max_tokens = None

    run_id = str(l2.get("run_id") or ad.name)
    rgs = str(l2.get("runtime_generation_status") or "")

    gen_meta = build_generator_metadata(
        provider_request=pr_blob or None,
        l2_output=l2 if isinstance(l2, dict) else {},
        prompt_id=prompt_id,
        artifact_dir=ad,
        repo_root=rr,
    )
    if temperature is not None:
        gen_meta["temperature"] = temperature  # caller override wins
    if max_tokens is not None:
        gen_meta["max_tokens"] = max_tokens

    l6_pkg_path = ad / "l6_shadow_eval_package.json"
    pkt: dict[str, Any] = {
        "packet_type": L6_PACKET_TYPE,
        "packet_version": L6_PACKET_VERSION,
        "section_id": section_id,
        "run_id": run_id,
        "runtime_generation_status": rgs,
        "generated_at_utc": _iso_mtime(l2_path),
        # Bidirectional navigation vs lane runtime_proof run_manifest / latest_* pointers.
        "runtime_proof_run_dir_repo_relative": repo_rel(rr, ad),
        "l6_shadow_eval_package_repo_relative": repo_rel(rr, l6_pkg_path),
        "section_output_ref": repo_rel(rr, l2_path),
        "x1d_judge_outputs_ref": repo_rel(rr, x1_path),
        "x2_gate_outputs_ref": repo_rel(rr, x2_path),
        "x3_disposition_ref": repo_rel(rr, x3_path),
        "final_resume_assembly_ref": None,
        "docx_render_ref": None,
        "generator_metadata": gen_meta,
        "x2_summary": summarize_x2(x2 if isinstance(x2, dict) else {}),
        "x1d_summary": summarize_x1d(x1 if isinstance(x1, dict) else {}),
        "x3_summary": summarize_x3(x3 if isinstance(x3, dict) else {}),
        "human_label_required": True,
        "human_label_status": "MISSING",
        "human_label_ref": None,
        "benchmark_set_id": None,
        "calibration_status": "NOT_CALIBRATED",
        "calibration_report_ref": None,
        "recommendation_packet_ref": None,
        "promotion_allowed": False,
        "learning_mutation_performed": False,
        "runtime_approval_authority": "NONE",
        "current_run_mutation_allowed": False,
        "prompt_mutation_performed": False,
        "gate_mutation_performed": False,
        "judge_mutation_performed": False,
        "threshold_mutation_performed": False,
        # backward hints (informational — not authoritative for enforcement)
        "offline_only": True,
        "notes": (
            "L6 shadow handoff packet: evidence-only shadow eval; NO runtime promotion; NO learning mutation."
            f" Lane={section_id}."
        ),
    }

    if section_id == "unify_bullets":
        bmap, _counts_inner = build_bullet_rewrite_map(l2 if isinstance(l2, dict) else {}, section_id="unify_bullets")
        rd_from_l2 = l2.get("rewrite_distribution") if isinstance(l2.get("rewrite_distribution"), dict) else {}
        pkt["rewrite_policy_id"] = UNIFY_REWRITE_POLICY_ID
        pkt["rewrite_distribution"] = {
            "HEAVY": int(rd_from_l2.get("HEAVY", 0)),
            "MODERATE": int(rd_from_l2.get("MODERATE", 0)),
            "LIGHT_PROTECTED": int(rd_from_l2.get("LIGHT_PROTECTED", 0)),
            "total": int(rd_from_l2.get("total", 0)),
        }
        pkt["bullet_rewrite_map"] = bmap
    elif section_id == "ibm_bullets":
        bmap, _ci = build_bullet_rewrite_map(l2 if isinstance(l2, dict) else {}, section_id="ibm_bullets")
        rd_from_l2 = l2.get("rewrite_distribution") if isinstance(l2.get("rewrite_distribution"), dict) else {}
        pkt["rewrite_policy_id"] = IBM_REWRITE_POLICY_ID
        pkt["rewrite_distribution"] = {
            "HEAVY": int(rd_from_l2.get("HEAVY", 0)),
            "MODERATE": int(rd_from_l2.get("MODERATE", 0)),
            "LIGHT_PROTECTED": int(rd_from_l2.get("LIGHT_PROTECTED", 0)),
            "total": int(rd_from_l2.get("total", 0)),
        }
        pkt["bullet_rewrite_map"] = bmap

    elif section_id == "ibm_narrative":
        cap_path = ad / "compiled_prompt_artifact.json"
        comp_allowed: list[str] = []
        if cap_path.is_file():
            try:
                cj = _load_json(cap_path)
                if isinstance(cj, dict) and isinstance(cj.get("allowed_fact_ids"), list):
                    comp_allowed = [str(x) for x in cj["allowed_fact_ids"]]
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                comp_allowed = []
        l2d = l2 if isinstance(l2, dict) else {}
        nar = str(l2d.get("narrative_sentence") or "")
        nar_hash = hashlib.sha256(nar.encode("utf-8")).hexdigest()
        gates_list = x2.get("gates") if isinstance(x2, dict) else []
        focus_gate_ids = (
            "x2_claim_ledger_claim_text_non_empty",
            "x2_claim_ledger_source_fact_ids_allow_list",
            "x2_ibm_narrative_source_supported",
            "x2_ibm_narrative_ibm_only_fact_scope",
        )
        x2_claim_focus: list[dict[str, Any]] = []
        if isinstance(gates_list, list):
            for g in gates_list:
                if not isinstance(g, dict):
                    continue
                gid = str(g.get("gate_id") or "")
                if gid in focus_gate_ids or gid.startswith("x2_claim_ledger"):
                    x2_claim_focus.append(
                        {
                            "gate_id": gid,
                            "pass": g.get("pass"),
                            "observed_value": g.get("observed_value"),
                        }
                    )
        trace_ref: str | None = None
        for cand in (ad / "runtime_payload.json", ad / "prompt_selection_trace.json"):
            if cand.is_file():
                trace_ref = repo_rel(rr, cand)
                break
        x3sum = summarize_x3(x3 if isinstance(x3, dict) else {})
        pkt["ibm_narrative_shadow_learning"] = {
            "section_id": "ibm_narrative",
            "run_id": run_id,
            "trace_runtime_artifact_ref": trace_ref,
            "x3_disposition_ref": pkt.get("x3_disposition_ref"),
            "prompt_hash_ref": gen_meta.get("prompt_hash"),
            "compiled_prompt_artifact_ref": repo_rel(rr, cap_path) if cap_path.is_file() else None,
            "output_hash_narrative_sentence_sha256": nar_hash,
            "sealed_l2_output_ref": pkt.get("section_output_ref"),
            "x1d_summary_ref": pkt.get("x1d_judge_outputs_ref"),
            "x2_gate_summary": pkt.get("x2_summary"),
            "x2_claim_and_allowed_fact_gates": x2_claim_focus,
            "allowed_fact_ids_audit": comp_allowed,
            "shadow_observations": [
                "L6 shadow handoff is offline-only; no durable L4 write; no mutation of X2/X3 or runtime disposition.",
                f"runtime_generation_status={rgs!r}",
            ],
            "drift_or_gap_signals": [
                f"x3_code={x3sum.get('x3_code')}",
                "Compare claim_text gate (x2_claim_ledger_claim_text_non_empty) and allow-list gate against compiled allowed_fact_ids.",
            ],
            "future_run_recommendations": [
                "When infra allows, re-run without APPS_RG_QWEN_OFFLINE_CONTRACT_STUB for live Qwen calibration signal.",
            ],
            "promotion_request_candidate": False,
            "current_run_effect": "none",
        }
        pkt["promotion_request_candidate"] = False
        pkt["current_run_effect"] = "none"

    exhaust_path = ad / "runtime_exhaust_bundle.json"
    edr_path = ad / "exit_disposition_receipt.json"
    if governed_l6_shadow_enabled() and exhaust_path.is_file():
        exhaust_doc = _load_json(exhaust_path)
        x3_from_exhaust = ""
        if isinstance(exhaust_doc, dict):
            x3_from_exhaust = str(exhaust_doc.get("x3_code") or "")
        x3sum_final = pkt.get("x3_summary") if isinstance(pkt.get("x3_summary"), dict) else {}
        governed_env = build_governed_l6_handoff_envelope(
            section_id=section_id,
            run_id=run_id,
            mode=GOVERNED_L6_SHADOW_MODE_SECTION,
            runtime_exhaust_ref=repo_rel(rr, exhaust_path),
            exit_disposition_ref=repo_rel(rr, edr_path) if edr_path.is_file() else "",
            x3_code=x3_from_exhaust or str(x3sum_final.get("x3_code") or ""),
        )
        pkt["governed_l6_handoff_envelope"] = governed_env
        pkt["promotion_allowed"] = False
        pkt["promotion_status"] = governed_env["promotion_status"]
        from apps_rg.runtime.spine.l6_eval_before_learn_receipt import (
            build_l6_eval_before_learn_receipt,
            emit_l6_eval_before_learn_receipt,
        )

        eval_receipt = build_l6_eval_before_learn_receipt(
            section_id=section_id,
            run_id=run_id,
            governed_envelope=governed_env,
            runtime_exhaust_ref=repo_rel(rr, exhaust_path),
            exit_disposition_ref=repo_rel(rr, edr_path) if edr_path.is_file() else "",
        )
        emit_l6_eval_before_learn_receipt(ad, eval_receipt)
        pkt["l6_eval_before_learn_receipt_ref"] = "l6_eval_before_learn_receipt.json"

    return pkt


__all__ = [
    "BULLET_LANE_IDS",
    "IBM_REWRITE_POLICY_ID",
    "L6_PACKET_TYPE",
    "L6_PACKET_VERSION",
    "UNIFY_REWRITE_POLICY_ID",
    "build_generator_metadata",
    "build_l6_shadow_handoff_dict",
    "build_bullet_rewrite_map",
    "repo_rel",
    "summarize_x1d",
    "summarize_x2",
    "summarize_x3",
]
