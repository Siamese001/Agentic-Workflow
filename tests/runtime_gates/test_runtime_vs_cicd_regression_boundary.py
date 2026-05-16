"""00C.8 Runtime vs CI/CD regression boundary tests.

Proof command:
    python -m pytest tests/runtime_gates/test_runtime_vs_cicd_regression_boundary.py -q

Doctrine rule (00C.8):
- Runtime anomaly gate (G25) MAY downgrade, pause, reroute, shrink scope,
  escalate, safe fallback, or abstain.
- Runtime anomaly gate MUST NOT publish new prompts, policies, registry
  entries, rubrics, retrieval profiles, or memory.
- CI/CD promotion may qualify next versions but is not a current-run
  disposition.
- L6 promotion may prepare future-run update only after completed-run
  eval/RCA/gauntlet/UWG.
- No runtime gate may silently alter current-run model/tool/provider choice
  outside the RouteContract and owner-layer fallback rules.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.contracts import Disposition

# Allowed live-run dispositions for G25 per 00C.6.
G25_ALLOWED = {
    Disposition.ALLOW,            # CONTINUE
    Disposition.MARK_DEGRADED,
    Disposition.SHRINK_SCOPE,
    Disposition.REROUTE,
    Disposition.ESCALATE_HITL,
    Disposition.ABSTAIN,
    Disposition.SAFE_FALLBACK,    # RETURN_BEST_PARTIAL
}

# Promotion-side vocabulary that MUST never appear in a runtime gate disposition.
PROMOTION_VOCAB = frozenset(
    {
        "PROMOTE",
        "ROLLOUT",
        "CANARY",
        "SHADOW_PROMOTE",
        "RUBRIC_UPDATE",
        "POLICY_PUBLISH",
        "MODEL_RELEASE",
        "ROLLBACK_VERSION",
    }
)


def test_runtime_dispositions_disjoint_from_promotion_vocab():
    """No Disposition value collides with promotion-side vocabulary."""
    runtime = {d.value for d in Disposition}
    overlap = runtime & PROMOTION_VOCAB
    assert not overlap, f"runtime/promotion vocab collision: {overlap}"


def test_g25_disposition_is_runtime_only(base_ctx):
    """G25 anomaly gate emits only the doctrine-allowed runtime dispositions."""
    from agentic_core.L5_safety.runtime_gates.g25_runtime_anomaly import (
        RuntimeAnomalyGate,
    )

    # Exercise across a range of observed deviations.
    cases = [
        {"tokens": 100, "latency_ms": 100},        # well within baseline
        {"tokens": 9000, "latency_ms": 9000},      # 4-5x baseline
        {"tokens": 50000, "latency_ms": 60000},    # severe
    ]
    for observed in cases:
        ctx = base_ctx
        ctx.observed = observed
        decision = RuntimeAnomalyGate().evaluate(ctx)
        assert decision.disposition in G25_ALLOWED, (
            f"G25 emitted non-runtime disposition: {decision.disposition}"
        )


def test_g29_learning_firewall_blocks_live_mutation(base_ctx):
    """G29 must not allow current-run mutation from L6 learning loop."""
    from agentic_core.L5_safety.runtime_gates.g29_learning_firewall import (
        LearningFirewallGate,
    )

    ctx = base_ctx
    ctx.learning_signal = {
        "runtime_only": True,    # signal claims it wants to mutate current run
        "future_run": False,
    }
    decision = LearningFirewallGate().evaluate(ctx)
    # Doctrine-allowed: BLOCK_LIVE_MUTATION / REJECT_PROMOTION / HOLD_FOR_REVIEW
    # / ARCHIVE map to canonical bounded dispositions. The crucial invariant
    # is "no current-run mutation is admitted" — DENY/BLOCK_COMMIT/QUARANTINE
    # for hard rejection, ESCALATE_HITL/MARK_DEGRADED/ABSTAIN for hold paths.
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.BLOCK_COMMIT,
        Disposition.QUARANTINE,
        Disposition.ESCALATE_HITL,
        Disposition.ABSTAIN,
        Disposition.MARK_DEGRADED,
    )
    # And the gate MUST not allow live mutation.
    assert decision.disposition is not Disposition.ALLOW
    assert decision.disposition is not Disposition.COMMIT_REQUEST


def test_runtime_gate_does_not_publish_promotion(base_ctx):
    """No runtime gate may emit a promotion-style disposition or alias."""
    from agentic_core.L5_safety.runtime_gates import all_gates, evaluate

    for gate_id in all_gates():
        decision = evaluate(gate_id, base_ctx)
        assert decision.disposition.value not in PROMOTION_VOCAB
        # alias must also not contain promotion verbs
        if decision.alias:
            assert decision.alias not in PROMOTION_VOCAB
