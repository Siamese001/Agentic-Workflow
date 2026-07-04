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

from apps_rg.prerequisites.briefing_validator import validate_apps_research_handoff
from apps_rg.runtime.final_resume_outputs import (
    build_final_resume_output_contract,
    emit_final_resume_product_outputs,
)
from apps_rg.runtime.full_run_section_status import (
    FINAL_AGGREGATION_LANE,
    LANE_DISPLAY_TXT_CANDIDATES,
    LaneSectionStatusRow,
    collect_full_run_section_status,
)
from apps_rg.runtime.runtime_proof_layout import find_repo_root
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

INLINE_REQUIRED_OUTPUT_SCHEMA_VERSION = "apps_rg.inline_required_output.v1"
INLINE_REQUIRED_OUTPUT_SECTION_ORDER = (
    "bcg",
    "section_lane_summary_table",
    "resume_docx_full_version_inline",
)
BCG_LOCKED_SECTION_ORDER = (
    "executive_answer",
    "p0_p1_px_recommendations",
    "board_level_readout",
    "issue_tree",
    "recommended_next_move",
    "evidence_map",
)
BCG_OUTPUT_KEYS = ("title", "section_order", *BCG_LOCKED_SECTION_ORDER)
SECTION_LANE_TABLE_COLUMNS = (
    "order",
    "section",
    "research_source_class",
    "r1a",
    "r1b",
    "lane_record",
    "provider_call_attempted",
    "primary_provider",
    "primary_model_observed",
    "pooling_selector_llm",
    "secondary_provider",
    "secondary_model_observed",
    "generation_status",
    "judges_run",
    "judge_models_scores",
    "judge_retry_fallback",
    "x2",
    "x3",
    "past_fail_blocker",
    "display_output",
    "l6_evidence",
)
INLINE_REQUIRED_OUTPUT_TOP_LEVEL_KEYS = (
    "schema_version",
    "immutable_section_order",
    "bcg",
    "section_lane_summary_table",
    "resume_docx_full_version_inline",
)
BCG_RECOMMENDATION_COLUMNS = ("priority", "recommendation", "evidence", "gate_outcome")
BCG_BOARD_READOUT_COLUMNS = ("question", "answer")
BCG_RECOMMENDATION_ROW_KEYS = BCG_RECOMMENDATION_COLUMNS
BCG_BOARD_READOUT_ROW_KEYS = BCG_BOARD_READOUT_COLUMNS
BCG_ISSUE_TREE_ROW_KEYS = (
    "section",
    "classification",
    "root_cause",
    "evidence",
    "causal_allocation",
    "required_implementation_plan",
)
BCG_EVIDENCE_MAP_ROW_KEYS = ("label", "path")
BCG_NESTED_TABLE_KEYS = ("columns", "rows")
SECTION_LANE_TABLE_KEYS = ("title", "columns", "rows")
RESUME_DOCX_INLINE_KEYS = ("title", "source", "text")
APPS_RESEARCH_PRIMARY_GENERATION_PROVIDER = "external_openai"
APPS_RESEARCH_PRIMARY_GENERATION_MODEL = "gpt-5.4-mini-2026-03-17"


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


