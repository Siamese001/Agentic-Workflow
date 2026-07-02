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
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.utils import write_gateway as _wg

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
from apps_rg.runtime.sections.section_generation import build_section_request
from apps_rg.runtime.sections.section_generation import generate_section, tag_reasoning_lane
from apps_rg.runtime.reasoning.bullet_lane_generation import (
    generate_bullet_lane_with_sc_and_claude,
    should_short_circuit_empty_selection,
    truthful_block_reason,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    build_employment_targeting_context,
    employment_pool_x1d_judge_rows,
    is_employment_pool_generation,
)
from apps_rg.runtime.section_proof.lane_proof_accounting import (
    generation_status_allows_json_parse,
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
    build_ibm_bullets_text_claim_coverage,
    run_ibm_bullets_x2_gates,
)
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.sections.executive_summary_lane import resolve_provider_model_name, write_x2_gate_outputs
from apps_rg.runtime.sections.ibm_canonical_hydration import should_hydrate_ibm_bullets_from_canonical
from apps_rg.runtime.sections.graph_evidence_contract import (
    build_graph_evidence_runtime_payload,
    build_selected_graph_evidence_plan,
    merge_graph_evidence_reporting_into_dict,
)

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
# Lane-internal normalization only; stripped before X2 (retired rewrite-intensity model).
IBM_DEFAULT_DISTRIBUTION: dict[str, int] = {
    "HEAVY": 0,
    "MODERATE": 3,
    "LIGHT_PROTECTED": 2,
    "total": 5,
}
BULLET_ID_ALIASES = {
    **{f"I{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"i{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"B{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
    **{f"b{i}": f"bul_ibm_{i:03d}" for i in range(1, 6)},
}
# 2200 -> 8000 (W5, plan apps-rg-aig-remaining-lanes-closeout-d4e1f7): same truncation defect
# as unify_bullets — bullets + claim ledger JSON exceeds the cap, every SC path parses to
# nothing, selector merges 0 bullets. 8000 was validated in the prior apps_rg_e2e session
# (that worktree was removed before its fix merged).
IBM_MAX_OUTPUT_TOKENS = 8000


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
    _wg.ensure_dir(path.parent)
    _wg.write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    return build_selected_graph_evidence_plan(
        section_id="ibm_bullets",
        selection_method="canonical_json_all_ibm_bullets",
        facts=ordered,
        required_fact_ids=list(IBM_BULLET_IDS),
    )


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
    return build_graph_evidence_runtime_payload(
        run_id_prefix="ibm_bullets",
        section_id="ibm_bullets",
        prompt_id=PROMPT_ID,
        repo_root=REPO_ROOT,
        base_json_path=base_json_path,
        base_hash=base_hash,
        selected_graph_evidence_plan=selected_fact_plan,
        allowed_graph_evidence_ids=sorted(allowed_fact_ids),
        target_title=target_title,
        target_company=target_company,
        jd_text=jd_text,
        briefing=briefing,
        writable_context_scope="ibm_bullets_only",
        extra_fields={
            "ibm_header": ibm_header,
            "rewrite_distribution_default": IBM_DEFAULT_DISTRIBUTION,
        },
    )


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


def _clamp_to_ibm_fact_scope(ids: list[str], allowed: set[str]) -> list[str]:
    """Drop citations outside the IBM allowed pool (W5, apps-rg-aig-remaining-lanes-closeout-d4e1f7).

    Mirrors the ``x2_ibm_only_fact_scope`` membership rule (bul_ibm_* root in the allowed pool).
    With W1 dense enrichment live, the model sometimes echoes surfaced ledger atoms (e.g.
    ``fact_solutions_002``) alongside its valid IBM citations; the enrichment is recall-only and
    never proof, so foreign ids are clamped out — same pattern as role_episode
    ``_normalize_source_ids``. When nothing valid remains the row keeps its original ids and the
    scope gate fails honestly.
    """
    if not allowed:
        return ids

    def _ok(sid: str) -> bool:
        return sid.startswith("bul_ibm_") and (
            sid in allowed or sid.split("_metric_")[0] in allowed
        )

    kept = [sid for sid in ids if _ok(sid)]
    return kept or ids


def _normalize_ibm_claim_ledger(parsed: dict[str, Any], allowed: set[str] | None = None) -> None:
    led = parsed.get("claim_ledger")
    if not isinstance(led, list):
        return
    for entry in led:
        if isinstance(entry, dict):
            ids = _normalize_fact_id_list(entry.get("source_fact_ids"))
            entry["source_fact_ids"] = _clamp_to_ibm_fact_scope(ids, allowed or set())


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
        _allowed_scope = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
        row["source_fact_ids"] = _clamp_to_ibm_fact_scope(
            _normalize_fact_id_list(row.get("source_fact_ids")), _allowed_scope
        )
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
    _normalize_ibm_claim_ledger(
        parsed, {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    )
    dist = parsed.get("rewrite_distribution") or {}
    if not dist.get("total"):
        counts = _count_intensities(normalized_bullets)
        parsed["rewrite_distribution"] = {**counts, "total": sum(counts.values())}
    if not isinstance(parsed.get("jd_alignment"), dict):
        parsed["jd_alignment"] = {"targeting_only": True, "jd_used_as_proof": False}
    parsed.setdefault("gap_notes", [])
    parsed.setdefault("change_log", [])
    parsed.setdefault("self_check", {"normalized_by_dispatch": True})
    from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
        strip_employment_bullet_intensity_model,
    )

    return strip_employment_bullet_intensity_model(parsed)


def retry_provider_for_parse(
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
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": IBM_MAX_OUTPUT_TOKENS}
    result = generate_section(tag_reasoning_lane(repair_payload, LANE_KEY))
    if not generation_status_allows_json_parse(result.runtime_generation_status):
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

    from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
        strip_employment_bullet_intensity_model,
    )

    return strip_employment_bullet_intensity_model(
        {
            "bullets": bullets,
            "selected_fact_plan": runtime_payload["selected_fact_plan"],
            "claim_ledger": claim_ledger,
            "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
            "gap_notes": [],
            "change_log": [{"operation": "offline_contract_stub", "reason": "APPS_RG_PROVIDER_MODEL_OFFLINE_CONTRACT_STUB"}],
            "self_check": {
                "bullet_count_valid": True,
                "no_cross_contamination": True,
                "metrics_preserved": True,
            },
        }
    )


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
    "bul_ibm_002": "weeks to hours",
    "bul_ibm_005": "20%",
}

_IBM_FOREIGN_METRIC_SCRUB_RE = (
    re.compile(r"\b99\.9\s*%", re.IGNORECASE),
    re.compile(r"\b30\s*%", re.IGNORECASE),
    re.compile(r"\b25\s*%", re.IGNORECASE),
    re.compile(r"\b50\s*%", re.IGNORECASE),
    re.compile(r"\$15\s*m(?:illion)?\b", re.IGNORECASE),
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
    """Inject locked IBM metric tokens per ``IBM_METRIC_ANCHOR_RULES`` when model output omits them.

    Only stable graph-approved visible metrics are eligible for deterministic insertion.
    If the active plan fact carries a different metric, the plan metric wins; if it
    carries no metric, this helper does not fabricate one.
    """
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_METRIC_ANCHOR_RULES
    from apps_rg.runtime.validators.bullet_line_discipline_x2 import DEFAULT_BULLET_MAX_CHARS

    def _append_metric_clause(base_text: str, clause_core: str) -> str:
        """Inject the metric as an IN-SENTENCE clause (W5, apps-rg-aig-remaining-lanes-closeout-d4e1f7).

        The previous ``"{base}. Delivered {token} at enterprise scale."`` style appended a SECOND
        sentence, deterministically failing ``x2_ibm_bullet_single_thought`` (and often the
        320-char paragraph cap) on every injected bullet. Convert the trailing terminator to a
        comma clause instead, with a shorter fallback when the long clause would break the cap.
        """
        base = (base_text or "").rstrip().rstrip(".!?").rstrip()
        if not base:
            return f"Delivered {clause_core} at enterprise scale."
        long_form = f"{base}, delivering {clause_core} at enterprise scale."
        if len(long_form) <= DEFAULT_BULLET_MAX_CHARS:
            return long_form
        return f"{base}, delivering {clause_core}."

    bullets = list(parsed.get("bullets") or [])
    if not bullets:
        return
    plan_by_bid = {str(f.get("fact_id") or "").strip(): f for f in plan_facts or [] if isinstance(f, dict)}
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

        plan_fact = plan_by_bid.get(root) or {}
        plan_metric = str(plan_fact.get("metric_raw") or "").strip()
        plan_has_metric = bool(plan_fact.get("has_metric") or plan_metric)
        canonical_aligns_with_plan = plan_metric and any(
            n.lower() in plan_metric.lower() for n in needles
        )

        if plan_fact and not canonical_aligns_with_plan:
            # Graph-selector reassigned this slot to a fact with its own metric.
            #   (a) plan_metric exists but conflicts with canonical -> surface the PLAN fact's
            #       own metric token (it is genuinely fact-backed) so the bullet owns a metric
            #       anchor without fabricating the canonical figure. This closes the case where
            #       the model omitted its own approved graph metric and
            #       x2_ibm_metric_anchor_bullet_ownership fails for *_missing_metric_token.
            #   (b) plan_metric is empty/has_metric is false -> the graph fact has no metric to
            #       claim; forcing any metric token would fabricate an unsupported claim, so skip.
            plan_token = _plan_metric_display_token(plan_metric)
            already_has_plan_metric = bool(plan_token) and plan_token.lower() in tl
            if plan_has_metric and plan_token and not already_has_plan_metric:
                cleaned = _scrub_foreign_ibm_metric_tokens(text, root)
                base_text = cleaned or text
                bullet["bullet_text"] = _append_metric_clause(base_text, plan_token)
                bullet["has_metric"] = True
                bullet["metric_raw"] = plan_metric
                src = list(bullet.get("source_fact_ids") or [])
                if root not in src:
                    src.insert(0, root)
                bullet["source_fact_ids"] = src
                repaired_any = True
                changelog.append(
                    {
                        "operation": "inject_ibm_plan_fact_metric",
                        "reason": f"surface_plan_metric:{root}:{plan_token}",
                    }
                )
                continue
            reason_detail = (
                f"plan_fact_metric_does_not_match_canonical:{root} "
                f"(canonical={token}, plan_metric={plan_metric!r}, has_metric={plan_has_metric})"
            )
            changelog.append(
                {
                    "operation": "skip_ibm_locked_metric_anchor",
                    "reason": (
                        f"{reason_detail} \u2014 graph selector chose this fact intentionally; "
                        "do not append canonical-metric suffix"
                    ),
                }
            )
            continue

        cleaned = _scrub_foreign_ibm_metric_tokens(text, root)
        bullet["bullet_text"] = _append_metric_clause(cleaned, f"{token} outcomes")
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


def demote_gated_ibm_metrics(parsed: dict[str, Any]) -> None:
    """Demote metric IDs that are not approved by the IBM graph allow-list."""
    if not isinstance(parsed, dict):
        return
    changelog = parsed.get("change_log")
    if not isinstance(changelog, list):
        return
    from apps_rg.runtime.sections.ibm_role_episode_evidence import PROMOTABLE_METRIC_OUTCOME_IDS

    allowed = set(PROMOTABLE_METRIC_OUTCOME_IDS)
    demoted_bullet_ids: set[str] = set()
    for entry in changelog:
        if not isinstance(entry, dict):
            continue
        ids = [str(x) for x in (entry.get("metric_outcome_ids") or [])]
        approved_ids = [x for x in ids if x in allowed]
        rejected_ids = [x for x in ids if x not in allowed and x.startswith("metric_ibm_")]
        if rejected_ids:
            bid = str(entry.get("bullet_id") or "").strip()
            if bid and not approved_ids:
                demoted_bullet_ids.add(bid)
            entry["metric_outcome_ids"] = approved_ids
            entry.setdefault("change_notes", [])
            if isinstance(entry["change_notes"], list):
                entry["change_notes"].append("demoted_unapproved_ibm_metric_to_qualitative")
    if not demoted_bullet_ids:
        return
    for bullet in parsed.get("bullets") or []:
        if not isinstance(bullet, dict):
            continue
        if str(bullet.get("bullet_id") or "").strip() not in demoted_bullet_ids:
            continue
        bullet["metric_raw"] = ""
        bullet["has_metric"] = False


# HOLD/DO_NOT_PROMOTE figures (x2_ibm_hold_metric_forbidden_in_output) — never promotable.
_HOLD_METRIC_TEXT_RE = re.compile(
    r"(?:\b(?:by|of|to|at|up to|achieving|delivering|driving|with)\s+)?"
    r"(?:\$\s*(?:15|30)\s*M\b|\b(?:25|30|35|40)\s*%)",
    re.IGNORECASE,
)


def demote_hold_metrics(parsed: dict[str, Any]) -> None:
    """Strip HOLD/DO_NOT_PROMOTE figures (25/30/35/40%, $15M, $30M) to qualitative prose.

    W5 (plan apps-rg-aig-remaining-lanes-closeout-d4e1f7): sibling of
    ``demote_gated_ibm_metrics`` — the PA forbids these figures, but when a generation path
    still surfaces one, this deterministic backstop removes the unpromotable figure so the
    bullet reads qualitatively. Graph-approved IBM metrics are never touched.
    """
    if not isinstance(parsed, dict):
        return
    from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

    for bullet in parsed.get("bullets") or []:
        if not isinstance(bullet, dict):
            continue
        text = str(bullet.get("bullet_text") or "")
        if not _HOLD_METRIC_TEXT_RE.search(text):
            continue
        # Sentence-aware demotion: when the bullet has multiple sentences, DROP the sentence
        # carrying the HOLD figure (also restores single-thought shape); when it is the only
        # sentence, strip just the figure in place.
        sentences = split_sentences(text)
        if len(sentences) > 1:
            kept = [s for s in sentences if not _HOLD_METRIC_TEXT_RE.search(s)]
            new_text = " ".join(kept).strip() if kept else _HOLD_METRIC_TEXT_RE.sub("", text)
        else:
            new_text = _HOLD_METRIC_TEXT_RE.sub("", text)
        new_text = re.sub(r"\s{2,}", " ", new_text).replace(" ,", ",").replace(" .", ".").strip()
        if new_text and not new_text.rstrip().endswith((".", "!", "?")):
            new_text = new_text.rstrip() + "."
        bullet["bullet_text"] = new_text
        mr = str(bullet.get("metric_raw") or "")
        if _HOLD_METRIC_TEXT_RE.search(mr):
            bullet["metric_raw"] = ""
            bullet["has_metric"] = bool(re.search(r"[\$\d]", new_text))


def scrub_cross_slot_plan_metrics(parsed: dict[str, Any], plan_facts: list[dict[str, Any]]) -> None:
    """Remove a slot's plan-fact metric token from every OTHER slot's bullet text.

    W4-residual (plan apps-rg-aig-remaining-lanes-closeout-d4e1f7): the gemini X1D judge
    decisive-failed ibm_bullets because a bullet carried ANOTHER slot's metric. The canonical-anchor scrub
    only covers IBM_METRIC_ANCHOR_RULES tokens; plan-fact metrics (graph-selected) were not
    scrubbed cross-slot. A metric claim not supported by the slot's own source fact is
    unsupported by construction — remove it deterministically.
    """
    if not isinstance(parsed, dict):
        return
    tokens_by_root: dict[str, str] = {}
    for f in plan_facts or []:
        if not isinstance(f, dict):
            continue
        tok = _plan_metric_display_token(str(f.get("metric_raw") or ""))
        if tok:
            tokens_by_root[str(f.get("fact_id") or "").strip()] = tok
    if not tokens_by_root:
        return
    for bullet in parsed.get("bullets") or []:
        if not isinstance(bullet, dict):
            continue
        own = str(bullet.get("bullet_id") or "").strip()
        text = str(bullet.get("bullet_text") or "")
        changed = False
        for root, tok in tokens_by_root.items():
            if root == own or not tok or tok.lower() not in text.lower():
                continue
            # Clause-aware removal: strip the token plus its dangling verb/prepositional shell.
            clause = re.compile(
                r"(?:,?\s*(?:and\s+)?(?:generating|delivering|driving|producing|securing|adding)\s+)?"
                + re.escape(tok)
                + r"(?:\s+(?:in|of)\s+[A-Za-z -]{0,40}?)?(?=$|[,.;)])",
                re.IGNORECASE,
            )
            new = clause.sub("", text)
            text = new if new != text else re.sub(re.escape(tok), "", text, flags=re.IGNORECASE)
            changed = True
            if str(bullet.get("metric_raw") or "").strip().lower().startswith(tok.lower()):
                bullet["metric_raw"] = ""
                bullet["has_metric"] = False
        if changed:
            text = re.sub(r"\s{2,}", " ", text)
            text = re.sub(r"\s+([,.])", r"\1", text).strip().strip(",")
            if text and not text.rstrip().endswith((".", "!", "?")):
                text = text.rstrip() + "."
            bullet["bullet_text"] = text


def _plan_metric_display_token(plan_metric: str) -> str:
    """Extract a single display-case numeric token from a plan fact's metric_raw.

    Mirrors the X2 gate's accepted-chunk regex (``[\\$\\d][\\$\\d.,%a-z-]*``) so the injected token
    is recognized by ``x2_ibm_metric_anchor_bullet_ownership``. Returns the first numeric/currency
    token from the first ``|``-delimited metric segment. Empty when no numeric token is present.
    """
    seg = str(plan_metric or "").split("|")[0].strip()
    m = re.search(r"[\$\d][\$\d.,%]*[A-Za-z%]?", seg)
    return m.group(0).strip() if m else ""


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
    approved_metric_evidence: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Primary evidence slice for X1D judges (fixes null allowed_fact_packet on base-resume pool).

    ``approved_metric_evidence`` surfaces approved, promotable, section-eligible
    metric_outcome nodes so the X1D grader can support a bullet's graph-approved metric
    claim (e.g. the alliance "20% joint revenue growth") even when the per-bundle metric
    was capped out of the proof-pool contribution by section display budgeting — without
    changing selection, the X2 allowed-fact scope, or generation.
    """
    packet: list[dict[str, Any]] = []
    for row in ibm_facts:
        if isinstance(row, dict):
            packet.append(dict(row))
    for row in approved_metric_evidence or []:
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
    """Single end-to-end ibm_bullets run (external_model): artifacts + X2/X1D/X3/L6."""
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
    # Plan-level HOLD demotion (W5, apps-rg-aig-remaining-lanes-closeout-d4e1f7): the ledger can
    # assign a slot a HOLD/DO_NOT_PROMOTE figure as its plan metric (e.g. bul_ibm_002 ->
    # "30% cost optimization"), which made the prompt's METRIC SURFACING and the anchor gate
    # demand the very token x2_ibm_hold_metric_forbidden_in_output bans — unsatisfiable by
    # construction. Demote the fact to qualitative at the plan seam so prompt, anchor gate, and
    # HOLD gate agree; the fact's qualitative claim_text is unchanged.
    for _f in ibm_facts:
        if isinstance(_f, dict) and _HOLD_METRIC_TEXT_RE.search(str(_f.get("metric_raw") or "")):
            _f["metric_raw"] = ""
            _f["has_metric"] = False
            _f["metric_demoted_hold"] = True
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
        _wg.ensure_dir(artifact_dir)
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
    from apps_rg.runtime.sections.section_generation import merge_transport_context

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
        section_id="ibm_bullets",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
        provider=str(args.provider),
        temperature=float(args.temperature),
        max_tokens=IBM_MAX_OUTPUT_TOKENS,
        output_filename="ibm_bullets_output.txt",
    )
    if blocked is not None:
        return blocked
    allowed_fact_ids = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or allowed_fact_ids)}
    selected_fact_plan = dict(runtime_payload.get("selected_fact_plan") or selected_fact_plan)
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_ibm_bullets_prompt(runtime_payload, run_id=runtime_payload["run_id"])
    messages = section_compiled.artifact.messages
    compiled_prompt = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    prompt_hash = sha16(compiled_prompt)
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    _wg.write_text(
        artifact_dir / "compiled_prompt.txt",
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

    from apps_rg.runtime.section_model_limits import (
        external_openai_generation_model,
        resolve_section_generation_model,
    )

    section_model = (
        external_openai_generation_model(section_id=LANE_KEY)
        if str(args.provider) == "external_openai"
        else resolve_section_generation_model(LANE_KEY)
    )
    provider_req, provider_payload = build_section_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=IBM_MAX_OUTPUT_TOKENS,
        temperature_bounds=IBM_TEMP_RANGE,
        model=section_model,
        provider_requested=str(args.provider),
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    tagged = tag_reasoning_lane(provider_payload, LANE_KEY)
    req_model = str(tagged.get("model", section_model))
    judge_mode = "mocked" if getattr(args, "mock_judges", False) else "blocked_if_unavailable"
    result, raw_output, parsed, parse_error, gen_meta = generate_bullet_lane_with_sc_and_claude(
        section_lane=LANE_KEY,
        slot_kind="bullets",
        provider_payload=tagged,
        parse_model_json=parse_model_json,
        normalize_parsed=lambda p: normalize_parsed_output(p, runtime_payload),
        artifact_dir=artifact_dir,
        run_id=str(runtime_payload.get("run_id") or ""),
        temperature_bounds=IBM_TEMP_RANGE,
        base_temperature=float(args.temperature) if args.provider == "external_claude" else IBM_TEMP_DEFAULT,
        required_bullet_ids=IBM_BULLET_IDS,
        targeting_context=build_employment_targeting_context(runtime_payload, section_lane=LANE_KEY),
        judge_mode=judge_mode,
        provider_profile=str(args.provider),
    )
    write_json(artifact_dir / "bullet_lane_generation.json", gen_meta)
    provider_result_data = result.to_dict() if result else {}
    runtime_generation_status = result.runtime_generation_status if result else "BLOCKED"
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    if generation_status_allows_json_parse(runtime_generation_status):
        if parsed is None:
            if str(args.provider) == "external_claude":
                raw_output, parsed, parse_error = retry_provider_for_parse(
                    messages, tagged, raw_output, parse_error
                )
                if parsed is not None:
                    record_parse_json_retry(artifact_dir, reason=parse_error or "parse_retry")
                    parsed = normalize_parsed_output(parsed, runtime_payload)
        if parsed is not None:
            from apps_rg.runtime.c0.graph_story_authority import forbid_base_resume_bullet_hydration

            forbid_base_resume_bullet_hydration(
                section_id="ibm_bullets",
                runtime_payload=runtime_payload,
                parsed=parsed,
                base_resume=base,
                would_hydrate_fn=should_hydrate_ibm_bullets_from_canonical,
            )
            # Deterministic metric anchoring: when a bullet's graph-selected plan fact carries
            # an approved metric the model dropped, surface that fact-backed token so
            # x2_ibm_metric_anchor_bullet_ownership is satisfied without fabricating figures.
            inject_ibm_locked_metric_anchors(
                parsed,
                plan_facts=ibm_facts,
                allowed_fact_ids=allowed_fact_ids,
            )
            # Demote gated/unconfirmed metrics to qualitative so
            # x2_ibm_metric_outcome_id_required_when_has_metric does not block on an
            # unpromotable figure.
            demote_gated_ibm_metrics(parsed)
            # W5 backstop: strip HOLD/DO_NOT_PROMOTE figures (25/30/35/40%, $15M, $30M)
            # any path still surfaced despite the PA ban.
            demote_hold_metrics(parsed)
            # W4-residual: a bullet must not claim ANOTHER slot's plan metric; scrub deterministically.
            scrub_cross_slot_plan_metrics(parsed, ibm_facts)
            align_ibm_claim_ledger_from_canonical_facts(
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
                operation="inject_ibm_plan_fact_metric_anchors",
                reason="surface_fact_backed_metric_tokens_model_dropped",
            )
    else:
        parsed = None
        # E2E-09/10: do not label REAL_LLM output as 'provider blocked' — the provider
        # produced output; an empty selection / parse failure is the real downstream cause.
        parse_error = truthful_block_reason(result, runtime_generation_status, parse_error)

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
    _wg.write_text(artifact_dir / "raw_model_output.txt", raw_output or "", encoding="utf-8")
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)

    # W4.4 (G16): a REAL_LLM employment-pool run that merged 0 bullets fails ONCE with the
    # true reason instead of cascading through X1D + the ~15-gate X2 wall. Provider-BLOCKED
    # runs keep today's path. Raw/parsed/provider/pool artifacts above stay as written.
    sc_fire, sc_reason = should_short_circuit_empty_selection(
        gen_meta, bullets, runtime_generation_status, artifact_dir=artifact_dir
    )
    if sc_fire:
        from apps_rg.runtime.sections.upstream_evidence_block import (
            write_empty_selection_short_circuit_artifacts,
        )

        return write_empty_selection_short_circuit_artifacts(
            repo_root=REPO_ROOT,
            artifact_dir=artifact_dir,
            section_id="ibm_bullets",
            provider=str(args.provider),
            runtime_payload=runtime_payload,
            reason=sc_reason,
            gen_meta=gen_meta,
            bullets_in_merged=len(bullets),
            output_filename="ibm_bullets_output.txt",
        )

    claim_ledger = claim_ledger_raw
    coverage = build_ibm_bullets_text_claim_coverage(bullets, claim_ledger, allowed_fact_ids)
    from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
        strip_employment_bullet_intensity_model,
    )

    parsed_for_x2 = strip_employment_bullet_intensity_model(
        {**(parsed or {}), "text_claim_coverage": coverage}
    ) or {"text_claim_coverage": coverage}
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
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "text_claim_coverage": coverage,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
    }
    _wg.write_text(artifact_dir / "ibm_bullets_output.txt", bullets_display_text(bullets) + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
    write_json(artifact_dir / "selected_fact_plan.json", l2_output["selected_fact_plan"])
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
    from apps_rg.runtime.sections.ibm_role_episode_evidence import (
        approved_promotable_metric_evidence,
    )

    allowed_fact_packet = build_ibm_bullets_allowed_fact_packet(
        ibm_facts=ibm_facts,
        ibm_header=ibm_header,
        proof_pool_ref=str(pool.proof_pool_ref or ""),
        proof_pool_digest=str(pool.proof_pool_digest or ""),
        approved_metric_evidence=approved_promotable_metric_evidence("ibm_bullets"),
    )
    # Variance-class alignment (2026-06): on the employment-pool path the Claude pool
    # SELECTOR has already model-scored every slot, but that selector is advisory-only. The
    # formal X1D proof row still comes from the section policy provider roster.
    from apps_rg.runtime.section_judge_policy import get_section_judge_policy

    proof_judge_keys = list(get_section_judge_policy("ibm_bullets").required_judge_providers)
    proof_x1d = [
        j.to_dict()
        for j in run_ibm_bullets_judges(
            bullets=bullets,
            claim_ledger=claim_ledger,
            judge_keys=proof_judge_keys,
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
    if is_employment_pool_generation(gen_meta):
        x1d = proof_x1d + employment_pool_x1d_judge_rows(
            artifact_dir=artifact_dir,
            section_id="ibm_bullets",
            gen_meta=gen_meta,
        )
    else:
        x1d = proof_x1d
    temperature = float(args.temperature) if args.provider == "external_claude" else IBM_TEMP_DEFAULT

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

    # Optional adjudicator: the default IBM judge is ONE composite judge. Escalate to the
    # multi-provider panel ONLY when a borderline condition fires (judge confidence near
    # threshold, X2-passed-but-judge-flags-risk, or a high-value metric bullet is borderline).
    # This is a SECOND OPINION, not a regeneration — it appends panel rows to the X1D set that
    # X3 then aggregates. Non-triggered runs keep the single composite judge (fast path).
    from apps_rg.runtime.judges.bullet_adjudicator import (
        ADJUDICATOR_PANEL_PROVIDER_KEYS,
        evaluate_bullet_adjudicator_trigger,
    )
    from apps_rg.runtime.judges.bullet_x2_aggregation import aggregate_bullet_section

    _x2_failed_ids = [g["gate_id"] for g in x2 if not g.get("pass", True)]
    _existing_judge_keys = {str(j.get("provider_key") or "") for j in x1d}
    _adj_decision = evaluate_bullet_adjudicator_trigger(
        section_id="ibm_bullets",
        composite_judges=x1d,
        x2_failed_gate_ids=_x2_failed_ids,
        bullets=bullets,
    )
    _agg = aggregate_bullet_section(
        section_id="ibm_bullets",
        composite_judges=x1d,
        x2_failed_gate_ids=_x2_failed_ids,
    )
    _should_adjudicate = _adj_decision.should_escalate or _agg.should_adjudicate
    _panel_keys = [
        k for k in ADJUDICATOR_PANEL_PROVIDER_KEYS if k and k not in _existing_judge_keys
    ]
    _adjudication_record: dict[str, Any] = {
        "section_id": "ibm_bullets",
        "trigger_decision": _adj_decision.to_dict(),
        "aggregation": _agg.to_dict(),
        "escalated": False,
        "panel_provider_keys": [],
    }
    if _should_adjudicate and _panel_keys:
        _panel_rows = [
            j.to_dict()
            for j in run_ibm_bullets_judges(
                bullets=bullets,
                claim_ledger=claim_ledger,
                judge_keys=_panel_keys,
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
        for _r in _panel_rows:
            _r["adjudicator_panel_row"] = True
        x1d = list(x1d) + _panel_rows
        _adjudication_record["escalated"] = True
        _adjudication_record["panel_provider_keys"] = list(_panel_keys)
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})
    write_json(artifact_dir / "bullet_adjudication.json", _adjudication_record)
    write_json(artifact_dir / "bullet_x2_aggregation.json", _agg.to_dict())

    # W4.1 (G14): bullet judge-feedback reselection — on a MODEL_BACKED judge fail (decisive
    # or soft) after an all-pass X2 wall, swap the implicated slot(s) to the first compliant
    # on-disk pool alternate, re-run the FULL X2 set (revert on regression), and re-judge ONCE
    # at the same rubric/threshold. Bounded exactly-once via reselection_receipt.json.
    from apps_rg.runtime.reasoning.bullet_fact_entailment import build_slot_entailment_corpus
    from apps_rg.runtime.reasoning.bullet_pool_reselection import (
        LaneRebuildState,
        run_bullet_judge_reselection,
    )
    from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
        strip_employment_bullet_intensity_model,
    )

    def _resel_post_chain(doc: dict[str, Any]) -> dict[str, Any]:
        doc = normalize_parsed_output(doc, runtime_payload) or doc
        inject_ibm_locked_metric_anchors(doc, plan_facts=ibm_facts, allowed_fact_ids=allowed_fact_ids)
        demote_gated_ibm_metrics(doc)
        demote_hold_metrics(doc)
        scrub_cross_slot_plan_metrics(doc, ibm_facts)
        align_ibm_claim_ledger_from_canonical_facts(
            doc, plan_facts=ibm_facts, allowed_fact_ids=allowed_fact_ids
        )
        return doc

    def _resel_rebuild_state(new_parsed: dict[str, Any]) -> LaneRebuildState:
        new_bullets = list(new_parsed.get("bullets") or [])
        new_ledger = list(new_parsed.get("claim_ledger") or [])
        new_parse_status, new_invalid = classify_ledger_parse_state(
            new_parsed,
            parse_error=parse_error,
            raw_output=raw_output,
            lane_profile="ibm_bullets",
        )
        new_norm = normalize_exec_summary_claim_ledger(new_ledger) if new_parse_status == "OK" else []
        new_canon = build_canonical_claim_ledger_v2_payload(
            new_norm,
            parse_status=new_parse_status,
            invalid_reason=new_invalid if new_parse_status != "OK" else None,
            claim_id_prefix="ibm_bullets_claim",
        )
        new_coverage = build_ibm_bullets_text_claim_coverage(new_bullets, new_ledger, allowed_fact_ids)
        new_parsed_for_x2 = strip_employment_bullet_intensity_model(
            {**new_parsed, "text_claim_coverage": new_coverage}
        ) or {"text_claim_coverage": new_coverage}
        new_usage = build_section_input_usage_ledger_v1(
            section_id="ibm_bullets",
            run_id=str(runtime_payload["run_id"]),
            request_id=req_id,
            trace_root=trace_rr,
            repo_root=REPO_ROOT,
            artifact_dir=artifact_dir,
            runtime_payload=runtime_payload,
            selected_fact_plan=new_parsed.get("selected_fact_plan") or l2_output["selected_fact_plan"],
            claim_ledger=new_ledger,
            allowed_fact_ids=allowed_fact_ids,
            jd_text=str(runtime_payload.get("jd_text") or ""),
            target_title=str(runtime_payload.get("target_title") or ""),
            target_company=str(runtime_payload.get("target_company") or ""),
            briefing_text=str(runtime_payload.get("briefing") or ""),
            jd_alignment=l2_output.get("jd_alignment"),
        )
        return LaneRebuildState(
            parsed=new_parsed,
            bullets=new_bullets,
            claim_ledger=new_ledger,
            coverage=new_coverage,
            parsed_for_x2=new_parsed_for_x2,
            canon_doc=new_canon,
            usage_doc=new_usage,
            display_text=bullets_display_text(new_bullets),
            parse_status=new_parse_status,
        )

    def _resel_run_x2(
        state: LaneRebuildState, x1d_rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return [
            g.to_dict()
            for g in run_ibm_bullets_x2_gates(
                bullets=state.bullets,
                parsed_output=state.parsed_for_x2,
                claim_ledger=state.claim_ledger,
                allowed_fact_ids=allowed_fact_ids,
                jd_text=args.jd_text,
                runtime_generation_status=runtime_generation_status,
                artifacts_dir=artifact_dir,
                provider_requested=args.provider,
                provider_attempted=args.provider,
                model_name=model_name,
                raw_output=raw_output,
                x1d_judges=x1d_rows,
                srfs_source_fact_slice_gate_active=srfs_slice_x2_active,
                proof_pool_metadata=pp_x2,
                proof_pool_ref=str(pool.proof_pool_ref or ""),
                proof_pool_digest=str(pool.proof_pool_digest or ""),
                base_resume=base,
                runtime_payload=runtime_payload,
            )
        ]

    def _resel_run_judges(state: LaneRebuildState, keys: list[str]) -> list[dict[str, Any]]:
        return [
            j.to_dict()
            for j in run_ibm_bullets_judges(
                bullets=state.bullets,
                claim_ledger=state.claim_ledger,
                judge_keys=list(keys),
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

    def _resel_write_usage(state: LaneRebuildState) -> None:
        write_json(
            artifact_dir / "section_input_usage_ledger.json",
            apply_proof_pool_to_usage_ledger(state.usage_doc, pool),
        )

    def _resel_write_artifacts(state: LaneRebuildState, x2_rows: list[dict[str, Any]]) -> None:
        write_json(
            artifact_dir / "parsed_output.json",
            {"parsed": state.parsed, "parse_error": parse_error, "parse_status": state.parse_status},
        )
        _wg.write_text(artifact_dir / "ibm_bullets_output.txt", state.display_text + "\n", encoding="utf-8")
        write_json(artifact_dir / "claim_ledger.json", state.claim_ledger)
        write_json(artifact_dir / "text_claim_coverage.json", state.coverage)
        write_json(artifact_dir / "canonical_claim_ledger_v2.json", state.canon_doc)
        _resel_write_usage(state)
        write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2_rows, section_id="ibm_bullets")
        write_json(
            artifact_dir / "fact_check_result.json",
            {
                "passed": not [g for g in x2_rows if not g["pass"]],
                "failed_gates": [g["gate_id"] for g in x2_rows if not g["pass"]],
            },
        )
        l2_output["bullets"] = state.bullets
        l2_output["claim_ledger"] = state.claim_ledger
        l2_output["selected_fact_plan"] = (
            state.parsed.get("selected_fact_plan") or l2_output["selected_fact_plan"]
        )
        l2_output["gap_notes"] = state.parsed.get("gap_notes") or []
        l2_output["change_log"] = state.parsed.get("change_log") or []
        l2_output["self_check"] = state.parsed.get("self_check") or l2_output["self_check"]
        l2_output["text_claim_coverage"] = state.coverage

    _resel = run_bullet_judge_reselection(
        artifact_dir=artifact_dir,
        section_id="ibm_bullets",
        run_id=str(runtime_payload["run_id"]),
        required_bullet_ids=IBM_BULLET_IDS,
        parsed=parsed,
        bullets=bullets,
        claim_ledger=claim_ledger,
        parsed_for_x2=parsed_for_x2,
        x1d=x1d,
        x2=x2,
        usage_doc=usage_doc,
        canon_doc=canon_doc,
        allowed_fact_ids=allowed_fact_ids,
        judge_mode=judge_mode,
        entailment_corpus=build_slot_entailment_corpus(
            "ibm_bullets", runtime_payload.get("selected_fact_plan") or {}
        ),
        post_chain=_resel_post_chain,
        rebuild_state=_resel_rebuild_state,
        run_x2=_resel_run_x2,
        run_judges=_resel_run_judges,
        write_usage_ledger=_resel_write_usage,
        write_lane_artifacts=_resel_write_artifacts,
    )
    parsed = _resel.parsed
    bullets = _resel.bullets
    claim_ledger = _resel.claim_ledger
    parsed_for_x2 = _resel.parsed_for_x2
    x2 = _resel.x2
    x1d = _resel.x1d
    usage_doc = _resel.usage_doc
    canon_doc = _resel.canon_doc

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

    l6_temp = float(args.temperature) if args.provider == "external_claude" else IBM_TEMP_DEFAULT
    l6_max = IBM_MAX_OUTPUT_TOKENS if args.provider == "external_claude" else None
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
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    rl2 = {
        "provider_attempted": args.provider,
        "runtime_generation_status": runtime_generation_status,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "raw_model_output": raw_output,
        "bullets": bullets,
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
    merge_graph_evidence_reporting_into_dict(
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
    _wg.write_text(artifact_dir / "command_output.txt", output_text + "\n", encoding="utf-8")
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
    "IBM_MAX_OUTPUT_TOKENS",
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
    "retry_provider_for_parse",
    "run_ibm_bullets_execution",
    "sha16",
    "write_json",
]
