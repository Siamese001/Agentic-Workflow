"""narrative_pass.py — Post-process generated_resume.json with HOP-4A..4H.

Pipeline:
  HOP-0.6 — Load CompanyBrief (4-mode loader, fail-loud per D2)
  HOP-2.6 — Extract company facets
  HOP-4A — Headline (Ensemble+Judge)
  HOP-4B — Exec Summary (Ensemble+Judge)
  HOP-4C — ENGINEERING & PLATFORM COMPETENCIES (Ensemble+Judge, set-level)
  HOP-4D — Unify per-bullet (Ensemble+Judge, critical)
  HOP-4E — IBM per-bullet (Ensemble+Judge, critical)
  HOP-4F — TraderSense per-bullet (Judge-only, medium)
  HOP-4G — EY per-bullet (Judge-only, medium)
  HOP-4H — Early Career (deterministic 1-line)
  HOP-4.7 — Marquee outcomes
  → write enriched generated_resume.json + narrative/ archive +
     run_report.json narrative section.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (W7.1).
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from apps_rg.integrations.company_facet_extractor import (
    CompanyFacets,
    extract_company_facets,
)
from apps_rg.integrations.company_research_loader import (
    CompanyResearchLoadOptions,
    load_company_brief,
)
from apps_rg.integrations.hops.competencies_ensemble import generate_competencies
from apps_rg.integrations.hops.early_career_compress import compress_early_career
from apps_rg.integrations.hops.exec_summary_ensemble import generate_exec_summary
from apps_rg.integrations.hops.ey_judge import generate_ey_bullets
from apps_rg.integrations.hops.headline_ensemble import generate_headline
from apps_rg.integrations.hops.ibm_ensemble import generate_ibm_bullets
from apps_rg.integrations.hops.marquee import select_marquee
from apps_rg.integrations.hops.tradersense_judge import generate_tradersense_bullets
from apps_rg.integrations.hops.unify_ensemble import generate_unify_bullets
from apps_rg.integrations.hops._role_bullet_runner import (
    BulletResult,
    NarrativeQualityError,
)
from apps_rg.types.company_research import CompanyBrief, CompanyBriefMissingError
from apps_rg.types.run_report import NarrativeRunReport, SectionVerdict

_log = logging.getLogger("apps_rg.narrative_pass")


def main() -> int:
    parser = argparse.ArgumentParser(prog="apps_rg.narrative_pass")
    parser.add_argument("--target-company", required=True)
    parser.add_argument("--target-role", default=None, help="Target role title (ATS title-match + headline guarantee)")
    parser.add_argument("--research-via", default=None, choices=["apps_research"])
    parser.add_argument("--auto-research-internal", action="store_true")
    parser.add_argument("--auto-research-tavily", action="store_true")
    parser.add_argument(
        "--manual-brief", default="apps_rg/scripts/_interactive_brief.json"
    )
    parser.add_argument(
        "--jd", default="apps_rg/scripts/_interactive_jd.json", help="Path to JD JSON (default: wizard-managed)"
    )
    parser.add_argument(
        "--master-resume",
        default="apps_shared/data/master_resume.json",
        help="Path to master_resume.json",
    )
    parser.add_argument(
        "--input-resume",
        required=True,
        help="Path to generated_resume.json from upstream pipeline",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Run output directory (artifacts/apps_rg/runs/<ts>/)",
    )
    parser.add_argument("--depth", default="standard", choices=["shallow", "standard", "deep"])
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = out_dir / "narrative" / "candidates"
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Load CompanyBrief.
    try:
        brief = load_company_brief(
            CompanyResearchLoadOptions(
                target_company=args.target_company,
                research_via=args.research_via,
                auto_research_internal=args.auto_research_internal,
                auto_research_tavily=args.auto_research_tavily,
                manual_path=Path(args.manual_brief),
                jd_path=Path(args.jd) if args.jd else None,
                depth=args.depth,
            )
        )
    except CompanyBriefMissingError as exc:
        _log.error("[HOP-0.6] CompanyBriefMissingError: %s", exc)
        return 2

    facets = extract_company_facets(brief)
    _log.info("[HOP-2.6] Extracted %d mirror terms", len(facets.language_to_mirror))

    # Load JD facets.
    jd_facets = _load_jd_facets(Path(args.jd))

    # Load existing generated resume.
    input_resume = Path(args.input_resume)
    try:
        resume_data = json.loads(input_resume.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _log.error("[narrative_pass] could not read input resume: %s", exc)
        return 3

    # Persist a provenance copy of the brief.
    (out_dir / "company_research.json").write_text(
        brief.model_dump_json(indent=2), encoding="utf-8"
    )

    report = NarrativeRunReport(
        company_brief_provenance={
            "company": brief.company,
            "source": brief.source.value,
            "fetched_at": brief.fetched_at.isoformat(),
        },
        narrative_candidates_path=str(archive_dir),
    )

    try:
        _run_narrative_pipeline(
            resume_data=resume_data,
            brief=brief,
            facets=facets,
            jd_facets=jd_facets,
            archive_dir=archive_dir,
            report=report,
            target_role=args.target_role or "",
        )
    except NarrativeQualityError as exc:
        _log.error("[narrative_pass] CRITICAL-tier failure: %s", exc)
        report.gate_failures.append({"reason": "critical_section_aborted", "detail": str(exc)})
        _write_outputs(out_dir, resume_data, report)
        return 4

    # Final ATS hardening pass — title-match guarantee + coverage diagnostic.
    # Runs AFTER all per-section HOPs so it operates on the assembled resume.
    # Only in-place edit: prepend JD target title to `headline` if absent.
    # No injection, no new sections — per user directive 2026-05-01, the
    # approved resume sections are fixed. Coverage gaps are surfaced in the
    # scorecard for visibility; authenticity comes from organic narrative.
    from apps_rg.integrations.ats_coverage import apply_ats_hardening

    jd_must_have = _load_jd_must_have(Path(args.jd))
    ats_report = apply_ats_hardening(
        resume_data,
        jd_must_have=jd_must_have,
        target_title=args.target_role or "",
    )
    report.jd_keyword_coverage = ats_report
    _log.info(
        "[narrative_pass] ATS hardening: title_modified=%s organic_coverage=%.2f missing=%s",
        ats_report["title_modified"],
        ats_report["coverage_result"]["coverage"],
        ats_report["coverage_result"]["missing"],
    )

    _write_outputs(out_dir, resume_data, report)
    _log.info("[narrative_pass] Complete. Outputs in %s", out_dir)
    return 0


def _run_narrative_pipeline(
    *,
    resume_data: Dict[str, Any],
    brief: CompanyBrief,
    facets: CompanyFacets,
    jd_facets: List[str],
    archive_dir: Path,
    report: NarrativeRunReport,
    target_role: str = "",
) -> None:
    mirror_terms = list(facets.language_to_mirror) + list(facets.differentiation)
    company = brief.company

    archetype = (
        resume_data.get("archetype")
        or _guess_archetype(jd_facets)
    )
    marquee_seed = _existing_marquee_seeds(resume_data)
    pain_points = list(brief.pain_points_inferred)

    fail_critical_on_unaccepted = _strict_critical_enabled()

    # HOP-4A Headline — target_role is woven INTO the 9-14 word headline
    # so the later ATS title-match pass does not need to prepend (which
    # would push the line over the single-line budget).
    head_res = generate_headline(
        company=company,
        archetype=archetype,
        marquee_outcomes=marquee_seed,
        pain_points=pain_points,
        jd_facets=jd_facets,
        company_facets=facets.all_terms(),
        mirror_terms=mirror_terms,
        seed_text=str(resume_data.get("headline") or ""),
        target_role=target_role,
        archive_dir=archive_dir,
    )
    resume_data["headline"] = head_res.winner.text
    report.add_verdict(_verdict_from(head_res.section_id, "critical", head_res))
    _abort_if_critical(head_res, fail_critical_on_unaccepted)

    # HOP-4B Exec Summary.
    years_of_experience = _compute_years_of_experience(_index_roles(resume_data))
    exec_res = generate_exec_summary(
        company=company,
        archetype=archetype,
        years_of_experience=years_of_experience,
        marquee_outcomes=marquee_seed,
        strategic_priorities=brief.strategic_priorities,
        jd_facets=jd_facets,
        company_facets=facets.all_terms(),
        mirror_terms=mirror_terms,
        seed_text=str(resume_data.get("executive_summary") or ""),
        archive_dir=archive_dir,
    )
    resume_data["executive_summary"] = exec_res.winner.text
    report.add_verdict(_verdict_from(exec_res.section_id, "critical", exec_res))
    _abort_if_critical(exec_res, fail_critical_on_unaccepted)

    # HOP-4C ENGINEERING & PLATFORM COMPETENCIES.
    comp_res = generate_competencies(
        company=company,
        jd_facets=jd_facets,
        company_facets=facets.all_terms(),
        mirror_terms=mirror_terms,
        seed_text="\n".join(_existing_competencies(resume_data)),
        archive_dir=archive_dir,
    )
    resume_data["competencies"] = [
        line.strip(" -•") for line in comp_res.winner.text.splitlines() if line.strip()
    ][:6]
    report.add_verdict(_verdict_from(comp_res.section_id, "critical", comp_res))
    _abort_if_critical(comp_res, fail_critical_on_unaccepted)

    # HOP-4D/4E/4F/4G: per-role bullet rewrites.
    role_table = _index_roles(resume_data)
    role_dispatch = [
        ("unify", generate_unify_bullets, "critical"),
        ("ibm", generate_ibm_bullets, "critical"),
        ("tradersense", generate_tradersense_bullets, "medium"),
        ("ey", generate_ey_bullets, "medium"),
    ]
    pool_hits = 0
    pool_attempts = 0
    for role_id, gen_fn, tier in role_dispatch:
        role_block = _find_role(role_table, role_id)
        if not role_block:
            _log.info("[narrative_pass] role %s not found in resume — skipping", role_id)
            continue
        bullets = _bullets_for_role(role_block)
        if not bullets:
            continue
        try:
            results = gen_fn(
                bullets=bullets,
                jd_facets=jd_facets,
                company_facets=facets.all_terms(),
                mirror_terms=mirror_terms,
                archive_dir=archive_dir,
            )
        except NarrativeQualityError:
            raise
        _apply_bullet_results(role_block, results)
        pool_hits += sum(1 for r in results if r.source == "pool")
        pool_attempts += len(results)
        # Aggregate verdict per role.
        all_accepted = all(r.accepted for r in results)
        avg_composite = (
            sum((r.verdict.composite if r.verdict else 0.0) for r in results) / max(1, len(results))
        )
        first_fail = next((r.verdict.first_failed_gate for r in results if r.verdict and not r.accepted), None)
        report.add_verdict(
            SectionVerdict(
                section_id=f"role_{role_id}",
                tier=tier,
                accepted=all_accepted,
                composite=avg_composite,
                chosen_source="ensemble" if tier == "critical" else "judge_only",
                failed_gate=first_fail,
            )
        )

    # HOP-4H Early Career — deterministic.
    early_roles = [r for r in role_table if _is_early_career(r)]
    if early_roles:
        line = compress_early_career(roles=early_roles)
        resume_data["early_career"] = line
        report.add_verdict(
            SectionVerdict(
                section_id="hop_4h_early_career",
                tier="skip",
                accepted=True,
                composite=1.0,
                chosen_source="deterministic",
            )
        )

    # HOP-4.7 Marquee.
    marquee = select_marquee(
        bullets_by_role=[
            {"role_id": _role_id(r), "bullets": _bullets_for_role(r)}
            for r in role_table
            if not _is_early_career(r)
        ],
        n=4,
    )
    resume_data["marquee_outcomes"] = [m.text for m in marquee]

    if pool_attempts:
        report.pool_first_hit_rate = round(pool_hits / pool_attempts, 4)


def _write_outputs(out_dir: Path, resume_data: Dict[str, Any], report: NarrativeRunReport) -> None:
    (out_dir / "generated_resume.json").write_text(
        json.dumps(resume_data, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out_dir / "narrative" / "scorecard.json").parent.mkdir(parents=True, exist_ok=True)
    (out_dir / "narrative" / "scorecard.json").write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
    )
    # Merge into run_report.json if present.
    run_report_path = out_dir / "run_report.json"
    existing: Dict[str, Any] = {}
    if run_report_path.exists():
        try:
            existing = json.loads(run_report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
    existing["narrative"] = report.to_dict()
    existing["narrative_completed_at"] = datetime.now(timezone.utc).isoformat()
    run_report_path.write_text(
        json.dumps(existing, indent=2, sort_keys=True), encoding="utf-8"
    )


# ----------------------------------------------------------------------- utils

def _strict_critical_enabled() -> bool:
    """When NARRATIVE_LENIENT_CRITICAL=1, critical-tier failures DO NOT abort.

    Default behavior (per locked decision D8) is fail-closed for critical-tier.
    The lenient mode is for offline / stub-generator smoke runs where the
    LLM gateway is intentionally bypassed and gates are expected to fail.
    """
    import os

    return os.getenv("NARRATIVE_LENIENT_CRITICAL", "").strip() not in {"1", "true", "yes"}


def _abort_if_critical(ens_result, strict: bool) -> None:
    if not strict:
        return
    if not ens_result.accepted:
        raise NarrativeQualityError(
            f"critical section {ens_result.section_id} did not pass "
            f"(reason: {ens_result.fail_reason})"
        )


def _verdict_from(section_id: str, tier: str, ens) -> SectionVerdict:
    v = ens.winner.verdict
    return SectionVerdict(
        section_id=section_id,
        tier=tier,
        accepted=ens.accepted,
        composite=v.composite if v else 0.0,
        chosen_source="ensemble",
        failed_gate=(v.first_failed_gate if v else None) if not ens.accepted else None,
    )


# Curated ATS-relevant terms extracted from SVP/executive-AI job descriptions.
# Used when the JD JSON only has `description` text and no pre-structured
# keyword list. The extractor runs against the raw description and returns
# whichever of these terms actually appear — so we never surface spurious
# keywords that aren't in the real posting.
_ATS_CANDIDATE_TERMS: Tuple[str, ...] = (
    # Role / title anchors
    "SVP", "Senior Vice President", "VP", "Chief AI Officer", "CAIO",
    # Agentic / AI platform
    "agentic", "agentic AI", "agentic transformation", "multi-agent",
    "LLM", "generative AI", "GenAI", "RAG", "GraphRAG", "retrieval augmented generation",
    "fine-tuning", "prompt engineering", "orchestration", "autonomy",
    # Platform / infrastructure
    "platform", "cloud", "AWS", "Azure", "GCP", "Kubernetes", "microservices",
    "API", "MLOps", "LLMOps", "observability", "CI/CD",
    # Data / ML
    "machine learning", "ML", "data science", "analytics", "data platform",
    "data strategy", "data governance", "feature engineering", "vector database",
    # Commercial / consulting
    "consulting", "go-to-market", "GTM", "P&L", "revenue", "partnerships",
    "client", "stakeholder", "enterprise", "Fortune 500", "Fortune 1000",
    # Governance / compliance
    "governance", "compliance", "SOC 2", "regulatory", "risk", "audit",
    "policy", "controls", "HIPAA", "SOX", "GDPR",
    # Leadership
    "leadership", "team", "hiring", "mentoring", "strategy", "roadmap",
    "vision", "executive", "C-suite",
    # Delivery
    "delivery", "engagement", "program management", "agile", "scrum",
    "cross-functional", "stakeholder management",
    # Industry verticals (common)
    "financial services", "healthcare", "retail", "insurance", "banking",
)


def _load_jd_must_have(jd_path: Optional[Path]) -> List[str]:
    """Return must-have / hard-requirement terms from the JD for ATS coverage.

    Priority:
      1. Pre-structured lists (`must_have`, `required_skills`, `keywords`)
      2. Extracted from the `description` text by scanning for curated
         ATS-relevant terms that actually appear.
    """
    if not jd_path or not jd_path.exists():
        return []
    try:
        data = json.loads(jd_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out: List[str] = []
    for key in ("must_have", "must_haves", "required_skills", "keywords"):
        v = data.get(key)
        if isinstance(v, list):
            out.extend(str(x).strip() for x in v if x and str(x).strip())
    # Fallback: extract from raw description text.
    if not out:
        description = str(data.get("description") or "")
        title = str(data.get("title") or "")
        blob = f"{title}\n{description}"
        for term in _ATS_CANDIDATE_TERMS:
            pattern = re.compile(rf"(?<![\w-]){re.escape(term)}(?![\w-])", re.IGNORECASE)
            if pattern.search(blob):
                out.append(term)
    # Dedupe case-insensitively, preserve order.
    seen: set = set()
    deduped: List[str] = []
    for term in out:
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(term)
    return deduped


def _load_jd_facets(jd_path: Optional[Path]) -> List[str]:
    if not jd_path or not jd_path.exists():
        return []
    try:
        data = json.loads(jd_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    facets: List[str] = []
    for key in ("must_have", "nice_to_have", "responsibilities", "keywords", "must_haves"):
        v = data.get(key)
        if isinstance(v, list):
            facets.extend(str(x) for x in v if x)
    return facets


def _guess_archetype(jd_facets: List[str]) -> str:
    blob = " ".join(jd_facets).lower()
    if "agentic" in blob:
        return "Agentic Transformation Leader"
    if "data" in blob and "ai" in blob:
        return "Enterprise AI Delivery Leader"
    return "Strategic Advisory Leader"


def _existing_marquee_seeds(resume_data: Dict[str, Any]) -> List[str]:
    if isinstance(resume_data.get("marquee_outcomes"), list):
        return [str(x) for x in resume_data["marquee_outcomes"]][:5]
    return []


def _existing_competencies(resume_data: Dict[str, Any]) -> List[str]:
    """Read competencies from any of the known schema keys.

    Priority order:
      1. competencies / core_competencies        (legacy shape)
      2. engineering_and_platform_competencies   (SVP master shape)
      3. strategic_and_technical_competencies    (canonical alt shape)
    Returns up to 8 lines — HOP-4C will trim to 6.
    """
    cats = resume_data.get("competencies") or resume_data.get("core_competencies") or []
    if isinstance(cats, list) and cats:
        return [str(c) for c in cats][:8]
    # SVP master shape: list of {area, skills}
    for key in ("engineering_and_platform_competencies", "strategic_and_technical_competencies"):
        rich = resume_data.get(key)
        if isinstance(rich, list) and rich:
            out: List[str] = []
            for entry in rich[:8]:
                if isinstance(entry, dict):
                    area = str(entry.get("area") or entry.get("name") or "").strip()
                    skills = str(entry.get("skills") or entry.get("items") or "").strip()
                    if area and skills:
                        out.append(f"{area}: {skills}")
                    elif area:
                        out.append(area)
                elif isinstance(entry, str) and entry.strip():
                    out.append(entry.strip())
            if out:
                return out
    return []


def _index_roles(resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    roles = resume_data.get("professional_experience") or resume_data.get("experience") or resume_data.get("roles") or []
    return [r for r in roles if isinstance(r, dict)]


def _find_role(role_table: List[Dict[str, Any]], role_id: str) -> Optional[Dict[str, Any]]:
    needle = role_id.lower()
    for r in role_table:
        haystack = " ".join(
            str(r.get(k) or "")
            for k in ("role_id", "company", "name", "title")
        ).lower()
        if needle in haystack:
            return r
    return None


def _role_id(role: Dict[str, Any]) -> str:
    return str(role.get("role_id") or role.get("company") or role.get("name") or "?")


def _bullets_for_role(role: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Schema variants observed in repo:
    #   master_resume.json (legacy)         -> "bullets" list[str|dict]
    #   master_resume_svp.json              -> "bullet_pool" list[{label,text,tags}]
    #   misc adapters                       -> "achievements" / "highlights"
    raw = (
        role.get("bullets")
        or role.get("bullet_pool")
        or role.get("achievements")
        or role.get("highlights")
        or []
    )
    out: List[Dict[str, Any]] = []
    for b in raw:
        if isinstance(b, str):
            out.append({"text": b, "pool_variants": []})
        elif isinstance(b, dict):
            text = str(
                b.get("text")
                or b.get("primary")
                or b.get("default")
                or ""
            )
            if not text:
                continue
            variants_raw = b.get("variants") or b.get("pool_variants") or []
            variants: List[str] = []
            for v in variants_raw:
                if isinstance(v, str):
                    variants.append(v)
                elif isinstance(v, dict):
                    variants.append(str(v.get("text") or v.get("primary") or ""))
            out.append({"text": text, "pool_variants": [v for v in variants if v]})
    return out


def _apply_bullet_results(role: Dict[str, Any], results: List[BulletResult]) -> None:
    # Determine which schema key holds the bullets (preserve in place).
    for key in ("bullets", "bullet_pool", "achievements", "highlights"):
        if key in role and isinstance(role[key], list):
            target_key = key
            break
    else:
        return  # no bullet container — nothing to write back
    raw = role[target_key]
    new_bullets: List[Any] = []
    for idx, original in enumerate(raw):
        chosen = next((r for r in results if r.bullet_index == idx), None)
        if chosen is None:
            new_bullets.append(original)
            continue
        if isinstance(original, dict):
            updated = dict(original)
            updated["text"] = chosen.chosen_text
            new_bullets.append(updated)
        else:
            new_bullets.append(chosen.chosen_text)
    role[target_key] = new_bullets


_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def _extract_start_year(role: Dict[str, Any]) -> Optional[int]:
    """Parse start year from heterogeneous date schemas (mirror of _extract_end_year)."""
    direct = role.get("start_year") or role.get("start")
    try:
        if direct is not None:
            return int(direct)
    except (TypeError, ValueError):
        pass
    dates = role.get("dates") or {}
    start = dates.get("start") if isinstance(dates, dict) else None
    if isinstance(start, str):
        m = _YEAR_RE.search(start)
        if m:
            return int(m.group(0))
    return None


def _compute_years_of_experience(roles: List[Dict[str, Any]]) -> Optional[int]:
    """Compute total years of professional experience from the earliest role start year.

    Used by HOP-4B exec_summary to state accurate tenure instead of defaulting
    to '15+ years', which under-sells a 20+ year career.
    """
    import datetime as _dt

    start_years = [y for y in (_extract_start_year(r) for r in roles) if y]
    if not start_years:
        return None
    earliest = min(start_years)
    current = _dt.date.today().year
    diff = current - earliest
    if diff <= 0:
        return None
    return diff


def _extract_end_year(role: Dict[str, Any]) -> Optional[int]:
    """Extract a numeric end year from heterogeneous date schemas.

    Recognizes:
      - role["end_year"] / role["end"] as int
      - role["dates"]["end"] as 'YYYY' / 'February 2023' / 'Present'
      - 'Present' / 'Current' -> current year (treated as ongoing)
    """
    import datetime as _dt

    direct = role.get("end_year") or role.get("end")
    try:
        if direct is not None:
            return int(direct)
    except (TypeError, ValueError):
        pass

    dates = role.get("dates") or {}
    end = dates.get("end") if isinstance(dates, dict) else None
    if isinstance(end, str):
        if end.strip().lower() in {"present", "current", "now"}:
            return _dt.date.today().year
        m = _YEAR_RE.search(end)
        if m:
            return int(m.group(0))
    return None


def _is_early_career(role: Dict[str, Any]) -> bool:
    """Roles whose end year is before 2010 are 'early career'.

    A role is NOT early-career if its end year cannot be determined
    AND its title/company has no 'early' or 'earlier career' marker.
    Fixes the 2026-05-01 misclassification where modern SVP roles got
    bucketed into 2002-2009 because dates were strings, not ints.
    """
    end_year = _extract_end_year(role)
    if end_year is not None:
        return end_year < 2010
    title_blob = " ".join(
        str(role.get(k) or "") for k in ("name", "company", "title")
    ).lower()
    return "early career" in title_blob or "earlier career" in title_blob


if __name__ == "__main__":
    sys.exit(main())
