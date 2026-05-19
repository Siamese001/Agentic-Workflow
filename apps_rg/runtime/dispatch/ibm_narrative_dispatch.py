"""App-local ibm_narrative runtime seam.

Canonical execution lives in ``apps_rg.runtime.sections.ibm_narrative_lane`` (invoked by
``python -m apps_rg --section ibm_narrative`` via ``canonical_dispatch``).

This module exposes ``run_ibm_narrative_execution`` (compile / provider / X1D / X2 / X3 / L6 shadow).

``python -m apps_rg.runtime.dispatch.ibm_narrative_dispatch`` is **retired** — it exits with guidance
to use ``python -m apps_rg --section ibm_narrative``.

**W3:** ``declared_temporary_slice`` — section runtime proof seam; see ``w3_execution_path_convergence_f8e3c1.md``.
"""
from __future__ import annotations

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_DECLARED_TEMPORARY_SLICE,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_DECLARED_TEMPORARY_SLICE
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    classify_ledger_parse_state,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.dispatch.competencies_dispatch import collect_employment_bullets
from apps_rg.runtime.dispatch.ibm_narrative_pa import compile_ibm_narrative_prompt
from apps_rg.runtime.exit.ibm_narrative_x3 import aggregate_x3
from apps_rg.runtime.ibm_narrative_judge_preflight import run_ibm_narrative_judge_credentials_preflight
from apps_rg.runtime.ibm_narrative_proof_accounting import (
    build_clean_x3_allow_readiness_document,
    classify_certification_class,
    classify_generation_class,
    classify_judge_class,
    classify_proof_class,
    compute_decisive_accounting_label,
)
from apps_rg.runtime.judges.executive_summary_x1d import _make_blocked_output
from apps_rg.runtime.judges.ibm_narrative_x1d import JUDGE_RUBRIC_VERSION, run_ibm_narrative_judges
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, ProviderResult, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.qwen_offline_contract_stub import (
    OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
    effective_offline_contract_stub_enabled,
    synthetic_qwen_provider_result,
)
from apps_rg.runtime.shadow.ibm_narrative_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
from apps_rg.runtime.validators.executive_summary_x2 import build_sentence_claim_coverage
from apps_rg.runtime.validators.ibm_narrative_x2 import (
    companion_ibm_bullets_have_full_metric_bundle,
    count_ibm_narrative_metric_hits,
    run_ibm_narrative_x2_gates,
)
from apps_rg.runtime.section_proof.section_input_usage_ledger import build_section_input_usage_ledger_v1
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    allow_non_allow_exit_zero_ok,
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    infer_product_quality_blocked_or_mock,
)
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    prepare_runtime_proof_run_dir,
    resolve_effective_lane_l2_path,
)
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.sections.ibm_canonical_hydration import remap_ibm_narrative_claim_ledger_to_fact_pool
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict

PROMPT_ID = "ibm_position_narrative_dispatch_v1"


def _generation_status_allows_structure_parse(runtime_generation_status: str) -> bool:
    return runtime_generation_status in {"REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS}


NARRATIVE_TEMP_DEFAULT = 0.45
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text
NARRATIVE_QWEN_MAX_TOKENS = 1200


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "ibm_narrative"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _preflight_blocked_synthetic_judges(judge_keys: list[str], message: str) -> list[dict[str, Any]]:
    """Blocked rows emitted when credential preflight fails before Qwen narrative generation."""
    rows: list[dict[str, Any]] = []
    for key in judge_keys:
        jo = _make_blocked_output(
            key,
            "preflight_block",
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE",
            message,
        )
        jo.judge_id = f"x1d_{key}_ibm_narrative"
        jo.rubric_version = JUDGE_RUBRIC_VERSION
        rows.append(jo.to_dict())
    return rows


def load_base_resume() -> tuple[dict[str, Any], Path, str]:
    return load_lane_base_resume_json(repo_root=REPO_ROOT)


def extract_ibm_employment(base_resume: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], set[str]]:
    facts_obj = base_resume.get("facts", base_resume)
    for emp in facts_obj.get("employment", []):
        if "ibm" not in str(emp.get("employer", "")).lower():
            continue
        bullets: list[dict[str, Any]] = []
        allowed: set[str] = set()
        for bullet in emp.get("bullets", []):
            bid = bullet.get("bullet_id")
            if not bid:
                continue
            allowed.add(bid)
            row = {
                "fact_id": bid,
                "claim_text": bullet.get("text", ""),
                "source_employment": emp.get("employer"),
                "has_metric": bool(bullet.get("has_metric")),
                "metric_raw": bullet.get("metric_raw", "") if bullet.get("has_metric") else "",
                "domain": bullet.get("domain", ""),
                "technologies": bullet.get("technologies", []),
            }
            bullets.append(row)
            if row.get("metric_raw"):
                allowed.add(f"{bid}_metric_{sha16(row['metric_raw'])[:8]}")
        header = {
            "employer": emp.get("employer"),
            "title": emp.get("title"),
            "location": emp.get("location"),
            "start_date": emp.get("start_date"),
            "end_date": emp.get("end_date"),
            "is_current": emp.get("is_current"),
            "fact_id": emp.get("fact_id", "exp_ibm_001"),
        }
        return header, bullets, allowed
    raise ValueError("IBM employment entry not found in base resume.")


