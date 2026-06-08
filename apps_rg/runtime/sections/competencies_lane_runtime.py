"""App-local competencies execution seam (compile → provider → X2 → X1D → X3 → L6).

**Primary runtime entry:** ``python -m apps_rg --section competencies`` via
``apps_rg.runtime.sections.competencies_lane`` (canonical selected-section path).

**Deprecated:** ``python -m apps_rg.runtime.sections.competencies_lane_runtime`` — exits with guidance;
do not use for runtime proof.

Shared helpers (``compile_competencies_prompt``, ``run_competencies_execution``) remain here for PA and
orchestration; they are not a standalone product entrypoint.
"""
from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
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

from apps_rg.runtime.competencies_proof_boundary import merge_jd_alignment
from apps_rg.runtime.dispatch.competencies_pa import compile_competencies_prompt
from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    classify_ledger_parse_state,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.sections.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.sections.companion_lane_context import (
    COMPANION_LANES,
    build_c0_proof_support_blob,
    build_resume_support_blob,
    load_companion_context,
)
from apps_rg.runtime.sections.competencies_lane_defaults import (
    BRIEFING_DEFAULT,
    COMPETENCIES_MAX_OUTPUT_TOKENS,
    COMPETENCIES_TEMP_DEFAULT,
    JD_TEXT_DEFAULT,
    LANE_KEY,
    PROMPT_ID,
    REPO_ROOT,
    TARGET_COMPANY_DEFAULT,
    TARGET_TITLE_DEFAULT,
)
from apps_rg.runtime.sections.competencies_term_phrase import term_phrase
from apps_rg.runtime.sections.lane_artifact_io import sha16, write_json
from apps_rg.runtime.sections.lane_base_resume import load_base_resume
from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
from apps_rg.runtime.exit.competencies_x3 import (
    X3Disposition,
    aggregate_x3,
    clarify_x3_for_competencies_live_provider_preflight,
)
from apps_rg.runtime.judges.competencies_x1d import run_competencies_judges
from apps_rg.runtime.providers.competencies_live_provider_gate import (
    REASON_PROVIDER_UNAVAILABLE,
    STATUS_BLOCKED_LIVE_PROVIDER,
    competencies_vllm_preflight_disabled,
    competencies_vllm_chat_timeout_s,
    competencies_vllm_preflight_timeout_s,
    live_provider_gate_audit_payload_failure,
)
from apps_rg.runtime.sections.section_generation import SECTION_MODEL_ID, build_section_request
from apps_rg.runtime.sections.section_generation import generate_section, tag_reasoning_lane
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
)
from apps_rg.runtime.sections.selected_role_fact_set import merge_normalized_srfs_reporting_into_dict

def _artifact_repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


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


