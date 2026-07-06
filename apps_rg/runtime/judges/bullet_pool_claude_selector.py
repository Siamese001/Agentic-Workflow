"""Pool selector: score self-consistency candidates and pick per-slot winners."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

from apps_rg.runtime.judges.executive_summary_x1d import (
    PROVIDERS,
    JudgeOutput,
    _artifact_path,
    _extract_anthropic_message_text,
    _extract_json_from_text,
    _is_openai_gpt5_chat_model,
)
from apps_rg.runtime.env_bootstrap import bootstrap_apps_rg_env
from apps_rg.runtime.reasoning.bullet_lane_self_consistency import SelfConsistencyPath
from apps_rg.runtime.judges.employment_bullet_judge_rubric import pool_selector_scoring_instruction
from apps_rg.runtime.reasoning.competencies_graph_pool import (
    COMPETENCIES_CANDIDATE_CATEGORY_COUNT,
    COMPETENCIES_FINAL_CATEGORY_COUNT,
    COMPETENCIES_SC_PATH_COUNT,
    COMPETENCIES_MIN_CATEGORY_COUNT,
    build_competencies_rejected_neighbor_audit,
    high_signal_competencies_selection_score,
    merge_competencies_graph_pool_top_eight,
    min_competencies_selection_score,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    FINAL_BULLET_COUNT,
    is_employment_bullet_lane,
    min_selection_score_for_lane,
    sc_path_count_for_lane,
)
from apps_rg.runtime.sections.executive_summary_context_limits import (
    resolve_bullet_selector_briefing_max_chars,
    resolve_bullet_selector_jd_max_chars,
)
from apps_rg.runtime.section_model_limits import (
    resolve_selector_provider_model,
    selector_role_for_section,
)

SlotKind = Literal["bullets", "competencies"]

# Bug:BulletPoolSelectorRubricSchemaDrift (AIG attempt4 + patch-run 2, 2026-06-11): the selector
# previously sent build_x1d_judge_system_prompt(compact=True) as its system prompt. That prompt's
# JUDGE_COMPACT_OUTPUT block hard-mandates "Return ONLY one compact JSON object" in the GRADE_ONLY
# rubric shape ({"score_scale", ..., "dimension_verdicts"}), contradicting the user prompt's
# {"selections": [...]} schema. Claude stochastically resolved the conflict by emitting
# the rubric object — alone (zero selections, silent MODEL_BACKED degradation) or followed by the
# selections object as a SECOND top-level JSON object (unparseable by _extract_json_from_text →
# BLOCKED_RESPONSE_PARSE_ERROR → fallback_first_complete_path → X3_BLOCK). The selector is NOT a
# rubric judge (see _call_anthropic_pool_selector docstring) — anchor its own output schema.
POOL_SELECTOR_SYSTEM_PROMPT = (
    "You are a strict pool SELECTOR for resume bullet/competency candidates - not a grading "
    'judge. Return ONLY one compact JSON object whose top-level keys are exactly "selections" '
    'and "pool_summary", following the schema in the user message. Do NOT return rubric or '
    "verdict JSON: no score_scale, no threshold, no dimension_verdicts, no findings. "
    "No markdown fences, no prose before or after the JSON object."
)

# W3: the Claude pool selector is itself a live external call inside the competencies/employment
# orchestration. Employment lanes keep the ordinary selector budget; the competencies graph pool
# gets the same bounded long-form budget as competencies generation because it ranks a larger
# structured candidate set. Operators can still opt in via env, bounded by the shared provider ceiling.
DEFAULT_POOL_SELECTOR_TIMEOUT_SECONDS = 90.0
DEFAULT_COMPETENCIES_POOL_SELECTOR_TIMEOUT_SECONDS = 240.0
SELECTOR_TIMING_RECEIPT_FILENAME = "bullet_pool_claude_selector_timing.json"


def pool_selector_timeout_s(*, default_seconds: float | None = None) -> float:
    """Effective wall-clock budget (seconds) for the Claude pool selector HTTP call.

    Reads ``APPS_RG_POOL_SELECTOR_TIMEOUT_SECONDS`` (default 90s unless the caller passes a
    lane-specific default), floored at 30s and bounded by the shared
    ``external_provider_timeout_max_s`` ceiling. A malformed value falls back to the default rather
    than failing the call.
    """
    from apps_rg.runtime.providers.external_provider import external_provider_timeout_max_s

    raw = os.environ.get("APPS_RG_POOL_SELECTOR_TIMEOUT_SECONDS", "").strip()
    ceiling = external_provider_timeout_max_s()
    default = DEFAULT_POOL_SELECTOR_TIMEOUT_SECONDS if default_seconds is None else float(default_seconds)
    if not raw:
        return max(30.0, min(default, ceiling))
    try:
        return max(30.0, min(float(raw), ceiling))
    except (TypeError, ValueError):
        return max(30.0, min(default, ceiling))


def _write_selector_timing_receipt(artifact_dir: Path | None, doc: dict[str, Any]) -> None:
    """Honest selector lifecycle receipt — written for started/finished/error/timeout alike, so a
    selector timeout is visibly distinct from a parse failure or a provider-unavailable block."""
    if artifact_dir is None:
        return
    try:
        (artifact_dir / SELECTOR_TIMING_RECEIPT_FILENAME).write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError:  # guardian: allow-silent-swallow -- diagnostic receipt is best-effort, never fatal
        pass


@dataclass(frozen=True)
class PoolSelectionResult:
    merged_parsed: dict[str, Any]
    selections: list[dict[str, Any]]
    judge_output: JudgeOutput | None
    selection_mode: str
    source_path_by_slot: dict[str, int]
    rejected_neighbor_audit: dict[str, Any] | None = None


class PoolSelectorUnavailableError(RuntimeError):
    """Raised when the selector cannot produce a real selection."""


def _first_path_failure_detail(paths: list[SelfConsistencyPath]) -> str:
    for path in paths:
        result = getattr(path, "provider_result", None)
        provider_error = str(getattr(result, "exact_provider_error", "") or "").strip()
        if provider_error:
            return provider_error
        parse_error = str(getattr(path, "parse_error", "") or "").strip()
        if parse_error:
            return parse_error
    return ""


def _sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _bullet_by_id(parsed: dict[str, Any], bullet_id: str) -> dict[str, Any] | None:
    for row in parsed.get("bullets") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("bullet_id") or "").strip() == bullet_id:
            return row
    return None


def inject_positional_bullet_ids_into_pool(
    paths: list[SelfConsistencyPath],
    required_bullet_ids: tuple[str, ...] | None,
) -> int:
    """Assign bullet_id positionally to pool samples that omit it.

    Closes Bug:BulletPoolSelectorBulletIdMissing (Brown SVP full_resume_183cf9252e02 ibm_bullets
    X3_BLOCK loop). PROVIDER_MODEL self-consistency samples often emit bullets shaped
    ``{bullet_theme, bullet_text}`` without ``bullet_id``. ``_bullet_by_id`` then returns ``None``
    for every required slot, ``_format_bullet_pool`` writes ``[bid] MISSING`` for all 20 paths, and
    ``run_claude_bullet_pool_selection`` produces zero merged bullets — even though PROVIDER_MODEL's text
    is fully populated. We replicate the canonical positional fallback already in
    ``ibm_bullets_lane.normalize_parsed_output`` lines 268-270 / equivalents in unify_bullets
    so the selector sees a non-empty pool.

    Returns the number of bullets that received a positional bullet_id assignment.
    Mutates ``path.parsed`` rows in place. Safe to call when ``required_bullet_ids`` is None or
    empty (no-op) — selector callers that don't require slot mapping keep prior behavior.
    """
    if not required_bullet_ids:
        return 0
    injected = 0
    for path in paths:
        parsed = path.parsed if path is not None else None
        if not isinstance(parsed, dict):
            continue
        bullets = parsed.get("bullets")
        if not isinstance(bullets, list):
            continue
        for idx, row in enumerate(bullets):
            if not isinstance(row, dict):
                continue
            existing = str(row.get("bullet_id") or "").strip()
            if existing:
                continue
            if idx >= len(required_bullet_ids):
                break
            text = str(row.get("bullet_text") or "").strip()
            if not text:
                continue
            row["bullet_id"] = required_bullet_ids[idx]
            row.setdefault("bullet_id_origin", "positional_pool_fallback")
            injected += 1
    return injected


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _allowed_fact_ids_from_context(targeting_context: dict[str, Any] | None) -> set[str]:
    return set(_as_str_list((targeting_context or {}).get("allowed_fact_ids")))


def _source_id_allowed(source_id: str, allowed_fact_ids: set[str]) -> bool:
    sid = str(source_id or "").strip()
    if not sid:
        return False
    if not allowed_fact_ids:
        return True
    if sid in allowed_fact_ids:
        return True
    root = sid.split("_metric_", 1)[0]
    return root in allowed_fact_ids


def _candidate_source_ids(row: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    ids.extend(_as_str_list(row.get("source_fact_ids")))
    ids.extend(_as_str_list(row.get("source_fact_id")))
    return ids


def _filter_claim_ledger_for_allowed_sources(
    claim_ledger: Any,
    allowed_fact_ids: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(claim_ledger, list):
        return []
    out: list[dict[str, Any]] = []
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        sids = _candidate_source_ids(row)
        if not allowed_fact_ids or (sids and all(_source_id_allowed(s, allowed_fact_ids) for s in sids)):
            out.append(dict(row))
    return out


def _selector_requires_valid_candidates(
    *,
    slot_kind: SlotKind,
    targeting_context: dict[str, Any] | None,
) -> bool:
    if slot_kind != "bullets":
        return False
    tc = targeting_context or {}
    return bool(tc.get("selector_requires_valid_candidates")) and bool(
        _allowed_fact_ids_from_context(tc)
    )


def _selector_valid_bullet_paths(
    paths: list[SelfConsistencyPath],
    *,
    required_bullet_ids: tuple[str, ...],
    targeting_context: dict[str, Any] | None,
) -> tuple[list[SelfConsistencyPath], dict[str, Any]]:
    """Return selector-visible paths after deterministic source/FEC eligibility filtering."""
    allowed_fact_ids = _allowed_fact_ids_from_context(targeting_context)
    strict = _selector_requires_valid_candidates(
        slot_kind="bullets",
        targeting_context=targeting_context,
    )
    receipt: dict[str, Any] = {
        "strict": strict,
        "allowed_fact_id_count": len(allowed_fact_ids),
        "required_bullet_ids": list(required_bullet_ids),
        "paths": [],
    }
    if not strict:
        return paths, receipt

    required = set(required_bullet_ids)
    filtered_paths: list[SelfConsistencyPath] = []
    for path in paths:
        parsed = path.parsed
        path_row: dict[str, Any] = {
            "path_index": path.path_index,
            "input_bullet_count": 0,
            "eligible_bullet_count": 0,
            "rejections": [],
        }
        if not isinstance(parsed, dict):
            path_row["rejections"].append({"reason": "parsed_missing"})
            filtered_paths.append(replace(path, parsed=None))
            receipt["paths"].append(path_row)
            continue

        eligible_bullets: list[dict[str, Any]] = []
        bullets = parsed.get("bullets") if isinstance(parsed.get("bullets"), list) else []
        path_row["input_bullet_count"] = len(bullets)
        for bullet in bullets:
            if not isinstance(bullet, dict):
                path_row["rejections"].append({"reason": "bullet_not_object"})
                continue
            bid = str(bullet.get("bullet_id") or "").strip()
            if bid not in required:
                path_row["rejections"].append(
                    {"bullet_id": bid, "reason": "bullet_id_not_required"}
                )
                continue
            source_ids = _candidate_source_ids(bullet)
            if not source_ids:
                path_row["rejections"].append(
                    {"bullet_id": bid, "reason": "missing_source_fact_ids"}
                )
                continue
            blocked = [sid for sid in source_ids if not _source_id_allowed(sid, allowed_fact_ids)]
            if blocked:
                path_row["rejections"].append(
                    {
                        "bullet_id": bid,
                        "reason": "source_fact_id_not_allowed",
                        "source_fact_ids": blocked,
                    }
                )
                continue
            eligible_bullets.append(dict(bullet))

        path_row["eligible_bullet_count"] = len(eligible_bullets)
        next_parsed: dict[str, Any] | None = None
        if eligible_bullets:
            next_parsed = dict(parsed)
            next_parsed["bullets"] = eligible_bullets
            next_parsed["claim_ledger"] = _filter_claim_ledger_for_allowed_sources(
                parsed.get("claim_ledger"),
                allowed_fact_ids,
            )
        filtered_paths.append(replace(path, parsed=next_parsed))
        receipt["paths"].append(path_row)

    return filtered_paths, receipt


def _selector_numeric_entailed_paths(
    paths: list[SelfConsistencyPath],
    *,
    required_bullet_ids: tuple[str, ...],
    targeting_context: dict[str, Any] | None,
) -> tuple[list[SelfConsistencyPath], dict[str, Any]]:
    """W4.3 (G15/G17): drop bullet rows whose numeric tokens are not entailed by the slot's
    fact corpus (``slot_entailment_corpus`` built upstream from selected_fact_plan C0-pool
    facts + bundle non-metric text). Exclusion only — bullet text is never rewritten.

    Fail-open: bypass env, missing/empty corpus, or a slot without corpus text leaves the
    candidate untouched (recorded in the receipt). A path whose bullets are all excluded
    gets ``parsed=None`` — mirroring ``_selector_valid_bullet_paths`` semantics — so the
    existing strict-emptiness return fires instead of dispatching a Claude selector call
    against a zero-candidate pool.
    """
    from apps_rg.runtime.reasoning.bullet_fact_entailment import (
        CORPUS_SOURCE_LABEL,
        ENTAILMENT_BYPASS_ENV,
        ENTAILMENT_REJECTION_REASON,
        numeric_entailment_check,
    )

    bypass = os.environ.get(ENTAILMENT_BYPASS_ENV, "").strip() == "1"
    corpus = (targeting_context or {}).get("slot_entailment_corpus")
    corpus = corpus if isinstance(corpus, dict) else {}
    receipt: dict[str, Any] = {
        "operation": "selector_fact_entailment_exclusion",
        "bypass": bypass,
        "corpus_source": CORPUS_SOURCE_LABEL,
        "corpus_present": bool(corpus),
        "slot_ids_with_corpus": sorted(str(k) for k in corpus),
        "required_bullet_ids": list(required_bullet_ids),
        "excluded_total": 0,
        "paths": [],
    }
    if bypass or not corpus:
        return paths, receipt

    excluded_total = 0
    filtered_paths: list[SelfConsistencyPath] = []
    for path in paths:
        parsed = path.parsed
        path_row: dict[str, Any] = {
            "path_index": path.path_index,
            "input_bullet_count": 0,
            "entailed_bullet_count": 0,
            "corpus_missing_slots": [],
            "rejections": [],
        }
        if not isinstance(parsed, dict):
            filtered_paths.append(path)
            receipt["paths"].append(path_row)
            continue

        bullets = parsed.get("bullets") if isinstance(parsed.get("bullets"), list) else []
        path_row["input_bullet_count"] = len(bullets)
        entailed_bullets: list[Any] = []
        for bullet in bullets:
            if not isinstance(bullet, dict):
                entailed_bullets.append(bullet)
                continue
            bid = str(bullet.get("bullet_id") or "").strip()
            corpus_text = str(corpus.get(bid) or "")
            if not corpus_text:
                # Fail-open per slot: no evidence corpus means no exclusion authority.
                if bid and bid not in path_row["corpus_missing_slots"]:
                    path_row["corpus_missing_slots"].append(bid)
                entailed_bullets.append(bullet)
                continue
            bullet_text = str(bullet.get("bullet_text") or "")
            entailed, missing_tokens = numeric_entailment_check(bullet_text, corpus_text)
            if entailed:
                entailed_bullets.append(bullet)
                continue
            excluded_total += 1
            path_row["rejections"].append(
                {
                    "bullet_id": bid,
                    "path_index": path.path_index,
                    "reason": ENTAILMENT_REJECTION_REASON,
                    "missing_tokens": missing_tokens,
                    "bullet_sha16": _sha16(bullet_text),
                }
            )

        path_row["entailed_bullet_count"] = sum(
            1 for b in entailed_bullets if isinstance(b, dict)
        )
        if entailed_bullets == bullets:
            filtered_paths.append(path)
        else:
            next_parsed: dict[str, Any] | None = None
            if any(isinstance(b, dict) for b in entailed_bullets):
                next_parsed = dict(parsed)
                next_parsed["bullets"] = entailed_bullets
            filtered_paths.append(replace(path, parsed=next_parsed))
        receipt["paths"].append(path_row)

    receipt["excluded_total"] = excluded_total
    return filtered_paths, receipt


def _append_entailment_receipt_round(artifact_dir: Path, doc: dict[str, Any]) -> None:
    """Rounds-append pattern (mirrors ``_write_employment_regen_artifact``) so the regen
    loop's per-invocation receipts all survive — last-write-wins would lose round 0."""
    from apps_rg.runtime.reasoning.bullet_fact_entailment import ENTAILMENT_RECEIPT_FILENAME

    path = artifact_dir / ENTAILMENT_RECEIPT_FILENAME
    prior: list[dict[str, Any]] = []
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and isinstance(loaded.get("rounds"), list):
                prior = loaded["rounds"]
        except (json.JSONDecodeError, OSError):
            prior = []
    path.write_text(
        json.dumps({"rounds": prior + [doc]}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _category_by_label(parsed: dict[str, Any], label: str) -> dict[str, Any] | None:
    norm = label.strip().lower()
    for key in ("competencies", "categories"):
        for row in parsed.get(key) or []:
            if not isinstance(row, dict):
                continue
            if str(row.get("category_label") or "").strip().lower() == norm:
                return row
    return None


def _is_competencies_graph_pool(section_id: str, slot_kind: SlotKind) -> bool:
    return str(section_id or "").strip().lower() == "competencies" and slot_kind == "competencies"


def _competencies_graph_selection_prompt(
    *,
    pool_text: str,
    targeting_context: dict[str, Any] | None,
    min_score_threshold: float,
    selector_name: str,
    regen_note: str = "",
) -> str:
    n_paths = len([p for p in pool_text.split("=== PATH ") if p.strip()]) or COMPETENCIES_SC_PATH_COUNT
    n_min = COMPETENCIES_MIN_CATEGORY_COUNT
    n_max = COMPETENCIES_FINAL_CATEGORY_COUNT
    n_candidate = COMPETENCIES_CANDIDATE_CATEGORY_COUNT
    high_signal = high_signal_competencies_selection_score()
    jd = (targeting_context or {}).get("jd_text") or ""
    briefing = (targeting_context or {}).get("briefing") or ""
    skills_ref = (targeting_context or {}).get("skills_graph_ref") or ""
    return (
        "You are the sole selector for competencies (graph_8x8_v1).\n"
        f"{n_paths} PROVIDER_MODEL self-consistency paths produced candidate category sets (up to {n_candidate} labels). "
        f"Select {n_min}-{n_max} categories — only the highest-signal categories that PASS graph/fact reality.\n"
        "Constraints:\n"
        "- augmented_skills_graph / selected_fact_plan are the only proof authority (JD and briefing are "
        "targeting emphasis only — never cite facts.skills or base-resume skill rows as proof).\n"
        "- Score each unique category_label variant on phrase_quality, evidence_alignment, distinctness, "
        "and anti_keyword_stuffing.\n"
        f"- Minimum score floor: only select variants with score >= {min_score_threshold:.2f} AND passes=true.\n"
        f"- High-signal target: prefer categories with score >= {high_signal:.2f}; include lower-scoring passing "
        f"categories only if needed to reach {n_min}.\n"
        f"- Output {n_min}-{n_max} selections when possible; each row must include category_label, "
        "path_index, score, passes, and rationale.\n"
        f"{regen_note}\n\n"
        f"JD (targeting only):\n{jd[:resolve_bullet_selector_jd_max_chars()]}\n\n"
        f"Briefing (targeting only):\n{briefing[:resolve_bullet_selector_briefing_max_chars()]}\n\n"
        f"Skills graph ref: {skills_ref}\n\n"
        "Return JSON only:\n"
        f'{{"selections":[{{"category_label":"...","path_index":0,"score":0.85,"passes":true,"rationale":"..."}}],'
        f'"pool_summary":{{"paths_scored":{n_paths},"min_category_count":{n_min},'
        f'"max_category_count":{n_max},'
        f'"candidate_category_count":{n_candidate},'
        f'"min_score_threshold":{min_score_threshold:.2f},"selector":"{selector_name}","mode":"graph_8x8"}}}}\n\n'
        "CANDIDATE POOL:\n"
        f"{pool_text}"
    )


def _format_bullet_pool(paths: list[SelfConsistencyPath], required_ids: tuple[str, ...]) -> str:
    blocks: list[str] = []
    for path in paths:
        if path.parsed is None:
            continue
        lines = [f"=== PATH {path.path_index} (temperature={path.temperature}) ==="]
        for bid in required_ids:
            bullet = _bullet_by_id(path.parsed, bid)
            if bullet is None:
                lines.append(f"[{bid}] MISSING")
            else:
                lines.append(f"[{bid}] text={bullet.get('bullet_text', '')}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _format_competency_pool(paths: list[SelfConsistencyPath]) -> str:
    blocks: list[str] = []
    for path in paths:
        if path.parsed is None:
            continue
        lines = [f"=== PATH {path.path_index} (temperature={path.temperature}) ==="]
        for cat in (path.parsed.get("competencies") or path.parsed.get("categories") or []):
            if not isinstance(cat, dict):
                continue
            label = str(cat.get("category_label") or "").strip()
            terms = cat.get("terms") or []
            phrase_bits: list[str] = []
            if isinstance(terms, list):
                for t in terms[:6]:
                    if isinstance(t, dict):
                        phrase_bits.append(str(t.get("text") or ""))
                    else:
                        phrase_bits.append(str(t))
            lines.append(f"[{label}] terms={', '.join(p for p in phrase_bits if p)}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _employment_bullet_selection_prompt(
    *,
    section_id: str,
    pool_text: str,
    required_bullet_ids: tuple[str, ...],
    targeting_context: dict[str, Any] | None,
    min_score_threshold: float,
    selector_name: str,
    regen_note: str = "",
) -> str:
    n_final = FINAL_BULLET_COUNT.get(section_id, len(required_bullet_ids))
    n_paths = sc_path_count_for_lane(section_id)
    ids_line = ", ".join(required_bullet_ids)
    jd = (targeting_context or {}).get("jd_text") or ""
    briefing = (targeting_context or {}).get("briefing") or ""
    skills_ref = (targeting_context or {}).get("skills_graph_ref") or ""
    return (
        f"You are the sole selector for {section_id} employment bullets.\n"
        f"{n_paths} PROVIDER_MODEL self-consistency paths produced candidate sets. Pick the top {n_final} bullets that PASS "
        f"quality — exactly one winning variant per bullet_id: {ids_line}.\n"
        "Constraints:\n"
        "- Skills graph / selected_fact_plan facts are the only proof authority (JD and briefing are targeting "
        "emphasis only — never copy JD phrases as proof).\n"
        f"- {pool_selector_scoring_instruction(section_id)}\n"
        f"- Minimum score floor: only select variants with score >= {min_score_threshold:.2f} AND passes=true. "
        f"If no variant for a slot meets the floor, set passes=false for that slot.\n"
        f"- Output exactly {n_final} selections when possible; each selected row must include score and passes.\n"
        f"{regen_note}\n\n"
        f"JD (targeting only):\n{jd[:resolve_bullet_selector_jd_max_chars()]}\n\n"
        f"Briefing (targeting only):\n{briefing[:resolve_bullet_selector_briefing_max_chars()]}\n\n"
        f"Skills graph ref: {skills_ref}\n\n"
        "Return JSON only:\n"
        f'{{"selections":[{{"bullet_id":"...","path_index":0,"score":0.85,"passes":true,"rationale":"..."}}],'
        f'"pool_summary":{{"paths_scored":{n_paths},"final_bullet_count":{n_final},'
        f'"min_score_threshold":{min_score_threshold:.2f},"selector":"{selector_name}"}}}}\n\n'
        "CANDIDATE POOL:\n"
        f"{pool_text}"
    )


def _selection_prompt(
    *,
    section_id: str,
    slot_kind: SlotKind,
    pool_text: str,
    required_bullet_ids: tuple[str, ...] | None,
    targeting_context: dict[str, Any] | None,
    min_score_threshold: float | None = None,
    selector_name: str = "anthropic_claude",
    regen_note: str = "",
) -> str:
    if _is_competencies_graph_pool(section_id, slot_kind):
        floor = (
            min_score_threshold
            if min_score_threshold is not None
            else min_competencies_selection_score()
        )
        return _competencies_graph_selection_prompt(
            pool_text=pool_text,
            targeting_context=targeting_context,
            min_score_threshold=floor,
            selector_name=selector_name,
            regen_note=regen_note,
        )
    if slot_kind == "bullets" and is_employment_bullet_lane(section_id) and required_bullet_ids:
        floor = (
            min_score_threshold
            if min_score_threshold is not None
            else min_selection_score_for_lane(section_id)
        )
        return _employment_bullet_selection_prompt(
            section_id=section_id,
            pool_text=pool_text,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
            min_score_threshold=floor,
            selector_name=selector_name,
            regen_note=regen_note,
        )
    if slot_kind == "bullets":
        ids_line = ", ".join(required_bullet_ids or ())
        task = (
            f"Select the best bullet_text per bullet_id from the self-consistency pool for section {section_id}. "
            f"Required ids: {ids_line}. "
            "Score each variant on factual_support, impact_clarity, ats_alignment_without_stuffing, "
            "rewrite_quality, and distinctness across bullets. "
            "Pick exactly one winning path_index per bullet_id."
        )
        schema = (
            f'{{"selections":[{{"bullet_id":"...","path_index":0,"score":0.0,"rationale":"..."}}],'
            f'"pool_summary":{{"paths_scored":N,"selector":"{selector_name}"}}}}'
        )
    else:
        task = (
            f"Select the best competency category block per category_label from the self-consistency pool "
            f"for section {section_id}. "
            "Score each variant on phrase_quality, evidence_alignment, distinctness across categories, "
            "and anti_keyword_stuffing. Pick exactly one winning path_index per category_label."
        )
        schema = (
            f'{{"selections":[{{"category_label":"...","path_index":0,"score":0.0,"rationale":"..."}}],'
            f'"pool_summary":{{"paths_scored":N,"selector":"{selector_name}"}}}}'
        )
    ctx = ""
    if targeting_context:
        ctx = f"\nTargeting context (emphasis only, not proof): {json.dumps(targeting_context, ensure_ascii=False)[:1200]}\n"
    return (
        f"{task}\n{ctx}\n"
        "Return JSON only.\n"
        f"Schema: {schema}\n\n"
        "CANDIDATE POOL:\n"
        f"{pool_text}"
    )


def _iter_top_level_json_object_spans(text: str) -> list[str]:
    """Return every balanced top-level ``{...}`` span in ``text`` (string/escape aware).

    Braces inside JSON string values are ignored; nested objects stay inside their
    enclosing top-level span. Unterminated objects yield nothing.
    """
    spans: list[str] = []
    depth = 0
    start = -1
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start != -1:
                spans.append(text[start : i + 1])
                start = -1
    return spans


def _parse_selections(text: str) -> dict[str, Any] | None:
    """Extract the pool-selection doc — the JSON object carrying a ``selections`` list.

    Bug:BulletPoolSelectorDualJsonObjects (AIG attempt4 + patch-run 2, 2026-06-11):
    Claude stochastically obeyed the old rubric system prompt IN ADDITION to the
    pool-selection user prompt and returned TWO top-level JSON objects — the rubric verdict
    first, then ``{"selections": [...]}`` — separated by a blank line (stop_reason=end_turn;
    not truncation). ``_extract_json_from_text`` cannot parse multi-object text: the direct
    ``json.loads`` and the first-``{``-to-last-``}`` span both raise "Extra data", and there
    are no markdown fences to strip — so a fully valid selections doc was discarded and the
    call blocked with "Pool selector JSON missing selections array". Scan balanced top-level
    objects and prefer the one that actually carries a ``selections`` list; otherwise keep
    the legacy single-object result (rubric-only responses keep their prior behavior).
    Genuinely unusable responses (no JSON, refusal prose) still return ``None`` and fail
    closed upstream — the synthetic decisive judge row remains the honest outcome.
    """
    doc = _extract_json_from_text(text)
    if isinstance(doc, dict) and isinstance(doc.get("selections"), list):
        return doc
    for span in _iter_top_level_json_object_spans(str(text or "")):
        try:
            candidate = json.loads(span)
        except json.JSONDecodeError:  # guardian: allow-silent-swallow -- scan continues to next balanced span
            continue
        if isinstance(candidate, dict) and isinstance(candidate.get("selections"), list):
            return candidate
    return doc


def _load_selection_doc_from_judge_artifacts(
    judge_out: JudgeOutput,
    artifact_dir: Path | None,
    *,
    provider_key: str,
) -> dict[str, Any] | None:
    if artifact_dir is not None:
        parse_path = _artifact_path(
            provider_key,
            "provider_parse_result",
            artifact_base=artifact_dir,
        )
        if parse_path.is_file():
            try:
                doc = json.loads(parse_path.read_text(encoding="utf-8"))
                result = doc.get("result")
                if isinstance(result, dict) and isinstance(result.get("selections"), list):
                    return result
            except (json.JSONDecodeError, OSError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                pass
        raw_path = _artifact_path(
            provider_key,
            "provider_response_raw",
            artifact_base=artifact_dir,
        )
        if raw_path.is_file():
            try:
                doc = json.loads(raw_path.read_text(encoding="utf-8"))
                if provider_key == "anthropic_claude":
                    text = _extract_anthropic_message_text(doc)
                else:
                    raw_response = str(doc.get("raw_response") or "")
                    response_doc = json.loads(raw_response) if raw_response else {}
                    choice = response_doc["choices"][0]
                    message = choice.get("message") or {}
                    text = str(message.get("content") or "")
                return _parse_selections(text)
            except (json.JSONDecodeError, OSError, TypeError, KeyError, IndexError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                pass
    if judge_out.rationale:
        return _parse_selections(str(judge_out.rationale))
    return None


def _call_anthropic_pool_selector(
    *,
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    model_source: str,
    artifact_dir: Path | None,
    timeout_s: float | None = None,
) -> tuple[JudgeOutput, dict[str, Any] | None]:
    """Anthropic call for pool JSON (not GRADE_ONLY rubric schema)."""
    import time
    import urllib.error
    import urllib.request
    from datetime import datetime, timezone

    from apps_rg.runtime.providers.external_provider import (
        apply_anthropic_adaptive_thinking_config,
        apply_anthropic_temperature_capability,
    )
    from apps_rg.runtime.judges.executive_summary_x1d import (
        _judge_live_https_allowed_under_pytest,
        _make_blocked_output,
        _pytest_network_disabled_blocked_output,
        _resolved_x1d_judge_max_output_tokens,
        _write_artifact,
    )

    timeout_s = pool_selector_timeout_s(default_seconds=timeout_s)
    max_tokens = _resolved_x1d_judge_max_output_tokens(attempt=1)
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": POOL_SELECTOR_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }
    apply_anthropic_temperature_capability(payload)
    apply_anthropic_adaptive_thinking_config(payload, os.environ)
    started_wall = datetime.now(timezone.utc).isoformat()
    req_path = _artifact_path("anthropic_claude", "provider_request", artifact_base=artifact_dir)
    _write_artifact(
        req_path,
        {
            "payload": payload,
            "input_hash": input_hash,
            "purpose": "bullet_pool_claude_selector",
            "effective_timeout_seconds": timeout_s,
            "timestamp": started_wall,
        },
    )
    _write_selector_timing_receipt(
        artifact_dir,
        {
            "phase": "started",
            "started_at": started_wall,
            "effective_timeout_seconds": timeout_s,
            "model": model,
            "input_hash": input_hash,
        },
    )
    if not _judge_live_https_allowed_under_pytest():
        _write_selector_timing_receipt(
            artifact_dir,
            {
                "phase": "blocked_pytest_network_disabled",
                "started_at": started_wall,
                "effective_timeout_seconds": timeout_s,
                "outcome": "provider_unavailable",
            },
        )
        blocked = _pytest_network_disabled_blocked_output(
            provider_key="anthropic_claude",
            input_hash=input_hash,
            model=model,
            service_label="Anthropic",
        )
        return blocked, None

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        _write_selector_timing_receipt(
            artifact_dir,
            {
                "phase": "error",
                "outcome": "provider_http_error",
                "http_status": exc.code,
                "elapsed_s": round(time.monotonic() - t0, 4),
                "effective_timeout_seconds": timeout_s,
            },
        )
        blocked = _make_blocked_output(
            "anthropic_claude",
            input_hash,
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE",
            f"Anthropic pool selector HTTP {exc.code}: {body[:400]}",
            model_name=model,
        )
        return blocked, None
    except (TimeoutError, urllib.error.URLError, OSError) as exc:
        # W3: a selector TIMEOUT is its own honest outcome, NOT a competencies generation failure.
        elapsed = round(time.monotonic() - t0, 4)
        is_timeout = isinstance(exc, TimeoutError) or "timed out" in str(exc).lower()
        outcome = "selector_timeout" if is_timeout else "provider_transport_error"
        _write_selector_timing_receipt(
            artifact_dir,
            {
                "phase": "error",
                "outcome": outcome,
                "elapsed_s": elapsed,
                "effective_timeout_seconds": timeout_s,
                "error": f"{type(exc).__name__}: {exc}",
            },
        )
        blocked = _make_blocked_output(
            "anthropic_claude",
            input_hash,
            "BLOCKED_SELECTOR_TIMEOUT" if is_timeout else "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_SELECTOR_TIMEOUT" if is_timeout else "BLOCKED_PROVIDER_UNAVAILABLE",
            f"Anthropic pool selector {outcome} after {elapsed}s "
            f"(budget {timeout_s}s): {type(exc).__name__}: {exc}",
            model_name=model,
        )
        return blocked, None

    completed_after_s = round(time.monotonic() - t0, 4)
    _write_selector_timing_receipt(
        artifact_dir,
        {
            "phase": "finished",
            "outcome": "response_received",
            "started_at": started_wall,
            "completed_after_s": completed_after_s,
            "effective_timeout_seconds": timeout_s,
            "raw_output_chars": len(raw_response or ""),
        },
    )
    raw_path = _artifact_path("anthropic_claude", "provider_response_raw", artifact_base=artifact_dir)
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    try:
        data = json.loads(raw_response)
        text = _extract_anthropic_message_text(data)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        blocked = _make_blocked_output(
            "anthropic_claude",
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Anthropic pool selector parse error: {exc}",
            raw_response_ref=str(raw_path),
            model_name=model,
        )
        return blocked, None
    if not str(text or "").strip():
        usage = data.get("usage") if isinstance(data, dict) else {}
        output_details = usage.get("output_tokens_details") if isinstance(usage, dict) else None
        detail_parts = []
        stop_reason = data.get("stop_reason") if isinstance(data, dict) else None
        if stop_reason:
            detail_parts.append(f"stop_reason={stop_reason}")
        if isinstance(output_details, dict):
            detail_parts.append(
                "output_tokens_details="
                + json.dumps(output_details, sort_keys=True, separators=(",", ":"))
            )
        detail = f" ({'; '.join(detail_parts)})" if detail_parts else ""
        blocked = _make_blocked_output(
            "anthropic_claude",
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Pool selector returned empty text{detail}",
            raw_response_ref=str(raw_path),
            model_name=model,
        )
        sel_path = _artifact_path("anthropic_claude", "provider_parse_result", artifact_base=artifact_dir)
        _write_artifact(
            sel_path,
            {"result": None, "raw_response_ref": str(raw_path), "purpose": "bullet_pool_claude_selector"},
        )
        return blocked, None

    selection_doc = _parse_selections(text)
    sel_path = _artifact_path("anthropic_claude", "provider_parse_result", artifact_base=artifact_dir)
    _write_artifact(
        sel_path,
        {"result": selection_doc, "raw_response_ref": str(raw_path), "purpose": "bullet_pool_claude_selector"},
    )
    if selection_doc is None:
        blocked = _make_blocked_output(
            "anthropic_claude",
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "Pool selector JSON missing selections array",
            raw_response_ref=str(raw_path),
            model_name=model,
        )
        return blocked, None

    judge_stub = JudgeOutput(
        judge_id="x1d_anthropic_claude_bullet_pool_selector",
        provider_name="Anthropic Claude",
        provider_key="anthropic_claude",
        evaluator_mode="MODEL_BACKED",
        provider_status="MODEL_BACKED_PASS",
        model_name=model,
        provider_available=True,
        provider_blocked=False,
        exact_provider_error=None,
        raw_response_ref=str(raw_path),
        input_hash=input_hash,
        pass_=True,
        rationale=str(model_source),
    )
    return judge_stub, selection_doc


def _call_openai_pool_selector(
    *,
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    model_source: str,
    artifact_dir: Path | None,
    timeout_s: float | None = None,
) -> tuple[JudgeOutput, dict[str, Any] | None]:
    """OpenAI call for pool JSON (competencies only)."""
    import time
    import urllib.error
    import urllib.request
    from datetime import datetime, timezone

    from apps_rg.runtime.judges.executive_summary_x1d import (
        _judge_live_https_allowed_under_pytest,
        _make_blocked_output,
        _pytest_network_disabled_blocked_output,
        _resolved_x1d_judge_max_output_tokens,
        _write_artifact,
    )

    timeout_s = pool_selector_timeout_s(default_seconds=timeout_s)
    max_tokens = _resolved_x1d_judge_max_output_tokens(attempt=1)
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": POOL_SELECTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    if _is_openai_gpt5_chat_model(model):
        payload["max_completion_tokens"] = max_tokens
    else:
        payload["max_tokens"] = max_tokens
        payload["temperature"] = 0.1
        payload["response_format"] = {"type": "json_object"}

    started_wall = datetime.now(timezone.utc).isoformat()
    req_path = _artifact_path("openai_chatgpt", "provider_request", artifact_base=artifact_dir)
    _write_artifact(
        req_path,
        {
            "payload": payload,
            "input_hash": input_hash,
            "purpose": "bullet_pool_openai_selector",
            "effective_timeout_seconds": timeout_s,
            "timestamp": started_wall,
        },
    )
    _write_selector_timing_receipt(
        artifact_dir,
        {
            "phase": "started",
            "started_at": started_wall,
            "effective_timeout_seconds": timeout_s,
            "model": model,
            "input_hash": input_hash,
        },
    )
    if not _judge_live_https_allowed_under_pytest():
        _write_selector_timing_receipt(
            artifact_dir,
            {
                "phase": "blocked_pytest_network_disabled",
                "started_at": started_wall,
                "effective_timeout_seconds": timeout_s,
                "outcome": "provider_unavailable",
            },
        )
        blocked = _pytest_network_disabled_blocked_output(
            provider_key="openai_chatgpt",
            input_hash=input_hash,
            model=model,
            service_label="OpenAI",
        )
        return blocked, None

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        _write_selector_timing_receipt(
            artifact_dir,
            {
                "phase": "error",
                "outcome": "provider_http_error",
                "http_status": exc.code,
                "elapsed_s": round(time.monotonic() - t0, 4),
                "effective_timeout_seconds": timeout_s,
            },
        )
        blocked = _make_blocked_output(
            "openai_chatgpt",
            input_hash,
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE",
            f"OpenAI pool selector HTTP {exc.code}: {body[:400]}",
            model_name=model,
        )
        return blocked, None
    except (TimeoutError, urllib.error.URLError, OSError) as exc:
        elapsed = round(time.monotonic() - t0, 4)
        is_timeout = isinstance(exc, TimeoutError) or "timed out" in str(exc).lower()
        outcome = "selector_timeout" if is_timeout else "provider_transport_error"
        _write_selector_timing_receipt(
            artifact_dir,
            {
                "phase": "error",
                "outcome": outcome,
                "elapsed_s": elapsed,
                "effective_timeout_seconds": timeout_s,
                "error": f"{type(exc).__name__}: {exc}",
            },
        )
        blocked = _make_blocked_output(
            "openai_chatgpt",
            input_hash,
            "BLOCKED_SELECTOR_TIMEOUT" if is_timeout else "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_SELECTOR_TIMEOUT" if is_timeout else "BLOCKED_PROVIDER_UNAVAILABLE",
            f"OpenAI pool selector {outcome} after {elapsed}s "
            f"(budget {timeout_s}s): {type(exc).__name__}: {exc}",
            model_name=model,
        )
        return blocked, None

    completed_after_s = round(time.monotonic() - t0, 4)
    _write_selector_timing_receipt(
        artifact_dir,
        {
            "phase": "finished",
            "outcome": "response_received",
            "started_at": started_wall,
            "completed_after_s": completed_after_s,
            "effective_timeout_seconds": timeout_s,
            "raw_output_chars": len(raw_response or ""),
        },
    )
    raw_path = _artifact_path("openai_chatgpt", "provider_response_raw", artifact_base=artifact_dir)
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    try:
        data = json.loads(raw_response)
        choice = data["choices"][0]
        message = choice.get("message") or {}
        text = str(message.get("content") or "").strip()
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        blocked = _make_blocked_output(
            "openai_chatgpt",
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"OpenAI pool selector parse error: {exc}",
            raw_response_ref=str(raw_path),
            model_name=model,
        )
        return blocked, None

    selection_doc = _parse_selections(text)
    sel_path = _artifact_path("openai_chatgpt", "provider_parse_result", artifact_base=artifact_dir)
    _write_artifact(
        sel_path,
        {"result": selection_doc, "raw_response_ref": str(raw_path), "purpose": "bullet_pool_openai_selector"},
    )
    if selection_doc is None:
        blocked = _make_blocked_output(
            "openai_chatgpt",
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "Pool selector JSON missing selections array",
            raw_response_ref=str(raw_path),
            model_name=model,
        )
        return blocked, None

    judge_stub = JudgeOutput(
        judge_id="x1d_openai_chatgpt_bullet_pool_selector",
        provider_name="OpenAI ChatGPT",
        provider_key="openai_chatgpt",
        evaluator_mode="MODEL_BACKED",
        provider_status="MODEL_BACKED_PASS",
        model_name=model,
        provider_available=True,
        provider_blocked=False,
        exact_provider_error=None,
        raw_response_ref=str(raw_path),
        input_hash=input_hash,
        pass_=True,
        rationale=str(model_source),
    )
    return judge_stub, selection_doc


def _merge_competencies_graph_pool_with_audit(
    paths: list[SelfConsistencyPath],
    selections: list[dict[str, Any]],
    *,
    base_parsed: dict[str, Any],
    targeting_context: dict[str, Any] | None,
    min_score_threshold: float | None = None,
) -> tuple[dict[str, Any], dict[str, int], dict[str, Any]]:
    tc = targeting_context or {}
    allowed_fact_ids = set(tc.get("allowed_fact_ids") or [])
    allowed_skill_ids = set(tc.get("allowed_skill_ids") or [])
    resume_support_blob_lower = str(tc.get("resume_support_blob_lower") or "")
    merged, source_map = merge_competencies_graph_pool_top_eight(
        paths,
        selections,
        base_parsed=base_parsed,
        min_score_threshold=min_score_threshold,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        resume_support_blob_lower=resume_support_blob_lower,
    )
    audit = build_competencies_rejected_neighbor_audit(
        paths,
        selections,
        merged,
        source_map,
        min_score_threshold=min_score_threshold,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        resume_support_blob_lower=resume_support_blob_lower,
    )
    merged = dict(merged)
    merged["competencies_rejected_neighbor_audit"] = audit
    return merged, source_map, audit


def _fallback_first_complete_path(
    paths: list[SelfConsistencyPath],
    *,
    slot_kind: SlotKind,
    required_bullet_ids: tuple[str, ...] | None,
    targeting_context: dict[str, Any] | None = None,
) -> PoolSelectionResult:
    def _deterministic_bullet_selections(path_index: int) -> list[dict[str, Any]]:
        return [
            {
                "bullet_id": bid,
                "path_index": path_index,
                "score": 1.0,
                "passes": True,
                "selection_reason": "deterministic_first_complete_path_fallback",
            }
            for bid in (required_bullet_ids or ())
        ]

    for path in paths:
        if path.parsed is None:
            continue
        if slot_kind == "bullets" and required_bullet_ids:
            if all(_bullet_by_id(path.parsed, bid) is not None for bid in required_bullet_ids):
                return PoolSelectionResult(
                    merged_parsed=dict(path.parsed),
                    selections=_deterministic_bullet_selections(path.path_index),
                    judge_output=None,
                    selection_mode="fallback_first_complete_path",
                    source_path_by_slot={bid: path.path_index for bid in required_bullet_ids},
                )
        elif slot_kind == "competencies":
            comps = path.parsed.get("competencies") or path.parsed.get("categories")
            if isinstance(comps, list) and len(comps) >= COMPETENCIES_MIN_CATEGORY_COUNT:
                merged, source_map, audit = _merge_competencies_graph_pool_with_audit(
                    paths,
                    [],
                    base_parsed=dict(path.parsed),
                    targeting_context=targeting_context,
                )
                return PoolSelectionResult(
                    merged_parsed=merged,
                    selections=[],
                    judge_output=None,
                    selection_mode="competencies_graph_adaptive_6_8_heuristic",
                    source_path_by_slot=source_map,
                    rejected_neighbor_audit=audit,
                )
    if slot_kind == "competencies":
        merged, source_map, audit = _merge_competencies_graph_pool_with_audit(
            paths,
            [],
            base_parsed=paths[0].parsed if paths and paths[0].parsed else {},
            targeting_context=targeting_context,
        )
        return PoolSelectionResult(
            merged_parsed=merged,
            selections=[],
            judge_output=None,
            selection_mode="competencies_graph_adaptive_6_8_heuristic",
            source_path_by_slot=source_map,
            rejected_neighbor_audit=audit,
        )
    base = paths[0].parsed if paths and paths[0].parsed else {}
    return PoolSelectionResult(
        merged_parsed=dict(base) if isinstance(base, dict) else {},
        selections=[],
        judge_output=None,
        selection_mode="fallback_empty",
        source_path_by_slot={},
    )


def _selection_passes(row: dict[str, Any]) -> bool:
    if "passes" not in row:
        return True
    val = row.get("passes")
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("true", "1", "yes")


def _bullet_passes_line_discipline(bullet: dict[str, Any] | None) -> bool:
    """Deterministic per-bullet compliance pre-check mirroring the X2 line-discipline gates.

    W5 (plan apps-rg-aig-remaining-lanes-closeout-d4e1f7): with N self-consistency paths the
    pool usually contains a compliant candidate per slot — prefer it over a max-score candidate
    that would deterministically fail X2 (e.g. 325-char paragraph block vs the 320 cap).
    """
    if not isinstance(bullet, dict):
        return False
    from apps_rg.runtime.validators.bullet_line_discipline_x2 import (
        check_bullet_no_embedded_newline,
        check_bullet_no_paragraph_block,
        check_bullet_single_thought,
    )
    from apps_rg.runtime.validators.bullet_quality_floor_x2 import (
        check_bullet_seniority_floor,
        check_bullet_technical_specificity_floor,
    )

    text = str(bullet.get("bullet_text") or "")
    bid = str(bullet.get("bullet_id") or "")
    return (
        check_bullet_no_paragraph_block(text)[0]
        and check_bullet_single_thought(text)[0]
        and check_bullet_no_embedded_newline(text)[0]
        # Quality floors are deterministic X2 gates too (W4-residual): prefer candidates that
        # already carry a strong executive verb/scale signal and a named mechanism.
        and check_bullet_seniority_floor(bid, text).passed
        and check_bullet_technical_specificity_floor(bid, text).passed
    )


def merge_bullet_selections(
    paths: list[SelfConsistencyPath],
    selections: list[dict[str, Any]],
    *,
    required_bullet_ids: tuple[str, ...],
    base_parsed: dict[str, Any] | None = None,
    min_score_threshold: float | None = None,
) -> tuple[dict[str, Any], dict[str, int]]:
    path_by_index = {p.path_index: p for p in paths}
    anchor = dict(base_parsed or (paths[0].parsed if paths else {}) or {})
    bullets_out: list[dict[str, Any]] = []
    source_map: dict[str, int] = {}

    def _bullet_for_selection(sel: dict[str, Any] | None, bid: str) -> dict[str, Any] | None:
        if not isinstance(sel, dict):
            return None
        path = path_by_index.get(int(sel.get("path_index", 0)))
        return _bullet_by_id(path.parsed or {}, bid) if path and path.parsed else None

    for bid in required_bullet_ids:
        slot_selections = [
            s
            for s in selections
            if str(s.get("bullet_id") or "").strip() == bid and _selection_passes(s)
        ]
        if min_score_threshold is not None:
            slot_selections = [
                s for s in slot_selections if float(s.get("score") or 0.0) >= min_score_threshold
            ]
        # Gate-aware preference (W5): among score-passing candidates, pick the highest-scored one
        # whose bullet also passes the deterministic line-discipline checks; fall back to the raw
        # max-score candidate when none are compliant (the lane then fails X2 honestly).
        ranked = sorted(slot_selections, key=lambda s: float(s.get("score") or 0.0), reverse=True)
        sel = next((s for s in ranked if _bullet_passes_line_discipline(_bullet_for_selection(s, bid))), None)
        if sel is None:
            sel = ranked[0] if ranked else None
        if sel is None:
            sel = next((s for s in selections if str(s.get("bullet_id") or "").strip() == bid), None)
        path_idx = int(sel.get("path_index", 0)) if isinstance(sel, dict) else 0
        path = path_by_index.get(path_idx) or paths[0]
        bullet = _bullet_by_id(path.parsed or {}, bid) if path and path.parsed else None
        if bullet is None:
            for p in paths:
                if p.parsed and _bullet_by_id(p.parsed, bid):
                    bullet = _bullet_by_id(p.parsed, bid)
                    path_idx = p.path_index
                    break
        # W5 all-paths compliance scan: the Claude selector returns ONE winner per slot, so the
        # ranked pre-filter above usually has a single candidate. When the winner's bullet fails
        # the deterministic line-discipline gates, scan every path for the same slot and take a
        # compliant alternative — the slot would otherwise deterministically fail X2 (e.g. a
        # 325-char paragraph block vs the 320 cap). Keep the winner when no path is compliant.
        if bullet is not None and not _bullet_passes_line_discipline(bullet):
            for p in paths:
                if not p.parsed:
                    continue
                alt = _bullet_by_id(p.parsed, bid)
                if alt is not None and _bullet_passes_line_discipline(alt):
                    bullet = alt
                    path_idx = p.path_index
                    break
        if bullet is not None:
            bullets_out.append(dict(bullet))
            source_map[bid] = path_idx

    merged = dict(anchor)
    merged["bullets"] = bullets_out
    ledger_rows: list[dict[str, Any]] = []
    for bid, pidx in source_map.items():
        src_path = path_by_index.get(pidx)
        if not src_path or not src_path.parsed:
            continue
        for row in src_path.parsed.get("claim_ledger") or []:
            if not isinstance(row, dict):
                continue
            sids = row.get("source_fact_ids") or []
            if bid in [str(x) for x in sids] or bid == str(row.get("bullet_id") or ""):
                ledger_rows.append(dict(row))
    if ledger_rows:
        merged["claim_ledger"] = ledger_rows
    elif anchor.get("claim_ledger"):
        merged["claim_ledger"] = list(anchor.get("claim_ledger") or [])
    # W5 (apps-rg-aig-remaining-lanes-closeout-d4e1f7): merge per-bullet ``change_log`` rows from
    # each selected bullet's SOURCE path, mirroring the claim_ledger merge above. Keeping only
    # the anchor path's change_log paired bullets from path N with bindings from path 0, so
    # metric_outcome_ids / role_episode_bundle_id bindings went missing for selected bullets
    # (x2_*_metric_outcome_id_required_when_has_metric failed on a structurally mismatched doc).
    change_rows: list[dict[str, Any]] = []
    for bid, pidx in source_map.items():
        src_path = path_by_index.get(pidx)
        if not src_path or not src_path.parsed:
            continue
        for row in src_path.parsed.get("change_log") or []:
            if not isinstance(row, dict):
                continue
            row_bid = str(row.get("bullet_id") or "")
            row_sids = [str(x) for x in (row.get("source_fact_ids") or [])]
            if bid == row_bid or bid in row_sids:
                change_rows.append(dict(row))
    if change_rows:
        merged["change_log"] = change_rows
    elif anchor.get("change_log"):
        merged["change_log"] = list(anchor.get("change_log") or [])
    return merged, source_map


def merge_competency_selections(
    paths: list[SelfConsistencyPath],
    selections: list[dict[str, Any]],
    *,
    base_parsed: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, int]]:
    path_by_index = {p.path_index: p for p in paths}
    anchor = dict(base_parsed or (paths[0].parsed if paths else {}) or {})
    labels_seen: set[str] = set()
    comps_out: list[dict[str, Any]] = []
    source_map: dict[str, int] = {}

    for sel in selections:
        if not isinstance(sel, dict):
            continue
        label = str(sel.get("category_label") or "").strip()
        if not label:
            continue
        path_idx = int(sel.get("path_index", 0))
        path = path_by_index.get(path_idx)
        cat = _category_by_label(path.parsed or {}, label) if path and path.parsed else None
        if cat is not None:
            comps_out.append(dict(cat))
            labels_seen.add(label.lower())
            source_map[label.lower()] = path_idx

    if not comps_out:
        for path in paths:
            if path.parsed and isinstance(path.parsed.get("competencies"), list):
                return dict(path.parsed), {}

    for path in paths:
        if not path.parsed:
            continue
        for cat in (path.parsed.get("competencies") or path.parsed.get("categories") or []):
            if not isinstance(cat, dict):
                continue
            label = str(cat.get("category_label") or "").strip()
            key = label.lower()
            if key and key not in labels_seen:
                comps_out.append(dict(cat))
                labels_seen.add(key)
                source_map[key] = path.path_index

    merged = dict(anchor)
    merged["competencies"] = comps_out
    if paths and paths[0].parsed and paths[0].parsed.get("claim_ledger"):
        merged["claim_ledger"] = list(paths[0].parsed.get("claim_ledger") or [])
    return merged, source_map


def run_claude_bullet_pool_selection(
    *,
    section_id: str,
    slot_kind: SlotKind,
    paths: list[SelfConsistencyPath],
    required_bullet_ids: tuple[str, ...] | None = None,
    targeting_context: dict[str, Any] | None = None,
    artifact_dir: Path | None = None,
    mode: str = "blocked_if_unavailable",
    min_score_threshold: float | None = None,
    regen_note: str = "",
) -> PoolSelectionResult:
    """Invoke the provider-backed pool selector and merge per-slot winners."""
    competencies_selector = _is_competencies_graph_pool(section_id, slot_kind)
    valid_paths = [p for p in paths if p.parsed is not None]
    if not valid_paths:
        if competencies_selector:
            detail = _first_path_failure_detail(paths)
            suffix = f"; first failure: {detail[:300]}" if detail else ""
            raise PoolSelectorUnavailableError(
                f"competencies selector unavailable: no parsed candidate paths{suffix}"
            )
        return _fallback_first_complete_path(
            paths,
            slot_kind=slot_kind,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
        )

    validity_receipt: dict[str, Any] | None = None
    if slot_kind == "bullets":
        inject_positional_bullet_ids_into_pool(valid_paths, required_bullet_ids)
        valid_paths, validity_receipt = _selector_valid_bullet_paths(
            valid_paths,
            required_bullet_ids=required_bullet_ids or (),
            targeting_context=targeting_context,
        )
        valid_paths = [p for p in valid_paths if p.parsed is not None]
        if artifact_dir is not None and validity_receipt is not None:
            (artifact_dir / "bullet_pool_candidate_validity.json").write_text(
                json.dumps(validity_receipt, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        # W4.3 (G15/G17): deterministic numeric fact-entailment exclusion — non-entailed
        # candidates never reach the Claude prompt, the merge, or the all-paths compliance
        # scan. Runs after the id-level validity filter, before the strict-emptiness check.
        valid_paths, entailment_receipt = _selector_numeric_entailed_paths(
            valid_paths,
            required_bullet_ids=required_bullet_ids or (),
            targeting_context=targeting_context,
        )
        valid_paths = [p for p in valid_paths if p.parsed is not None]
        if artifact_dir is not None:
            _append_entailment_receipt_round(artifact_dir, entailment_receipt)
        if not valid_paths and _selector_requires_valid_candidates(
            slot_kind=slot_kind,
            targeting_context=targeting_context,
        ):
            if competencies_selector:
                raise PoolSelectorUnavailableError(
                    "competencies selector unavailable: no eligible candidates after graph/fact filtering"
                )
            return PoolSelectionResult(
                merged_parsed={},
                selections=[],
                judge_output=None,
                selection_mode="blocked_no_selector_eligible_candidates",
                source_path_by_slot={},
            )
        pool_text = _format_bullet_pool(valid_paths, required_bullet_ids or ())
    else:
        pool_text = _format_competency_pool(valid_paths)

    selector_role = selector_role_for_section(section_id, slot_kind=slot_kind)
    provider_key, model, model_source = resolve_selector_provider_model(selector_role)
    prompt = _selection_prompt(
        section_id=section_id,
        slot_kind=slot_kind,
        pool_text=pool_text,
        required_bullet_ids=required_bullet_ids,
        targeting_context=targeting_context,
        min_score_threshold=min_score_threshold,
        selector_name=provider_key,
        regen_note=regen_note,
    )
    input_hash = _sha16(prompt)
    selector_timeout_s = pool_selector_timeout_s(
        default_seconds=(
            DEFAULT_COMPETENCIES_POOL_SELECTOR_TIMEOUT_SECONDS
            if competencies_selector
            else DEFAULT_POOL_SELECTOR_TIMEOUT_SECONDS
        )
    )

    if mode == "mocked" and not competencies_selector:
        return _fallback_first_complete_path(
            valid_paths,
            slot_kind=slot_kind,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
        )

    meta = PROVIDERS.get(provider_key) or {}
    bootstrap_apps_rg_env()
    api_key = os.environ.get(str(meta.get("env") or ""), "").strip()
    if not api_key:
        if competencies_selector:
            raise PoolSelectorUnavailableError(
                f"competencies selector unavailable: missing {provider_key} credentials"
            )
        return _fallback_first_complete_path(
            valid_paths,
            slot_kind=slot_kind,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
        )

    if provider_key == "openai_chatgpt":
        judge_out, parsed_sel = _call_openai_pool_selector(
            api_key=api_key,
            prompt=prompt,
            model=model,
            input_hash=input_hash,
            model_source=model_source,
            artifact_dir=artifact_dir,
            timeout_s=selector_timeout_s,
        )
    elif provider_key == "anthropic_claude":
        judge_out, parsed_sel = _call_anthropic_pool_selector(
            api_key=api_key,
            prompt=prompt,
            model=model,
            input_hash=input_hash,
            model_source=model_source,
            artifact_dir=artifact_dir,
            timeout_s=selector_timeout_s,
        )
    else:
        raise PoolSelectorUnavailableError(
            f"{selector_role} unavailable: unsupported selector provider {provider_key!r}"
        )

    if artifact_dir is not None:
        (artifact_dir / "bullet_pool_claude_selector_judge.json").write_text(
            json.dumps(judge_out.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if parsed_sel is None:
        parsed_sel = _load_selection_doc_from_judge_artifacts(
            judge_out,
            artifact_dir,
            provider_key=judge_out.provider_key,
        )
    if competencies_selector and (parsed_sel is None or judge_out.pass_ is False):
        raise PoolSelectorUnavailableError(
            "competencies selector unavailable: "
            f"{judge_out.exact_provider_error or judge_out.provider_status or 'unavailable'}"
        )
    if parsed_sel is None and judge_out.pass_ is False:
        return _fallback_first_complete_path(
            valid_paths,
            slot_kind=slot_kind,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
        )

    selections = list((parsed_sel or {}).get("selections") or [])
    base = valid_paths[0].parsed
    tc = targeting_context or {}
    rejected_neighbor_audit: dict[str, Any] | None = None

    if slot_kind == "bullets" and required_bullet_ids:
        floor = min_score_threshold
        if floor is None and is_employment_bullet_lane(section_id):
            floor = min_selection_score_for_lane(section_id)
        merged, source_map = merge_bullet_selections(
            valid_paths,
            selections,
            required_bullet_ids=required_bullet_ids,
            base_parsed=base,
            min_score_threshold=floor,
        )
        selection_mode = "claude_employment_top_n_pass"
    elif _is_competencies_graph_pool(section_id, slot_kind):
        floor = min_score_threshold or min_competencies_selection_score()
        merged, source_map, rejected_neighbor_audit = _merge_competencies_graph_pool_with_audit(
            valid_paths,
            selections,
            base_parsed=base,
            min_score_threshold=floor,
            targeting_context=tc,
        )
        selection_mode = (
            "claude_competencies_adaptive_6_8_pass"
            if provider_key == "anthropic_claude"
            else "openai_competencies_adaptive_6_8_pass"
        )
    else:
        merged, source_map = merge_competency_selections(valid_paths, selections, base_parsed=base)
        selection_mode = "claude_per_slot_selection"

    return PoolSelectionResult(
        merged_parsed=merged,
        selections=selections,
        judge_output=judge_out,
        selection_mode=selection_mode,
        source_path_by_slot=source_map,
        rejected_neighbor_audit=rejected_neighbor_audit,
    )


__all__ = [
    "PoolSelectionResult",
    "PoolSelectorUnavailableError",
    "SELECTOR_TIMING_RECEIPT_FILENAME",
    "merge_bullet_selections",
    "merge_competency_selections",
    "pool_selector_timeout_s",
    "run_claude_bullet_pool_selection",
]
