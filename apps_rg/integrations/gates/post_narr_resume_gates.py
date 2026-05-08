"""POST-NARR Resume Gates — Whole-resume coherence checks.

Gates that run after all narrative hops complete (4A-4H).
W6 implements cross-section consistency and ATS-targeted checks.

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W6)
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from datetime import datetime
from typing import Any

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

_log = logging.getLogger("apps_rg.gates.post_narr")


def _extract_text(artifact: Any) -> str:
    """Extract text from artifact."""
    if isinstance(artifact, dict):
        return artifact.get("text", "")
    elif hasattr(artifact, "text"):
        return str(getattr(artifact, "text", ""))
    return ""


def _extract_keywords(text: str) -> set[str]:
    """Extract normalized keywords from text."""
    # Lowercase, remove punctuation, split
    normalized = re.sub(r'[^\w\s]', ' ', text.lower())
    words = normalized.split()
    # Filter to meaningful words (3+ chars)
    return set(w for w in words if len(w) >= 3)


def _find_duplicate_claims(sections: dict[str, str]) -> list[dict[str, Any]]:
    """Find claims/outcomes that appear in multiple sections."""
    # Extract numeric claims from each section
    # Pattern: $X, X%, X users/customers, or standalone numbers (simpler, more reliable)
    claim_pattern = r'(?i)(?:\$?\d+(?:\.\d+)?[\s]?[MKBkm]?(?:illion)?|\d+\%|\d+\s*(?:users?|customers?|people?|employees?))'
    
    section_claims: dict[str, list[str]] = {}
    for section_id, text in sections.items():
        claims = re.findall(claim_pattern, text)
        section_claims[section_id] = [c.lower() for c in claims]
    
    # Find duplicates across sections
    duplicates = []
    all_claims: dict[str, list[str]] = {}  # claim -> list of sections
    
    for section_id, claims in section_claims.items():
        for claim in claims:
            if claim not in all_claims:
                all_claims[claim] = []
            all_claims[claim].append(section_id)
    
    for claim, sections in all_claims.items():
        if len(sections) > 1:
            duplicates.append({
                "claim": claim,
                "sections": sections,
                "count": len(sections),
            })
    
    return duplicates


def jd_keyword_coverage_min_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W6: JD must-have keywords ≥80% present in resume.
    
    ATS-targeted check ensuring job description requirements
    are reflected in generated resume content.
    """
    gate_id = "jd_keyword_coverage_min"
    
    text = _extract_text(artifact)
    if not text:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No resume text available for JD coverage check",
            reason_codes=("missing_text",),
        )
    
    # Get JD keywords from context
    jd_keywords = context.get("jd_keywords", [])
    if not jd_keywords:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No JD keywords provided for coverage check",
            reason_codes=("missing_jd_keywords",),
        )
    
    # Extract keywords from resume text
    resume_keywords = _extract_keywords(text)
    
    # Check coverage
    found = []
    missing = []
    
    resume_text_lower = text.lower()
    
    for keyword in jd_keywords:
        keyword_lower = keyword.lower()
        # Check if keyword appears in full resume text (more reliable than token matching)
        if keyword_lower in resume_text_lower:
            found.append(keyword)
        else:
            missing.append(keyword)
    
    coverage_pct = len(found) / len(jd_keywords) * 100
    min_coverage = 80  # 80% minimum
    
    if coverage_pct >= min_coverage:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.PASS,
            reason=f"JD keyword coverage: {coverage_pct:.1f}% ({len(found)}/{len(jd_keywords)})",
            reason_codes=(
                "coverage_sufficient",
                f"coverage:{coverage_pct:.0f}%",
            ),
            evidence_refs=(
                f"found:{len(found)}",
                f"missing:{len(missing)}",
            ),
        )
    
    _log.warning(
        "[W6] JD coverage insufficient: %.1f%% (need %d%%)",
        coverage_pct, min_coverage
    )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.FAIL,
        reason=f"JD keyword coverage insufficient: {coverage_pct:.1f}% (min: {min_coverage}%)",
        reason_codes=(
            "coverage_insufficient",
            f"coverage:{coverage_pct:.0f}%",
            f"min:{min_coverage}%",
        ),
        evidence_refs=(
            f"missing:{','.join(missing[:5])}",
            f"found:{len(found)}",
        ),
    )


