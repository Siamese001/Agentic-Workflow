"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit CommitRequest or call DurableWriteGateway (L4 authority).

Original: apps_rg/cache/chunk_commit.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Direct L4 durable write via CommitRequest (runtime authority)

Importing this module raises RuntimeError immediately.
Core Exit/L4 owns all durable state commits.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/cache/chunk_commit.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.cache.chunk_commit is QUARANTINED. "
    "apps_rg may NOT emit CommitRequest or call DurableWriteGateway. "
    "Core Exit/L4 owns all durable state commits. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
