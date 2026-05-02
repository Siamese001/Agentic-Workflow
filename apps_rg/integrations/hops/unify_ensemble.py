"""HOP-4D-UNIFY — Per-Bullet Ensemble+Judge for Unify role.

Critical-tier. Pool-first attempt before LLM regen; per-bullet length
parity ±15% of source; 6 bullets typical.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P4.4).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from apps_rg.integrations.hops._role_bullet_runner import BulletResult, run_role_bullets

SECTION_ID = "hop_4d_unify"
TIER = "critical"
ROLE_ID = "unify"


def generate_unify_bullets(
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
        tier="critical",
        n_candidates=3,
    )


__all__ = ["ROLE_ID", "SECTION_ID", "TIER", "generate_unify_bullets"]
