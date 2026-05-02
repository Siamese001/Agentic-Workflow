"""HOP-4G-EY — Judge-only with pool-first fallback.

Medium-tier. Mirrors TraderSense pattern with role-specific framing
(regulatory advisory, model validation).

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P5.3).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from apps_rg.integrations.hops._role_bullet_runner import BulletResult, run_role_bullets

SECTION_ID = "hop_4g_ey"
TIER = "medium"
ROLE_ID = "ey"


def generate_ey_bullets(
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


__all__ = ["ROLE_ID", "SECTION_ID", "TIER", "generate_ey_bullets"]
