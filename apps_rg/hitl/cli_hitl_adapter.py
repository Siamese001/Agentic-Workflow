"""W7 P-HITL2 — CLI HITL adapter for apps_rg.

THIS IS THE SINGLE input() CHOKEPOINT for all of apps_rg.

No other module in apps_rg/ may call input().  All interactive human
decisions flow through this adapter.

The adapter:
  1. Renders the RuntimeAuthorGateDecisionRequest to stdout.
  2. Prompts for the chosen option_id via a single input() call.
  3. Returns a HumanReviewDecision with decision_hash computed inline.

Non-interactive mode (CI / tests): if sys.stdin is not a TTY, the adapter
raises NonInteractiveError rather than hanging.  Tests monkeypatch
`cli_hitl_adapter.input` to inject a deterministic response.

Plan: apps-rg-canonical-wireup-c8a4f2 W7 P-HITL2.
"""
from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone

from apps_rg.hitl.hitl_schemas import (
    BoundedOption,
    HumanReviewDecision,
    RuntimeAuthorGateDecisionRequest,
)


class NonInteractiveError(RuntimeError):
    """Raised when the adapter is invoked in a non-TTY context."""


# Patchable in tests: tests replace this with a lambda returning a preset string.
_input = input


def prompt(request: RuntimeAuthorGateDecisionRequest) -> HumanReviewDecision:
    """Render the decision request and collect a bounded human choice.

    Returns a HumanReviewDecision with a valid decision_hash.
    """
    if not sys.stdin.isatty():
        raise NonInteractiveError(
            "cli_hitl_adapter.prompt() requires an interactive TTY. "
            "In CI/tests, monkeypatch cli_hitl_adapter._input."
        )

    _render(request)

    valid_ids = {opt.option_id for opt in request.bounded_options}
    chosen_id: str = ""
    while chosen_id not in valid_ids:
        chosen_id = _input(
            f"\nEnter option ID [{'/'.join(sorted(valid_ids))}]: "
        ).strip()
        if chosen_id not in valid_ids:
            print(f"  Invalid choice. Please pick from: {sorted(valid_ids)}")

    decision_id = str(uuid.uuid4())
    timestamp = datetime.now(tz=timezone.utc).isoformat()
    decision_hash = HumanReviewDecision.compute_hash(
        decision_id, chosen_id, request.input_manifest_hash
    )
    return HumanReviewDecision(
        decision_id=decision_id,
        request_id=request.request_id,
        chosen_option_id=chosen_id,
        decision_timestamp=timestamp,
        input_manifest_hash=request.input_manifest_hash,
        decision_hash=decision_hash,
        replay_key=request.replay_key,
    )


# ---------------------------------------------------------------------------
# Rendering helpers (pure I/O, no state)
# ---------------------------------------------------------------------------

def _render(request: RuntimeAuthorGateDecisionRequest) -> None:
    print("\n" + "=" * 60)
    print(f"  HITL REVIEW REQUIRED  [{request.trigger_kind}]")
    print("=" * 60)
    print(f"  Run:        {request.run_id}")
    print(f"  Confidence: {request.confidence_score:.0%}")
    if request.recommendations:
        print("\n  Recommendations:")
        for rec in request.recommendations:
            print(f"    • {rec}")
    if request.evidence_refs:
        print("\n  Evidence:")
        for ref in request.evidence_refs:
            print(f"    - {ref}")
    print("\n  Options:")
    for opt in request.bounded_options:
        tag = " ★ recommended" if opt.is_recommended else ""
        print(f"    [{opt.option_id}] {opt.label}{tag}")
        print(f"         → {opt.consequence}")
    print()
