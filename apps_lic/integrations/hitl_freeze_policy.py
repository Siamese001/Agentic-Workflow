"""apps_lic HITL Freeze Policy — decision-only, no state writes.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-deferred-scope-followup-d3f9b2.md W1 D2-P1
ADR:  ADR-023 (Runtime HITL Exit Control)

Evaluates whether a completed (or partially-completed) apps_lic run should
be FROZEN for human review rather than immediately finalized.

Design invariants
-----------------
1. DECISION-ONLY — this module never writes durable state.
2. All outputs are immutable dataclasses.
3. Hard-fail exit-rubric dims always take precedence (fail before freeze).
4. If policy evaluation raises for any reason, the result is a freeze with
   reason="policy_eval_error" so the caller can escalate safely.
5. Re-clearance evaluation is a pure state-machine lookup; the caller owns
   persistence of the new X3 disposition.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml

_POLICY_PATH = Path(__file__).resolve().parent.parent / "config" / "hitl_policy.yaml"

# ---------------------------------------------------------------------------
# Public result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FreezeDecision:
    """Outcome of HITLFreezePolicy.evaluate().

    Attributes
    ----------
    should_freeze:
        True → caller must route draft to HITL review queue.
    freeze_status:
        One of: "frozen", "no_freeze", "bypassed", "policy_eval_error".
    triggered_by:
        Human-readable summary of the first matching freeze trigger.
    omission_escalation:
        True if the freeze was triggered by an omission_policy=hitl_required claim.
    dim_scores:
        Snapshot of the dim_id → score mapping that was evaluated (may be empty
        if not provided by caller).
    """

    should_freeze: bool
    freeze_status: str
    triggered_by: str = ""
    omission_escalation: bool = False
    dim_scores: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class HITLReClearanceDecision:
    """Outcome of HITLFreezePolicy.evaluate_reclearance().

    Attributes
    ----------
    new_x3_disposition:
        The X3 disposition to emit — one of ALLOW_FINISH, DENY, REROUTE.
    new_freeze_status:
        The terminal state: "cleared", "rejected", "returned_to_l1".
    is_terminal:
        Always True — re-clearance evaluation always produces a terminal state.
    reviewer_note:
        Optional note from the review context (pass-through; not interpreted).
    """

    new_x3_disposition: str
    new_freeze_status: str
    is_terminal: bool = True
    reviewer_note: str = ""


# ---------------------------------------------------------------------------
# Policy loader
# ---------------------------------------------------------------------------


def _load_policy(path: Path = _POLICY_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# ---------------------------------------------------------------------------
# HITLFreezePolicy
# ---------------------------------------------------------------------------


class HITLFreezePolicy:
    """Evaluate freeze triggers for an apps_lic run.

    Usage
    -----
    ::

        policy = HITLFreezePolicy()
        decision = policy.evaluate(
            dim_scores={"tone_fit_seniority": 0.3, "clear_cta": 0.9},
            run_context={
                "recipient_class": "EXECUTIVE",
                "outreach_mode": "cold",
                "confidence_score": 0.5,
                "omission_escalations": ["claim_foo"],  # hitl_required claims
                "asymmetric_insight_required": False,
                "technical_claim_depth_high": True,
            },
        )
        if decision.should_freeze:
            # route to HITL queue; record freeze_status on run record
            ...
    """

    def __init__(self, policy_path: Path = _POLICY_PATH) -> None:
        self._policy: dict[str, Any] = {}
        try:
            self._policy = _load_policy(policy_path)
        except (OSError, yaml.YAMLError):
            pass  # degraded mode: all evaluations return policy_eval_error freeze

    # ------------------------------------------------------------------
    # Primary evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        *,
        dim_scores: dict[str, float],
        run_context: dict[str, Any],
        hard_fails: list[str] | None = None,
    ) -> FreezeDecision:
        """Evaluate whether the run should be frozen.

        Parameters
        ----------
        dim_scores:
            Mapping of exit-rubric dim_id → score (0.0–1.0).
        run_context:
            Dict with at minimum: recipient_class, outreach_mode,
            confidence_score. May include omission_escalations (list of
            hitl_required claim ids), asymmetric_insight_required,
            technical_claim_depth_high.
        hard_fails:
            List of dim_ids that already hard-failed. If non-empty, the caller
            should use SAFE_ABSTAIN / DENY rather than freeze — this method
            returns no_freeze in that case to avoid masking the hard fail.
        """
        if os.environ.get("HITL_FREEZE_BYPASS", "").strip() == "1":
            return FreezeDecision(
                should_freeze=False,
                freeze_status="bypassed",
                triggered_by="HITL_FREEZE_BYPASS env var set",
                dim_scores=dict(dim_scores),
            )

        if hard_fails:
            return FreezeDecision(
                should_freeze=False,
                freeze_status="no_freeze",
                triggered_by=f"hard_fail takes precedence: {hard_fails[0]}",
                dim_scores=dict(dim_scores),
            )

        if not self._policy:
            return FreezeDecision(
                should_freeze=True,
                freeze_status="policy_eval_error",
                triggered_by="policy file could not be loaded",
                dim_scores=dict(dim_scores),
            )

        try:
            return self._evaluate_inner(dim_scores, run_context)
        except Exception:  # noqa: BLE001  # guardian: allow-broad-exception -- freeze eval must never crash the run; fail-safe to freeze
            return FreezeDecision(
                should_freeze=True,
                freeze_status="policy_eval_error",
                triggered_by="unexpected exception in freeze evaluation",
                dim_scores=dict(dim_scores),
            )

    def _evaluate_inner(
        self,
        dim_scores: dict[str, float],
        run_context: dict[str, Any],
    ) -> FreezeDecision:
        recipient_class = str(run_context.get("recipient_class", "")).upper()
        confidence = float(run_context.get("confidence_score", 1.0))
        omission_escalations: list[str] = run_context.get("omission_escalations") or []
        asymmetric_required = bool(run_context.get("asymmetric_insight_required", False))
        technical_high = bool(run_context.get("technical_claim_depth_high", False))

        _exec_classes = {"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"}

        # 1. Omission-policy escalations always freeze
        if omission_escalations:
            return FreezeDecision(
                should_freeze=True,
                freeze_status="frozen",
                triggered_by=f"omission_policy=hitl_required for claims: {omission_escalations[:3]}",
                omission_escalation=True,
                dim_scores=dict(dim_scores),
            )

        # 2. Confidence-based escalation
        conf_policy = self._policy.get("freeze_on_low_confidence") or {}
        conf_threshold = float(conf_policy.get("confidence_threshold", 0.55))
        conf_condition = conf_policy.get("condition", "")
        if confidence < conf_threshold and _matches_exec_condition(conf_condition, recipient_class, _exec_classes):
            return FreezeDecision(
                should_freeze=True,
                freeze_status="frozen",
                triggered_by=f"low confidence {confidence:.2f} < {conf_threshold} for {recipient_class}",
                dim_scores=dict(dim_scores),
            )

        # 3. Dim-score triggers
        for trigger in self._policy.get("freeze_on_dim_low_score") or []:
            dim_id = str(trigger.get("dim_id", ""))
            threshold = float(trigger.get("threshold", 0.5))
            condition = trigger.get("condition") or ""

            score = dim_scores.get(dim_id)
            if score is None:
                continue
            if score >= threshold:
                continue

            if not _matches_trigger_condition(
                condition=condition,
                recipient_class=recipient_class,
                exec_classes=_exec_classes,
                asymmetric_required=asymmetric_required,
                technical_high=technical_high,
            ):
                continue

            return FreezeDecision(
                should_freeze=True,
                freeze_status="frozen",
                triggered_by=f"{dim_id} score {score:.2f} < threshold {threshold}",
                dim_scores=dict(dim_scores),
            )

        return FreezeDecision(
            should_freeze=False,
            freeze_status="no_freeze",
            dim_scores=dict(dim_scores),
        )

    # ------------------------------------------------------------------
    # Re-clearance evaluation
    # ------------------------------------------------------------------

    def evaluate_reclearance(
        self,
        *,
        reviewer_action: str,
        reviewer_note: str = "",
    ) -> HITLReClearanceDecision:
        """Evaluate a reviewer's re-clearance action.

        Parameters
        ----------
        reviewer_action:
            One of: "approve", "reject", "return_to_l1".
        reviewer_note:
            Optional human note from the reviewer (pass-through).

        Returns
        -------
        HITLReClearanceDecision
            Always a terminal decision with new_x3_disposition set.
        """
        reclearance = (self._policy.get("reclearance") or {})
        disposition_map: dict[str, str] = reclearance.get("disposition_map") or {
            "cleared": "ALLOW_FINISH",
            "rejected": "DENY",
            "returned_to_l1": "REROUTE",
        }

        _action_to_state = {
            "approve": "cleared",
            "reject": "rejected",
            "return_to_l1": "returned_to_l1",
        }

        new_state = _action_to_state.get(str(reviewer_action).lower(), "rejected")
        new_x3 = disposition_map.get(new_state, "DENY")

        return HITLReClearanceDecision(
            new_x3_disposition=new_x3,
            new_freeze_status=new_state,
            is_terminal=True,
            reviewer_note=reviewer_note,
        )


# ---------------------------------------------------------------------------
# Condition helpers (pure functions)
# ---------------------------------------------------------------------------


def _matches_exec_condition(
    condition: str,
    recipient_class: str,
    exec_classes: set[str],
) -> bool:
    """Return True if the condition requires exec classes and recipient qualifies."""
    if not condition:
        return True
    if "EXECUTIVE" in condition or "C_LEVEL" in condition or "CTO" in condition:
        return recipient_class in exec_classes
    return True


def _matches_trigger_condition(
    *,
    condition: str,
    recipient_class: str,
    exec_classes: set[str],
    asymmetric_required: bool,
    technical_high: bool,
) -> bool:
    """Evaluate a freeze trigger's condition string.

    Conditions are simple declarative strings from the YAML config.
    We parse the most common patterns; unknown conditions default to True
    (conservative — prefer freeze over missed trigger).
    """
    if not condition:
        return True
    c = condition.lower()

    # exec-class condition
    if "recipient_class in [executive" in c or "c_level" in c or "cto" in c or "vp_eng" in c:
        if recipient_class not in exec_classes:
            return False

    # asymmetric_insight_required
    if "asymmetric_insight_required == true" in c:
        if not asymmetric_required:
            return False

    # technical_claim_depth_high
    if "technical_claim_depth_high" in c:
        if not technical_high:
            return False

    return True


__all__ = [
    "FreezeDecision",
    "HITLReClearanceDecision",
    "HITLFreezePolicy",
]
