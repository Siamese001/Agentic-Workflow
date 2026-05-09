"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT contain runtime hop runners (def generate_*).

Original: apps_rg/integrations/hops/ibm_ensemble.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Contains generate_* methods (runtime hop runners)

Importing this module raises RuntimeError immediately.
Core L2/L3 owns all runtime execution. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations.hops.ibm_ensemble is QUARANTINED. "
    "apps_rg may NOT contain runtime hop runners. "
    "Core L2/L3 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to:
# archives/apps_rg/quarantine_w4_20260509/integrations/hops/ibm_ensemble.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
"""HOP-4E-IBM — ORIGINAL (QUARANTINED)"""
# from __future__ import annotations
# from pathlib import Path
# from typing import Iterable, List, Optional, Sequence
# from apps_rg.integrations.hops._role_bullet_runner import BulletResult, run_role_bullets

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
