"""Unify bullets section lane — canonical implementation for ``python -m apps_rg --section unify_bullets``.

Wires PA → provider → canonical claim ledger v2 envelope → sentence coverage → X2 → X1D → X3 → L6
under ``artifacts/apps_rg/runtime_proofs/unify_bullets`` (same Option-B layout pattern as executive_summary).

**Does not import or call ``unify_bullets_dispatch``.** Dispatch remains a CLI retirement shell only.

**W3 classification:** declared temporary slice (same spine bucket contract as sibling section lanes).
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg --section unify_bullets"
    )

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
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
    pass

from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    classify_ledger_parse_state,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.sections.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    infer_product_quality_blocked_or_mock,
)
from apps_rg.runtime.section_proof.section_input_usage_ledger import build_section_input_usage_ledger_v1
from apps_rg.runtime.sections.unify_bullets_pa import compile_unify_bullets_prompt
from apps_rg.runtime.exit.unify_bullets_x3 import aggregate_x3 as _aggregate_unify_bullets_x3
from apps_rg.runtime.judges.unify_bullets_x1d import run_unify_bullets_judges  # singleton fallback only
from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.reasoning.bullet_lane_generation import generate_bullet_lane_with_sc_and_claude
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    build_employment_targeting_context,
    employment_pool_x1d_judge_rows,
    is_employment_pool_generation,
)
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run, prepare_runtime_proof_run_dir
from apps_rg.runtime.shadow.unify_bullets_l6 import build_l6_shadow_package, extend_unify_bullets_l6_learning_fields
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.sections.executive_summary_lane import resolve_provider_model_name, write_x2_gate_outputs
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict
from apps_rg.runtime.validators.fact_id_typo_repair import (
    repair_fact_id_against_allowlist,
    repair_unify_bullet_surface_id,
)
from apps_rg.runtime.validators.unify_bullets_x2 import (
    PROTECTED_BULLET_DEFAULT,
    UNIFY_BULLET_IDS,
    build_unify_bullets_text_claim_coverage,
    run_unify_bullets_x2_gates,
)


PROMPT_ID = "unify_bullet_tailor_v1"
UNIFY_TEMP_DEFAULT = 0.45
UNIFY_TEMP_RANGE = (0.35, 0.55)
UNIFY_MAX_OUTPUT_TOKENS = 2400
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text

BULLET_ID_ALIASES = {
    **{f"B{i}": f"bul_unify_{i:03d}" for i in range(1, 7)},
    **{f"b{i}": f"bul_unify_{i:03d}" for i in range(1, 7)},
}


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "unify_bullets"
PROMPT_TEMPLATE = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_base_resume() -> tuple[dict[str, Any], Path, str]:
    return load_lane_base_resume_json(repo_root=REPO_ROOT)


def extract_unify_employment(base_resume: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], set[str]]:
    facts_obj = base_resume.get("facts", base_resume)
    for emp in facts_obj.get("employment", []):
        if "unify" not in str(emp.get("employer", "")).lower():
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
            "fact_id": emp.get("fact_id", "exp_unify_001"),
        }
        return header, bullets, allowed
    raise ValueError("Unify employment entry not found in base resume.")


def build_selected_fact_plan(facts: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        facts,
        key=lambda r: UNIFY_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in UNIFY_BULLET_IDS else 99,
    )
    return {
        "section_id": "unify_bullets",
        "selection_method": "canonical_json_all_unify_bullets",
        "facts": ordered,
        "required_fact_ids": list(UNIFY_BULLET_IDS),
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    unify_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("unify_bullets_%Y%m%d_%H%M%S"),
        "section_id": "unify_bullets",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT))
        if base_json_path.is_relative_to(REPO_ROOT)
        else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "unify_header": unify_header,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "unify_bullets_only",
        "full_resume_writable": False,
        "protected_bullet_default": PROTECTED_BULLET_DEFAULT,
        "pool_path_count": 15,
        "selection_model": "qwen_pool_claude_top_n_pass",
    }


def _canonicalize_unify_gate_metric_text(text: str) -> str:
    if not text:
        return text
    s = text
    s = re.sub(
        r"\bsix\s+months\s+to\s+(?:just\s+)?three\s+weeks\b",
        "six months to three weeks",
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(
        r"\b6\s+months\s+to\s+(?:just\s+)?3\s+weeks\b",
        "six months to three weeks",
        s,
        flags=re.IGNORECASE,
    )
    return s


def _canonicalize_bul_w7_unify_source_fact_id(fid: str) -> str:
    """Normalize model typos (whitespace, ``bul_unify_.003`` → ``bul_unify_003``)."""
    s = str(fid).strip()
    if "bul_unify" in s:
        s = re.sub(r"bul_unify_\.", "bul_unify_", s)
        s = re.sub(r"\s+", "", s)
    if s.startswith("bul_w7_unify"):
        s = re.sub(r"\s+", "", s)
    return s


def _legacy_unify_to_ledger_id_map(runtime_payload: dict[str, Any]) -> dict[str, str]:
    """Map canonical ``bul_unify_*`` ids to active ledger ``fact_*`` pool members when needed."""
    allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    if not allowed or any(x.startswith("bul_unify_") for x in allowed):
        return {}
    plan_facts = list((runtime_payload.get("selected_fact_plan") or {}).get("facts") or [])
    plan_ids = [str(f.get("fact_id")) for f in plan_facts if f.get("fact_id")][: len(UNIFY_BULLET_IDS)]
    if len(plan_ids) < len(UNIFY_BULLET_IDS):
        plan_ids = sorted(x for x in allowed if str(x).startswith("fact_"))[: len(UNIFY_BULLET_IDS)]
    remap: dict[str, str] = {}
    for idx, legacy in enumerate(UNIFY_BULLET_IDS):
        if idx < len(plan_ids):
            remap[legacy] = plan_ids[idx]
    return remap


def _remap_unify_id(token: str, remap: dict[str, str], allowed: set[str]) -> str:
    base = str(token).split("_metric_")[0]
    metric_tail = token.split("_metric_", 1)[1] if "_metric_" in token else ""
    mapped = remap.get(base, base)
    repaired = repair_fact_id_against_allowlist(mapped, allowed)
    if metric_tail and repaired in allowed:
        metric_id = f"{repaired}_metric_{metric_tail}"
        return metric_id if metric_id in allowed else repaired
    return repaired


def _normalize_unify_source_fact_id_list(
    ids: Any,
    *,
    remap: dict[str, str] | None = None,
    allowed: set[str] | None = None,
) -> list[str]:
    if ids is None:
        return []
    if not isinstance(ids, list):
        return []
    remap = remap or {}
    allowed = allowed or set()
    out: list[str] = []
    for raw in ids:
        canon = _canonicalize_bul_w7_unify_source_fact_id(str(raw))
        if remap:
            canon = _remap_unify_id(canon, remap, allowed)
        elif allowed:
            canon = repair_unify_bullet_surface_id(canon, allowed)
        else:
            canon = repair_unify_bullet_surface_id(canon, None)
        out.append(canon)
    return out


def _normalize_unify_claim_ledger(
    parsed: dict[str, Any],
    *,
    remap: dict[str, str] | None = None,
    allowed: set[str] | None = None,
) -> None:
    led = parsed.get("claim_ledger")
    if not isinstance(led, list):
        return
    for entry in led:
        if isinstance(entry, dict):
            entry["source_fact_ids"] = _normalize_unify_source_fact_id_list(
                entry.get("source_fact_ids"),
                remap=remap,
                allowed=allowed,
            )


def normalize_unify_parsed_without_ledger_synthesis(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Normalize bullet IDs / metric phrasing only.

    Does **not** fabricate ``claim_ledger`` or ``claim_text`` from ``bullet_text`` when the model omits them.
    """
    if not parsed:
        return parsed
    allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    legacy_remap = _legacy_unify_to_ledger_id_map(runtime_payload)
    protected_default = legacy_remap.get(PROTECTED_BULLET_DEFAULT, PROTECTED_BULLET_DEFAULT)
    normalized_bullets: list[dict[str, Any]] = []
    for idx, bullet in enumerate((parsed.get("bullets") or [])[:6]):
        row = dict(bullet)
        bid = str(row.get("bullet_id", "")).strip()
        bid = repair_unify_bullet_surface_id(bid, allowed if allowed else None)
        row["bullet_id"] = BULLET_ID_ALIASES.get(bid, bid)
        if legacy_remap:
            row["bullet_id"] = legacy_remap.get(row["bullet_id"], row["bullet_id"])
        elif row["bullet_id"] not in UNIFY_BULLET_IDS and idx < len(UNIFY_BULLET_IDS):
            row["bullet_id"] = UNIFY_BULLET_IDS[idx]
        if not row.get("source_fact_ids"):
            row["source_fact_ids"] = [row["bullet_id"]]
        row["source_fact_ids"] = _normalize_unify_source_fact_id_list(
            row.get("source_fact_ids"),
            remap=legacy_remap,
            allowed=allowed,
        )
        bt = row.get("bullet_text")
        if isinstance(bt, str):
            row["bullet_text"] = _canonicalize_unify_gate_metric_text(bt)
        normalized_bullets.append(row)

    out = dict(parsed)
    out["bullets"] = normalized_bullets
    if isinstance(out.get("claim_ledger"), list):
        for cl in out["claim_ledger"]:
            if not isinstance(cl, dict):
                continue
            ct = cl.get("claim_text")
            if isinstance(ct, str):
                cl["claim_text"] = _canonicalize_unify_gate_metric_text(ct)
    _normalize_unify_claim_ledger(out, remap=legacy_remap, allowed=allowed)
    if not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    if not isinstance(out.get("jd_alignment"), dict):
        out["jd_alignment"] = {"targeting_only": True, "jd_used_as_proof": False}
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    out.setdefault("self_check", {"normalized_by_lane": True})
    _sync_unify_claim_ledger_to_bullets(out, remap=legacy_remap, allowed=allowed)
    _repair_protected_unify_bullet_metrics(
        out,
        runtime_payload,
        protected_bullet_id=protected_default,
    )
    from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
        strip_employment_bullet_intensity_model,
    )

    return strip_employment_bullet_intensity_model(out)


