"""
QUARANTINE NOTICE — AG-RGGOV-5: CORE_OWNED_FEC_ONLY

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit FinalEvidenceContract. Core C0 owns FEC emission.

Original: apps_rg/cert/fec_producer.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-5 — apps_rg must not remain a live FEC producer

Importing this module raises RuntimeError to prevent accidental usage.
For evidence_profile_ref, use apps_rg/profiles/rg_evidence_profile.yaml (declarative).
"""

import sys

if sys.modules.get(__name__) is None:
    # Module being imported — raise immediately
    raise RuntimeError(
        "QUARANTINE VIOLATION (AG-RGGOV-5): "
        "apps_rg.cert.fec_producer is QUARANTINED. "
        "apps_rg may NOT emit FinalEvidenceContract. "
        "Core C0 owns FEC emission. "
        "Use apps_rg/profiles/rg_evidence_profile.yaml for declarative evidence rules. "
        "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
    )