def build_selected_fact_plan(facts: list[dict[str, Any]], required_ids: list[str]) -> dict[str, Any]:
    return {
        "section_id": "competencies",
        "selection_method": "canonical_base_resume_employment_bullets",
        "facts": facts,
        "required_fact_ids": required_ids,
    }


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

            repaired_sids: list[str] = []
            for x in raw_t.get("source_fact_ids") or []:
                base = _fix_fact_id_typos(str(x), allowed_fact_ids).split("_metric_")[0]
                if base in allowed_fact_ids and base not in repaired_sids:
                    repaired_sids.append(base)
            if not repaired_sids:
                repaired_sids = [resolved]
            if raw_t.get("source_fact_ids") != repaired_sids:
                raw_t["source_fact_ids"] = repaired_sids
            if str(raw_t.get("source_fact_id", "")).split("_metric_")[0] not in allowed_fact_ids:
                raw_t["source_fact_id"] = repaired_sids[0]


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
    """Expand structured categories below executive rigor minimum (3 terms per category).

    Addresses ``x2_competencies_min_items_per_category`` / ``x2_competency_format_category_colon_terms``
    without inventing canonical fact ids — fragments are restricted to bullet ``technologies`` and short
    claim splits (see :func:`_candidate_phrases_for_category`).
    """
    from apps_rg.runtime.sections.competencies_rigor import MIN_ITEMS_PER_CATEGORY

    min_terms = MIN_ITEMS_PER_CATEGORY

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

        while _nonempty_terms_total(terms_raw) < min_terms:
            need_before = _nonempty_terms_total(terms_raw)

            validated_set: set[str] = set()
            for sr in cat.get("source_fact_ids") or []:
                x = _fix_fact_id_typos(str(sr))
                fid = x.split("_metric_")[0]
                if fid in allowed_fact_ids:
                    validated_set.add(fid)
            validated = sorted(validated_set)
            if not validated:
                break

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
                row = rows_by_id.get(validated[0]) or {}
                for tech in row.get("technologies") or []:
                    cand = str(tech).strip()
                    if not cand or _sentence_like_term(cand):
                        continue
                    words = cand.split()
                    if len(words) > 6:
                        cand = " ".join(words[:4])
                    if not _novel_term_vs_seen(cand, combined_seen):
                        continue
                    if term_primary_support_overlap(cand, validated[0], resume_support_blob_lower):
                        eligible.append((len(cand), cand.lower(), cand, validated[0]))
                        break
                if not eligible:
                    claim = str(row.get("claim_text") or "").strip()
                    for chunk in re.split(r"[,;]\s*|\s+and\s+", claim):
                        cand = chunk.strip()
                        if not cand or _sentence_like_term(cand):
                            continue
                        wc = len(cand.split())
                        if wc < 2 or wc > 6:
                            continue
                        if not _novel_term_vs_seen(cand, combined_seen):
                            continue
                        if term_primary_support_overlap(cand, validated[0], resume_support_blob_lower):
                            eligible.append((len(cand), cand.lower(), cand, validated[0]))
                            break
            if not eligible:
                break
            eligible.sort()
            chosen = eligible[0]
            _, _, phrase, sfid = chosen
            append_term = {"text": phrase, "source_fact_id": sfid, "source_fact_ids": [sfid]}
            wr = parsed.setdefault("removed_or_rewritten_terms")
            if not isinstance(wr, list):
                wr = []
                parsed["removed_or_rewritten_terms"] = wr
            changelog.append(
                {
                    "operation": "expand_structured_competency_min_terms",
                    "reason": (
                        f"structured category below {min_terms} terms — appended grounded phrase from "
                        "validated bullet technologies/fragments"
                    ),
                    "category_label": cat.get("category_label"),
                    "phrase": phrase,
                    "source_fact_id": sfid,
                }
            )
            wr.append(f"expand min-terms: +{phrase!r} (@{sfid}) in {cat.get('category_label', '?')}")
            terms_raw.append(append_term)
            cat["terms"] = terms_raw
            global_seen.add(phrase.lower().strip().rstrip("."))
            if _nonempty_terms_total(terms_raw) <= need_before:
                break


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
    from apps_rg.runtime.sections.competencies_certification_contract import (
        sanitize_competencies_no_certification_category,
    )

    sanitized, cert_log = sanitize_competencies_no_certification_category(out.get("competencies") or [])
    out["competencies"] = sanitized
    if cert_log:
        cl = out.get("change_log")
        if not isinstance(cl, list):
            cl = []
        out["change_log"] = [*cl, *cert_log]
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
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": COMPETENCIES_MAX_OUTPUT_TOKENS}
    result = generate_section(
        tag_reasoning_lane(repair_payload, LANE_KEY),
        artifact_dir=artifact_dir,
        run_id=run_id,
    )
    if result.runtime_generation_status != "REAL_LLM":
        return raw_output, None, parse_error
    new_raw = result.raw_model_output
    new_parsed, new_err = parse_model_json(new_raw)
    return new_raw, new_parsed, new_err


# Offline SRFS stub: three distinct short phrases per category; no token may repeat >5× globally
# (x2_no_keyword_stuffing) after deterministic repair — avoids ``governed capability cluster`` templates.
_SRFS_STUB_TERM_TRIPLES: tuple[tuple[str, str, str], ...] = (
    ("observability posture", "trace sampling", "metric cadence"),
    ("routing policy", "mesh coordination", "budget caps"),
    ("retrieval discipline", "index hygiene", "rank tuning"),
    ("lifecycle standardization", "release cadence", "defect triage"),
    ("platform tiers", "data planes", "gateway hardening"),
    ("security baselines", "access reviews", "vault rotation"),
    ("cost governance", "capacity planning", "quota envelopes"),
    ("team leadership", "stakeholder alignment", "roadmap framing"),
)


