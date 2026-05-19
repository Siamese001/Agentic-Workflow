"""X3 for competencies — reuses corrected executive_summary policy."""
from __future__ import annotations

from dataclasses import replace

from apps_rg.runtime.exit.executive_summary_x3 import X3Disposition, aggregate_x3

__all__ = [
    "X3Disposition",
    "aggregate_x3",
    "clarify_x3_for_competencies_live_provider_preflight",
]


def clarify_x3_for_competencies_live_provider_preflight(
    x3: X3Disposition,
    *,
    live_preflight_blocked: bool,
) -> X3Disposition:
    """Rewrite disposition copy when TCP preflight aborted generation.

    Raw ``aggregate_x3`` may classify empty-parse X2 failures ahead of the BLOCKED narrative; for
    unreachable vLLM the authoritative blocker is the live provider gate (see
    ``competencies_live_provider_gate.json``). X2 sidecars remain on disk for forensics.
    """
    if not live_preflight_blocked:
        return x3
    remediation = [r for r in x3.required_remediation if not r.startswith("Fix failed X2 gates")]
    probe = "Restore reachable Qwen/vLLM endpoint (see competencies_live_provider_gate.json and stderr)."
    if probe not in remediation:
        remediation.insert(0, probe)
    return replace(
        x3,
        decisive_reason="Runtime generation is BLOCKED (BLOCKED_LIVE_PROVIDER / PROVIDER_UNAVAILABLE).",
        review_reason="",
        x2_failed_gates=[],
        required_remediation=remediation,
    )
