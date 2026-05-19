"""App-local competencies execution seam (compile → provider → X2 → X1D → X3 → L6).

**Primary runtime entry:** ``python -m apps_rg --section competencies`` via
``apps_rg.runtime.sections.competencies_lane`` (canonical selected-section path).

**Deprecated:** ``python -m apps_rg.runtime.dispatch.competencies_dispatch`` — exits with guidance;
do not use for runtime proof.

Shared helpers (``compile_competencies_prompt``, ``run_competencies_execution``) remain here for PA and
orchestration; they are not a standalone product entrypoint.
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
import re
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from apps_rg.runtime.competencies_proof_boundary import merge_jd_alignment
from apps_rg.runtime.dispatch.competencies_pa import compile_competencies_prompt
from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    classify_ledger_parse_state,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.dispatch.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.exit.competencies_x3 import X3Disposition, aggregate_x3
from apps_rg.runtime.judges.competencies_x1d import run_competencies_judges
from apps_rg.runtime.providers.competencies_live_provider_gate import (
    REASON_PROVIDER_UNAVAILABLE,
    STATUS_BLOCKED_LIVE_PROVIDER,
    competencies_vllm_preflight_disabled,
    competencies_vllm_chat_timeout_s,
    competencies_vllm_preflight_timeout_s,
    live_provider_gate_audit_payload_failure,
)
from apps_rg.runtime.providers.qwen_vllm_provider import DEFAULT_QWEN_MODEL, build_qwen_request
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.qwen_offline_contract_stub import (
    OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
    effective_offline_contract_stub_enabled,
    synthetic_qwen_provider_result,
)
from apps_rg.runtime.shadow.competencies_l6 import build_l6_shadow_package
from apps_rg.runtime.validators.executive_summary_x2 import build_sentence_claim_coverage
from apps_rg.runtime.validators.competencies_x2 import (
    find_bullet_restatement_term,
    run_competencies_x2_gates,
    term_primary_support_overlap,
)
from apps_rg.runtime.section_proof.section_input_usage_ledger import build_section_input_usage_ledger_v1
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    MOCK_JUDGES_REJECT_EXIT_CODE,
    allow_non_allow_exit_zero_ok,
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    emit_mock_judges_blocked_stderr,
    infer_product_quality_blocked_or_mock,
    mock_judges_blocked_before_run,
)
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    prepare_runtime_proof_run_dir,
    resolve_effective_lane_l2_path,
)
from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict

PROMPT_ID = "competencies_dispatch_v1"
COMPETENCIES_TEMP_DEFAULT = 0.38
TARGET_TITLE_DEFAULT = "SVP Engineering, Agentic AI Platforms"
TARGET_COMPANY_DEFAULT = "Synthetic Enterprise Corp."
JD_TEXT_DEFAULT = resolve_jd_for_lanes().description
BRIEFING_DEFAULT = resolve_briefing_for_lanes(briefing_artifact_ref=None).text
COMPETENCIES_QWEN_MAX_TOKENS = 2800

COMPANION_LANES: tuple[tuple[str, str], ...] = (
    ("executive_summary", "executive_summary"),
    ("unify_narrative", "unify_narrative"),
    ("unify_bullets", "unify_bullets"),
    ("ibm_bullets", "ibm_bullets"),
    ("ibm_narrative", "ibm_narrative"),
)


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()
LANE_KEY = "competencies"


def _artifact_repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def term_phrase(raw: Any) -> str:
    """Normalize a competency term to display text (string or structured object)."""
    if isinstance(raw, dict):
        return str(raw.get("text") or raw.get("phrase") or raw.get("term") or "").strip()
    return str(raw).strip()


def canonicalize_competency_terms_for_proof(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str] | None = None,
) -> None:
    """Persist canonical structured term rows: ``text``, ``source_fact_id``, ``source_fact_ids``."""
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return
    for cat in comps:
        if not isinstance(cat, dict):
            continue
        ids_norm = [
            _fix_fact_id_typos(str(x), allowed_fact_ids).split("_metric_")[0]
            for x in (cat.get("source_fact_ids") or [])
            if x
        ]
        terms_raw = cat.get("terms") if isinstance(cat.get("terms"), list) else []
        new_terms: list[dict[str, Any]] = []
        for t in terms_raw:
            if isinstance(t, dict):
                txt = term_phrase(t)
                sid_raw = t.get("source_fact_id")
                sid = (
                    _fix_fact_id_typos(str(sid_raw), allowed_fact_ids).split("_metric_")[0]
                    if sid_raw is not None and str(sid_raw).strip()
                    else ""
                )
                if not sid and ids_norm:
                    sid = ids_norm[0]
                sup = t.get("source_fact_ids")
                if isinstance(sup, list) and sup:
                    sf_ids = sorted(
                        {
                            _fix_fact_id_typos(str(x), allowed_fact_ids).split("_metric_")[0]
                            for x in sup
                        }
                    )
                else:
                    sf_ids = list(ids_norm)
                if sid and sid not in sf_ids:
                    sf_ids = [sid] + [x for x in sf_ids if x != sid]
                jd_sig = t.get("jd_signal_ids")
                row: dict[str, Any] = {"text": txt, "source_fact_id": sid, "source_fact_ids": sf_ids}
                if isinstance(jd_sig, list):
                    row["jd_signal_ids"] = jd_sig
                new_terms.append(row)
            elif isinstance(t, str) and t.strip():
                sid0 = ids_norm[0] if ids_norm else ""
                sf_ids = list(ids_norm)
                new_terms.append({"text": t.strip(), "source_fact_id": sid0, "source_fact_ids": sf_ids})
        cat["terms"] = new_terms


def _terms_list_has_dict(terms_raw: Any) -> bool:
    return isinstance(terms_raw, list) and any(isinstance(t, dict) for t in terms_raw)


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_base_resume() -> tuple[dict[str, Any], Path, str]:
    return load_lane_base_resume_json(repo_root=REPO_ROOT)


def collect_employment_bullets(base_resume: dict[str, Any]) -> tuple[list[dict[str, Any]], set[str], list[str]]:
    facts_obj = base_resume.get("facts", base_resume)
    rows: list[dict[str, Any]] = []
    allowed: set[str] = set()
    bullet_lowers: list[str] = []
    for emp in facts_obj.get("employment", []):
        for bullet in emp.get("bullets", []):
            bid = bullet.get("bullet_id")
            if not bid:
                continue
            allowed.add(bid)
            txt = bullet.get("text", "")
            bullet_lowers.append(txt.lower())
            rows.append(
                {
                    "fact_id": bid,
                    "claim_text": txt,
                    "source_employment": emp.get("employer"),
                    "has_metric": bool(bullet.get("has_metric")),
                    "metric_raw": bullet.get("metric_raw", "") if bullet.get("has_metric") else "",
                    "domain": bullet.get("domain", ""),
                    "technologies": bullet.get("technologies", []),
                }
            )
            if bullet.get("metric_raw"):
                allowed.add(f"{bid}_metric_{sha16(str(bullet['metric_raw']))[:8]}")
    rows.sort(key=lambda r: r["fact_id"])
    return rows, allowed, bullet_lowers


def build_selected_fact_plan(facts: list[dict[str, Any]], required_ids: list[str]) -> dict[str, Any]:
    return {
        "section_id": "competencies",
        "selection_method": "canonical_base_resume_employment_bullets",
        "facts": facts,
        "required_fact_ids": required_ids,
    }


def load_companion_context() -> str:
    parts: list[str] = []
    for label, lane in COMPANION_LANES:
        path = resolve_effective_lane_l2_path(REPO_ROOT, lane)
        if path is None or not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        chunk_lines = [f"### {label}"]
        if label == "executive_summary":
            t = str(data.get("resume_display_text") or "").strip()
            if t:
                chunk_lines.append(t)
        elif label == "unify_narrative":
            t = str(data.get("narrative_sentence") or "").strip()
            if t:
                chunk_lines.append(t)
        elif label == "ibm_narrative":
            t = str(data.get("narrative_sentence") or "").strip()
            if t:
                chunk_lines.append(t)
        elif label in ("unify_bullets", "ibm_bullets"):
            for b in data.get("bullets") or []:
                chunk_lines.append(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}")
        if len(chunk_lines) > 1:
            parts.append("\n".join(chunk_lines))
    return "\n\n".join(parts)


def build_resume_support_blob(bullet_rows: list[dict[str, Any]], companion_blob: str) -> str:
    chunks: list[str] = []
    for row in bullet_rows:
        chunks.append(str(row.get("claim_text", "")))
        for tech in row.get("technologies") or []:
            chunks.append(str(tech))
    chunks.append(companion_blob)
    return " ".join(chunks).lower()


def build_c0_proof_support_blob(bullet_rows: list[dict[str, Any]]) -> str:
    """C0 employment bullets + technologies only — excludes companion/U-tier for proof overlap."""
    chunks: list[str] = []
    for row in bullet_rows:
        chunks.append(str(row.get("claim_text", "")))
        for tech in row.get("technologies") or []:
            chunks.append(str(tech))
    return " ".join(chunks).lower()


def build_runtime_payload(
    *,
    base_json_path: Path,
    base_hash: str,
    selected_fact_plan: dict[str, Any],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
) -> dict[str, Any]:
    return {
        "run_id": datetime.now(timezone.utc).strftime("competencies_%Y%m%d_%H%M%S"),
        "section_id": "competencies",
        "prompt_id": PROMPT_ID,
        "base_resume_json_ref": str(base_json_path.relative_to(REPO_ROOT)) if base_json_path.is_relative_to(REPO_ROOT) else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": selected_fact_plan,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "writable_context_scope": "competencies_only",
        "full_resume_writable": False,
    }


def build_prompt_messages(
    runtime_payload: dict[str, Any],
    companion_context: str,
    fact_lines: str,
) -> list[dict[str, str]]:
    """W5: PA-compiled single system message via ``section_prompt_adapter`` (no inline prompt fallback)."""
    run_id = str(runtime_payload.get("run_id") or "competencies_prompt_build")
    compiled = compile_competencies_prompt(
        runtime_payload,
        companion_context=companion_context,
        fact_lines=fact_lines,
        run_id=run_id,
    )
    return compiled.artifact.messages


def parse_model_json(raw: str) -> tuple[dict[str, Any] | None, str]:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            parsed = {"competencies": parsed}
        if isinstance(parsed, dict):
            return parsed, ""
    except json.JSONDecodeError as exc:
        salvaged, salvage_err = salvage_truncated_competencies_json(text)
        if salvaged is not None:
            return salvaged, ""
        return None, f"JSON parse failed: {exc}"
    return None, "Model output was not a JSON object."


def salvage_truncated_competencies_json(text: str) -> tuple[dict[str, Any] | None, str]:
    """Recover competencies[] when vLLM hits max_tokens mid claim_ledger (finish_reason=length)."""
    marker = '"claim_ledger"'
    if marker not in text or '"competencies"' not in text:
        return None, "no salvage anchor"
    head = text[: text.index(marker)].rstrip().rstrip(",")
    tail_stub = (
        ', "claim_ledger": [], "jd_alignment": {"targeting_only": true, "jd_used_as_proof": false, '
        '"briefing_used_as_proof": false, "companion_context_used_as_proof": false}, '
        '"excluded_jd_skills": [], "removed_or_rewritten_terms": [], "gap_notes": [], '
        '"change_log": [{"operation": "salvage_truncated_competencies_json", "reason": "length"}], '
        '"self_check": {}}'
    )
    try:
        parsed = json.loads(head + tail_stub)
    except json.JSONDecodeError as exc:
        return None, str(exc)
    if not isinstance(parsed, dict) or not isinstance(parsed.get("competencies"), list):
        return None, "salvaged object missing competencies"
    return parsed, ""


def _fix_fact_id_typos(fid: str, allowed_fact_ids: set[str] | None = None) -> str:
    from apps_rg.runtime.validators.fact_id_typo_repair import repair_fact_id_against_allowlist

    return repair_fact_id_against_allowlist(fid, allowed_fact_ids)


def _novel_term_vs_seen(candidate: str, seen_lower: set[str]) -> bool:
    """Reject candidates that collide with X2 duplicate/near-duplicate rules."""
    cl = candidate.strip().lower()
    if len(cl) < 3:
        return False
    if cl in seen_lower:
        return False
    for existing in seen_lower:
        if len(existing) >= 10 and len(cl) >= 10 and (cl in existing or existing in cl):
            return False
    return True


def _sentence_like_term(candidate: str) -> bool:
    tl = candidate.strip()
    if re.search(r"[.!?]\s", tl) or (tl.endswith(".") and len(tl) > 1):
        return True
    if len(tl.split()) > 9:
        return True
    if re.match(r"^(?:the|a|an)\s+\w+", tl, re.I):
        return True
    return False


def _candidate_phrases_for_category(cat: dict[str, Any], rows_by_id: dict[str, dict[str, Any]]) -> list[str]:
    """Phrases grounded in sourced bullets only (technologies + short claim fragments)."""
    ordered: list[str] = []
    seen_l: set[str] = set()
    fid_list = [_fix_fact_id_typos(str(x)).split("_metric_")[0] for x in (cat.get("source_fact_ids") or [])]

    def push(phrase: str) -> None:
        p = str(phrase).strip().rstrip(".,;:")
        if len(p) < 4 or len(p) > 56:
            return
        low = p.lower()
        if low in seen_l:
            return
        seen_l.add(low)
        ordered.append(p)

    for fid in fid_list:
        row = rows_by_id.get(fid)
        if not row:
            continue
        for tech in row.get("technologies") or []:
            if isinstance(tech, str) and tech.strip():
                push(tech)
        raw = str(row.get("claim_text", "") or "").strip()
        if not raw:
            continue
        fragments = [
            fragment.strip().rstrip(".,;—")
            for fragment in re.split(r"[,;:]+|\s+and\s+", raw, flags=re.I)
            if isinstance(fragment, str) and fragment.strip()
        ]
        for frag in fragments:
            if "\n" in frag or len(frag) > 96:
                continue
            trimmed = frag if len(frag) <= 56 else frag[:56].rsplit(maxsplit=1)[0].strip()
            push(trimmed)
    return ordered


def repair_structured_competencies_source_facts(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    resume_support_blob_lower: str,
) -> None:
    """Bind structured term ``source_fact_id`` deterministically when the model cites an unusable token.

    - Never invents canonical ``bul_*`` ids beyond those already declared on the category (filtered to allowed).
    - When multiple category facts remain, prefers the lexicographically first fact id whose resume-grounding
      heuristic overlaps the competency phrase; otherwise falls back to the first validated category fact id.
      (Both choices are deterministic and drawn from validated category provenance.)
    """

    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return

    changelog = parsed.setdefault("change_log", [])
    if not isinstance(changelog, list):
        changelog = []
        parsed["change_log"] = changelog

    for cat in comps:
        if not isinstance(cat, dict):
            continue
        terms_raw = cat.get("terms")
        if not isinstance(terms_raw, list):
            continue
        if not _terms_list_has_dict(terms_raw):
            continue

        raw_ids = [_fix_fact_id_typos(str(x), allowed_fact_ids) for x in (cat.get("source_fact_ids") or [])]
        validated = sorted(
            {base for x in raw_ids if (base := x.split("_metric_")[0]) in allowed_fact_ids}
        )
        if not validated:
            continue

        for raw_t in terms_raw:
            if not isinstance(raw_t, dict):
                continue
            phrase = term_phrase(raw_t)
            if not phrase:
                continue

            sr = raw_t.get("source_fact_id")
            current_base = ""
            if sr is not None and str(sr).strip():
                current_base = _fix_fact_id_typos(str(sr), allowed_fact_ids).split("_metric_")[0]

            picked = ""
            if current_base in allowed_fact_ids and term_primary_support_overlap(
                phrase, current_base, resume_support_blob_lower
            ):
                picked = current_base
            else:
                for fid in validated:
                    if term_primary_support_overlap(phrase, fid, resume_support_blob_lower):
                        picked = fid
                        break

            fallback = validated[0]
            resolved = picked or fallback

            if str(raw_t.get("source_fact_id", "")).split("_metric_")[0] != resolved:
                raw_before = raw_t.get("source_fact_id")
                raw_t["source_fact_id"] = resolved
                changelog.append(
                    {
                        "operation": "repair_structured_competencies_source_fact",
                        "reason": (
                            "source_fact_id not usable for deterministic X2 grounding; "
                            "rebound within validated category source_fact_ids"
                        ),
                        "category_label": cat.get("category_label"),
                        "phrase": phrase,
                        "source_fact_id_before": raw_before,
                        "source_fact_id_after": resolved,
                    },
                )


def _structured_terms_near_duplicate(a: str, b: str) -> bool:
    """Mirrors competencies X2 duplicate/near-duplicate detection for flattened phrases."""
    a_norm = a.lower().strip().rstrip(".")
    b_norm = b.lower().strip().rstrip(".")
    if a_norm == b_norm:
        return True
    return bool(
        len(a_norm) >= 10 and len(b_norm) >= 10 and (a_norm in b_norm or b_norm in a_norm)
    )


def _long_bullet_text_restatement(term: str, bullet_texts_lower: list[str]) -> bool:
    """Mirror ``competencies_x2._bullet_restatement`` — long phrase embedded in a canon bullet."""

    tn = term.lower().strip()
    if len(tn) < 36:
        return False
    return any(tn in b for b in bullet_texts_lower)


def coerce_structured_competencies_resume_support(
    parsed: dict[str, Any],
    bullet_rows: list[dict[str, Any]],
    resume_support_blob_lower: str,
    bullet_texts_lower: list[str],
    *,
    allowed_fact_ids: set[str] | None = None,
) -> None:
    """Rewrite unsupported structured competency phrases using bullet-derived fragments already in blob.

    Terms with no grounding options are dropped rather than emitting resume-ungrounded payloads.
    """
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return
    rows_by_id = {str(r.get("fact_id")): r for r in bullet_rows if r.get("fact_id")}
    rewrote = parsed.setdefault("removed_or_rewritten_terms")
    if not isinstance(rewrote, list):
        rewrote = []
        parsed["removed_or_rewritten_terms"] = rewrote
    changelog = parsed.setdefault("change_log", [])
    if not isinstance(changelog, list):
        changelog = []
        parsed["change_log"] = changelog

    for cat in comps:
        if not isinstance(cat, dict):
            continue
        terms_raw = cat.get("terms")
        if not isinstance(terms_raw, list) or not _terms_list_has_dict(terms_raw):
            continue
        new_terms: list[Any] = []
        for raw_t in terms_raw:
            if not isinstance(raw_t, dict):
                new_terms.append(raw_t)
                continue
            phrase = term_phrase(raw_t)
            if not phrase:
                continue
            sr = raw_t.get("source_fact_id")
            fid_base = (
                _fix_fact_id_typos(str(sr), allowed_fact_ids).split("_metric_")[0]
                if sr is not None and str(sr).strip()
                else ""
            )
            if not fid_base:
                changelog.append(
                    {
                        "operation": "drop_ungrounded_structured_competency",
                        "reason": "missing source_fact_id after structured repair",
                        "category_label": cat.get("category_label"),
                        "phrase": phrase,
                    }
                )
                continue
            if (
                term_primary_support_overlap(phrase, fid_base, resume_support_blob_lower)
                and not _long_bullet_text_restatement(phrase, bullet_texts_lower)
            ):
                new_terms.append(raw_t)
                continue

            cand_pool = _candidate_phrases_for_category(
                {"source_fact_ids": [fid_base], "category_label": cat.get("category_label")},
                rows_by_id,
            )
            eligible = sorted(
                (
                    str(c).strip()
                    for c in cand_pool
                    if term_primary_support_overlap(str(c).strip(), fid_base, resume_support_blob_lower)
                    and not _long_bullet_text_restatement(str(c).strip(), bullet_texts_lower)
                ),
                key=lambda c: (len(c), c.lower()),
            )
            if not eligible:
                rewrote.append(
                    f"DROPPED ungrounded term {phrase!r} (fact {fid_base}) "
                    f"within {cat.get('category_label', '?')}"
                )
                changelog.append(
                    {
                        "operation": "drop_ungrounded_structured_competency",
                        "reason": "no bullet fragments for bound fact overlap resume support blob",
                        "category_label": cat.get("category_label"),
                        "phrase": phrase,
                        "source_fact_id": fid_base,
                    }
                )
                continue

            resolved = eligible[0]
            if resolved != phrase:
                raw_next = dict(raw_t)
                raw_next["text"] = resolved
                rewrote.append(
                    f"{phrase}→{resolved} (within {cat.get('category_label', '?')} via {fid_base})"
                )
                changelog.append(
                    {
                        "operation": "coerce_structured_competency_resume_support",
                        "reason": "term tokens absent from resume support blob — substituted sourced fragment",
                        "category_label": cat.get("category_label"),
                        "phrase_before": phrase,
                        "phrase_after": resolved,
                        "source_fact_id": fid_base,
                    }
                )
                new_terms.append(raw_next)
            else:
                new_terms.append(raw_t)
        cat["terms"] = new_terms


_KEYWORD_STUFFING_STOPWORDS = frozenset(
    {
        "and",
        "or",
        "the",
        "a",
        "an",
        "of",
        "for",
        "to",
        "in",
        "on",
        "with",
        "via",
        "per",
        "by",
    }
)


def _competency_term_content_words(phrase: str) -> list[str]:
    return [
        w
        for w in re.findall(r"[a-z]{3,}", phrase.lower())
        if w not in _KEYWORD_STUFFING_STOPWORDS
    ]


def reduce_competency_keyword_stuffing(parsed: dict[str, Any]) -> None:
    """Drop structured terms until x2_no_keyword_stuffing (<=5 repeats per non-stopword)."""
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return

    def _global_word_freq() -> dict[str, int]:
        freq: dict[str, int] = {}
        for cat in comps:
            if not isinstance(cat, dict):
                continue
            terms_raw = cat.get("terms")
            if not isinstance(terms_raw, list):
                continue
            for raw_t in terms_raw:
                phrase = term_phrase(raw_t) if isinstance(raw_t, dict) else str(raw_t or "")
                for w in _competency_term_content_words(phrase):
                    freq[w] = freq.get(w, 0) + 1
        return freq

    changelog = parsed.setdefault("change_log", [])
    if not isinstance(changelog, list):
        changelog = []
        parsed["change_log"] = changelog

    while True:
        freq = _global_word_freq()
        if not freq or max(freq.values()) <= 5:
            break
        worst = max(freq, key=lambda w: freq[w])
        removed = False
        for cat in comps:
            if not isinstance(cat, dict):
                continue
            terms_raw = cat.get("terms")
            if not isinstance(terms_raw, list):
                continue
            kept: list[Any] = []
            for raw_t in terms_raw:
                phrase = term_phrase(raw_t) if isinstance(raw_t, dict) else str(raw_t or "")
                words = _competency_term_content_words(phrase)
                if not removed and worst in words and len(terms_raw) > 2:
                    changelog.append(
                        {
                            "operation": "drop_keyword_stuffing_term",
                            "reason": "x2_no_keyword_stuffing",
                            "category_label": cat.get("category_label"),
                            "phrase": phrase,
                            "overloaded_token": worst,
                        }
                    )
                    removed = True
                    continue
                kept.append(raw_t)
            if removed:
                cat["terms"] = kept
                break
        if not removed:
            break


def dedupe_structured_competency_terms(parsed: dict[str, Any]) -> None:
    """Collapse duplicate structured competency phrases deterministically (X2-aligned near-duplicate rule)."""
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return
    rewrote = parsed.setdefault("removed_or_rewritten_terms")
    if not isinstance(rewrote, list):
        rewrote = []
        parsed["removed_or_rewritten_terms"] = rewrote
    changelog = parsed.setdefault("change_log", [])
    if not isinstance(changelog, list):
        changelog = []
        parsed["change_log"] = changelog

    flattened_seen: list[str] = []

    def _keep_phrase(phrase_lower: str) -> bool:
        for seen in flattened_seen:
            if _structured_terms_near_duplicate(phrase_lower, seen):
                return False
        flattened_seen.append(phrase_lower)
        return True

    for cat in comps:
        if not isinstance(cat, dict):
            continue
        terms_raw = cat.get("terms")
        if not isinstance(terms_raw, list) or not _terms_list_has_dict(terms_raw):
            continue
        kept: list[dict[str, Any]] = []
        for raw_t in terms_raw:
            if not isinstance(raw_t, dict):
                continue
            phrase = term_phrase(raw_t)
            if not phrase:
                continue
            low = phrase.lower().strip().rstrip(".")
            if _keep_phrase(low):
                kept.append(raw_t)
            else:
                changelog.append(
                    {
                        "operation": "drop_structured_competency_near_duplicate",
                        "reason": "x2_duplicate_variants_collapsed / near-duplicate term",
                        "category_label": cat.get("category_label"),
                        "phrase": phrase,
                    }
                )
                rewrote.append(
                    f"DEDUP dropped {phrase!r} near-duplicate "
                    f"within {cat.get('category_label', '?')}"
                )
        cat["terms"] = kept


def expand_structured_competencies_min_two_terms(
    parsed: dict[str, Any],
    *,
    bullet_rows: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    resume_support_blob_lower: str,
    bullet_texts_lower: list[str],
) -> None:
    """When a structured (dict-backed) competency category emits only one nonempty term after repair/dedupe,
    deterministically append a second short grounded phrase sourced from the same validated ``bul_*`` rows.

    Addresses ``x2_competency_format_category_colon_terms`` (2≤terms≤6) without inventing canonical fact ids —
    fragments are restricted to bullet ``technologies`` and short claim splits (see
    :func:`_candidate_phrases_for_category`).
    """

    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return

    rows_by_id = {str(r.get("fact_id")): r for r in bullet_rows if r.get("fact_id")}

    def _nonempty_terms_total(terms_raw: Any) -> int:
        if not isinstance(terms_raw, list):
            return 0
        total = 0
        for t in terms_raw:
            if isinstance(t, dict):
                if term_phrase(t):
                    total += 1
            elif isinstance(t, str) and t.strip():
                total += 1
        return total

    global_seen: set[str] = set()
    for cat0 in comps:
        if not isinstance(cat0, dict):
            continue
        for tt in cat0.get("terms") or []:
            p0 = term_phrase(tt)
            if p0:
                global_seen.add(p0.lower().strip().rstrip("."))

    changelog = parsed.setdefault("change_log", [])
    if not isinstance(changelog, list):
        changelog = []
        parsed["change_log"] = changelog

    for cat in comps:
        if not isinstance(cat, dict):
            continue
        terms_raw = cat.get("terms")
        if not isinstance(terms_raw, list) or not _terms_list_has_dict(terms_raw):
            continue
        if _nonempty_terms_total(terms_raw) != 1:
            continue

        validated_set: set[str] = set()
        for sr in cat.get("source_fact_ids") or []:
            x = _fix_fact_id_typos(str(sr))
            fid = x.split("_metric_")[0]
            if fid in allowed_fact_ids:
                validated_set.add(fid)
        validated = sorted(validated_set)
        if not validated:
            continue

        local_seen: set[str] = set()
        for t in terms_raw:
            pv = term_phrase(t)
            if pv:
                local_seen.add(pv.lower().strip().rstrip("."))
        combined_seen = global_seen | local_seen

        cand_pool = _candidate_phrases_for_category(cat, rows_by_id)
        eligible: list[tuple[int, str, str, str]] = []
        for raw_cand in cand_pool:
            cand = str(raw_cand).strip()
            if not cand:
                continue
            if _sentence_like_term(cand):
                continue
            if _long_bullet_text_restatement(cand, bullet_texts_lower):
                continue
            if not _novel_term_vs_seen(cand, combined_seen):
                continue
            picked_fid = ""
            for fid in validated:
                if term_primary_support_overlap(cand, fid, resume_support_blob_lower):
                    picked_fid = fid
                    break
            if not picked_fid:
                continue
            eligible.append((len(cand), cand.lower(), cand, picked_fid))

        if not eligible:
            continue
        eligible.sort()
        chosen = eligible[0]
        _, _, phrase, sfid = chosen
        append_term = {"text": phrase, "source_fact_id": sfid}
        wr = parsed.setdefault("removed_or_rewritten_terms")
        if not isinstance(wr, list):
            wr = []
            parsed["removed_or_rewritten_terms"] = wr
        changelog.append(
            {
                "operation": "expand_structured_competency_min_two_terms",
                "reason": (
                    "structured category had exactly one nonempty term — appended second phrase from "
                    "validated category bullet technologies/fragments overlapping resume blob"
                ),
                "category_label": cat.get("category_label"),
                "phrase": phrase,
                "source_fact_id": sfid,
            }
        )
        wr.append(f"expand min-two: +{phrase!r} (@{sfid}) in {cat.get('category_label', '?')}")
        terms_raw.append(append_term)
        cat["terms"] = terms_raw
        global_seen.add(phrase.lower().strip().rstrip("."))


def collapse_duplicate_competency_terms(
    parsed: dict[str, Any],
    bullet_rows: list[dict[str, Any]],
    resume_support_blob_lower: str,
) -> None:
    """Rewrite duplicate/near-duplicate term strings across categories before X2 (resume-grounded substitutes)."""
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return
    rows_by_id = {str(r.get("fact_id")): r for r in bullet_rows if r.get("fact_id")}
    blob = resume_support_blob_lower

    rewrote = parsed.setdefault("removed_or_rewritten_terms")
    if not isinstance(rewrote, list):
        rewrote = []
        parsed["removed_or_rewritten_terms"] = rewrote
    change_log = parsed.setdefault("change_log")
    if not isinstance(change_log, list):
        change_log = []
        parsed["change_log"] = change_log

    flattened_before: list[str] = []
    for cat in comps:
        if not isinstance(cat, dict):
            continue
        for t in cat.get("terms") or []:
            p = term_phrase(t)
            if p:
                flattened_before.append(p)

    seen_lower: set[str] = set()
    made_change = False

    for cat in comps:
        if not isinstance(cat, dict):
            continue
        terms_raw = cat.get("terms")
        if not isinstance(terms_raw, list):
            continue
        if _terms_list_has_dict(terms_raw):
            for raw_t in terms_raw:
                p = term_phrase(raw_t)
                if p:
                    seen_lower.add(p.lower().rstrip("."))
            continue
        cand_pool = _candidate_phrases_for_category(cat, rows_by_id)
        new_terms: list[str] = []
        for raw_t in terms_raw:
            if not isinstance(raw_t, str):
                continue
            t_orig = raw_t.strip()
            if not t_orig:
                continue
            low = t_orig.lower()
            is_dup_with_seen = False
            if low in seen_lower:
                is_dup_with_seen = True
            else:
                for ext in seen_lower:
                    if len(ext) >= 10 and len(low) >= 10 and (low in ext or ext in low):
                        is_dup_with_seen = True
                        break
                if not is_dup_with_seen:
                    for nt in new_terms:
                        nl = nt.lower()
                        if low == nl or (
                            len(low) >= 10 and len(nl) >= 10 and (low in nl or nl in low)
                        ):
                            is_dup_with_seen = True
                            break
            replacement: str | None = None
            if is_dup_with_seen:
                for cand in cand_pool:
                    low_c = cand.lower()
                    if low_c not in blob:
                        continue
                    if low_c == low:
                        continue
                    if _sentence_like_term(cand):
                        continue
                    if _novel_term_vs_seen(
                        cand,
                        seen_lower | {lt.lower().rstrip(".") for lt in new_terms},
                    ):
                        replacement = cand
                        break
            use_t = replacement if replacement is not None else t_orig
            if replacement is not None:
                made_change = True
                rewrote.append(f"{t_orig}→{replacement} (within {cat.get('category_label', '?')})")

            low_use = use_t.strip().lower().rstrip(".")

            def _coll(low: str) -> bool:
                if low in seen_lower:
                    return True
                for ext in seen_lower:
                    if len(low) >= 10 and len(ext) >= 10 and (low in ext or ext in low):
                        return True
                for nt in new_terms:
                    nl = nt.strip().lower().rstrip(".")
                    if (
                        nl == low
                        or (
                            len(low) >= 10
                            and len(nl) >= 10
                            and (low in nl or nl in low)
                        )
                    ):
                        return True
                return False

            if _coll(low_use):
                alt: str | None = None
                for cand in cand_pool:
                    cl = cand.lower()
                    if cl not in blob or _sentence_like_term(cand):
                        continue
                    if cl == low_use:
                        continue
                    if _novel_term_vs_seen(
                        cand,
                        seen_lower | {lt.lower().rstrip(".") for lt in new_terms},
                    ):
                        alt = cand
                        break
                if alt:
                    rewrote.append(
                        f"{use_t}→{alt} "
                        "(post-substitution dedupe near x2_duplicate_variants_collapsed)",
                    )
                    made_change = True
                    use_t = alt.strip()
                    low_use = use_t.lower().rstrip(".")

            seen_lower.add(low_use)
            new_terms.append(use_t.strip())
        cat["terms"] = new_terms

    flattened_after = [
        p
        for c in comps
        if isinstance(c, dict)
        for tt in (c.get("terms") or [])
        for p in [term_phrase(tt)]
        if p
    ]
    if made_change:
        change_log.append(
            {
                "operation": "duplicate_terms_collapsed_dispatch",
                "reason": "x2_duplicate_variants_collapsed",
                "term_count_before_after": [len(flattened_before), len(flattened_after)],
            },
        )


def rebuild_claim_ledger_from_competencies(parsed: dict[str, Any], allowed_fact_ids: set[str]) -> None:
    """One claim_ledger row per category term row (canonical shape for competencies X2 mapping)."""
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return
    ledger: list[dict[str, Any]] = []
    for cat in comps:
        if not isinstance(cat, dict):
            continue
        raw_ids = [_fix_fact_id_typos(str(x)) for x in (cat.get("source_fact_ids") or [])]
        ids = sorted({x.split("_metric_")[0] for x in raw_ids if x.split("_metric_")[0] in allowed_fact_ids})
        if not ids:
            continue
        cat["source_fact_ids"] = ids
        for raw_t in cat.get("terms") or []:
            ts = term_phrase(raw_t)
            if not ts:
                continue
            if isinstance(raw_t, dict) and raw_t.get("source_fact_id") is not None:
                sid = _fix_fact_id_typos(str(raw_t["source_fact_id"])).split("_metric_")[0]
                if sid in allowed_fact_ids:
                    ledger.append({"claim_text": ts, "source_fact_ids": [sid]})
                continue
            ledger.append({"claim_text": ts, "source_fact_ids": list(ids)})
    parsed["claim_ledger"] = ledger


def ensure_claim_ledger_coverage(parsed: dict[str, Any], allowed_fact_ids: set[str]) -> None:
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return
    ledger: list[dict[str, Any]] = list(parsed.get("claim_ledger") or [])
    covered = {str(e.get("claim_text", "")).strip().lower() for e in ledger if isinstance(e, dict)}
    for cat in comps:
        if not isinstance(cat, dict):
            continue
        raw_ids = [_fix_fact_id_typos(str(x)) for x in (cat.get("source_fact_ids") or [])]
        ids = [x.split("_metric_")[0] for x in raw_ids if x.split("_metric_")[0] in allowed_fact_ids]
        if not ids:
            continue
        cat["source_fact_ids"] = ids
        for raw_t in cat.get("terms") or []:
            ts = term_phrase(raw_t)
            if not ts:
                continue
            if ts.lower() not in covered:
                if isinstance(raw_t, dict) and raw_t.get("source_fact_id") is not None:
                    sid = _fix_fact_id_typos(str(raw_t["source_fact_id"])).split("_metric_")[0]
                    if sid in allowed_fact_ids:
                        ledger.append({"claim_text": ts, "source_fact_ids": [sid]})
                else:
                    ledger.append({"claim_text": ts, "source_fact_ids": list(ids)})
                covered.add(ts.lower())
    for entry in ledger:
        raw_ids = entry.get("source_fact_ids")
        if not isinstance(raw_ids, list):
            continue
        entry["source_fact_ids"] = [_fix_fact_id_typos(str(x)).split("_metric_")[0] for x in raw_ids]
    parsed["claim_ledger"] = ledger


def prune_claim_ledger_bullet_paste(parsed: dict[str, Any]) -> None:
    """Remove claim_ledger rows that look like full employment-bullet pastes, not competency noun phrases."""

    comps = parsed.get("competencies")
    term_claim_lower: set[str] = set()
    if isinstance(comps, list):
        for cat in comps:
            if not isinstance(cat, dict):
                continue
            for raw_t in cat.get("terms") or []:
                p = term_phrase(raw_t)
                if p:
                    term_claim_lower.add(p.strip().lower())

    ledger = parsed.get("claim_ledger")
    if not isinstance(ledger, list):
        return
    # Canonical employment bullets are often 180–260+ chars; competencies stay short noun phrases.
    _employment_bullet_heuristic_min_chars = 220

    cleaned: list[dict[str, Any]] = []
    for entry in ledger:
        if not isinstance(entry, dict):
            continue
        ct = str(entry.get("claim_text", "")).strip()
        if "\n" in ct:
            continue
        low = ct.lower().rstrip(".")
        if low in term_claim_lower:
            cleaned.append(entry)
            continue
        if len(ct) > _employment_bullet_heuristic_min_chars:
            continue
        cleaned.append(entry)
    parsed["claim_ledger"] = cleaned


def normalize_parsed_output(parsed: dict[str, Any] | None, runtime_payload: dict[str, Any], allowed_fact_ids: set[str]) -> dict[str, Any] | None:
    if not parsed:
        return parsed
    out = dict(parsed)
    if not isinstance(out.get("competencies"), list):
        out["competencies"] = []
    if not isinstance(out.get("selected_fact_plan"), dict):
        out["selected_fact_plan"] = runtime_payload["selected_fact_plan"]
    else:
        out["selected_fact_plan"] = {
            **runtime_payload["selected_fact_plan"],
            "required_fact_ids": out["selected_fact_plan"].get("required_fact_ids")
            or runtime_payload["selected_fact_plan"]["required_fact_ids"],
        }
    out.setdefault("jd_alignment", {})
    out["jd_alignment"] = merge_jd_alignment(out.get("jd_alignment"))
    out.setdefault("excluded_jd_skills", [])
    out.setdefault("removed_or_rewritten_terms", [])
    out.setdefault("gap_notes", [])
    out.setdefault("change_log", [])
    out.setdefault("self_check", {"normalized_by_dispatch": True})
    prune_claim_ledger_bullet_paste(out)
    ensure_claim_ledger_coverage(out, allowed_fact_ids)
    return out


def retry_qwen_for_parse(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parse_error: str,
    *,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
) -> tuple[str, dict[str, Any] | None, str]:
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                f"JSON INVALID: {parse_error}. Return one NEW compact JSON object only with required keys: "
                "competencies (8), selected_fact_plan, claim_ledger, jd_alignment, excluded_jd_skills, "
                "removed_or_rewritten_terms, gap_notes, change_log, self_check."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": COMPETENCIES_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(
        tag_reasoning_lane(repair_payload, LANE_KEY),
        artifact_dir=artifact_dir,
        run_id=run_id,
    )
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    def _term_obj(phrase: str, fid: str) -> dict[str, Any]:
        return {"text": phrase, "source_fact_id": fid, "source_fact_ids": [fid]}

    pp = runtime_payload.get("proof_pool_metadata") or {}
    pool_type = str(pp.get("proof_pool_type") or "")
    if pool_type in ("selected_role_fact_set", "broad_skills_ledger"):
        raw_allowed = [str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])]
        allowed = [x for x in raw_allowed if "_metric_" not in x]
        if not allowed and raw_allowed:
            allowed = sorted({x.split("_metric_", 1)[0] for x in raw_allowed})
        if not allowed:
            allowed = ["proof_pool_placeholder"]
        competencies_srfs: list[dict[str, Any]] = []
        for i in range(8):
            fid = allowed[i % len(allowed)]
            competencies_srfs.append(
                {
                    "category_label": f"SRFS Competency Area {i + 1}",
                    "terms": [
                        _term_obj(f"governed capability cluster {i}a", fid),
                        _term_obj(f"governed capability cluster {i}b", fid),
                        _term_obj(f"governed capability cluster {i}c", fid),
                    ],
                    "source_fact_ids": [fid],
                }
            )
        ledger_srfs: list[dict[str, Any]] = []
        for cat in competencies_srfs:
            ids = list(cat["source_fact_ids"])
            for t in cat["terms"]:
                ts = term_phrase(t)
                if not ts:
                    continue
                if isinstance(t, dict) and t.get("source_fact_id") is not None:
                    sid = _fix_fact_id_typos(str(t["source_fact_id"])).split("_metric_")[0]
                    ledger_srfs.append({"claim_text": ts, "source_fact_ids": [sid]})
                else:
                    ledger_srfs.append({"claim_text": ts, "source_fact_ids": list(ids)})
        return {
            "competencies": competencies_srfs,
            "selected_fact_plan": runtime_payload["selected_fact_plan"],
            "claim_ledger": ledger_srfs,
            "jd_alignment": {
                "targeting_only": True,
                "jd_used_as_proof": False,
                "briefing_used_as_proof": False,
                "companion_context_used_as_proof": False,
            },
            "excluded_jd_skills": ["raw LLMOps toolchain dump"],
            "removed_or_rewritten_terms": [],
            "gap_notes": [],
            "change_log": [],
            "self_check": {"eight_categories": True, "terms_are_phrases": True},
        }

    competencies: list[dict[str, Any]] = [
        {
            "category_label": "Agentic AI Platforms",
            "terms": [
                _term_obj("governed agentic systems", "bul_unify_001"),
                _term_obj("multi-agent coordination", "bul_unify_001"),
                _term_obj("policy-aware routing", "bul_unify_001"),
            ],
            "source_fact_ids": ["bul_unify_001"],
        },
        {
            "category_label": "Dependency Intelligence",
            "terms": [
                _term_obj("graph signal extraction", "bul_unify_002"),
                _term_obj("modernization acceleration cues", "bul_unify_002"),
                _term_obj("dependency intelligence", "bul_unify_002"),
            ],
            "source_fact_ids": ["bul_unify_002"],
        },
        {
            "category_label": "Retrieval and Quality Gates",
            "terms": [
                _term_obj("retrieval instrumentation posture", "bul_unify_003"),
                _term_obj("quality gate patterns", "bul_unify_003"),
                _term_obj("observability rollouts", "bul_unify_003"),
            ],
            "source_fact_ids": ["bul_unify_003"],
        },
        {
            "category_label": "AI Lifecycle Operations",
            "terms": [
                _term_obj("lifecycle standardization", "bul_unify_004"),
                _term_obj("delivery acceleration", "bul_unify_004"),
                _term_obj("monitoring discipline", "bul_unify_004"),
            ],
            "source_fact_ids": ["bul_unify_004"],
        },
        {
            "category_label": "Cloud Platforms and Data Planes",
            "terms": [
                _term_obj("distributed service tiers", "bul_unify_005"),
                _term_obj("lakehouse-adjacent pipelines", "bul_unify_005"),
                _term_obj("identity-aware gateways", "bul_unify_005"),
            ],
            "source_fact_ids": ["bul_unify_005"],
        },
        {
            "category_label": "Platform Productization",
            "terms": [
                _term_obj("platform economics lift", "bul_unify_006"),
                _term_obj("specialist scaling curve", "bul_unify_006"),
                _term_obj("IP-forward packaging", "bul_unify_006"),
            ],
            "source_fact_ids": ["bul_unify_006"],
        },
        {
            "category_label": "Enterprise AI and Analytics",
            "terms": [
                _term_obj("cloud posture modernization", "bul_ibm_001"),
                _term_obj("uptime discipline", "bul_ibm_001"),
                _term_obj("regulated delivery contexts", "bul_ibm_001"),
            ],
            "source_fact_ids": ["bul_ibm_001"],
        },
        {
            "category_label": "Partnership and Revenue Engineering",
            "terms": [
                _term_obj("multi-year alliance rhythm", "bul_ibm_005"),
                _term_obj("joint sell patterns", "bul_ibm_005"),
                _term_obj("incremental revenue streams", "bul_ibm_005"),
            ],
            "source_fact_ids": ["bul_ibm_005"],
        },
    ]
    ledger: list[dict[str, Any]] = []
    for cat in competencies:
        ids = list(cat["source_fact_ids"])
        for t in cat["terms"]:
            ts = term_phrase(t)
            if not ts:
                continue
            if isinstance(t, dict) and t.get("source_fact_id") is not None:
                sid = _fix_fact_id_typos(str(t["source_fact_id"])).split("_metric_")[0]
                ledger.append({"claim_text": ts, "source_fact_ids": [sid]})
            else:
                ledger.append({"claim_text": ts, "source_fact_ids": list(ids)})
    return {
        "competencies": competencies,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": ledger,
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
        "excluded_jd_skills": ["raw LLMOps toolchain dump"],
        "removed_or_rewritten_terms": [],
        "gap_notes": [],
        "change_log": [],
        "self_check": {"eight_categories": True, "terms_are_phrases": True},
    }


def competencies_display_text(competencies: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for c in competencies:
        label = str(c.get("category_label", "")).strip()
        terms = c.get("terms") or []
        if isinstance(terms, list):
            phrases = [p for t in terms if (p := term_phrase(t))]
            lines.append(f"{label}: {', '.join(phrases)}")
    return "\n".join(lines)


def infer_product_quality(runtime_generation_status: str, x2_gates: list[dict[str, Any]]) -> tuple[str, str]:
    failed = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    return infer_product_quality_blocked_or_mock(
        runtime_generation_status=runtime_generation_status,
        x2_failed_gate_ids=failed,
        pass_reason="REAL_LLM output passed all deterministic competencies gates.",
    )


def clarify_x3_for_competencies_live_provider_preflight(
    x3: X3Disposition,
    *,
    live_preflight_blocked: bool,
) -> X3Disposition:
    """Rewrite disposition copy when TCP preflight aborted generation.

    Raw ``aggregate_x3`` may classify empty-parse X2 failures ahead of the BLOCKED narrative; for
    unreachable vLLM the authoritative blocker is the live provider gate (see
    ``competencies_live_provider_gate.json``). X2 sidecars remain on disk for forensics.
    """
    if not live_preflight_blocked:
        return x3
    remediation = [r for r in x3.required_remediation if not r.startswith("Fix failed X2 gates")]
    probe = "Restore reachable Qwen/vLLM endpoint (see competencies_live_provider_gate.json and stderr)."
    if probe not in remediation:
        remediation.insert(0, probe)
    return replace(
        x3,
        decisive_reason="Runtime generation is BLOCKED (BLOCKED_LIVE_PROVIDER / PROVIDER_UNAVAILABLE).",
        review_reason="",
        x2_failed_gates=[],
        required_remediation=remediation,
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


def retry_qwen_competency_restatement(
    messages: list[dict[str, str]],
    provider_payload: dict[str, Any],
    raw_output: str,
    parsed: dict[str, Any],
    bad_term: str,
    runtime_payload: dict[str, Any],
    allowed_fact_ids: set[str],
    *,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """One repair turn when a competency term copies a long bullet substring."""
    repair_messages = [
        *messages,
        {"role": "assistant", "content": raw_output},
        {
            "role": "user",
            "content": (
                f"DETERMINISTIC_REVISION: The term or phrase \"{bad_term}\" overlaps a canonical employment bullet. "
                "Rewrite ALL eight categories so every term is a short distinct noun phrase (max 5 words, under 48 characters) "
                "that does NOT contain any contiguous 18+ character substring copied from C0 candidate_facts / proof bullets. "
                "Keep bul_* source_fact_ids accurate. Return full JSON again with the same required keys; "
                "selected_fact_plan stub only (section_id, selection_method, required_fact_ids)."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": COMPETENCIES_QWEN_MAX_TOKENS}
    result = call_qwen_vllm(
        tag_reasoning_lane(repair_payload, LANE_KEY),
        artifact_dir=artifact_dir,
        run_id=run_id,
    )
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, parsed
    new_raw = result.raw_model_output
    new_parsed, _err = parse_model_json(new_raw)
    if new_parsed is None:
        return raw_output, parsed
    new_parsed = normalize_parsed_output(new_parsed, runtime_payload, allowed_fact_ids)
    if not isinstance(new_parsed.get("change_log"), list):
        new_parsed["change_log"] = []
    new_parsed["change_log"] = list(parsed.get("change_log") or []) + list(new_parsed.get("change_log") or [])
    new_parsed["change_log"].append(
        {"operation": "bullet_restatement_repair", "reason": "x2_no_bullet_outcome_restatement"},
    )
    return json.dumps(new_parsed, sort_keys=True, separators=(",", ":")), new_parsed


def run_competencies_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.dispatch.competencies_dispatch",
    print_output: bool = True,
) -> dict[str, Any]:
    from apps_rg.runtime.proof_pool_lane_integration import load_section_proof_for_lane

    pool, base, base_path, base_hash = load_section_proof_for_lane(
        section_id="competencies",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    bullet_rows = pool.bullet_rows
    allowed_fact_ids = pool.allowed_fact_ids
    selected_fact_plan = pool.selected_fact_plan
    pp_meta = pool.proof_pool_metadata
    bullet_lowers = [str(r.get("claim_text") or "").lower() for r in bullet_rows]
    companion_context = load_companion_context()
    resume_blob = build_resume_support_blob(bullet_rows, companion_context)
    c0_proof_blob = build_c0_proof_support_blob(bullet_rows)

    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
    )
    runtime_payload["proof_pool_metadata"] = pp_meta
    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    (artifact_dir / "companion_generated_sections.txt").write_text(companion_context or "(none)\n", encoding="utf-8")

    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )

    fact_lines = "\n".join(
        f"- {row['fact_id']}: {row['claim_text']}"
        + (f" | tech: {', '.join(row['technologies'])}" if row.get("technologies") else "")
        for row in bullet_rows
    )
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_competencies_prompt(
        runtime_payload,
        companion_context=companion_context,
        fact_lines=fact_lines,
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
            "allowed_fact_ids": sorted(str(x) for x in allowed_fact_ids),
        },
    )

    provider_raw_output: str | None = None
    provider_request_data = None
    provider_result_data = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"
    live_preflight_blocked = False

    provider_req, provider_payload = build_qwen_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=COMPETENCIES_QWEN_MAX_TOKENS,
        timeout_seconds=competencies_vllm_chat_timeout_s(),
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_request_data.get("model") or DEFAULT_QWEN_MODEL)
    _run_id = str(runtime_payload.get("run_id") or "")
    if effective_offline_contract_stub_enabled():
        stub_raw = json.dumps(build_mock_output(runtime_payload), sort_keys=True, separators=(",", ":"))
        result = synthetic_qwen_provider_result(raw_model_output=stub_raw, requested_model=req_model)
    elif str(args.provider).strip().lower() == "qwen_vllm":
        base_url = str(provider_request_data.get("provider_url") or "")
        pre_timeout = competencies_vllm_preflight_timeout_s()
        print(
            f"[competencies] live qwen_vllm: shared HTTP /v1/models preflight base_url={base_url!r} "
            f"model={req_model!r} timeout_s={pre_timeout}",
            file=sys.stderr,
            flush=True,
        )
        if competencies_vllm_preflight_disabled():
            print(
                "[competencies] WARNING: APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_DISABLE is set — "
                "skipping HTTP models preflight in slice (not recommended for unattended runs).",
                file=sys.stderr,
                flush=True,
            )
        result = call_qwen_vllm(
            tag_reasoning_lane(provider_payload, LANE_KEY),
            artifact_dir=artifact_dir,
            run_id=_run_id or None,
        )
        if getattr(result, "apps_rg_qwen_preflight_blocked", False):
            live_preflight_blocked = True
            snap = getattr(result, "apps_rg_last_probe_snapshot", None)
            write_json(
                artifact_dir / "competencies_live_provider_gate.json",
                live_provider_gate_audit_payload_failure(
                    provider_base_url=base_url,
                    preflight_detail=str(result.exact_provider_error or "http_models_preflight_failed"),
                    timeout_s=pre_timeout,
                    probe_snapshot=dict(snap) if isinstance(snap, dict) else None,
                ),
            )
            print(
                f"{STATUS_BLOCKED_LIVE_PROVIDER}: {REASON_PROVIDER_UNAVAILABLE} — "
                f"HTTP /v1/models preflight blocked for {base_url!r}",
                file=sys.stderr,
                flush=True,
            )
    else:
        result = call_qwen_vllm(
            tag_reasoning_lane(provider_payload, LANE_KEY),
            artifact_dir=artifact_dir,
            run_id=_run_id or None,
        )
    provider_result_data = result.to_dict()
    if live_preflight_blocked:
        provider_result_data = {
            **provider_result_data,
            "live_provider_gate_status": STATUS_BLOCKED_LIVE_PROVIDER,
            "provider_unreachable_reason": REASON_PROVIDER_UNAVAILABLE,
            "live_provider_gate_artifact": "competencies_live_provider_gate.json",
        }
    raw_output = result.raw_model_output
    provider_raw_output = raw_output
    raw_model_output_original = raw_output
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    runtime_generation_status = result.runtime_generation_status
    if result.runtime_generation_status in ("REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS):
        parsed, parse_error = parse_model_json(raw_model_output_original)
        if parsed is None:
            raw_model_output_original, parsed, parse_error = retry_qwen_for_parse(
                messages,
                provider_payload,
                raw_model_output_original,
                parse_error,
                artifact_dir=artifact_dir,
                run_id=_run_id or None,
            )
        if parsed is not None:
            parsed = normalize_parsed_output(parsed, runtime_payload, allowed_fact_ids)
            comps = parsed.get("competencies") or []
            if isinstance(comps, list) and len(comps) >= 8 and not parsed.get("claim_ledger"):
                rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
                clog = list(parsed.get("change_log") or [])
                clog.append(
                    {
                        "operation": "rebuild_claim_ledger_after_length_truncation",
                        "reason": "deterministic",
                    }
                )
                parsed["change_log"] = clog
            raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
            bad_term = find_bullet_restatement_term(parsed.get("competencies") or [], bullet_lowers)
            if bad_term:
                raw_output, parsed = retry_qwen_competency_restatement(
                    messages,
                    provider_payload,
                    raw_output,
                    parsed,
                    bad_term,
                    runtime_payload,
                    allowed_fact_ids,
                    artifact_dir=artifact_dir,
                    run_id=_run_id or None,
                )
                if parsed is not None:
                    raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        else:
            raw_output = raw_model_output_original
    else:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    if parsed is not None:
        collapse_duplicate_competency_terms(parsed, bullet_rows, resume_blob)
        repair_structured_competencies_source_facts(
            parsed,
            allowed_fact_ids=allowed_fact_ids,
            resume_support_blob_lower=c0_proof_blob,
        )
        coerce_structured_competencies_resume_support(
            parsed,
            bullet_rows,
            c0_proof_blob,
            bullet_lowers,
            allowed_fact_ids=allowed_fact_ids,
        )
        dedupe_structured_competency_terms(parsed)
        reduce_competency_keyword_stuffing(parsed)
        expand_structured_competencies_min_two_terms(
            parsed,
            bullet_rows=bullet_rows,
            allowed_fact_ids=allowed_fact_ids,
            resume_support_blob_lower=c0_proof_blob,
            bullet_texts_lower=bullet_lowers,
        )
        dedupe_structured_competency_terms(parsed)
        reduce_competency_keyword_stuffing(parsed)
        canonicalize_competency_terms_for_proof(parsed, allowed_fact_ids=allowed_fact_ids)
        coerce_structured_competencies_resume_support(
            parsed,
            bullet_rows,
            c0_proof_blob,
            bullet_lowers,
            allowed_fact_ids=allowed_fact_ids,
        )
        dedupe_structured_competency_terms(parsed)
        rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
        prune_claim_ledger_bullet_paste(parsed)
        raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))

    competencies = list((parsed or {}).get("competencies") or [])
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    display_text = competencies_display_text(competencies)
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output or "",
        lane_profile="competencies",
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
        claim_id_prefix="competencies_claim",
    )
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)
    coverage = build_sentence_claim_coverage(display_text, claim_ledger, allowed_fact_ids)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    effective_sfp_c = (parsed or {}).get("selected_fact_plan") if isinstance(parsed, dict) else None
    if not isinstance(effective_sfp_c, dict):
        effective_sfp_c = selected_fact_plan
    write_json(artifact_dir / "selected_fact_plan.json", effective_sfp_c)
    competency_group_fact_support: list[dict[str, Any]] = []
    for cat in competencies:
        if isinstance(cat, dict):
            competency_group_fact_support.append(
                {
                    "category_label": cat.get("category_label"),
                    "source_fact_ids": list(cat.get("source_fact_ids") or []),
                }
            )
    req_id_c = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    jd_alignment_final = merge_jd_alignment((parsed or {}).get("jd_alignment") if isinstance(parsed, dict) else None)
    trace_rr_c = artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="competencies",
        run_id=str(runtime_payload["run_id"]),
        request_id=req_id_c,
        trace_root=trace_rr_c,
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=effective_sfp_c,
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        jd_text=str(runtime_payload.get("jd_text") or ""),
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        briefing_text=str(runtime_payload.get("briefing") or ""),
        jd_alignment=jd_alignment_final,
        extra_section_fields={"competency_group_fact_support": competency_group_fact_support},
    )
    from apps_rg.runtime.proof_pool_lane_integration import apply_proof_pool_to_usage_ledger

    write_json(
        artifact_dir / "section_input_usage_ledger.json",
        apply_proof_pool_to_usage_ledger(usage_doc, pool),
    )

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_allowed_mock = bool(args.mock_judges and getattr(args, "allow_test_mock_judges", False))
    judge_mode = "mocked" if judge_allowed_mock else "blocked_if_unavailable"
    x1d = [
        j.to_dict()
        for j in run_competencies_judges(
            competencies=competencies,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            companion_context=companion_context,
            mode=judge_mode,
            artifact_base=artifact_dir,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active = bool(str(pp_x2.get("proof_pool_type") or "").strip())

    x2 = [
        g.to_dict()
        for g in run_competencies_x2_gates(
            competencies=competencies,
            parsed_output=parsed,
            claim_ledger=claim_ledger,
            jd_text=args.jd_text,
            briefing_text=getattr(args, "briefing", "") or "",
            bullet_texts_lower=bullet_lowers,
            resume_support_blob=resume_blob,
            c0_proof_blob=c0_proof_blob,
            allowed_fact_ids=allowed_fact_ids,
            runtime_generation_status=runtime_generation_status,
            cli_provider=args.provider,
            live_preflight_blocked=live_preflight_blocked,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
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
        "section_id": "competencies",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "competencies": competencies,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": jd_alignment_final,
        "excluded_jd_skills": (parsed or {}).get("excluded_jd_skills") or [],
        "removed_or_rewritten_terms": (parsed or {}).get("removed_or_rewritten_terms") or [],
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
        "text_claim_coverage": coverage,
    }
    write_json(artifact_dir / "competencies_output.json", competencies)
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        attach_reasoning_to_prompt_trace(
            {
                "runtime_path": trace_runtime_path,
                "prompt_id": PROMPT_ID,
                "provider": args.provider,
                "temperature": args.temperature,
                "section_prompt_adapter": True,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "compiler_template_id": section_compiled.artifact.template_id,
            },
            provider=args.provider,
            lane_key=LANE_KEY,
            provider_result_data=provider_result_data if isinstance(provider_result_data, dict) else None,
        ),
    )

    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2)
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    product_quality_status, product_quality_reason = infer_product_quality(runtime_generation_status, x2)

    x3 = aggregate_x3(
        resume_display_text=display_text or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
        judge_required_for_allow=False,
    )
    x3 = clarify_x3_for_competencies_live_provider_preflight(
        x3,
        live_preflight_blocked=live_preflight_blocked,
    )
    write_json(artifact_dir / "x3_disposition.json", x3.to_dict())

    bundle = compute_lane_proof_bundle(
        args,
        section_id="competencies",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
    )
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    jd_al_out = jd_alignment_final
    section_agg: dict[str, Any] = {
        "schema_version": "1",
        "section_id": "competencies",
        "canonical_aggregation_note": (
            "CANONICAL_DOWNSTREAM_AGGREGATION_INPUT — use this file as the sole bundle-shaped join surface "
            "for competencies (display_lines, competencies[], claim_ledger, proof-boundary flags, X2/X3 refs). "
            "competencies_output.json is legacy competencies[] only; provider_response.json is transport-only diagnostic."
        ),
        "artifact_role_bundle": {
            "competencies_section_output.json": "canonical_downstream_aggregation_input",
            "competencies_output.json": "legacy_competencies_array_only",
            "provider_response.json": "diagnostic_transport_metadata_only",
            "l2_output.json": "rich_runtime_section_object_with_refs",
        },
        "display_lines": [ln for ln in (display_text or "").split("\n") if str(ln).strip()],
        "competencies": competencies,
        "claim_ledger": claim_ledger,
        "selected_fact_ids": sorted(str(x) for x in allowed_fact_ids),
        "targeting_only": bool(jd_al_out.get("targeting_only")),
        "jd_used_as_proof": bool(jd_al_out.get("jd_used_as_proof")),
        "briefing_used_as_proof": bool(jd_al_out.get("briefing_used_as_proof")),
        "companion_context_used_as_proof": bool(jd_al_out.get("companion_context_used_as_proof")),
        "runtime_generation_status": runtime_generation_status,
        "x2_gate_outputs_ref": _artifact_repo_rel(artifact_dir / "x2_gate_outputs.json", REPO_ROOT),
        "x3_disposition_ref": _artifact_repo_rel(artifact_dir / "x3_disposition.json", REPO_ROOT),
        "section_input_usage_ledger_ref": _artifact_repo_rel(
            artifact_dir / "section_input_usage_ledger.json",
            REPO_ROOT,
        ),
        "proof_eligible": bool(bundle.get("proof_eligible")),
        "proof_scope": bundle.get("proof_scope"),
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    write_json(artifact_dir / "competencies_section_output.json", section_agg)
    l2_output["competencies_section_output_ref"] = _artifact_repo_rel(
        artifact_dir / "competencies_section_output.json",
        REPO_ROOT,
    )
    write_json(artifact_dir / "l2_output.json", l2_output)

    l6_temp = float(args.temperature)
    l6_max = COMPETENCIES_QWEN_MAX_TOKENS
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    section_agg["l6_shadow_eval_package_ref"] = _artifact_repo_rel(
        artifact_dir / "l6_shadow_eval_package.json",
        REPO_ROOT,
    )
    section_agg["l6_shadow_learning_ref"] = _artifact_repo_rel(
        artifact_dir / "l6_shadow_learning.json",
        REPO_ROOT,
    )
    _prop_path = artifact_dir / "l6_future_run_proposals.json"
    if _prop_path.is_file():
        section_agg["l6_future_run_proposals_ref"] = _artifact_repo_rel(_prop_path, REPO_ROOT)
    _rca_path = artifact_dir / "l6_shadow_rca_sketch.json"
    if _rca_path.is_file():
        section_agg["l6_shadow_rca_sketch_ref"] = _artifact_repo_rel(_rca_path, REPO_ROOT)
    write_json(artifact_dir / "competencies_section_output.json", section_agg)

    l2_output["l6_shadow_eval_package_ref"] = section_agg["l6_shadow_eval_package_ref"]
    l2_output["l6_shadow_learning_ref"] = section_agg["l6_shadow_learning_ref"]
    if section_agg.get("l6_future_run_proposals_ref"):
        l2_output["l6_future_run_proposals_ref"] = section_agg["l6_future_run_proposals_ref"]
    if section_agg.get("l6_shadow_rca_sketch_ref"):
        l2_output["l6_shadow_rca_sketch_ref"] = section_agg["l6_shadow_rca_sketch_ref"]
    write_json(artifact_dir / "l2_output.json", l2_output)

    rl2 = {
        "provider_attempted": args.provider,
        "runtime_generation_status": runtime_generation_status,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "raw_model_output": raw_output,
        "raw_model_output_provider": provider_raw_output,
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    attach_lane_proof_bundle_fields(
        rl2,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )

    _smr_co = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "competencies",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": None,
        "claim_ledger_hash": None,
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": product_quality_status,
        "x2_failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        "x3_code": x3.x3_code,
        "proof_eligible": bundle["proof_eligible"],
        "judge_proof_eligible": bundle["judge_proof_eligible"],
    }
    merge_normalized_srfs_reporting_into_dict(
        _smr_co,
        section_id="competencies",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_co)

    write_json(
        artifact_dir / "real_l2_generation_result.json",
        rl2,
    )

    comp_json = json.dumps(competencies, separators=(",", ":"), ensure_ascii=False)
    lines = [
        "COMPETENCIES_OUTPUT:",
        comp_json,
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
    status_hint = (
        "PASS_RUNTIME_PROOF_ELIGIBLE" if bundle["proof_eligible"] else "PASS_NONCERTIFYING_RUNTIME_PROOF"
    )
    lines.extend(
        [
            "",
            "RUNTIME_PROOF_SUMMARY:",
            f"RUNTIME_GENERATION_STATUS: {runtime_generation_status}",
            f"STATUS: {status_hint}",
            f"PRODUCT_STATUS: {x3.x3_code}",
            f"PROOF_ELIGIBLE: {str(bundle['proof_eligible']).lower()}",
            "NOTE: STATUS PASS alone never implies X3 ALLOW or certification — check PRODUCT_STATUS and PROOF_ELIGIBLE.",
            f"CANONICAL_AGGREGATION_INPUT: competencies_section_output.json ({_artifact_repo_rel(artifact_dir / 'competencies_section_output.json', REPO_ROOT)})",
            "",
            "L6_SHADOW_EVAL_PACKAGE:",
            str(artifact_dir / "l6_shadow_eval_package.json"),
            "offline_only=true",
            "l6_shadow_learning=" + str(artifact_dir / "l6_shadow_learning.json"),
        ]
    )
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
        section_id="competencies",
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
    )
    if allow_non_allow_exit_zero_ok(args):
        exit_code = 0
    else:
        exit_code = 0 if x3.x3_code == "X3_ALLOW" else 2
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "runtime_payload": runtime_payload,
        "x3": x3,
        "output_text": output_text,
        "exit_code": exit_code,
        "runtime_generation_status": runtime_generation_status,
        "competencies": competencies,
    }


def run_dispatch(args: argparse.Namespace) -> int:
    """Argparse helper kept for import parity; ``__main__`` exits deprecated — use ``apps_rg`` CLI."""
    if mock_judges_blocked_before_run(args):
        emit_mock_judges_blocked_stderr(dispatcher_label="competencies_dispatch")
        return MOCK_JUDGES_REJECT_EXIT_CODE
    ctx = run_competencies_execution(
        args,
        artifact_dir_override=None,
        trace_runtime_path="apps_rg.runtime.dispatch.competencies_dispatch",
        print_output=True,
    )
    return int(ctx["exit_code"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run apps_rg competencies runtime seam.")
    parser.add_argument(
        "--provider",
        choices=["qwen_vllm"],
        default="qwen_vllm",
        help="Generation provider (qwen_vllm only). Offline tests: set APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1.",
    )
    parser.add_argument("--temperature", type=float, default=COMPETENCIES_TEMP_DEFAULT)
    parser.add_argument("--x1d-judges", default="gemini_pro,openai_chatgpt,anthropic_claude")
    parser.add_argument(
        "--mock-judges",
        action="store_true",
        help=(
            "Use mocked judge rows for contract-test plumbing only. Blocked unless paired with "
            "`--allow-test-mock-judges`."
        ),
    )
    parser.add_argument(
        "--allow-test-mock-judges",
        action="store_true",
        help=(
            "Test-only hatch: allow `--mock-judges`. Emits judge_proof_eligible=false and proof_eligible=false "
            "(never runtime certification)."
        ),
    )
    parser.add_argument("--target-title", default=TARGET_TITLE_DEFAULT)
    parser.add_argument("--target-company", default=TARGET_COMPANY_DEFAULT)
    parser.add_argument("--jd-text", default=JD_TEXT_DEFAULT)
    parser.add_argument("--briefing", default=BRIEFING_DEFAULT)
    parser.add_argument(
        "--allow-non-allow-exit-zero",
        action="store_true",
        help="Exit 0 for inspection despite X3≠ALLOW — does not bypass mock-judge blocks.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    return run_dispatch(build_parser().parse_args(argv))


if __name__ == "__main__":
    from apps_rg.runtime.deprecated_runtime_cli import exit_deprecated_dispatch_cli

    raise SystemExit(exit_deprecated_dispatch_cli(section="competencies"))
