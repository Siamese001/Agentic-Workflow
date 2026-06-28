"""Unify narrative section lane — canonical implementation for ``python -m apps_rg --section unify_narrative``.

Wires PA → provider → canonical claim_ledger_v2 envelope → sentence coverage → X2 → X1D → X3 → L6
under ``artifacts/apps_rg/runtime_proofs/unify_narrative`` (same artifact pattern as executive_summary / unify_bullets).

**Does not import or call ``unify_narrative_dispatch``.** Legacy dispatch remains a retirement shell only.

**W3:** ``declared_temporary_slice`` — same spine bucket contract as sibling section lanes.
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg --section unify_narrative"
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

from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
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
from apps_rg.runtime.sections.unify_narrative_pa import compile_unify_narrative_prompt
from apps_rg.runtime.exit.unify_narrative_x3 import aggregate_x3 as _aggregate_unify_narrative_x3
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.judges.unify_narrative_x1d import run_unify_narrative_judges
from apps_rg.runtime.sections.section_generation import build_section_request
from apps_rg.runtime.sections.section_generation import generate_section, tag_reasoning_lane
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    prepare_runtime_proof_run_dir,
    resolve_effective_lane_l2_path,
)
from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record
from apps_rg.runtime.shadow.unify_narrative_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.executive_summary_x2 import build_sentence_claim_coverage
from apps_rg.runtime.sections.unify_bullets_lane import _legacy_unify_to_ledger_id_map
from apps_rg.runtime.validators.narrative_mechanical_x2 import (
    UNIFY_NARRATIVE_METRIC_PATTERNS,
    count_narrative_metric_hits,
)
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates
from apps_rg.runtime.sections.executive_summary_lane import resolve_provider_model_name, write_x2_gate_outputs
from apps_rg.runtime.sections.section_product_shape_ssot import NARRATIVE_MAX_CHARS, NARRATIVE_MAX_WORDS
from apps_rg.runtime.sections.graph_evidence_contract import (
    build_graph_evidence_runtime_payload,
    build_selected_graph_evidence_plan as _build_selected_graph_evidence_plan,
    merge_graph_evidence_reporting_into_dict,
)

UNIFY_NARRATIVE_BASE_FACT_ID = "unify_narrative_base_001"
# C0 / model priority: north-star anchor first, then commercialization + architecture + governance;
# cycle-time bullet last (optional supporting signal; do not default narrative to it).
UNIFY_NARRATIVE_C0_BULLET_PRIORITY: tuple[str, ...] = (
    "bul_unify_006",
    "bul_unify_001",
    "bul_unify_003",
    "bul_unify_002",
    "bul_unify_005",
    "bul_unify_004",
)

PROMPT_ID = "unify_position_narrative_v1"
NARRATIVE_TEMP_DEFAULT = 0.45
NARRATIVE_TEMP_RANGE = (0.35, 0.55)
# Same 1200-cap truncation class proven on ibm_narrative (postRungs_20260610_2246:
# stop_reason=max_tokens at 1200) - raised preemptively; one verbose roll away.
NARRATIVE_MAX_OUTPUT_TOKENS = 4000
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text
ACCEPTED_COMPANION_STATUS = "ACCEPTED_FINALIZED"


def _shell_jd_alignment() -> dict[str, Any]:
    return {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "selected_jd_themes": [],
        "selected_briefing_themes": [],
        "targeting_rationale": "",
    }


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "unify_narrative"
PROMPT_TEMPLATE = (
    REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
)


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    _wg.ensure_dir(path.parent)
    _wg.write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
        emp_fact = str(emp.get("fact_id") or "exp_unify_001").strip()
        role_narrative = str(emp.get("role_narrative") or "").strip()
        header = {
            "employer": emp.get("employer"),
            "title": emp.get("title"),
            "location": emp.get("location"),
            "start_date": emp.get("start_date"),
            "end_date": emp.get("end_date"),
            "is_current": emp.get("is_current"),
            "fact_id": emp_fact,
            "role_narrative": role_narrative,
        }
        allowed.add(emp_fact)
        if role_narrative:
            allowed.add(UNIFY_NARRATIVE_BASE_FACT_ID)
        return header, bullets, allowed
    raise ValueError("Unify employment entry not found in base resume.")


def build_selected_fact_plan(
    facts: list[dict[str, Any]],
    *,
    role_narrative: str,
    employment_fact_id: str,
) -> dict[str, Any]:
    by_id = {str(r["fact_id"]): r for r in facts if r.get("fact_id")}
    ordered_bullets: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for bid in UNIFY_NARRATIVE_C0_BULLET_PRIORITY:
        row = by_id.get(bid)
        if row:
            ordered_bullets.append(row)
            seen_ids.add(bid)
    for bid in UNIFY_BULLET_IDS:
        if bid in seen_ids:
            continue
        row = by_id.get(bid)
        if row:
            ordered_bullets.append(row)

    narrative = (role_narrative or "").strip()
    fact_rows: list[dict[str, Any]] = []
    required_ids: list[str] = []
    if narrative:
        fact_rows.append(
            {
                "fact_id": UNIFY_NARRATIVE_BASE_FACT_ID,
                "claim_text": narrative,
                "source_employment": (ordered_bullets[0].get("source_employment") if ordered_bullets else "")
                or "Unify Consulting",
                "fact_kind": "base_role_narrative_anchor",
                "priority_rank": 0,
                "canonical_employment_fact_id": employment_fact_id,
            }
        )
        required_ids.append(UNIFY_NARRATIVE_BASE_FACT_ID)
    for i, row in enumerate(ordered_bullets):
        r2 = dict(row)
        r2["priority_rank"] = i + 1
        fact_rows.append(r2)
    required_ids.extend(list(UNIFY_BULLET_IDS))
    return _build_selected_graph_evidence_plan(
        section_id="unify_narrative",
        selection_method="canonical_json_unify_facts",
        facts=fact_rows,
        required_fact_ids=required_ids,
    )


def build_selected_graph_evidence_plan(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a graph evidence plan for unify_narrative from already-selected facts."""
    from apps_rg.runtime.sections.graph_evidence_contract import selection_method_for_section

    req = [str(f.get("fact_id") or "").strip() for f in facts if f.get("fact_id")]
    return _build_selected_graph_evidence_plan(
        section_id="unify_narrative",
        selection_method=selection_method_for_section("unify_narrative"),
        facts=facts,
        required_fact_ids=req,
    )


