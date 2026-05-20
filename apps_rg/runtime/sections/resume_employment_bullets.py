"""Shared resume employment bullet extraction for section lanes (W11-M4A).

Canonical home for ``collect_employment_bullets`` — used by proof-pool and multi-lane
compile paths. ``apps_rg.runtime.sections.competencies_lane_runtime`` re-exports for
compatibility only.
"""

from __future__ import annotations

import hashlib
from typing import Any


def _sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def collect_employment_bullets(
    base_resume: dict[str, Any],
) -> tuple[list[dict[str, Any]], set[str], list[str]]:
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
                allowed.add(f"{bid}_metric_{_sha16(str(bullet['metric_raw']))[:8]}")
    rows.sort(key=lambda r: r["fact_id"])
    return rows, allowed, bullet_lowers