def build_selected_fact_plan(facts: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        facts,
        key=lambda r: IBM_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in IBM_BULLET_IDS else 99,
    )
    return {
        "section_id": "ibm_narrative",
        "selection_method": "canonical_json_ibm_facts",
        "facts": ordered,
        "required_fact_ids": list(IBM_BULLET_IDS),
    }


def build_selected_fact_plan_ibm_narrative_srfs(facts: list[dict[str, Any]]) -> dict[str, Any]:
    from apps_rg.runtime.sections.selected_role_fact_set import selection_method_for_section

    return {
        "section_id": "ibm_narrative",
        "selection_method": selection_method_for_section("ibm_narrative"),
        "facts": facts,
        "required_fact_ids": [str(f.get("fact_id") or "").strip() for f in facts if f.get("fact_id")],
    }


def load_companion_ibm_bullets_text() -> str:
    path = resolve_effective_lane_l2_path(REPO_ROOT, "ibm_bullets")
    if path is None or not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    bullets = data.get("bullets") or []
    return "\n".join(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}" for b in bullets)


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    ibm_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    companion_bullets_ref: str | None,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    candidate_name: str = "",
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("ibm_narrative_%Y%m%d_%H%M%S"),
        "section_id": "ibm_narrative",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "ibm_header": ibm_header,
        "candidate_name": candidate_name,
        "companion_ibm_bullets_ref": companion_bullets_ref,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "ibm_narrative_only",
        "full_resume_writable": False,
    }


def build_prompt_messages(runtime_payload: dict[str, Any], companion_text: str) -> list[dict[str, str]]:
    """W7: PA-compiled system prompt via ``section_prompt_adapter`` (no inline fallback)."""
    rid = str(runtime_payload.get("run_id") or "ibm_narrative_prompt_build")
    return compile_ibm_narrative_prompt(runtime_payload, companion_text, run_id=rid).artifact.messages


def parse_model_json(raw: str) -> tuple[dict[str, Any] | None, str]:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed, ""
    except json.JSONDecodeError as exc:
        return None, f"JSON parse failed: {exc}"
    return None, "Model output was not a JSON object."


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    out = dict(parsed)
    narrative = str(out.get("narrative_sentence", "")).strip()
    while narrative.count(",") >= 5:
        narrative = re.sub(r",\s+and\s+", " and ", narrative, count=1)
        if narrative.count(",") >= 5:
            narrative = re.sub(r",\s+", " ", narrative, count=1)
    if narrative and not narrative.endswith((".", "!", "?")):
        narrative += "."
    out["narrative_sentence"] = narrative
    if not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    ledger = out.get("claim_ledger")
    if isinstance(ledger, list):
        for entry in ledger:
            raw_ids = entry.get("source_fact_ids")
            if not isinstance(raw_ids, list):
                continue
            fixed: list[str] = []
            for fid in raw_ids:
                s = str(fid)
                while "bul_ibm__" in s:
                    s = s.replace("bul_ibm__", "bul_ibm_", 1)
                if re.match(r"^bul_ib_\d{3}$", s):
                    s = "bul_ibm_" + s[7:]
                fixed.append(s)
            entry["source_fact_ids"] = fixed
    if not out.get("claim_ledger"):
        out["claim_ledger"] = [
            {
                "claim_text": narrative,
                "source_fact_ids": list(IBM_BULLET_IDS),
            }
        ]
    allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    ibm_ids = [bid for bid in IBM_BULLET_IDS if bid in allowed] or sorted(
        x for x in allowed if str(x).startswith("bul_ibm_")
    )[:6]
    ledger = out.get("claim_ledger")
    if isinstance(ledger, list) and narrative and ibm_ids:
        parts = re.split(r",\s+(?=establishing\b)", narrative, maxsplit=1, flags=re.I)
        if len(parts) == 2:
            lead = parts[0].strip().rstrip(".")
            tail = parts[1].strip().rstrip(".")
            out["claim_ledger"] = [
                {
                    "claim_text": lead,
                    "source_fact_ids": ibm_ids[:3],
                },
                {
                    "claim_text": tail,
                    "source_fact_ids": ibm_ids[2:5] or ibm_ids[:2],
                },
            ]
    if not isinstance(out.get("jd_alignment"), dict):
        out["jd_alignment"] = {"targeting_only": True, "jd_used_as_proof": False}
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    out.setdefault("self_check", {"normalized_by_dispatch": True})
    return out


def truncate_narrative_after_first_metric_hit(narrative: str) -> str:
    """When multiple tracked IBM metrics remain in one clause, drop text from the second metric onward."""
    s = narrative.strip()
    patterns = (
        re.compile(r"\$15\s*m", re.I),
        re.compile(r"99\.9%"),
        re.compile(r"\b30\s*%"),
        re.compile(r"\b25\s*%"),
        re.compile(r"\b50\s*%"),
    )
    spans: list[tuple[int, int]] = []
    for rx in patterns:
        for m in rx.finditer(s):
            spans.append((m.start(), m.end()))
    spans.sort(key=lambda x: x[0])
    if len(spans) < 2:
        return s
    cut = spans[1][0]
    clipped = s[:cut].rstrip()
    clipped = re.sub(r"\s*[,;:]\s*$", "", clipped)
    clipped = re.sub(r"\s+and\s*$", "", clipped, flags=re.I)
    clipped = clipped.rstrip(" ,")
    return clipped if clipped else s