def _first_nonempty(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _briefing_blob(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    text = str(value or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {"briefing_text": text}
    return parsed if isinstance(parsed, dict) else {"briefing_text": text}


def _short_digest(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "NOT_OBSERVED"
    return text[:12]


def _payload_dict(blob: dict[str, Any]) -> dict[str, Any]:
    payload = blob.get("payload")
    return payload if isinstance(payload, dict) else {}


def _artifact_input_value(blob: dict[str, Any], *keys: str) -> str:
    payload = _payload_dict(blob)
    for source in (blob, payload):
        for key in keys:
            value = str(source.get(key) or "").strip()
            if value:
                return value
    return ""


def _resolve_input_ref(ref: str, *, run_root: Path, repo_root: Path) -> str:
    text = str(ref or "").strip()
    if not text or text.startswith(("http://", "https://")):
        return text
    path = Path(text).expanduser()
    if path.is_absolute():
        return str(path)
    for base in (run_root, repo_root, Path.cwd()):
        try:
            candidate = (base / path).resolve()
            if candidate.is_file():
                return str(candidate)
        except OSError:
            continue
    return text


def _first_existing_json(paths: list[Path]) -> tuple[Path | None, dict[str, Any]]:
    for path in paths:
        data = _load_json(path)
        if data:
            return path, data
    return None, {}


def _research_handoff_receipt(run_root: Path) -> dict[str, Any]:
    candidates = [run_root / "apps_research_handoff_validation_receipt.json"]
    try:
        candidates.extend(sorted(run_root.rglob("apps_research_handoff_validation_receipt.json")))
    except OSError:
        pass
    _path, data = _first_existing_json(candidates)
    return data


def _research_artifact_dirs(run_root: Path) -> list[Path]:
    dirs: list[Path] = []
    for ref_path in (
        run_root / "research" / "research_artifact_ref.json",
        run_root / "research_bridge_response.json",
    ):
        data = _load_json(ref_path)
        raw = str(data.get("research_artifact_dir") or "").strip()
        if raw:
            dirs.append(Path(raw).expanduser())
    return dirs


def _research_envelope(run_root: Path, *, repo_root: Path, brief_ref: str) -> dict[str, Any]:
    candidates: list[Path] = [run_root / "apps_research_briefing_envelope.json"]
    resolved_brief = _resolve_input_ref(brief_ref, run_root=run_root, repo_root=repo_root)
    if resolved_brief and not resolved_brief.startswith(("http://", "https://")):
        brief_path = Path(resolved_brief)
        candidates.extend(
            [
                brief_path.parent / "apps_research_briefing_envelope.json",
                brief_path.with_suffix(brief_path.suffix + ".apps_research_envelope.json"),
                brief_path.with_suffix(".envelope.json"),
            ]
        )
    for artifact_dir in _research_artifact_dirs(run_root):
        candidates.append(artifact_dir / "apps_research_briefing_envelope.json")
    _path, data = _first_existing_json(candidates)
    return data


def _apps_research_gate_context(
    run_root: Path,
    *,
    repo_root: Path,
    ingress: dict[str, Any],
    spine: dict[str, Any],
    brief_ref: str,
    auto_research_internal: Any,
) -> dict[str, Any]:
    jd_ref = _first_nonempty(
        _artifact_input_value(ingress, "job_description_ref", "jd_ref", "jd_path"),
        _artifact_input_value(ingress, "jd", "job_description_text", "jd_text"),
    )
    resolved_brief = _resolve_input_ref(brief_ref, run_root=run_root, repo_root=repo_root)
    resolved_jd = _resolve_input_ref(jd_ref, run_root=run_root, repo_root=repo_root)
    strict_required = auto_research_internal is True and bool(str(brief_ref or "").strip())
    validation_envelope: dict[str, Any] | None = None
    try:
        validation = validate_apps_research_handoff(
            brief_ref=resolved_brief,
            jd_ref=resolved_jd,
            require_observed=strict_required,
            require_x1_x3_authorization=strict_required,
        )
        validation_receipt = validation.to_receipt()
        validation_envelope = validation.envelope if isinstance(validation.envelope, dict) else None
    except (OSError, ValueError) as exc:
        validation_receipt = {
            "schema_version": "apps_rg.apps_research_handoff_validation_receipt.v1",
            "observed": False,
            "valid": not strict_required,
            "reason": f"brief_ref_unresolvable:{type(exc).__name__}",
            "envelope_path": "",
        }
    receipt = _research_handoff_receipt(run_root) or validation_receipt
    envelope = (
        validation_envelope
        if isinstance(validation_envelope, dict)
        else _research_envelope(run_root, repo_root=repo_root, brief_ref=resolved_brief)
    )
    auth = (
        envelope.get("apps_research_x1_x3_authorization")
        if isinstance(envelope.get("apps_research_x1_x3_authorization"), dict)
        else {}
    )
    x1 = auth.get("x1") if isinstance(auth.get("x1"), dict) else {}
    x2 = auth.get("x2") if isinstance(auth.get("x2"), dict) else {}
    x3 = auth.get("x3") if isinstance(auth.get("x3"), dict) else {}
    route_decision = spine.get("route_decision") if isinstance(spine.get("route_decision"), dict) else {}
    observed = receipt.get("observed")
    valid = receipt.get("valid")
    reason = str(receipt.get("reason") or "NOT_OBSERVED")
    x1_status = str(x1.get("status") or "NOT_OBSERVED")
    x2_status = str(x2.get("status") or "NOT_OBSERVED")
    x3_status = str(x3.get("status") or "NOT_OBSERVED")
    x3_disposition = str(x3.get("disposition") or "NOT_OBSERVED")
    x2_score = _score_text(x2.get("score")) if x2.get("score") is not None else "NOT_OBSERVED"
    x2_judge_model = str(x2.get("judge_model") or "NOT_OBSERVED")
    generation_provider = str(envelope.get("generation_provider") or "NOT_OBSERVED")
    generation_model = str(envelope.get("generation_model") or "NOT_OBSERVED")
    handoff_eligible = (
        envelope.get("handoff_eligible") if isinstance(envelope, dict) else "NOT_OBSERVED"
    )
    summary = (
        f"handoff_observed={observed}; handoff_valid={valid}; reason={reason}; "
        f"run_id={str(envelope.get('run_id') or route_decision.get('research_run_id') or 'NOT_OBSERVED')}; "
        f"eligible={handoff_eligible}; stale={envelope.get('is_stale', 'NOT_OBSERVED')}; "
        f"X1={x1_status}; X2={x2_status}"
        f"{' score=' + x2_score if x2_score != 'NOT_OBSERVED' else ''}"
        f"{' judge_model=' + x2_judge_model if x2_judge_model != 'NOT_OBSERVED' else ''}; "
        f"X3={x3_status}/{x3_disposition}; "
        f"brief_sha={_short_digest(envelope.get('brief_sha256') or receipt.get('envelope_brief_sha256'))}; "
        f"jd_sha={_short_digest(envelope.get('jd_sha256') or receipt.get('envelope_jd_sha256'))}"
    )
    return {
        "summary": summary,
        "observed": observed,
        "valid": valid,
        "reason": reason,
        "x1_status": x1_status,
        "x2_status": x2_status,
        "x3_status": x3_status,
        "x3_disposition": x3_disposition,
        "x2_judge_model": x2_judge_model,
        "x2_score": x2_score,
        "generation_provider": generation_provider,
        "generation_model": generation_model,
    }


def _research_source_class(
    *,
    auto_research_internal: Any,
    delegation_observed: Any,
    briefing_present: bool,
    research_via: str = "",
) -> str:
    via = str(research_via or "").strip().lower()
    if delegation_observed is True:
        return "FRESH_APPS_RESEARCH"
    if via in {"skip", "operator_skip", "none"}:
        return "OPERATOR_SKIP"
    if briefing_present:
        return "STATIC_MANUAL_BRIEF"
    if auto_research_internal is True:
        return "MISSING_APPS_RESEARCH"
    return "NOT_OBSERVED"


def _research_x2_cell(gates: dict[str, Any]) -> str:
    status = str(gates.get("x2_status") or "NOT_OBSERVED")
    if status == "NOT_OBSERVED":
        reason = str(gates.get("reason") or "").strip()
        return f"NOT_OBSERVED; blocker={reason}" if reason else "NOT_OBSERVED"
    parts = [status]
    score = str(gates.get("x2_score") or "").strip()
    judge = str(gates.get("x2_judge_model") or "").strip()
    if score and score != "NOT_OBSERVED":
        parts.append(score)
    if judge and judge != "NOT_OBSERVED":
        parts.append(f"judge={judge}")
    return "; ".join(parts)


def _research_x3_cell(gates: dict[str, Any]) -> str:
    disposition = str(gates.get("x3_disposition") or gates.get("x3_status") or "NOT_OBSERVED")
    x1_status = str(gates.get("x1_status") or "NOT_OBSERVED")
    if disposition == "NOT_OBSERVED":
        reason = str(gates.get("reason") or "").strip()
        return f"NOT_OBSERVED; blocker={reason}" if reason else "NOT_OBSERVED"
    return f"{disposition}; X1={x1_status}"


def _research_briefing_context(run_root: Path, *, repo_root: Path) -> dict[str, Any]:
    phase1 = _load_json(run_root / "modular_r4" / "phase1_lane_inventory.json")
    targeting = phase1.get("lane_argv_targeting") if isinstance(phase1.get("lane_argv_targeting"), dict) else {}
    briefing = _briefing_blob(targeting.get("briefing_text"))
    ingress = _load_json(run_root / "ingress_raw.json")
    spine = _load_json(run_root / "spine_run_manifest.json")
    route_decision = spine.get("route_decision") if isinstance(spine.get("route_decision"), dict) else {}
    delegation_observed = (
        spine.get("research_delegation_executed")
        if "research_delegation_executed" in spine
        else route_decision.get("research_delegation_executed")
        if "research_delegation_executed" in route_decision
        else "NOT_OBSERVED"
    )
    auto_research_internal = ingress.get("auto_research_internal", route_decision.get("research_delegation_enabled"))
    research_via = _first_nonempty(ingress.get("research_via"), route_decision.get("research_via"))
    source = _first_nonempty(
        targeting.get("briefing_source"),
        briefing.get("source"),
        ingress.get("research_via"),
        "NOT_OBSERVED",
    )
    digest = _first_nonempty(
        targeting.get("briefing_digest"),
        briefing.get("briefing_digest"),
        briefing.get("digest"),
        ingress.get("brief_hash"),
    )
    ref = _first_nonempty(
        targeting.get("briefing_ref_used"),
        targeting.get("briefing_artifact_ref"),
        route_decision.get("delegated_briefing_path"),
        ingress.get("manual_brief"),
        ingress.get("manual_brief_path"),
        ingress.get("briefing_artifact_ref"),
    )
    company = _first_nonempty(targeting.get("target_company"), briefing.get("target_company"), ingress.get("target_company"))
    title = _first_nonempty(
        targeting.get("target_title"),
        briefing.get("target_role"),
        briefing.get("target_title"),
        ingress.get("target_role"),
    )
    briefing_text = _first_nonempty(briefing.get("briefing_text"), targeting.get("briefing_text"), ingress.get("briefing_text"))
    gates = _apps_research_gate_context(
        run_root,
        repo_root=repo_root,
        ingress=ingress,
        spine=spine,
        brief_ref=ref,
        auto_research_internal=auto_research_internal,
    )
    return {
        "auto_research_internal": auto_research_internal,
        "research_delegation_executed": delegation_observed,
        "research_via": research_via,
        "source": source,
        "digest": digest,
        "ref": ref,
        "target_company": company,
        "target_title": title,
        "briefing_text": briefing_text,
        "briefing_text_chars": len(briefing_text) if briefing_text else 0,
        "fetched_at": _first_nonempty(briefing.get("fetched_at"), targeting.get("fetched_at")),
        "source_url": _first_nonempty(briefing.get("source_url"), targeting.get("source_url")),
        "briefing_present": bool(briefing_text or ref or digest),
        "apps_research_gates": gates,
    }


def _research_briefing_row(run_root: Path, *, repo_root: Path, cache: dict[str, str]) -> dict[str, Any]:
    context = _research_briefing_context(run_root, repo_root=repo_root)
    delegation_observed = context["research_delegation_executed"]
    auto_research_internal = context.get("auto_research_internal")
    source = str(context.get("source") or "NOT_OBSERVED")
    digest = str(context.get("digest") or "")
    ref = str(context.get("ref") or "")
    company = str(context.get("target_company") or "")
    title = str(context.get("target_title") or "")
    briefing_present = bool(context.get("briefing_present"))
    gates = context.get("apps_research_gates") if isinstance(context.get("apps_research_gates"), dict) else {}
    generation_provider = str(gates.get("generation_provider") or "").strip()
    generation_model = str(gates.get("generation_model") or "").strip()
    research_source_class = _research_source_class(
        auto_research_internal=auto_research_internal,
        delegation_observed=delegation_observed,
        briefing_present=briefing_present,
        research_via=str(context.get("research_via") or ""),
    )
    p0_static_manual = auto_research_internal is True and delegation_observed is not True
    evidence_parts = [
        f"auto_research_internal={auto_research_internal}",
        f"research_delegation_executed={delegation_observed}",
        f"source={source}",
    ]
    if context.get("fetched_at"):
        evidence_parts.append(f"fetched_at={context['fetched_at']}")
    if digest:
        evidence_parts.append(f"digest={digest}")
    if ref:
        evidence_parts.append(f"ref={ref}")
    if company or title:
        evidence_parts.append(f"target={company or 'UNKNOWN'} / {title or 'UNKNOWN'}")
    if context.get("briefing_text_chars"):
        evidence_parts.append(f"briefing_text_chars={context['briefing_text_chars']}")
    if not briefing_present:
        evidence_parts.append("briefing missing")
    return {
        "order": 0,
        "section": "research_briefing_input",
        "research_source_class": research_source_class,
        "r1a": cache["r1a"],
        "r1b": cache["r1b"],
        "lane_record": "YES" if briefing_present else "NO",
        "provider_call_attempted": delegation_observed,
        "primary_provider": (
            generation_provider
            if delegation_observed is True and generation_provider and generation_provider != "NOT_OBSERVED"
            else APPS_RESEARCH_PRIMARY_GENERATION_PROVIDER
            if delegation_observed is True
            else "STATIC_MANUAL_BRIEF" if briefing_present else "NOT_OBSERVED"
        ),
        "primary_model_observed": (
            generation_model
            if delegation_observed is True and generation_model and generation_model != "NOT_OBSERVED"
            else APPS_RESEARCH_PRIMARY_GENERATION_MODEL
            if delegation_observed is True
            else "NOT_OBSERVED"
        ),
        "pooling_selector_llm": "N/A",
        "secondary_provider": "N/A",
        "secondary_model_observed": "N/A",
        "generation_status": (
            "P0_STATIC_MANUAL_BRIEF_USED"
            if p0_static_manual
            else f"BRIEFING_PRESENT:{source}" if briefing_present else "MISSING_BRIEFING"
        ),
        "judges_run": "N/A",
        "judge_models_scores": "N/A",
        "judge_retry_fallback": "N/A",
        "x2": _research_x2_cell(gates),
        "x3": (
            "FAIL"
            if p0_static_manual or not briefing_present
            else _research_x3_cell(gates)
        ),
        "past_fail_blocker": "; ".join(evidence_parts),
        "display_output": ref or "MISSING",
        "l6_evidence": "N/A",
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


def _section_lane_abs_dir(section: dict[str, Any], *, repo_root: Path) -> Path | None:
    lane_dir = str(section.get("lane_dir") or "").strip()
    if lane_dir:
        path = Path(lane_dir)
        return path if path.is_absolute() else repo_root / path
    display = str(section.get("display_txt_path") or "").strip()
    if display:
        return Path(display).parent
    return None


def _lane_provider_proof(section: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    lane_dir = _section_lane_abs_dir(section, repo_root=repo_root)
    if lane_dir is None:
        return {}
    provider_request = _load_json(lane_dir / "provider_request.json")
    provider_response = _load_json(lane_dir / "provider_response.json")
    run_manifest = _load_json(lane_dir / "run_manifest.json")
    l2_output = _load_json(lane_dir / "l2_output.json")
    return {
        "provider_request": provider_request,
        "provider_response": provider_response,
        "run_manifest": run_manifest,
        "l2_output": l2_output,
        "has_lane_proof": any((provider_request, provider_response, run_manifest, l2_output)),
    }


def _lane_provider_attempted(record: dict[str, Any], proof: dict[str, Any]) -> Any:
    request = proof.get("provider_request") if isinstance(proof.get("provider_request"), dict) else {}
    if "provider_attempted" in request:
        return request.get("provider_attempted")
    if request.get("provider_requested") or request.get("model"):
        return True
    if "provider_call_attempted" in record:
        return record.get("provider_call_attempted")
    return "NOT_OBSERVED"


def _lane_primary_provider(record: dict[str, Any], proof: dict[str, Any]) -> str:
    request = proof.get("provider_request") if isinstance(proof.get("provider_request"), dict) else {}
    response = proof.get("provider_response") if isinstance(proof.get("provider_response"), dict) else {}
    l2_output = proof.get("l2_output") if isinstance(proof.get("l2_output"), dict) else {}
    return _first_nonempty(
        request.get("provider_requested"),
        response.get("provider_requested"),
        response.get("provider"),
        l2_output.get("provider_requested"),
        record.get("provider_profile"),
    ) or "NOT_OBSERVED"


def _lane_primary_model(record: dict[str, Any], proof: dict[str, Any]) -> str:
    request = proof.get("provider_request") if isinstance(proof.get("provider_request"), dict) else {}
    response = proof.get("provider_response") if isinstance(proof.get("provider_response"), dict) else {}
    l2_output = proof.get("l2_output") if isinstance(proof.get("l2_output"), dict) else {}
    return _first_nonempty(
        record.get("model_id"),
        response.get("model_id"),
        response.get("model"),
        response.get("model_name"),
        request.get("model"),
        request.get("model_id"),
        l2_output.get("model_id"),
        l2_output.get("model"),
        l2_output.get("model_name"),
    ) or "NOT_OBSERVED"


def _lane_generation_status(
    record: dict[str, Any],
    section: dict[str, Any],
    proof: dict[str, Any],
) -> str:
    manifest = proof.get("run_manifest") if isinstance(proof.get("run_manifest"), dict) else {}
    l2_output = proof.get("l2_output") if isinstance(proof.get("l2_output"), dict) else {}
    return _first_nonempty(
        section.get("runtime_generation_status"),
        manifest.get("runtime_generation_status"),
        l2_output.get("runtime_generation_status"),
        record.get("generation_status"),
    ) or "NOT_OBSERVED"


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


def _build_section_lane_table(
    run_root: Path,
    sections: list[dict[str, Any]],
    *,
    repo_root: Path,
) -> list[dict[str, Any]]:
    provider_records = _load_provider_call_records(run_root)
    cache = _cache_preflight(run_root)
    by_id = _section_by_id(sections)
    rows: list[dict[str, Any]] = [_research_briefing_row(run_root, repo_root=repo_root, cache=cache)]
    for idx, section_id in enumerate(_generation_ordered_section_ids(sections, provider_records), 1):
        section = by_id.get(section_id, {})
        record = provider_records.get(section_id, {})
        provider_proof = _lane_provider_proof(section, repo_root=repo_root)
        l6 = section.get("l6") if isinstance(section.get("l6"), dict) else {}
        rows.append(
            {
                "order": idx,
                "section": section_id,
                "research_source_class": "N/A",
                "r1a": cache["r1a"],
                "r1b": cache["r1b"],
                "lane_record": "YES" if record or section or provider_proof.get("has_lane_proof") else "NO",
                "provider_call_attempted": _lane_provider_attempted(record, provider_proof),
                "primary_provider": _lane_primary_provider(record, provider_proof),
                "primary_model_observed": _lane_primary_model(record, provider_proof),
                "pooling_selector_llm": _pooling_selector_cell(section_id),
                "secondary_provider": _secondary_provider_cell(record),
                "secondary_model_observed": _provider_cell(record, "secondary_model_id"),
                "generation_status": _lane_generation_status(record, section, provider_proof),
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


def _exact_key_order(value: Any, keys: tuple[str, ...]) -> bool:
    return isinstance(value, dict) and tuple(value.keys()) == keys


def _validate_row_keys(rows: Any, keys: tuple[str, ...], label: str) -> list[str]:
    if not isinstance(rows, list):
        return [f"{label}.rows_not_list"]
    errors: list[str] = []
    for idx, row in enumerate(rows):
        if not _exact_key_order(row, keys):
            observed = list(row.keys()) if isinstance(row, dict) else type(row).__name__
            errors.append(f"{label}[{idx}].keys={observed}")
    return errors


def _inline_required_output_shape_errors(inline: Any) -> list[str]:
    errors: list[str] = []
    if not _exact_key_order(inline, INLINE_REQUIRED_OUTPUT_TOP_LEVEL_KEYS):
        observed = list(inline.keys()) if isinstance(inline, dict) else type(inline).__name__
        return [f"inline_required_output.keys={observed}"]
    if inline.get("schema_version") != INLINE_REQUIRED_OUTPUT_SCHEMA_VERSION:
        errors.append("schema_version")
    if inline.get("immutable_section_order") != list(INLINE_REQUIRED_OUTPUT_SECTION_ORDER):
        errors.append("immutable_section_order")

    bcg = inline.get("bcg")
    if not _exact_key_order(bcg, BCG_OUTPUT_KEYS):
        observed = list(bcg.keys()) if isinstance(bcg, dict) else type(bcg).__name__
        errors.append(f"bcg.keys={observed}")
    else:
        if bcg.get("title") != "BCG Executive Output - apps_rg Run":
            errors.append("bcg.title")
        if bcg.get("section_order") != list(BCG_LOCKED_SECTION_ORDER):
            errors.append("bcg.section_order")
        recs = bcg.get("p0_p1_px_recommendations")
        if not _exact_key_order(recs, BCG_NESTED_TABLE_KEYS):
            observed = list(recs.keys()) if isinstance(recs, dict) else type(recs).__name__
            errors.append(f"bcg.p0_p1_px_recommendations.keys={observed}")
        else:
            if recs.get("columns") != list(BCG_RECOMMENDATION_COLUMNS):
                errors.append("bcg.p0_p1_px_recommendations.columns")
            errors.extend(
                _validate_row_keys(
                    recs.get("rows"),
                    BCG_RECOMMENDATION_ROW_KEYS,
                    "bcg.p0_p1_px_recommendations.rows",
                )
            )
        board = bcg.get("board_level_readout")
        if not _exact_key_order(board, BCG_NESTED_TABLE_KEYS):
            observed = list(board.keys()) if isinstance(board, dict) else type(board).__name__
            errors.append(f"bcg.board_level_readout.keys={observed}")
        else:
            if board.get("columns") != list(BCG_BOARD_READOUT_COLUMNS):
                errors.append("bcg.board_level_readout.columns")
            errors.extend(
                _validate_row_keys(
                    board.get("rows"),
                    BCG_BOARD_READOUT_ROW_KEYS,
                    "bcg.board_level_readout.rows",
                )
            )
        if not isinstance(bcg.get("executive_answer"), str):
            errors.append("bcg.executive_answer")
        issue_tree = bcg.get("issue_tree")
        if not isinstance(issue_tree, list):
            errors.append("bcg.issue_tree")
        else:
            errors.extend(_validate_row_keys(issue_tree, BCG_ISSUE_TREE_ROW_KEYS, "bcg.issue_tree"))
        next_moves = bcg.get("recommended_next_move")
        if not isinstance(next_moves, list) or not all(isinstance(item, str) for item in next_moves):
            errors.append("bcg.recommended_next_move")
        evidence_map = bcg.get("evidence_map")
        if not isinstance(evidence_map, list):
            errors.append("bcg.evidence_map")
        else:
            errors.extend(_validate_row_keys(evidence_map, BCG_EVIDENCE_MAP_ROW_KEYS, "bcg.evidence_map"))

    lane_table = inline.get("section_lane_summary_table")
    if not _exact_key_order(lane_table, SECTION_LANE_TABLE_KEYS):
        observed = list(lane_table.keys()) if isinstance(lane_table, dict) else type(lane_table).__name__
        errors.append(f"section_lane_summary_table.keys={observed}")
    else:
        if lane_table.get("title") != "Section Lane Summary Table":
            errors.append("section_lane_summary_table.title")
        if lane_table.get("columns") != list(SECTION_LANE_TABLE_COLUMNS):
            errors.append("section_lane_summary_table.columns")
        errors.extend(
            _validate_row_keys(
                lane_table.get("rows"),
                SECTION_LANE_TABLE_COLUMNS,
                "section_lane_summary_table.rows",
            )
        )

    resume = inline.get("resume_docx_full_version_inline")
    if not _exact_key_order(resume, RESUME_DOCX_INLINE_KEYS):
        observed = list(resume.keys()) if isinstance(resume, dict) else type(resume).__name__
        errors.append(f"resume_docx_full_version_inline.keys={observed}")
    else:
        if resume.get("title") != "Resume DOCX Full Version Inline":
            errors.append("resume_docx_full_version_inline.title")
        if not isinstance(resume.get("source"), str) or not resume.get("source"):
            errors.append("resume_docx_full_version_inline.source")
        if not isinstance(resume.get("text"), str) or not resume.get("text").strip():
            errors.append("resume_docx_full_version_inline.text")
    return errors


def _non_authorized_section_ids(doc: dict[str, Any]) -> dict[str, list[str]]:
    blocked: dict[str, list[str]] = {
        "x3_blocked": [],
        "pre_run_blocked": [],
        "not_run": [],
        "unknown": [],
    }
    for section in doc.get("sections", []):
        if not isinstance(section, dict):
            continue
        section_id = str(section.get("section") or "").strip()
        if not section_id:
            continue
        x3_code = str(section.get("x3_code") or "")
        bucket = str(section.get("status_bucket") or "")
        if x3_code.startswith("X3_BLOCK"):
            blocked["x3_blocked"].append(section_id)
        elif bucket == "pre_run_blocked" or x3_code.startswith("PRE_RUN:"):
            blocked["pre_run_blocked"].append(section_id)
        elif bucket == "not_run" or x3_code == "NOT_RUN":
            blocked["not_run"].append(section_id)
        elif x3_code not in {"X3_ALLOW", "X3_REVIEW_JUDGE_SOFT_FAIL"}:
            blocked["unknown"].append(section_id)
    return blocked


def _resume_inline_authorization(doc: dict[str, Any]) -> tuple[bool, list[str]]:
    summary = doc.get("result_summary") if isinstance(doc.get("result_summary"), dict) else {}
    final_out = doc.get("final_resume_output") if isinstance(doc.get("final_resume_output"), dict) else {}
    rendered = final_out.get("rendered_resume_text") if isinstance(final_out.get("rendered_resume_text"), dict) else {}
    docx = final_out.get("resume_docx") if isinstance(final_out.get("resume_docx"), dict) else {}
    spine = final_out.get("final_resume_json") if isinstance(final_out.get("final_resume_json"), dict) else {}
    reasons: list[str] = []
    if summary.get("outcome_authorized") is not True:
        reasons.append("outcome_authorized_false")
    if str(final_out.get("status") or "") != "PASS":
        reasons.append(f"final_resume_output_status={final_out.get('status') or 'UNKNOWN'}")
    failed_gates = final_out.get("failed_gate_ids")
    if isinstance(failed_gates, list) and failed_gates:
        reasons.append("failed_final_resume_gates=" + ",".join(str(gate) for gate in failed_gates))
    for artifact_label, artifact in (
        ("final_resume_json", spine),
        ("rendered_resume_text", rendered),
        ("resume_docx", docx),
    ):
        if not artifact.get("exists") or int(artifact.get("bytes") or 0) <= 0:
            reasons.append(f"{artifact_label}_missing_or_empty")
    for label, sections in _non_authorized_section_ids(doc).items():
        if sections:
            reasons.append(f"{label}=" + ",".join(sections))
    return not reasons, reasons


def _blocked_resume_inline_text(doc: dict[str, Any], reasons: list[str]) -> str:
    return "\n".join(
        [
            "NO_AUTHORIZED_RESUME_OUTPUT",
            "source_of_truth=current_e2e_run_artifacts_only",
            f"run_root={doc.get('run_root_abs') or 'UNKNOWN'}",
            "status=BLOCKED",
            "reason=" + ("; ".join(reasons) if reasons else "unknown_blocker"),
            "policy=do_not_inline_FINAL_RESUME_OUTPUT_txt_unless_current_run_authorized",
        ]
    )


def _resume_inline_source(doc: dict[str, Any], authorized: bool) -> str:
    if authorized:
        return (
            "FINAL_RESUME_OUTPUT.txt rendered from the current E2E run final-resume spine "
            "used for outputs/resume.docx."
        )
    return (
        "No authorized resume text emitted; this block is derived only from the current E2E "
        "run ledger and final-resume output contract."
    )


def _authorized_resume_inline_text(doc: dict[str, Any]) -> str:
    run_root = Path(str(doc.get("run_root_abs") or ""))
    resume_path = run_root / FINAL_RESUME_OUTPUT_TXT
    if not resume_path.is_file():
        return "[MANDATORY_OUTPUT_MISSING: FINAL_RESUME_OUTPUT.txt]"
    try:
        return resume_path.read_text(encoding="utf-8").rstrip() or "[MANDATORY_OUTPUT_EMPTY: FINAL_RESUME_OUTPUT.txt]"
    except OSError:
        return "[MANDATORY_OUTPUT_UNREADABLE: FINAL_RESUME_OUTPUT.txt]"


def _resume_inline_text(doc: dict[str, Any]) -> str:
    authorized, reasons = _resume_inline_authorization(doc)
    if not authorized:
        return _blocked_resume_inline_text(doc, reasons)
    return _authorized_resume_inline_text(doc)


def _inline_output_gates(doc: dict[str, Any]) -> list[dict[str, Any]]:
    final_out = doc.get("final_resume_output") if isinstance(doc.get("final_resume_output"), dict) else {}
    rendered = final_out.get("rendered_resume_text") if isinstance(final_out.get("rendered_resume_text"), dict) else {}
    docx = final_out.get("resume_docx") if isinstance(final_out.get("resume_docx"), dict) else {}
    spine = final_out.get("final_resume_json") if isinstance(final_out.get("final_resume_json"), dict) else {}
    lane_table = doc.get("section_lane_table") if isinstance(doc.get("section_lane_table"), list) else []
    inline = doc.get("inline_required_output") if isinstance(doc.get("inline_required_output"), dict) else {}
    bcg = inline.get("bcg") if isinstance(inline.get("bcg"), dict) else {}
    recs = bcg.get("p0_p1_px_recommendations") if isinstance(bcg.get("p0_p1_px_recommendations"), dict) else {}
    rec_rows = recs.get("rows") if isinstance(recs.get("rows"), list) else []
    rec_priorities = {str(row.get("priority") or "") for row in rec_rows if isinstance(row, dict)}
    row0 = lane_table[0] if lane_table and isinstance(lane_table[0], dict) else {}
    resume_inline = (
        inline.get("resume_docx_full_version_inline")
        if isinstance(inline.get("resume_docx_full_version_inline"), dict)
        else {}
    )
    resume_inline_authorized, resume_inline_blockers = _resume_inline_authorization(doc)
    shape_errors = _inline_required_output_shape_errors(inline)
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
            "pass": resume_inline_authorized
            and bool(rendered.get("exists"))
            and int(rendered.get("bytes") or 0) > 0,
            "observed_value": {
                "artifact": rendered,
                "current_run_authorized": resume_inline_authorized,
                "blockers": resume_inline_blockers,
            },
            "threshold": "current-run authorized nonempty FINAL_RESUME_OUTPUT.txt",
        },
        {
            "gate_id": "mandatory_final_resume_json_present",
            "pass": resume_inline_authorized
            and bool(spine.get("exists"))
            and int(spine.get("bytes") or 0) > 0,
            "observed_value": {
                "artifact": spine,
                "current_run_authorized": resume_inline_authorized,
                "blockers": resume_inline_blockers,
            },
            "threshold": f"current-run authorized {FINAL_RESUME_ASSEMBLY_JSON_RELPATH}",
        },
        {
            "gate_id": "mandatory_resume_docx_present",
            "pass": resume_inline_authorized
            and bool(docx.get("exists"))
            and int(docx.get("bytes") or 0) > 0,
            "observed_value": {
                "artifact": docx,
                "current_run_authorized": resume_inline_authorized,
                "blockers": resume_inline_blockers,
            },
            "threshold": f"current-run authorized {FINAL_RESUME_DOCX_RELPATH}",
        },
        {
            "gate_id": "mandatory_inline_required_json_shape_locked",
            "pass": not shape_errors,
            "observed_value": {
                "schema_version": inline.get("schema_version"),
                "immutable_section_order": inline.get("immutable_section_order"),
                "shape_errors": shape_errors,
            },
            "threshold": {
                "schema_version": INLINE_REQUIRED_OUTPUT_SCHEMA_VERSION,
                "immutable_section_order": list(INLINE_REQUIRED_OUTPUT_SECTION_ORDER),
                "top_level_keys": list(INLINE_REQUIRED_OUTPUT_TOP_LEVEL_KEYS),
            },
        },
        {
            "gate_id": "mandatory_bcg_p0_p1_px_recommendations_locked",
            "pass": (
                bcg.get("title") == "BCG Executive Output - apps_rg Run"
                and bcg.get("section_order") == list(BCG_LOCKED_SECTION_ORDER)
                and {"P0", "P1", "PX"}.issubset(rec_priorities)
            ),
            "observed_value": {
                "title": bcg.get("title"),
                "section_order": bcg.get("section_order"),
                "priorities": sorted(rec_priorities),
            },
            "threshold": "BCG title + section order + P0/P1/PX recommendations",
        },
        {
            "gate_id": "mandatory_research_briefing_input_row0_locked",
            "pass": row0.get("order") == 0 and row0.get("section") == "research_briefing_input",
            "observed_value": {
                "order": row0.get("order"),
                "section": row0.get("section"),
                "generation_status": row0.get("generation_status"),
            },
            "threshold": "row 0 research_briefing_input",
        },
        {
            "gate_id": "mandatory_apps_research_row0_x1_x2_x3_gates_locked",
            "pass": (
                row0.get("order") == 0
                and row0.get("section") == "research_briefing_input"
                and str(row0.get("research_source_class") or "") not in {"", "NOT_OBSERVED"}
                and str(row0.get("x2") or "") not in {"", "NOT_OBSERVED"}
                and str(row0.get("x3") or "") not in {"", "NOT_OBSERVED"}
            ),
            "observed_value": {
                "research_source_class": row0.get("research_source_class"),
                "x2": row0.get("x2"),
                "x3": row0.get("x3"),
            },
            "threshold": "row 0 research_source_class plus compact X2/X3 handoff cells",
        },
        {
            "gate_id": "mandatory_resume_docx_inline_json_present",
            "pass": resume_inline_authorized
            and bool(str(resume_inline.get("text") or "").strip())
            and "NO_AUTHORIZED_RESUME_OUTPUT" not in str(resume_inline.get("text") or ""),
            "observed_value": {
                "title": resume_inline.get("title"),
                "text_chars": len(str(resume_inline.get("text") or "")),
                "current_run_authorized": resume_inline_authorized,
                "blockers": resume_inline_blockers,
            },
            "threshold": "resume_docx_full_version_inline.text is current-run authorized resume content",
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
        "| # | Section | Research source class | R1A | R1B | Lane record | Provider call attempted | Primary provider | Primary model observed | Pooling selector LLM | Secondary provider | Secondary model observed | Generation status | Judges run | Judge models / scores | Judge retry / fallback | X2 | X3 | Past fail / blocker | Display output | L6 evidence |",
        "|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    if not rows:
        lines.append("| 0 | `NO_ROWS` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NO` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NO` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NOT_OBSERVED` | `mandatory section lane table missing` | `MISSING` | `NOT_OBSERVED` |")
        return lines
    for row in rows:
        lines.append(
            "| "
            f"{row.get('order')} | "
            f"`{_markdown_table_escape(row.get('section'))}` | "
            f"`{_markdown_table_escape(row.get('research_source_class'))}` | "
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
    inline = doc.get("inline_required_output") if isinstance(doc.get("inline_required_output"), dict) else {}
    resume = (
        inline.get("resume_docx_full_version_inline")
        if isinstance(inline.get("resume_docx_full_version_inline"), dict)
        else {}
    )
    source = str(resume.get("source") or "No inline resume source observed.")
    text = str(resume.get("text") or "").rstrip()
    return [
        "## Resume DOCX Full Version Inline",
        "",
        f"Source: `{source}`",
        "",
        "```text",
        text or "[MANDATORY_OUTPUT_MISSING: resume_docx_full_version_inline.text]",
        "```",
    ]


def _research_row(doc: dict[str, Any]) -> dict[str, Any]:
    rows = doc.get("section_lane_table") if isinstance(doc.get("section_lane_table"), list) else []
    for row in rows:
        if isinstance(row, dict) and row.get("section") == "research_briefing_input":
            return row
    return {}


def _build_bcg_recommendations(doc: dict[str, Any]) -> list[dict[str, str]]:
    final_out = doc.get("final_resume_output") if isinstance(doc.get("final_resume_output"), dict) else {}
    final_status = str(final_out.get("status") or "UNKNOWN")
    failed_final = final_out.get("failed_gate_ids") if isinstance(final_out.get("failed_gate_ids"), list) else []
    research = _research_row(doc)
    lane_rows = doc.get("section_lane_table") if isinstance(doc.get("section_lane_table"), list) else []
    rows: list[dict[str, str]] = []
    if research.get("generation_status") == "P0_STATIC_MANUAL_BRIEF_USED":
        rows.extend(
            [
                {
                    "priority": "P0",
                    "recommendation": "Fail closed when auto_research_internal=True but apps_research delegation does not execute.",
                    "evidence": str(research.get("past_fail_blocker") or "research_delegation_executed=False"),
                    "gate_outcome": "Block before section generation.",
                },
                {
                    "priority": "P0",
                    "recommendation": "Keep row 0 named research_briefing_input; do not call it apps_research unless apps_research actually ran.",
                    "evidence": "No apps_research provider/model/run receipt observed for this run.",
                    "gate_outcome": "Prevent false provenance.",
                },
                {
                    "priority": "P0",
                    "recommendation": "Require a fresh research artifact or explicit operator skip before resume lanes run.",
                    "evidence": str(research.get("past_fail_blocker") or "static manual brief"),
                    "gate_outcome": "Block stale/manual research.",
                },
            ]
        )
    first_blocker = next(
        (
            finding
            for finding in doc.get("rca_findings", [])
            if isinstance(finding, dict) and str(finding.get("section") or "") == "competencies"
        ),
        None,
    )
    if isinstance(first_blocker, dict):
        rows.append(
            {
                "priority": "P0",
                "recommendation": "Fix competencies first-lane execution failure before scheduling downstream lanes.",
                "evidence": str(first_blocker.get("evidence") or first_blocker.get("classification") or "competencies blocked"),
                "gate_outcome": "No downstream lane without upstream authorization.",
            }
        )
    blocked_generated_lanes = [
        str(row.get("section") or "")
        for row in lane_rows
        if isinstance(row, dict)
        and str(row.get("section") or "") != "research_briefing_input"
        and str(row.get("x3") or "").startswith("X3_BLOCK")
    ]
    if blocked_generated_lanes:
        rows.append(
            {
                "priority": "P0",
                "recommendation": "Fix X3-blocked generated lanes before authorizing the final resume.",
                "evidence": ", ".join(blocked_generated_lanes),
                "gate_outcome": "Outcome remains blocked until every required generated lane clears X3.",
            }
        )
    if final_status != "PASS":
        rows.append(
            {
                "priority": "P0",
                "recommendation": "Keep final resume product gate failed while generated-section gap markers exist.",
                "evidence": ", ".join(str(x) for x in failed_final) or final_status,
                "gate_outcome": "Final resume unauthorized.",
            }
        )
    provider_gap_sections = [
        str(row.get("section") or "")
        for row in lane_rows
        if isinstance(row, dict)
        and str(row.get("x3") or "").startswith("X3_BLOCK")
        and str(row.get("generation_status") or "") == "REAL_LLM"
        and (
            row.get("provider_call_attempted") is not True
            or str(row.get("primary_provider") or "") in {"", "NOT_OBSERVED"}
            or str(row.get("primary_model_observed") or "") in {"", "NOT_OBSERVED"}
        )
    ]
    if provider_gap_sections:
        rows.append(
            {
                "priority": "P1",
                "recommendation": "Capture provider attempts, retries, fallback, and observed model IDs for failed lanes.",
                "evidence": "Provider proof gap in: " + ", ".join(provider_gap_sections),
                "gate_outcome": "Make failure RCA auditable.",
            }
        )
    phase1_no_run_lanes = [
        str(row.get("section") or "")
        for row in lane_rows
        if isinstance(row, dict)
        and "PHASE1_NO_RUN_DIR" in str(row.get("x3") or row.get("past_fail_blocker") or "")
    ]
    rows.extend(
        [
            {
                "priority": "P1",
                "recommendation": "Add dependency-token reporting for every PHASE1_NO_RUN_DIR lane.",
                "evidence": (
                    "PHASE1_NO_RUN_DIR lanes: " + ", ".join(phase1_no_run_lanes)
                    if phase1_no_run_lanes
                    else "Downstream lanes report prior lane failed / missing run dir."
                ),
                "gate_outcome": "Show exact upstream repair order.",
            },
            {
                "priority": "PX",
                "recommendation": "Add a research freshness-age policy.",
                "evidence": str(research.get("past_fail_blocker") or "briefing freshness not observed"),
                "gate_outcome": "Warn or block by age threshold.",
            },
            {
                "priority": "PX",
                "recommendation": "Add research source class to the locked BCG and lane table.",
                "evidence": str(research.get("research_source_class") or "NOT_OBSERVED"),
                "gate_outcome": "Distinguish FRESH_APPS_RESEARCH, STATIC_MANUAL_BRIEF, and OPERATOR_SKIP.",
            },
            {
                "priority": "PX",
                "recommendation": "Compare latest run to prior passing research wiring when latest run uses a static/manual research path.",
                "evidence": "Prior runs may use artifacts/apps_research/.../briefing.md while this run used a static JSON brief.",
                "gate_outcome": "Surface regression automatically.",
            },
        ]
    )
    return rows


def _build_bcg_issue_tree(doc: dict[str, Any]) -> list[dict[str, Any]]:
    issue_rows: list[dict[str, Any]] = []
    research = _research_row(doc)
    if research.get("generation_status") == "P0_STATIC_MANUAL_BRIEF_USED":
        issue_rows.append(
            {
                "section": "research_briefing_input",
                "classification": "P0_STATIC_MANUAL_BRIEF_USED",
                "root_cause": "The run carried auto_research_internal=True but did not execute apps_research delegation.",
                "evidence": [
                    "research_delegation_executed=False",
                    str(research.get("past_fail_blocker") or ""),
                ],
                "causal_allocation": {},
                "required_implementation_plan": [
                    "Add a fail-closed gate requiring research_delegation_executed=True when auto_research_internal=True.",
                    "Require a fresh apps_research artifact path and run receipt before apps_rg consumes briefing content.",
                    "Render briefing source, freshness date, and apps_research execution status in row 0.",
                    "Block resume lane execution unless research is explicitly skipped or freshly completed.",
                ],
            }
        )
    for finding in doc.get("rca_findings", []):
        if not isinstance(finding, dict):
            continue
        issue_rows.append(
            {
                "section": str(finding.get("section") or ""),
                "classification": str(finding.get("classification") or ""),
                "root_cause": str(finding.get("root_cause") or ""),
                "evidence": [str(finding.get("evidence") or "")],
                "causal_allocation": finding.get("causal_allocation"),
                "required_implementation_plan": _validated_plan_items(finding),
            }
        )
    return issue_rows


def _build_inline_required_output(doc: dict[str, Any]) -> dict[str, Any]:
    summary = doc["result_summary"]
    counts = doc["section_counts"]
    research = _research_row(doc)
    final_out = doc.get("final_resume_output") if isinstance(doc.get("final_resume_output"), dict) else {}
    final_status = str(final_out.get("status") or "UNKNOWN")
    authorized = bool(summary.get("outcome_authorized")) and final_status == "PASS"
    resume_inline_authorized, _resume_inline_blockers = _resume_inline_authorization(doc)
    research_status = str(research.get("generation_status") or "NOT_OBSERVED")
    if research_status == "P0_STATIC_MANUAL_BRIEF_USED":
        executive_answer = (
            "The run is blocked and must not authorize a final resume. The first P0 failure is that "
            "research was expected but apps_research did not run; the run consumed a static manual "
            "brief instead. Resume generation also failed to produce authorized content: "
            f"{counts['ran_real_llm']} sections reported REAL_LLM, {counts['pre_run_blocked']} lanes "
            "were pre-run blocked, and final resume assembly contains gap markers."
        )
    elif authorized:
        executive_answer = "The run reached an authorized product outcome. Preserve the generated outputs and review the run ledger for section and judge proof."
    else:
        executive_answer = (
            "The run is blocked and must not authorize a final resume. Required generation and/or "
            "final product gates did not clear; use the P0/P1/PX recommendations below as the repair order."
        )
    board_rows = [
        {"question": "Did apps_research run?", "answer": "Yes" if research.get("provider_call_attempted") is True else "No"},
        {"question": "Research source class", "answer": str(research.get("research_source_class") or "NOT_OBSERVED")},
        {"question": "Research input used", "answer": str(research.get("primary_provider") or "NOT_OBSERVED")},
        {"question": "Briefing evidence", "answer": str(research.get("past_fail_blocker") or "NOT_OBSERVED")},
        {"question": "Did resume generation run?", "answer": f"{counts['ran_real_llm']} REAL_LLM section(s)"},
        {"question": "Final product authorized?", "answer": str(summary.get("outcome_authorized"))},
        {"question": "Primary blocker", "answer": str(research.get("generation_status") or summary.get("fault") or "NOT_OBSERVED")},
        {"question": "Decision", "answer": "Do not authorize; fix P0 gates first." if not authorized else "Authorized; preserve evidence."},
    ]
    evidence_map = [
        {"label": "Mandatory run ledger", "path": f"@{doc['run_root_abs']}\\{MANDATORY_RUN_OUTPUT_MD}"},
        {"label": "Machine-readable ledger", "path": f"@{doc['run_root_abs']}\\{MANDATORY_RUN_OUTPUT_JSON}"},
        {"label": "Final resume text", "path": f"@{doc['run_root_abs']}\\{FINAL_RESUME_OUTPUT_TXT}"},
        {"label": "Final resume output contract", "path": f"@{doc['run_root_abs']}\\{FINAL_RESUME_OUTPUT_JSON}"},
        {"label": "Resume DOCX", "path": f"@{doc['run_root_abs']}\\{FINAL_RESUME_DOCX_RELPATH}"},
    ]
    return {
        "schema_version": INLINE_REQUIRED_OUTPUT_SCHEMA_VERSION,
        "immutable_section_order": list(INLINE_REQUIRED_OUTPUT_SECTION_ORDER),
        "bcg": {
            "title": "BCG Executive Output - apps_rg Run",
            "section_order": list(BCG_LOCKED_SECTION_ORDER),
            "executive_answer": executive_answer,
            "p0_p1_px_recommendations": {
                "columns": list(BCG_RECOMMENDATION_COLUMNS),
                "rows": _build_bcg_recommendations(doc),
            },
            "board_level_readout": {
                "columns": list(BCG_BOARD_READOUT_COLUMNS),
                "rows": board_rows,
            },
            "issue_tree": _build_bcg_issue_tree(doc),
            "recommended_next_move": [
                "Fix P0 gates before rerun.",
                "Rerun the integrated apps_rg path only after research and first-lane generation are product-authorized or explicitly skipped.",
                "Treat final assembly as valid only when every required section and product output is product-authorized.",
            ],
            "evidence_map": evidence_map,
        },
        "section_lane_summary_table": {
            "title": "Section Lane Summary Table",
            "columns": list(SECTION_LANE_TABLE_COLUMNS),
            "rows": doc.get("section_lane_table") if isinstance(doc.get("section_lane_table"), list) else [],
        },
        "resume_docx_full_version_inline": {
            "title": "Resume DOCX Full Version Inline",
            "source": _resume_inline_source(doc, resume_inline_authorized),
            "text": _resume_inline_text(doc),
        },
    }


def _render_locked_bcg_from_inline(inline: dict[str, Any], doc: dict[str, Any]) -> str:
    bcg = inline.get("bcg") if isinstance(inline.get("bcg"), dict) else {}
    recs = bcg.get("p0_p1_px_recommendations") if isinstance(bcg.get("p0_p1_px_recommendations"), dict) else {}
    board = bcg.get("board_level_readout") if isinstance(bcg.get("board_level_readout"), dict) else {}
    lines = [
        f"# {bcg.get('title') or 'BCG Executive Output - apps_rg Run'}",
        "",
        f"Generated: `{doc['generated_at_utc']}`",
        f"Run root: `@{doc['run_root_abs']}`",
        "",
        "## Executive Answer",
        "",
        str(bcg.get("executive_answer") or ""),
        "",
        "## P0/P1/PX Recommendations",
        "",
        "| Priority | Recommendation | Evidence | Gate / Outcome |",
        "|---|---|---|---|",
    ]
    for row in recs.get("rows") if isinstance(recs.get("rows"), list) else []:
        if not isinstance(row, dict):
            continue
        lines.append(
            "| "
            f"`{_markdown_table_escape(row.get('priority'))}` | "
            f"{_markdown_table_escape(row.get('recommendation'))} | "
            f"`{_markdown_table_escape(row.get('evidence'))}` | "
            f"{_markdown_table_escape(row.get('gate_outcome'))} |"
        )
    lines.extend(
        [
            "",
            "## Board-Level Readout",
            "",
            "| Question | Answer |",
            "|---|---|",
        ]
    )
    for row in board.get("rows") if isinstance(board.get("rows"), list) else []:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| {_markdown_table_escape(row.get('question'))} | `{_markdown_table_escape(row.get('answer'))}` |"
        )
    lines.extend(["", "## Issue Tree", ""])
    issue_tree = bcg.get("issue_tree") if isinstance(bcg.get("issue_tree"), list) else []
    if not issue_tree:
        lines.append("- No blocking issue tree was generated from section evidence.")
    for issue in issue_tree:
        if not isinstance(issue, dict):
            continue
        lines.append(
            f"- `{issue.get('section')}`: {issue.get('classification')}"
        )
        lines.append(f"  - Root cause: {issue.get('root_cause') or '-'}")
        evidence = issue.get("evidence") if isinstance(issue.get("evidence"), list) else []
        for item in evidence:
            if str(item).strip():
                lines.append(f"  - Evidence: `{_markdown_table_escape(item)}`")
        allocation = issue.get("causal_allocation") if isinstance(issue.get("causal_allocation"), dict) else {}
        if allocation:
            lines.append("  - Causal allocation:")
            lines.append(f"    - Dominant cause: {allocation.get('dominant_cause') or '-'}")
            if allocation.get("retry_recoverability") or allocation.get("retry_recoverability_reason"):
                lines.append(
                    "    - Retry recoverability: "
                    f"`{allocation.get('retry_recoverability') or '-'}` - "
                    f"{allocation.get('retry_recoverability_reason') or '-'}"
                )
            alloc_rows = allocation.get("allocation") if isinstance(allocation.get("allocation"), list) else []
            for row in alloc_rows:
                if not isinstance(row, dict):
                    continue
                evidence_refs = ", ".join(str(ref) for ref in row.get("evidence_refs") or [])
                lines.append(
                    "    - "
                    f"`{row.get('domain')}` / `{row.get('causal_role')}` / "
                    f"`{row.get('work_share')}`: {row.get('root_cause_link')} "
                    f"Evidence: `{_markdown_table_escape(evidence_refs)}`. "
                    f"Required work: {row.get('required_work')}"
                )
        plan = (
            issue.get("required_implementation_plan")
            if isinstance(issue.get("required_implementation_plan"), list)
            else issue.get("implementation_plan")
            if isinstance(issue.get("implementation_plan"), list)
            else []
        )
        if plan:
            lines.append("  - Required implementation plan:")
            for item in plan:
                lines.append(f"    - {item}")
    lines.extend(["", "## Recommended Next Move", ""])
    for idx, item in enumerate(bcg.get("recommended_next_move") if isinstance(bcg.get("recommended_next_move"), list) else [], 1):
        lines.append(f"{idx}. {item}")
    lines.extend(["", "## Evidence Map", ""])
    for item in bcg.get("evidence_map") if isinstance(bcg.get("evidence_map"), list) else []:
        if not isinstance(item, dict):
            continue
        lines.append(f"- {item.get('label')}: `{item.get('path')}`")
    return "\n".join(lines)


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
    inline = doc.get("inline_required_output") if isinstance(doc.get("inline_required_output"), dict) else {}
    if inline:
        return _render_locked_bcg_from_inline(inline, doc)
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
    repo = (repo_root or find_repo_root(root)).resolve()
    sections = _collect_section_records(root, repo_root=repo, section_id=section_id)
    result_summary = _result_summary(result, root)
    final_required = _final_resume_output_required(root, result_summary)
    final_output = _load_json(root / FINAL_RESUME_OUTPUT_JSON)
    if not final_output:
        final_output = build_final_resume_output_contract(root, repo_root=repo, required=final_required)
    section_lane_table = _build_section_lane_table(root, sections, repo_root=repo)
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
    doc["inline_required_output"] = _build_inline_required_output(doc)
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
    repo = (repo_root or find_repo_root(root)).resolve()
    root.mkdir(parents=True, exist_ok=True)
    pre_summary = _result_summary(result, root)
    final_required = _final_resume_output_required(root, pre_summary)
    emit_final_resume_product_outputs(
        root,
        repo_root=repo,
        required=final_required,
    )
    doc = build_mandatory_run_output(
        root,
        repo_root=repo,
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