def _sync_unify_claim_ledger_to_bullets(
    out: dict[str, Any],
    *,
    remap: dict[str, str] | None = None,
    allowed: set[str] | None = None,
) -> None:
    """Align claim_ledger rows with bullet_text and bullet_id roots (no fabricated claims)."""
    bullets = [b for b in (out.get("bullets") or []) if isinstance(b, dict)]
    if not bullets:
        return
    ledger: list[dict[str, Any]] = []
    for bullet in bullets:
        bt = str(bullet.get("bullet_text") or "").strip()
        if not bt:
            continue
        bid = str(bullet.get("bullet_id") or "").strip()
        sids = _normalize_unify_source_fact_id_list(
            bullet.get("source_fact_ids"),
            remap=remap,
            allowed=allowed,
        )
        if bid and not any(str(x).split("_metric_")[0] == bid for x in sids):
            sids = [bid, *sids]
        if not sids and bid:
            sids = [bid]
        ledger.append({"claim_text": bt, "source_fact_ids": sids})
    if ledger:
        out["claim_ledger"] = ledger


def _repair_protected_unify_bullet_metrics(
    out: dict[str, Any],
    runtime_payload: dict[str, Any],
    *,
    protected_bullet_id: str = PROTECTED_BULLET_DEFAULT,
) -> None:
    """When the protected bullet omits canonical metrics, substitute resume-grounded text from the plan."""
    bullets = list(out.get("bullets") or [])
    protected = next((b for b in bullets if b.get("bullet_id") == protected_bullet_id), None)
    if not isinstance(protected, dict):
        return
    text = str(protected.get("bullet_text") or "")
    if all(token in text for token in ("$22M", "20%", "8", "28")):
        return
    facts = list((runtime_payload.get("selected_fact_plan") or {}).get("facts") or [])
    canonical = ""
    for fact in facts:
        fid = str(fact.get("fact_id") or "")
        claim = str(fact.get("claim_text") or "")
        if fid == protected_bullet_id or ("$22M" in claim and "20%" in claim):
            canonical = claim
            break
    if not canonical:
        return
    protected["bullet_text"] = _canonicalize_unify_gate_metric_text(canonical)
    protected["has_metric"] = True
    protected["metric_raw"] = protected.get("metric_raw") or "$22M, 20%, 8 to 28"
    protected["source_fact_ids"] = [protected_bullet_id]
    changelog = out.setdefault("change_log", [])
    if isinstance(changelog, list):
        changelog.append(
            {
                "operation": "repair_protected_unify_bullet_metrics",
                "reason": "restore_canonical_protected_metrics_from_plan",
            }
        )
    _sync_unify_claim_ledger_to_bullets(out)