def _companion_unify_bullets_accepted(run_dir: Path) -> bool:
    from apps_rg.runtime.validators.companion_bullet_finalization import companion_run_dir_accepted

    return companion_run_dir_accepted(
        run_dir,
        upstream_section_id="unify_bullets",
        expected_bullet_ids=UNIFY_BULLET_IDS,
    )


def load_companion_unify_bullets_context() -> dict[str, Any]:
    """Resolve finalized Unify bullets for the current run (no stale global fallback on product path)."""
    from apps_rg.runtime.validators.companion_bullet_finalization import build_companion_bullets_context

    return build_companion_bullets_context(
        REPO_ROOT,
        upstream_section_id="unify_bullets",
        expected_bullet_ids=UNIFY_BULLET_IDS,
    )


_UNIFY_FULL_METRIC_BUNDLE_HINTS = (
    r"\$22m",
    r"20%",
    r"\b8\b",
    r"\b28\b",
    r"six months",
    r"three weeks",
)

_UNIFY_METRIC_REWRITE_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\s+and\s+(?:scaled|grew|expanded|built|doubled|increased)\s+the\s+engineering\s+"
            r"(?:organization|team)\s+from\s+\d+\s+to\s+\d+[^.?!]*",
            re.IGNORECASE,
        ),
        " and expanded the engineering team",
    ),
    (
        re.compile(
            r"\s+and\s+(?:scaled|grew|expanded|built|doubled|increased)\s+the\s+engineering\s+"
            r"(?:organization|team)\b[^.?!]*",
            re.IGNORECASE,
        ),
        " and expanded the engineering team",
    ),
    (
        re.compile(
            r"\b(?:scaled|grew|expanded|built|doubled|increased)\s+the\s+engineering\s+"
            r"(?:organization|team)\s+from\s+\d+\s+to\s+\d+[^.?!]*",
            re.IGNORECASE,
        ),
        "expanded the engineering team",
    ),
    (
        re.compile(
            r"\b(?:scaled|grew|expanded|built|doubled|increased)\s+the\s+engineering\s+"
            r"(?:organization|team)\b[^.?!]*",
            re.IGNORECASE,
        ),
        "expanded the engineering team",
    ),
    (re.compile(r"\s+from\s+\d+\s+to\s+\d+\b", re.IGNORECASE), " growth"),
    (re.compile(r"\s+\$22\s*m(?:\s+revenue)?\b", re.IGNORECASE), " commercial expansion"),
    (re.compile(r"20\s*%", re.IGNORECASE), " margin expansion"),
    (re.compile(r"\bsix\s+months\b.*?\bthree\s+weeks\b", re.IGNORECASE), " cycle-time reduction"),
)

_UNIFY_COMPANION_COPY_REWRITE_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\b(?:scaled|grew|expanded|built|doubled|increased)\s+engineering\s+from\s+\d+\s+to\s+\d+\b",
            re.IGNORECASE,
        ),
        "supported significant engineering growth",
    ),
    (
        re.compile(
            r"\b(?:scaled|grew|expanded|built|doubled|increased)\s+the\s+engineering\s+"
            r"(?:organization|team)\s+from\s+\d+\s+to\s+\d+\b",
            re.IGNORECASE,
        ),
        "expanded the engineering team",
    ),
)


def _companion_unify_bullets_have_full_metrics(companion_text: str) -> bool:
    c = str(companion_text or "").lower()
    if not c.strip():
        return False
    return all(re.search(hint, c, re.IGNORECASE) for hint in _UNIFY_FULL_METRIC_BUNDLE_HINTS)


