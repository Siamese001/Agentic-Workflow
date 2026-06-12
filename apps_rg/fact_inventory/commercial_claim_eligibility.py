"""SSOT loader and archive trace verification for commercial claim-eligible MEDIUM facts."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHIVE_DIR = _REPO_ROOT / "artifacts/apps_rg/fact_inventory/phase_i_resumes_archive_extracted"
_ELIGIBILITY_REL = Path("apps_rg/config/fact_inventory/commercial_claim_eligibility.yaml")

# Bullet/narrative lanes only — headline and executive_summary remain HIGH-only.
CLAIM_ELIGIBLE_MEDIUM_SECTIONS: frozenset[str] = frozenset(
    {
        "unify_bullets",
        "unify_narrative",
        "ibm_bullets",
        "ibm_narrative",
        "insurtech_bullets",
        "insurtech_narrative",
        "ey_bullets",
        "ey_narrative",
    },
)

VerificationStatusLiteral = Literal[
    "eligible_high_qualitative",
    "eligible_high_with_metrics_requires_source_trace",
    "eligible_medium_with_source_trace",
    "human_review_medium",
    "blocked_low_confidence",
    "blocked_needs_verification",
]

_STOPWORDS = frozenset(
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
        "through",
        "while",
        "about",
        "into",
        "also",
        "must",
        "should",
        "could",
        "would",
        "years",
        "year",
        "experience",
        "including",
        "across",
        "within",
        "using",
        "based",
        "drove",
        "led",
        "held",
    }
)


def repo_root() -> Path:
    return _REPO_ROOT


def eligibility_config_path(repo_root: Path | None = None) -> Path:
    root = repo_root or _REPO_ROOT
    return root / _ELIGIBILITY_REL


def archive_extract_dir(repo_root: Path | None = None) -> Path:
    root = repo_root or _REPO_ROOT
    return root / "artifacts/apps_rg/fact_inventory/phase_i_resumes_archive_extracted"


def ledger_variant_to_archive_basename(variant: str) -> str:
    """Map ledger ``source_resume_variants`` label to Phase I extracted filename."""
    name = variant.strip()
    if not name.lower().endswith(".txt"):
        name = f"{name}.txt"
    # Extracted archives omit ``&`` and similar punctuation from filenames.
    name = name.replace("&", "").replace("–", "-").replace("—", "-")
    return re.sub(r"_+", "_", name.replace(" ", "_"))


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("$", " ")
    lowered = re.sub(r"(\d+)\s*%\s*", r"\1 percent ", lowered)
    lowered = re.sub(r"(\d+)\s*million", r"\1 million ", lowered, flags=re.I)
    lowered = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _significant_tokens(claim_text: str) -> tuple[str, ...]:
    norm = _normalize_text(claim_text)
    parts = re.findall(r"[a-z0-9]+", norm)
    tokens = [p for p in parts if len(p) > 3 and p not in _STOPWORDS]
    # Always keep numeric tokens from metrics
    for m in re.findall(r"\d+", claim_text):
        if m not in tokens:
            tokens.append(m)
    seen: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.append(t)
    return tuple(seen[:24])


def verify_archive_source_trace(
    row: dict[str, Any],
    *,
    archive_dir: Path | None = None,
    min_token_hit_ratio: float = 0.45,
) -> dict[str, Any]:
    """Return audit dict: passed, traces, missing_variants, token_hit_ratio."""
    claim = str(row.get("claim_text") or "")
    tokens = _significant_tokens(claim)
    if not tokens:
        return {
            "passed": False,
            "reason": "no_significant_tokens_in_claim",
            "token_hit_ratio": 0.0,
            "traces": [],
            "missing_variants": list(row.get("source_resume_variants") or []),
        }

    adir = archive_dir or archive_extract_dir()
    traces: list[dict[str, Any]] = []
    missing: list[str] = []
    best_ratio = 0.0

    for variant in row.get("source_resume_variants") or []:
        vstr = str(variant).strip()
        if not vstr:
            continue
        basename = ledger_variant_to_archive_basename(vstr)
        path = adir / basename
        if not path.is_file():
            missing.append(vstr)
            continue
        body_norm = _normalize_text(path.read_text(encoding="utf-8", errors="replace"))
        hits = sum(1 for tok in tokens if tok in body_norm)
        ratio = hits / len(tokens)
        best_ratio = max(best_ratio, ratio)
        traces.append(
            {
                "source_resume_variant": vstr,
                "archive_relpath": str(path.relative_to(_REPO_ROOT)).replace("\\", "/"),
                "token_hit_ratio": round(ratio, 3),
                "tokens_matched": hits,
                "tokens_total": len(tokens),
            }
        )

    passed = bool(traces) and best_ratio >= min_token_hit_ratio
    reason = "ok" if passed else (
        "missing_archive_files" if not traces else "insufficient_token_overlap_with_archive"
    )
    return {
        "passed": passed,
        "reason": reason,
        "token_hit_ratio": round(best_ratio, 3),
        "traces": traces,
        "missing_variants": missing,
    }


@lru_cache(maxsize=1)
def load_claim_eligibility_registry(repo_root_str: str | None = None) -> dict[str, Any]:
    root = Path(repo_root_str) if repo_root_str else _REPO_ROOT
    path = eligibility_config_path(root)
    if not path.is_file():
        return {"schema_version": 1, "facts": {}}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("commercial_claim_eligibility.yaml must be mapping")
    facts = data.get("facts") or {}
    if not isinstance(facts, dict):
        raise TypeError("facts must be mapping")
    return data


def registry_fact_entry(candidate_fact_id: str, *, repo_root: Path | None = None) -> dict[str, Any] | None:
    reg = load_claim_eligibility_registry(str(repo_root or _REPO_ROOT))
    entry = (reg.get("facts") or {}).get(candidate_fact_id)
    return entry if isinstance(entry, dict) else None


def is_claim_eligible_medium(candidate_fact_id: str, *, repo_root: Path | None = None) -> bool:
    entry = registry_fact_entry(candidate_fact_id, repo_root=repo_root)
    return bool(entry and entry.get("claim_eligible_medium") is True)


def claim_eligible_verification_status_for_row(
    row: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> VerificationStatusLiteral | None:
    fid = str(row.get("candidate_fact_id") or "")
    if str(row.get("confidence") or "") != "MEDIUM":
        return None
    entry = registry_fact_entry(fid, repo_root=repo_root)
    if not entry or not entry.get("claim_eligible_medium"):
        return None
    if not entry.get("source_trace_archive_relpaths"):
        return None
    return "eligible_medium_with_source_trace"


def split_medium_rows_by_eligibility(
    medium_rows: list[dict[str, Any]],
    *,
    repo_root: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (claim_eligible_medium_rows, confirmation_queue_medium_rows)."""
    eligible: list[dict[str, Any]] = []
    queue: list[dict[str, Any]] = []
    for row in medium_rows:
        if claim_eligible_verification_status_for_row(row, repo_root=repo_root):
            eligible.append(row)
        else:
            queue.append(row)
    return eligible, queue