def parse_model_json(raw: str) -> tuple[dict[str, Any] | None, str]:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
                strip_employment_bullet_intensity_model,
            )

            return strip_employment_bullet_intensity_model(parsed), ""
    except json.JSONDecodeError as exc:
        return None, f"JSON parse failed: {exc}"
    return None, "Model output was not a JSON object."


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
                f"JSON INVALID: {parse_error}. Return a NEW complete compact JSON object only. "
                "Use bullet_id values bul_unify_001..bul_unify_006 exactly. "
                "Include a non-empty claim_ledger: every row must have non-empty claim_text and valid source_fact_ids. "
                "Include all six bullets bul_unify_001..bul_unify_006. "
                "Do NOT emit rewrite_intensity, rewrite_distribution, or HEAVY/MODERATE/LIGHT_PROTECTED fields."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": UNIFY_MAX_OUTPUT_TOKENS}
    result = call_qwen_vllm(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def _clamp_mock_bullet_text(text: str, *, max_chars: int) -> str:
    """Keep offline mock bullets within line-discipline paragraph cap."""
    cleaned = str(text or "").strip()
    if len(cleaned) <= max_chars:
        return cleaned
    head = cleaned[: max_chars - 3].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{head}..."


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    from apps_rg.runtime.validators.bullet_line_discipline_x2 import DEFAULT_BULLET_MAX_CHARS

    by_id = {f["fact_id"]: f for f in runtime_payload["selected_fact_plan"]["facts"]}
    bullets = []
    claim_ledger = []
    for bid in UNIFY_BULLET_IDS:
        fact = by_id[bid]
        text = str(fact["claim_text"] or "")
        if ": " in text:
            text = text.split(": ", 1)[-1].strip()
        if bid == "bul_unify_001":
            text = (
                "Designed and operationalized a governed agentic AI platform for regulated enterprise "
                "workflows, combining policy gating and validation controls for traceable production delivery."
            )
        elif bid == "bul_unify_006":
            text = (
                "Productized agentic AI platform services, generating $22M IP-led revenue and 20% "
                "gross-margin expansion while scaling the ML organization from 8 to 28 engineers and "
                "compressing delivery from six months to three weeks."
            )
        else:
            text = _clamp_mock_bullet_text(text, max_chars=DEFAULT_BULLET_MAX_CHARS)
        metric_ids = [bid]
        if fact.get("metric_raw"):
            metric_ids.append(f"{bid}_metric_{sha16(fact['metric_raw'])[:8]}")
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "has_metric": fact.get("has_metric", False),
                "metric_raw": fact.get("metric_raw") or None,
                "source_fact_ids": metric_ids,
            }
        )
        claim_ledger.append({"claim_text": text, "source_fact_ids": metric_ids})

    return {
        "bullets": bullets,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": claim_ledger,
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": [{"operation": "offline_contract_stub", "reason": "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"}],
        "self_check": {
            "bullet_count_valid": True,
            "no_cross_contamination": True,
            "metrics_preserved": True,
        },
    }