def build_mock_output(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    def _term_obj(phrase: str, fid: str) -> dict[str, Any]:
        return {"text": phrase, "source_fact_id": fid, "source_fact_ids": [fid]}

    raw_allowed = [str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])]
    allowed = [x for x in raw_allowed if "_metric_" not in x]
    if not allowed and raw_allowed:
        allowed = sorted({x.split("_metric_", 1)[0] for x in raw_allowed})
    if not allowed:
        allowed = ["proof_pool_placeholder"]
    plan_facts = list((runtime_payload.get("selected_fact_plan") or {}).get("facts") or [])
    facts_by_id = {
        str(f.get("fact_id") or "").strip(): f for f in plan_facts if str(f.get("fact_id") or "").strip()
    }

    def _stub_terms_for_fact(fid: str, fallback: tuple[str, str, str]) -> list[dict[str, Any]]:
        row = facts_by_id.get(fid) or {}
        phrases: list[str] = []
        for tech in row.get("technologies") or []:
            t = str(tech).strip()
            if not t:
                continue
            words = t.split()
            if 2 <= len(words) <= 6:
                phrases.append(t)
            elif len(words) > 6:
                phrases.append(" ".join(words[:4]))
        if len(phrases) < 2:
            claim = str(row.get("claim_text") or "").strip()
            for chunk in re.split(r"[,;]\s*|\s+and\s+", claim):
                c = chunk.strip()
                wc = len(c.split())
                if 2 <= wc <= 6:
                    phrases.append(c)
                if len(phrases) >= 3:
                    break
        fb0, fb1, fb2 = fallback
        while len(phrases) < 2:
            phrases.append((fb0, fb1, fb2)[len(phrases) % 3])
        return [_term_obj(p, fid) for p in phrases[:3]]

    competencies_out: list[dict[str, Any]] = []
    for i in range(8):
        fid = allowed[i % len(allowed)]
        fallback = _SRFS_STUB_TERM_TRIPLES[i % len(_SRFS_STUB_TERM_TRIPLES)]
        competencies_out.append(
            {
                "category_label": f"Graph Competency Area {i + 1}",
                "terms": _stub_terms_for_fact(fid, fallback),
                "source_fact_ids": [fid],
            }
        )
    ledger_out: list[dict[str, Any]] = []
    for cat in competencies_out:
        ids = list(cat["source_fact_ids"])
        for t in cat["terms"]:
            ts = term_phrase(t)
            if not ts:
                continue
            if isinstance(t, dict) and t.get("source_fact_id") is not None:
                sid = _fix_fact_id_typos(str(t["source_fact_id"])).split("_metric_")[0]
                ledger_out.append({"claim_text": ts, "source_fact_ids": [sid]})
            else:
                ledger_out.append({"claim_text": ts, "source_fact_ids": list(ids)})
    return {
        "competencies": competencies_out,
        "selected_fact_plan": runtime_payload["selected_fact_plan"],
        "claim_ledger": ledger_out,
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
        pass_reason="REAL_LLM output passed all deterministic competencies gates.",
    )


def write_x2_gate_outputs(
    path: Path,
    gates: list[dict[str, Any]],
    *,
    section_id: str | None = "competencies",
) -> None:
    if section_id:
        from apps_rg.runtime.sections.section_x2_gate_outputs import (
            write_section_x2_gate_outputs,
        )

        write_section_x2_gate_outputs(path.parent, section_id, gates)
        return
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
                "Rewrite all categories (6–8 per product shape) so every term is a short distinct noun phrase (max 5 words, under 48 characters) "
                "that does NOT contain any contiguous 18+ character substring copied from C0 candidate_facts / proof bullets. "
                "Keep bul_* source_fact_ids accurate. Return full JSON again with the same required keys; "
                "selected_fact_plan stub only (section_id, selection_method, required_fact_ids)."
            ),
        },
    ]
    repair_payload = {**provider_payload, "messages": repair_messages, "max_tokens": COMPETENCIES_MAX_OUTPUT_TOKENS}
    result = generate_section(
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


"""Compat lazy re-export — canonical: apps_rg.runtime.sections.competencies_lane_execution."""

_LANE_EXEC_EXPORTS = frozenset({"run_competencies_execution", "run_competencies_lane_execution"})


def __getattr__(name: str) -> Any:
    if name in _LANE_EXEC_EXPORTS:
        from apps_rg.runtime.sections import competencies_lane_execution as _lane

        return getattr(_lane, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | _LANE_EXEC_EXPORTS)



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run apps_rg competencies runtime seam.")
    parser.add_argument(
        "--provider",
        choices=["external_claude"],
        default="external_claude",
        help="Generation provider (qwen_vllm only). Live vLLM required; offline contract stub is disabled.",
    )
    parser.add_argument("--temperature", type=float, default=COMPETENCIES_TEMP_DEFAULT)
    parser.add_argument(
        "--x1d-judges",
        default="gemini_pro",
        help="Single X1D judge for competencies (graph pool selector row; not a triple panel).",
    )
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



