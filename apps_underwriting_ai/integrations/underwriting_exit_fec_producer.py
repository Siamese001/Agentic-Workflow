"""Exit FEC producer integration for apps_underwriting_ai.

W5.2 — Full implementation.

Wires the FinalEvidenceContract into the Exit v6 pipeline. Enforces fail-closed
discipline: missing FEC, policy_hash, or blueprint_hash triggers Exit terminal
rather than a degraded pass.

Responsibility boundaries (enforced by this module):
  - Emits EXACTLY ONE X3 disposition per run.
  - Fails closed on every precondition violation (never degrades silently).
  - L6 observability is AFTER-RUNTIME ONLY — this module must not be called
    before the full L2 pipeline has completed.
  - UWG_ONLY write path — no direct L4 writes.
  - Does NOT call LLM providers, open-web retrieval, or routing logic.

X3 Disposition classes:
  X3A_APPROVE      — verdict APPROVE, all gates passed, FEC PASS/WEAK_WITH_CAVEATS
  X3B_REFER        — verdict REFER, or HITL_REQUIRED posture
  X3C_DECLINE      — verdict DECLINE, all gates passed
  X3D_INSUFFICIENT — verdict INSUFFICIENT_EVIDENCE, or FEC FAIL without missing-doc gate
  X3E_SAFE_ABSTAIN — any precondition violation (fail-closed terminal)

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W5.2.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

_LOGGER = logging.getLogger(__name__)

EXIT_MODE = "FAIL_CLOSED"
DURABLE_WRITE_PATH = "UWG_ONLY"

# X3 disposition classes.
X3A_APPROVE = "X3A_APPROVE"
X3B_REFER = "X3B_REFER"
X3C_DECLINE = "X3C_DECLINE"
X3D_INSUFFICIENT = "X3D_INSUFFICIENT"
X3E_SAFE_ABSTAIN = "X3E_SAFE_ABSTAIN"

_VALID_X3 = frozenset({X3A_APPROVE, X3B_REFER, X3C_DECLINE, X3D_INSUFFICIENT, X3E_SAFE_ABSTAIN})

# Verdict strings emitted by L2 DecisionAssemblyAdapter / DeterministicRiskScorer.
_VERDICT_APPROVE = "APPROVE"
_VERDICT_REFER = "REFER"
_VERDICT_DECLINE = "DECLINE"
_VERDICT_INSUFFICIENT = "INSUFFICIENT_EVIDENCE"

_REQUIRED_FEC_FIELDS = (
    "c0_mode",
    "c0_state",
    "evidence_ids",
    "support_score",
    "evidence_sufficiency",
)

_REQUIRED_CONTEXT_KEYS = (
    "demo_policy_hash",
    "blueprint_hash",
    "route_contract",
)

# HITL postures that escalate to X3B_REFER.
_HITL_ESCALATE_POSTURES = frozenset({"HITL_REQUIRED", "HITL_ADVISORY"})

# FEC c0_states that are not fail-closed by themselves.
_C0_PASS_STATES = frozenset({"PASS", "WEAK_WITH_CAVEATS"})


def validate_exit_preconditions(
    final_evidence_contract: dict[str, Any] | None,
    run_context: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Validate that all Exit fail-closed preconditions are satisfied.

    Returns:
        (ok, violations) — ok=True means Exit may proceed; violations lists
        every missing or invalid precondition.
    """
    violations: list[str] = []
    if not final_evidence_contract:
        violations.append("final_evidence_contract is missing or empty")
        return False, violations
    for fec_field in _REQUIRED_FEC_FIELDS:
        if fec_field not in final_evidence_contract:
            violations.append(f"FEC missing required field: {fec_field}")
    for key in _REQUIRED_CONTEXT_KEYS:
        if not run_context.get(key):
            violations.append(f"run_context missing required key: {key}")
    return len(violations) == 0, violations


