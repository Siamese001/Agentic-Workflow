"""Executive-summary SRFS wiring: arsenal projection as ranking signal (fact_id proof only)."""
from __future__ import annotations

from typing import Any, Literal

from apps_rg.fact_inventory.executive_summary_arsenal_projection import (
    ExecutiveSummaryArsenalProjection,
    project_executive_summary_arsenal,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    JD_BRIEFING_FORBIDDEN_FACT_ID_PREFIXES,
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    RoleFamilyPriority,
    SelectedLedgerFactSlice,
    ledger_row_to_slice,
)

ExecFactBucket = Literal[
    "architecture",
    "governance",
    "commercialization",
    "actuarial_quant",
    "partner_gtm",
    "other",
]

DEFAULT_ARSENAL_ROLE_FAMILY_KEY = "SVP_ENGINEERING_AI_PLATFORM"

_PROFILE_SLOT_QUOTAS: dict[str, dict[ExecFactBucket, int]] = {
    "SVP_ENGINEERING_AI_PLATFORM": {
        "architecture": 2,
        "governance": 1,
        "commercialization": 1,
        "actuarial_quant": 1,
        "partner_gtm": 0,
        "other": 0,
    },
    "AI_FINANCIAL_SERVICES": {
        "governance": 2,
        "actuarial_quant": 2,
        "architecture": 1,
        "commercialization": 1,
        "partner_gtm": 0,
        "other": 0,
    },
    "ANTHROPIC_PARTNERSHIPS_APPLIED_AI": {
        "partner_gtm": 2,
        "architecture": 1,
        "commercialization": 1,
        "governance": 0,
        "actuarial_quant": 0,
        "other": 0,
    },
}


def _is_jd_briefing_fact_id(fact_id: str) -> bool:
    low = fact_id.lower()
    return any(low.startswith(p) or p in low for p in JD_BRIEFING_FORBIDDEN_FACT_ID_PREFIXES)


def _is_skill_id(value: str) -> bool:
    return value.startswith("skill_")


def resolve_arsenal_role_family_key(
    *,
    role_family_priorities: tuple[RoleFamilyPriority, ...],
    target_role: str,
    jd_text: str,
    briefing_text: str = "",
) -> str:
    """Map inferred taxonomy priorities + targeting text → arsenal profile key."""
    corpus = f"{target_role} {jd_text} {briefing_text}".lower()
    top_rf = role_family_priorities[0].role_family if role_family_priorities else ""

    if top_rf == "PARTNERSHIPS_GTM" or (
        "partnership" in corpus and "alliance" in corpus
    ):
        return "ANTHROPIC_PARTNERSHIPS_APPLIED_AI"

    fin_signals = (
        "financial services",
        "governance",
        "risk",
        "basel",
        "ccar",
        "actuarial",
        "derivative",
        "hedging",
        "greeks",
    )
    if top_rf == "AI_GOVERNANCE_RISK" or any(s in corpus for s in fin_signals):
        if top_rf != "ENGINEERING_PLATFORM" and (
            top_rf in ("AI_GOVERNANCE_RISK", "STRATEGIC_FINANCE", "QUANT_TRADING_HPC")
            or sum(1 for s in fin_signals if s in corpus) >= 2
        ):
            return "AI_FINANCIAL_SERVICES"

    if top_rf in ("ENGINEERING_PLATFORM", "AI_SOLUTIONS_ARCHITECTURE", "EXECUTIVE_LEADERSHIP"):
        return "SVP_ENGINEERING_AI_PLATFORM"

    if "anthropic" in corpus or "applied ai" in corpus:
        return "ANTHROPIC_PARTNERSHIPS_APPLIED_AI"

    return DEFAULT_ARSENAL_ROLE_FAMILY_KEY


def classify_exec_fact_bucket(row: dict[str, Any]) -> ExecFactBucket:
    df = str(row.get("domain_family") or "")
    fid = str(row.get("candidate_fact_id") or "")
    if df == "PARTNERSHIPS_GTM" or "partnerships_gtm" in fid:
        return "partner_gtm"
    if df == "QUANT_TRADING_HPC" or "quant_hpc" in fid or fid == "fact_certs_001":
        return "actuarial_quant"
    if df == "AI_GOVERNANCE_RISK" or "governance" in fid:
        return "governance"
    if df in ("EXECUTIVE_LEADERSHIP", "REVENUE_OPERATIONS", "STRATEGIC_FINANCE") or fid.startswith(
        "fact_exec_"
    ):
        return "commercialization"
    if df in ("ENGINEERING_PLATFORM", "AI_SOLUTIONS_ARCHITECTURE", "DATA_ANALYTICS_LEADERSHIP"):
        return "architecture"
    return "other"