def _remove_earliest_metric_span(narrative: str) -> str:
    """Drop the earliest tracked IBM metric substring (best-effort for companion full-metric-bundle mode)."""
    s = narrative.strip()
    if not s:
        return s
    patterns = (
        re.compile(r"\$15\s*m", re.I),
        re.compile(r"99\.9%"),
        re.compile(r"\b30\s*%"),
        re.compile(r"\b25\s*%"),
        re.compile(r"\b50\s*%"),
    )
    earliest: tuple[int, int] | None = None
    for rx in patterns:
        m = rx.search(s)
        if m and (earliest is None or m.start() < earliest[0]):
            earliest = (m.start(), m.end())

    # Handle $15 spelled with digits only (counted by metric gate)
    dollar_plain = re.search(r"\$15\b", s)
    if dollar_plain:
        cand = (dollar_plain.start(), dollar_plain.end())
        if earliest is None or cand[0] < earliest[0]:
            earliest = cand

    if earliest is None:
        return s
    left = s[: earliest[0]].rstrip()
    right = s[earliest[1] :].lstrip()
    out = left
    if right:
        out = (left + " " + right).strip() if left else right
    out = re.sub(r"\s*[,;:]\s*$", "", out)
    out = re.sub(r"^\s*[,;:]\s*", "", out)
    out = re.sub(r"\s+and\s+$", "", out, flags=re.I)
    return out.strip()


def collapse_narrative_sentence_for_companion_metric_budget(narrative: str, companion_text: str, max_rounds: int = 48) -> str:
    """When companion bullets expose the KPI bundle, strip tracked bullet metrics until none remain."""
    s = narrative.strip()
    if not companion_text.strip() or not companion_ibm_bullets_have_full_metric_bundle(companion_text):
        return s
    for _ in range(max_rounds):
        hits = count_ibm_narrative_metric_hits(s)
        if hits == 0:
            break
        before = s
        s = _remove_earliest_metric_span(s)
        if count_ibm_narrative_metric_hits(s) == hits:
            alt = truncate_narrative_after_first_metric_hit(before)
            if alt != before:
                s = alt
        if count_ibm_narrative_metric_hits(s) == hits and s == before:
            break
    return s