def merge_claim_eligible_into_lane_pool(
    high_lane_rows: list[dict[str, Any]],
    claim_eligible_rows: list[dict[str, Any]],
    *,
    lane: str,
    taxonomy: dict[str, Any],
    role_family_priorities: tuple[Any, ...],
) -> list[dict[str, Any]]:
    from apps_rg.fact_inventory import candidate_fact_ledger as ledger_mod

    def _classify_company_lane(company_raw: str) -> str:
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

    priority_rank = {str(rp.role_family): i for i, rp in enumerate(role_family_priorities)}
    if not priority_rank:
        priority_rank = {rid: i for i, rid in enumerate(sorted(ledger_mod.taxonomy_role_family_ids(taxonomy)))}

    def _rank(row: dict[str, Any]) -> tuple[int, int, str]:
        rf_norm = {
            ledger_mod.normalize_role_family_id(str(x), taxonomy=taxonomy)
            for x in row.get("role_families_supported") or []
        }
        overlaps = rf_norm.intersection(priority_rank.keys())
        if overlaps:
            best = min(priority_rank[rf] for rf in overlaps)
            summed = sum(priority_rank[rf] for rf in overlaps)
            return (best, summed, str(row.get("candidate_fact_id") or ""))
        penal = len(priority_rank) + 10
        return (penal, penal, str(row.get("candidate_fact_id") or ""))

    lane_rows = [r for r in claim_eligible_rows if _classify_company_lane(str(r.get("company") or "")) == lane]
    if not lane_rows:
        return high_lane_rows
    merged = list(high_lane_rows) + list(lane_rows)
    return sorted(merged, key=lambda row: (_rank(row), -len(str(row.get("claim_text") or ""))))


__all__ = [
    "CLAIM_ELIGIBLE_MEDIUM_SECTIONS",
    "archive_extract_dir",
    "claim_eligible_verification_status_for_row",
    "eligibility_config_path",
    "is_claim_eligible_medium",
    "ledger_variant_to_archive_basename",
    "load_claim_eligibility_registry",
    "merge_claim_eligible_into_lane_pool",
    "registry_fact_entry",
    "repo_root",
    "split_medium_rows_by_eligibility",
    "verify_archive_source_trace",
]
