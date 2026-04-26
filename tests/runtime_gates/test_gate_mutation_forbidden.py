"""00C.8 anti-mutation tests.

Proof command:
    python -m pytest tests/runtime_gates/test_gate_mutation_forbidden.py -q

Doctrine rule (00C parent FORBIDDEN OUTPUTS):
A gate MUST NOT mutate any packet, L4 state, route contract, prompt
envelope, C0 contract, L2 artifact, Exit disposition, or L6 proposal.
We assert this by snapshotting the relevant ctx slices, running every gate,
and verifying no slice changed.
"""

from __future__ import annotations

import copy

from agentic_core.L5_safety.runtime_gates import all_gates, evaluate

# Slices that gates must NOT mutate.
GUARDED_FIELDS = (
    "route_contract",
    "retrieval_plan",
    "evidence",
    "prompt_packet",
    "tool_call",
    "memory_op",
    "workflow_state",
    "output",
    "trace_artifacts",
    "learning_signal",
    "intent",
    "caller_scope_baseline",
)


def test_no_gate_mutates_guarded_ctx_slice(base_ctx):
    """Run every gate against the same context and confirm zero mutation."""
    snapshot = {k: copy.deepcopy(getattr(base_ctx, k)) for k in GUARDED_FIELDS}
    for gate_id in all_gates():
        evaluate(gate_id, base_ctx)
    for k, before in snapshot.items():
        after = getattr(base_ctx, k)
        assert before == after, (
            f"gate run mutated guarded ctx slice: {k!r}\n"
            f"before={before!r}\nafter={after!r}"
        )


def test_envelope_identity_preserved(base_ctx):
    """request_id / run_id / trace_root / tenant_id MUST NOT change."""
    snap = (
        base_ctx.request_id,
        base_ctx.run_id,
        base_ctx.trace_root,
        base_ctx.tenant_id,
        base_ctx.policy_hash,
        base_ctx.blueprint_hash,
        base_ctx.replay_key,
    )
    for gate_id in all_gates():
        evaluate(gate_id, base_ctx)
    after = (
        base_ctx.request_id,
        base_ctx.run_id,
        base_ctx.trace_root,
        base_ctx.tenant_id,
        base_ctx.policy_hash,
        base_ctx.blueprint_hash,
        base_ctx.replay_key,
    )
    assert snap == after


def test_decision_carries_evidence_refs_when_present():
    """When the gate sets evidence_refs / replay_refs, they survive verdict serialization."""
    from agentic_core.L5_safety.runtime_gates.types import (
        Disposition,
        GateDecision,
    )

    decision = GateDecision(
        gate_id="G09",
        disposition=Disposition.ALLOW,
        evidence_refs=["doc1:1-3", "doc2:5-7"],
        replay_refs=["replay-1"],
        source_lineage_refs=["src-A"],
    )
    v = decision.to_verdict()
    assert v["evidence_refs"] == ["doc1:1-3", "doc2:5-7"]
    assert v["replay_refs"] == ["replay-1"]
    assert v["source_lineage_refs"] == ["src-A"]
