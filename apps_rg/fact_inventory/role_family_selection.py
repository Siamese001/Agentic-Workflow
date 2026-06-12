"""Role-family inference helpers for graph-native evidence selection."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any


def digest_text(sample: str) -> str:
    return hashlib.sha256(sample.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RoleFamilyPriority:
    role_family: str
    score: int
    evidence_terms: tuple[str, ...]
    source_channels: tuple[str, ...]


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
        role_family_id = row["id"]
        kws_raw = row.get("jd_signal_keywords") or []
        if not isinstance(kws_raw, list):
            raise TypeError(f"jd_signal_keywords must be list for {role_family_id}")
        keywords = sorted(str(k).lower().strip() for k in kws_raw if str(k).strip())
        evidence_terms: list[str] = []
        channels: set[str] = set()
        score = 0
        for keyword in keywords:
            matched_any = False
            for channel, blob in corpuses:
                if keyword in blob:
                    matched_any = True
                    channels.add(channel)
            if matched_any:
                score += 1
                evidence_terms.append(keyword)

        deduped: list[str] = []
        seen: set[str] = set()
        for term in evidence_terms:
            if term not in seen:
                seen.add(term)
                deduped.append(term)
        aggregated[role_family_id] = {
            "score": score,
            "evidence_terms": tuple(deduped),
            "source_channels": tuple(sorted(channels)),
        }

    ordered = sorted(aggregated.keys(), key=lambda rid: (-aggregated[rid]["score"], rid))
    return tuple(
        RoleFamilyPriority(
            role_family=rid,
            score=aggregated[rid]["score"],
            evidence_terms=tuple(aggregated[rid]["evidence_terms"]),
            source_channels=tuple(aggregated[rid]["source_channels"]),
        )
        for rid in ordered
        if aggregated[rid]["score"] > 0
    )


__all__ = [
    "RoleFamilyPriority",
    "digest_text",
    "infer_role_family_priorities",
]
