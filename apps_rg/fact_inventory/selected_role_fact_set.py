"""Bounded role-family adaptive fact selection (apps_rg) → SelectedRoleFactSet artifacts.

Downstream résumé section generation stays unwired until a future task.

Invariant: JD/briefing never mint ledger facts; candidate rows stay non-canonical.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from apps_rg.fact_inventory import candidate_fact_ledger as ledger_mod

_REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[2]

SECTION_KEYS: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
    "executive_summary",
    "headline",
)

SelectionPolicyLiteral = Literal["role_family_keyword_v1_bounded_ledger"]
CompanyLaneLiteral = Literal["ibm_only", "unify", "insurtech", "ey", "other"]
VerificationStatusLiteral = Literal[
    "eligible_high_qualitative",
    "eligible_high_with_metrics_requires_source_trace",
    "eligible_medium_with_source_trace",
    "human_review_medium",
    "blocked_low_confidence",
    "blocked_needs_verification",
]
UnsupportedJDKindLiteral = Literal[
    "jd_sentence_no_matching_taxonomy_keywords",
    "jd_sentence_no_high_confidence_ledger_overlap_under_priorities",
]

_STOPWORD = frozenset(
    {
        "that",
        "this",
        "with",
        "from",
        "your",
        "will",
        "have",
        "been",
        "were",
        "they",
        "their",
        "what",
        "when",
        "where",
        "which",
        "while",
        "about",
        "such",
        "into",
        "also",
        "must",
        "should",
        "could",
        "would",
        "years",
        "year",
        "experience",
    }
)

_DEFAULT_CONFIDENCE_POLICY = (
    "HIGH → external-validation candidate buckets by section (ledger-provisional facts). "
    "MEDIUM with registry claim_eligible_medium + archive source_trace → bullet/narrative "
    "section pools only (verification=eligible_medium_with_source_trace). "
    "Other MEDIUM → human confirmation queue only. "
    "LOW / NEEDS_VERIFICATION → blocked from external-ready selections."
)


def digest_text(sample: str) -> str:
    return hashlib.sha256(sample.encode("utf-8")).hexdigest()


def utc_timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _norm_whitespace(txt: str) -> str:
    return re.sub(r"\s+", " ", txt.strip())


def classify_company_lane(company_raw: str) -> CompanyLaneLiteral:
    u = company_raw.upper()
    if "UNIFY" in u:
        return "unify"
    if "IBM" in u:
        return "ibm_only"
    if "INSUR" in u or "POLICY ADMINISTRATION" in u:
        return "insurtech"
    if "ERNST" in u or "YOUNG" in u or u.strip() == "EY" or " EY " in f" {u} ":
        return "ey"
    return "other"


def _token_set(text: str) -> frozenset[str]:
    lowered = text.lower()
    parts = re.findall(r"[a-z0-9]+", lowered)
    return frozenset(p for p in parts if len(p) > 3 and p not in _STOPWORD)


@dataclass(frozen=True)
class RoleFamilyPriority:
    role_family: str
    score: int
    evidence_terms: tuple[str, ...]
    source_channels: tuple[str, ...]


@dataclass(frozen=True)
class SelectedLedgerFactSlice:
    candidate_fact_id: str
    claim_text: str
    confidence: str
    source_resume_variants: tuple[str, ...]
    role_families_supported: tuple[str, ...]
    capability_tags: tuple[str, ...]
    metric_values: tuple[str, ...]
    allowed_resume_use: str
    risk_notes: str
    company: str
    domain_family: str
    verification_status: VerificationStatusLiteral
    company_lane: CompanyLaneLiteral
    allocation_hint: str = ""
    claim_eligible_medium: bool = False
    source_trace_archive_relpaths: tuple[str, ...] = ()


@dataclass(frozen=True)
class BlockedFactSlice:
    candidate_fact_id: str
    confidence: str
    block_reason: str
    verification_status: VerificationStatusLiteral


@dataclass(frozen=True)
class HumanConfirmationQueueItem:
    fact: SelectedLedgerFactSlice
    queue_reason: str
    suggested_section: str


@dataclass(frozen=True)
class UnsupportedJDNeed:
    theme_label: str
    jd_evidence_snippet: str
    kind: UnsupportedJDKindLiteral


@dataclass(frozen=True)
class SelectedRoleFactSet:
    selection_id: str
    target_company: str
    target_role: str
    jd_digest: str
    briefing_digest: str
    source_ledger_path: str
    taxonomy_ref: str
    selected_at: str
    role_family_priorities: tuple[RoleFamilyPriority, ...]
    selected_facts_by_section: dict[str, list[SelectedLedgerFactSlice]]
    selected_facts_by_role_family: dict[str, tuple[str, ...]]
    blocked_facts: tuple[BlockedFactSlice, ...]
    facts_requiring_human_confirmation: tuple[HumanConfirmationQueueItem, ...]
    unsupported_jd_needs: tuple[UnsupportedJDNeed, ...]
    selection_policy: SelectionPolicyLiteral
    confidence_policy: str
    no_jd_fact_minting_assertion: Literal[True]
    candidate_not_canonical_assertion: Literal[True]
    competencies_capability_tags_ordered: tuple[str, ...]


def ledger_row_to_slice(
    row: dict[str, Any],
    *,
    taxonomy: dict[str, Any],
    allocation_hint: str = "",
) -> SelectedLedgerFactSlice:
    rf_norm = tuple(
        ledger_mod.normalize_role_family_id(str(x), taxonomy=taxonomy) for x in row["role_families_supported"]
    )
    conf = row["confidence"]
    metrics = tuple(str(x) for x in row.get("metric_values") or [])
    if conf == "HIGH":
        vstat: VerificationStatusLiteral = (
            "eligible_high_with_metrics_requires_source_trace" if metrics else "eligible_high_qualitative"
        )
    elif conf == "MEDIUM":
        from apps_rg.fact_inventory.commercial_claim_eligibility import (
            claim_eligible_verification_status_for_row,
        )

        eligible_vstat = claim_eligible_verification_status_for_row(row)
        vstat = eligible_vstat if eligible_vstat else "human_review_medium"
    elif conf == "LOW":
        vstat = "blocked_low_confidence"
    else:
        vstat = "blocked_needs_verification"

    lane = classify_company_lane(str(row.get("company") or ""))
    claim_eligible = vstat == "eligible_medium_with_source_trace"
    trace_paths: tuple[str, ...] = ()
    if claim_eligible:
        from apps_rg.fact_inventory.commercial_claim_eligibility import registry_fact_entry

        entry = registry_fact_entry(str(row["candidate_fact_id"]))
        if entry:
            raw_paths = entry.get("source_trace_archive_relpaths") or []
            trace_paths = tuple(str(p) for p in raw_paths if str(p).strip())
    return SelectedLedgerFactSlice(
        candidate_fact_id=row["candidate_fact_id"],
        claim_text=str(row["claim_text"]),
        confidence=conf,
        source_resume_variants=tuple(str(x) for x in row["source_resume_variants"]),
        role_families_supported=rf_norm,
        capability_tags=tuple(str(x) for x in row.get("capability_tags") or []),
        metric_values=metrics,
        allowed_resume_use=str(row.get("allowed_resume_use") or ""),
        risk_notes=str(row.get("risk_notes") or ""),
        company=str(row.get("company") or ""),
        domain_family=str(row.get("domain_family") or ""),
        verification_status=vstat,
        company_lane=lane,
        allocation_hint=allocation_hint,
        claim_eligible_medium=claim_eligible,
        source_trace_archive_relpaths=trace_paths,
    )


def infer_role_family_priorities(
    *,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    taxonomy: dict[str, Any],
) -> tuple[RoleFamilyPriority, ...]:
    corpuses = (
        ("target_role", target_role.lower()),
        ("jd", jd_text.lower()),
        ("briefing", briefing_text.lower()),
    )
    aggregated: dict[str, dict[str, Any]] = {}

    rf_rows = taxonomy.get("role_families") or []
    if not isinstance(rf_rows, list):
        raise TypeError("taxonomy.role_families must be list")

    for row in sorted(rf_rows, key=lambda r: str(r.get("id", ""))):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            continue
        rf_id = row["id"]
        kws_raw = row.get("jd_signal_keywords") or []
        if not isinstance(kws_raw, list):
            raise TypeError(f"jd_signal_keywords must be list for {rf_id}")
        kws = sorted(str(k).lower().strip() for k in kws_raw if str(k).strip())
        evid: list[str] = []
        chan: set[str] = set()
        score = 0
        for kw in kws:
            matched_any = False
            for channel, blob in corpuses:
                if kw in blob:
                    matched_any = True
                    chan.add(channel)
            if matched_any:
                score += 1
                evid.append(kw)
        uniq: list[str] = []
        seen: set[str] = set()
        for e in evid:
            if e not in seen:
                seen.add(e)
                uniq.append(e)
        aggregated[rf_id] = {
            "score": score,
            "evidence_terms": tuple(uniq),
            "source_channels": tuple(sorted(chan)),
        }

    ordered = sorted(aggregated.keys(), key=lambda rid: (-aggregated[rid]["score"], rid))
    out = tuple(
        RoleFamilyPriority(
            role_family=rid,
            score=aggregated[rid]["score"],
            evidence_terms=tuple(aggregated[rid]["evidence_terms"]),
            source_channels=tuple(aggregated[rid]["source_channels"]),
        )
        for rid in ordered
        if aggregated[rid]["score"] > 0
    )
    return out


def _priority_rank_map(role_family_priorities: tuple[RoleFamilyPriority, ...]) -> dict[str, int]:
    return {rp.role_family: idx for idx, rp in enumerate(role_family_priorities)}


def _fallback_rank_map(taxonomy: dict[str, Any]) -> dict[str, int]:
    ids = sorted(ledger_mod.taxonomy_role_family_ids(taxonomy))
    return {rid: idx for idx, rid in enumerate(ids)}


def _effective_rank_map(
    role_family_priorities: tuple[RoleFamilyPriority, ...],
    taxonomy: dict[str, Any],
) -> dict[str, int]:
    pr = _priority_rank_map(role_family_priorities)
    return pr if pr else _fallback_rank_map(taxonomy)


def _row_rank_tuple(
    row: dict[str, Any],
    *,
    pr: dict[str, int],
    taxonomy: dict[str, Any],
) -> tuple[int, int, str]:
    rf_norm = {
        ledger_mod.normalize_role_family_id(str(x), taxonomy=taxonomy) for x in row.get("role_families_supported") or []
    }
    overlaps = rf_norm.intersection(pr.keys())
    if overlaps:
        best = min(pr[rf] for rf in overlaps)
        summed = sum(pr[rf] for rf in overlaps)
        return (best, summed, row["candidate_fact_id"])
    penal = len(pr) + 10
    return (penal, penal, row["candidate_fact_id"])


def sorted_high_rows_global(
    high_rows: list[dict[str, Any]],
    *,
    role_family_priorities: tuple[RoleFamilyPriority, ...],
    taxonomy: dict[str, Any],
) -> list[dict[str, Any]]:
    pr = _effective_rank_map(role_family_priorities, taxonomy)
    return sorted(
        high_rows,
        key=lambda r: (_row_rank_tuple(r, pr=pr, taxonomy=taxonomy), -len(str(r.get("claim_text") or "")), r["candidate_fact_id"]),
    )


def _jd_sentences(jd_text: str) -> list[str]:
    raw = jd_text.strip()
    if not raw:
        return []
    chunks = re.split(r"[\.\n\r;]+", raw)
    return [_norm_whitespace(s) for s in chunks if len(_norm_whitespace(s)) > 16]


def _taxonomy_keyword_vocab(taxonomy: dict[str, Any]) -> tuple[str, ...]:
    vocab: list[str] = []
    rf_rows = taxonomy.get("role_families") or []
    if not isinstance(rf_rows, list):
        raise TypeError("role_families must be list")
    for row in rf_rows:
        if not isinstance(row, dict):
            continue
        kws = row.get("jd_signal_keywords") or []
        if isinstance(kws, list):
            for k in kws:
                ks = str(k).lower().strip()
                if ks:
                    vocab.append(ks)
    return tuple(sorted(set(vocab)))


def _merged_priority_terms(role_family_priorities: tuple[RoleFamilyPriority, ...]) -> tuple[str, ...]:
    acc: list[str] = []
    seen: set[str] = set()
    for rp in role_family_priorities:
        for t in rp.evidence_terms:
            if t not in seen:
                seen.add(t)
                acc.append(t)
    return tuple(acc)


def build_unsupported_jd_needs(
    *,
    jd_text: str,
    taxonomy: dict[str, Any],
    role_family_priorities: tuple[RoleFamilyPriority, ...],
    high_rows: list[dict[str, Any]],
) -> tuple[UnsupportedJDNeed, ...]:
    vocab = _taxonomy_keyword_vocab(taxonomy)
    high_claim_tokens = _token_set(" ".join(str(f.get("claim_text") or "") for f in high_rows))
    priority_terms_low = tuple(t.lower() for t in _merged_priority_terms(role_family_priorities))

    out: list[UnsupportedJDNeed] = []
    for sent in _jd_sentences(jd_text):
        s_low = sent.lower()
        taxonomy_hit = any(kw in s_low for kw in vocab)
        if not taxonomy_hit:
            out.append(
                UnsupportedJDNeed(
                    theme_label=f"snippet_{digest_text(sent)[:10]}",
                    jd_evidence_snippet=sent[:320],
                    kind="jd_sentence_no_matching_taxonomy_keywords",
                )
            )
            continue

        jd_tokens = _token_set(sent)
        overlap = jd_tokens & high_claim_tokens if jd_tokens else frozenset()
        if jd_tokens and not overlap and role_family_priorities:
            prio_hit = any(pt in s_low for pt in priority_terms_low if pt.strip())
            if prio_hit:
                out.append(
                    UnsupportedJDNeed(
                        theme_label=f"prio_gap_{digest_text(sent)[:12]}",
                        jd_evidence_snippet=sent[:320],
                        kind="jd_sentence_no_high_confidence_ledger_overlap_under_priorities",
                    )
                )
    return tuple(out)


def _suggest_confirmation_section(row: dict[str, Any]) -> str:
    lane = classify_company_lane(str(row.get("company") or ""))
    if lane == "ibm_only":
        return "ibm_bullets"
    if lane == "unify":
        return "unify_bullets"
    if lane == "insurtech":
        return "insurtech_bullets"
    if lane == "ey":
        return "ey_bullets"
    return "executive_summary"


def _partition_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    high: list[dict[str, Any]] = []
    medium: list[dict[str, Any]] = []
    low: list[dict[str, Any]] = []
    needsv: list[dict[str, Any]] = []
    for r in rows:
        c = r.get("confidence")
        if c == "HIGH":
            high.append(r)
        elif c == "MEDIUM":
            medium.append(r)
        elif c == "LOW":
            low.append(r)
        elif c == "NEEDS_VERIFICATION":
            needsv.append(r)
        else:
            raise ValueError(f"unknown confidence {c!r} on {r.get('candidate_fact_id')}")
    return high, medium, low, needsv


def _take_unique(
    pool: list[dict[str, Any]],
    n: int,
    *,
    used: set[str],
    taxonomy: dict[str, Any],
    hint: str,
) -> tuple[list[SelectedLedgerFactSlice], set[str]]:
    if n <= 0:
        return [], used
    out: list[SelectedLedgerFactSlice] = []
    for row in pool:
        fid = row["candidate_fact_id"]
        if fid in used:
            continue
        used.add(fid)
        out.append(ledger_row_to_slice(row, taxonomy=taxonomy, allocation_hint=hint))
        if len(out) >= n:
            break
    return out, used


def _filter_lane(pool: list[dict[str, Any]], lane: CompanyLaneLiteral) -> list[dict[str, Any]]:
    if lane == "other":
        return [r for r in pool if classify_company_lane(str(r.get("company") or "")) == "other"]
    return [r for r in pool if classify_company_lane(str(r.get("company") or "")) == lane]


def _exclude_ids(pool: list[dict[str, Any]], banned: set[str]) -> list[dict[str, Any]]:
    return [r for r in pool if r["candidate_fact_id"] not in banned]


def _sorted_narrative_pool(pool: list[dict[str, Any]], *, min_len: int = 140) -> list[dict[str, Any]]:
    narrowed = [r for r in pool if len(str(r.get("claim_text") or "")) >= min_len]
    return sorted(narrowed, key=lambda r: (-len(str(r.get("claim_text") or "")), r["candidate_fact_id"]))


def _allocate_exec_summary_facts(
    pool_sorted: list[dict[str, Any]],
    *,
    used_global: set[str],
    taxonomy: dict[str, Any],
    max_total: int = 10,
    max_per_domain_family: int = 2,
) -> list[SelectedLedgerFactSlice]:
    df_counts: dict[str, int] = {}
    slices: list[SelectedLedgerFactSlice] = []
    for row in pool_sorted:
        fid = row["candidate_fact_id"]
        if fid in used_global:
            continue
        df = str(row.get("domain_family") or "unknown")
        if df_counts.get(df, 0) >= max_per_domain_family:
            continue
        used_global.add(fid)
        df_counts[df] = df_counts.get(df, 0) + 1
        slices.append(ledger_row_to_slice(row, taxonomy=taxonomy, allocation_hint="executive_summary"))
        if len(slices) >= max_total:
            break
    return slices


def _build_selected_facts_by_role_family(
    section_map: dict[str, list[SelectedLedgerFactSlice]],
) -> dict[str, tuple[str, ...]]:
    order: dict[str, list[str]] = {}
    for sec in SECTION_KEYS:
        if sec == "competencies":
            continue
        for sl in section_map.get(sec, []):
            fid = sl.candidate_fact_id
            for rf in sl.role_families_supported:
                bucket = order.setdefault(rf, [])
                if fid not in bucket:
                    bucket.append(fid)
    return {rid: tuple(ids) for rid, ids in sorted(order.items(), key=lambda t: t[0])}


def _competencies_tags(section_map: dict[str, list[SelectedLedgerFactSlice]]) -> tuple[str, ...]:
    tags_seen: dict[str, None] = {}
    for sec in SECTION_KEYS:
        if sec == "competencies":
            continue
        for sl in section_map.get(sec, []):
            for t in sl.capability_tags:
                tags_seen.setdefault(t, None)
    return tuple(sorted(tags_seen))


def selected_role_fact_set_to_json_dict(srfs: SelectedRoleFactSet) -> dict[str, Any]:
    return asdict(srfs)


def rendered_markdown_summary(srfs: SelectedRoleFactSet) -> str:
    lines: list[str] = []
    lines.append("# Selected Role Fact Set (bounded selection)")
    lines.append("")
    lines.append(f"**selection_id**: `{srfs.selection_id}`")
    lines.append(f"**selected_at**: `{srfs.selected_at}`")
    lines.append(f"**target_company**: {srfs.target_company}")
    lines.append(f"**target_role**: {srfs.target_role}")
    lines.append(f"**source_ledger_path**: `{srfs.source_ledger_path}`")
    lines.append(f"**taxonomy_ref**: `{srfs.taxonomy_ref}`")
    lines.append(f"**no_jd_fact_minting_assertion**: `{srfs.no_jd_fact_minting_assertion}`")
    lines.append(f"**candidate_not_canonical_assertion**: `{srfs.candidate_not_canonical_assertion}`")
    lines.append("")
    lines.append("## Role-family priorities")
    for rp in srfs.role_family_priorities:
        et = ", ".join(rp.evidence_terms)
        ch = ", ".join(rp.source_channels)
        lines.append(f"- **{rp.role_family}** (score={rp.score}; evidence_terms: {et}; sources: {ch})")
    if not srfs.role_family_priorities:
        lines.append("- *(none inferred — internal ranking falls back alphabetically)*")
    lines.append("")
    lines.append("## Selected facts per section (HIGH-confidence external-validation candidates)")
    for sec in SECTION_KEYS:
        items = srfs.selected_facts_by_section.get(sec, [])
        if sec == "competencies":
            lines.append(f"### `{sec}`")
            lines.append("- fact projection rows intentionally empty until wiring")
            ct = ", ".join(srfs.competencies_capability_tags_ordered)
            lines.append(f"- **competencies_capability_tags_ordered**: {ct}")
            continue
        lines.append(f"### `{sec}`")
        for sl in items:
            lines.append(
                f"- `{sl.candidate_fact_id}` [{sl.confidence}] lane={sl.company_lane} verification={sl.verification_status} "
                f"metrics={list(sl.metric_values)}",
            )
    lines.append("")
    lines.append("## Facts requiring human confirmation (MEDIUM ledger rows)")
    for q in srfs.facts_requiring_human_confirmation:
        fid = q.fact.candidate_fact_id
        lines.append(f"- `{fid}` suggested_section=`{q.suggested_section}` | {q.queue_reason}")
    lines.append("")
    lines.append("## Blocked facts (LOW / NEEDS_VERIFICATION)")
    for bf in srfs.blocked_facts:
        lines.append(f"- `{bf.candidate_fact_id}` [{bf.confidence}] {bf.block_reason}")
    lines.append("")
    lines.append("## Unsupported / unclassified JD themes (JD is labeling-only evidence)")
    for u in srfs.unsupported_jd_needs:
        lines.append(f"- `{u.kind}` | excerpt: {u.jd_evidence_snippet[:240]}")
    lines.append("")
    lines.append("## Confidence policy")
    lines.append(srfs.confidence_policy)
    return "\n".join(lines) + "\n"


_OFFLINE_SRFS_JSON_WRITE_ENV = "APPS_RG_OFFLINE_SRFS_JSON_WRITE"


def write_selected_role_fact_set_artifacts(
    srfs: SelectedRoleFactSet,
    *,
    repo_root: Path | None = None,
    timestamp_slug: str | None = None,
    fact_inventory_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Offline inventory CLI only — product runtime uses in-memory ``select_candidate_facts_for_role``."""
    import os

    if os.environ.get(_OFFLINE_SRFS_JSON_WRITE_ENV) != "1":
        raise RuntimeError(
            "write_selected_role_fact_set_artifacts removed from product path; "
            f"set {_OFFLINE_SRFS_JSON_WRITE_ENV}=1 for apps_rg.fact_inventory.select_role_facts only"
        )
    root = repo_root or _REPO_ROOT_DEFAULT
    slug = timestamp_slug or srfs.selected_at
    out_dir = fact_inventory_dir or (root / "artifacts" / "apps_rg" / "fact_inventory")
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"selected_role_fact_set_{slug}.json"
    md_path = out_dir / f"selected_role_fact_set_{slug}.md"
    json_path.write_text(
        json.dumps(selected_role_fact_set_to_json_dict(srfs), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(rendered_markdown_summary(srfs), encoding="utf-8")
    return json_path, md_path


def select_candidate_facts_for_role(
    *,
    target_company: str,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    ledger: dict[str, Any],
    taxonomy: dict[str, Any],
    source_ledger_path: str | None = None,
    taxonomy_ref: str | None = None,
    selection_policy: SelectionPolicyLiteral = "role_family_keyword_v1_bounded_ledger",
    now_slug: str | None = None,
    repo_root: Path | None = None,
) -> SelectedRoleFactSet:
    root = repo_root or _REPO_ROOT_DEFAULT
    jd_norm = jd_text.strip()
    br_norm = briefing_text.strip()
    ledger_display = source_ledger_path or str(root / ledger_mod.REPO_APPS_REL)
    tax_display = taxonomy_ref or str(root / ledger_mod.TAXONOMY_REL)

    jd_d_full = digest_text(jd_norm)
    br_d_full = digest_text(br_norm)

    facts = ledger.get("candidate_facts") or []
    if not isinstance(facts, list):
        raise TypeError("candidate_facts malformed")
    row_dicts = [r for r in facts if isinstance(r, dict)]
    for row in row_dicts:
        ledger_mod.validate_fact_shape(row)

    ids_sorted_digest = digest_text(json.dumps(sorted(r["candidate_fact_id"] for r in row_dicts)))
    selection_key_material = "|".join(
        (target_company.strip(), target_role.strip(), jd_d_full, br_d_full, ledger_display, tax_display, ids_sorted_digest),
    )
    deterministic_id_part = digest_text(selection_key_material)[:48]
    selected_at = now_slug or utc_timestamp_slug()
    selection_id = f"srf_sel_{deterministic_id_part}_{selected_at}"

    role_family_priorities = infer_role_family_priorities(
        target_role=target_role,
        jd_text=jd_norm,
        briefing_text=br_norm,
        taxonomy=taxonomy,
    )

    high_rows, medium_rows, low_rows, nv_rows = _partition_rows(row_dicts)

    from apps_rg.fact_inventory.commercial_claim_eligibility import (
        merge_claim_eligible_into_lane_pool,
        split_medium_rows_by_eligibility,
    )

    claim_eligible_medium_rows, medium_confirmation_rows = split_medium_rows_by_eligibility(
        medium_rows,
        repo_root=root,
    )

    blocked: list[BlockedFactSlice] = []
    for r in low_rows:
        pj = ledger_row_to_slice(r, taxonomy=taxonomy, allocation_hint="blocked_low")
        blocked.append(
            BlockedFactSlice(
                candidate_fact_id=pj.candidate_fact_id,
                confidence=pj.confidence,
                block_reason="LOW_CONFIDENCE_BLOCK_FOR_EXTERNAL_SELECTION",
                verification_status="blocked_low_confidence",
            )
        )
    for r in nv_rows:
        pj = ledger_row_to_slice(r, taxonomy=taxonomy, allocation_hint="blocked_needs_verification")
        blocked.append(
            BlockedFactSlice(
                candidate_fact_id=pj.candidate_fact_id,
                confidence=pj.confidence,
                block_reason="METRIC_OR_ASSERTION_NEEDS_SOURCE_VERIFICATION",
                verification_status="blocked_needs_verification",
            )
        )

    high_sorted_global = sorted_high_rows_global(high_rows, role_family_priorities=role_family_priorities, taxonomy=taxonomy)
    high_unify_sorted = sorted_high_rows_global(
        _filter_lane(high_rows, "unify"),
        role_family_priorities=role_family_priorities,
        taxonomy=taxonomy,
    )
    high_ibm_sorted = sorted_high_rows_global(
        _filter_lane(high_rows, "ibm_only"),
        role_family_priorities=role_family_priorities,
        taxonomy=taxonomy,
    )
    high_insurtech_sorted = sorted_high_rows_global(
        _filter_lane(high_rows, "insurtech"),
        role_family_priorities=role_family_priorities,
        taxonomy=taxonomy,
    )
    high_ey_sorted = sorted_high_rows_global(
        _filter_lane(high_rows, "ey"),
        role_family_priorities=role_family_priorities,
        taxonomy=taxonomy,
    )

    confirmation_queue = tuple(
        HumanConfirmationQueueItem(
            fact=ledger_row_to_slice(r, taxonomy=taxonomy, allocation_hint="medium_confirmation"),
            queue_reason=(
                "MEDIUM_FACT_REQUIRES_AMIT_CONFIRMATION_BEFORE_EXTERNAL_USE — "
                f"suggested_allocation={_suggest_confirmation_section(r)}."
            ),
            suggested_section=_suggest_confirmation_section(r),
        )
        for r in sorted(
            medium_confirmation_rows,
            key=lambda row: (
                classify_company_lane(str(row.get("company") or "")),
                row["candidate_fact_id"],
            ),
        )
    )

    selected_by_section: dict[str, list[SelectedLedgerFactSlice]] = {k: [] for k in SECTION_KEYS}
    used_global: set[str] = set()

    from apps_rg.fact_inventory.exec_summary_graph_projection_w4b import (
        DEFAULT_ARSENAL_ROLE_FAMILY_KEY,
        allocate_executive_summary_with_arsenal,
        build_executive_summary_arsenal_context,
        compute_executive_summary_reserved_fact_ids,
    )

    exec_reserved: tuple[str, ...] = ()
    try:
        role_key, projection, arsenal_ledger, _ext_ids = build_executive_summary_arsenal_context(
            repo_root=root,
            role_family_priorities=role_family_priorities,
            target_role=target_role,
            jd_text=jd_norm,
            briefing_text=br_norm,
        )
        exec_reserved = compute_executive_summary_reserved_fact_ids(
            high_sorted_global,
            projection=projection,
            role_family_key=role_key,
            arsenal_ledger=arsenal_ledger,
            role_family_priorities=role_family_priorities,
        )
    except FileNotFoundError:
        role_key = DEFAULT_ARSENAL_ROLE_FAMILY_KEY
        projection = None
        arsenal_ledger = None

    headline_pool = _exclude_ids(high_sorted_global, set(exec_reserved))
    headline_vals, used_global = _take_unique(
        headline_pool, 5, used=used_global, taxonomy=taxonomy, hint="headline"
    )

    if projection is not None and arsenal_ledger is not None:
        exec_slices = allocate_executive_summary_with_arsenal(
            high_sorted_global,
            reserved_ids=exec_reserved,
            used_global=used_global,
            taxonomy=taxonomy,
            projection=projection,
            role_family_key=role_key,
            arsenal_ledger=arsenal_ledger,
            role_family_priorities=role_family_priorities,
            max_total=10,
            max_per_domain_family=2,
        )
    else:
        exec_pool = [r for r in high_sorted_global if r["candidate_fact_id"] not in used_global]
        exec_slices = _allocate_exec_summary_facts(
            exec_pool,
            used_global=used_global,
            taxonomy=taxonomy,
            max_total=10,
            max_per_domain_family=2,
        )

    ub_pool = merge_claim_eligible_into_lane_pool(
        _exclude_ids(high_unify_sorted, used_global),
        claim_eligible_medium_rows,
        lane="unify",
        taxonomy=taxonomy,
        role_family_priorities=role_family_priorities,
    )
    ub_slices, used_global = _take_unique(
        ub_pool,
        6 if ub_pool else 0,
        used=used_global,
        taxonomy=taxonomy,
        hint="unify_bullets",
    )
    unify_bullet_ids = {s.candidate_fact_id for s in ub_slices}

    unify_n_base = merge_claim_eligible_into_lane_pool(
        _exclude_ids(high_unify_sorted, unify_bullet_ids | used_global),
        claim_eligible_medium_rows,
        lane="unify",
        taxonomy=taxonomy,
        role_family_priorities=role_family_priorities,
    )
    unify_n_pool = [
        r
        for r in _sorted_narrative_pool(unify_n_base, min_len=120)
        if classify_company_lane(str(r.get("company") or "")) == "unify"
    ]
    un_slices, used_global = _take_unique(
        unify_n_pool,
        5 if unify_n_pool else 0,
        used=used_global,
        taxonomy=taxonomy,
        hint="unify_narrative",
    )

    ib_sorted = sorted_high_rows_global(high_ibm_sorted, role_family_priorities=role_family_priorities, taxonomy=taxonomy)
    ib_b_pool = merge_claim_eligible_into_lane_pool(
        _exclude_ids(ib_sorted, used_global),
        claim_eligible_medium_rows,
        lane="ibm_only",
        taxonomy=taxonomy,
        role_family_priorities=role_family_priorities,
    )
    ib_b_slices, used_global = _take_unique(
        ib_b_pool,
        min(6, len(ib_b_pool)) if ib_b_pool else 0,
        used=used_global,
        taxonomy=taxonomy,
        hint="ibm_bullets",
    )
    ib_bullet_ids_local = {s.candidate_fact_id for s in ib_b_slices}

    ib_n_base = merge_claim_eligible_into_lane_pool(
        _exclude_ids(ib_sorted, ib_bullet_ids_local | used_global),
        claim_eligible_medium_rows,
        lane="ibm_only",
        taxonomy=taxonomy,
        role_family_priorities=role_family_priorities,
    )
    ib_n_candidates = [
        r
        for r in _sorted_narrative_pool(ib_n_base, min_len=100)
        if classify_company_lane(str(r.get("company") or "")) == "ibm_only"
    ]
    ibn_slices, used_global = _take_unique(
        ib_n_candidates,
        min(5, len(ib_n_candidates)) if ib_n_candidates else 0,
        used=used_global,
        taxonomy=taxonomy,
        hint="ibm_narrative",
    )

    ins_b_pool = merge_claim_eligible_into_lane_pool(
        _exclude_ids(high_insurtech_sorted, used_global),
        claim_eligible_medium_rows,
        lane="insurtech",
        taxonomy=taxonomy,
        role_family_priorities=role_family_priorities,
    )
    ins_b_slices, used_global = _take_unique(
        ins_b_pool,
        min(3, len(ins_b_pool)) if ins_b_pool else 0,
        used=used_global,
        taxonomy=taxonomy,
        hint="insurtech_bullets",
    )
    ins_bullet_ids_local = {s.candidate_fact_id for s in ins_b_slices}
    ins_n_candidates = [
        r
        for r in _sorted_narrative_pool(
            _exclude_ids(high_insurtech_sorted, ins_bullet_ids_local | used_global),
            min_len=80,
        )
        if classify_company_lane(str(r.get("company") or "")) == "insurtech"
    ]
    insn_slices, used_global = _take_unique(
        ins_n_candidates,
        min(3, len(ins_n_candidates)) if ins_n_candidates else 0,
        used=used_global,
        taxonomy=taxonomy,
        hint="insurtech_narrative",
    )

    ey_b_pool = merge_claim_eligible_into_lane_pool(
        _exclude_ids(high_ey_sorted, used_global),
        claim_eligible_medium_rows,
        lane="ey",
        taxonomy=taxonomy,
        role_family_priorities=role_family_priorities,
    )
    ey_b_slices, used_global = _take_unique(
        ey_b_pool,
        min(3, len(ey_b_pool)) if ey_b_pool else 0,
        used=used_global,
        taxonomy=taxonomy,
        hint="ey_bullets",
    )
    ey_bullet_ids_local = {s.candidate_fact_id for s in ey_b_slices}
    ey_n_candidates = [
        r
        for r in _sorted_narrative_pool(
            _exclude_ids(high_ey_sorted, ey_bullet_ids_local | used_global),
            min_len=80,
        )
        if classify_company_lane(str(r.get("company") or "")) == "ey"
    ]
    eyn_slices, used_global = _take_unique(
        ey_n_candidates,
        min(3, len(ey_n_candidates)) if ey_n_candidates else 0,
        used=used_global,
        taxonomy=taxonomy,
        hint="ey_narrative",
    )

    selected_by_section["headline"] = headline_vals
    selected_by_section["executive_summary"] = exec_slices
    selected_by_section["unify_bullets"] = ub_slices
    selected_by_section["unify_narrative"] = un_slices
    selected_by_section["ibm_bullets"] = ib_b_slices
    selected_by_section["ibm_narrative"] = ibn_slices
    selected_by_section["insurtech_bullets"] = ins_b_slices
    selected_by_section["insurtech_narrative"] = insn_slices
    selected_by_section["ey_bullets"] = ey_b_slices
    selected_by_section["ey_narrative"] = eyn_slices
    selected_by_section["competencies"] = [
        *ub_slices[:2],
        *ib_b_slices[:2],
        *ins_b_slices[:1],
        *ey_b_slices[:1],
        *headline_vals[:2],
    ][:8]

    comps_tags = _competencies_tags(selected_by_section)

    unsupported = build_unsupported_jd_needs(
        jd_text=jd_norm,
        taxonomy=taxonomy,
        role_family_priorities=role_family_priorities,
        high_rows=high_rows,
    )

    flat_sel = [
        *headline_vals,
        *exec_slices,
        *ub_slices,
        *un_slices,
        *ib_b_slices,
        *ibn_slices,
        *ins_b_slices,
        *insn_slices,
        *ey_b_slices,
        *eyn_slices,
        *selected_by_section["competencies"],
    ]
    ledger_mod.assert_selection_bounded_to_ledger([s.candidate_fact_id for s in flat_sel], ledger)
    ledger_mod.assert_selection_bounded_to_ledger([q.fact.candidate_fact_id for q in confirmation_queue], ledger)

    by_rf = _build_selected_facts_by_role_family(selected_by_section)

    return SelectedRoleFactSet(
        selection_id=selection_id,
        target_company=target_company.strip(),
        target_role=target_role.strip(),
        jd_digest=jd_d_full[:64],
        briefing_digest=br_d_full[:64],
        source_ledger_path=ledger_display,
        taxonomy_ref=tax_display,
        selected_at=selected_at,
        role_family_priorities=role_family_priorities,
        selected_facts_by_section=selected_by_section,
        selected_facts_by_role_family=by_rf,
        blocked_facts=tuple(blocked),
        facts_requiring_human_confirmation=confirmation_queue,
        unsupported_jd_needs=unsupported,
        selection_policy=selection_policy,
        confidence_policy=_DEFAULT_CONFIDENCE_POLICY,
        no_jd_fact_minting_assertion=True,
        candidate_not_canonical_assertion=True,
        competencies_capability_tags_ordered=comps_tags,
    )


__all__ = [
    "BlockedFactSlice",
    "HumanConfirmationQueueItem",
    "RoleFamilyPriority",
    "SECTION_KEYS",
    "SelectionPolicyLiteral",
    "SelectedLedgerFactSlice",
    "SelectedRoleFactSet",
    "UnsupportedJDNeed",
    "build_unsupported_jd_needs",
    "classify_company_lane",
    "digest_text",
    "infer_role_family_priorities",
    "ledger_row_to_slice",
    "rendered_markdown_summary",
    "select_candidate_facts_for_role",
    "selected_role_fact_set_to_json_dict",
    "sorted_high_rows_global",
    "utc_timestamp_slug",
    "write_selected_role_fact_set_artifacts",
]
