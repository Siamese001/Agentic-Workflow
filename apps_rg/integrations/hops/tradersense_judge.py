"""HOP-4F-TRADERSENSE — Judge-only with pool-first fallback.

Medium-tier. Pool-first → fall-through to single-LLM regen + judge;
chronology compression hint in prompt. Failure degrades with run_report flag,
does NOT abort the pipeline.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P5.2).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from apps_rg.integrations.hops._role_bullet_runner import BulletResult, run_role_bullets

SECTION_ID = "hop_4f_tradersense"
TIER = "medium"
ROLE_ID = "tradersense"


def generate_tradersense_bullets(
    *,
    bullets: Sequence[dict],
    jd_facets: Iterable[str],
    company_facets: Iterable[str],
    mirror_terms: Iterable[str],
    archive_dir: Optional[Path] = None,
) -> List[BulletResult]:
    return run_role_bullets(
        role_id=ROLE_ID,
        bullets=bullets,
        jd_facets=jd_facets,
        company_facets=company_facets,
        mirror_terms=mirror_terms,
        archive_dir=archive_dir,
        tier="medium",
        n_candidates=1,
    )


__all__ = ["ROLE_ID", "SECTION_ID", "TIER", "generate_tradersense_bullets"]
