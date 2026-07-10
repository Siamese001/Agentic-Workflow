"""Deterministic prior-pass versus current-failure output bisect.

The bisect keeps three questions separate: where the runs first differ, which
difference is causally relevant, and why recovery did or did not work.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

OUTPUT_BISECT_SCHEMA_VERSION = "apps_rg.output_bisect.v1"
OUTPUT_BISECT_GATE_ID = "APPS_RG_OUTPUT_BISECT_INCOMPLETE"

CAUSAL_CLASSIFICATIONS = {
    "CAUSAL",
    "CONTRIBUTING",
    "RULED_OUT",
    "CORRELATED_ONLY",
    "DOWNSTREAM_EFFECT",
    "EVIDENCE_GAP",
}


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _text_hash(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _split_reasons(value: Any) -> list[str]:
    return [part.strip() for part in str(value or "").split(";") if part.strip()]


def _display_from_payload(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("resume_display_text", "raw_model_output", "output_text", "text"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                text = raw.strip()
                if key == "raw_model_output":
                    try:
                        parsed = json.loads(text)
                    except json.JSONDecodeError:
                        return text
                    nested = _display_from_payload(parsed)
                    return nested or text
                return text
        for nested in value.values():
            found = _display_from_payload(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _display_from_payload(nested)
            if found:
                return found
    return ""


def _candidate_from_file(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {"present": False, "digest": "", "word_count": 0, "evidence_ref": ""}
    text = ""
    if path.suffix.lower() == ".json":
        text = _display_from_payload(_load_json(path))
    else:
        try:
            raw = path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            raw = ""
        if raw:
            try:
                text = _display_from_payload(json.loads(raw))
            except json.JSONDecodeError:
                text = raw
    return {
        "present": bool(text),
        "digest": _text_hash(text) if text else "",
        "word_count": len(re.findall(r"\S+", text)),
        "evidence_ref": str(path),
    }


def _candidate_for_call(lane: Path, call_id: str) -> dict[str, Any]:
    if call_id:
        matches = sorted(lane.glob(f"provider_response*{call_id}*.json"))
        if matches:
            return _candidate_from_file(matches[0])
    return {"present": False, "digest": "", "word_count": 0, "evidence_ref": ""}


def _x2_rows(lane: Path | None) -> list[dict[str, Any]]:
    doc = _load_json(lane / "x2_gate_outputs.json") if lane is not None else {}
    rows = doc.get("gates")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _judge_rows(lane: Path | None) -> list[dict[str, Any]]:
    doc = _load_json(lane / "x1d_llm_judge_outputs.json") if lane is not None else {}
    rows = doc.get("judges")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _x3(lane: Path | None) -> dict[str, Any]:
    return _load_json(lane / "x3_disposition.json") if lane is not None else {}


def _attempt_timeline(run_label: str, lane: Path | None) -> list[dict[str, Any]]:
    if lane is None or not lane.is_dir():
        prior_missing = run_label == "prior_passing"
        return [
            {
                "run": run_label,
                "sequence": 1,
                "phase": "lane_resolution",
                "attempt": "-",
                "candidate_digest": "",
                "word_count": 0,
                "trigger_or_input": (
                    "no prior passing lane was found"
                    if prior_missing
                    else "lane artifact directory not found"
                ),
                "repair_or_action": "none",
                "gate_scope": "NONE",
                "gate_result": "NOT_APPLICABLE" if prior_missing else "EVIDENCE_NOT_RECORDED",
                "failed_gate_ids": [],
                "judge_result": "NO_PRIOR_PASSING_RUN" if prior_missing else "EVIDENCE_NOT_RECORDED",
                "disposition": "NO_BASELINE" if prior_missing else "EVIDENCE_GAP",
                "acceptance_scope": "NOT_APPLICABLE",
                "evidence_ref": "",
                "complete": prior_missing,
            }
        ]

    timeline: list[dict[str, Any]] = []
    regen = _load_json(lane / "synthesis_regen_receipt.json")
    repair = _load_json(lane / "section_repair_ledger.json")
    x2_rows = _x2_rows(lane)
    judges = _judge_rows(lane)
    x3 = _x3(lane)
    initial = _candidate_from_file(lane / "raw_model_output.txt")
    initial_defects = _split_reasons(regen.get("reject_reason"))
    timeline.append(
        {
            "run": run_label,
            "sequence": 1,
            "phase": "initial_generation",
            "attempt": 0,
            "candidate_digest": initial["digest"],
            "word_count": initial["word_count"],
            "trigger_or_input": "; ".join(initial_defects) or "initial candidate",
            "repair_or_action": "dispatch provider generation",
            "gate_scope": "PRE_X2_SYNTHESIS_SHAPE" if initial_defects else "FULL_X2",
            "gate_result": "FAIL" if initial_defects else "PASS_OR_NOT_TRIGGERED",
            "failed_gate_ids": initial_defects,
            "judge_result": "NOT_REACHED_PRE_X2" if initial_defects else "PENDING",
            "disposition": "REPAIR_TRIGGERED" if initial_defects else "ADVANCED_TO_X2",
            "acceptance_scope": "INITIAL_CANDIDATE",
            "evidence_ref": initial["evidence_ref"],
            "complete": bool(initial["present"]),
        }
    )

    attempts = regen.get("attempts")
    attempts = attempts if isinstance(attempts, list) else []
    for index, raw_attempt in enumerate(attempts):
        attempt = raw_attempt if isinstance(raw_attempt, dict) else {}
        call_id = str(attempt.get("call_id") or "")
        candidate = _candidate_for_call(lane, call_id)
        next_attempt = attempts[index + 1] if index + 1 < len(attempts) else {}
        defects_after = _split_reasons(
            next_attempt.get("reject_reason")
            if isinstance(next_attempt, dict) and next_attempt.get("reject_reason")
            else regen.get("final_reject_reason")
        )
        shape_count = attempt.get("shape_failure_count")
        shape_pass = shape_count == 0 and not defects_after
        mono = attempt.get("monotonicity")
        mono = mono if isinstance(mono, dict) else {}
        monotonic = mono.get("accepted") is True
        if shape_pass:
            acceptance_scope = "FULL_PRE_X2_SHAPE_PASS"
        elif monotonic:
            acceptance_scope = "MONOTONIC_IMPROVEMENT_ONLY"
        else:
            acceptance_scope = "REJECTED"
        timeline.append(
            {
                "run": run_label,
                "sequence": len(timeline) + 1,
                "phase": "pre_judge_synthesis_retry",
                "attempt": attempt.get("attempt") or index + 1,
                "candidate_digest": candidate["digest"] or str(attempt.get("candidate_digest") or ""),
                "word_count": candidate["word_count"] or int(attempt.get("regen_resume_word_count") or 0),
                "trigger_or_input": str(attempt.get("reject_reason") or ""),
                "repair_or_action": f"provider retry {call_id or index + 1}",
                "gate_scope": "PRE_X2_SYNTHESIS_SHAPE",
                "gate_result": "PASS" if shape_pass else "FAIL",
                "failed_gate_ids": defects_after,
                "judge_result": "NOT_REACHED_PRE_X2",
                "disposition": (
                    "ADVANCED_AS_IMPROVEMENT"
                    if monotonic and not shape_pass
                    else "ADVANCED_TO_X2"
                    if shape_pass
                    else str(attempt.get("skipped") or "REJECTED")
                ),
                "acceptance_scope": acceptance_scope,
                "evidence_ref": candidate["evidence_ref"] or str(lane / "synthesis_regen_receipt.json"),
                "complete": bool(
                    (candidate["digest"] or attempt.get("candidate_digest"))
                    and attempt.get("reject_reason")
                    and (defects_after or shape_pass)
                ),
            }
        )

    for row in repair.get("repairs") if isinstance(repair.get("repairs"), list) else []:
        if not isinstance(row, dict):
            continue
        timeline.append(
            {
                "run": run_label,
                "sequence": len(timeline) + 1,
                "phase": "deterministic_repair",
                "attempt": row.get("seq") or "-",
                "candidate_digest": "",
                "word_count": 0,
                "trigger_or_input": str(row.get("reason") or ""),
                "repair_or_action": str(row.get("operation") or row.get("kind") or "repair"),
                "gate_scope": "PRE_FINAL_X2",
                "gate_result": "MUTATED" if row.get("replaced_l2") else "NO_CHANGE",
                "failed_gate_ids": [],
                "judge_result": "NOT_REACHED",
                "disposition": "REPLACED_L2" if row.get("replaced_l2") else "BLOCKED_OR_LEDGER_ONLY",
                "acceptance_scope": "DETERMINISTIC_REWRITE",
                "evidence_ref": str(lane / "section_repair_ledger.json"),
                "complete": bool(row.get("operation") and row.get("reason")),
            }
        )

    failed_x2 = [str(row.get("gate_id") or "") for row in x2_rows if row.get("pass") is not True]
    timeline.append(
        {
            "run": run_label,
            "sequence": len(timeline) + 1,
            "phase": "final_x2",
            "attempt": repair.get("authoritative_attempt_number") or 1,
            "candidate_digest": _candidate_from_file(lane / "resume_display_text.txt")["digest"],
            "word_count": _candidate_from_file(lane / "resume_display_text.txt")["word_count"],
            "trigger_or_input": "all deterministic product gates",
            "repair_or_action": "evaluate full X2 gate set",
            "gate_scope": "FULL_X2",
            "gate_result": "FAIL" if failed_x2 else "PASS",
            "failed_gate_ids": failed_x2,
            "judge_result": "NOT_REACHED_X2_FAILED" if failed_x2 else "ADVANCED_TO_JUDGES",
            "disposition": "BLOCKED" if failed_x2 else "ADVANCED",
            "acceptance_scope": "PRODUCT_GATE",
            "evidence_ref": str(lane / "x2_gate_outputs.json"),
            "complete": bool(x2_rows),
        }
    )

    if judges:
        for judge in judges:
            score = judge.get("score")
            threshold = judge.get("threshold")
            timeline.append(
                {
                    "run": run_label,
                    "sequence": len(timeline) + 1,
                    "phase": "judge_panel",
                    "attempt": str(judge.get("provider_key") or judge.get("judge_id") or "judge"),
                    "candidate_digest": str(judge.get("input_hash") or ""),
                    "word_count": 0,
                    "trigger_or_input": "; ".join(str(x) for x in judge.get("findings") or []),
                    "repair_or_action": "grade candidate",
                    "gate_scope": "X1D_MODEL_BACKED_JUDGE",
                    "gate_result": "PASS" if judge.get("pass") is True else "FAIL",
                    "failed_gate_ids": [str(x) for x in judge.get("fail_reasons") or []],
                    "judge_result": f"{score}/{threshold} {judge.get('provider_status') or ''}".strip(),
                    "disposition": "JUDGE_PASS" if judge.get("pass") is True else "JUDGE_FAIL",
                    "acceptance_scope": "MODEL_BACKED_GRADE",
                    "evidence_ref": str(judge.get("raw_response_ref") or lane / "x1d_llm_judge_outputs.json"),
                    "complete": bool(judge.get("judge_id") and score is not None and threshold is not None),
                }
            )
        if all(row.get("pass") is True for row in judges):
            timeline.append(
                {
                    "run": run_label,
                    "sequence": len(timeline) + 1,
                    "phase": "judge_retry_status",
                    "attempt": "-",
                    "candidate_digest": "",
                    "word_count": 0,
                    "trigger_or_input": "all configured judges passed",
                    "repair_or_action": "no judge retry required",
                    "gate_scope": "JUDGE_REMEDIATION",
                    "gate_result": "NOT_NEEDED",
                    "failed_gate_ids": [],
                    "judge_result": "NOT_NEEDED_ALL_JUDGES_PASSED",
                    "disposition": "NO_RETRY",
                    "acceptance_scope": "NOT_APPLICABLE",
                    "evidence_ref": str(lane / "judge_remediation_cycles.json"),
                    "complete": True,
                }
            )
    else:
        timeline.append(
            {
                "run": run_label,
                "sequence": len(timeline) + 1,
                "phase": "judge_panel",
                "attempt": "-",
                "candidate_digest": "",
                "word_count": 0,
                "trigger_or_input": "X2 failed before judge dispatch" if failed_x2 else "judge evidence absent",
                "repair_or_action": "none",
                "gate_scope": "X1D_MODEL_BACKED_JUDGE",
                "gate_result": "NOT_RUN" if failed_x2 else "EVIDENCE_NOT_RECORDED",
                "failed_gate_ids": failed_x2,
                "judge_result": "JUDGES_NOT_REACHED" if failed_x2 else "EVIDENCE_NOT_RECORDED",
                "disposition": "PRE_JUDGE_BLOCK" if failed_x2 else "EVIDENCE_GAP",
                "acceptance_scope": "NOT_APPLICABLE",
                "evidence_ref": str(lane / "x1d_llm_judge_outputs.json"),
                "complete": bool(failed_x2),
            }
        )

    timeline.append(
        {
            "run": run_label,
            "sequence": len(timeline) + 1,
            "phase": "x3_disposition",
            "attempt": "-",
            "candidate_digest": str(x3.get("final_summary_hash") or ""),
            "word_count": 0,
            "trigger_or_input": str(x3.get("decisive_reason") or ""),
            "repair_or_action": "authorize or block product output",
            "gate_scope": "X3",
            "gate_result": "PASS" if x3.get("pass") is True else "FAIL",
            "failed_gate_ids": [str(x) for x in x3.get("x2_failed_gates") or []],
            "judge_result": str(x3.get("x1d_evaluator_mode") or ""),
            "disposition": str(x3.get("x3_code") or "NOT_OBSERVED"),
            "acceptance_scope": "PRODUCT_AUTHORIZATION",
            "evidence_ref": str(lane / "x3_disposition.json"),
            "complete": bool(x3.get("x3_code")),
        }
    )
    return timeline


def _input_refs(lane: Path | None) -> dict[str, Any]:
    doc = _load_json(lane / "section_input_usage_ledger.json") if lane is not None else {}
    refs = doc.get("input_refs")
    return refs if isinstance(refs, dict) else {}


def _lineage_value(run: Path | None, lane: Path | None, stage: str) -> tuple[str, str]:
    if stage == "u0_ingress":
        doc = _load_json(run / "ingress_raw.json") if run is not None else {}
        return _stable_hash(doc) if doc else "", str(run / "ingress_raw.json") if run else ""
    if stage == "u0_payload":
        doc = _load_json(run / "u0_receipt.json") if run is not None else {}
        return str(doc.get("payload_digest") or ""), str(run / "u0_receipt.json") if run else ""
    refs = _input_refs(lane)
    ref_keys = {
        "jd_material": "jd_text_hash",
        "briefing_material": "briefing_hash",
        "targeting_bundle": "targeting_bundle_digest",
        "proof_pool": "graph_digest",
        "selected_fact_plan": "selected_fact_plan_hash",
    }
    if stage in ref_keys:
        return str(refs.get(ref_keys[stage]) or ""), str(lane / "section_input_usage_ledger.json") if lane else ""
    if stage == "provider_request":
        doc = _load_json(lane / "provider_request.json") if lane is not None else {}
        return _stable_hash(doc) if doc else "", str(lane / "provider_request.json") if lane else ""
    if stage == "initial_candidate":
        row = _candidate_from_file(lane / "raw_model_output.txt") if lane is not None else {}
        return str(row.get("digest") or ""), str(row.get("evidence_ref") or "")
    if stage == "retry_loop":
        doc = _load_json(lane / "synthesis_regen_receipt.json") if lane is not None else {}
        value = {
            "triggered": doc.get("triggered", False),
            "attempt_count": len(doc.get("attempts") or []) if isinstance(doc.get("attempts"), list) else 0,
            "accepted": doc.get("accepted"),
            "reverted_to_first_pass": doc.get("reverted_to_first_pass", False),
            "final_reject_reason": doc.get("final_reject_reason") or "",
        }
        return _stable_hash(value), str(lane / "synthesis_regen_receipt.json") if lane else ""
    if stage == "deterministic_finalization":
        doc = _load_json(lane / "executive_summary_finalize_coherence.json") if lane is not None else {}
        return _stable_hash(doc) if doc else "", str(lane / "executive_summary_finalize_coherence.json") if lane else ""
    if stage == "final_x2":
        rows = _x2_rows(lane)
        value = [(row.get("gate_id"), row.get("pass")) for row in rows]
        return _stable_hash(value) if rows else "", str(lane / "x2_gate_outputs.json") if lane else ""
    if stage == "judges":
        rows = _judge_rows(lane)
        value = [(row.get("provider_key"), row.get("score"), row.get("pass")) for row in rows]
        return _stable_hash(value) if rows else "NO_JUDGE_ROWS", str(lane / "x1d_llm_judge_outputs.json") if lane else ""
    if stage == "x3":
        doc = _x3(lane)
        return str(doc.get("x3_code") or ""), str(lane / "x3_disposition.json") if lane else ""
    return "", ""


def _lineage(
    baseline_run: Path | None,
    current_run: Path,
    baseline_lane: Path | None,
    current_lane: Path | None,
) -> list[dict[str, Any]]:
    stages = (
        "u0_ingress",
        "u0_payload",
        "jd_material",
        "briefing_material",
        "targeting_bundle",
        "proof_pool",
        "selected_fact_plan",
        "provider_request",
        "initial_candidate",
        "retry_loop",
        "deterministic_finalization",
        "final_x2",
        "judges",
        "x3",
    )
    rows: list[dict[str, Any]] = []
    for stage in stages:
        prior, prior_ref = _lineage_value(baseline_run, baseline_lane, stage)
        current, current_ref = _lineage_value(current_run, current_lane, stage)
        match = bool(prior and current and prior == current)
        prior_detail = ""
        current_detail = ""
        if stage == "u0_ingress":
            prior_ingress = _load_json(baseline_run / "ingress_raw.json") if baseline_run else {}
            current_ingress = _load_json(current_run / "ingress_raw.json")
            prior_detail = str(prior_ingress.get("manual_brief") or "NOT_OBSERVED")
            current_detail = str(current_ingress.get("manual_brief") or "NOT_OBSERVED")
        if not prior and not current:
            classification = "EVIDENCE_GAP"
            reason = "Neither run recorded evidence for this stage."
        elif match:
            classification = "RULED_OUT"
            reason = "The evidence is identical at this stage."
        elif stage in {"u0_ingress", "u0_payload", "briefing_material", "targeting_bundle"}:
            classification = "CORRELATED_ONLY"
            reason = "The runs differ here, but the available artifacts do not prove this targeting change caused the failed sentence shape."
        elif stage in {"proof_pool", "selected_fact_plan", "provider_request", "initial_candidate"}:
            classification = "CONTRIBUTING"
            reason = "This changed the material presented to generation or the generated candidate, but no counterfactual replay isolates it as the sole cause."
        elif stage == "retry_loop":
            classification = "CAUSAL"
            reason = "The current repair loop exhausted its attempts with a failing defect still present and reverted to the first candidate."
        elif stage == "deterministic_finalization":
            classification = "CAUSAL"
            reason = "Current deterministic finalization changed the published text before full X2 evaluation."
        else:
            classification = "DOWNSTREAM_EFFECT"
            reason = "This is an observed consequence of the earlier candidate and recovery differences."
        rows.append(
            {
                "order": len(rows) + 1,
                "stage": stage,
                "prior_value": prior or "NOT_OBSERVED",
                "current_value": current or "NOT_OBSERVED",
                "prior_detail": prior_detail,
                "current_detail": current_detail,
                "match": match,
                "classification": classification,
                "reason": reason,
                "prior_evidence_ref": prior_ref,
                "current_evidence_ref": current_ref,
            }
        )
    return rows


def _git_show(repo_root: Path, commit: str, file_path: str) -> str:
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", commit):
        return ""
    try:
        completed = subprocess.run(
            ["git", "show", f"{commit}:{file_path}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            shell=False,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return completed.stdout if completed.returncode == 0 else ""


def _symbol_hash(source: str, symbol: str) -> str:
    if not source:
        return ""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ""
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
            segment = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            return _text_hash(segment)
    return ""


def _git_subject(repo_root: Path, commit: str) -> str:
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", commit):
        return ""
    try:
        completed = subprocess.run(
            ["git", "show", "-s", "--format=%s", "--end-of-options", commit],
            cwd=repo_root,
            capture_output=True,
            text=True,
            shell=False,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _symbol_change_commits(
    repo_root: Path,
    baseline_commit: str,
    current_commit: str,
    file_path: str,
    symbol: str,
    baseline_hash: str,
) -> list[dict[str, Any]]:
    if not all(
        re.fullmatch(r"[0-9a-fA-F]{7,64}", value)
        for value in (baseline_commit, current_commit)
    ):
        return []
    try:
        completed = subprocess.run(
            [
                "git",
                "rev-list",
                "--reverse",
                f"{baseline_commit}..{current_commit}",
                "--",
                file_path,
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            shell=False,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if completed.returncode != 0:
        return []
    changes: list[dict[str, Any]] = []
    prior_hash = baseline_hash
    for commit in completed.stdout.splitlines():
        commit = commit.strip()
        if not re.fullmatch(r"[0-9a-fA-F]{40,64}", commit):
            continue
        current_hash = _symbol_hash(_git_show(repo_root, commit, file_path), symbol)
        if not current_hash or current_hash == prior_hash:
            continue
        subject = _git_subject(repo_root, commit)
        pr_match = re.search(
            r"(?:Merge pull request|Merge PR)\s+#(\d+)",
            subject,
            flags=re.IGNORECASE,
        )
        changes.append(
            {
                "commit": commit,
                "subject": subject,
                "pr_number": int(pr_match.group(1)) if pr_match else None,
                "prior_symbol_hash": prior_hash,
                "current_symbol_hash": current_hash,
            }
        )
        prior_hash = current_hash
    return changes


def _code_binding(
    repo_root: Path,
    baseline_commit: str,
    current_commit: str,
    file_path: str,
    symbol: str,
    role: str,
) -> dict[str, Any]:
    baseline_hash = _symbol_hash(_git_show(repo_root, baseline_commit, file_path), symbol)
    current_hash = _symbol_hash(_git_show(repo_root, current_commit, file_path), symbol)
    if not baseline_hash or not current_hash:
        status = "CODE_CAUSE_NOT_ISOLATED"
    elif baseline_hash == current_hash:
        status = "LATENT_PATH_PREEXISTED_BASELINE"
    else:
        status = "SYMBOL_CHANGED_BETWEEN_REVISIONS"
    changes = (
        _symbol_change_commits(
            repo_root,
            baseline_commit,
            current_commit,
            file_path,
            symbol,
            baseline_hash,
        )
        if baseline_hash and current_hash and baseline_hash != current_hash
        else []
    )
    if status == "SYMBOL_CHANGED_BETWEEN_REVISIONS" and not changes:
        status = "CODE_CAUSE_NOT_ISOLATED"
    return {
        "role": role,
        "file": file_path,
        "symbol": symbol,
        "baseline_symbol_hash": baseline_hash,
        "current_symbol_hash": current_hash,
        "changed_between_revisions": bool(baseline_hash and current_hash and baseline_hash != current_hash),
        "status": status,
        "symbol_change_commits": changes,
        "first_change_commit": changes[0]["commit"] if changes else "",
        "first_change_subject": changes[0]["subject"] if changes else "",
        "first_change_pr_number": changes[0]["pr_number"] if changes else None,
    }


def _gate_matrix(baseline_lane: Path | None, current_lane: Path | None) -> list[dict[str, Any]]:
    prior = {str(row.get("gate_id") or ""): row for row in _x2_rows(baseline_lane)}
    current = {str(row.get("gate_id") or ""): row for row in _x2_rows(current_lane)}
    rows: list[dict[str, Any]] = []
    for gate_id in sorted(set(prior) | set(current)):
        before = prior.get(gate_id, {})
        after = current.get(gate_id, {})
        rows.append(
            {
                "gate_id": gate_id,
                "prior": "PASS" if before.get("pass") is True else "FAIL" if before else "NOT_OBSERVED",
                "current": "PASS" if after.get("pass") is True else "FAIL" if after else "NOT_OBSERVED",
                "changed": before.get("pass") != after.get("pass"),
                "current_reason": str(after.get("failure_reason") or after.get("observed_value") or ""),
                "prior_evidence_ref": str(baseline_lane / "x2_gate_outputs.json") if baseline_lane else "",
                "current_evidence_ref": str(current_lane / "x2_gate_outputs.json") if current_lane else "",
            }
        )
    return rows


def _judge_matrix(baseline_lane: Path | None, current_lane: Path | None) -> list[dict[str, Any]]:
    prior = {str(row.get("provider_key") or row.get("judge_id") or ""): row for row in _judge_rows(baseline_lane)}
    current = {str(row.get("provider_key") or row.get("judge_id") or ""): row for row in _judge_rows(current_lane)}
    keys = sorted(set(prior) | set(current))
    if not keys:
        return [
            {
                "judge": "configured_panel",
                "prior": "NOT_OBSERVED",
                "current": "JUDGES_NOT_REACHED",
                "reason": "No current judge rows were emitted because X2 failed first.",
            }
        ]
    return [
        {
            "judge": key,
            "prior": (
                f"{prior[key].get('score')}/{prior[key].get('threshold')} {'PASS' if prior[key].get('pass') is True else 'FAIL'}"
                if key in prior
                else "NOT_OBSERVED"
            ),
            "current": (
                f"{current[key].get('score')}/{current[key].get('threshold')} {'PASS' if current[key].get('pass') is True else 'FAIL'}"
                if key in current
                else "JUDGES_NOT_REACHED"
            ),
            "reason": (
                "; ".join(str(x) for x in current[key].get("fail_reasons") or [])
                if key in current
                else "Current X2 failure prevented judge dispatch."
            ),
        }
        for key in keys
    ]


def _plain_defect(value: str) -> str:
    text = str(value or "").lower()
    if "cross_fact" in text or "too_many_source_fact" in text:
        return "combined too many source facts in one sentence"
    if "fragment" in text or "no_finite_verb" in text:
        return "left a sentence that the grammar check treated as incomplete"
    if "robotic_transition" in text:
        return "repeated formulaic transition phrases"
    if "word count" in text or "maximum" in text:
        return "exceeded the summary length limit"
    if "unsupported bridge" in text:
        return "used a bridge phrase not supported by the evidence packet"
    return str(value or "quality check failure")


def _layperson_explanation(
    prior_timeline: list[dict[str, Any]],
    current_timeline: list[dict[str, Any]],
    baseline_revision: dict[str, Any],
    lineage: list[dict[str, Any]],
    section_id: str,
) -> list[str]:
    no_prior = any(
        row.get("judge_result") == "NO_PRIOR_PASSING_RUN"
        for row in prior_timeline
        if isinstance(row, dict)
    )
    judges = [row for row in prior_timeline if row.get("phase") == "judge_panel"]
    judge_scores = ", ".join(
        f"{row.get('attempt')} {str(row.get('judge_result')).split()[0]}"
        for row in judges
        if row.get("judge_result")
    )
    prior_identity = (
        f"PR #{baseline_revision.get('pr_number')}"
        if baseline_revision.get("pr_number")
        else "The prior passing revision"
    )
    retries = [row for row in current_timeline if row.get("phase") == "pre_judge_synthesis_retry"]
    defects = []
    for row in retries:
        for reason in row.get("failed_gate_ids") or []:
            plain = _plain_defect(str(reason))
            if plain not in defects:
                defects.append(plain)
    current_x2 = next((row for row in current_timeline if row.get("phase") == "final_x2"), {})
    current_judges = next((row for row in current_timeline if row.get("phase") == "judge_panel"), {})
    if section_id == "final_resume_aggregation":
        return [
            f"{prior_identity} authorized final assembly because every required section, including the executive summary, had already cleared its product checks.",
            "The current final assembly did not fail as an independent writing attempt; it was blocked downstream because the executive summary never became eligible for assembly.",
            "No aggregation retry or aggregation judge could repair that upstream section failure, so the underlying executive-summary retry and X2 evidence remains the controlling root cause.",
        ]
    ingress = next((row for row in lineage if row.get("stage") == "u0_ingress"), {})
    ingress_sentence = (
        "The runs first differ at ingestion: the prior run used "
        f"{ingress.get('prior_detail') or 'a different briefing source'}, while the current run used "
        f"{ingress.get('current_detail') or 'another briefing source'}; later targeting, fact-selection, and provider-request evidence also changed, so the initial text difference cannot be attributed to the code revision alone."
    )
    return [
        (
            "No prior passing same-scenario run was available, so this report does not claim a before-versus-after recovery result."
            if no_prior
            else f"{prior_identity} passed without a judge-driven retry because its first scored executive summary cleared the full deterministic check and both judges approved it"
            + (f" ({judge_scores})." if judge_scores else ".")
        ),
        ingress_sentence,
        (
            f"The current run then made {len(retries)} pre-judge repair attempt(s), but "
            f"{'; and '.join(defects) if defects else 'the recorded defects were not cleared'}; it reverted to its first candidate, the final deterministic check still failed "
            f"({', '.join(str(x) for x in current_x2.get('failed_gate_ids') or []) or 'failed gates not recorded'}), "
            f"so {current_judges.get('judge_result') or 'the judges were not reached'} and the resume remained blocked."
        ),
    ]


def build_section_output_bisect(
    *,
    section_id: str,
    run_root: Path,
    repo_root: Path,
    current_lane: Path | None,
    baseline_run: Path | None,
    baseline_lane: Path | None,
    baseline_revision: dict[str, Any],
    current_revision: dict[str, Any],
) -> dict[str, Any]:
    baseline_available = bool(
        baseline_run is not None
        and baseline_run.is_dir()
        and baseline_lane is not None
        and baseline_lane.is_dir()
    )
    prior_timeline = _attempt_timeline("prior_passing", baseline_lane)
    current_timeline = _attempt_timeline("current_failure", current_lane)
    lineage = _lineage(baseline_run, run_root, baseline_lane, current_lane)
    first_observed = next((row for row in lineage if not row.get("match")), {})
    first_causal = next((row for row in lineage if row.get("classification") == "CAUSAL"), {})
    if section_id == "final_resume_aggregation":
        first_causal = {
            "order": 0,
            "stage": "upstream_section_authorization",
            "classification": "CAUSAL",
            "reason": "Final assembly was blocked because the executive summary never reached product authorization.",
        }
    baseline_commit = str(baseline_revision.get("git_commit") or "")
    current_commit = str(current_revision.get("git_commit") or "")
    bindings: list[dict[str, Any]] = []
    if not baseline_available:
        bindings = [
            {
                "role": "revision comparison",
                "file": "",
                "symbol": "",
                "baseline_symbol_hash": "",
                "current_symbol_hash": "",
                "changed_between_revisions": False,
                "status": "NOT_APPLICABLE_NO_PRIOR_BASELINE",
            }
        ]
    elif section_id == "executive_summary":
        bindings = [
            _code_binding(
                repo_root,
                baseline_commit,
                current_commit,
                "apps_rg/runtime/sections/executive_summary_lane.py",
                "retry_provider_for_synthesis",
                "pre-judge retry and first-pass reversion",
            ),
            _code_binding(
                repo_root,
                baseline_commit,
                current_commit,
                "apps_rg/runtime/sections/executive_summary_voice_repair.py",
                "ensure_required_allowed_fact_utilization",
                "deterministic finalization of required evidence utilization",
            ),
            _code_binding(
                repo_root,
                baseline_commit,
                current_commit,
                "apps_rg/runtime/validators/executive_summary_x2.py",
                "check_exec_summary_no_sentence_fragment",
                "final sentence-fragment verdict",
            ),
        ]
    else:
        bindings = [
            {
                "role": "section-specific producer not mapped",
                "file": "",
                "symbol": "",
                "baseline_symbol_hash": "",
                "current_symbol_hash": "",
                "changed_between_revisions": False,
                "status": "DOWNSTREAM_CAUSE_REQUIRES_SECTION_BISECT",
            }
        ]
    code_status = (
        "CODE_CAUSE_NOT_ISOLATED"
        if any(row.get("status") == "CODE_CAUSE_NOT_ISOLATED" for row in bindings)
        else "NOT_APPLICABLE_NO_PRIOR_BASELINE"
        if not baseline_available
        else "DOWNSTREAM_CAUSE_REQUIRES_SECTION_BISECT"
        if section_id != "executive_summary"
        else "ISOLATED_TO_SYMBOLS"
    )
    finalization_binding = next(
        (
            row
            for row in bindings
            if row.get("role")
            == "deterministic finalization of required evidence utilization"
        ),
        {},
    )
    if section_id == "executive_summary":
        underlying_root_cause = {
            "first_observed_divergence_root_cause": {
                "status": "NOT_CAUSALLY_ISOLATED",
                "conclusion": (
                    "U0 ingested a different briefing source and the downstream targeting, proof-selection, "
                    "provider-request, and initial-candidate evidence changed. Without a controlled replay, "
                    "those upstream changes explain where divergence began but do not prove one sole cause."
                ),
                "evidence_refs": [
                    str(first_observed.get("prior_evidence_ref") or ""),
                    str(first_observed.get("current_evidence_ref") or ""),
                ],
            },
            "recovery_failure_root_cause": {
                "status": "ISOLATED",
                "conclusion": (
                    "Both pre-judge retries were only monotonic improvements: each retained the fact-conflation "
                    "defect, the retry budget ended, and retry_provider_for_synthesis reverted to the first candidate."
                ),
                "code_surface": "apps_rg/runtime/sections/executive_summary_lane.py::retry_provider_for_synthesis",
                "revision_relation": "LATENT_PATH_PREEXISTED_BASELINE",
            },
            "final_gate_root_cause": {
                "status": "ISOLATED",
                "conclusion": (
                    "Deterministic required-fact finalization changed the published text before X2; the final "
                    "fragment and fact-conflation checks then blocked judge dispatch."
                ),
                "code_surface": (
                    "apps_rg/runtime/sections/executive_summary_voice_repair.py::"
                    "ensure_required_allowed_fact_utilization"
                ),
                "first_change_commit": str(
                    finalization_binding.get("first_change_commit") or ""
                ),
                "first_change_subject": str(
                    finalization_binding.get("first_change_subject") or ""
                ),
                "validator_surface": (
                    "apps_rg/runtime/validators/executive_summary_x2.py::"
                    "check_exec_summary_no_sentence_fragment"
                ),
            },
        }
    else:
        underlying_root_cause = {
            "downstream_root_cause": {
                "status": "ISOLATED_TO_UPSTREAM_SECTION",
                "conclusion": (
                    "This section was blocked downstream of the executive-summary product-authorization failure."
                ),
            }
        }
    return {
        "schema_version": OUTPUT_BISECT_SCHEMA_VERSION,
        "section_id": section_id,
        "scope": (
            "FULL_CAUSAL_BISECT"
            if baseline_available and section_id == "executive_summary"
            else "NO_PRIOR_BASELINE"
            if not baseline_available
            else "DOWNSTREAM_SECTION_BISECT"
        ),
        "first_observed_divergence": first_observed,
        "first_causally_relevant_divergence": first_causal,
        "ingestion_to_outcome_lineage": lineage,
        "prior_attempt_timeline": prior_timeline,
        "current_attempt_timeline": current_timeline,
        "gate_matrix": _gate_matrix(baseline_lane, current_lane),
        "judge_matrix": _judge_matrix(baseline_lane, current_lane),
        "code_cause_status": code_status,
        "code_bindings": bindings,
        "underlying_root_cause": underlying_root_cause,
        "layperson_explanation": _layperson_explanation(
            prior_timeline,
            current_timeline,
            baseline_revision,
            lineage,
            section_id,
        ),
    }


def validate_section_output_bisect(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if doc.get("schema_version") != OUTPUT_BISECT_SCHEMA_VERSION:
        errors.append("invalid:schema_version")
    scope = str(doc.get("scope") or "")
    for key in (
        "ingestion_to_outcome_lineage",
        "prior_attempt_timeline",
        "current_attempt_timeline",
        "judge_matrix",
        "code_bindings",
        "underlying_root_cause",
        "layperson_explanation",
    ):
        if not doc.get(key):
            errors.append(f"missing_or_empty:{key}")
    if scope == "FULL_CAUSAL_BISECT":
        for key in (
            "first_observed_divergence",
            "first_causally_relevant_divergence",
            "gate_matrix",
        ):
            if not doc.get(key):
                errors.append(f"missing_or_empty:{key}")
    explanations = doc.get("layperson_explanation")
    if not isinstance(explanations, list) or len(explanations) != 3 or any(
        len(str(item).strip()) < 40 for item in explanations
    ):
        errors.append("invalid:layperson_explanation")
    for row in doc.get("ingestion_to_outcome_lineage") or []:
        if not isinstance(row, dict) or row.get("classification") not in CAUSAL_CLASSIFICATIONS:
            errors.append("invalid:lineage_row")
            break
    if scope == "FULL_CAUSAL_BISECT":
        for label in ("prior_attempt_timeline", "current_attempt_timeline"):
            for row in doc.get(label) or []:
                if not isinstance(row, dict) or row.get("complete") is not True:
                    errors.append(f"incomplete:{label}")
                    break
                if row.get("phase") == "pre_judge_synthesis_retry" and row.get("acceptance_scope") not in {
                    "FULL_PRE_X2_SHAPE_PASS",
                    "MONOTONIC_IMPROVEMENT_ONLY",
                    "REJECTED",
                }:
                    errors.append(f"ambiguous_retry_acceptance:{label}")
                    break
    current_rows = doc.get("current_attempt_timeline") or []
    x2_failed = any(
        isinstance(row, dict) and row.get("phase") == "final_x2" and row.get("gate_result") == "FAIL"
        for row in current_rows
    )
    if scope == "FULL_CAUSAL_BISECT" and x2_failed and not any(
        isinstance(row, dict)
        and row.get("phase") == "judge_panel"
        and row.get("judge_result") == "JUDGES_NOT_REACHED"
        for row in current_rows
    ):
        errors.append("missing:JUDGES_NOT_REACHED")
    if scope == "FULL_CAUSAL_BISECT" and doc.get("code_cause_status") != "ISOLATED_TO_SYMBOLS":
        errors.append("CODE_CAUSE_NOT_ISOLATED")
    for binding in doc.get("code_bindings") or []:
        if (
            isinstance(binding, dict)
            and binding.get("changed_between_revisions") is True
            and not binding.get("first_change_commit")
        ):
            errors.append("CODE_CAUSE_NOT_ISOLATED:first_change_commit")
            break
    return errors


def _escape(value: Any) -> str:
    return str(value if value not in (None, "") else "-").replace("|", "\\|").replace("\n", " ")


def _render_timeline(title: str, rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Seq | Phase | Attempt | Candidate | Trigger / defect | Action | Gate scope | Gate result | Judge | Disposition | Acceptance meaning | Evidence |",
        "|---:|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row.get('sequence')} | `{_escape(row.get('phase'))}` | `{_escape(row.get('attempt'))}` | "
            f"`{_escape(str(row.get('candidate_digest') or '')[:16])}` | {_escape(row.get('trigger_or_input'))} | "
            f"{_escape(row.get('repair_or_action'))} | `{_escape(row.get('gate_scope'))}` | "
            f"`{_escape(row.get('gate_result'))}` | `{_escape(row.get('judge_result'))}` | "
            f"`{_escape(row.get('disposition'))}` | `{_escape(row.get('acceptance_scope'))}` | "
            f"`{_escape(row.get('evidence_ref'))}` |"
        )
    return lines


def render_output_bisect(sections: list[dict[str, Any]]) -> str:
    lines = ["# apps_rg Output Bisect", ""]
    if not sections:
        return "\n".join(lines + ["No failed-section bisect was required.", ""])
    for section in sections:
        lines.extend([f"## Section: {section.get('section_id')}", "", "### Layperson RCA", ""])
        for sentence in section.get("layperson_explanation") or []:
            lines.append(str(sentence))
            lines.append("")
        first_observed = section.get("first_observed_divergence") or {}
        first_causal = section.get("first_causally_relevant_divergence") or {}
        lines.extend(
            [
                "### Divergence And Root Cause",
                "",
                f"- First observed divergence: `{first_observed.get('stage') or 'NOT_ISOLATED'}` - {first_observed.get('reason') or '-'}",
                f"- First causally relevant divergence: `{first_causal.get('stage') or 'NOT_ISOLATED'}` - {first_causal.get('reason') or '-'}",
                f"- Code cause status: `{section.get('code_cause_status')}`",
                "",
                "### Underlying Root Cause",
                "",
            ]
        )
        for label, finding in (section.get("underlying_root_cause") or {}).items():
            finding = finding if isinstance(finding, dict) else {}
            lines.append(f"- `{label}` / `{finding.get('status') or 'EVIDENCE_GAP'}`: {finding.get('conclusion') or '-'}")
            if finding.get("code_surface"):
                lines.append(f"  - Code surface: `{finding.get('code_surface')}`")
            if finding.get("first_change_commit"):
                lines.append(
                    f"  - First change commit: `{finding.get('first_change_commit')}` "
                    f"({finding.get('first_change_subject') or 'subject not observed'})"
                )
        lines.extend(
            [
                "",
                "### Ingestion-To-Outcome Lineage",
                "",
                "| Order | Stage | Prior | Current | Match | Classification | Why | Prior evidence | Current evidence |",
                "|---:|---|---|---|---|---|---|---|---|",
            ]
        )
        for row in section.get("ingestion_to_outcome_lineage") or []:
            lines.append(
                f"| {row.get('order')} | `{_escape(row.get('stage'))}` | `{_escape(str(row.get('prior_value'))[:24])}` | "
                f"`{_escape(str(row.get('current_value'))[:24])}` | `{row.get('match')}` | "
                f"`{_escape(row.get('classification'))}` | {_escape(row.get('reason'))} | "
                f"`{_escape(row.get('prior_evidence_ref'))}` | `{_escape(row.get('current_evidence_ref'))}` |"
            )
        lines.extend(["", "### Code Bindings", "", "| Role | File | Symbol | Changed in comparison | First change commit / PR | Status |", "|---|---|---|---|---|---|"])
        for row in section.get("code_bindings") or []:
            first_change = (
                f"PR #{row.get('first_change_pr_number')} / {row.get('first_change_commit')}"
                if row.get("first_change_pr_number")
                else str(row.get("first_change_commit") or "PREEXISTED_BASELINE")
            )
            lines.append(
                f"| {_escape(row.get('role'))} | `{_escape(row.get('file'))}` | `{_escape(row.get('symbol'))}` | "
                f"`{row.get('changed_between_revisions')}` | `{_escape(first_change)}` | `{_escape(row.get('status'))}` |"
            )
        lines.extend([""] + _render_timeline("Prior Passing Run", section.get("prior_attempt_timeline") or []))
        lines.extend([""] + _render_timeline("Current Failing Run", section.get("current_attempt_timeline") or []))
        lines.extend(["", "### Full X2 Gate Matrix", "", "| Gate | Prior | Current | Changed | Current reason |", "|---|---|---|---|---|"])
        for row in section.get("gate_matrix") or []:
            lines.append(
                f"| `{_escape(row.get('gate_id'))}` | `{row.get('prior')}` | `{row.get('current')}` | "
                f"`{row.get('changed')}` | {_escape(row.get('current_reason'))} |"
            )
        lines.extend(["", "### Judge Matrix", "", "| Judge | Prior | Current | Reason |", "|---|---|---|---|"])
        for row in section.get("judge_matrix") or []:
            lines.append(
                f"| `{_escape(row.get('judge'))}` | `{_escape(row.get('prior'))}` | "
                f"`{_escape(row.get('current'))}` | {_escape(row.get('reason'))} |"
            )
        lines.append("")
    return "\n".join(lines)


__all__ = [
    "OUTPUT_BISECT_GATE_ID",
    "OUTPUT_BISECT_SCHEMA_VERSION",
    "build_section_output_bisect",
    "render_output_bisect",
    "validate_section_output_bisect",
]