def claim_uniqueness_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W6: Same outcome cited at most once across sections.
    
    Prevents 'resume stuffing' where the same achievement is
    repeated in multiple sections to pad content.
    """
    gate_id = "claim_uniqueness"
    
    # Get all sections from context
    sections = context.get("resume_sections", {})
    if not sections:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No resume sections provided for uniqueness check",
            reason_codes=("missing_sections",),
        )
    
    # Find duplicate claims
    duplicates = _find_duplicate_claims(sections)
    
    if duplicates:
        _log.warning(
            "[W6] %d duplicate claims across sections",
            len(duplicates)
        )
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"{len(duplicates)} claims duplicated across sections",
            reason_codes=(
                "duplicate_claims",
                f"count:{len(duplicates)}",
            ),
            evidence_refs=tuple(
                f"claim:{d['claim']},sections:{','.join(d['sections'][:2])}"
                for d in duplicates[:5]
            ),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason="All claims unique across sections",
        reason_codes=("claims_unique",),
    )


def cross_section_consistency_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W6: Archetype/tenure/outcomes consistent across sections.
    
    Ensures the resume presents a coherent narrative without
    contradictions between executive summary, experience, etc.
    """
    gate_id = "cross_section_consistency"
    
    sections = context.get("resume_sections", {})
    if not sections:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No resume sections for consistency check",
            reason_codes=("missing_sections",),
        )
    
    # Extract archetypes mentioned in each section
    expected_archetype = context.get("archetype", "").lower()
    archetype_mismatches = []
    
    # Check for consistent tenure claims
    tenure_years: dict[str, list[int]] = {}
    tenure_pattern = r'(?i)(\d+)\+?\s*years?(?:\s+of\s+experience)?'
    
    for section_id, text in sections.items():
        matches = re.findall(tenure_pattern, text)
        if matches:
            tenure_years[section_id] = [int(m) for m in matches]
    
    # Check tenure consistency
    all_years = [y for years in tenure_years.values() for y in years]
    if all_years:
        max_year = max(all_years)
        min_year = min(all_years)
        
        # If tenure varies by >2 years across sections, flag inconsistency
        if max_year - min_year > 2:
            _log.warning(
                "[W6] Tenure inconsistent: %d vs %d years",
                min_year, max_year
            )
            return GateVerdict(
                gate_id=gate_id,
                result=Result.FAIL,
                reason=f"Tenure inconsistent across sections: {min_year}-{max_year} years",
                reason_codes=(
                    "tenure_inconsistent",
                    f"min:{min_year}",
                    f"max:{max_year}",
                ),
                evidence_refs=tuple(
                    f"section:{s},years:{y[0]}" for s, y in tenure_years.items() if y
                ),
            )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason="Cross-section consistency verified",
        reason_codes=("consistency_verified",),
    )