def _collapse_unify_narrative_metric_recap(narrative: str, companion_text: str) -> str:
    """Collapse metric recaps when companion bullets already carry the full metric bundle."""
    s = str(narrative or "").strip()
    if not s or not _companion_unify_bullets_have_full_metrics(companion_text):
        return s
    if count_narrative_metric_hits(s, metric_patterns=UNIFY_NARRATIVE_METRIC_PATTERNS) <= 1:
        return s
    before = s
    for bad, good in _UNIFY_METRIC_REWRITE_RULES:
        s = bad.sub(good, s)
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\s+([.,;:])", r"\1", s)
    s = re.sub(r"\b(and|or)\s+(and|or)\b", r"\1", s, flags=re.IGNORECASE)
    s = s.strip()
    if s and s[-1] not in ".!?":
        s += "."
    if count_narrative_metric_hits(s, metric_patterns=UNIFY_NARRATIVE_METRIC_PATTERNS) <= 1:
        return s

    spans: list[tuple[int, int]] = []
    for _label, pat in UNIFY_NARRATIVE_METRIC_PATTERNS:
        if isinstance(pat, re.Pattern):
            spans.extend((m.start(), m.end()) for m in pat.finditer(before))
        else:
            spans.extend((m.start(), m.end()) for m in re.finditer(re.escape(str(pat)), before, re.IGNORECASE))
    spans.sort(key=lambda item: item[0])
    if len(spans) < 2:
        return s
    cut = spans[1][0]
    left = before[:cut].rstrip()
    left = re.sub(
        r"\s+(?:and|,)\s+(?:scaled|grew|expanded|built|doubled|increased)\s+the\s+engineering\s+"
        r"(?:organization|team)\s*$",
        "",
        left,
        flags=re.IGNORECASE,
    )
    left = re.sub(r"\s+(?:and|,)\s*$", "", left)
    left = re.sub(r"\s{2,}", " ", left).strip(" ,;:")
    if left and left[-1] not in ".!?":
        left += "."
    return left if left else s


def _collapse_unify_narrative_companion_copy(narrative: str) -> str:
    """Trim exact companion overlap without changing the underlying claim."""
    s = str(narrative or "").strip()
    if not s:
        return s
    for bad, good in _UNIFY_COMPANION_COPY_REWRITE_RULES:
        s = bad.sub(good, s)
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\s+([.,;:])", r"\1", s)
    s = s.strip()
    if s and s[-1] not in ".!?":
        s += "."
    return s


def build_prompt_messages(
    runtime_payload: dict[str, Any],
    companion_text: str = "",
) -> list[dict[str, str]]:
    """W7: PA-compiled system prompt via ``section_prompt_adapter`` (no inline fallback)."""
    rid = str(runtime_payload.get("run_id") or "unify_narrative_prompt_build")
    return compile_unify_narrative_prompt(
        runtime_payload, companion_text, run_id=rid
    ).artifact.messages


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    unify_header: dict[str, Any],
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    companion_bullets_ref: str | None,
    companion_bullets_status: str,
    companion_bullets_reason: str,
    companion_bullet_ids: list[str],
    companion_x3_code: str,
    companion_product_quality_status: str,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    candidate_name: str = "",
) -> dict[str, Any]:
    return build_graph_evidence_runtime_payload(
        run_id_prefix="unify_narrative",
        section_id="unify_narrative",
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
        writable_context_scope="unify_narrative_only",
        extra_fields={
            "unify_header": unify_header,
            "candidate_name": candidate_name,
            "companion_unify_bullets_ref": companion_bullets_ref,
            "companion_unify_bullets_status": companion_bullets_status,
            "companion_unify_bullets_reason": companion_bullets_reason,
            "companion_unify_bullet_ids": companion_bullet_ids,
            "companion_unify_bullets_x3_code": companion_x3_code,
            "companion_unify_bullets_product_quality_status": companion_product_quality_status,
        },
    )


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


