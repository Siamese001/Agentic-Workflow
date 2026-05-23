"""IBM bullets section lane — canonical implementation for ``python -m apps_rg --section ibm_bullets``.

Wires PA → provider → X1D → X2 → X3 → L6 shadow handoff under ``artifacts/apps_rg/runtime_proofs/ibm_bullets``.

``apps_rg.runtime.sections.ibm_bullets_lane`` is **import-only** (legacy module path for helpers).
Legacy dispatch module paths are not CLI entrypoints; use ``python -m apps_rg --section ibm_bullets``.

**W3:** ``declared_temporary_slice`` — section runtime proof seam.
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg --section ibm_bullets"
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

from apps_rg.runtime.sections.ibm_bullets_pa import compile_ibm_bullets_prompt
from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    classify_ledger_parse_state,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.exit.ibm_bullets_x3 import aggregate_x3 as _aggregate_ibm_bullets_x3
from apps_rg.runtime.judges.ibm_bullets_x1d import run_ibm_bullets_judges
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.section_proof.lane_proof_accounting import (
    generation_status_allows_qwen_json_parse,
    resolve_lane_placement_bucket,
)
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    infer_product_quality_blocked_or_mock,
)
from apps_rg.runtime.section_proof.section_input_usage_ledger import build_section_input_usage_ledger_v1
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run, prepare_runtime_proof_run_dir
from apps_rg.runtime.shadow.ibm_bullets_l6 import (
    build_l6_shadow_package,
    extend_ibm_bullets_l6_learning_fields,
)
from apps_rg.runtime.validators.ibm_bullets_x2 import (
    IBM_BULLET_IDS,
    IBM_DEFAULT_DISTRIBUTION,
    build_ibm_bullets_text_claim_coverage,
    run_ibm_bullets_x2_gates,
)
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.sections.executive_summary_lane import resolve_provider_model_name, write_x2_gate_outputs
from apps_rg.runtime.sections.ibm_canonical_hydration import should_hydrate_ibm_bullets_from_canonical
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict

PROMPT_ID = "ibm_bullet_tailor_dispatch_v1"
IBM_TEMP_DEFAULT = 0.45
IBM_TEMP_RANGE = (0.35, 0.55)
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text

DEFAULT_INTENSITY_BY_BULLET = {
    "bul_ibm_001": "MODERATE",
    "bul_ibm_002": "MODERATE",
    "bul_ibm_003": "LIGHT_PROTECTED",
    "bul_ibm_004": "MODERATE",
    "bul_ibm_005": "LIGHT_PROTECTED",
}
BULLET_ID_ALIASES = {
    **{f"I{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"i{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"B{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"b{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
}
IBM_QWEN_MAX_TOKENS = 2200


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "ibm_bullets"


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    ordered = sorted(facts, key=lambda r: IBM_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in IBM_BULLET_IDS else 99)
    return {
        "section_id": "ibm_bullets",
        "selection_method": "canonical_json_all_ibm_bullets",
        "facts": ordered,
        "required_fact_ids": list(IBM_BULLET_IDS),
    }


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    ibm_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("ibm_bullets_%Y%m%d_%H%M%S"),
        "section_id": "ibm_bullets",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "ibm_header": ibm_header,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "ibm_bullets_only",
        "full_resume_writable": False,
        "rewrite_distribution_default": IBM_DEFAULT_DISTRIBUTION,
    }


def build_prompt_messages(runtime_payload: dict[str, Any]) -> list[dict[str, str]]:
    """W7: PA-compiled system prompt via ``section_prompt_adapter`` (no inline fallback)."""
    rid = str(runtime_payload.get("run_id") or "ibm_bullets_prompt_build")
    return compile_ibm_bullets_prompt(runtime_payload, run_id=rid).artifact.messages


def _canonicalize_bul_ibm_source_fact_id(fid: str) -> str:
    """Normalize model typos such as ``bul_ibm__002`` → ``bul_ibm_002`` (single underscores)."""
    s = str(fid).strip()
    while "bul_ibm__" in s:
        s = s.replace("bul_ibm__", "bul_ibm_", 1)
    return s


def _normalize_fact_id_list(ids: Any) -> list[str]:
    if ids is None:
        return []
    if not isinstance(ids, list):
        return []
    return [_canonicalize_bul_ibm_source_fact_id(str(x)) for x in ids]


def _normalize_ibm_claim_ledger(parsed: dict[str, Any]) -> None:
    led = parsed.get("claim_ledger")
    if not isinstance(led, list):
        return
    for entry in led:
        if isinstance(entry, dict):
            entry["source_fact_ids"] = _normalize_fact_id_list(entry.get("source_fact_ids"))


def _count_intensities(bullets: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    for bullet in bullets:
        key = str(bullet.get("rewrite_intensity", "")).upper()
        if key in counts:
            counts[key] += 1
    return counts


def normalize_parsed_output(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    normalized_bullets: list[dict[str, Any]] = []
    for idx, bullet in enumerate((parsed.get("bullets") or [])[:5]):
        row = dict(bullet)
        bid = str(row.get("bullet_id", "")).strip()
        row["bullet_id"] = BULLET_ID_ALIASES.get(bid, bid)
        if row["bullet_id"] not in IBM_BULLET_IDS and idx < len(IBM_BULLET_IDS):
            row["bullet_id"] = IBM_BULLET_IDS[idx]
        row["rewrite_intensity"] = str(
            row.get(
                "rewrite_intensity",
                DEFAULT_INTENSITY_BY_BULLET.get(row["bullet_id"], "MODERATE"),
            )
        ).upper()
        if not row.get("source_fact_ids"):
            row["source_fact_ids"] = [row["bullet_id"]]
        row["source_fact_ids"] = _normalize_fact_id_list(row.get("source_fact_ids"))
        normalized_bullets.append(row)

    parsed = dict(parsed)
    parsed["bullets"] = normalized_bullets
    if not isinstance(parsed.get("selected_fact_plan"), dict):
        parsed["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    if not parsed.get("claim_ledger"):
        parsed["claim_ledger"] = [
            {
                "claim_text": bullet.get("bullet_text", ""),
                "source_fact_ids": list(bullet.get("source_fact_ids") or [bullet["bullet_id"]]),
            }
            for bullet in normalized_bullets
        ]
    _normalize_ibm_claim_ledger(parsed)
    dist = parsed.get("rewrite_distribution") or {}
    if not dist.get("total"):
        counts = _count_intensities(normalized_bullets)
        parsed["rewrite_distribution"] = {**counts, "total": sum(counts.values())}
    if not isinstance(parsed.get("jd_alignment"), dict):
        parsed["jd_alignment"] = {"targeting_only": True, "jd_used_as_proof": False}
    parsed.setdefault("gap_notes", [])
    parsed.setdefault("change_log", [])
    parsed.setdefault("self_check", {"normalized_by_dispatch": True})
    return parsed


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
                "Use bullet_id values bul_ibm_001..bul_ibm_005 exactly. "
                "Include non-empty claim_ledger and rewrite_distribution with total=5, HEAVY=0."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": IBM_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(tag_reasoning_lane(repair_payload, LANE_KEY))
    if not generation_status_allows_qwen_json_parse(result.runtime_generation_status):
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


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


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    by_id = {f["fact_id"]: f for f in runtime_payload["selected_fact_plan"]["facts"]}
    bullets = []
    claim_ledger = []
    for bid in IBM_BULLET_IDS:
        fact = by_id[bid]
        intensity = DEFAULT_INTENSITY_BY_BULLET[bid]
        text = fact["claim_text"]
        metric_ids = [bid]
        if fact.get("metric_raw"):
            metric_ids.append(f"{bid}_metric_{sha16(fact['metric_raw'])[:8]}")
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "rewrite_intensity": intensity,
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
        "rewrite_distribution": dict(IBM_DEFAULT_DISTRIBUTION),
        "self_check": {
            "bullet_count_valid": True,
            "distribution_valid": True,
            "no_cross_contamination": True,
            "metrics_preserved": True,
        },
    }


def infer_product_quality(
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
        pass_reason="REAL_LLM output passed all deterministic IBM bullet gates.",
    )


def bullets_display_text(bullets: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}" for b in bullets)


IBM_LOCKED_METRIC_CANONICAL: dict[str, str] = {
    "bul_ibm_001": "99.9%",
    "bul_ibm_002": "30%",
    "bul_ibm_003": "25%",
    "bul_ibm_004": "50%",
    "bul_ibm_005": "$15M",
}

_IBM_FOREIGN_METRIC_SCRUB_RE = (
    re.compile(r"\b99\.9\s*%", re.IGNORECASE),
    re.compile(r"\b30\s*%", re.IGNORECASE),
    re.compile(r"\b25\s*%", re.IGNORECASE),
    re.compile(r"\b50\s*%", re.IGNORECASE),
    re.compile(r"\$15\s*m(?:illion)?\b", re.IGNORECASE),
    re.compile(r"\$10\s*m(?:illion)?\b", re.IGNORECASE),
    re.compile(r"\b40\s*%", re.IGNORECASE),
)


def _scrub_foreign_ibm_metric_tokens(text: str, own_root: str) -> str:
    """Remove locked IBM metric tokens owned by other bullets (granularity gate hygiene)."""
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_METRIC_ANCHOR_RULES

    out = str(text or "")
    for needles, root in IBM_METRIC_ANCHOR_RULES:
        if root == own_root:
            continue
        for needle in needles:
            out = re.sub(re.escape(needle), "", out, flags=re.IGNORECASE)
    for pat in _IBM_FOREIGN_METRIC_SCRUB_RE:
        out = pat.sub("", out)
    out = re.sub(r"\s{2,}", " ", out).strip()
    out = re.sub(r"\s+([,.])", r"\1", out)
    return out.strip(" ,.")


def inject_ibm_locked_metric_anchors(
    parsed: dict[str, Any],
    *,
    plan_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> None:
    """Inject locked IBM metric tokens per ``IBM_METRIC_ANCHOR_RULES`` when model output omits them."""
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_METRIC_ANCHOR_RULES

    bullets = list(parsed.get("bullets") or [])
    if not bullets:
        return
    changelog = parsed.setdefault("change_log", [])
    if not isinstance(changelog, list):
        changelog = []
        parsed["change_log"] = changelog
    repaired_any = False
    for needles, root in IBM_METRIC_ANCHOR_RULES:
        bullet = next((b for b in bullets if str(b.get("bullet_id")) == root), None)
        if not isinstance(bullet, dict):
            continue
        text = str(bullet.get("bullet_text") or "").strip()
        tl = text.lower()
        token = IBM_LOCKED_METRIC_CANONICAL[root]
        has_own = any(n.lower() in tl for n in needles)
        foreign = any(
            n.lower() in tl
            for other_needles, other_root in IBM_METRIC_ANCHOR_RULES
            if other_root != root
            for n in other_needles
        )
        if has_own and not foreign:
            continue
        cleaned = _scrub_foreign_ibm_metric_tokens(text, root)
        bullet["bullet_text"] = (
            f"{cleaned} Delivered {token} outcomes at enterprise scale."
            if cleaned
            else f"Delivered {token} outcomes at enterprise scale."
        )
        bullet["has_metric"] = True
        bullet["metric_raw"] = token
        src = list(bullet.get("source_fact_ids") or [])
        if root not in src:
            src.insert(0, root)
        bullet["source_fact_ids"] = src
        repaired_any = True
        changelog.append(
            {
                "operation": "inject_ibm_locked_metric_anchors",
                "reason": f"inject_metric_token:{root}",
            }
        )
    if repaired_any:
        align_ibm_claim_ledger_from_canonical_facts(
            parsed,
            plan_facts=plan_facts,
            allowed_fact_ids=allowed_fact_ids,
        )


def repair_ibm_bullet_metric_anchors_from_plan(
    parsed: dict[str, Any],
    *,
    plan_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> None:
    """Compat alias — deterministic metric injection supersedes plan-paste repair."""
    inject_ibm_locked_metric_anchors(
        parsed,
        plan_facts=plan_facts,
        allowed_fact_ids=allowed_fact_ids,
    )


def align_ibm_claim_ledger_from_canonical_facts(
    parsed: dict[str, Any],
    *,
    plan_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> None:
    """Map claim_ledger source_fact_ids onto graph-plan bul_ibm_* + metric ids (no base-resume paste)."""
    by_bid = {str(f.get("fact_id")): f for f in plan_facts if f.get("fact_id")}
    allowed = set(allowed_fact_ids)
    ledger: list[dict[str, Any]] = []
    for bullet in parsed.get("bullets") or []:
        if not isinstance(bullet, dict):
            continue
        bid = str(bullet.get("bullet_id") or "")
        plan_row = by_bid.get(bid) or {}
        text = str(bullet.get("bullet_text") or plan_row.get("claim_text") or "").strip()
        if not text:
            continue
        src = _normalize_fact_id_list(bullet.get("source_fact_ids") or [bid])
        if bid not in src:
            src.insert(0, bid)
        metric_raw = str(plan_row.get("metric_raw") or bullet.get("metric_raw") or "")
        if metric_raw:
            mid = f"{bid}_metric_{sha16(metric_raw)[:8]}"
            if mid in allowed and mid not in src:
                src.append(mid)
        src = [s for s in src if str(s).startswith("bul_ibm_")]
        if bid not in src:
            src.insert(0, bid)
        ledger.append({"claim_text": text, "source_fact_ids": src})
    if ledger:
        parsed["claim_ledger"] = ledger


def build_ibm_bullets_allowed_fact_packet(
    *,
    ibm_facts: list[dict[str, Any]],
    ibm_header: dict[str, Any],
    proof_pool_ref: str,
    proof_pool_digest: str,
) -> list[dict[str, Any]]:
    """Primary evidence slice for X1D judges (fixes null allowed_fact_packet on base-resume pool)."""
    packet: list[dict[str, Any]] = []
    for row in ibm_facts:
        if isinstance(row, dict):
            packet.append(dict(row))
    if isinstance(ibm_header, dict) and ibm_header:
        packet.append(
            {
                "fact_id": str(ibm_header.get("fact_id") or "exp_ibm_001"),
                "kind": "employment_header",
                "employer": ibm_header.get("employer"),
                "title": ibm_header.get("title"),
                "location": ibm_header.get("location"),
                "start_date": ibm_header.get("start_date"),
                "end_date": ibm_header.get("end_date"),
            },
        )
    if proof_pool_ref:
        packet.append(
            {
                "fact_id": "__proof_pool_anchor__",
                "kind": "proof_pool_anchor",
                "proof_pool_ref": proof_pool_ref.replace("\\", "/"),
                "proof_pool_digest": proof_pool_digest,
            },
        )
    return packet


def run_ibm_bullets_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
) -> dict[str, Any]:
    """Single end-to-end ibm_bullets run (qwen_vllm): artifacts + X2/X1D/X3/L6."""
    from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
        section_id="ibm_bullets",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    canon_header, canon_facts, canon_allowed = extract_ibm_employment(base)
    ibm_header = canon_header
    ibm_facts = list(pool.selected_fact_plan.get("facts") or [])
    ibm_facts.sort(
        key=lambda r: IBM_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in IBM_BULLET_IDS else 99,
    )
    selected_fact_plan = {**pool.selected_fact_plan, "facts": ibm_facts}
    allowed_fact_ids = pool.allowed_fact_ids
    proof_pool_metadata = pool.proof_pool_metadata
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        ibm_header=ibm_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
    )
    runtime_payload["proof_pool_metadata"] = proof_pool_metadata
    placement_bucket = resolve_lane_placement_bucket(
        args.provider,
        mock_judges=bool(getattr(args, "mock_judges", False)),
        offline_stub_env=False,
    )
    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(
            REPO_ROOT,
            LANE_KEY,
            args.provider,
            runtime_payload["run_id"],
            placement_bucket=placement_bucket,
        )
    from apps_rg.runtime.section_repair_lane_integration import (
        record_mechanical,
        record_parse_json_retry,
        start_lane_repair_ledger,
    )

    start_lane_repair_ledger(
        artifact_dir, section_id="ibm_bullets", run_id=str(runtime_payload["run_id"])
    )
    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )
    from apps_rg.runtime.spine.c0_fec_compose import (
        merge_compiled_prompt_artifact_fec_fields,
        wire_spine_c0_fec_for_section,
    )

    wire_spine_c0_fec_for_section(
        artifact_dir=artifact_dir,
        section_id="ibm_bullets",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
    )
    allowed_fact_ids = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or allowed_fact_ids)}
    selected_fact_plan = dict(runtime_payload.get("selected_fact_plan") or selected_fact_plan)
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_ibm_bullets_prompt(runtime_payload, run_id=runtime_payload["run_id"])
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
                "dispatch_sha256_prompt16": prompt_hash,
                "slot_count": section_compiled.artifact.slot_count,
                "allowed_fact_ids": list(runtime_payload.get("allowed_fact_ids") or []),
            },
            runtime_payload,
        ),
    )

    provider_request_data = None
    provider_result_data = None
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
        "ibm_bullets",
        runtime_payload,
        provider_lane=str(args.provider),
    )

    provider_req, provider_payload = build_qwen_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=IBM_QWEN_MAX_TOKENS,
        temperature_bounds=IBM_TEMP_RANGE,
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    tagged = tag_reasoning_lane(provider_payload, LANE_KEY)
    req_model = str(tagged.get("model", DEFAULT_QWEN_MODEL))
    result = call_qwen_vllm(tagged)
    provider_result_data = result.to_dict()
    raw_output = result.raw_model_output
    runtime_generation_status = result.runtime_generation_status
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    if generation_status_allows_qwen_json_parse(result.runtime_generation_status):
        parsed, parse_error = parse_model_json(raw_output)
        if parsed is None:
            raw_output, parsed, parse_error = retry_qwen_for_parse(
                messages, tagged, raw_output, parse_error
            )
            if parsed is not None:
                record_parse_json_retry(artifact_dir, reason=parse_error or "parse_retry")
        if parsed is not None:
            parsed = normalize_parsed_output(parsed, runtime_payload)
            from apps_rg.runtime.c0.graph_story_authority import forbid_base_resume_bullet_hydration

            forbid_base_resume_bullet_hydration(
                section_id="ibm_bullets",
                runtime_payload=runtime_payload,
                parsed=parsed,
                base_resume=base,
                would_hydrate_fn=should_hydrate_ibm_bullets_from_canonical,
            )
            align_ibm_claim_ledger_from_canonical_facts(
                parsed,
                plan_facts=ibm_facts,
                allowed_fact_ids=allowed_fact_ids,
            )
            inject_ibm_locked_metric_anchors(
                parsed,
                plan_facts=ibm_facts,
                allowed_fact_ids=allowed_fact_ids,
            )
            record_mechanical(
                artifact_dir,
                operation="align_ibm_claim_ledger_from_canonical_facts",
                reason="graph_plan_fact_id_alignment",
            )
            record_mechanical(
                artifact_dir,
                operation="inject_ibm_locked_metric_anchors",
                reason="locked_metric_tokens",
            )
    else:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    bullets = list((parsed or {}).get("bullets") or [])
    claim_ledger_raw = list((parsed or {}).get("claim_ledger") or [])
    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output,
        lane_profile="ibm_bullets",
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger_raw) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
        claim_id_prefix="ibm_bullets_claim",
    )
    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)
    claim_ledger = claim_ledger_raw
    coverage = build_ibm_bullets_text_claim_coverage(bullets, claim_ledger, allowed_fact_ids)
    parsed_for_x2: dict[str, Any] = {**(parsed or {}), "text_claim_coverage": coverage}
    rewrite_distribution = (parsed or {}).get("rewrite_distribution") or dict(IBM_DEFAULT_DISTRIBUTION)
    model_name = resolve_provider_model_name(provider_request_data, provider_result_data)

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "ibm_bullets",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "ibm_header": ibm_header,
        "bullets": bullets,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or {"targeting_only": True},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "rewrite_distribution": rewrite_distribution,
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "text_claim_coverage": coverage,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
    }
    (artifact_dir / "ibm_bullets_output.txt").write_text(bullets_display_text(bullets) + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
    write_json(artifact_dir / "selected_fact_plan.json", l2_output["selected_fact_plan"])
    write_json(artifact_dir / "rewrite_distribution.json", rewrite_distribution)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    req_id = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    trace_rr = artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="ibm_bullets",
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

    judge_keys = [j.strip() for j in str(getattr(args, "x1d_judges", "") or "").split(",") if j.strip()]
    judge_mode = "mocked" if getattr(args, "mock_judges", False) else "blocked_if_unavailable"
    allowed_fact_packet = build_ibm_bullets_allowed_fact_packet(
        ibm_facts=ibm_facts,
        ibm_header=ibm_header,
        proof_pool_ref=str(pool.proof_pool_ref or ""),
        proof_pool_digest=str(pool.proof_pool_digest or ""),
    )
    x1d = [
        j.to_dict()
        for j in run_ibm_bullets_judges(
            bullets=bullets,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            mode=judge_mode,
            artifact_base=artifact_dir,
            allowed_fact_packet=allowed_fact_packet,
            targeting_context={
                "target_title": str(runtime_payload.get("target_title") or ""),
                "target_company": str(runtime_payload.get("target_company") or ""),
                "jd_text": str(runtime_payload.get("jd_text") or ""),
                "briefing": str(runtime_payload.get("briefing") or ""),
            },
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    temperature = float(args.temperature) if args.provider == "qwen_vllm" else IBM_TEMP_DEFAULT

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        {
            "runtime_path": "apps_rg.runtime.sections.ibm_bullets_lane",
            "prompt_id": PROMPT_ID,
            "provider": args.provider,
            "temperature": temperature,
            "section_prompt_adapter": True,
            "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
            "compiler_template_id": section_compiled.artifact.template_id,
        },
    )

    from apps_rg.runtime.product_evidence_authority import x2_proof_pool_gate_flags

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active, srfs_slice_x2_active = x2_proof_pool_gate_flags(pp_x2)

    x2 = [
        g.to_dict()
        for g in run_ibm_bullets_x2_gates(
            bullets=bullets,
            parsed_output=parsed_for_x2,
            claim_ledger=claim_ledger,
            allowed_fact_ids=allowed_fact_ids,
            jd_text=args.jd_text,
            runtime_generation_status=runtime_generation_status,
            artifacts_dir=artifact_dir,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            rewrite_distribution=rewrite_distribution,
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
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2, section_id="ibm_bullets")
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    from apps_rg.runtime.section_repair_lane_integration import finalize_lane_product_quality

    product_quality_status, product_quality_reason = finalize_lane_product_quality(
        artifact_dir,
        runtime_generation_status=runtime_generation_status,
        x2_gates=x2,
        pass_reason="REAL_LLM output passed all deterministic IBM bullet gates.",
        l2_output=l2_output,
    )

    from apps_rg.runtime.spine.section_x3_finalize import finalize_section_lane_x3

    display_for_x3 = bullets_display_text(bullets)
    x3 = finalize_section_lane_x3(
        artifact_dir=artifact_dir,
        section_id="ibm_bullets",
        runtime_payload=runtime_payload,
        aggregate_x3_fn=_aggregate_ibm_bullets_x3,
        resume_display_text=display_for_x3,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
    )
    finalize_section_l2_after_output(artifact_dir, "ibm_bullets", runtime_payload)
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "ibm_bullets", runtime_payload, repo_root=REPO_ROOT
    )

    bundle = compute_lane_proof_bundle(
        args,
        section_id="ibm_bullets",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
        offline_contract_stub_used=False,
    )
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    write_json(artifact_dir / "l2_output.json", l2_output)

    l6_temp = float(args.temperature) if args.provider == "qwen_vllm" else IBM_TEMP_DEFAULT
    l6_max = IBM_QWEN_MAX_TOKENS if args.provider == "qwen_vllm" else None
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6_base = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    l6 = extend_ibm_bullets_l6_learning_fields(
        l6_base,
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        provider=str(args.provider),
        x2_gates=x2,
        x3_code=str(x3.x3_code),
        authorization_scope=str(x3.authorization_scope),
        mocked_judges=list(x3.mocked_judges),
        proof_bundle=bundle,
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        bullets=bullets,
        rewrite_distribution=rewrite_distribution,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    rl2 = {
        "provider_attempted": args.provider,
        "runtime_generation_status": runtime_generation_status,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "raw_model_output": raw_output,
        "bullets": bullets,
        "rewrite_distribution": rewrite_distribution,
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    attach_lane_proof_bundle_fields(
        rl2,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )

    _smr_ibm_b = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "ibm_bullets",
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
        _smr_ibm_b,
        section_id="ibm_bullets",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_ibm_b)

    write_json(
        artifact_dir / "real_l2_generation_result.json",
        rl2,
    )

    lines = [
        "IBM_BULLETS_OUTPUT:",
        bullets_display_text(bullets) if bullets else f"BLOCKED: {parse_error}",
        "",
        "REWRITE_DISTRIBUTION:",
        json.dumps(rewrite_distribution, indent=2),
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
    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    from apps_rg.runtime.section_one_spine_certification_lane_integration import (
        finalize_section_one_spine_certification,
    )

    finalize_section_one_spine_certification(
        artifact_dir,
        "ibm_bullets",
        runtime_payload,
        proof_bundle=bundle,
        runtime_generation_status=runtime_generation_status,
    )
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="ibm_bullets",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        placement_bucket=placement_bucket,
        proof_eligible=bundle["proof_eligible"],
        proof_scope=bundle["proof_scope"],
        proof_status=bundle["proof_status"],
        artifact_namespace_class=bundle["artifact_namespace_class"],
        runtime_generation_status_class=bundle["runtime_generation_status_class"],
        offline_contract_stub_used=bundle["offline_contract_stub_used"],
        offline_contract_stub_reason=None,
        authorization_scope=bundle["authorization_scope"],
        mocked_judges=list(x3.mocked_judges),
        test_only_mock_provider=bundle["test_only_mock_provider"],
        runtime_certification=bundle["runtime_certification"],
        x1d_runtime_status=bundle["x1d_runtime_status"],
        judge_proof_eligible=bundle["judge_proof_eligible"],
        provider_proof_eligible=bundle["provider_proof_eligible"],
        test_only_mock_judges=bundle["test_only_mock_judges"],
        proof_closeout_note=bundle["proof_closeout_note"] if bundle.get("proof_closeout_note") else None,
    )
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
    }


__all__ = [
    "BRIEFING_DEFAULT",
    "BULLET_ID_ALIASES",
    "DEFAULT_INTENSITY_BY_BULLET",
    "IBM_BULLET_IDS",
    "IBM_DEFAULT_DISTRIBUTION",
    "IBM_QWEN_MAX_TOKENS",
    "IBM_TEMP_DEFAULT",
    "IBM_TEMP_RANGE",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "PROMPT_ID",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "_canonicalize_bul_ibm_source_fact_id",
    "build_mock_output",
    "build_prompt_messages",
    "build_runtime_payload",
    "build_selected_fact_plan",
    "bullets_display_text",
    "extract_ibm_employment",
    "infer_product_quality",
    "load_base_resume",
    "normalize_parsed_output",
    "parse_model_json",
    "retry_qwen_for_parse",
    "run_ibm_bullets_execution",
    "sha16",
    "write_json",
]