def _select_x3_disposition(
    verdict: str,
    hitl_posture: str,
    c0_state: str,
    contradiction_flags: list[str],
    reason_codes: list[str],
) -> str:
    """Select the single X3 disposition for this run.

    Priority order (first match wins):
      1. INSUFFICIENT_EVIDENCE verdict → X3D
      2. FEC c0_state=FAIL or empty reason_codes → X3E (fail-closed)
      3. HITL_REQUIRED or HITL_ADVISORY posture → X3B
      4. DECLINE verdict → X3C
      5. REFER verdict → X3B
      6. APPROVE verdict → X3A
      7. Unknown verdict → X3E (fail-closed unknown)
    """
    verdict_upper = verdict.upper()

    if verdict_upper == _VERDICT_INSUFFICIENT:
        return X3D_INSUFFICIENT

    if c0_state not in _C0_PASS_STATES:
        return X3E_SAFE_ABSTAIN

    if not reason_codes:
        return X3E_SAFE_ABSTAIN

    if hitl_posture in _HITL_ESCALATE_POSTURES:
        return X3B_REFER

    if verdict_upper == _VERDICT_DECLINE:
        return X3C_DECLINE

    if verdict_upper == _VERDICT_REFER:
        return X3B_REFER

    if verdict_upper == _VERDICT_APPROVE:
        return X3A_APPROVE

    # Unknown verdict → fail-closed.
    return X3E_SAFE_ABSTAIN


