"""G24 — Determinism / Replay Gate.

Spec: certify the run is replayable enough for audit and trust.
Stop: durable commit MUST be blocked if replay certification is required and invalid.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.types import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)


@register_gate
class DeterminismReplayGate:
    GATE_ID = "G24"
    PRIMARY_LAYER = "Exit"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        artifacts = ctx.trace_artifacts
        replay_required = bool(artifacts.get("replay_required", False))
        replay_key = artifacts.get("replay_key", "")
        policy_hash = ctx.policy_hash
        blueprint_hash = ctx.blueprint_hash
        snapshot_id = artifacts.get("snapshot_id", "")
        wall_clock_used = bool(artifacts.get("wall_clock_used", False))
        raw_entropy_used = bool(artifacts.get("raw_entropy_used", False))
        mixed_state_read = bool(artifacts.get("mixed_state_read", False))
        silent_provider_fallback = bool(artifacts.get("silent_provider_fallback", False))
        digest_match = bool(artifacts.get("digest_match", True))
        # Critical breaks.
        if not replay_key:
            signals.append(RegressionSignal(name="missing_replay_key_count", value=1.0, severity="alert"))
            if replay_required:
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.BLOCK_COMMIT,
                    alias=DecisionAlias.NON_REPLAYABLE.value,
                    reason_codes=["missing_replay_key"],
                    signals=signals,
                    stop_condition_violated=True,
                )
        if not policy_hash:
            signals.append(RegressionSignal(name="policy_hash_mismatch", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                alias=DecisionAlias.NON_REPLAYABLE.value,
                reason_codes=["missing_policy_hash"],
                signals=signals,
                stop_condition_violated=True,
            )
        if not snapshot_id:
            signals.append(RegressionSignal(name="snapshot_mismatch", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                reason_codes=["missing_snapshot_id"],
                signals=signals,
            )
        if not digest_match:
            signals.append(RegressionSignal(name="replay_digest_mismatch", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                alias=DecisionAlias.RERUN_UNDER_FREEZE.value,
                reason_codes=["digest_mismatch"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Non-deterministic sources.
        nondet_reasons = []
        if wall_clock_used:
            nondet_reasons.append("wall_clock")
        if raw_entropy_used:
            nondet_reasons.append("raw_entropy")
        if mixed_state_read:
            nondet_reasons.append("mixed_state")
        if silent_provider_fallback:
            nondet_reasons.append("silent_provider_fallback")
        if nondet_reasons:
            signals.append(RegressionSignal(name="non_deterministic_route_count", value=1.0, severity="warn"))
            if replay_required:
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.BLOCK_COMMIT,
                    alias=DecisionAlias.NON_REPLAYABLE.value,
                    reason_codes=nondet_reasons,
                    signals=signals,
                    stop_condition_violated=True,
                )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                reason_codes=["non_deterministic_sources"],
                signals=signals,
                metadata={"reasons": nondet_reasons},
            )
        # All clean.
        if replay_required and not blueprint_hash:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                reason_codes=["missing_blueprint_hash"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.CERTIFY.value,
            reason_codes=["replay_certified"],
            signals=signals,
        )


__all__ = ["DeterminismReplayGate"]
