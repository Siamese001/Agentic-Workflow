"""HardenedanthropicexecutorStrategy - QUARANTINED PLACEHOLDER

This module has been moved to apps_rg/_quarantine/ as part of W4 governance enforcement.

Reason: Runtime authority violation (direct anthropic import - provider authority).
All provider interaction now lives in agentic_core L2/L5.

See: .windsurf/plans/author-gate-enforcement-deferred-scope-complete-d7f5e3.md
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.enforcement.HardenedanthropicexecutorStrategy is QUARANTINED. "
    "apps_rg may NOT make direct provider calls. "
    "Core L2/L5 owns provider interaction."
)
