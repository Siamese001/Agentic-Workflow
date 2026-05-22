"""Post-X1D judge-informed Qwen remediation for executive_summary (apps_rg only)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.executive_summary_repair_policy import (
    JUDGE_REGEN_MAX_ATTEMPTS,
    judge_regeneration_enabled,
    judge_safe_prefilter_enabled,
)
from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

_SYNTHESIS_TAXONOMY = frozenset(
    {
        "synthesis",
        "bullet",
        "stack",
        "staccato",
        "weave",
        "integrated",
        "paragraph",
        "narrative",
    }
)
_EXEC_SIGNAL_TAXONOMY = frozenset(
    {
        "executive_signal",
        "svp",
        "strategic",
        "platform",
        "governance",
        "commercial",
        "innovation",
    }
)
_JD_TAXONOMY = frozenset(
    {
        "jd",
        "briefing",
        "targeting",
        "innovation",
        "enterprise architecture",
        "it strategy",
    }
)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _judge_text_blob(judge: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("findings", "fail_reasons", "quality_flags", "remediation_suggestions"):
        val = judge.get(key)
        if isinstance(val, list):
            parts.extend(str(x) for x in val)
        elif val:
            parts.append(str(val))
    if judge.get("rationale"):
        parts.append(str(judge.get("rationale")))
    return " ".join(parts).lower()


def _taxonomy_tags(blob: str) -> set[str]:
    tags: set[str] = set()
    if any(t in blob for t in _SYNTHESIS_TAXONOMY):
        tags.add("synthesis")
    if any(t in blob for t in _EXEC_SIGNAL_TAXONOMY):
        tags.add("executive_signal")
    if any(t in blob for t in _JD_TAXONOMY):
        tags.add("jd_emphasis")
    return tags


def _is_model_backed_soft_fail(judge: dict[str, Any]) -> bool:
    if judge.get("evaluator_mode") != "MODEL_BACKED":
        return False
    if judge.get("decisive_failure"):
        return False
    if judge.get("provider_status") == "MODEL_BACKED_FAIL":
        return True
    if judge.get("pass") is False:
        return True
    ns = judge.get("normalized_score")
    nt = judge.get("normalized_threshold")
    if ns is not None and nt is not None:
        return float(ns) < float(nt)
    return False


def _median_normalized_score(judges: list[dict[str, Any]]) -> float | None:
    scores: list[float] = []
    for j in judges:
        if j.get("evaluator_mode") != "MODEL_BACKED":
            continue
        ns = j.get("normalized_score")
        if ns is None:
            continue
        try:
            scores.append(float(ns))
        except (TypeError, ValueError):
            continue
    if not scores:
        return None
    scores.sort()
    mid = len(scores) // 2
    if len(scores) % 2:
        return scores[mid]
    return (scores[mid - 1] + scores[mid]) / 2.0


def evaluate_judge_remediation_trigger(
    x1d_judges: list[dict[str, Any]],
    *,
    runtime_generation_status: str,
    x2_passed: bool,
) -> tuple[bool, dict[str, Any]]:
    """Return whether post-judge Qwen regen should run (X2 must already be green)."""
    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_remediation_trigger_v1",
        "triggered": False,
        "runtime_generation_status": runtime_generation_status,
        "x2_passed": x2_passed,
    }
    if runtime_generation_status != "REAL_LLM" or not x2_passed:
        receipt["reason"] = "requires_real_llm_and_x2_pass"
        return False, receipt

    soft_fails = [j for j in x1d_judges if _is_model_backed_soft_fail(j)]
    receipt["soft_fail_count"] = len(soft_fails)
    min_fail = _env_int("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MIN_FAIL_COUNT", 2)
    median_threshold = _env_float("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MEDIAN_THRESHOLD", 0.75)

    tag_sets = [_taxonomy_tags(_judge_text_blob(j)) for j in soft_fails]
    shared_tags: set[str] = set()
    if tag_sets:
        shared_tags = set.intersection(*tag_sets) if len(tag_sets) > 1 else tag_sets[0]

    quorum = len(soft_fails) >= min_fail and bool(shared_tags)
    median = _median_normalized_score(x1d_judges)
    receipt["median_normalized_score"] = median
    median_fail = median is not None and median < median_threshold

    decisive_dims = []
    for j in x1d_judges:
        if not j.get("decisive_failure"):
            continue
        blob = _judge_text_blob(j)
        if "synthesis" in blob or "executive_signal" in blob or "executive signal" in blob:
            decisive_dims.append(j.get("provider_key") or "unknown")
    decisive_trigger = bool(decisive_dims)
    receipt["decisive_synthesis_providers"] = decisive_dims
    receipt["quorum_shared_tags"] = sorted(shared_tags)
    receipt["quorum_soft_fail"] = quorum
    receipt["median_fail"] = median_fail

    triggered = quorum or median_fail or decisive_trigger
    receipt["triggered"] = triggered
    if triggered:
        if quorum:
            receipt["trigger_mode"] = "quorum_soft_fail"
        elif median_fail:
            receipt["trigger_mode"] = "median_normalized_below_threshold"
        else:
            receipt["trigger_mode"] = "decisive_synthesis_or_executive_signal"
    else:
        receipt["reason"] = "no_quorum_median_or_decisive_trigger"
    return triggered, receipt


def _collect_judge_feedback_lines(x1d_judges: list[dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {
        "synthesis": [],
        "jd_emphasis": [],
        "executive_signal": [],
    }
    for j in x1d_judges:
        if not (_is_model_backed_soft_fail(j) or j.get("decisive_failure")):
            continue
        blob = _judge_text_blob(j)
        tags = _taxonomy_tags(blob)
        provider = str(j.get("provider_name") or j.get("provider_key") or "judge")
        for finding in j.get("findings") or []:
            line = f"{provider}: {finding}"
            if "synthesis" in tags:
                out["synthesis"].append(line)
            if "jd_emphasis" in tags:
                out["jd_emphasis"].append(line)
            if "executive_signal" in tags:
                out["executive_signal"].append(line)
        for suggestion in j.get("remediation_suggestions") or []:
            line = f"{provider} remediation: {suggestion}"
            if "synthesis" in tags:
                out["synthesis"].append(line)
    return out


def build_judge_remediation_user_message(
    *,
    x1d_judges: list[dict[str, Any]],
    unused_fact_ids: list[str],
    allowed_fact_count: int,
) -> str:
    feedback = _collect_judge_feedback_lines(x1d_judges)
    unused_note = ""
    if unused_fact_ids:
        preview = ", ".join(unused_fact_ids[:12])
        suffix = "..." if len(unused_fact_ids) > 12 else ""
        unused_note = (
            f"Unused allowed facts ({len(unused_fact_ids)}): {preview}{suffix}. "
            "Weave supported substance from these ids into claim_ledger rows — do not invent claims.\n"
        )
    prefer_five = ""
    if allowed_fact_count >= 6:
        prefer_five = "Shape: 4 or 5 sentences; prefer 5 when integrating additional allowed facts.\n"
    else:
        prefer_five = "Shape: 4 or 5 sentences; fit_to_evidence integrated narrative.\n"
    return (
        "JUDGE_REMEDIATION (GRADE_ONLY feedback — do not invent facts):\n"
        f"- synthesis: {' | '.join(feedback['synthesis'][:6]) or 'improve integrated narrative; reduce bullet-stack'}\n"
        f"- jd_emphasis: {' | '.join(feedback['jd_emphasis'][:4]) or 'shape emphasis from JD/briefing only; jd_used_as_proof=false'}\n"
        f"- executive_signal: {' | '.join(feedback['executive_signal'][:4]) or 'elevate SVP platform/governance/commercial signal from allowed facts'}\n"
        f"{unused_note}"
        f"{prefer_five}"
        "Integrate metrics into narrative; no Additionally/Furthermore; no credential dump.\n"
        "Do not pad for length; add substance only from allowed facts not yet cited in claim_ledger.\n"
        "Return a NEW complete JSON object (RAW JSON only; first char {, last char }). "
        "THIRD PERSON ONLY. Keep jd_used_as_proof=false."
    )


def try_judge_safe_prefilter(
    parsed: dict[str, Any],
    selected_facts: list[dict[str, Any]],
    srfs_integration: dict[str, Any] | None,
    *,
    artifact_dir: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    if product_fail_closed_runtime():
        return parsed, None
    if not judge_safe_prefilter_enabled():
        return parsed, None
    from apps_rg.runtime.sections.exec_summary_srfs_judge_safe import apply_srfs_judge_safe_repair

    repaired, receipt = apply_srfs_judge_safe_repair(parsed, selected_facts, srfs_integration)
    if artifact_dir is not None and receipt and receipt.get("prefilter_applied"):
        from apps_rg.runtime.section_repair_lane_integration import record_deterministic_rewrite

        record_deterministic_rewrite(
            artifact_dir,
            operation="srfs_judge_safe_prefilter",
            reason=str(receipt.get("reason") or "judge_safe")[:240],
        )
    return repaired, receipt


def retry_qwen_for_judge_remediation(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    *,
    x1d_judges: list[dict[str, Any]],
    trigger_receipt: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    unused_fact_ids: list[str],
    srfs_integration: dict[str, Any] | None = None,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Bounded post-judge same-authority regen (max 1 attempt when enabled)."""
    from apps_rg.runtime.providers.qwen_vllm import call_qwen_vllm, tag_reasoning_lane
    from apps_rg.runtime.sections.executive_summary_lane import (
        LANE_KEY,
        normalize_executive_summary_llm_output,
        parse_model_json,
        prune_exec_summary_claim_ledger_orphans,
        write_json,
    )

    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_remediation_v1",
        "enabled": judge_regeneration_enabled(),
        "trigger": trigger_receipt,
        "accepted": False,
        "max_attempts": JUDGE_REGEN_MAX_ATTEMPTS,
        "attempts": [],
    }
    if not judge_regeneration_enabled():
        receipt["skipped"] = "judge_regen_disabled"
        if artifact_dir is not None:
            write_json(artifact_dir / "judge_remediation_receipt.json", receipt)
        return raw_output, parsed, receipt

    pre_parsed = dict(parsed)
    pre_parsed, prefilter_meta = try_judge_safe_prefilter(
        pre_parsed,
        list(selected_fact_plan.get("facts") or []),
        srfs_integration,
        artifact_dir=artifact_dir,
    )
    if prefilter_meta:
        receipt["judge_safe_prefilter"] = prefilter_meta
        if prefilter_meta.get("repair_candidate_accepted") and not prefilter_meta.get("repair_unchanged"):
            parsed = pre_parsed
            raw_output = json.dumps(
                {k: v for k, v in parsed.items() if k != "selected_fact_plan"},
                ensure_ascii=False,
                separators=(",", ":"),
            )
            receipt["prefilter_applied"] = True

    current_raw = raw_output
    current_parsed = parsed
    thread_messages = list(messages)
    allowed_count = len(allowed_fact_ids)

    for attempt in range(JUDGE_REGEN_MAX_ATTEMPTS):
        repair_user = build_judge_remediation_user_message(
            x1d_judges=x1d_judges,
            unused_fact_ids=unused_fact_ids,
            allowed_fact_count=allowed_count,
        )
        thread_messages = [
            *thread_messages,
            {"role": "assistant", "content": current_raw},
            {"role": "user", "content": repair_user},
        ]
        repair_payload = {**provider_payload, "messages": thread_messages}
        result = call_qwen_vllm(
            tag_reasoning_lane(repair_payload, LANE_KEY),
            artifact_dir=artifact_dir,
            run_id=run_id,
        )
        attempt_record: dict[str, Any] = {
            "attempt": attempt + 1,
            "runtime_status": result.runtime_generation_status,
        }
        if result.runtime_generation_status != "REAL_LLM":
            attempt_record["skipped"] = "non_real_llm"
            receipt["attempts"].append(attempt_record)
            break
        new_raw = result.raw_model_output
        new_parsed, new_err = parse_model_json(new_raw)
        attempt_record["parse_ok"] = bool(new_parsed)
        if new_parsed:
            new_parsed = normalize_executive_summary_llm_output(
                new_parsed,
                selected_fact_plan,
                srfs_integration=srfs_integration,
            )
            prune_exec_summary_claim_ledger_orphans(new_parsed, allowed_fact_ids)
            regen_text = str(new_parsed.get("resume_display_text") or "")
            attempt_record["regen_resume_word_count"] = len(re.findall(r"\S+", regen_text))
            current_raw = new_raw
            current_parsed = new_parsed
            if artifact_dir is not None:
                write_json(artifact_dir / "provider_response_judge_regen.json", result.to_dict())
        else:
            attempt_record["parse_error"] = new_err
        receipt["attempts"].append(attempt_record)

    receipt["accepted"] = bool(current_parsed.get("resume_display_text"))
    if artifact_dir is not None:
        write_json(artifact_dir / "judge_remediation_receipt.json", receipt)
    return current_raw, current_parsed, receipt