def external_proof_fact_ids_from_projection(
    arsenal_ledger: dict[str, Any],
    projection: ExecutiveSummaryArsenalProjection,
) -> frozenset[str]:
    """Fact IDs linkable from externally-eligible arsenal skills only (never skill_id)."""
    skill_by_id = {
        str(r["skill_id"]): r
        for r in (arsenal_ledger.get("skill_rows") or [])
        if isinstance(r, dict) and r.get("skill_id")
    }
    out: set[str] = set()
    for sid in projection.external_eligible_skill_ids:
        row = skill_by_id.get(sid)
        if not row or not skill_row_eligible_for_external_claim(row):
            continue
        for fid in row.get("fact_id_links") or []:
            fs = str(fid).strip()
            if not fs or _is_skill_id(fs) or _is_jd_briefing_fact_id(fs):
                continue
            out.add(fs)
    return frozenset(out)


def _partner_gtm_optional(
    role_family_priorities: tuple[RoleFamilyPriority, ...],
) -> bool:
    for rp in role_family_priorities[:3]:
        if rp.role_family == "PARTNERSHIPS_GTM" and rp.score > 0:
            return True
    return False


def _slot_quotas_for_profile(
    role_family_key: str,
    *,
    role_family_priorities: tuple[RoleFamilyPriority, ...],
) -> dict[ExecFactBucket, int]:
    base = dict(_PROFILE_SLOT_QUOTAS.get(role_family_key, _PROFILE_SLOT_QUOTAS[DEFAULT_ARSENAL_ROLE_FAMILY_KEY]))
    if role_family_key == "SVP_ENGINEERING_AI_PLATFORM" and _partner_gtm_optional(role_family_priorities):
        base["partner_gtm"] = 1
    return base


def _row_sort_key(
    row: dict[str, Any],
    *,
    external_fact_ids: frozenset[str],
    bucket: ExecFactBucket,
    bucket_wanted: int,
) -> tuple[int, int, str]:
    fid = str(row["candidate_fact_id"])
    arsenal_boost = 0 if fid in external_fact_ids else 1
    bucket_boost = 0 if bucket_wanted > 0 else 2
    return (arsenal_boost, bucket_boost, fid)


def compute_executive_summary_reserved_fact_ids(
    pool_sorted: list[dict[str, Any]],
    *,
    projection: ExecutiveSummaryArsenalProjection,
    role_family_key: str,
    arsenal_ledger: dict[str, Any],
    role_family_priorities: tuple[RoleFamilyPriority, ...],
) -> tuple[str, ...]:
    """Reserve exec-critical facts before headline _take_unique consumes them."""
    external_ids = external_proof_fact_ids_from_projection(arsenal_ledger, projection)
    quotas = _slot_quotas_for_profile(role_family_key, role_family_priorities=role_family_priorities)
    reserved: list[str] = []
    used: set[str] = set()
    df_counts: dict[str, int] = {}

    for bucket, quota in quotas.items():
        if quota <= 0:
            continue
        picked = 0
        candidates = [
            r
            for r in pool_sorted
            if classify_exec_fact_bucket(r) == bucket and r["candidate_fact_id"] not in used
        ]
        candidates.sort(
            key=lambda r: _row_sort_key(
                r,
                external_fact_ids=external_ids,
                bucket=bucket,
                bucket_wanted=quota,
            ),
        )
        for row in candidates:
            fid = row["candidate_fact_id"]
            df = str(row.get("domain_family") or "unknown")
            if df_counts.get(df, 0) >= 2:
                continue
            if external_ids and fid not in external_ids and bucket in (
                "actuarial_quant",
                "partner_gtm",
                "governance",
            ):
                if not (row.get("source_resume_variants") or row.get("claim_text")):
                    continue
            used.add(fid)
            df_counts[df] = df_counts.get(df, 0) + 1
            reserved.append(fid)
            picked += 1
            if picked >= quota:
                break
        if picked < quota and bucket == "partner_gtm" and role_family_key == "ANTHROPIC_PARTNERSHIPS_APPLIED_AI":
            for row in pool_sorted:
                if picked >= quota:
                    break
                fid = row["candidate_fact_id"]
                if fid in used:
                    continue
                claim = str(row.get("claim_text") or "").lower()
                if fid not in external_ids and "aws" not in claim and "partner" not in claim:
                    continue
                df = str(row.get("domain_family") or "unknown")
                if df_counts.get(df, 0) >= 2:
                    continue
                used.add(fid)
                df_counts[df] = df_counts.get(df, 0) + 1
                reserved.append(fid)
                picked += 1

    for fid in projection.linked_fact_ids:
        fs = str(fid)
        if fs in used or _is_skill_id(fs) or _is_jd_briefing_fact_id(fs):
            continue
        if fs not in external_ids:
            continue
        row = next((r for r in pool_sorted if r["candidate_fact_id"] == fs), None)
        if row is None:
            continue
        df = str(row.get("domain_family") or "unknown")
        if df_counts.get(df, 0) >= 2:
            continue
        used.add(fs)
        df_counts[df] = df_counts.get(df, 0) + 1
        reserved.append(fs)

    return tuple(dict.fromkeys(reserved))


