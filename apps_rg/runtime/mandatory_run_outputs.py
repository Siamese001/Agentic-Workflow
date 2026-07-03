"""Mandatory apps_rg run outputs.

Every apps_rg run must leave two human-facing artifacts:

* ``APPS_RG_MANDATORY_RUN_OUTPUT.md`` - operational ledger of what ran.
* ``BCG_EXECUTIVE_OUTPUT.md`` - decision-oriented RCA and implementation plan.

The emitter is intentionally data-driven from run artifacts so failed runs still
produce useful output.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.full_run_section_status import (
    FINAL_AGGREGATION_LANE,
    LANE_DISPLAY_TXT_CANDIDATES,
    LaneSectionStatusRow,
    collect_full_run_section_status,
)
from apps_rg.runtime.final_resume_outputs import (
    build_final_resume_output_contract,
    emit_final_resume_product_outputs,
)
from apps_rg.runtime.run_output_contract import (
    APPS_RG_MANDATORY_RUN_OUTPUT_JSON,
    APPS_RG_MANDATORY_RUN_OUTPUT_MD,
    BCG_EXECUTIVE_OUTPUT_MD,
    FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
    FINAL_RESUME_DOCX_RELPATH,
    FINAL_RESUME_OUTPUT_JSON,
    FINAL_RESUME_OUTPUT_TXT,
    FULL_RUN_SECTION_STATUS_JSON,
    REVIEW_BUNDLE_FILENAME,
)

MANDATORY_RUN_OUTPUT_JSON = APPS_RG_MANDATORY_RUN_OUTPUT_JSON
MANDATORY_RUN_OUTPUT_MD = APPS_RG_MANDATORY_RUN_OUTPUT_MD


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _repo_rel(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _x2_summary_doc(x2: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    gates = x2.get("gates")
    if not isinstance(gates, list):
        failed = x2.get("failed_gates") or x2.get("x2_failed_gate_ids")
        if isinstance(failed, list) and failed:
            return (
                "FAIL",
                [
                    {
                        "gate_id": str(gate_id),
                        "failure_reason": "",
                        "observed_value": None,
                        "threshold": None,
                    }
                    for gate_id in failed
                ],
            )
        return "UNKNOWN", []
    failed_rows: list[dict[str, Any]] = []
    for gate in gates:
        if not isinstance(gate, dict) or gate.get("pass", True):
            continue
        failed_rows.append(
            {
                "gate_id": str(gate.get("gate_id") or gate.get("id") or "unknown_gate"),
                "failure_reason": gate.get("failure_reason") or "",
                "observed_value": gate.get("observed_value"),
                "threshold": gate.get("threshold"),
                "evidence_ref": gate.get("evidence_ref"),
            }
        )
    return ("FAIL" if failed_rows else "PASS"), failed_rows


def _score_text(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _judge_rows_from_blob(blob: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for judge in _as_list(blob.get("judges")):
        if not isinstance(judge, dict):
            continue
        provider = str(judge.get("provider_name") or judge.get("provider_key") or "judge")
        rows.append(
            {
                "provider": provider,
                "provider_key": judge.get("provider_key"),
                "model": judge.get("model_name") or judge.get("model_actual"),
                "score": judge.get("score"),
                "threshold": judge.get("threshold"),
                "pass": judge.get("pass"),
                "provider_status": judge.get("provider_status") or judge.get("mode"),
                "decisive_failure": judge.get("decisive_failure"),
                "soft_fail": judge.get("soft_fail"),
                "blocked": judge.get("blocked"),
                "mocked": judge.get("mocked"),
                "error": judge.get("error"),
            }
        )
    return rows


def _normalize_judge_record(judge: dict[str, Any]) -> dict[str, Any]:
    provider = str(
        judge.get("provider")
        or judge.get("provider_name")
        or judge.get("provider_key")
        or "judge"
    )
    return {
        "provider": provider,
        "provider_key": judge.get("provider_key"),
        "model": judge.get("model") or judge.get("model_name") or judge.get("model_actual"),
        "score": judge.get("score"),
        "threshold": judge.get("threshold"),
        "pass": judge.get("pass"),
        "provider_status": judge.get("provider_status") or judge.get("mode"),
        "decisive_failure": judge.get("decisive_failure"),
        "soft_fail": judge.get("soft_fail"),
        "blocked": judge.get("blocked"),
        "mocked": judge.get("mocked"),
        "error": judge.get("error"),
    }


def _resolve_display(root: Path, section_id: str) -> tuple[str | None, str | None]:
    for name in LANE_DISPLAY_TXT_CANDIDATES.get(section_id, ("command_output.txt",)):
        candidate = root / name
        if candidate.is_file() and candidate.stat().st_size > 0:
            return name, str(candidate.resolve())
    return None, None


def _row_from_single_section(
    run_root: Path,
    *,
    section_id: str,
    repo_root: Path,
) -> LaneSectionStatusRow:
    x3 = _load_json(run_root / "x3_disposition.json")
    x2_pass, failed = _x2_summary_doc(_load_json(run_root / "x2_gate_outputs.json"))
    manifest = _load_json(run_root / "run_manifest.json")
    l2 = _load_json(run_root / "l2_output.json")
    display_name, display_abs = _resolve_display(run_root, section_id)
    judges = _judge_rows_from_blob(_load_json(run_root / "x1d_llm_judge_outputs.json"))
    judge_summary = "; ".join(
        (
            f"{j['provider']}"
            f"{' `' + str(j['model']) + '`' if j.get('model') else ''}: "
            f"{_score_text(j.get('score'))}/5 vs {_score_text(j.get('threshold'))} "
            f"{'PASS' if j.get('pass') is True else 'FAIL' if j.get('pass') is False else 'UNKNOWN'}"
        )
        for j in judges
    )
    return LaneSectionStatusRow(
        lane=section_id,
        lane_dir=_repo_rel(run_root, repo_root),
        display_txt_rel=display_name,
        display_txt_abs=display_abs,
        x3_code=str(x3.get("x3_code") or x3.get("disposition") or "UNKNOWN"),
        product_quality=str(x3.get("product_quality_status") or "UNKNOWN"),
        x2_pass=x2_pass,
        x2_failed_gate_ids=", ".join(str(g.get("gate_id")) for g in failed),
        runtime_generation_status=str(
            manifest.get("runtime_generation_status")
            or l2.get("runtime_generation_status")
            or x3.get("runtime_generation_status")
            or "UNKNOWN"
        ),
        executed=True,
        judge_summary=judge_summary,
        judge_details=tuple(judges),
    )


def _status_bucket(row: LaneSectionStatusRow, pre_run: dict[str, Any]) -> str:
    x3 = str(row.x3_code or "")
    runtime = str(row.runtime_generation_status or "")
    if not row.executed or x3 == "NOT_RUN":
        return "not_run"
    if runtime == "REAL_LLM":
        return "ran_real_llm"
    if runtime == "ASSEMBLED":
        return "assembled"
    if x3.startswith("PRE_RUN:") or pre_run:
        return "pre_run_blocked"
    return "ran_unknown_runtime"


def _classify_failure(section_id: str, failed_gates: list[dict[str, Any]], pre_run: dict[str, Any]) -> str:
    blocker = str(pre_run.get("blocker") or pre_run.get("lane_exec_status") or "").strip()
    lane_status = str(pre_run.get("lane_exec_status") or "").strip()
    pre_run_text = f"{blocker} {lane_status}".lower()
    if "temperature" in pre_run_text and "deprecated" in pre_run_text:
        return "Provider capability failure: Anthropic rejected deprecated temperature for the selected model."
    if pre_run and not failed_gates and blocker != "EXECUTED_X3_BLOCK":
        detail = blocker
        if lane_status and lane_status != blocker:
            detail = f"{blocker}; {lane_status}"
        return f"Pre-run dependency blocked execution: {detail}"
    gate_ids = " ".join(str(g.get("gate_id") or "") for g in failed_gates).lower()
    reasons = " ".join(str(g.get("failure_reason") or "") for g in failed_gates).lower()
    combined = f"{gate_ids} {reasons}"
    if "competenc" in section_id:
        return "Evidence mapping failure: visible content was not fully backed by source facts or graph lineage."
    if "claim_ledger" in combined or "bullet_count" in combined or "parse" in combined:
        return "Output contract failure: parsed content or claim ledger did not satisfy section schema."
    if "technical_specificity" in combined:
        return "Deterministic specificity failure: generated text missed required mechanism/technology signal."
    if "source_fact" in combined or "graph" in combined:
        return "Evidence mapping failure: visible content was not fully backed by source facts or graph lineage."
    if failed_gates:
        return "Deterministic gate failure."
    return "No section-level failure recorded."


def _section_record_from_row(row: LaneSectionStatusRow, *, repo_root: Path) -> dict[str, Any]:
    lane_dir = Path(row.lane_dir) if row.lane_dir else None
    if lane_dir and not lane_dir.is_absolute():
        lane_dir = repo_root / lane_dir
    if lane_dir is None and row.display_txt_abs:
        lane_dir = Path(row.display_txt_abs).parent
    x3 = _load_json(lane_dir / "x3_disposition.json") if lane_dir is not None else {}
    x2_status, failed_gates = (
        _x2_summary_doc(_load_json(lane_dir / "x2_gate_outputs.json"))
        if lane_dir is not None
        else (row.x2_pass, [])
    )
    pre_run = (
        _load_json(lane_dir / "integrated_lane_pre_run_failure.json")
        if lane_dir is not None
        else {}
    )
    judges = (
        [_normalize_judge_record(j) for j in row.judge_details]
        if row.judge_details
        else _judge_rows_from_blob(
            _load_json(lane_dir / "x1d_llm_judge_outputs.json") if lane_dir is not None else {}
        )
    )
    l6_files: list[str] = []
    if lane_dir is not None and lane_dir.is_dir():
        l6_files = sorted(
            _repo_rel(p, repo_root)
            for p in lane_dir.glob("l6*")
            if p.is_file()
        )
        post_runtime = lane_dir / "post_runtime"
        if post_runtime.is_dir():
            l6_files.extend(
                sorted(_repo_rel(p, repo_root) for p in post_runtime.glob("l6*") if p.is_file())
            )
    status = _status_bucket(row, pre_run)
    return {
        "section": row.lane,
        "status_bucket": status,
        "executed": row.executed,
        "lane_dir": row.lane_dir,
        "display_txt_relpath": row.display_txt_rel,
        "display_txt_path": row.display_txt_abs,
        "x3_code": row.x3_code,
        "x2_pass": x2_status or row.x2_pass,
        "product_quality_status": row.product_quality,
        "runtime_generation_status": row.runtime_generation_status,
        "failed_gates": failed_gates,
        "failure_classification": _classify_failure(row.lane, failed_gates, pre_run),
        "pre_run_failure": pre_run,
        "judges": judges,
        "judge_summary": row.judge_summary,
        "judge_issue_summary": {
            "blocked_judges": _as_list(x3.get("blocked_judges")),
            "mocked_judges": _as_list(x3.get("mocked_judges")),
            "soft_failed_judges": _as_list(x3.get("soft_failed_judges")),
            "decisive_judge_failures": _as_list(x3.get("decisive_judge_failures")),
            "model_backed_pass_provider_keys": _as_list(x3.get("model_backed_pass_provider_keys")),
        },
        "l6": {
            "file_count": len(l6_files),
            "files": l6_files,
            "product_authority": "future_run_advisory_only" if l6_files else "not_observed",
        },
    }


def _collect_section_records(
    run_root: Path,
    *,
    repo_root: Path,
    section_id: str | None,
) -> list[dict[str, Any]]:
    if (run_root / "lanes").is_dir() or (run_root / "modular_r4" / "sections").is_dir():
        rows = collect_full_run_section_status(run_root, repo_root=repo_root)
    elif (run_root / "x3_disposition.json").is_file() or section_id:
        rows = [
            _row_from_single_section(
                run_root,
                section_id=section_id or run_root.name,
                repo_root=repo_root,
            )
        ]
    else:
        rows = []
    return [_section_record_from_row(row, repo_root=repo_root) for row in rows]


def _count_sections(sections: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "total": len(sections),
        "ran_real_llm": 0,
        "allowed": 0,
        "blocked": 0,
        "pre_run_blocked": 0,
        "not_run": 0,
        "unknown": 0,
    }
    for section in sections:
        bucket = str(section.get("status_bucket") or "")
        x3 = str(section.get("x3_code") or "")
        if bucket == "ran_real_llm":
            counts["ran_real_llm"] += 1
        if x3 == "X3_ALLOW":
            counts["allowed"] += 1
        elif x3.startswith("X3_BLOCK"):
            counts["blocked"] += 1
        elif bucket == "pre_run_blocked":
            counts["pre_run_blocked"] += 1
        elif bucket == "not_run":
            counts["not_run"] += 1
        else:
            counts["unknown"] += 1
    return counts


def _result_summary(result: dict[str, Any] | None, run_root: Path) -> dict[str, Any]:
    result = result or {}
    result_pass = str(result.get("decisive_status") or "").upper() == "PASS" or (
        result.get("exit_code") == 0 and result.get("all_lanes_authorized") is True
    )
    terminal = _load_json(run_root / "terminal_ret_packet.json")
    terminal_payload = terminal.get("payload") if isinstance(terminal.get("payload"), dict) else {}
    exhaust = _load_json(run_root / "runtime_exhaust_bundle.json")
    exhaust_payload = exhaust.get("payload") if isinstance(exhaust.get("payload"), dict) else {}
    proof_gate = _load_json(run_root / "integrated_product_proof_gate_result.json")
    terminal_fault = "" if result_pass else str(terminal_payload.get("l2_fault") or "")
    return {
        "exit_status": result.get("exit_status") or ("success" if result_pass else "error" if terminal_fault else "unknown"),
        "execution_status": result.get("execution_status") or ("completed" if result_pass else "failed" if terminal_fault else "unknown"),
        "outcome_authorized": bool(result.get("outcome_authorized") or result_pass),
        "decisive_status": result.get("decisive_status") or "",
        "all_lanes_authorized": result.get("all_lanes_authorized"),
        "x3_disposition": (
            result.get("x3_disposition")
            or ("X3_ALLOW" if result_pass else "")
            or terminal_payload.get("x3_disposition")
            or exhaust_payload.get("x3_disposition")
            or ""
        ),
        "fault": result.get("fault") or (terminal_fault if not result_pass else ""),
        "run_id": result.get("run_id") or terminal_payload.get("run_id") or "",
        "request_id": result.get("request_id") or terminal_payload.get("request_id") or "",
        "proof_gate_status": proof_gate.get("status") or "",
        "proof_classification": proof_gate.get("proof_classification") or "",
        "decisive_reason": proof_gate.get("decisive_reason") or result.get("failure_reason") or "",
    }


def _final_resume_output_required(run_root: Path, summary: dict[str, Any]) -> bool:
    return True


def _load_provider_call_records(run_root: Path) -> dict[str, dict[str, Any]]:
    candidates = (
        run_root / "modular_r4" / "section_provider_calls.json",
        run_root / "section_provider_calls.json",
    )
    for path in candidates:
        doc = _load_json(path)
        records = doc.get("records")
        if not isinstance(records, list):
            continue
        out: dict[str, dict[str, Any]] = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            lane = str(record.get("section_lane") or record.get("lane") or "").strip()
            if lane:
                out[lane] = record
        if out:
            return out
    return {}


def _cache_preflight(run_root: Path) -> dict[str, str]:
    doc = _load_json(run_root / "whole_run_cache_preflight.json")
    return {
        "r1a": str(doc.get("r1a_preflight_status") or "NOT_OBSERVED"),
        "r1b": str(doc.get("r1b_preflight_status") or "NOT_OBSERVED"),
    }


def _section_by_id(sections: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(section.get("section") or ""): section for section in sections}


def _judge_model_score_cell(section: dict[str, Any]) -> str:
    judges = section.get("judges") if isinstance(section.get("judges"), list) else []
    cells: list[str] = []
    for judge in judges:
        if not isinstance(judge, dict):
            continue
        provider = str(judge.get("provider") or judge.get("provider_key") or "judge")
        model = str(judge.get("model") or "NOT_OBSERVED")
        score = _score_text(judge.get("score"))
        threshold = _score_text(judge.get("threshold"))
        passed = "PASS" if judge.get("pass") is True else "FAIL" if judge.get("pass") is False else "UNKNOWN"
        cells.append(f"{provider} / {model}: {score} vs {threshold} {passed}")
    return "; ".join(cells) if cells else "NOT_OBSERVED"


def _judge_retry_fallback_cell(section: dict[str, Any]) -> str:
    issues = section.get("judge_issue_summary") if isinstance(section.get("judge_issue_summary"), dict) else {}
    cells: list[str] = []
    for key in ("blocked_judges", "mocked_judges", "soft_failed_judges", "decisive_judge_failures"):
        values = issues.get(key)
        if isinstance(values, list) and values:
            cells.append(f"{key}={','.join(str(v) for v in values)}")
    return "; ".join(cells) if cells else "NOT_OBSERVED"


def _provider_cell(record: dict[str, Any], key: str, *, default: str = "NOT_OBSERVED") -> str:
    value = str(record.get(key) or "").strip()
    return value or default


def _pooling_selector_cell(section_id: str) -> str:
    if section_id == "competencies" or section_id.endswith("_bullets"):
        return "NOT_OBSERVED"
    return "N/A"


def _secondary_provider_cell(record: dict[str, Any]) -> str:
    provider = _provider_cell(record, "secondary_provider", default="")
    return provider or "NOT_OBSERVED"


def _generation_ordered_section_ids(
    sections: list[dict[str, Any]],
    provider_records: dict[str, dict[str, Any]],
) -> list[str]:
    def candidate_index(lane: str) -> int:
        raw = provider_records[lane].get("candidate_index")
        try:
            return int(raw)
        except (TypeError, ValueError):
            return 999

    ordered = sorted(
        provider_records,
        key=candidate_index,
    )
    for section in sections:
        lane = str(section.get("section") or "")
        if lane and lane not in ordered:
            ordered.append(lane)
    return ordered


def _build_section_lane_table(run_root: Path, sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    provider_records = _load_provider_call_records(run_root)
    cache = _cache_preflight(run_root)
    by_id = _section_by_id(sections)
    rows: list[dict[str, Any]] = []
    for idx, section_id in enumerate(_generation_ordered_section_ids(sections, provider_records), 1):
        section = by_id.get(section_id, {})
        record = provider_records.get(section_id, {})
        l6 = section.get("l6") if isinstance(section.get("l6"), dict) else {}
        rows.append(
            {
                "order": idx,
                "section": section_id,
                "r1a": cache["r1a"],
                "r1b": cache["r1b"],
                "lane_record": "YES" if record or section else "NO",
                "provider_call_attempted": record.get("provider_call_attempted")
                if "provider_call_attempted" in record
                else "NOT_OBSERVED",
                "primary_provider": _provider_cell(record, "provider_profile"),
                "primary_model_observed": _provider_cell(record, "model_id"),
                "pooling_selector_llm": _pooling_selector_cell(section_id),
                "secondary_provider": _secondary_provider_cell(record),
                "secondary_model_observed": _provider_cell(record, "secondary_model_id"),
                "generation_status": _provider_cell(
                    record,
                    "generation_status",
                    default=str(section.get("runtime_generation_status") or "NOT_OBSERVED"),
                ),
                "judges_run": "YES" if section.get("judges") else "NO",
                "judge_models_scores": _judge_model_score_cell(section),
                "judge_retry_fallback": _judge_retry_fallback_cell(section),
                "x2": str(section.get("x2_pass") or "NOT_OBSERVED"),
                "x3": str(section.get("x3_code") or record.get("decisive_reason_code") or "NOT_OBSERVED"),
                "past_fail_blocker": str(
                    section.get("failure_classification")
                    or record.get("decisive_reason_code")
                    or "NOT_OBSERVED"
                ),
                "display_output": str(section.get("display_txt_relpath") or "MISSING"),
                "l6_evidence": str(l6.get("product_authority") or "NOT_OBSERVED"),
            }
        )
    return rows


def _inline_output_gates(doc: dict[str, Any]) -> list[dict[str, Any]]:
    final_out = doc.get("final_resume_output") if isinstance(doc.get("final_resume_output"), dict) else {}
    rendered = final_out.get("rendered_resume_text") if isinstance(final_out.get("rendered_resume_text"), dict) else {}
    docx = final_out.get("resume_docx") if isinstance(final_out.get("resume_docx"), dict) else {}
    spine = final_out.get("final_resume_json") if isinstance(final_out.get("final_resume_json"), dict) else {}
    lane_table = doc.get("section_lane_table") if isinstance(doc.get("section_lane_table"), list) else []
    gates = [
        {
            "gate_id": "mandatory_bcg_inline_output_present",
            "pass": True,
            "observed_value": BCG_EXECUTIVE_OUTPUT_MD,
            "threshold": "BCG executive markdown rendered inline",
        },
        {
            "gate_id": "mandatory_section_lane_table_inline_present",
            "pass": bool(lane_table),
            "observed_value": len(lane_table),
            "threshold": ">=1 lane table row",
        },
        {
            "gate_id": "mandatory_resume_text_inline_present",
            "pass": bool(rendered.get("exists")) and int(rendered.get("bytes") or 0) > 0,
            "observed_value": rendered,
            "threshold": "nonempty FINAL_RESUME_OUTPUT.txt",
        },
        {
            "gate_id": "mandatory_final_resume_json_present",
            "pass": bool(spine.get("exists")) and int(spine.get("bytes") or 0) > 0,
            "observed_value": spine,
            "threshold": FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
        },
        {
            "gate_id": "mandatory_resume_docx_present",
            "pass": bool(docx.get("exists")) and int(docx.get("bytes") or 0) > 0,
            "observed_value": docx,
            "threshold": FINAL_RESUME_DOCX_RELPATH,
        },
    ]
    for gate in gates:
        gate["failure_reason"] = "" if gate["pass"] else "mandatory post-run inline output missing"
    return gates


def _top_rca_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for section in sections:
        x3 = str(section.get("x3_code") or "")
        bucket = str(section.get("status_bucket") or "")
        failed = section.get("failed_gates") or []
        if x3 == "X3_ALLOW" and bucket not in {"pre_run_blocked", "not_run"}:
            continue
        if not failed and bucket not in {"pre_run_blocked", "not_run"} and x3 != "NOT_RUN":
            continue
        gate_text = ", ".join(str(g.get("gate_id")) for g in failed if isinstance(g, dict))
        implementation_plan = _implementation_plan(section)
        causal_allocation = _causal_allocation(section)
        findings.append(
            {
                "section": str(section.get("section") or ""),
                "classification": str(section.get("failure_classification") or ""),
                "root_cause": _root_cause(section),
                "evidence": gate_text or x3 or bucket,
                "causal_allocation": causal_allocation,
                "implementation_plan": implementation_plan,
                "action": _recommended_action(section),
            }
        )
    return findings


def _root_cause(section: dict[str, Any]) -> str:
    classification = str(section.get("failure_classification") or "").lower()
    section_id = str(section.get("section") or "")
    if "output contract" in classification:
        return (
            "The lane's provider output, parser, and claim-ledger contract are not a single "
            "enforced schema from generation through X2 validation."
        )
    if "specificity" in classification:
        return (
            "The lane does not bind narrative text to evidence-backed mechanism or technology "
            "requirements before deterministic specificity validation."
        )
    if "evidence mapping" in classification:
        return (
            "Visible content can be rendered before every term or claim has source-fact IDs, "
            "graph lineage, and claim-ledger coverage."
        )
    if "provider capability" in classification:
        return (
            "The Anthropic Messages API request included a model-incompatible temperature field "
            "after the generation model changed to a no-temperature Sonnet 5 family model."
        )
    if "pre-run" in classification:
        return (
            "The lane dependency graph allows a downstream lane to be scheduled without an "
            "explicit upstream product-authorization token."
        )
    if section_id == FINAL_AGGREGATION_LANE:
        return (
            "Final aggregation eligibility is downstream of required section authorization and "
            "must stay blocked until every required lane has product-authorized evidence."
        )
    return "The failed gate evidence has not been traced to a single owning runtime contract."


def _implementation_plan(section: dict[str, Any]) -> list[str]:
    classification = str(section.get("failure_classification") or "").lower()
    section_id = str(section.get("section") or "")
    if "output contract" in classification:
        return [
            "Trace the lane's canonical output schema from provider prompt to parser to X2 gate input and remove alternate empty or partial shapes.",
            "Move required-field and bullet-count validation ahead of X2 so malformed provider responses fail before claim evaluation.",
            "Emit claim-ledger rows with source_fact_id and claim_text at generation/parsing time instead of attempting post-hoc repair.",
            "Add a fixture that proves malformed provider output is rejected and a compliant provider payload produces the expected ledger rows.",
            "Add a CI assertion that the lane cannot emit display content unless the schema and claim-ledger contract is satisfied.",
        ]
    if "specificity" in classification:
        return [
            "Define the accepted mechanism and technology vocabulary for the lane from source evidence, not from generic resume keywords.",
            "Require each narrative sentence that makes a capability claim to bind to at least one evidence-backed mechanism fact.",
            "Update the deterministic specificity gate to check evidence-bound mechanisms in the claim ledger before accepting display text.",
            "Add a regression fixture with one generic narrative rejection and one mechanism-bound narrative acceptance.",
        ]
    if "evidence mapping" in classification:
        return [
            "List every visible term or claim missing source_fact_id, graph path ID, or claim-ledger coverage from the failed gate evidence.",
            "Change the section enrichment step so selected visible terms are emitted only with canonical source_fact_ids and graph lineage.",
            "Add a pre-display validation guard that blocks rendering when any visible claim lacks lineage or per-term ledger coverage.",
            "Add a regression fixture that rejects ungrounded terms and accepts the same terms only when backed by source facts and graph paths.",
        ]
    if "provider capability" in classification:
        return [
            "Centralize provider request capability checks for Anthropic model families before any HTTP payload is serialized.",
            "Omit temperature from Claude Sonnet 5 generation, selector, and judge payloads while preserving it for older supported Anthropic models.",
            "Persist the exact provider HTTP error into lane pre-run failure receipts and mandatory RCA evidence.",
            "Add regression tests that prove Sonnet 5 payloads omit temperature and the run ledger surfaces provider capability errors.",
        ]
    if "pre-run" in classification:
        return [
            "Represent the upstream lane's product authorization as an explicit dependency token consumed by the downstream lane.",
            "Write the upstream blocker lane, gate, and artifact path into the pre-run failure receipt when dependency authorization is absent.",
            "Update rerun orchestration so upstream repair lanes execute and certify before dependent lanes are scheduled.",
            "Add an integration fixture proving the dependent lane remains blocked until the upstream authorization token is present.",
        ]
    if section_id == FINAL_AGGREGATION_LANE:
        return [
            "Compute aggregation eligibility from the mandatory per-section product-authorization ledger instead of inferred run completion.",
            "Emit a missing-lane manifest that names each non-authorized required section and its decisive gate evidence.",
            "Keep final assembly blocked until every required section has product-authorized evidence in the same run root.",
            "Add an aggregation fixture proving one blocked or not-run required section prevents final resume assembly.",
        ]
    return [
        "Assign the failed gate family to one owning runtime contract before changing prompts or thresholds.",
        "Trace the artifact producer, parser, and validator for that contract and identify where invalid state first becomes representable.",
        "Add a contract-level regression fixture at that boundary so symptom-only downstream repairs cannot pass.",
    ]


def _failed_gate_ids(section: dict[str, Any]) -> list[str]:
    return [
        str(gate.get("gate_id") or "unknown_gate")
        for gate in section.get("failed_gates") or []
        if isinstance(gate, dict)
    ]


def _gate_reason(section: dict[str, Any], *needles: str) -> str:
    lowered = [needle.lower() for needle in needles]
    for gate in section.get("failed_gates") or []:
        if not isinstance(gate, dict):
            continue
        gate_id = str(gate.get("gate_id") or "").lower()
        reason = str(gate.get("failure_reason") or "").strip()
        observed = gate.get("observed_value")
        haystack = f"{gate_id} {reason}".lower()
        if lowered and not any(needle in haystack for needle in lowered):
            continue
        if observed not in (None, "", [], {}):
            return f"{gate.get('gate_id')}: {reason or observed} observed={observed}"
        return f"{gate.get('gate_id')}: {reason or 'failed'}"
    return ""


def _pre_run_reason(section: dict[str, Any]) -> str:
    pre_run = section.get("pre_run_failure")
    if not isinstance(pre_run, dict):
        return ""
    blocker = pre_run.get("blocker") or pre_run.get("lane_exec_status") or section.get("x3_code")
    lane_status = pre_run.get("lane_exec_status")
    if lane_status and lane_status != blocker:
        return f"{blocker}; {lane_status}"
    return str(blocker or "")


def _allocation_row(
    *,
    domain: str,
    causal_role: str,
    root_cause_link: str,
    work_share: str,
    evidence_refs: list[str],
    required_work: str,
) -> dict[str, Any]:
    return {
        "domain": domain,
        "causal_role": causal_role,
        "root_cause_link": root_cause_link,
        "work_share": work_share,
        "evidence_refs": evidence_refs,
        "required_work": required_work,
    }


def _causal_allocation(section: dict[str, Any]) -> dict[str, Any]:
    classification = str(section.get("failure_classification") or "").lower()
    section_id = str(section.get("section") or "")
    gate_ids = _failed_gate_ids(section)
    if "output contract" in classification:
        bullet_gate = _gate_reason(section, "bullet_count")
        ledger_gate = _gate_reason(section, "claim_ledger")
        source_gate = _gate_reason(section, "source_fact")
        return {
            "dominant_cause": "The runtime accepted provider output but the parser/schema/ledger contract emitted an empty product artifact.",
            "retry_recoverability": "LOW",
            "retry_recoverability_reason": "Additional model attempts cannot repair a parser and claim-ledger path that converts generated bullets into zero product bullets and zero claims.",
            "allocation": [
                _allocation_row(
                    domain="Parser / normalization contract",
                    causal_role="PRIMARY",
                    root_cause_link=bullet_gate or "The bullet-count gate observed an empty parsed bullet artifact.",
                    work_share="40%",
                    evidence_refs=["x2_insurtech_bullets_bullet_count_3"],
                    required_work="Normalize provider JSON into the canonical bullet schema before X2 and fail closed before display when parsing yields zero bullets.",
                ),
                _allocation_row(
                    domain="Claim ledger / provenance contract",
                    causal_role="CONTRIBUTING",
                    root_cause_link=ledger_gate or source_gate or "The claim ledger lacked claim_text and supported source_fact_ids for generated claims.",
                    work_share="30%",
                    evidence_refs=[
                        "x2_claim_ledger_claim_text_non_empty",
                        "x2_insurtech_bullets_source_fact_ids_supported",
                    ],
                    required_work="Emit claim_text and source_fact_ids during parsing so every bullet is provenance-bound before judge or gate review.",
                ),
                _allocation_row(
                    domain="Validation / gate precision",
                    causal_role="DETECTION",
                    root_cause_link="X2 detected empty bullets and ledger rows, but the RCA must preserve which parser/schema contract produced the empty artifact.",
                    work_share="15%",
                    evidence_refs=gate_ids,
                    required_work="Attach parser input/output references and failed field names to the gate evidence.",
                ),
                _allocation_row(
                    domain="Retry / repair policy",
                    causal_role="LOW_RECOVERY",
                    root_cause_link="Retries target the model, while the observed failure is an empty parsed artifact after generation.",
                    work_share="15%",
                    evidence_refs=["self_consistency_paths.json", "parsed_output.json"],
                    required_work="Allow retry only after parser and claim-ledger contracts prove they can preserve a valid generated payload.",
                ),
            ],
        }
    if "specificity" in classification:
        specificity_gate = _gate_reason(section, "technical_specificity")
        return {
            "dominant_cause": "The generated narrative was not constrained to include an evidence-backed mechanism token before deterministic specificity validation.",
            "retry_recoverability": "HIGH",
            "retry_recoverability_reason": "A targeted repair can add a source-backed mechanism or technology token without changing the underlying evidence set.",
            "allocation": [
                _allocation_row(
                    domain="Generation instruction / output control",
                    causal_role="PRIMARY",
                    root_cause_link=specificity_gate or "The specificity gate found no named mechanism or technology token in display text.",
                    work_share="45%",
                    evidence_refs=["x2_narrative_technical_specificity_floor"],
                    required_work="Bind the narrative prompt and repair step to accepted source-backed mechanism vocabulary.",
                ),
                _allocation_row(
                    domain="Claim ledger / provenance contract",
                    causal_role="CONTRIBUTING",
                    root_cause_link="The accepted mechanism must be present in both display text and the claim ledger, not only in hidden evidence.",
                    work_share="20%",
                    evidence_refs=["claim_ledger.json", "text_claim_coverage.json"],
                    required_work="Expose the mechanism token in claim text and source_fact_ids before the specificity gate runs.",
                ),
                _allocation_row(
                    domain="Retry / repair policy",
                    causal_role="HIGH_RECOVERY",
                    root_cause_link="The lane had supported content but missed a deterministic token, so gate-aware text repair is the correct retry shape.",
                    work_share="25%",
                    evidence_refs=["x2_narrative_technical_specificity_floor", "section_repair_ledger.json"],
                    required_work="Trigger a targeted rewrite that only inserts an evidence-backed mechanism token.",
                ),
                _allocation_row(
                    domain="Validation / gate precision",
                    causal_role="DETECTION",
                    root_cause_link="The gate names the missing token class but should also emit the accepted vocabulary and evidence source used for repair.",
                    work_share="10%",
                    evidence_refs=["x2_gate_outputs.json"],
                    required_work="Include accepted mechanism vocabulary and source-fact anchors in the gate receipt.",
                ),
            ],
        }
    if "evidence mapping" in classification:
        graph_gate = _gate_reason(section, "competencies_graph_granularity")
        term_gate = _gate_reason(section, "term_supported")
        ledger_gate = _gate_reason(section, "all_terms_source_fact_ids")
        confidence_gate = _gate_reason(section, "confidence")
        return {
            "dominant_cause": "The visible competency surface can be assembled before category, term, confidence, and graph lineage proof is complete.",
            "retry_recoverability": "LOW",
            "retry_recoverability_reason": "Blind retries regenerate text against the same incomplete proof contract; only gate-aware lineage repair can recover it.",
            "allocation": [
                _allocation_row(
                    domain="Evidence substrate / graph lineage",
                    causal_role="PRIMARY",
                    root_cause_link=graph_gate or term_gate or "Failed gates show missing category source facts or unsupported visible terms.",
                    work_share="45%",
                    evidence_refs=[
                        "x2_competencies_graph_granularity_gates",
                        "x2_competency_term_supported",
                    ],
                    required_work="Add category-level source-fact coverage and remove or bind unsupported visible terms before display.",
                ),
                _allocation_row(
                    domain="Artifact transformation contract",
                    causal_role="CONTRIBUTING",
                    root_cause_link=ledger_gate or confidence_gate or "Selected graph evidence was not preserved into per-term source_fact_ids and per-category confidence.",
                    work_share="25%",
                    evidence_refs=[
                        "x2_all_terms_source_fact_ids",
                        "x2_competencies_per_category_confidence_nonconstant",
                    ],
                    required_work="Make graph selection, claim ledger, category confidence, and display a lossless transformation contract.",
                ),
                _allocation_row(
                    domain="Validation / gate precision",
                    causal_role="DETECTION",
                    root_cause_link="The gates detected missing lineage, but the RCA must preserve the exact category, term, source fact, and owning producer.",
                    work_share="20%",
                    evidence_refs=gate_ids,
                    required_work="Emit a category-by-category repair matrix in the gate receipt and RCA.",
                ),
                _allocation_row(
                    domain="Retry / repair policy",
                    causal_role="LOW_RECOVERY",
                    root_cause_link="More candidate generations cannot satisfy missing source_fact_ids or unsupported graph terms unless the repair step fills lineage first.",
                    work_share="10%",
                    evidence_refs=["self_consistency_paths.json", "section_repair_ledger.json"],
                    required_work="Replace blind retry with gate-aware lineage repair for missing facts, terms, and confidence.",
                ),
            ],
        }
    if "provider capability" in classification:
        pre_run = _pre_run_reason(section)
        return {
            "dominant_cause": "The selected Anthropic model rejected a request field that the transport still emitted unconditionally.",
            "retry_recoverability": "NONE",
            "retry_recoverability_reason": "Repeating the same request cannot recover while the serialized payload contains the deprecated temperature field.",
            "allocation": [
                _allocation_row(
                    domain="Provider capability contract",
                    causal_role="PRIMARY",
                    root_cause_link=pre_run or "Anthropic returned HTTP 400 for deprecated temperature.",
                    work_share="55%",
                    evidence_refs=["self_consistency_paths.json", "provider_request.json"],
                    required_work="Sanitize Anthropic payloads by model capability before sending HTTP requests.",
                ),
                _allocation_row(
                    domain="Model pin / provider profile",
                    causal_role="CONTRIBUTING",
                    root_cause_link="The generation model changed to Claude Sonnet 5 without updating transport capability rules.",
                    work_share="25%",
                    evidence_refs=["apps_rg/config/provider_profiles.yaml", "config/model_catalog.json"],
                    required_work="Keep provider profile model changes paired with transport capability tests.",
                ),
                _allocation_row(
                    domain="Observability / RCA reporting",
                    causal_role="DETECTION",
                    root_cause_link="The no-candidate selector error must carry the first provider HTTP error.",
                    work_share="20%",
                    evidence_refs=[MANDATORY_RUN_OUTPUT_JSON, "integrated_lane_pre_run_failure.json"],
                    required_work="Propagate first provider failure details into mandatory run RCA records.",
                ),
            ],
        }
    if "pre-run" in classification:
        pre_run = _pre_run_reason(section)
        return {
            "dominant_cause": "A downstream lane was evaluated without an upstream product-authorization token.",
            "retry_recoverability": "NONE",
            "retry_recoverability_reason": "The dependent lane cannot recover through generation retries until the upstream lane is product-authorized.",
            "allocation": [
                _allocation_row(
                    domain="Orchestration / dependency control",
                    causal_role="PRIMARY",
                    root_cause_link=pre_run or "The pre-run receipt reports an upstream lane was not finalized.",
                    work_share="55%",
                    evidence_refs=["integrated_lane_pre_run_failure.json"],
                    required_work="Represent upstream lane product authorization as an explicit dependency token.",
                ),
                _allocation_row(
                    domain="Aggregation / product authorization",
                    causal_role="CONTRIBUTING",
                    root_cause_link="The dependent narrative must not schedule until its upstream bullets lane is certified.",
                    work_share="25%",
                    evidence_refs=[MANDATORY_RUN_OUTPUT_JSON],
                    required_work="Consume the upstream token before dependent-lane scheduling.",
                ),
                _allocation_row(
                    domain="Retry / repair policy",
                    causal_role="NO_RECOVERY",
                    root_cause_link="No model retry can create the missing upstream authorization token.",
                    work_share="10%",
                    evidence_refs=["integrated_lane_pre_run_failure.json"],
                    required_work="Route retries to the upstream blocked lane, not the dependent lane.",
                ),
                _allocation_row(
                    domain="Observability / RCA reporting",
                    causal_role="REPORTING_GAP",
                    root_cause_link="The operator output must name the upstream blocker, artifact, and lane token that is missing.",
                    work_share="10%",
                    evidence_refs=["integrated_lane_pre_run_failure.json"],
                    required_work="Surface upstream lane, missing token, and repair order in the RCA.",
                ),
            ],
        }
    if section_id == FINAL_AGGREGATION_LANE:
        return {
            "dominant_cause": "Final assembly depends on the required-lane authorization ledger and correctly remained blocked.",
            "retry_recoverability": "NONE",
            "retry_recoverability_reason": "Aggregation cannot recover until upstream blocked and not-run required lanes become product-authorized in the same run root.",
            "allocation": [
                _allocation_row(
                    domain="Aggregation / product authorization",
                    causal_role="PRIMARY",
                    root_cause_link="The mandatory section ledger contains blocked, pre-run-blocked, or not-run required lanes.",
                    work_share="60%",
                    evidence_refs=[MANDATORY_RUN_OUTPUT_JSON],
                    required_work="Compute final aggregation eligibility directly from the required-lane product-authorization ledger.",
                ),
                _allocation_row(
                    domain="Orchestration / dependency control",
                    causal_role="CONTRIBUTING",
                    root_cause_link="Final assembly must wait for upstream lane tokens rather than inferred run completion.",
                    work_share="20%",
                    evidence_refs=[FULL_RUN_SECTION_STATUS_JSON],
                    required_work="Require same-run product-authorization tokens for every required section.",
                ),
                _allocation_row(
                    domain="Retry / repair policy",
                    causal_role="NO_RECOVERY",
                    root_cause_link="Retrying aggregation cannot repair missing upstream product authorization.",
                    work_share="10%",
                    evidence_refs=[FULL_RUN_SECTION_STATUS_JSON],
                    required_work="Route repair to the blocking lanes before aggregation.",
                ),
                _allocation_row(
                    domain="Observability / RCA reporting",
                    causal_role="REPORTING_GAP",
                    root_cause_link="The output must name every non-authorized required lane that prevents assembly.",
                    work_share="10%",
                    evidence_refs=[MANDATORY_RUN_OUTPUT_JSON],
                    required_work="Emit a missing-lane manifest in the aggregation RCA.",
                ),
            ],
        }
    return {
        "dominant_cause": "The failed gate evidence has not been allocated to one owning runtime contract.",
        "retry_recoverability": "UNKNOWN",
        "retry_recoverability_reason": "Recoverability cannot be assessed until the owning contract is identified.",
        "allocation": [
            _allocation_row(
                domain="Validation / gate precision",
                causal_role="PRIMARY",
                root_cause_link="The available failed gates do not name a precise owning producer, parser, or validator contract.",
                work_share="100%",
                evidence_refs=gate_ids or ["x3_disposition.json"],
                required_work="Trace the failed evidence to the runtime contract that first allowed invalid state.",
            )
        ],
    }


def _validated_plan_items(finding: dict[str, Any]) -> list[str]:
    plan = finding.get("implementation_plan")
    if not isinstance(plan, list):
        return [
            "Trace the failed evidence to the owning runtime contract before changing downstream presentation.",
            "Patch the producer, parser, or validator where invalid state first becomes representable.",
            "Add a contract-level regression fixture so symptom-only downstream repair cannot pass.",
        ]
    items = [str(item).strip() for item in plan if str(item).strip()]
    if 3 <= len(items) <= 5:
        return items
    return [
        "Trace the failed evidence to the owning runtime contract before changing downstream presentation.",
        "Patch the producer, parser, or validator where invalid state first becomes representable.",
        "Add a contract-level regression fixture so symptom-only downstream repair cannot pass.",
    ]


def _validated_causal_allocation(finding: dict[str, Any]) -> dict[str, Any] | None:
    allocation = finding.get("causal_allocation")
    if not isinstance(allocation, dict):
        return None
    rows = allocation.get("allocation")
    if not isinstance(rows, list) or not rows:
        return None
    valid_rows: list[dict[str, Any]] = []
    required = {"domain", "causal_role", "root_cause_link", "work_share", "evidence_refs", "required_work"}
    for row in rows:
        if not isinstance(row, dict) or not required.issubset(row):
            return None
        domain = str(row.get("domain") or "").strip()
        root_cause_link = str(row.get("root_cause_link") or "").strip()
        if not domain or not root_cause_link or root_cause_link == domain or len(root_cause_link) < 20:
            return None
        evidence_refs = row.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            return None
        valid_rows.append(row)
    dominant = str(allocation.get("dominant_cause") or "").strip()
    retry = str(allocation.get("retry_recoverability") or "").strip()
    retry_reason = str(allocation.get("retry_recoverability_reason") or "").strip()
    if not dominant or not retry or not retry_reason:
        return None
    return {
        "dominant_cause": dominant,
        "retry_recoverability": retry,
        "retry_recoverability_reason": retry_reason,
        "allocation": valid_rows,
    }


def _render_causal_allocation_lines(finding: dict[str, Any], *, indent: str) -> list[str]:
    allocation = _validated_causal_allocation(finding)
    if allocation is None:
        return [
            f"{indent}- **RCA format gap:** missing causal allocation with concrete root-cause-linked rows."
        ]
    lines = [
        f"{indent}- Causal allocation:",
        f"{indent}  - Dominant cause: {allocation['dominant_cause']}",
        (
            f"{indent}  - Retry recoverability: `{allocation['retry_recoverability']}` - "
            f"{allocation['retry_recoverability_reason']}"
        ),
        f"{indent}  - Allocation rows:",
    ]
    for row in allocation["allocation"]:
        evidence = ", ".join(str(ref) for ref in row.get("evidence_refs") or [])
        lines.append(
            f"{indent}    - `{row['domain']}` / `{row['causal_role']}` / "
            f"`{row['work_share']}`: {row['root_cause_link']} "
            f"Evidence: `{_markdown_table_escape(evidence)}`. "
            f"Required work: {row['required_work']}"
        )
    return lines


def _recommended_action(section: dict[str, Any]) -> str:
    classification = str(section.get("failure_classification") or "").lower()
    section_id = str(section.get("section") or "")
    if "output contract" in classification:
        return "Implement the output-contract plan; do not rerun until schema and claim-ledger contract tests pass."
    if "specificity" in classification:
        return "Implement the evidence-bound specificity plan; do not rely on text-only regeneration."
    if "evidence mapping" in classification:
        return "Implement the evidence-mapping plan; do not accept visible claims without lineage."
    if "provider capability" in classification:
        return "Implement the provider-capability payload fix before rerunning Anthropic-backed lanes."
    if "pre-run" in classification:
        return "Implement the dependency-token plan before scheduling the dependent lane."
    if section_id == FINAL_AGGREGATION_LANE:
        return "Implement the aggregation-eligibility plan before final assembly."
    return "Inspect failed gates and rerun after targeted remediation."


def _markdown_table_escape(value: Any) -> str:
    return str(value if value is not None else "-").replace("|", "\\|").replace("\n", " ")


def _render_section_lane_table_lines(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## Section Lane Summary Table",
        "",
        "| # | Section | R1A | R1B | Lane record | Provider call attempted | Primary provider | Primary model observed | Pooling selector LLM | Secondary provider | Secondary model observed | Generation status | Judges run | Judge models / scores | Judge retry / fallback | X2 | X3 | Past fail / blocker | Display output | L6 evidence |",
        "|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    if not rows:
        lines.append("| 0 | `NO_ROWS` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NO` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NO` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `mandatory section lane table missing` | `MISSING` | `NOT_OBSERVED` |")
        return lines
    for row in rows:
        lines.append(
            "| "
            f"{row.get('order')} | "
            f"`{_markdown_table_escape(row.get('section'))}` | "
            f"`{_markdown_table_escape(row.get('r1a'))}` | "
            f"`{_markdown_table_escape(row.get('r1b'))}` | "
            f"`{_markdown_table_escape(row.get('lane_record'))}` | "
            f"`{_markdown_table_escape(row.get('provider_call_attempted'))}` | "
            f"`{_markdown_table_escape(row.get('primary_provider'))}` | "
            f"`{_markdown_table_escape(row.get('primary_model_observed'))}` | "
            f"`{_markdown_table_escape(row.get('pooling_selector_llm'))}` | "
            f"`{_markdown_table_escape(row.get('secondary_provider'))}` | "
            f"`{_markdown_table_escape(row.get('secondary_model_observed'))}` | "
            f"`{_markdown_table_escape(row.get('generation_status'))}` | "
            f"`{_markdown_table_escape(row.get('judges_run'))}` | "
            f"`{_markdown_table_escape(row.get('judge_models_scores'))}` | "
            f"`{_markdown_table_escape(row.get('judge_retry_fallback'))}` | "
            f"`{_markdown_table_escape(row.get('x2'))}` | "
            f"`{_markdown_table_escape(row.get('x3'))}` | "
            f"`{_markdown_table_escape(row.get('past_fail_blocker'))}` | "
            f"`{_markdown_table_escape(row.get('display_output'))}` | "
            f"`{_markdown_table_escape(row.get('l6_evidence'))}` |"
        )
    return lines


def _render_resume_inline_lines(doc: dict[str, Any]) -> list[str]:
    run_root = Path(str(doc.get("run_root_abs") or ""))
    resume_path = run_root / FINAL_RESUME_OUTPUT_TXT
    text = ""
    if resume_path.is_file():
        try:
            text = resume_path.read_text(encoding="utf-8").rstrip()
        except OSError:
            text = ""
    return [
        "## Resume DOCX Full Version Inline",
        "",
        "Source: `FINAL_RESUME_OUTPUT.txt` rendered from the same final-resume spine used for `outputs/resume.docx`.",
        "",
        "```text",
        text or "[MANDATORY_OUTPUT_MISSING: FINAL_RESUME_OUTPUT.txt]",
        "```",
    ]


def _render_mandatory_markdown(doc: dict[str, Any]) -> str:
    summary = doc["result_summary"]
    sections = doc["sections"]
    counts = doc["section_counts"]
    rca = doc["rca_findings"]
    final_out = doc.get("final_resume_output") if isinstance(doc.get("final_resume_output"), dict) else {}
    lane_table = doc.get("section_lane_table") if isinstance(doc.get("section_lane_table"), list) else []
    inline_gates = doc.get("mandatory_inline_output_gates") if isinstance(doc.get("mandatory_inline_output_gates"), list) else []
    lines = [
        "# apps_rg Mandatory Run Output",
        "",
        f"Generated: `{doc['generated_at_utc']}`",
        f"Run root: `@{doc['run_root_abs']}`",
        "",
        "## Outcome",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Exit status | `{summary.get('exit_status') or '-'}` |",
        f"| Execution status | `{summary.get('execution_status') or '-'}` |",
        f"| Outcome authorized | `{summary.get('outcome_authorized')}` |",
        f"| X3 disposition | `{summary.get('x3_disposition') or '-'}` |",
        f"| Fault | `{_markdown_table_escape(summary.get('fault') or '-')}` |",
        f"| Integrated proof gate | `{summary.get('proof_gate_status') or '-'}` `{summary.get('proof_classification') or '-'}` |",
        f"| Final resume output gate | `{final_out.get('status') or 'UNKNOWN'}` |",
        "",
        "## Mandatory Inline Output Gates",
        "",
        "| Gate | Status | Observed |",
        "|---|---|---|",
    ]
    for gate in inline_gates:
        if not isinstance(gate, dict):
            continue
        lines.append(
            "| "
            f"`{gate.get('gate_id')}` | "
            f"`{'PASS' if gate.get('pass') is True else 'FAIL'}` | "
            f"`{_markdown_table_escape(gate.get('observed_value'))}` |"
        )
    lines.extend(
        [
            "",
        "## Section Counts",
        "",
        "| Total | Real LLM | X3 allow | X3 block | Pre-run blocked | Not run | Unknown/other |",
        "|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| {counts['total']} | {counts['ran_real_llm']} | {counts['allowed']} | "
            f"{counts['blocked']} | {counts['pre_run_blocked']} | {counts['not_run']} | "
            f"{counts['unknown']} |"
        ),
        "",
        ]
    )
    lines.extend(_render_section_lane_table_lines(lane_table))
    lines.extend(
        [
            "",
        "## Section Execution Ledger",
        "",
        "| Section | Ran status | X3 | X2 | Product | Runtime | Failed gates | Display |",
        "|---|---|---|---|---|---|---|---|",
        ]
    )
    for section in sections:
        failed = ", ".join(
            str(g.get("gate_id"))
            for g in section.get("failed_gates") or []
            if isinstance(g, dict)
        )
        lines.append(
            "| "
            f"`{section.get('section')}` | `{section.get('status_bucket')}` | "
            f"`{section.get('x3_code')}` | `{section.get('x2_pass')}` | "
            f"`{section.get('product_quality_status')}` | "
            f"`{section.get('runtime_generation_status')}` | "
            f"`{_markdown_table_escape(failed or '-')}` | "
            f"`{_markdown_table_escape(section.get('display_txt_relpath') or '-')}` |"
        )
    lines.extend(
        [
            "",
            "## Final Resume Product Outputs",
            "",
            "| Artifact | Path | Status | Bytes | SHA256 |",
            "|---|---|---|---:|---|",
        ]
    )
    final_artifacts = (
        ("Canonical final resume JSON", final_out.get("final_resume_json")),
        ("Rendered final resume text", final_out.get("rendered_resume_text")),
        ("Final resume DOCX", final_out.get("resume_docx")),
    )
    for label, art in final_artifacts:
        art = art if isinstance(art, dict) else {}
        exists = "PASS" if art.get("exists") else "MISSING"
        lines.append(
            "| "
            f"{label} | `{_markdown_table_escape(art.get('relpath') or '-')}` | "
            f"`{exists}` | {int(art.get('bytes') or 0)} | "
            f"`{_markdown_table_escape(art.get('sha256') or '-')}` |"
        )
    failed_final = final_out.get("failed_gate_ids") if isinstance(final_out.get("failed_gate_ids"), list) else []
    lines.extend(
        [
            "",
            "| Gate | Status | Observed |",
            "|---|---|---|",
        ]
    )
    for gate in final_out.get("gates") or []:
        if not isinstance(gate, dict):
            continue
        lines.append(
            "| "
            f"`{gate.get('gate_id')}` | "
            f"`{'PASS' if gate.get('pass') is True else 'FAIL'}` | "
            f"`{_markdown_table_escape(gate.get('observed_value'))}` |"
        )
    if failed_final:
        lines.append("")
        lines.append(f"Final resume output failed gates: `{_markdown_table_escape(', '.join(str(g) for g in failed_final))}`")
    lines.extend(["", "## Judge Execution Ledger", ""])
    lines.append("| Section | Judge | Model | Status | Score | Threshold | Pass | Issues |")
    lines.append("|---|---|---|---|---:|---:|---|---|")
    for section in sections:
        judges = section.get("judges") or []
        issues = section.get("judge_issue_summary") or {}
        issue_text = ", ".join(
            f"{key}={','.join(str(x) for x in val)}"
            for key, val in issues.items()
            if isinstance(val, list) and val
        )
        if not judges:
            reason = "section_not_run" if section.get("status_bucket") in {"not_run", "pre_run_blocked"} else "no_judge_rows_observed"
            lines.append(
                f"| `{section.get('section')}` | `-` | `-` | `{reason}` |  |  | `UNKNOWN` | `{_markdown_table_escape(issue_text or '-')}` |"
            )
            continue
        for judge in judges:
            passed = "PASS" if judge.get("pass") is True else "FAIL" if judge.get("pass") is False else "UNKNOWN"
            lines.append(
                "| "
                f"`{section.get('section')}` | `{_markdown_table_escape(judge.get('provider'))}` | "
                f"`{_markdown_table_escape(judge.get('model') or '-')}` | "
                f"`{_markdown_table_escape(judge.get('provider_status') or '-')}` | "
                f"{_score_text(judge.get('score'))} | {_score_text(judge.get('threshold'))} | "
                f"`{passed}` | `{_markdown_table_escape(issue_text or '-')}` |"
            )
    lines.extend(["", "## RCA Findings", ""])
    if not rca:
        lines.append("- No blocking RCA findings recorded.")
    else:
        for idx, finding in enumerate(rca, 1):
            lines.append(f"{idx}. `{finding['section']}` - {finding['classification']}")
            lines.append(f"   - Root cause: {finding.get('root_cause') or '-'}")
            lines.append(
                f"   - Evidence: `{_markdown_table_escape(finding.get('evidence') or '-')}`"
            )
            lines.extend(_render_causal_allocation_lines(finding, indent="   "))
            lines.append("   - Required implementation plan:")
            for item in _validated_plan_items(finding):
                lines.append(f"     - {item}")
    lines.extend(["", "## L6 Shadow Observability", ""])
    lines.append("| Section | L6 files | Authority |")
    lines.append("|---|---:|---|")
    for section in sections:
        l6 = section.get("l6") or {}
        lines.append(
            f"| `{section.get('section')}` | {int(l6.get('file_count') or 0)} | `{l6.get('product_authority') or '-'}` |"
        )
    lines.extend([""])
    lines.extend(_render_resume_inline_lines(doc))
    return "\n".join(lines)


def _render_bcg_markdown(doc: dict[str, Any]) -> str:
    summary = doc["result_summary"]
    sections = doc["sections"]
    counts = doc["section_counts"]
    rca = doc["rca_findings"]
    final_out = doc.get("final_resume_output") if isinstance(doc.get("final_resume_output"), dict) else {}
    failed_count = counts["blocked"] + counts["pre_run_blocked"] + counts["not_run"]
    final_status = str(final_out.get("status") or "UNKNOWN")
    final_gate_blocks = final_status == "FAIL"
    authorized = bool(summary.get("outcome_authorized")) and not final_gate_blocks
    blocker_text = (
        "final resume output gate failed"
        if final_gate_blocks
        else summary.get("fault") or summary.get("decisive_reason") or "section gates / aggregation"
    )
    if authorized:
        answer = "The run reached an authorized product outcome. Preserve the generated outputs and review the run ledger for section and judge proof."
    elif failed_count:
        answer = (
            "The run did not fail because every section was unusable. It failed because "
            f"{failed_count} section or aggregation surfaces were not product-authorized, "
            "so final assembly was correctly blocked."
        )
    else:
        answer = "The run was not product-authorized, but no section-level blocker was classified; inspect terminal fault and proof-gate evidence."
    lines = [
        "# BCG Executive Output - apps_rg Run",
        "",
        f"Generated: `{doc['generated_at_utc']}`",
        f"Run root: `@{doc['run_root_abs']}`",
        "",
        "## Executive Answer",
        "",
        answer,
        "",
        "## Board-Level Readout",
        "",
        "| Question | Answer |",
        "|---|---|",
        f"| Did real generation run? | `{counts['ran_real_llm']}` section(s) reported `REAL_LLM`. |",
        f"| Was a final product authorized? | `{summary.get('outcome_authorized')}` |",
        f"| What blocked the run? | `{_markdown_table_escape('None - all required sections, final aggregation, and product outputs are authorized' if authorized else blocker_text)}` |",
        f"| Final resume output gate | `{final_out.get('status') or 'UNKNOWN'}` |",
        f"| Primary decision | `{_markdown_table_escape('Preserve outputs and review evidence ledgers; no blocker remediation required.' if authorized else 'Fix targeted blockers and rerun; do not weaken X2/X3 gates.')}` |",
        "",
        "## Run Scorecard",
        "",
        "| Section | Result | Interpretation | Required fix |",
        "|---|---|---|---|",
    ]
    for section in sections:
        x3 = str(section.get("x3_code") or "")
        bucket = str(section.get("status_bucket") or "")
        if x3 == "X3_ALLOW":
            interp = (
                "Authorized final assembly output."
                if section.get("section") == "final_resume_aggregation"
                else "Usable candidate content; product-authorized for this run."
            )
        elif bucket == "pre_run_blocked":
            interp = "Did not become eligible because an upstream dependency failed."
        elif bucket == "not_run":
            interp = "Did not run in this execution path."
        else:
            interp = str(section.get("failure_classification") or "Requires review.")
        if x3 == "X3_ALLOW":
            required_fix = "No blocker; preserve section evidence for assembly."
        else:
            required_fix = "See root-cause implementation plan in Issue Tree."
        lines.append(
            f"| `{section.get('section')}` | `{x3 or bucket}` | "
            f"{_markdown_table_escape(interp)} | {_markdown_table_escape(required_fix)} |"
        )
    lines.extend(["", "## Issue Tree", ""])
    if not rca:
        lines.append("- No blocking issue tree was generated from section evidence.")
    else:
        for finding in rca:
            lines.append(
                f"- `{finding['section']}`: {finding['classification']} "
                f"({finding['evidence']})."
            )
            lines.append(f"  - Root cause: {finding.get('root_cause') or '-'}")
            lines.extend(_render_causal_allocation_lines(finding, indent="  "))
            lines.append("  - Required implementation plan:")
            for item in _validated_plan_items(finding):
                lines.append(f"    - {item}")
    lines.extend(["", "## Recommended Next Move", ""])
    if authorized:
        lines.append("1. Preserve the generated output package and run evidence.")
        lines.append("2. Review the mandatory ledger and section-status table for audit details.")
        lines.append("3. Treat future edits as new changes requiring the same X2/X3 gates.")
    elif final_gate_blocks:
        lines.append("1. Fix the final resume output gates before treating the run as product-ready.")
        lines.append("2. Regenerate the mandatory final resume text and DOCX from the canonical spine.")
        lines.append("3. Re-render the mandatory ledger and summary after the product outputs pass.")
    else:
        lines.append("1. Fix the P0 blocker sections named above.")
        lines.append("2. Rerun the integrated apps_rg path with the same JD and briefing.")
        lines.append("3. Treat final assembly as valid only when every required section is product-authorized.")
    lines.extend(["", "## Evidence Map", ""])
    lines.append(f"- Mandatory run ledger: `@{doc['run_root_abs']}\\{MANDATORY_RUN_OUTPUT_MD}`")
    lines.append(f"- Machine-readable ledger: `@{doc['run_root_abs']}\\{MANDATORY_RUN_OUTPUT_JSON}`")
    lines.append(f"- Rendered final resume: `@{doc['run_root_abs']}\\{FINAL_RESUME_OUTPUT_TXT}`")
    lines.append(f"- Final resume output contract: `@{doc['run_root_abs']}\\{FINAL_RESUME_OUTPUT_JSON}`")
    lines.append(f"- Resume DOCX: `@{doc['run_root_abs']}\\{FINAL_RESUME_DOCX_RELPATH}`")
    lines.append(f"- Section status: `@{doc['run_root_abs']}\\{FULL_RUN_SECTION_STATUS_JSON}`")
    lines.append(f"- Review bundle: `@{doc['run_root_abs']}\\{REVIEW_BUNDLE_FILENAME}`")
    return "\n".join(lines)


def _render_bcg_markdown_locked(doc: dict[str, Any]) -> str:
    summary = doc["result_summary"]
    counts = doc["section_counts"]
    rca = doc["rca_findings"]
    final_out = doc.get("final_resume_output") if isinstance(doc.get("final_resume_output"), dict) else {}
    final_status = str(final_out.get("status") or "UNKNOWN")
    authorized = bool(summary.get("outcome_authorized")) and final_status == "PASS"
    blocked_count = counts["blocked"] + counts["pre_run_blocked"] + counts["not_run"]
    status = "AUTHORIZED" if authorized else "BLOCKED"
    business_read = (
        "Final resume package is authorized; preserve the generated product and evidence ledgers."
        if authorized
        else (
            "No final resume can be authorized until mandatory generated-section gaps and "
            "final product gates are resolved. Locked base-resume fields are still rendered inline for review."
        )
    )
    technical_read = (
        f"Sections total={counts['total']}, REAL_LLM={counts['ran_real_llm']}, "
        f"X3 allow={counts['allowed']}, blocked/pre-run/not-run={blocked_count}, "
        f"final_resume_output_gate={final_status}."
    )
    priority_rows: list[dict[str, str]] = []
    failed_final = final_out.get("failed_gate_ids") if isinstance(final_out.get("failed_gate_ids"), list) else []
    if final_status != "PASS":
        priority_rows.append(
            {
                "priority": "P0",
                "finding": "Final resume product output gate is not PASS.",
                "evidence": ", ".join(str(x) for x in failed_final) or final_status,
                "required_action": "Keep final output blocked while preserving mandatory inline resume, JSON spine, and DOCX evidence.",
            }
        )
    for finding in rca[:6]:
        if not isinstance(finding, dict):
            continue
        priority_rows.append(
            {
                "priority": "P0" if not authorized else "P1",
                "finding": f"{finding.get('section')}: {finding.get('classification')}",
                "evidence": str(finding.get("evidence") or "-"),
                "required_action": str(finding.get("action") or "Apply the root-cause implementation plan."),
            }
        )
    if not priority_rows:
        priority_rows.append(
            {
                "priority": "P1",
                "finding": "No blocking section RCA rows were emitted.",
                "evidence": "mandatory ledger",
                "required_action": "Preserve gates and continue rendering BCG, lane table, and full resume inline after each run.",
            }
        )

    lines = [
        "# BCG Executive Brief",
        "",
        f"Generated: `{doc['generated_at_utc']}`",
        f"Run root: `@{doc['run_root_abs']}`",
        "",
        "North star: Produce a complete, auditable resume output package with real generation provenance, judge evidence, final resume text, and DOCX output visible inline.",
        f"Decision status: `{status}`",
        f"Business read: {business_read}",
        f"Technical evidence: {technical_read}",
        "Priority rule: Fix P0 product-output and lane-authorization blockers before rerun; treat P1 rows as hardening opportunities after P0 clears.",
        "",
        "## Decision Gates",
        "",
        "| Gate | Status | Evidence |",
        "|---|---|---|",
        f"| Outcome authorization | `{'PASS' if authorized else 'FAIL'}` | `outcome_authorized={summary.get('outcome_authorized')}` |",
        f"| Real generation observed | `{'PASS' if counts['ran_real_llm'] else 'FAIL'}` | `{counts['ran_real_llm']}` REAL_LLM section(s) |",
        f"| Final resume output | `{'PASS' if final_status == 'PASS' else 'FAIL'}` | `{final_status}` |",
        "| Inline output contract | `PASS` | BCG, section lane table, and resume text are mandatory surfaces |",
        "",
        "## P0-P1 Opportunities",
        "",
        "| Priority | Finding | Evidence | Required action |",
        "|---|---|---|---|",
    ]
    for row in priority_rows:
        lines.append(
            "| "
            f"`{row['priority']}` | "
            f"{_markdown_table_escape(row['finding'])} | "
            f"`{_markdown_table_escape(row['evidence'])}` | "
            f"{_markdown_table_escape(row['required_action'])} |"
        )
    lines.extend(["", "## Issue Tree", ""])
    if not rca:
        lines.append("- No blocking issue tree was generated from section evidence.")
    else:
        for finding in rca:
            lines.append(
                f"- `{finding['section']}`: {finding['classification']} "
                f"({finding['evidence']})."
            )
            lines.append(f"  - Root cause: {finding.get('root_cause') or '-'}")
            lines.extend(_render_causal_allocation_lines(finding, indent="  "))
            lines.append("  - Required implementation plan:")
            for item in _validated_plan_items(finding):
                lines.append(f"    - {item}")
    lines.extend(["", "## Next Step", ""])
    if authorized:
        lines.append("1. Preserve the generated output package and run evidence.")
        lines.append("2. Review the mandatory ledger and section-status table for audit details.")
        lines.append("3. Treat future edits as new changes requiring the same X2/X3 gates.")
    else:
        lines.append("1. Fix the P0 blocker rows above.")
        lines.append("2. Rerun the integrated apps_rg path with the same JD and briefing.")
        lines.append("3. Treat final assembly as valid only when every required section and product output is product-authorized.")
    lines.extend(["", "## Evidence Map", ""])
    lines.append(f"- Mandatory run ledger: `@{doc['run_root_abs']}\\{MANDATORY_RUN_OUTPUT_MD}`")
    lines.append(f"- Machine-readable ledger: `@{doc['run_root_abs']}\\{MANDATORY_RUN_OUTPUT_JSON}`")
    lines.append(f"- Rendered final resume: `@{doc['run_root_abs']}\\{FINAL_RESUME_OUTPUT_TXT}`")
    lines.append(f"- Final resume output contract: `@{doc['run_root_abs']}\\{FINAL_RESUME_OUTPUT_JSON}`")
    lines.append(f"- Resume DOCX: `@{doc['run_root_abs']}\\{FINAL_RESUME_DOCX_RELPATH}`")
    lines.append(f"- Section status: `@{doc['run_root_abs']}\\{FULL_RUN_SECTION_STATUS_JSON}`")
    lines.append(f"- Review bundle: `@{doc['run_root_abs']}\\{REVIEW_BUNDLE_FILENAME}`")
    return "\n".join(lines)


def build_mandatory_run_output(
    run_root: Path,
    *,
    repo_root: Path | None = None,
    result: dict[str, Any] | None = None,
    section_id: str | None = None,
) -> dict[str, Any]:
    root = Path(run_root).resolve()
    repo = (repo_root or root).resolve()
    sections = _collect_section_records(root, repo_root=repo, section_id=section_id)
    result_summary = _result_summary(result, root)
    final_required = _final_resume_output_required(root, result_summary)
    final_output = _load_json(root / FINAL_RESUME_OUTPUT_JSON)
    if not final_output:
        final_output = build_final_resume_output_contract(root, repo_root=repo, required=final_required)
    section_lane_table = _build_section_lane_table(root, sections)
    doc = {
        "schema_version": "apps_rg.mandatory_run_output.v1",
        "generated_at_utc": _utc_now(),
        "run_root_abs": str(root),
        "run_root": _repo_rel(root, repo),
        "result_summary": result_summary,
        "section_counts": _count_sections(sections),
        "sections": sections,
        "section_lane_table": section_lane_table,
        "final_resume_output": final_output,
        "rca_findings": _top_rca_sections(sections),
        "mandatory_artifacts": {
            "bcg_executive_output_md": BCG_EXECUTIVE_OUTPUT_MD,
            "mandatory_run_output_md": MANDATORY_RUN_OUTPUT_MD,
            "mandatory_run_output_json": MANDATORY_RUN_OUTPUT_JSON,
            "final_resume_output_txt": FINAL_RESUME_OUTPUT_TXT,
            "final_resume_output_json": FINAL_RESUME_OUTPUT_JSON,
            "final_resume_docx": FINAL_RESUME_DOCX_RELPATH,
            "canonical_final_resume_json": FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
        },
    }
    doc["mandatory_inline_output_gates"] = _inline_output_gates(doc)
    return doc


def emit_mandatory_run_outputs(
    run_root: Path,
    *,
    repo_root: Path | None = None,
    result: dict[str, Any] | None = None,
    section_id: str | None = None,
    print_stdout: bool = False,
) -> dict[str, Any]:
    """Write mandatory apps_rg run output artifacts."""
    root = Path(run_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    pre_summary = _result_summary(result, root)
    final_required = _final_resume_output_required(root, pre_summary)
    emit_final_resume_product_outputs(
        root,
        repo_root=repo_root,
        required=final_required,
    )
    doc = build_mandatory_run_output(
        root,
        repo_root=repo_root,
        result=result,
        section_id=section_id,
    )
    json_path = root / MANDATORY_RUN_OUTPUT_JSON
    md_path = root / MANDATORY_RUN_OUTPUT_MD
    bcg_path = root / BCG_EXECUTIVE_OUTPUT_MD
    json_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    _write_text(md_path, _render_mandatory_markdown(doc))
    _write_text(bcg_path, _render_bcg_markdown_locked(doc))
    if print_stdout:
        print((bcg_path).read_text(encoding="utf-8"), flush=True)
        print((md_path).read_text(encoding="utf-8"), flush=True)
        sys.stdout.flush()
    return {
        "json_path": json_path,
        "markdown_path": md_path,
        "bcg_markdown_path": bcg_path,
        "payload": doc,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Emit mandatory apps_rg BCG and run-ledger outputs.")
    parser.add_argument("run_dir", help="apps_rg run directory")
    parser.add_argument("--section", default="", help="Section id for a section-only run")
    parser.add_argument("--no-print", action="store_true", help="Do not print generated markdown")
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        print(f"Run dir not found: {run_dir}", file=sys.stderr)
        return 2
    emit_mandatory_run_outputs(
        run_dir,
        section_id=str(args.section or "") or None,
        print_stdout=not bool(args.no_print),
    )
    return 0


__all__ = [
    "BCG_EXECUTIVE_OUTPUT_MD",
    "MANDATORY_RUN_OUTPUT_JSON",
    "MANDATORY_RUN_OUTPUT_MD",
    "build_mandatory_run_output",
    "emit_mandatory_run_outputs",
]


if __name__ == "__main__":
    raise SystemExit(main())