def rerun_x2_after_judge_remediation(
    *,
    resume_display_text: str,
    parsed_for_x2: dict[str, Any],
    claim_ledger: list[dict[str, Any]],
    text_claim_coverage: dict[str, Any],
    allowed_fact_ids: set[str],
    args: Any,
    temperature: float,
    runtime_generation_status: str,
    artifact_dir: Path,
    model_name: str | None,
    prompt_hash: str,
    compiled_prompt: str | None,
    raw_output: str,
    selected_facts: list[dict[str, Any]],
    x1d_judges: list[dict[str, Any]],
    srfs_integration: dict[str, Any] | None,
    proof_pool_metadata: dict[str, Any] | None,
    proof_pool_ref: str,
    proof_pool_digest: str,
) -> list[dict[str, Any]]:
    gates = run_x2_gates(
        resume_display_text=resume_display_text,
        parsed_output=parsed_for_x2,
        claim_ledger=claim_ledger,
        text_claim_coverage=text_claim_coverage,
        allowed_fact_ids=allowed_fact_ids,
        target_company=str(args.target_company),
        jd_text=str(getattr(args, "jd_text", "") or ""),
        temperature=temperature,
        runtime_generation_status=runtime_generation_status,
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        artifacts_dir=artifact_dir,
        provider_requested=str(args.provider),
        provider_attempted=str(args.provider),
        model_name=model_name,
        prompt_hash=prompt_hash,
        compiled_prompt=compiled_prompt,
        raw_output=raw_output,
        target_role=getattr(args, "target_role", None),
        selected_facts=selected_facts,
        x1d_judges=x1d_judges,
        srfs_integration=srfs_integration,
        proof_pool_metadata=proof_pool_metadata,
        proof_pool_ref=proof_pool_ref,
        proof_pool_digest=proof_pool_digest,
    )
    return [g.to_dict() for g in gates]


