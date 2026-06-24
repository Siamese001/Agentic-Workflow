"""Load candidate skills/fact ledger and role-family taxonomy (apps_rg only).

JD and briefing texts are targeting inputs — they MUST NOT synthesize ledger facts.

This module does not mutate generation seams; ingest + helpers for forthcoming selection logic.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any

REPO_APPS_REL = Path("artifacts") / "apps_rg" / "fact_inventory" / (
    "master_candidate_skills_fact_ledger_20260518T1100Z.json"
)
TAXONOMY_REL = Path("apps_rg") / "config" / "domain_contract" / "master_role_family_taxonomy.yaml"

REQUIRED_LEDGER_FACT_FIELDS: tuple[str, ...] = (
    "candidate_fact_id",
    "claim_text",
    "confidence",
    "source_resume_variants",
    "role_families_supported",
)


class ConfidenceBand(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class FactUsageBand(str, Enum):
    """How a fact row may contribute to externally-shipped resumes after gates."""

    # HIGH: deterministic X2 unchanged; wording still must trace to approved sources after validation.
    ALLOW_AFTER_NORMAL_VALIDATION = "allow_after_normal_validation"
    REQUIRE_HUMAN_REVIEW_FOR_CANONICAL_USE = "require_human_review_for_canonical_use"
    BLOCK_FINAL_EXTERNAL = "block_final_external"


JD_BRIEFING_CANNOT_CREATE_FACTS = (
    "JD/briefing may only reorder, filter, or prioritize candidate_fact_id selections from the "
    "ledger plus the canonical base resume fact store. Free-text JD/briefing must never be "
    "ingested as a new factual claim suitable for resume proof."
)


def jd_briefing_cannot_create_facts_note() -> str:
    """Explicit policy surface for callers and reviewers."""
    return JD_BRIEFING_CANNOT_CREATE_FACTS


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def default_ledger_path(repo_root: Path | None = None) -> Path:
    root = repo_root or _repo_root_from_here()
    return root / REPO_APPS_REL


def default_taxonomy_path(repo_root: Path | None = None) -> Path:
    root = repo_root or _repo_root_from_here()
    return root / TAXONOMY_REL


def load_master_candidate_fact_ledger(
    *,
    repo_root: Path | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    ledger_path = path or default_ledger_path(repo_root)
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    if "candidate_facts" not in payload:
        raise ValueError("ledger missing candidate_facts")
    facts = payload["candidate_facts"]
    if not isinstance(facts, list):
        raise TypeError("candidate_facts must be list")
    for row in facts:
        validate_fact_shape(row)
    return payload


def load_master_role_family_taxonomy(
    *,
    repo_root: Path | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    import yaml

    tax_path = path or default_taxonomy_path(repo_root)
    loaded = yaml.safe_load(tax_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise TypeError("taxonomy must deserialize to mapping")
    return dict(loaded)


def taxonomy_role_family_ids(taxonomy: Mapping[str, Any]) -> frozenset[str]:
    rows = taxonomy.get("role_families") or []
    ids: list[str] = []
    if not isinstance(rows, list):
        raise TypeError("role_families must be list")
    for item in rows:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            ids.append(item["id"])
    return frozenset(ids)


def taxonomy_aliases(taxonomy: Mapping[str, Any]) -> dict[str, str]:
    aliases = taxonomy.get("role_family_id_aliases") or {}
    if not isinstance(aliases, dict):
        raise TypeError("role_family_id_aliases must be dict")
    cleaned: dict[str, str] = {}
    for k, v in aliases.items():
        if isinstance(k, str) and isinstance(v, str):
            cleaned[k] = v
    return cleaned


def normalize_role_family_id(
    role_family: str,
    *,
    taxonomy: Mapping[str, Any],
) -> str:
    aliases = taxonomy_aliases(taxonomy)
    return aliases.get(role_family, role_family)


def allowed_role_family_ids_expanded(taxonomy: Mapping[str, Any]) -> frozenset[str]:
    base = taxonomy_role_family_ids(taxonomy)
    return base | frozenset(taxonomy_aliases(taxonomy).keys())


def validate_fact_shape(row: Mapping[str, Any]) -> None:
    for key in REQUIRED_LEDGER_FACT_FIELDS:
        if key not in row:
            raise ValueError(f"ledger fact missing {key}: {row.get('candidate_fact_id')!r}")
    if not isinstance(row["candidate_fact_id"], str):
        raise TypeError("candidate_fact_id must be str")
    if not isinstance(row["claim_text"], str):
        raise TypeError("claim_text must be str")
    confidence = row["confidence"]
    if confidence not in {e.value for e in ConfidenceBand}:
        raise ValueError(f"invalid confidence on {row['candidate_fact_id']}: {confidence!r}")
    src = row["source_resume_variants"]
    if not isinstance(src, list) or not all(isinstance(s, str) for s in src):
        raise TypeError("source_resume_variants must be list[str]")
    rf = row["role_families_supported"]
    if not isinstance(rf, list) or not all(isinstance(s, str) for s in rf):
        raise TypeError("role_families_supported must be list[str]")
    capability_tags = row.get("capability_tags")
    if capability_tags is not None and (
        not isinstance(capability_tags, list) or not all(isinstance(s, str) for s in capability_tags)
    ):
        raise TypeError("capability_tags must be list[str] when present")
    proof_text = row.get("proof_text")
    if proof_text is not None and not isinstance(proof_text, str):
        raise TypeError("proof_text must be str when present")


def fact_usage_band(confidence_raw: str) -> FactUsageBand:
    band = ConfidenceBand(confidence_raw)
    if band is ConfidenceBand.HIGH:
        return FactUsageBand.ALLOW_AFTER_NORMAL_VALIDATION
    if band is ConfidenceBand.MEDIUM:
        return FactUsageBand.REQUIRE_HUMAN_REVIEW_FOR_CANONICAL_USE
    return FactUsageBand.BLOCK_FINAL_EXTERNAL


def is_promotable_to_canonical_external(confidence_raw: str) -> bool:
    """MEDIUM / LOW / NEEDS_VERIFICATION are never silently canonical for external resumes."""
    return ConfidenceBand(confidence_raw) is ConfidenceBand.HIGH


def ledger_fact_ids(ledger: Mapping[str, Any]) -> frozenset[str]:
    facts = ledger.get("candidate_facts") or []
    out: list[str] = []
    if not isinstance(facts, list):
        raise TypeError("candidate_facts malformed")
    for row in facts:
        if isinstance(row, dict):
            fid = row.get("candidate_fact_id")
            if isinstance(fid, str):
                out.append(fid)
    return frozenset(out)


def assert_selection_bounded_to_ledger(candidate_ids: Iterable[str], ledger: Mapping[str, Any]) -> None:
    """Runtime guardrail: rejecting selections that JD text could invent."""
    universe = ledger_fact_ids(ledger)
    for cid in candidate_ids:
        if cid not in universe:
            raise ValueError(f"selection {cid!r} not backed by ledger fact ids")


def validate_role_family_references_for_fact(
    role_families_supported: Sequence[str],
    taxonomy: Mapping[str, Any],
) -> None:
    allowed = taxonomy_role_family_ids(taxonomy)
    aliases = taxonomy_aliases(taxonomy)
    expanded_ok = allowed | frozenset(aliases.keys())
    for rf in role_families_supported:
        normalized = aliases.get(rf, rf)
        if rf not in expanded_ok:
            raise ValueError(f"unknown role family id {rf!r}")
        if normalized not in allowed:
            raise ValueError(f"normalized role family {normalized!r} off taxonomy")


def candidate_fact_tag_universe(ledger: Mapping[str, Any]) -> frozenset[str]:
    facts = ledger.get("candidate_facts") or []
    tags: set[str] = set()
    if not isinstance(facts, list):
        return frozenset()
    for row in facts:
        if not isinstance(row, dict):
            continue
        ct = row.get("capability_tags") or []
        if isinstance(ct, list):
            for t in ct:
                if isinstance(t, str):
                    tags.add(t)
    return frozenset(tags)