def bullets_display_text(bullets: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}" for b in bullets)


def enrich_unify_parsed_for_x2(
    parsed: dict[str, Any] | None,
    *,
    coverage: dict[str, Any],
    input_payload_hash: str,
    allowed_fact_ids: set[str],
) -> dict[str, Any] | None:
    if parsed is None:
        return None
    from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
        strip_employment_bullet_intensity_model,
    )

    parsed = strip_employment_bullet_intensity_model(parsed)
    enriched = dict(parsed)
    enriched["text_claim_coverage"] = coverage
    output_body = {
        key: enriched[key]
        for key in (
            "bullets",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
            "text_claim_coverage",
        )
        if key in enriched
    }
    enriched["input_payload_hash"] = input_payload_hash
    enriched["output_payload_hash"] = sha16(json.dumps(output_body, sort_keys=True))
    enriched["claim_ledger_hash"] = sha16(json.dumps(enriched.get("claim_ledger") or [], sort_keys=True))
    enriched["allowed_fact_ids_hash"] = sha16(json.dumps(sorted(allowed_fact_ids), sort_keys=True))
    return enriched


def infer_unify_bullets_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
    *,
    artifact_dir: Path | None = None,
) -> tuple[str, str]:
    from apps_rg.runtime.section_repair_lane_integration import infer_lane_product_quality

    return infer_lane_product_quality(
        runtime_generation_status,
        x2_gates,
        artifact_dir=artifact_dir,
        pass_reason="REAL_LLM output passed all deterministic Unify bullet gates.",
    )


def build_prompt_messages(runtime_payload: dict[str, Any]) -> list[dict[str, str]]:
    """PA-assembled messages via ``section_prompt_adapter`` + unify bullets template."""
    run_id = str(runtime_payload.get("run_id") or "unify_bullets_prompt_build")
    compiled = compile_unify_bullets_prompt(runtime_payload, run_id=run_id)
    return compiled.artifact.messages