class UnderwritingExitFecProducer:
    """Integrates the FEC into Exit v6 with fail-closed enforcement.

    W5.2 — Full implementation.

    Invariants:
      - Emits exactly one X3 per run (enforced via _x3_emitted flag).
      - Never called before L2 pipeline completes (L6 post-run only).
      - Never writes to L4 directly (UWG_ONLY write path).
      - Fails closed on every precondition — never degrades silently.
    """

    def __init__(self) -> None:
        self._x3_emitted: bool = False
        self._x3_disposition: str = ""

    def produce_exit_bundle(
        self,
        final_evidence_contract: dict[str, Any] | None,
        run_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Produce the Exit bundle with exactly one X3 disposition.

        Fail-closed on any precondition violation. Emits X3E_SAFE_ABSTAIN
        on every violation path.

        Args:
            final_evidence_contract: FEC from the C0 evidence pass.
            run_context: Runtime context with policy hash, blueprint hash,
                route_contract, verdict, reason_codes, hitl_posture, etc.

        Returns:
            Exit bundle dict with a single x3_disposition.

        Raises:
            RuntimeError: If called more than once per instance (exactly-one-X3
                invariant — caller must instantiate a fresh producer per run).
        """
        if self._x3_emitted:
            raise RuntimeError(
                "UnderwritingExitFecProducer.produce_exit_bundle() called more than once. "
                "Exactly one X3 disposition per run is enforced — instantiate a fresh producer."
            )

        exit_id = f"exit-{uuid.uuid4().hex[:16]}"

        # ------------------------------------------------------------------ #
        # Precondition validation — fail-closed on any violation.
        # ------------------------------------------------------------------ #
        ok, violations = validate_exit_preconditions(final_evidence_contract, run_context)
        if not ok:
            self._x3_emitted = True
            self._x3_disposition = X3E_SAFE_ABSTAIN
            _LOGGER.info(
                "[apps_underwriting_ai] Exit fail-closed: %d violations: %s",
                len(violations),
                violations,
            )
            return {
                "exit_id": exit_id,
                "exit_mode": EXIT_MODE,
                "x3_disposition": X3E_SAFE_ABSTAIN,
                "x3_emitted": True,
                "violations": violations,
                "durable_write_path": DURABLE_WRITE_PATH,
                "l4_write_attempted": False,
                "l6_post_run_only": True,
                "demo_mode": True,
            }

        # ------------------------------------------------------------------ #
        # Extract decision fields from run_context.
        # ------------------------------------------------------------------ #
        verdict = str(run_context.get("verdict", "")).upper() or _VERDICT_INSUFFICIENT
        reason_codes: list[str] = list(run_context.get("reason_code_bundle") or [])
        hitl_posture = str(run_context.get("hitl_posture", "HITL_NONE"))
        demo_policy_hash = str(run_context.get("demo_policy_hash", ""))
        blueprint_hash = str(run_context.get("blueprint_hash", ""))
        demo_packet_id = str(run_context.get("demo_packet_id", exit_id))

        fec = final_evidence_contract  # type: ignore[assignment]
        c0_state = str(fec.get("c0_state", "UNKNOWN"))  # type: ignore[union-attr]
        contradiction_flags: list[str] = list(fec.get("contradiction_flags") or [])  # type: ignore[union-attr]
        evidence_ids: list[str] = list(fec.get("evidence_ids") or [])  # type: ignore[union-attr]
        support_score = float(fec.get("support_score", 0.0))  # type: ignore[union-attr]

        # ------------------------------------------------------------------ #
        # Additional fail-closed checks beyond precondition validation.
        # ------------------------------------------------------------------ #
        additional_violations: list[str] = []

        # Verdict must have at least one reason code.
        if not reason_codes and verdict != _VERDICT_INSUFFICIENT:
            additional_violations.append("verdict lacks reason_codes")

        # Unresolved contradiction flags with APPROVE verdict → escalate.
        if contradiction_flags and verdict == _VERDICT_APPROVE:
            additional_violations.append(
                f"contradiction_flags unresolved with APPROVE verdict: {contradiction_flags}"
            )

        # UNKNOWN c0_state is not passable.
        if c0_state == "UNKNOWN":
            additional_violations.append("c0_state is UNKNOWN — FEC not fully resolved")

        if additional_violations:
            self._x3_emitted = True
            self._x3_disposition = X3E_SAFE_ABSTAIN
            _LOGGER.info(
                "[apps_underwriting_ai] Exit additional fail-closed: %s",
                additional_violations,
            )
            return {
                "exit_id": exit_id,
                "exit_mode": EXIT_MODE,
                "x3_disposition": X3E_SAFE_ABSTAIN,
                "x3_emitted": True,
                "violations": additional_violations,
                "durable_write_path": DURABLE_WRITE_PATH,
                "l4_write_attempted": False,
                "l6_post_run_only": True,
                "demo_mode": True,
            }

        # ------------------------------------------------------------------ #
        # X3 disposition selection — exactly one emitted.
        # ------------------------------------------------------------------ #
        x3 = _select_x3_disposition(
            verdict=verdict,
            hitl_posture=hitl_posture,
            c0_state=c0_state,
            contradiction_flags=contradiction_flags,
            reason_codes=reason_codes,
        )

        self._x3_emitted = True
        self._x3_disposition = x3

        # ------------------------------------------------------------------ #
        # Build and return the exit bundle.
        # ------------------------------------------------------------------ #
        return {
            "exit_id": exit_id,
            "exit_mode": EXIT_MODE,
            "x3_disposition": x3,
            "x3_emitted": True,
            "verdict": verdict,
            "reason_code_bundle": reason_codes,
            "hitl_posture": hitl_posture,
            "c0_state": c0_state,
            "contradiction_flags_count": len(contradiction_flags),
            "evidence_ids_count": len(evidence_ids),
            "support_score": support_score,
            "demo_policy_hash": demo_policy_hash,
            "blueprint_hash": blueprint_hash,
            "demo_packet_id": demo_packet_id,
            "final_evidence_contract": fec,
            "durable_write_path": DURABLE_WRITE_PATH,
            "l4_write_attempted": False,
            "l6_post_run_only": True,
            "demo_mode": True,
            "violations": [],
        }

    @property
    def x3_emitted(self) -> bool:
        """True after produce_exit_bundle() has run."""
        return self._x3_emitted

    @property
    def x3_disposition(self) -> str:
        """The X3 disposition emitted, or '' before produce_exit_bundle() runs."""
        return self._x3_disposition