def allocate_executive_summary_with_arsenal(
    pool_sorted: list[dict[str, Any]],
    *,
    reserved_ids: tuple[str, ...],
    used_global: set[str],
    taxonomy: dict[str, Any],
    projection: ExecutiveSummaryArsenalProjection,
    role_family_key: str,
    arsenal_ledger: dict[str, Any],
    role_family_priorities: tuple[RoleFamilyPriority, ...],
    max_total: int = 10,
    max_per_domain_family: int = 2,
) -> list[SelectedLedgerFactSlice]:
    """Allocate executive_summary slice using arsenal ranking; proof remains fact_id-only."""
    external_ids = external_proof_fact_ids_from_projection(arsenal_ledger, projection)
    quotas = _slot_quotas_for_profile(role_family_key, role_family_priorities=role_family_priorities)
    row_by_id = {r["candidate_fact_id"]: r for r in pool_sorted}
    df_counts: dict[str, int] = {}
    slices: list[SelectedLedgerFactSlice] = []
    bucket_filled: dict[ExecFactBucket, int] = {b: 0 for b in quotas}

    def _append(row: dict[str, Any], hint: str) -> bool:
        fid = row["candidate_fact_id"]
        if fid in used_global or _is_skill_id(fid):
            return False
        df = str(row.get("domain_family") or "unknown")
        if df_counts.get(df, 0) >= max_per_domain_family:
            return False
        used_global.add(fid)
        df_counts[df] = df_counts.get(df, 0) + 1
        slices.append(ledger_row_to_slice(row, taxonomy=taxonomy, allocation_hint=hint))
        return True

    for fid in reserved_ids:
        row = row_by_id.get(fid)
        if row is None:
            continue
        bucket = classify_exec_fact_bucket(row)
        if _append(row, f"executive_summary|arsenal_reserved:{bucket}"):
            bucket_filled[bucket] = bucket_filled.get(bucket, 0) + 1
        if len(slices) >= max_total:
            return slices

    def _fill_priority(row: dict[str, Any]) -> tuple[int, int, int, str]:
        bucket = classify_exec_fact_bucket(row)
        fid = str(row["candidate_fact_id"])
        need = quotas.get(bucket, 0) - bucket_filled.get(bucket, 0)
        return (
            0 if need > 0 else 1,
            0 if fid in external_ids else 1,
            0 if bucket != "other" else 1,
            fid,
        )

    for row in sorted(pool_sorted, key=_fill_priority):
        if len(slices) >= max_total:
            break
        if row["candidate_fact_id"] in used_global:
            continue
        bucket = classify_exec_fact_bucket(row)
        if _append(row, f"executive_summary|arsenal:{bucket}"):
            bucket_filled[bucket] = bucket_filled.get(bucket, 0) + 1

    return slices


def build_executive_summary_arsenal_context(
    *,
    repo_root: Any,
    role_family_priorities: tuple[RoleFamilyPriority, ...],
    target_role: str,
    jd_text: str,
    briefing_text: str,
) -> tuple[str, ExecutiveSummaryArsenalProjection, dict[str, Any], frozenset[str]]:
    """Load arsenal, project, return (role_key, projection, ledger, external_proof_fact_ids)."""
    arsenal_ledger = load_master_skills_arsenal_ledger(repo_root=repo_root)
    role_key = resolve_arsenal_role_family_key(
        role_family_priorities=role_family_priorities,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
    )
    projection = project_executive_summary_arsenal(role_key, ledger=arsenal_ledger)
    external_ids = external_proof_fact_ids_from_projection(arsenal_ledger, projection)
    return role_key, projection, arsenal_ledger, external_ids


__all__ = [
    "allocate_executive_summary_with_arsenal",
    "build_executive_summary_arsenal_context",
    "classify_exec_fact_bucket",
    "compute_executive_summary_reserved_fact_ids",
    "external_proof_fact_ids_from_projection",
    "resolve_arsenal_role_family_key",
]