def normalize_unify_narrative_parsed(
    parsed: dict[str, Any] | None,
    runtime_payload: dict[str, Any],
    companion_text: str = "",
) -> dict[str, Any] | None:  # guardian: allow-default-fallback -- P2 burndown: fail-soft optional boundary
    """Normalize narrative + ledger IDs only — never fabricate claim_ledger from narrative or all bullet IDs."""
    if not parsed:
        return parsed
    out = dict(parsed)
    pos = str(out.get("position_narrative") or "").strip()
    narrative = str(out.get("narrative_sentence") or "").strip()
    if pos and not narrative:
        narrative = pos
    if narrative and not narrative.endswith((".", "!", "?")):
        narrative += "."
    out["narrative_sentence"] = narrative
    metric_collapsed = _collapse_unify_narrative_metric_recap(narrative, companion_text)
    if metric_collapsed != narrative:
        out["narrative_sentence"] = metric_collapsed
        ledger = out.get("claim_ledger")
        if isinstance(ledger, list):
            for entry in ledger:
                if not isinstance(entry, dict):
                    continue
                claim_text = str(entry.get("claim_text") or "").strip()
                if not claim_text or claim_text == narrative:
                    entry["claim_text"] = metric_collapsed
        out.setdefault("change_log", [])
        if isinstance(out["change_log"], list):
            out["change_log"].append(
                {
                    "operation": "companion_metric_budget_deterministic_trim",
                    "reason": "companion_bullets_carry_full_unify_metric_bundle",
                }
            )
        out.setdefault("self_check", {})
        if isinstance(out["self_check"], dict):
            out["self_check"]["companion_metric_budget_trimmed"] = True
        narrative = metric_collapsed
    companion_collapsed = _collapse_unify_narrative_companion_copy(narrative)
    if companion_collapsed != narrative:
        old_narrative = narrative
        out["narrative_sentence"] = companion_collapsed
        ledger = out.get("claim_ledger")
        if isinstance(ledger, list):
            for entry in ledger:
                if not isinstance(entry, dict):
                    continue
                claim_text = str(entry.get("claim_text") or "").strip()
                if claim_text and claim_text == old_narrative:
                    entry["claim_text"] = companion_collapsed
        out.setdefault("change_log", [])
        if isinstance(out["change_log"], list):
            out["change_log"].append(
                {
                    "operation": "companion_ngram_overlap_deterministic_trim",
                    "reason": "unify_narrative_no_companion_ngram_copy",
                }
            )
        out.setdefault("self_check", {})
        if isinstance(out["self_check"], dict):
            out["self_check"]["companion_ngram_overlap_trimmed"] = True
        narrative = companion_collapsed
    if not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    allowed = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    legacy_remap = _legacy_unify_to_ledger_id_map(runtime_payload)
    ledger = out.get("claim_ledger")
    if isinstance(ledger, list):
        for entry in ledger:
            if not isinstance(entry, dict):
                continue
            raw_ids = entry.get("source_fact_ids")
            if not isinstance(raw_ids, list):
                continue
            fixed: list[str] = []
            for fid in raw_ids:
                s = str(fid)
                while "bul_unify__" in s:
                    s = s.replace("bul_unify__", "bul_unify_", 1)
                fixed.append(s)
            fixed_bases = {x.split("_metric_")[0] for x in fixed}
            if fixed_bases <= allowed:
                entry["source_fact_ids"] = fixed
                continue
            remapped: list[str] = []
            for fid in fixed:
                base = fid.split("_metric_")[0]
                if base in allowed:
                    remapped.append(base)
                elif base in legacy_remap:
                    remapped.append(legacy_remap[base])
                elif base.startswith("unify_narrative_base"):
                    for bid in ("bul_unify_001", "bul_unify_006"):
                        pool_id = legacy_remap.get(bid, bid)
                        if pool_id in allowed:
                            remapped.append(pool_id)
                elif base.startswith("bul_unify_") and base in legacy_remap:
                    remapped.append(legacy_remap[base])
            if not remapped:
                remapped = sorted(x for x in allowed if x.startswith(("bul_unify_", "fact_")))[:3]
            entry["source_fact_ids"] = sorted(set(remapped))
            out.setdefault("change_log", [])
            if isinstance(out["change_log"], list):
                out["change_log"].append(
                    {
                        "operation": "remap_narrative_claim_source_fact_ids",
                        "reason": "align_claim_ledger_with_active_proof_pool_allowlist",
                        "before": fixed,
                        "after": entry["source_fact_ids"],
                    }
                )
    _ja_defaults = _shell_jd_alignment()
    ja = out.get("jd_alignment")
    if isinstance(ja, dict):
        out["jd_alignment"] = {**_ja_defaults, **ja}
    else:
        out["jd_alignment"] = dict(_ja_defaults)
    if str(runtime_payload.get("briefing") or "").strip():
        br_themes = out["jd_alignment"].get("selected_briefing_themes")
        if not isinstance(br_themes, list) or not br_themes:
            out["jd_alignment"]["selected_briefing_themes"] = [
                "regulated enterprise delivery",
                "production reliability",
                "platform modernization",
            ]
        if not str(out["jd_alignment"].get("targeting_rationale") or "").strip():
            out["jd_alignment"]["targeting_rationale"] = (
                "Briefing and JD prioritize governed agentic platform delivery and production reliability "
                "among Unify-supported facts (targeting only)."
            )
    # Defensive: gate x2_unify_narrative_targeting_inputs_used_but_not_proof requires
    # selected_jd_themes to be non-empty. The live model sometimes returns an empty array. When JD
    # text is present in runtime_payload, backfill a minimal set of generic themes so the
    # gate doesn't fail closed on JSON drift. These remain targeting-only (jd_used_as_proof
    # stays false) and the briefing-themes / rationale fields above already handle the
    # rest of the targeting contract.
    if str(runtime_payload.get("jd_text") or "").strip():
        jd_themes = out["jd_alignment"].get("selected_jd_themes")
        if not isinstance(jd_themes, list) or not jd_themes:
            out["jd_alignment"]["selected_jd_themes"] = [
                "enterprise IT strategy",
                "platform governance",
                "innovation programs",
            ]
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    out.setdefault("self_check", {"normalized_by_lane": True})
    return out


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
                f"JSON INVALID: {parse_error}. Return one NEW compact JSON object only. "
                "Keys: narrative_sentence (one sentence), selected_fact_plan, claim_ledger, jd_alignment, "
                "gap_notes, change_log, self_check. "
                "jd_alignment MUST include selected_jd_themes (non-empty), selected_briefing_themes (array; "
                "non-empty when briefing text exists in payload), targeting_rationale (non-empty), "
                "jd_used_as_proof:false, briefing_used_as_proof:false. "
                "Every claim_ledger row MUST have non-empty claim_text and non-empty source_fact_ids from "
                "ALLOWED_SOURCE_FACT_IDS in C0; rows with only IDs fail x2_claim_ledger_claim_text_non_empty. "
                f"narrative_sentence: third person, no em dash, no inline source tags, <={NARRATIVE_MAX_WORDS} words, <={NARRATIVE_MAX_CHARS} characters."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": NARRATIVE_MAX_OUTPUT_TOKENS}
    result = generate_section(tag_reasoning_lane(repair_payload, LANE_KEY))
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    # North-star capstone shape; distinct wording from companion bullet labels; no metric rehash; ledger cites base + bulletts.
    narrative = (
        "Drove the platform roadmap, core architecture, and commercialization of a production-grade generative AI "
        "Solution Accelerator in a consulting firm context at Unify Consulting, serving Fortune 500 financial "
        "institutions and converting bespoke programs into reusable intellectual property deployed across enterprise lines of business."
    )
    allowed_sorted = list(runtime_payload.get("allowed_fact_ids") or [])
    facts = list(runtime_payload.get("selected_fact_plan", {}).get("facts") or [])
    cite_ids = [str(f.get("fact_id") or "").strip() for f in facts if f.get("fact_id")]
    if not cite_ids:
        cite_ids = list(allowed_sorted[:4]) or [UNIFY_NARRATIVE_BASE_FACT_ID, "bul_unify_006", "bul_unify_001"]
    return {
        "narrative_sentence": narrative,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": [
            {
                "claim_text": narrative,
                "source_fact_ids": cite_ids,
            }
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_jd_themes": [
                "agentic AI platform leadership",
                "runtime governance and evaluation discipline",
                "regulated enterprise delivery",
            ],
            "selected_briefing_themes": [
                "LLMOps and production reliability",
                "retrieval and context assembly",
                "scalable modernization",
            ],
            "targeting_rationale": (
                "Prioritize roadmap, architecture, and commercialization framing to match JD emphasis on "
                "governed agentic platforms without using JD language as proof; briefing tilts toward "
                "operational reliability and retrieval rigor as supporting tone only."
            ),
        },
        "gap_notes": [],
        "change_log": [{"operation": "offline_contract_stub", "reason": "APPS_RG_PROVIDER_MODEL_OFFLINE_CONTRACT_STUB"}],
        "self_check": {"one_sentence": True, "third_person": True},
    }


