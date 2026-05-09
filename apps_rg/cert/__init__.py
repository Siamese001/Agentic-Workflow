"""
QUARANTINE NOTICE — AG-RGGOV-5: CORE_OWNED_FEC_ONLY

This package is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit FinalEvidenceContract. Core C0 owns FEC emission.

apps_rg may supply evidence_profile_ref only (declarative reference to
rg_evidence_profile.yaml). Runtime FEC emission is prohibited.

See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19
"""

import sys

# AG-RGGOV-5: Prevent any import of this quarantined package
raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-5): "
    "apps_rg.cert is QUARANTINED. "
    "apps_rg may NOT emit FinalEvidenceContract. "
    "Core C0 owns FEC emission. "
    "Use apps_rg/profiles/rg_evidence_profile.yaml for declarative evidence rules. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