def run_unify_bullets_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
) -> dict[str, Any]:
    """Single end-to-end unify_bullets run (qwen_vllm): artifacts + X2/X1D/X3/L6."""
    from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
        section_id="unify_bullets",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    unify_header, _, _ = extract_unify_employment(base)
    unify_facts = list(pool.selected_fact_plan.get("facts") or [])
    unify_facts.sort(
        key=lambda r: UNIFY_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in UNIFY_BULLET_IDS else 99,
    )
    selected_fact_plan = {**pool.selected_fact_plan, "facts": unify_facts}
    allowed_fact_ids = pool.allowed_fact_ids
    proof_pool_metadata = pool.proof_pool_metadata
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        unify_header=unify_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        target_title=str(getattr(args, "target_title", "") or "").strip() or TARGET_TITLE_DEFAULT,
        target_company=str(getattr(args, "target_company", "") or "").strip() or TARGET_COMPANY_DEFAULT,
        jd_text=str(getattr(args, "jd_text", "") or "").strip() or JD_TEXT_DEFAULT,
        briefing=str(getattr(args, "briefing", "") or "").strip() or BRIEFING_DEFAULT,
    )
    runtime_payload["proof_pool_metadata"] = proof_pool_metadata
    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    from apps_rg.runtime.section_repair_lane_integration import (
        record_deterministic_rewrite,
        record_parse_json_retry,
        start_lane_repair_ledger,
    )

    start_lane_repair_ledger(
        artifact_dir, section_id="unify_bullets", run_id=str(runtime_payload["run_id"])
    )

    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )
    from apps_rg.runtime.spine.c0_fec_compose import (
        merge_compiled_prompt_artifact_fec_fields,
    )
    from apps_rg.runtime.sections.upstream_evidence_block import wire_spine_c0_fec_or_block

    blocked = wire_spine_c0_fec_or_block(
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        section_id="unify_bullets",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
        provider=str(args.provider),
        temperature=float(args.temperature),
        max_tokens=UNIFY_MAX_OUTPUT_TOKENS,
        output_filename="unify_bullets_output.txt",
    )
    if blocked is not None:
        return blocked

    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_unify_bullets_prompt(runtime_payload, run_id=runtime_payload["run_id"])
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
        merge_compiled_prompt_artifact_fec_fields(
            {
                "section_id": section_compiled.section_id,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "compiler_template_id": section_compiled.artifact.template_id,
                "pa_prompt_hash": section_compiled.artifact.prompt_hash,
                "provider_prompt_hash": prompt_hash,
                "slot_count": section_compiled.artifact.slot_count,
            },
            runtime_payload,
        ),
    )

    provider_request_data: dict[str, Any] | None = None
    provider_result_data: dict[str, Any] | None = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"

    from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2
    from apps_rg.runtime.section_l2_lane_integration import (
        finalize_section_l2_after_output,
        prepare_section_l2_before_provider,
    )
    from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
        finalize_section_runtime_exhaust_before_l6,
        gate_section_l6_shadow_after_exhaust,
    )

    prepare_section_l2_before_provider(
        artifact_dir,
        "unify_bullets",
        runtime_payload,
        provider_lane=str(args.provider),
    )

    provider_req, provider_payload = build_qwen_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=UNIFY_MAX_OUTPUT_TOKENS,
        temperature_bounds=UNIFY_TEMP_RANGE,
    )
    provider_payload = tag_reasoning_lane(provider_payload, LANE_KEY)
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_payload.get("model", DEFAULT_QWEN_MODEL))
    judge_mode = "mocked" if getattr(args, "mock_judges", False) else "blocked_if_unavailable"
    result, raw_output, parsed_in, parse_error, gen_meta = generate_bullet_lane_with_sc_and_claude(
        section_lane=LANE_KEY,
        slot_kind="bullets",
        provider_payload=provider_payload,
        parse_model_json=parse_model_json,
        normalize_parsed=lambda p: normalize_unify_parsed_without_ledger_synthesis(p, runtime_payload),
        artifact_dir=artifact_dir,
        run_id=str(runtime_payload.get("run_id") or ""),
        temperature_bounds=UNIFY_TEMP_RANGE,
        base_temperature=float(args.temperature) if args.provider == "qwen_vllm" else UNIFY_TEMP_DEFAULT,
        required_bullet_ids=UNIFY_BULLET_IDS,
        targeting_context=build_employment_targeting_context(runtime_payload, section_lane=LANE_KEY),
        judge_mode=judge_mode,
        provider_profile=str(args.provider),
    )
    write_json(artifact_dir / "bullet_lane_generation.json", gen_meta)
    provider_result_data = result.to_dict() if result else {}
    runtime_generation_status = result.runtime_generation_status if result else "BLOCKED"
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    parsed = parsed_in
    if (
        str(args.provider) == "qwen_vllm"
        and result
        and result.runtime_generation_status == "REAL_LLM"
        and parsed_in is None
    ):
        raw_output, parsed_in, parse_error = retry_qwen_for_parse(
            messages, provider_payload, raw_output, parse_error
        )
        if parsed_in is not None:
            record_parse_json_retry(artifact_dir, reason=parse_error or "parse_retry")
        parsed = (
            normalize_unify_parsed_without_ledger_synthesis(parsed_in, runtime_payload) if parsed_in else None
        )
    if parsed is not None:
        from apps_rg.runtime.c0.graph_story_authority import forbid_base_resume_bullet_hydration
        from apps_rg.runtime.sections.unify_canonical_hydration import (
            should_hydrate_unify_bullets_from_canonical,
        )

        forbid_base_resume_bullet_hydration(
            section_id="unify_bullets",
            runtime_payload=runtime_payload,
            parsed=parsed,
            base_resume=base,
            would_hydrate_fn=should_hydrate_unify_bullets_from_canonical,
        )
        _pre_metric_repair = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        _repair_protected_unify_bullet_metrics(out=parsed, runtime_payload=runtime_payload)
        if json.dumps(parsed, sort_keys=True, separators=(",", ":")) != _pre_metric_repair:
            record_deterministic_rewrite(
                artifact_dir,
                operation="repair_protected_unify_bullet_metrics",
                reason="restore_canonical_protected_metrics",
            )
    elif result and result.runtime_generation_status == OFFLINE_CONTRACT_STUB_RUNTIME_STATUS:
        parsed_in, parse_error = parse_model_json(raw_output)
        parsed = normalize_unify_parsed_without_ledger_synthesis(parsed_in, runtime_payload) if parsed_in else None
    elif not parsed:
        parse_error = (result.exact_provider_error if result else None) or parse_error or "provider blocked"

    bullets = list((parsed or {}).get("bullets") or [])
    claim_ledger_raw = list((parsed or {}).get("claim_ledger") or []) if parsed else []
    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output,
        lane_profile="unify_bullets",
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger_raw) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
        claim_id_prefix="unify_bullets_claim",
    )
    claim_ledger = claim_ledger_raw

    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)

    display_for_coverage = bullets_display_text(bullets)
    coverage = build_unify_bullets_text_claim_coverage(bullets, claim_ledger, allowed_fact_ids)
    parsed_for_x2 = enrich_unify_parsed_for_x2(
        parsed,
        coverage=coverage,
        input_payload_hash=input_payload_hash,
        allowed_fact_ids=allowed_fact_ids,
    )
    model_name = resolve_provider_model_name(provider_request_data, provider_result_data)
    temperature = float(args.temperature) if args.provider == "qwen_vllm" else UNIFY_TEMP_DEFAULT

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "unify_bullets",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "product_quality_reason": "",
        "unify_header": unify_header,
        "bullets": bullets,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "text_claim_coverage": coverage,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "allowed_fact_ids_hash": (parsed_for_x2 or {}).get("allowed_fact_ids_hash"),
    }
    from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
        sanitize_l2_employment_bullet_record,
    )

    write_json(artifact_dir / "l2_output.json", sanitize_l2_employment_bullet_record(l2_output))
    (artifact_dir / "unify_bullets_output.txt").write_text(display_for_coverage + "\n", encoding="utf-8")
    write_json(artifact_dir / "selected_fact_plan.json", l2_output["selected_fact_plan"])
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    req_id = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    trace_rr = artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="unify_bullets",
        run_id=str(runtime_payload["run_id"]),
        request_id=req_id,
        trace_root=trace_rr,
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=l2_output["selected_fact_plan"],
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        jd_text=str(runtime_payload.get("jd_text") or ""),
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        briefing_text=str(runtime_payload.get("briefing") or ""),
        jd_alignment=l2_output.get("jd_alignment"),
    )
    from apps_rg.runtime.c0.section_proof_loader import apply_proof_pool_to_usage_ledger

    write_json(
        artifact_dir / "section_input_usage_ledger.json",
        apply_proof_pool_to_usage_ledger(usage_doc, pool),
    )
    judge_mode = "mocked" if getattr(args, "mock_judges", False) else "blocked_if_unavailable"
    if is_employment_pool_generation(gen_meta):
        x1d = employment_pool_x1d_judge_rows(
            artifact_dir=artifact_dir,
            section_id=LANE_KEY,
            gen_meta=gen_meta,
        )
    else:
        judge_keys = ["anthropic_claude"]
        x1d = [
            j.to_dict()
            for j in run_unify_bullets_judges(
                bullets=bullets,
                claim_ledger=claim_ledger,
                judge_keys=judge_keys,
                mode=judge_mode,
                artifact_base=artifact_dir,
            )
        ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    trace = attach_reasoning_to_prompt_trace(
        {
            "runtime_path": "apps_rg.runtime.sections.unify_bullets_lane",
            "prompt_id": PROMPT_ID,
            "provider": args.provider,
            "temperature": temperature,
            "section_prompt_adapter": True,
            "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
            "compiler_template_id": section_compiled.artifact.template_id,
        },
        provider=args.provider,
        lane_key=LANE_KEY,
        provider_result_data=provider_result_data if isinstance(provider_result_data, dict) else None,
    )
    write_json(artifact_dir / "prompt_selection_trace.json", trace)
    write_json(artifact_dir / "fact_check_result.json", {"passed": False, "failed_gates": [], "status": "pending"})
    write_json(
        artifact_dir / "real_l2_generation_result.json",
        {
            "provider_attempted": args.provider,
            "runtime_generation_status": runtime_generation_status,
            "prompt_hash": prompt_hash,
            "model": model_name,
            "input_payload_hash": input_payload_hash,
            "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
            "status": "pending",
        },
    )
    write_json(artifact_dir / "x3_disposition.json", {"x3_code": "PENDING", "status": "pending"})
    write_json(artifact_dir / "section_metric_receipt.json", {"status": "pending", "prompt_hash": prompt_hash})
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", [], section_id="unify_bullets")

    from apps_rg.runtime.product_evidence_authority import x2_proof_pool_gate_flags

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active, srfs_slice_x2_active = x2_proof_pool_gate_flags(pp_x2)

    x2 = [
        g.to_dict()
        for g in run_unify_bullets_x2_gates(
            bullets=bullets,
            parsed_output=parsed_for_x2,
            claim_ledger=claim_ledger,
            allowed_fact_ids=allowed_fact_ids,
            jd_text=runtime_payload["jd_text"],
            runtime_generation_status=runtime_generation_status,
            artifacts_dir=artifact_dir,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            srfs_source_fact_slice_gate_active=srfs_slice_x2_active,
            proof_pool_metadata=pp_x2,
            proof_pool_ref=str(pool.proof_pool_ref or ""),
            proof_pool_digest=str(pool.proof_pool_digest or ""),
            base_resume=base,
            runtime_payload=runtime_payload,
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
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2, section_id="unify_bullets")
    write_json(
        artifact_dir / "fact_check_result.json",
        {
            "passed": not [g for g in x2 if not g["pass"]],
            "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        },
    )

    from apps_rg.runtime.section_repair_lane_integration import finalize_lane_product_quality

    product_quality_status, product_quality_reason = finalize_lane_product_quality(
        artifact_dir,
        runtime_generation_status=runtime_generation_status,
        x2_gates=x2,
        pass_reason="REAL_LLM output passed all deterministic Unify bullet gates.",
        l2_output=l2_output,
    )

    display_for_x3 = display_for_coverage
    x3 = _aggregate_unify_bullets_x3(
        resume_display_text=display_for_x3,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
    )
    proof_bundle = compute_lane_proof_bundle(
        args,
        section_id="unify_bullets",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
    )
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=proof_bundle,
    )
    write_json(artifact_dir / "l2_output.json", sanitize_l2_employment_bullet_record(l2_output))

    from apps_rg.runtime.spine.section_x3_finalize import finalize_section_lane_x3

    x3 = finalize_section_lane_x3(
        artifact_dir=artifact_dir,
        section_id="unify_bullets",
        runtime_payload=runtime_payload,
        x3_result=x3,
        x3_doc_extra={
            "proof_eligible": proof_bundle["proof_eligible"],
            "judge_proof_eligible": proof_bundle["judge_proof_eligible"],
        },
    )
    finalize_section_l2_after_output(artifact_dir, "unify_bullets", runtime_payload)
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "unify_bullets", runtime_payload, repo_root=REPO_ROOT
    )

    l6_temp = float(args.temperature)
    l6_max = UNIFY_MAX_OUTPUT_TOKENS
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6_base = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    l6 = extend_unify_bullets_l6_learning_fields(
        l6_base,
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        provider=str(args.provider),
        x2_gates=x2,
        x3_code=str(x3.x3_code),
        proof_bundle=proof_bundle,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    real_result = {
        "provider_attempted": args.provider,
        "provider_available": bool(provider_result_data and provider_result_data.get("provider_available")),
        "exact_provider_error": (provider_result_data or {}).get("exact_provider_error"),
        "runtime_generation_status": runtime_generation_status,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "temperature": temperature,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "allowed_fact_ids_hash": (parsed_for_x2 or {}).get("allowed_fact_ids_hash"),
        "raw_model_output": raw_output,
        "parsed_model_output": parsed_for_x2,
        "bullets": bullets,
        "claim_ledger": claim_ledger,
        "text_claim_coverage": coverage,
        "fact_check_result": {
            "passed": not [g for g in x2 if not g["pass"]],
            "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        },
        "product_quality_status": product_quality_status,
        "x3_disposition_ref": str(artifact_dir / "x3_disposition.json"),
        "l6_shadow_eval_package_ref": str(artifact_dir / "l6_shadow_eval_package.json"),
    }
    attach_lane_proof_bundle_fields(
        real_result,
        runtime_generation_status=runtime_generation_status,
        bundle=proof_bundle,
    )
    write_json(artifact_dir / "real_l2_generation_result.json", real_result)
    _smr_ub = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "unify_bullets",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": product_quality_status,
        "x2_failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        "x3_code": x3.x3_code,
        "proof_eligible": proof_bundle["proof_eligible"],
        "judge_proof_eligible": proof_bundle["judge_proof_eligible"],
    }
    merge_normalized_srfs_reporting_into_dict(
        _smr_ub,
        section_id="unify_bullets",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_ub)

    output_lines = [
        "L2_UNIFY_BULLETS_OUTPUT:",
        display_for_coverage if bullets else f"BLOCKED: {parse_error}",
        "",
        "X1D_LLM_JUDGE_OUTPUTS:",
        "| Provider | Mode | Score | Threshold | Pass | Decisive Failure | Error |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for judge in x1d:
        output_lines.append(
            f"| {judge['provider_name']} | {judge['evaluator_mode']} | {judge.get('score')} | "
            f"{judge.get('threshold')} | {judge.get('pass')} | {judge.get('decisive_failure')} | "
            f"{judge.get('exact_provider_error') or ''} |"
        )
    output_lines.extend(["", "X2_DETERMINISTIC_GATE_OUTPUTS:"])
    for gate in x2:
        output_lines.append(f"- {gate['gate_id']}: {'PASS' if gate['pass'] else 'FAIL'}")
    output_lines.extend(["", "X3_DISPOSITION:", json.dumps(x3.to_dict(), indent=2), "", "L6_SHADOW_EVAL_PACKAGE:"])
    output_lines.append(str(artifact_dir / "l6_shadow_eval_package.json"))
    output_lines.append("offline_only=true")
    output_text = "\n".join(output_lines)
    (artifact_dir / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")

    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    from apps_rg.runtime.section_one_spine_certification_lane_integration import (
        finalize_section_one_spine_certification,
    )

    finalize_section_one_spine_certification(
        artifact_dir,
        "unify_bullets",
        runtime_payload,
        proof_bundle=proof_bundle,
        runtime_generation_status=runtime_generation_status,
    )
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="unify_bullets",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        proof_eligible=proof_bundle["proof_eligible"],
        judge_proof_eligible=proof_bundle["judge_proof_eligible"],
        proof_scope=proof_bundle["proof_scope"],
        test_only_mock_provider=proof_bundle["test_only_mock_provider"],
        runtime_certification=proof_bundle["runtime_certification"],
        x1d_runtime_status=proof_bundle["x1d_runtime_status"],
        provider_proof_eligible=proof_bundle["provider_proof_eligible"],
        test_only_mock_judges=proof_bundle["test_only_mock_judges"],
        proof_closeout_note=proof_bundle.get("proof_closeout_note") or None,
    )
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "args": args,
        "runtime_payload": runtime_payload,
        "base_path": base_path,
        "base_hash": base_hash,
        "selected_fact_plan_initial": selected_fact_plan,
        "allowed_fact_ids": allowed_fact_ids,
        "section_compiled": section_compiled,
        "messages": messages,
        "input_payload_hash": input_payload_hash,
        "prompt_hash": prompt_hash,
        "compiled_prompt": compiled_prompt,
        "provider_request_data": provider_request_data,
        "provider_result_data": provider_result_data,
        "raw_output": raw_output,
        "parsed": parsed,
        "parse_error": parse_error,
        "parse_status": parse_status,
        "canon_doc": canon_doc,
        "runtime_generation_status": runtime_generation_status,
        "claim_ledger": claim_ledger,
        "bullets_display_text": display_for_coverage,
        "coverage": coverage,
        "parsed_for_x2": parsed_for_x2,
        "model_name": model_name,
        "temperature": temperature,
        "l2_output": l2_output,
        "x1d": x1d,
        "x2": x2,
        "x3": x3,
        "trace": trace,
        "product_quality_status": product_quality_status,
        "product_quality_reason": product_quality_reason,
        "provider_requested_resolved": prq,
        "provider_attempted_resolved": pratt,
        "output_text": output_text,
    }


__all__ = [
    "BRIEFING_DEFAULT",
    "BULLET_ID_ALIASES",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "PROMPT_ID",
    "PROMPT_TEMPLATE",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "UNIFY_MAX_OUTPUT_TOKENS",
    "UNIFY_TEMP_DEFAULT",
    "UNIFY_TEMP_RANGE",
    "build_mock_output",
    "build_runtime_payload",
    "build_selected_fact_plan",
    "bullets_display_text",
    "enrich_unify_parsed_for_x2",
    "extract_unify_employment",
    "infer_unify_bullets_product_quality",
    "load_base_resume",
    "normalize_unify_parsed_without_ledger_synthesis",
    "parse_model_json",
    "retry_qwen_for_parse",
    "run_unify_bullets_execution",
    "sha16",
    "write_json",
]
