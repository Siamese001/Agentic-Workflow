"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from L2 execution utils for provider clients.

Original: apps_rg/utils/providers_anthropic_client_util.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — L2 execution util import (runtime authority)

Importing this module raises RuntimeError immediately.
Core L2 owns all provider clients.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/utils/providers_anthropic_client_util.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.utils.providers_anthropic_client_util is QUARANTINED. "
    "apps_rg may NOT import from L2 execution. "
    "Core L2 owns provider clients. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