def rerun_soft_failed_judges(
    *,
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    judge_packet: dict[str, Any],
    judge_packet_ref: str,
    compiled_prompt: str | None,
    artifact_dir: Path,
    judge_keys: list[str],
    judge_mode: str,
    prior_judges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Re-run only model-backed soft-failed judges after remediation."""
    from apps_rg.runtime.judges.executive_summary_judge_packet import build_deterministic_gate_summary
    from apps_rg.runtime.judges.executive_summary_x1d import run_llm_judges

    soft_keys = {
        str(j.get("provider_key"))
        for j in prior_judges
        if j.get("provider_key") and _is_model_backed_soft_fail(j)
    }
    if not soft_keys:
        return list(prior_judges)

    packet = dict(judge_packet)
    packet["deterministic_gate_summary"] = build_deterministic_gate_summary(
        resume_display_text=resume_display_text,
        parsed_output={"resume_display_text": resume_display_text, "claim_ledger": claim_ledger},
        claim_ledger=claim_ledger,
        allowed_fact_ids=set(packet.get("allowed_fact_ids") or []),
        srfs_integration=None,
    )
    packet["candidate_output"] = {
        "resume_display_text": resume_display_text,
        "claim_ledger": claim_ledger,
    }
    keys_to_run = [k for k in judge_keys if k in soft_keys]
    if not keys_to_run:
        return list(prior_judges)

    refreshed = {
        str(j.get("provider_key")): j
        for j in run_llm_judges(
            resume_display_text=resume_display_text,
            claim_ledger=claim_ledger,
            judge_keys=keys_to_run,
            mode=judge_mode,
            artifact_base=artifact_dir,
            judge_packet=packet,
            judge_packet_ref=judge_packet_ref,
            compiled_prompt=compiled_prompt,
        )
    }
    out: list[dict[str, Any]] = []
    for j in prior_judges:
        pk = str(j.get("provider_key") or "")
        if pk in refreshed:
            out.append(refreshed[pk].to_dict())
        else:
            out.append(j)
    return out
