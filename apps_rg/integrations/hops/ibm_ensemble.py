"""HOP-4E-IBM — Per-Bullet Ensemble+Judge for IBM role.

Critical-tier. Mirrors Unify pattern with role-specific JD-emphasis
(scale, financial services, regulatory).

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P4.5).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from apps_rg.integrations.hops._role_bullet_runner import BulletResult, run_role_bullets

SECTION_ID = "hop_4e_ibm"
TIER = "critical"
ROLE_ID = "ibm"


def generate_ibm_bullets(
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


__all__ = ["ROLE_ID", "SECTION_ID", "TIER", "generate_ibm_bullets"]
