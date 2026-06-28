"""Mandatory apps_rg run outputs.

Every apps_rg run must leave two human-facing artifacts:

* ``APPS_RG_MANDATORY_RUN_OUTPUT.md`` - operational ledger of what ran.
* ``BCG_EXECUTIVE_OUTPUT.md`` - decision-oriented RCA and next action.

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

MANDATORY_RUN_OUTPUT_JSON = "APPS_RG_MANDATORY_RUN_OUTPUT.json"
MANDATORY_RUN_OUTPUT_MD = "APPS_RG_MANDATORY_RUN_OUTPUT.md"
BCG_EXECUTIVE_OUTPUT_MD = "BCG_EXECUTIVE_OUTPUT.md"


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
    if pre_run and not failed_gates and blocker != "EXECUTED_X3_BLOCK":
        return f"Pre-run dependency blocked execution: {blocker}"
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
    if (run_root / "lanes").is_dir():
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
    terminal = _load_json(run_root / "terminal_ret_packet.json")
    terminal_payload = terminal.get("payload") if isinstance(terminal.get("payload"), dict) else {}
    exhaust = _load_json(run_root / "runtime_exhaust_bundle.json")
    exhaust_payload = exhaust.get("payload") if isinstance(exhaust.get("payload"), dict) else {}
    proof_gate = _load_json(run_root / "integrated_product_proof_gate_result.json")
    return {
        "exit_status": result.get("exit_status") or ("error" if terminal_payload.get("l2_fault") else "unknown"),
        "execution_status": result.get("execution_status") or ("failed" if terminal_payload.get("l2_fault") else "unknown"),
        "outcome_authorized": bool(result.get("outcome_authorized")),
        "x3_disposition": (
            result.get("x3_disposition")
            or terminal_payload.get("x3_disposition")
            or exhaust_payload.get("x3_disposition")
            or ""
        ),
        "fault": result.get("fault") or terminal_payload.get("l2_fault") or "",
        "run_id": result.get("run_id") or terminal_payload.get("run_id") or "",
        "request_id": result.get("request_id") or terminal_payload.get("request_id") or "",
        "proof_gate_status": proof_gate.get("status") or "",
        "proof_classification": proof_gate.get("proof_classification") or "",
        "decisive_reason": proof_gate.get("decisive_reason") or "",
    }


def _top_rca_sections(sections: list[dict[str, Any]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for section in sections:
        x3 = str(section.get("x3_code") or "")
        bucket = str(section.get("status_bucket") or "")
        failed = section.get("failed_gates") or []
        if x3 == "X3_ALLOW" and bucket not in {"pre_run_blocked", "not_run"}:
            continue
        if not failed and bucket not in {"pre_run_blocked", "not_run"} and x3 != "NOT_RUN":
            continue
        gate_text = ", ".join(str(g.get("gate_id")) for g in failed if isinstance(g, dict))
        findings.append(
            {
                "section": str(section.get("section") or ""),
                "classification": str(section.get("failure_classification") or ""),
                "evidence": gate_text or x3 or bucket,
                "action": _recommended_action(section),
            }
        )
    return findings


def _recommended_action(section: dict[str, Any]) -> str:
    classification = str(section.get("failure_classification") or "").lower()
    section_id = str(section.get("section") or "")
    if "output contract" in classification:
        return "Fix provider output contract, token budget, parsing, and claim-ledger emission before rerun."
    if "specificity" in classification:
        return "Regenerate or repair text with an accepted mechanism/technology token."
    if "evidence mapping" in classification:
        return "Repair source-fact, graph lineage, and per-term claim ledger coverage."
    if "pre-run" in classification:
        return "Resolve upstream lane and rerun this dependent section."
    if section_id == FINAL_AGGREGATION_LANE:
        return "Run final aggregation only after all required sections are product-authorized."
    return "Inspect failed gates and rerun after targeted remediation."


def _markdown_table_escape(value: Any) -> str:
    return str(value if value is not None else "-").replace("|", "\\|").replace("\n", " ")


def _render_mandatory_markdown(doc: dict[str, Any]) -> str:
    summary = doc["result_summary"]
    sections = doc["sections"]
    counts = doc["section_counts"]
    rca = doc["rca_findings"]
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
        "## Section Execution Ledger",
        "",
        "| Section | Ran status | X3 | X2 | Product | Runtime | Failed gates | Display |",
        "|---|---|---|---|---|---|---|---|",
    ]
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
            lines.append(
                f"{idx}. `{finding['section']}` - {finding['classification']} "
                f"Evidence: `{_markdown_table_escape(finding['evidence'])}`. "
                f"Action: {finding['action']}"
            )
    lines.extend(["", "## L6 Shadow Observability", ""])
    lines.append("| Section | L6 files | Authority |")
    lines.append("|---|---:|---|")
    for section in sections:
        l6 = section.get("l6") or {}
        lines.append(
            f"| `{section.get('section')}` | {int(l6.get('file_count') or 0)} | `{l6.get('product_authority') or '-'}` |"
        )
    return "\n".join(lines)


def _render_bcg_markdown(doc: dict[str, Any]) -> str:
    summary = doc["result_summary"]
    sections = doc["sections"]
    counts = doc["section_counts"]
    rca = doc["rca_findings"]
    failed_count = counts["blocked"] + counts["pre_run_blocked"] + counts["not_run"]
    if summary.get("outcome_authorized"):
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
        f"| What blocked the run? | `{_markdown_table_escape(summary.get('fault') or summary.get('decisive_reason') or 'section gates / aggregation')}` |",
        f"| Primary decision | `Fix targeted blockers and rerun; do not weaken X2/X3 gates.` |",
        "",
        "## Run Scorecard",
        "",
        "| Section | Result | Interpretation | Action |",
        "|---|---|---|---|",
    ]
    for section in sections:
        x3 = str(section.get("x3_code") or "")
        bucket = str(section.get("status_bucket") or "")
        if x3 == "X3_ALLOW":
            interp = "Usable candidate content; still subject to whole-run assembly."
        elif bucket == "pre_run_blocked":
            interp = "Did not become eligible because an upstream dependency failed."
        elif bucket == "not_run":
            interp = "Did not run in this execution path."
        else:
            interp = str(section.get("failure_classification") or "Requires review.")
        lines.append(
            f"| `{section.get('section')}` | `{x3 or bucket}` | "
            f"{_markdown_table_escape(interp)} | {_markdown_table_escape(_recommended_action(section))} |"
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
    lines.extend(["", "## Recommended Next Move", ""])
    lines.append("1. Fix the P0 blocker sections named above.")
    lines.append("2. Rerun the integrated apps_rg path with the same JD and briefing.")
    lines.append("3. Treat final assembly as valid only when every required section is product-authorized.")
    lines.extend(["", "## Evidence Map", ""])
    lines.append(f"- Mandatory run ledger: `@{doc['run_root_abs']}\\{MANDATORY_RUN_OUTPUT_MD}`")
    lines.append(f"- Machine-readable ledger: `@{doc['run_root_abs']}\\{MANDATORY_RUN_OUTPUT_JSON}`")
    lines.append(f"- Section status: `@{doc['run_root_abs']}\\full_run_section_status.json`")
    lines.append(f"- Review bundle: `@{doc['run_root_abs']}\\review_bundle.zip`")
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
    doc = {
        "schema_version": "apps_rg.mandatory_run_output.v1",
        "generated_at_utc": _utc_now(),
        "run_root_abs": str(root),
        "run_root": _repo_rel(root, repo),
        "result_summary": _result_summary(result, root),
        "section_counts": _count_sections(sections),
        "sections": sections,
        "rca_findings": _top_rca_sections(sections),
        "mandatory_artifacts": {
            "bcg_executive_output_md": BCG_EXECUTIVE_OUTPUT_MD,
            "mandatory_run_output_md": MANDATORY_RUN_OUTPUT_MD,
            "mandatory_run_output_json": MANDATORY_RUN_OUTPUT_JSON,
        },
    }
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
    _write_text(bcg_path, _render_bcg_markdown(doc))
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
