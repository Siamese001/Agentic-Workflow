"""Immutable candidate pool + best-of publish for executive_summary judge regen (W3)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    _holistic_judge_score,
    snapshot_model_backed_judge_scores,
)
from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
    major_dimension_fail_count,
)

SCORES_FRESHNESS_CARRIED_FORWARD = "carried_forward"
SCORES_FRESHNESS_SOFT_FAILED_ONLY = "soft_failed_only"
SCORES_FRESHNESS_FULL_PANEL = "full_panel"


def _sha256_sorted_ids(ids: set[str] | list[str]) -> str:
    normalized = sorted({str(x).strip() for x in ids if str(x).strip()})
    payload = json.dumps(normalized, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical_digest_payload(fields: dict[str, Any]) -> str:
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_candidate_digest(fields: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_digest_payload(fields).encode("utf-8")).hexdigest()


def _dimension_verdicts_snapshot(x1d_judges: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for j in x1d_judges:
        if not isinstance(j, dict) or j.get("evaluator_mode") != "MODEL_BACKED":
            continue
        pk = str(j.get("provider_key") or j.get("judge_id") or "").strip()
        if not pk:
            continue
        dv = j.get("dimension_verdicts")
        if isinstance(dv, dict):
            out[pk] = dv
    return out


def _x2_gates_all_pass(x2_gates: tuple[dict[str, Any], ...] | list[dict[str, Any]]) -> bool:
    rows = [g for g in x2_gates if isinstance(g, dict)]
    return bool(rows) and not any(not bool(g.get("pass")) for g in rows)


@dataclass(frozen=True)
class CandidateSnapshot:
    """Frozen publish candidate (H-1)."""

    candidate_id: str
    resume_display_text: str
    parsed_json: dict[str, Any]
    claim_ledger: tuple[dict[str, Any], ...]
    x2_gate_outputs: tuple[dict[str, Any], ...]
    model_backed_scores_snapshot: dict[str, Any]
    dimension_verdicts_snapshot: dict[str, Any]
    source_fact_ids_digest: str
    allowed_fact_ids_digest: str
    prompt_hash: str
    provider_lane: str
    model_name: str
    run_refs: dict[str, Any]
    scores_freshness: str
    publish_eligible: bool
    raw_output: str
    candidate_digest: str

    def to_summary_row(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_digest": self.candidate_digest,
            "publish_eligible": self.publish_eligible,
            "x2_all_pass": _x2_gates_all_pass(self.x2_gate_outputs),
            "scores_freshness": self.scores_freshness,
            "model_backed_scores_snapshot": self.model_backed_scores_snapshot,
        }


def freeze_candidate_snapshot(
    *,
    candidate_id: str,
    raw_output: str,
    parsed: dict[str, Any],
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    x2_gates: list[dict[str, Any]],
    x1d_judges: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    prompt_hash: str,
    model_name: str,
    provider_lane: str = "",
    run_refs: dict[str, Any] | None = None,
    scores_freshness: str,
    publish_eligible: bool,
) -> CandidateSnapshot:
    ledger_rows = tuple(dict(r) for r in claim_ledger if isinstance(r, dict))
    x2_rows = tuple(dict(g) for g in x2_gates if isinstance(g, dict))
    source_ids: set[str] = set()
    for row in ledger_rows:
        for fid in row.get("source_fact_ids") or []:
            s = str(fid).strip()
            if s:
                source_ids.add(s)
    digest_fields = {
        "candidate_id": candidate_id,
        "resume_display_text": resume_display_text,
        "parsed_json": parsed,
        "claim_ledger": [dict(r) for r in ledger_rows],
        "x2_gate_outputs": [dict(g) for g in x2_rows],
        "model_backed_scores_snapshot": snapshot_model_backed_judge_scores(x1d_judges),
        "dimension_verdicts_snapshot": _dimension_verdicts_snapshot(x1d_judges),
        "source_fact_ids_digest": _sha256_sorted_ids(source_ids),
        "allowed_fact_ids_digest": _sha256_sorted_ids(allowed_fact_ids),
        "prompt_hash": prompt_hash,
        "provider_lane": provider_lane,
        "model_name": model_name,
        "run_refs": run_refs or {},
        "scores_freshness": scores_freshness,
        "publish_eligible": publish_eligible,
        "raw_output": raw_output,
    }
    digest = compute_candidate_digest(digest_fields)
    return CandidateSnapshot(
        candidate_id=candidate_id,
        resume_display_text=resume_display_text,
        parsed_json=dict(parsed),
        claim_ledger=ledger_rows,
        x2_gate_outputs=x2_rows,
        model_backed_scores_snapshot=digest_fields["model_backed_scores_snapshot"],
        dimension_verdicts_snapshot=digest_fields["dimension_verdicts_snapshot"],
        source_fact_ids_digest=digest_fields["source_fact_ids_digest"],
        allowed_fact_ids_digest=digest_fields["allowed_fact_ids_digest"],
        prompt_hash=prompt_hash,
        provider_lane=provider_lane,
        model_name=model_name,
        run_refs=run_refs or {},
        scores_freshness=scores_freshness,
        publish_eligible=publish_eligible,
        raw_output=raw_output,
        candidate_digest=digest,
    )


@dataclass
class PoolPublishResult:
    selected: CandidateSnapshot | None
    x1d_judges: list[dict[str, Any]]
    receipt: dict[str, Any]
    raw_output: str
    parsed: dict[str, Any]
    resume_display_text: str
    claim_ledger: list[dict[str, Any]]
    x2_gates: list[dict[str, Any]]
    coverage: dict[str, Any] | None = None


class CandidatePool:
    """Append-only pool of frozen candidates."""

    def __init__(self) -> None:
        self._entries: list[CandidateSnapshot] = []

    def add(self, snapshot: CandidateSnapshot) -> None:
        self._entries.append(snapshot)

    def entries(self) -> list[CandidateSnapshot]:
        return list(self._entries)

    def publish_eligible(self) -> list[CandidateSnapshot]:
        return [s for s in self._entries if s.publish_eligible and _x2_gates_all_pass(s.x2_gate_outputs)]


def _model_backed_judges(judges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [j for j in judges if isinstance(j, dict) and j.get("evaluator_mode") == "MODEL_BACKED"]


def publish_rank_metrics(judges: list[dict[str, Any]]) -> tuple[float, float, int]:
    """Return (min_holistic, sum_holistic, total_major_dimension_fails) for ranking."""
    scores: list[float] = []
    major_total = 0
    for j in _model_backed_judges(judges):
        hs = _holistic_judge_score(j)
        if hs is not None:
            scores.append(hs)
        major_total += major_dimension_fail_count(j)
    if not scores:
        return (-1.0, -1.0, major_total)
    return (min(scores), sum(scores), major_total)


def select_best_publish_candidate(
    ranked: list[tuple[CandidateSnapshot, list[dict[str, Any]]]],
) -> tuple[CandidateSnapshot, list[dict[str, Any]], dict[str, Any]]:
    """Argmax min holistic with tie-break: sum, fewer major fails, prefer scratch."""
    if not ranked:
        raise ValueError("no ranked candidates")

    best_snap: CandidateSnapshot | None = None
    best_judges: list[dict[str, Any]] | None = None
    best_key: tuple[float, float, int, int] | None = None
    comparison: list[dict[str, Any]] = []

    for snap, judges in ranked:
        min_s, sum_s, major = publish_rank_metrics(judges)
        scratch_bonus = 1 if snap.candidate_id == "scratch" else 0
        key = (min_s, sum_s, -major, scratch_bonus)
        comparison.append(
            {
                "candidate_id": snap.candidate_id,
                "candidate_digest": snap.candidate_digest,
                "min_holistic": min_s,
                "sum_holistic": sum_s,
                "major_dimension_fail_total": major,
                "scratch_tie_preference": scratch_bonus,
            },
        )
        if best_key is None or key > best_key:
            best_key = key
            best_snap = snap
            best_judges = judges

    assert best_snap is not None and best_judges is not None
    return best_snap, best_judges, {"rank_comparison": comparison, "winning_key": list(best_key or ())}


def finalize_pool_publish(
    pool: CandidatePool,
    *,
    artifact_dir: Any,
    write_json_fn: Callable[[Any, dict[str, Any]], None],
    rescore_full_panel: Callable[[CandidateSnapshot], tuple[list[dict[str, Any]], dict[str, Any]]],
    enrich_parsed_for_x2_fn: Callable[..., dict[str, Any]],
    build_coverage_fn: Callable[[str, list[dict[str, Any]], set[str]], dict[str, Any]],
    allowed_fact_ids: set[str],
    input_payload_hash: str,
    runtime_payload: dict[str, Any],
    write_x2_fn: Callable[[Any, list[dict[str, Any]]], None],
    write_x1d_fn: Callable[[Any, list[dict[str, Any]]], None],
    l2_output: dict[str, Any],
    scratch_anchor_resume: str,
) -> PoolPublishResult:
    """Full-panel rescore publish-eligible snapshots, argmax, rebind artifacts (H-3/H-6)."""
    from pathlib import Path
    from apps_rg.runtime.sections.executive_summary_judge_remediation import (
        all_model_backed_judges_pass,
    )

    eligible = pool.publish_eligible()
    receipt: dict[str, Any] = {
        "schema": "executive_summary_publish_integrity_v1",
        "artifact_rebind_complete": False,
        "publish_integrity_failed": False,
    }
    empty_result = PoolPublishResult(
        selected=None,
        x1d_judges=[],
        receipt=receipt,
        raw_output="",
        parsed={},
        resume_display_text="",
        claim_ledger=[],
        x2_gates=[],
    )
    if not eligible:
        receipt["skipped"] = "no_publish_eligible_candidates"
        return empty_result

    ranked: list[tuple[CandidateSnapshot, list[dict[str, Any]]]] = []
    full_panel_rows: list[dict[str, Any]] = []
    for snap in eligible:
        judges, rescore_receipt = rescore_full_panel(snap)
        ranked_snap = freeze_candidate_snapshot(
            candidate_id=snap.candidate_id,
            raw_output=snap.raw_output,
            parsed=dict(snap.parsed_json),
            resume_display_text=snap.resume_display_text,
            claim_ledger=[dict(r) for r in snap.claim_ledger],
            x2_gates=[dict(g) for g in snap.x2_gate_outputs],
            x1d_judges=judges,
            allowed_fact_ids=allowed_fact_ids,
            prompt_hash=snap.prompt_hash,
            model_name=snap.model_name,
            provider_lane=snap.provider_lane,
            run_refs=dict(snap.run_refs),
            scores_freshness=SCORES_FRESHNESS_FULL_PANEL,
            publish_eligible=True,
        )
        row = {
            "candidate_id": snap.candidate_id,
            "pre_rank_digest": snap.candidate_digest,
            "full_panel_digest": ranked_snap.candidate_digest,
            "rescore_receipt": rescore_receipt,
            "final_materialized_x2_all_pass": _x2_gates_all_pass(ranked_snap.x2_gate_outputs),
            "judge_certified": all_model_backed_judges_pass(judges),
        }
        if not row["final_materialized_x2_all_pass"]:
            row["publish_excluded_reason"] = "final_materialized_x2_failed"
            full_panel_rows.append(row)
            continue
        if not row["judge_certified"]:
            row["publish_excluded_reason"] = "full_panel_judges_not_certified"
            full_panel_rows.append(row)
            continue
        full_panel_rows.append(row)
        ranked.append((ranked_snap, judges))

    adir = Path(artifact_dir)
    if not ranked:
        receipt["skipped"] = "no_final_materialized_publish_eligible_candidates"
        receipt["full_panel_rescore"] = full_panel_rows
        write_json_fn(
            adir / "candidate_pool_summary.json",
            {
                "schema": "executive_summary_candidate_pool_summary_v1",
                "candidates": [s.to_summary_row() for s in pool.entries()],
                "publish_eligible_ids": [s.candidate_id for s in eligible],
                "full_panel_rescore": full_panel_rows,
                "publish_selected_snapshot_id": None,
                "published_candidate_digest": "",
                "publish_reason": receipt["skipped"],
                "rank": {"rank_comparison": [], "winning_key": []},
                "x2_publish_eligible": False,
                "judge_certified": False,
            },
        )
        return empty_result

    selected, selected_judges, rank_receipt = select_best_publish_candidate(ranked)
    publish_reason = "argmax_full_panel_min_holistic"
    if selected.candidate_id == "scratch":
        publish_reason = "scratch_selected"
        if len(eligible) == 1:
            publish_reason = "only_scratch_publish_eligible"
        elif str(scratch_anchor_resume or "").strip() == str(selected.resume_display_text or "").strip():
            publish_reason = "regen_regressed_or_rejected_publish_scratch"

    pool_summary = {
        "schema": "executive_summary_candidate_pool_summary_v1",
        "candidates": [s.to_summary_row() for s in pool.entries()],
        "publish_eligible_ids": [s.candidate_id for s in eligible],
        "full_panel_rescore": full_panel_rows,
        "publish_selected_snapshot_id": selected.candidate_id,
        "published_candidate_digest": selected.candidate_digest,
        "publish_reason": publish_reason,
        "rank": rank_receipt,
        "x2_publish_eligible": _x2_gates_all_pass(selected.x2_gate_outputs),
        "judge_certified": all_model_backed_judges_pass(selected_judges),
    }
    write_json_fn(adir / "candidate_pool_summary.json", pool_summary)

    claim_ledger = [dict(r) for r in selected.claim_ledger]
    resume_display_text = str(selected.resume_display_text or "")
    parsed = dict(selected.parsed_json)
    raw_output = str(selected.raw_output or "")
    x2_gates = [dict(g) for g in selected.x2_gate_outputs]
    coverage = build_coverage_fn(resume_display_text, claim_ledger, allowed_fact_ids)
    parsed_for_x2 = enrich_parsed_for_x2_fn(
        parsed,
        coverage=coverage,
        input_payload_hash=input_payload_hash,
        allowed_fact_ids=allowed_fact_ids,
        runtime_payload=runtime_payload,
    )

    (adir / "raw_model_output.txt").write_text(raw_output, encoding="utf-8")
    (adir / "resume_display_text.txt").write_text(resume_display_text + "\n", encoding="utf-8")
    write_json_fn(adir / "claim_ledger.json", claim_ledger)
    write_json_fn(adir / "text_claim_coverage.json", coverage)
    write_json_fn(adir / "parsed_output.json", {"parsed": parsed, "parse_status": "OK"})
    l2_output["resume_display_text"] = resume_display_text
    l2_output["claim_ledger"] = claim_ledger
    l2_output["text_claim_coverage"] = coverage
    write_json_fn(adir / "l2_output.json", l2_output)
    write_x2_fn(adir / "x2_gate_outputs.json", x2_gates)
    write_x1d_fn(adir, selected_judges)
    write_json_fn(
        adir / "fact_check_result.json",
        {
            "passed": not any(not g.get("pass") for g in x2_gates if isinstance(g, dict)),
            "failed_gates": [
                g.get("gate_id")
                for g in x2_gates
                if isinstance(g, dict) and not g.get("pass")
            ],
            "judge_remediation_applied": True,
            "publish_baseline": selected.candidate_id,
        },
    )

    rebound_verify = freeze_candidate_snapshot(
        candidate_id=selected.candidate_id,
        raw_output=raw_output,
        parsed=parsed,
        resume_display_text=resume_display_text,
        claim_ledger=claim_ledger,
        x2_gates=x2_gates,
        x1d_judges=selected_judges,
        allowed_fact_ids=allowed_fact_ids,
        prompt_hash=selected.prompt_hash,
        model_name=selected.model_name,
        provider_lane=selected.provider_lane,
        run_refs=dict(selected.run_refs),
        scores_freshness=SCORES_FRESHNESS_FULL_PANEL,
        publish_eligible=True,
    )
    final_digest = rebound_verify.candidate_digest
    integrity = {
        "published_candidate_digest": selected.candidate_digest,
        "final_artifact_digest_source": final_digest,
        "publish_selected_snapshot_id": selected.candidate_id,
        "artifact_rebind_complete": True,
        "publish_integrity_failed": final_digest != selected.candidate_digest,
    }
    if integrity["publish_integrity_failed"]:
        raise RuntimeError("publish_integrity_failed: digest mismatch after rebind")
    write_json_fn(adir / "publish_integrity_receipt.json", integrity)

    receipt.update(integrity)
    receipt["final_publish_baseline"] = selected.candidate_id
    receipt["publish_reason"] = publish_reason
    receipt["candidate_pool_summary_path"] = "candidate_pool_summary.json"

    return PoolPublishResult(
        selected=selected,
        x1d_judges=selected_judges,
        receipt=receipt,
        raw_output=raw_output,
        parsed=parsed,
        resume_display_text=resume_display_text,
        claim_ledger=claim_ledger,
        x2_gates=x2_gates,
        coverage=coverage,
    )


__all__ = [
    "SCORES_FRESHNESS_CARRIED_FORWARD",
    "SCORES_FRESHNESS_FULL_PANEL",
    "SCORES_FRESHNESS_SOFT_FAILED_ONLY",
    "CandidatePool",
    "CandidateSnapshot",
    "PoolPublishResult",
    "compute_candidate_digest",
    "finalize_pool_publish",
    "freeze_candidate_snapshot",
    "publish_rank_metrics",
    "select_best_publish_candidate",
]