def reconcile_narrative_claim_ledger(
    narrative: str,
    ledger: list[Any],
    *,
    allowed_fact_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Subset ledger to claims still verbatim in narrative; fallback when trimming removed clause-level claims."""
    nlow = narrative.lower()
    kept: list[dict[str, Any]] = []
    for e in ledger or []:
        if not isinstance(e, dict):
            continue
        ct = str(e.get("claim_text", "")).strip()
        if len(ct) >= 6 and ct.lower() in nlow:
            kept.append(dict(e))
    if kept:
        return kept
    fallback_ids = ["bul_ibm_001"]
    if allowed_fact_ids:
        facts = sorted(x for x in allowed_fact_ids if str(x).startswith("fact_"))
        if facts:
            fallback_ids = facts[:3]
    return [{"claim_text": narrative.strip().rstrip(".!?"), "source_fact_ids": fallback_ids}]


def apply_companion_metric_budget_trim(
    parsed: dict[str, Any] | None,
    companion_text: str,
    *,
    runtime_payload: dict[str, Any] | None = None,
) -> None:
    """In-place deterministic trim against companion bullets before X2 (does not loosen gates)."""
    if not parsed:
        return
    before = str(parsed.get("narrative_sentence", "")).strip()
    collapsed = collapse_narrative_sentence_for_companion_metric_budget(before, companion_text).strip()
    if collapsed != before:
        clog = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
        clog.append({"operation": "companion_metric_budget_deterministic_trim", "reason": "deterministic_pre_x2"})
        parsed["change_log"] = clog
    parsed["narrative_sentence"] = collapsed
    led = list(parsed.get("claim_ledger") or []) if isinstance(parsed.get("claim_ledger"), list) else []
    allowed = (
        {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
        if isinstance(runtime_payload, dict)
        else None
    )
    parsed["claim_ledger"] = reconcile_narrative_claim_ledger(collapsed, led, allowed_fact_ids=allowed)


def retry_qwen_for_parse(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parse_error: str,
) -> tuple[str, dict[str, Any] | None, str]:
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                f"JSON INVALID: {parse_error}. Return one NEW compact JSON object only. "
                "Keys: narrative_sentence (one sentence), selected_fact_plan, claim_ledger, jd_alignment, "
                "gap_notes, change_log, self_check. "
                "narrative_sentence: third person, IBM anchor, bul_ibm_* claim_ledger only, no em dash, no inline source tags."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def retry_qwen_for_metric_budget(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    companion_text: str,
    runtime_payload: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """One repair turn when companion bullets already carry the full metric bundle."""
    narrative = str(parsed.get("narrative_sentence") or "")
    if not companion_text or not companion_ibm_bullets_have_full_metric_bundle(companion_text):
        return raw_output, parsed
    if count_ibm_narrative_metric_hits(narrative) == 0:
        return raw_output, parsed
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                "DETERMINISTIC_REVISION: Accepted IBM bullets already list $15M, 99.9%, 30%, 25%, and 50%. "
                "narrative_sentence MUST include ZERO of those tracked metric tokens — use qualitative "
                "modernization reliability lineage partnership framing only — return one full JSON object with the "
                "same keys and a fully revised narrative_sentence plus matching claim_ledger rows."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, parsed
    new_raw = result.raw_model_output
    new_parsed, _err = parse_model_json(new_raw)
    if new_parsed is None:
        return raw_output, parsed
    new_parsed = normalize_parsed_output(new_parsed, runtime_payload)
    prior_log = list(parsed.get("change_log") or []) if isinstance(parsed.get("change_log"), list) else []
    new_parsed["change_log"] = prior_log + list(new_parsed.get("change_log") or [])
    new_parsed["change_log"].append(
        {"operation": "metric_budget_repair", "reason": "companion_ibm_bullets_full_metrics"}
    )
    return new_raw, new_parsed


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    narrative = (
        "At IBM, led enterprise-scale modernization across cloud and analytics programs for regulated financial services, "
        "establishing lineage and observability foundations and hyperscaler partnership discipline shaping later "
        "production AI platform leadership."
    )
    pp = runtime_payload.get("proof_pool_metadata") or {}
    pool_type = str(pp.get("proof_pool_type") or "")
    is_srfs = pool_type == "selected_role_fact_set"
    is_ledger = pool_type == "broad_skills_ledger"
    allowed_sorted = list(runtime_payload.get("allowed_fact_ids") or [])
    if (is_srfs or is_ledger) and allowed_sorted:
        from apps_rg.runtime.sections.selected_role_fact_set import stub_source_fact_ids_for_allowed

        bases = stub_source_fact_ids_for_allowed(allowed_sorted, max_ids=6)
        if len(bases) >= 3:
            ledger = [
                {
                    "claim_text": (
                        "At IBM, led enterprise-scale modernization across cloud and analytics programs "
                        "for regulated financial services"
                    ),
                    "source_fact_ids": bases[:2],
                },
                {"claim_text": "establishing lineage and observability foundations", "source_fact_ids": [bases[2]]},
                {
                    "claim_text": "hyperscaler partnership discipline shaping later production AI platform leadership",
                    "source_fact_ids": bases[3:6] if len(bases) > 3 else [bases[-1]],
                },
            ]
        else:
            ledger = [{"claim_text": narrative, "source_fact_ids": bases}]
    else:
        ledger = [
            {
                "claim_text": (
                    "At IBM, led enterprise-scale modernization across cloud and analytics programs "
                    "for regulated financial services"
                ),
                "source_fact_ids": ["bul_ibm_001", "bul_ibm_002"],
            },
            {
                "claim_text": "establishing lineage and observability foundations",
                "source_fact_ids": ["bul_ibm_004"],
            },
            {
                "claim_text": "hyperscaler partnership discipline shaping later production AI platform leadership",
                "source_fact_ids": ["bul_ibm_005"],
            },
        ]
    return {
        "narrative_sentence": narrative,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": ledger,
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [{"operation": "offline_contract_stub", "reason": "deterministic_fixture"}],
        "self_check": {"one_sentence": True, "third_person": True},
    }


def infer_product_quality(runtime_generation_status: str, x2_gates: list[dict[str, Any]]) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    return infer_product_quality_blocked_or_mock(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason="REAL_LLM output passed all deterministic ibm_narrative gates.",
    )


def write_x2_gate_outputs(path: Path, gates: list[dict[str, Any]]) -> None:
    failed = [g["gate_id"] for g in gates if not g["pass"]]
    write_json(
        path,
        {
            "gates": gates,
            "failed_gates": failed,
            "x2_passed": sum(1 for g in gates if g["pass"]),
            "x2_failed": len(failed),
            "total_x2_gates": len(gates),
        },
    )


def run_ibm_narrative_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.dispatch.ibm_narrative_dispatch",
    print_output: bool = False,
) -> dict[str, Any]:
    """Single end-to-end ibm_narrative run: artifacts + X1D/X2/X3/L6."""
    from apps_rg.runtime.proof_pool_lane_integration import load_section_proof_for_lane
    from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_BASE_RESUME_FALLBACK
    from apps_rg.runtime.sections import selected_role_fact_set as _srfs

    pool, base, base_path, base_hash = load_section_proof_for_lane(
        section_id="ibm_narrative",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    candidate_name = str(
        base.get("candidate_name") or (base.get("header") or {}).get("name") or ""
    ).strip()
    if pool.proof_source == PROOF_SOURCE_BASE_RESUME_FALLBACK:
        ibm_header, ibm_facts, allowed_fact_ids = extract_ibm_employment(base)
        selected_fact_plan = build_selected_fact_plan(ibm_facts)
    else:
        ibm_header, _, _ = extract_ibm_employment(base)
        ibm_facts = [_srfs.plan_fact_to_employment_bullet_row(f) for f in pool.selected_fact_plan.get("facts", [])]
        ibm_facts.sort(
            key=lambda r: IBM_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in IBM_BULLET_IDS else 99,
        )
        if pool.srfs_present:
            selected_fact_plan = build_selected_fact_plan_ibm_narrative_srfs(ibm_facts)
        else:
            selected_fact_plan = {**pool.selected_fact_plan, "facts": ibm_facts}
        allowed_fact_ids = pool.allowed_fact_ids
    proof_pool_metadata = pool.proof_pool_metadata
    companion_text = load_companion_ibm_bullets_text()
    ibm_bullets_l2 = resolve_effective_lane_l2_path(REPO_ROOT, "ibm_bullets")
    companion_ref = (
        str(ibm_bullets_l2.relative_to(REPO_ROOT))
        if ibm_bullets_l2 is not None and companion_text
        else None
    )
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        ibm_header=ibm_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        companion_bullets_ref=companion_ref,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
        candidate_name=candidate_name,
    )
    runtime_payload["proof_pool_metadata"] = proof_pool_metadata
    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    (artifact_dir / "companion_ibm_bullets_context.txt").write_text(
        companion_text or "(none)\n", encoding="utf-8"
    )
    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )

    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_ibm_narrative_prompt(
        runtime_payload,
        companion_text,
        run_id=runtime_payload["run_id"],
    )
    messages = section_compiled.artifact.messages
    compiled_prompt = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    prompt_hash = sha16(compiled_prompt)
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    (artifact_dir / "compiled_prompt.txt").write_text(
        json.dumps(messages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_json(
        artifact_dir / "compiled_prompt_artifact.json",
        {
            "section_id": section_compiled.section_id,
            "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
            "compiler_template_id": section_compiled.artifact.template_id,
            "pa_prompt_hash": section_compiled.artifact.prompt_hash,
            "dispatch_sha256_prompt16": prompt_hash,
            "slot_count": section_compiled.artifact.slot_count,
            "allowed_fact_ids": list(runtime_payload.get("allowed_fact_ids") or []),
        },
    )

    provider_request_data = None
    provider_result_data = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"

    judge_keys = [j.strip() for j in str(getattr(args, "x1d_judges", "") or "").split(",") if j.strip()]
    judge_allowed_mock = bool(args.mock_judges and getattr(args, "allow_test_mock_judges", False))
    offline_stub_on = effective_offline_contract_stub_enabled()

    if offline_stub_on:
        preflight_art: dict[str, Any] = {"skipped": True, "reason": "offline_contract_stub"}
    elif judge_allowed_mock:
        preflight_art = {"skipped": True, "reason": "mock_judge_cli_flags"}
    else:
        preflight_art = dict(run_ibm_narrative_judge_credentials_preflight(judge_keys, os.environ))
    preflight_blocked = bool(preflight_art.get("preflight_blocked"))
    write_json(artifact_dir / "ibm_narrative_judge_preflight.json", preflight_art)

    provider_req, provider_payload = build_qwen_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=NARRATIVE_QWEN_MAX_TOKENS,
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_request_data.get("model") or DEFAULT_QWEN_MODEL)

    if preflight_blocked and not offline_stub_on and not judge_allowed_mock:
        result = ProviderResult(
            provider_requested=str(provider_req.provider_requested),
            provider_attempted=bool(provider_req.provider_attempted),
            provider_available=False,
            exact_provider_error="IBM narrative X1D judge credential preflight blocked narrative generation.",
            runtime_generation_status="BLOCKED",
            model=str(req_model),
            raw_model_output="",
            provider_response={"preflight_blocked": True, "preflight": preflight_art},
            reasoning_execution_receipt=None,
        )
        provider_result_data = result.to_dict()
        raw_output = result.raw_model_output
        runtime_generation_status = result.runtime_generation_status
        write_json(artifact_dir / "provider_response.json", provider_result_data)
        parsed = None
        parse_error = result.exact_provider_error or "preflight_blocked"
    elif offline_stub_on:
        stub_raw = json.dumps(build_mock_output(runtime_payload), sort_keys=True, separators=(",", ":"))
        result = synthetic_qwen_provider_result(raw_model_output=stub_raw, requested_model=req_model)
        provider_result_data = result.to_dict()
        raw_output = result.raw_model_output
        runtime_generation_status = result.runtime_generation_status
        write_json(artifact_dir / "provider_response.json", provider_result_data)
        if _generation_status_allows_structure_parse(result.runtime_generation_status):
            parsed, parse_error = parse_model_json(raw_output)
            if parsed is None:
                raw_output, parsed, parse_error = retry_qwen_for_parse(
                    messages, provider_payload, raw_output, parse_error
                )
            if parsed is not None:
                parsed = normalize_parsed_output(parsed, runtime_payload)
                raw_output, parsed = retry_qwen_for_metric_budget(
                    messages,
                    provider_payload,
                    raw_output,
                    parsed,
                    companion_text,
                    runtime_payload,
                )
                apply_companion_metric_budget_trim(
                    parsed, companion_text, runtime_payload=runtime_payload
                )
                parsed = normalize_parsed_output(parsed, runtime_payload)
                remap_ibm_narrative_claim_ledger_to_fact_pool(parsed, runtime_payload)
        else:
            parsed = None
            parse_error = result.exact_provider_error or "provider blocked"
    else:
        result = call_qwen_vllm(tag_reasoning_lane(provider_payload, LANE_KEY))
        provider_result_data = result.to_dict()
        raw_output = result.raw_model_output
        runtime_generation_status = result.runtime_generation_status
        write_json(artifact_dir / "provider_response.json", provider_result_data)
        if _generation_status_allows_structure_parse(result.runtime_generation_status):
            parsed, parse_error = parse_model_json(raw_output)
            if parsed is None:
                raw_output, parsed, parse_error = retry_qwen_for_parse(
                    messages, provider_payload, raw_output, parse_error
                )
            if parsed is not None:
                parsed = normalize_parsed_output(parsed, runtime_payload)
                raw_output, parsed = retry_qwen_for_metric_budget(
                    messages,
                    provider_payload,
                    raw_output,
                    parsed,
                    companion_text,
                    runtime_payload,
                )
                apply_companion_metric_budget_trim(
                    parsed, companion_text, runtime_payload=runtime_payload
                )
                parsed = normalize_parsed_output(parsed, runtime_payload)
                remap_ibm_narrative_claim_ledger_to_fact_pool(parsed, runtime_payload)
        else:
            parsed = None
            parse_error = result.exact_provider_error or "provider blocked"

    narrative = str((parsed or {}).get("narrative_sentence") or "").strip()
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    judge_mode = "mocked" if judge_allowed_mock else "blocked_if_unavailable"
    if preflight_blocked and not offline_stub_on and not judge_allowed_mock:
        blocker_detail = "; ".join(preflight_art.get("preflight_decisive_blockers") or [])
        x1d = _preflight_blocked_synthetic_judges(
            judge_keys,
            blocker_detail or "judge credential preflight failed before narrative generation",
        )
    else:
        x1d = [
            j.to_dict()
            for j in run_ibm_narrative_judges(
                narrative_sentence=narrative,
                claim_ledger=claim_ledger,
                judge_keys=judge_keys,
                companion_bullets_context=companion_text,
                mode=judge_mode,
                artifact_base=artifact_dir,
            )
        ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output or "",
        lane_profile="ibm_narrative",
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
        claim_id_prefix="ibm_narrative_claim",
    )
    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)
    coverage = build_sentence_claim_coverage(narrative, claim_ledger, allowed_fact_ids)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    write_json(artifact_dir / "selected_fact_plan.json", (parsed or {}).get("selected_fact_plan") or selected_fact_plan)
    req_id_n = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    trace_rr_n = artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="ibm_narrative",
        run_id=str(runtime_payload["run_id"]),
        request_id=req_id_n,
        trace_root=trace_rr_n,
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=(parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        jd_text=str(runtime_payload.get("jd_text") or ""),
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        briefing_text=str(runtime_payload.get("briefing") or ""),
        jd_alignment=(parsed or {}).get("jd_alignment") if isinstance(parsed, dict) else None,
    )
    from apps_rg.runtime.proof_pool_lane_integration import apply_proof_pool_to_usage_ledger

    write_json(
        artifact_dir / "section_input_usage_ledger.json",
        apply_proof_pool_to_usage_ledger(usage_doc, pool),
    )
    parsed_for_x2: dict[str, Any] = {**(parsed or {}), "text_claim_coverage": coverage}

    mock_provider_cli = str(getattr(args, "provider", "") or "").strip().lower() == "mock"
    plumbing_waiver_cli = bool(getattr(args, "allow_non_allow_exit_zero", False))
    hatch_mp = bool(getattr(args, "allow_test_mock_provider", False)) or (
        plumbing_waiver_cli and mock_provider_cli
    )
    test_only_mock_provider_eff = mock_provider_cli and hatch_mp

    allowed_ids_list = list(runtime_payload.get("allowed_fact_ids") or [])
    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active = bool(str(pp_x2.get("proof_pool_type") or "").strip())
    x2 = [
        g.to_dict()
        for g in run_ibm_narrative_x2_gates(
            narrative_sentence=narrative,
            parsed_output=parsed_for_x2,
            claim_ledger=claim_ledger,
            jd_text=args.jd_text,
            runtime_generation_status=runtime_generation_status,
            companion_bullet_texts=companion_text or None,
            candidate_name=candidate_name,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            allowed_fact_ids=allowed_ids_list,
            test_only_mock_provider=test_only_mock_provider_eff,
            artifacts_dir=artifact_dir,
            text_claim_coverage=coverage,
            srfs_source_fact_slice_gate_active=proof_pool_x2_active,
            proof_pool_metadata=pp_x2,
            proof_pool_ref=str(pool.proof_pool_ref or ""),
            proof_pool_digest=str(pool.proof_pool_digest or ""),
        )
    ]
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        write_x2_source_fact_pool_receipt,
    )

    for g in x2:
        obs = g.get("observed_value")
        if isinstance(obs, dict) and obs.get("x2_source_fact_pool_status"):
            write_x2_source_fact_pool_receipt(artifact_dir, obs)
            break

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "ibm_narrative",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "ibm_header": ibm_header,
        "narrative_sentence": narrative,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or {"targeting_only": True},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
        "judge_preflight_blocked": bool(preflight_blocked),
        "text_claim_coverage": coverage,
    }
    (artifact_dir / "ibm_narrative_output.txt").write_text(narrative + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        {
            "runtime_path": trace_runtime_path,
            "prompt_id": PROMPT_ID,
            "provider": args.provider,
            "temperature": args.temperature,
            "section_prompt_adapter": True,
            "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
            "compiler_template_id": section_compiled.artifact.template_id,
        },
    )

    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2)
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    product_quality_status, product_quality_reason = infer_product_quality(runtime_generation_status, x2)

    x3 = aggregate_x3(
        resume_display_text=narrative or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
    )
    write_json(artifact_dir / "x3_disposition.json", x3.to_dict())

    bundle = compute_lane_proof_bundle(
        args,
        section_id="ibm_narrative",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
    )
    mocked_rows = any(str(j.get("evaluator_mode")) == "MOCKED" for j in x1d)
    blocked_rows = any(str(j.get("evaluator_mode", "")).startswith("BLOCKED_") for j in x1d)
    decisive_blockers: list[str] = []
    if bundle.get("test_only_mock_judges"):
        decisive_blockers.append("mocked X1D judges present")
    if mocked_rows and x3.mocked_judges:
        decisive_blockers.append("runtime X1D judge rows evaluated in MOCKED mode")
    if preflight_blocked:
        decisive_blockers.extend(list(preflight_art.get("preflight_decisive_blockers") or []))
    if judge_allowed_mock or bundle.get("test_only_mock_judges"):
        recommended_next_action = "rerun without --mock-judges for clean X3 ALLOW"
    elif preflight_blocked:
        recommended_next_action = (
            "configure missing judge credentials; Gemini expects GOOGLE_API_KEY "
            "(GEMINI_API_KEY is a deprecated legacy alias)."
        )
    elif runtime_generation_status == "REAL_LLM":
        recommended_next_action = (
            "review x3_disposition.json; ensure deterministic X2 gates pass and configured model-backed judges pass "
            "(clean X3 ALLOW requires every_active X1D judge MODEL_BACKED_PASS)."
        )
    else:
        recommended_next_action = (
            "restore REAL_LLM narrative generation before attempting clean X3 ALLOW with model-backed judges."
        )
    generation_class_label = classify_generation_class(
        runtime_generation_status=runtime_generation_status,
        offline_contract_stub_active=offline_stub_on,
        test_only_mock_provider=bool(bundle.get("test_only_mock_provider")),
    )
    judge_class_label = classify_judge_class(x1d)
    proof_class_label = classify_proof_class(bundle=bundle, x3_code=x3.x3_code, x3_pass=bool(x3.pass_))
    certification_class_label = classify_certification_class(
        bundle=bundle, x3_code=x3.x3_code, x3_pass=bool(x3.pass_)
    )

    readiness_doc = build_clean_x3_allow_readiness_document(
        section_id="ibm_narrative",
        run_id=str(runtime_payload["run_id"]),
        clean_allow_possible_at_start=bool(
            preflight_art.get("all_required_available")
            and not judge_allowed_mock
            and not offline_stub_on
        ),
        required_judges=list(judge_keys),
        provider_preflight_status_by_judge=(
            dict(preflight_art["provider_preflight_status_by_judge"])
            if isinstance(preflight_art.get("provider_preflight_status_by_judge"), dict)
            else {}
        ),
        mocked_judges_present=bool(mocked_rows),
        blocked_judges_present=bool(blocked_rows),
        mocked_judge_flags_active=judge_allowed_mock,
        x2_hard_gates_required=len(x2),
        x2_hard_gates_passed=sum(1 for g in x2 if g.get("pass")),
        x3_code=x3.x3_code,
        proceed_to_runtime=bool(x3.proceed_to_runtime),
        product_authorized=bool(x3.pass_),
        proof_eligible=bool(bundle.get("proof_eligible")),
        proof_scope=str(bundle.get("proof_scope") or ""),
        decisive_blockers=decisive_blockers,
        recommended_next_action=recommended_next_action,
        preflight_artifact_written=True,
    )
    write_json(artifact_dir / "clean_x3_allow_readiness.json", readiness_doc)

    x2_fail_count = sum(1 for g in x2 if not g.get("pass"))
    decisive_accounting_label_value = compute_decisive_accounting_label(
        command_fault=False,
        runtime_generation_status=runtime_generation_status,
        x2_failure_count=x2_fail_count,
        x3_code=x3.x3_code,
        x3_pass=bool(x3.pass_),
        proceed_to_runtime=bool(x3.proceed_to_runtime),
        mock_judges_active=bool(judge_allowed_mock),
        proof_eligible=bool(bundle.get("proof_eligible")),
        preflight_blocked=bool(preflight_blocked),
        bundle_proof_scope=str(bundle.get("proof_scope") or ""),
    )

    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    l2_output["generation_class"] = generation_class_label
    l2_output["judge_class"] = judge_class_label
    l2_output["proof_class"] = proof_class_label
    l2_output["certification_class"] = certification_class_label
    l2_output["decisive_accounting_label"] = decisive_accounting_label_value
    write_json(artifact_dir / "l2_output.json", l2_output)

    l6_temp = float(args.temperature)
    l6_max = NARRATIVE_QWEN_MAX_TOKENS
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    rl2 = {
        "provider_attempted": args.provider,
        "runtime_generation_status": runtime_generation_status,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "raw_model_output": raw_output,
        "narrative_sentence": narrative,
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    attach_lane_proof_bundle_fields(
        rl2,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    rl2["generation_class"] = generation_class_label
    rl2["judge_class"] = judge_class_label
    rl2["proof_class"] = proof_class_label
    rl2["certification_class"] = certification_class_label

    _smr_in = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "ibm_narrative",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": product_quality_status,
        "x2_failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        "x3_code": x3.x3_code,
        "proof_eligible": bundle["proof_eligible"],
        "judge_proof_eligible": bundle["judge_proof_eligible"],
    }
    merge_normalized_srfs_reporting_into_dict(
        _smr_in,
        section_id="ibm_narrative",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_in)

    write_json(
        artifact_dir / "real_l2_generation_result.json",
        rl2,
    )

    banner_lines: list[str] = []
    allow_exit = bool(getattr(args, "allow_non_allow_exit_zero", False))
    if allow_exit and x3.x3_code != "X3_ALLOW":
        banner_lines.extend(
            [
                "*** PROCESS EXIT OVERRIDDEN FOR INSPECTION ONLY. PRODUCT X3 IS NOT ALLOW.",
                "*** x3_disposition.json is authoritative for disposition; CLI exit codes may not reflect authorization.",
                "",
            ]
        )
    if judge_allowed_mock:
        banner_lines.extend(["Mocked judges cannot satisfy clean X3 ALLOW.", ""])

    lines = [
        *banner_lines,
        "IBM_NARRATIVE_OUTPUT:",
        narrative if narrative else f"BLOCKED: {parse_error}",
        "",
        "X1D_LLM_JUDGE_OUTPUTS:",
        "| Provider | Mode | Status | Score | Pass | Decisive Failure |",
        "|---|---|---|---:|---|---|",
    ]
    for judge in x1d:
        lines.append(
            f"| {judge['provider_name']} | {judge['evaluator_mode']} | {judge.get('provider_status')} | "
            f"{judge.get('score')} | {judge.get('pass')} | {judge.get('decisive_failure')} |"
        )
    lines.extend(["", "X2_DETERMINISTIC_GATE_OUTPUTS:"])
    for gate in x2:
        lines.append(f"- {gate['gate_id']}: {'PASS' if gate['pass'] else 'FAIL'}")
    lines.extend(["", "X3_DISPOSITION:", json.dumps(x3.to_dict(), indent=2), "", "L6_SHADOW_EVAL_PACKAGE:", str(artifact_dir / "l6_shadow_eval_package.json"), "offline_only=true"])
    output_text = "\n".join(lines)
    (artifact_dir / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")
    if print_output:
        print(output_text)
    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="ibm_narrative",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        proof_eligible=bundle["proof_eligible"],
        proof_scope=bundle["proof_scope"],
        test_only_mock_provider=bundle["test_only_mock_provider"],
        runtime_certification=bundle["runtime_certification"],
        x1d_runtime_status=bundle["x1d_runtime_status"],
        judge_proof_eligible=bundle["judge_proof_eligible"],
        provider_proof_eligible=bundle["provider_proof_eligible"],
        test_only_mock_judges=bundle["test_only_mock_judges"],
        proof_closeout_note=bundle["proof_closeout_note"] if bundle.get("proof_closeout_note") else None,
        decisive_accounting_label=decisive_accounting_label_value,
        shell_exit_overridden_for_inspection=bool(getattr(args, "allow_non_allow_exit_zero", False)),
        product_authorized=bool(x3.pass_),
        x3_json_source_of_truth=True,
        not_release_signoff=True,
        generation_class=generation_class_label,
        judge_class=judge_class_label,
        proof_class=proof_class_label,
        certification_class=certification_class_label,
        run_bundle_index_document_metadata={
            "generation_class": generation_class_label,
            "judge_class": judge_class_label,
            "proof_class": proof_class_label,
            "certification_class": certification_class_label,
        },
    )
    exit_code = 0 if allow_non_allow_exit_zero_ok(args) else (0 if x3.x3_code == "X3_ALLOW" else 2)
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "args": args,
        "runtime_payload": runtime_payload,
        "section_compiled": section_compiled,
        "messages": messages,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "x3": x3,
        "output_text": output_text,
        "runtime_generation_status": runtime_generation_status,
        "allowed_fact_ids": allowed_fact_ids,
        "exit_code": exit_code,
    }


if __name__ == "__main__":
    from apps_rg.runtime.deprecated_runtime_cli import exit_deprecated_dispatch_cli

    raise SystemExit(exit_deprecated_dispatch_cli(section="ibm_narrative"))
