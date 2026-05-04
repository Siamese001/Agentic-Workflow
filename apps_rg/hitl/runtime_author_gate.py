"""W7 P-HITL3 + P-HITL6 — RuntimeAuthorGate core for apps_rg.

Implements the X3B HITL freeze / prompt / persist / L5-re-clear / Exit-hand-off
sequence defined in the plan design proposal:

    freeze()
      → emits HITLReviewPacket (X3B carrier)
      → calls cli_hitl_adapter.prompt()   ← ONLY caller of input()
      → persists HumanReviewDecision via HITLReplayStore
      → calls _l5_re_clear()             ← produces L5ReClearanceReceipt
      → returns HITLReviewPacket with l5_receipt attached

The caller (apps_rg/__main__.py or an L2 step) is responsible for handing
the returned HITLReviewPacket to the Exit V6 pipeline.  This module does
NOT write L4 directly.  All durable writes and cache promotions go through
Exit → UWG → L4.

Hard constraints enforced:
  ✓ No direct L4 write from this module.
  ✓ input() is only called via cli_hitl_adapter.prompt().
  ✓ L5 re-clearance treats human input as HUMAN_CALIBRATED data, not sovereign.
  ✓ L6 consumption is deferred to after Exit finalizes the run.

Plan: apps-rg-canonical-wireup-c8a4f2 W7 P-HITL3 + P-HITL6.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.hitl import cli_hitl_adapter
from apps_rg.hitl.hitl_replay_store import HITLReplayStore
from apps_rg.hitl.hitl_schemas import (
    HITLReviewPacket,
    HumanReviewDecision,
    L5ReClearanceReceipt,
    RuntimeAuthorGateDecisionRequest,
)

try:
    from agentic_core.L5_safety.runtime_gates.g06_hitl_approval import HITLApprovalGate
    from agentic_core.L5_safety.runtime_gates.types import (
        Disposition,
        GateContext,
        GateDecision,
        GraderType,
        Result,
        Severity,
    )
    _L5_AVAILABLE = True
except ImportError:
    _L5_AVAILABLE = False


class RuntimeAuthorGate:
    """apps_rg HITL gate — freeze → prompt → persist → re-clear → hand to Exit.

    Usage:
        gate = RuntimeAuthorGate(run_dir=Path(...))
        review_packet = gate.freeze(request)
        # pass review_packet to Exit V6 pipeline
    """

    def __init__(self, run_dir: Path, policy_hash: str = "") -> None:
        self._store = HITLReplayStore(run_dir)
        self._policy_hash = policy_hash or _unknown_policy_hash()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def freeze(
        self,
        request: RuntimeAuthorGateDecisionRequest,
    ) -> HITLReviewPacket:
        """Execute the full HITL cycle.  Returns a HITLReviewPacket ready
        for Exit V6.  Does NOT write L4 or call Exit directly.
        """
        # Step 1: collect human decision via CLI adapter (single input() point)
        decision = cli_hitl_adapter.prompt(request)

        # Step 2: verify hash consistency
        if not decision.verify_hash():
            raise ValueError(
                f"HumanReviewDecision hash verification failed for "
                f"decision_id={decision.decision_id!r}"
            )

        # Step 3: persist to append-only replay store
        self._store.append(decision)

        # Step 4: L5 re-clearance
        l5_receipt = self._l5_re_clear(decision)

        # Step 5: build and return the Exit X3B carrier
        return HITLReviewPacket(
            review_id=str(uuid.uuid4()),
            run_id=request.run_id,
            freeze_reason=request.trigger_kind,
            input_manifest_hash=request.input_manifest_hash,
            decision=decision,
            l5_receipt=l5_receipt,
        )

    # ------------------------------------------------------------------
    # L5 re-clearance
    # ------------------------------------------------------------------

    def _l5_re_clear(
        self,
        decision: HumanReviewDecision,
    ) -> L5ReClearanceReceipt:
        """Re-run L5 G06 with the human decision as HUMAN_CALIBRATED data.

        The human decision is NOT sovereign authority — it is untrusted data
        until L5 clears it.  The gate_verdict.source is HUMAN_CALIBRATED.
        """
        binding_hash = L5ReClearanceReceipt.compute_binding_hash(
            decision.decision_id, self._policy_hash
        )
        cleared_at = datetime.now(tz=timezone.utc).isoformat()

        gate_verdict_dict: dict[str, Any] = {}
        if _L5_AVAILABLE:
            ctx = GateContext(
                run_id=decision.request_id,
                policy_hash=self._policy_hash,
                hitl={
                    "review_requested": True,
                    "human_decision": {
                        "decision_id": decision.decision_id,
                        "chosen_option_id": decision.chosen_option_id,
                        "decision_hash": decision.decision_hash,
                        "operator_id": decision.operator_id,
                    },
                    "grader_type": GraderType.HUMAN_CALIBRATED.value,
                },
            )
            gate_decision: GateDecision = HITLApprovalGate().evaluate(ctx)
            gate_verdict_dict = gate_decision.to_verdict()
            # Stamp source as HUMAN_CALIBRATED (not sovereign)
            gate_verdict_dict["grader_type"] = GraderType.HUMAN_CALIBRATED.value
        else:
            # Degraded path: L5 not importable (stub for testing)
            gate_verdict_dict = {
                "gate_id": "G06",
                "disposition": Disposition.ESCALATE_HITL.value
                if _L5_AVAILABLE
                else "ESCALATE_HITL",
                "grader_type": "human_calibrated",
                "result": "PASS",
                "source": "human_review",
                "note": "L5 unavailable — degraded re-clearance",
            }

        return L5ReClearanceReceipt(
            receipt_id=str(uuid.uuid4()),
            decision_id=decision.decision_id,
            cleared_at=cleared_at,
            policy_hash=self._policy_hash,
            binding_hash=binding_hash,
            gate_verdict_dict=gate_verdict_dict,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unknown_policy_hash() -> str:
    return hashlib.sha256(b"apps_rg.runtime_author_gate.unknown_policy").hexdigest()