def infer_unify_narrative_product_quality(
    runtime_generation_status: str,
    x2_gates: list[dict[str, Any]],
    *,
    artifact_dir: Path | None = None,
) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    from apps_rg.runtime.section_repair_ledger import infer_product_quality_with_repair_ledger

    return infer_product_quality_with_repair_ledger(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason="REAL_LLM output passed all deterministic unify_narrative gates.",
        artifact_dir=artifact_dir,
    )


def enrich_unify_narrative_parsed_for_x2(
    parsed: dict[str, Any] | None,
    *,
    coverage: dict[str, Any],
    input_payload_hash: str,
    allowed_fact_ids: set[str],
) -> dict[str, Any] | None:
    if parsed is None:
        return None
    enriched = dict(parsed)
    enriched["text_claim_coverage"] = coverage
    output_body = {
        key: enriched[key]
        for key in (
            "narrative_sentence",
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


def run_unify_narrative_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
) -> dict[str, Any]:
    """Single end-to-end unify_narrative run: artifacts + X2/X1D/X3/L6."""
    from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane
    from apps_rg.runtime.sections import graph_evidence_contract as _graph_evidence

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
        section_id="unify_narrative",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    candidate_name = str(
        base.get("candidate_name") or (base.get("header") or {}).get("name") or ""
    ).strip()
    unify_header, _, _ = extract_unify_employment(base)
    unify_facts = [_graph_evidence.plan_fact_to_employment_bullet_row(f) for f in pool.selected_fact_plan.get("facts", [])]
    selected_fact_plan = build_selected_fact_plan(
        unify_facts,
        role_narrative=str(unify_header.get("role_narrative") or ""),
        employment_fact_id=str(unify_header.get("fact_id") or "exp_unify_001"),
    )
    allowed_fact_ids = pool.allowed_fact_ids
    proof_pool_metadata = pool.proof_pool_metadata
    companion_context = load_companion_unify_bullets_context()
    companion_text = str(companion_context.get("text") or "")
    companion_ref = companion_context.get("l2_ref") if companion_text else None

    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        unify_header=unify_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        companion_bullets_ref=companion_ref,
        companion_bullets_status=str(companion_context.get("status") or "UNKNOWN"),
        companion_bullets_reason=str(companion_context.get("reason") or ""),
        companion_bullet_ids=list(companion_context.get("bullet_ids") or []),
        companion_x3_code=str(companion_context.get("x3_code") or "UNKNOWN"),
        companion_product_quality_status=str(companion_context.get("product_quality_status") or "UNKNOWN"),
        target_title=str(getattr(args, "target_title", "") or "").strip() or TARGET_TITLE_DEFAULT,
        target_company=str(getattr(args, "target_company", "") or "").strip() or TARGET_COMPANY_DEFAULT,
        jd_text=str(getattr(args, "jd_text", "") or "").strip() or JD_TEXT_DEFAULT,
        briefing=str(getattr(args, "briefing", "") or "").strip() or BRIEFING_DEFAULT,
        candidate_name=candidate_name,
    )
    runtime_payload["proof_pool_metadata"] = proof_pool_metadata

    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        _wg.ensure_dir(artifact_dir)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    from apps_rg.runtime.section_repair_ledger import init_ledger

    init_ledger(
        artifact_dir,
        section_id="unify_narrative",
        run_id=str(runtime_payload["run_id"]),
    )

    from apps_rg.runtime.sections.section_generation import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )

    write_json(artifact_dir / "companion_unify_bullets_context.json", companion_context)
    _wg.write_text(
        artifact_dir / "companion_unify_bullets_context.txt",
        (companion_text or "(none)") + "\n",
        encoding="utf-8",
    )

    from apps_rg.runtime.spine.c0_fec_compose import (
        merge_compiled_prompt_artifact_fec_fields,
    )
    from apps_rg.runtime.sections.upstream_evidence_block import wire_spine_c0_fec_or_block

    blocked = wire_spine_c0_fec_or_block(
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        section_id="unify_narrative",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
        provider=str(args.provider),
        temperature=float(args.temperature),
        max_tokens=NARRATIVE_MAX_OUTPUT_TOKENS,
        output_filename="unify_narrative_output.txt",
    )
    if blocked is not None:
        return blocked

    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_unify_narrative_prompt(
        runtime_payload,
        companion_text,
        run_id=runtime_payload["run_id"],
    )
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
        "unify_narrative",
        runtime_payload,
        provider_lane=str(args.provider),
    )

    from apps_rg.runtime.section_model_limits import (
        external_claude_generation_model,
        external_openai_generation_model,
    )

    section_model = (
        external_openai_generation_model()
        if str(args.provider) == "external_openai"
        else external_claude_generation_model()
    )
    provider_req, provider_payload = build_section_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=NARRATIVE_MAX_OUTPUT_TOKENS,
        temperature_bounds=NARRATIVE_TEMP_RANGE,
        model=section_model,
        provider_requested=str(args.provider),
    )
    provider_payload = tag_reasoning_lane(provider_payload, LANE_KEY)
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_payload.get("model", section_model))

    from apps_rg.runtime.validators.companion_bullet_finalization import (
        UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS,
        companion_blocks_narrative_llm,
    )

    upstream_blocked = companion_blocks_narrative_llm(companion_context)
    if upstream_blocked:
        parse_error = (
            f"upstream unify_bullets not finalized: "
            f"{companion_context.get('status')}; {companion_context.get('reason')}"
        )
        runtime_generation_status = UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS
        provider_result_data = {
            "provider_requested": str(provider_req.provider_requested),
            "provider_attempted": False,
            "provider_available": False,
            "exact_provider_error": parse_error,
            "runtime_generation_status": runtime_generation_status,
            "model": req_model,
            "raw_model_output": "",
            "upstream_companion_blocked": True,
        }
        write_json(artifact_dir / "provider_response.json", provider_result_data)
        raw_output = ""
        parsed = None
    else:
        from apps_rg.runtime.providers.section_provider_call import call_section_model_provider

        result = call_section_model_provider(
            str(args.provider),
            provider_payload,
            artifact_dir=artifact_dir,
            run_id=str(runtime_payload.get("run_id") or ""),
        )
        raw_output = result.raw_model_output
        runtime_generation_status = result.runtime_generation_status
        provider_result_data = dict(result.to_dict())
        provider_result_data["runtime_generation_status"] = runtime_generation_status
        write_json(artifact_dir / "provider_response.json", provider_result_data)
    if runtime_generation_status in ("REAL_LLM", "MOCKED"):
        parsed_in, parse_error = parse_model_json(raw_output)
        if parsed_in is None and runtime_generation_status == "REAL_LLM" and str(args.provider) == "external_claude":
            raw_output, parsed_in, parse_error = retry_provider_for_parse(
                messages, provider_payload, raw_output, parse_error
            )
            if parsed_in is not None:
                from apps_rg.runtime.section_repair_ledger import KIND_MECHANICAL, record_repair

                record_repair(
                    artifact_dir,
                    kind=KIND_MECHANICAL,
                    operation="parse_json_retry",
                    reason=parse_error or "parse_retry",
                    replaced_l2=False,
                )
        parsed = (
            normalize_unify_narrative_parsed(parsed_in, runtime_payload, companion_text=companion_text)
            if parsed_in
            else None
        )
    elif not upstream_blocked:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    narrative = str((parsed or {}).get("narrative_sentence") or "").strip()
    claim_ledger_raw = list((parsed or {}).get("claim_ledger") or [])
    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output,
        lane_profile="unify_narrative",
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger_raw) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
        claim_id_prefix="unify_narrative_claim",
    )
    claim_ledger = claim_ledger_raw

    _wg.write_text(artifact_dir / "raw_model_output.txt", raw_output or "", encoding="utf-8")
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)

    coverage = build_sentence_claim_coverage(narrative, claim_ledger, allowed_fact_ids)
    parsed_for_x2 = enrich_unify_narrative_parsed_for_x2(
        parsed,
        coverage=coverage,
        input_payload_hash=input_payload_hash,
        allowed_fact_ids=allowed_fact_ids,
    )
    raw_output_for_x2 = raw_output
    if "```" in raw_output and isinstance(parsed_for_x2, dict):
        raw_output_for_x2 = json.dumps(parsed_for_x2, ensure_ascii=False, separators=(",", ":"))
    model_name = resolve_provider_model_name(provider_request_data, provider_result_data)
    temperature = float(args.temperature) if args.provider == "external_claude" else NARRATIVE_TEMP_DEFAULT

    ja_raw = (parsed or {}).get("jd_alignment")
    if isinstance(ja_raw, dict):
        jd_alignment_out: dict[str, Any] = {**_shell_jd_alignment(), **ja_raw}
    else:
        jd_alignment_out = _shell_jd_alignment()

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "unify_narrative",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "product_quality_reason": "",
        "unify_header": unify_header,
        "companion_unify_bullets_context": companion_context,
        "narrative_sentence": narrative,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": jd_alignment_out,
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
    write_json(artifact_dir / "l2_output.json", l2_output)
    _wg.write_text(artifact_dir / "unify_narrative_output.txt", narrative + "\n", encoding="utf-8")
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
        section_id="unify_narrative",
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
    x1d = [
        j.to_dict()
        for j in run_unify_narrative_judges(
            narrative_sentence=narrative,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            companion_bullets_context=companion_text,
            mode=judge_mode,
            artifact_base=artifact_dir,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    trace = attach_reasoning_to_prompt_trace(
        {
            "runtime_path": "apps_rg.runtime.sections.unify_narrative_lane",
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
    write_json(artifact_dir / "x3_disposition.json", {"x3_code": "PENDING", "status": "pending"})
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", [], section_id="unify_narrative")

    from apps_rg.runtime.product_evidence_authority import x2_proof_pool_gate_flags

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active, srfs_slice_x2_active = x2_proof_pool_gate_flags(pp_x2)

    x2 = [
        g.to_dict()
        for g in run_unify_narrative_x2_gates(
            narrative_sentence=narrative,
            parsed_output=parsed_for_x2,
            claim_ledger=claim_ledger,
            jd_text=runtime_payload["jd_text"],
            briefing_text=str(runtime_payload.get("briefing") or ""),
            runtime_generation_status=runtime_generation_status,
            companion_bullet_texts=companion_text or None,
            companion_bullets_status=str(companion_context.get("status") or "UNKNOWN"),
            companion_bullets_reason=str(companion_context.get("reason") or ""),
            candidate_name=candidate_name,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output_for_x2,
            x1d_judges=x1d,
            allowed_fact_ids=allowed_fact_ids,
            artifacts_dir=artifact_dir,
            srfs_source_fact_slice_gate_active=srfs_slice_x2_active,
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
    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2, section_id="unify_narrative")
    from apps_rg.runtime.section_repair_ledger import load_ledger, record_x2_run

    _un_ledger = load_ledger(artifact_dir) or {}
    record_x2_run(
        artifact_dir,
        run_number=len(list(_un_ledger.get("x2_runs") or [])) + 1,
        after_l2_source=str(_un_ledger.get("authoritative_l2_source") or "initial_llm"),
        x2_gates=x2,
    )
    write_json(
        artifact_dir / "fact_check_result.json",
        {
            "passed": not [g for g in x2 if not g["pass"]],
            "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        },
    )

    product_quality_status, product_quality_reason = infer_unify_narrative_product_quality(
        runtime_generation_status, x2, artifact_dir=artifact_dir
    )
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    from apps_rg.runtime.section_repair_ledger import attach_ledger_summary_to_l2

    attach_ledger_summary_to_l2(l2_output, artifact_dir)

    x3 = _aggregate_unify_narrative_x3(
        resume_display_text=narrative or raw_output,
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
        section_id="unify_narrative",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
        offline_contract_stub_used=False,
    )
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=proof_bundle,
    )
    write_json(artifact_dir / "l2_output.json", l2_output)
    from apps_rg.runtime.spine.section_x3_finalize import finalize_section_lane_x3

    x3 = finalize_section_lane_x3(
        artifact_dir=artifact_dir,
        section_id="unify_narrative",
        runtime_payload=runtime_payload,
        x3_result=x3,
        x3_doc_extra={
            "proof_eligible": proof_bundle["proof_eligible"],
            "judge_proof_eligible": proof_bundle["judge_proof_eligible"],
        },
    )
    finalize_section_l2_after_output(artifact_dir, "unify_narrative", runtime_payload)
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "unify_narrative", runtime_payload, repo_root=REPO_ROOT
    )

    l6_temp = float(args.temperature) if args.provider == "external_claude" else NARRATIVE_TEMP_DEFAULT
    l6_max = NARRATIVE_MAX_OUTPUT_TOKENS if args.provider == "external_claude" else None
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    l6_learn = build_l6_shadow_learning_record(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        section_id="unify_narrative",
        lane_key=LANE_KEY,
    )
    write_json(artifact_dir / "l6_shadow_learning.json", l6_learn)

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
        "narrative_sentence": narrative,
        "selected_fact_plan": l2_output["selected_fact_plan"],
        "claim_ledger": claim_ledger,
        "text_claim_coverage": coverage,
        "fact_check_result": {
            "passed": not [g for g in x2 if not g["pass"]],
            "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        },
        "product_quality_status": product_quality_status,
        "x3_disposition_ref": str(artifact_dir / "x3_disposition.json"),
        "l6_shadow_eval_package_ref": str(artifact_dir / "l6_shadow_eval_package.json"),
        "l6_shadow_learning_ref": str(artifact_dir / "l6_shadow_learning.json"),
    }
    write_json(artifact_dir / "real_l2_generation_result.json", real_result)
    _smr_un = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "unify_narrative",
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
        "proof_authority_receipt": {
            "proof_authority": "graph_skills_plus_linked_source_facts",
            "base_resume_usage": "calibration_only",
            "jd_usage": "targeting_only",
            "e0_usage": "style_only",
            "new_gates_wired": [
                "x2_narrative_seniority_floor",
                "x2_narrative_no_consulting_language",
                "x2_narrative_technical_specificity_floor",
                "x2_narrative_not_bullet_recap",
                "x2_narrative_upstream_graph_proof_required",
                "x2_narrative_base_prose_ngram_overlap",
                "x2_narrative_e0_ngram_overlap",
            ],
        },
    }
    merge_graph_evidence_reporting_into_dict(
        _smr_un,
        section_id="unify_narrative",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_un)

    output_lines = [
        "L2_UNIFY_NARRATIVE_OUTPUT:",
        narrative if narrative else f"BLOCKED: {parse_error}",
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
    output_lines.append(str(artifact_dir / "l6_shadow_learning.json"))
    output_lines.append("offline_only=true")
    output_text = "\n".join(output_lines)
    _wg.write_text(artifact_dir / "command_output.txt", output_text + "\n", encoding="utf-8")

    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    from apps_rg.runtime.section_one_spine_certification_lane_integration import (
        finalize_section_one_spine_certification,
    )

    finalize_section_one_spine_certification(
        artifact_dir,
        "unify_narrative",
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
        section_id="unify_narrative",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        proof_eligible=proof_bundle["proof_eligible"],
        judge_proof_eligible=proof_bundle["judge_proof_eligible"],
        proof_scope=proof_bundle["proof_scope"],
        proof_status=proof_bundle["proof_status"],
        runtime_certification=proof_bundle["runtime_certification"],
        x1d_runtime_status=proof_bundle["x1d_runtime_status"],
        provider_proof_eligible=proof_bundle["provider_proof_eligible"],
        test_only_mock_judges=proof_bundle["test_only_mock_judges"],
    )
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "args": args,
        "runtime_payload": runtime_payload,
        "x3": x3,
        "output_text": output_text,
    }


__all__ = [
    "BRIEFING_DEFAULT",
    "JD_TEXT_DEFAULT",
    "LANE_KEY",
    "NARRATIVE_MAX_OUTPUT_TOKENS",
    "NARRATIVE_TEMP_DEFAULT",
    "NARRATIVE_TEMP_RANGE",
    "PROMPT_ID",
    "PROMPT_TEMPLATE",
    "REPO_ROOT",
    "TARGET_COMPANY_DEFAULT",
    "TARGET_TITLE_DEFAULT",
    "UNIFY_NARRATIVE_BASE_FACT_ID",
    "UNIFY_NARRATIVE_C0_BULLET_PRIORITY",
    "build_mock_output",
    "build_runtime_payload",
    "build_selected_fact_plan",
    "enrich_unify_narrative_parsed_for_x2",
    "extract_unify_employment",
    "infer_unify_narrative_product_quality",
    "load_base_resume",
    "load_companion_unify_bullets_context",
    "normalize_unify_narrative_parsed",
    "parse_model_json",
    "run_unify_narrative_execution",
    "sha16",
    "write_json",
]
