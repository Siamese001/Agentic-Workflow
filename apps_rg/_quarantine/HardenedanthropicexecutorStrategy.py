"""QUARANTINE NOTICE -- AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT make direct provider calls or contain execution strategies.

Original: apps_rg/enforcement/HardenedanthropicexecutorStrategy.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE -- Contains direct anthropic import (provider authority)

Importing this module raises RuntimeError.
Core L2 Execution owns all provider calls through SovereignLLMGateway.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.enforcement.HardenedanthropicexecutorStrategy is QUARANTINED. "
    "apps_rg may NOT make direct provider calls. "
    "Core L2 Execution owns all provider calls. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