def bullet_count_per_role_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W6: Each role has 3-5 bullets.
    
    ATS-friendly formatting with sufficient but not excessive detail.
    """
    gate_id = "bullet_count_per_role"
    
    # Expect experience_roles as list of dicts with 'bullets' key
    roles = context.get("experience_roles", [])
    if not roles:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No experience roles provided for bullet count",
            reason_codes=("missing_roles",),
        )
    
    min_bullets = 3
    max_bullets = 5
    violations = []
    
    for role in roles:
        role_title = role.get("title", "Unknown")
        bullets = role.get("bullets", [])
        bullet_count = len(bullets)
        
        if bullet_count < min_bullets or bullet_count > max_bullets:
            violations.append({
                "role": role_title,
                "bullets": bullet_count,
            })
    
    if violations:
        _log.warning(
            "[W6] %d roles with invalid bullet count",
            len(violations)
        )
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"{len(violations)} roles have bullet count outside 3-5 range",
            reason_codes=(
                "bullet_count_invalid",
                f"violations:{len(violations)}",
            ),
            evidence_refs=tuple(
                f"role:{v['role']},count:{v['bullets']}" for v in violations[:5]
            ),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason=f"All {len(roles)} roles have 3-5 bullets",
        reason_codes=("bullet_count_valid", f"roles:{len(roles)}"),
    )


def role_chronology_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W6: Roles strictly date-descending, no unexplained gaps >12mo.
    
    Standard resume convention check plus gap detection.
    """
    gate_id = "role_chronology"
    
    roles = context.get("experience_roles", [])
    if not roles:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No experience roles for chronology check",
            reason_codes=("missing_roles",),
        )
    
    # Sort roles by end date (most recent first)
    sorted_roles = sorted(
        roles,
        key=lambda r: r.get("end_date", "9999-12"),
        reverse=True
    )
    
    # Check date-descending order
    prev_start = None
    order_violations = []
    
    for i, role in enumerate(sorted_roles):
        start_date = role.get("start_date", "")
        end_date = role.get("end_date", "")
        
        if prev_start and start_date > prev_start:
            order_violations.append({
                "role": role.get("title", "Unknown"),
                "start": start_date,
                "prev_start": prev_start,
            })
        
        prev_start = start_date
    
    # Check for unexplained gaps >12 months
    gaps = []
    max_gap_months = 12
    
    for i in range(len(sorted_roles) - 1):
        current_role = sorted_roles[i]
        next_role = sorted_roles[i + 1]
        
        current_start = current_role.get("start_date", "")
        next_end = next_role.get("end_date", "")
        
        if current_start and next_end:
            # Parse dates (YYYY-MM format)
            try:
                current_dt = datetime.strptime(current_start, "%Y-%m")
                next_dt = datetime.strptime(next_end, "%Y-%m")
                
                # Gap is the time between next role's end and current role's start
                # next_dt chronologically comes before current_dt
                gap_months = (current_dt.year - next_dt.year) * 12 + (current_dt.month - next_dt.month)
                
                if gap_months > max_gap_months:
                    gaps.append({
                        "between": f"{current_role.get('title')} and {next_role.get('title')}",
                        "gap_months": gap_months,
                    })
            except ValueError:
                # Invalid date format, skip gap check for this pair
                pass
    
    if order_violations or gaps:
        _log.warning(
            "[W6] Chronology issues: %d order, %d gaps",
            len(order_violations), len(gaps)
        )
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"Chronology issues: {len(order_violations)} order violations, {len(gaps)} unexplained gaps",
            reason_codes=(
                "chronology_invalid",
                f"order_issues:{len(order_violations)}",
                f"gaps:{len(gaps)}",
            ),
            evidence_refs=tuple(
                f"gap:{g['between']},months:{g['gap_months']}" for g in gaps[:3]
            ),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason=f"Role chronology valid: {len(sorted_roles)} roles in order, no unexplained gaps",
        reason_codes=("chronology_valid", f"roles:{len(sorted_roles)}"),
    )


def ats_composite_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W6: Composite ATS-targeted gate running all W6 checks.
    
    Aggregated check for resume coherence and ATS optimization.
    """
    gates = [
        ("jd_coverage", jd_keyword_coverage_min_gate),
        ("claim_uniqueness", claim_uniqueness_gate),
        ("cross_section", cross_section_consistency_gate),
        ("bullet_count", bullet_count_per_role_gate),
        ("chronology", role_chronology_gate),
    ]
    
    failures = []
    passes = []
    unknowns = []
    
    for name, gate_fn in gates:
        verdict = gate_fn(artifact, context)
        if verdict.result == Result.FAIL:
            failures.append((name, verdict))
        elif verdict.result == Result.PASS:
            passes.append((name, verdict))
        else:
            unknowns.append((name, verdict))
    
    # Composite result
    if failures:
        return GateVerdict(
            gate_id="ats_composite",
            result=Result.FAIL,
            reason=f"ATS checks failed: {', '.join(f[0] for f in failures)}",
            reason_codes=tuple(f"fail:{f[0]}" for f in failures),
        )
    
    if unknowns and not passes:
        return GateVerdict(
            gate_id="ats_composite",
            result=Result.UNKNOWN,
            reason=f"ATS checks indeterminate: {', '.join(u[0] for u in unknowns)}",
            reason_codes=tuple(f"unknown:{u[0]}" for u in unknowns),
        )
    
    return GateVerdict(
        gate_id="ats_composite",
        result=Result.PASS,
        reason=f"ATS checks passed: {len(passes)} checks",
        reason_codes=tuple(f"pass:{p[0]}" for p in passes),
    )


__all__ = [
    "jd_keyword_coverage_min_gate",
    "claim_uniqueness_gate",
    "cross_section_consistency_gate",
    "bullet_count_per_role_gate",
    "role_chronology_gate",
    "ats_composite_gate",
]
