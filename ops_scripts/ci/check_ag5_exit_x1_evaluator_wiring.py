#!/usr/bin/env python3
"""CI smoke: AG-5 X1 checkout wiring imports and executes on a neutral envelope."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    import sys

    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))

    from agentic_core.runtime.exit.exit_review_normalizer import normalize_ag5_terminal_input
    from agentic_core.runtime.exit.x1_checkout_runner import run_ag5_x1_checkout

    raw = {
        "source_type": "APP_BINDING_COMPATIBILITY_PACKAGE",
        "route_contract_ref": "route://ci-wiring",
        "route_id": "R_CI",
        "replay_key": "replay-ci-wiring",
        "terminal_class": "answer_only",
        "path_class": "neutral",
        "policy_hash": "ci-ph",
        "route_contract": {"policy_hash": "ci-ph"},
        "output": {"completion_score": 1.0},
        "otel_spans": {
            "spans": {
                k: {"present": True}
                for k in (
                    "trace_root",
                    "route_contract",
                    "tool_invocations",
                    "evidence_contracts",
                    "step_outputs",
                    "exit_disposition",
                )
            },
        },
        "exec_trace": {"replay_receipts_present": True},
        "app_id": "apps_rg",
        "task_class": "resume_generation",
    }
    pkt = normalize_ag5_terminal_input(raw)
    x1 = run_ag5_x1_checkout(pkt)
    if not x1.is_overall_pass():
        fb = x1.first_blocking_gate()
        blk = fb.gate_id if fb else "X1"
        print("[AG5-X1-WIRING] FAIL: X1 overall_pass=False first_blocker=", blk)
        return 1
    print("[AG5-X1-WIRING] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
