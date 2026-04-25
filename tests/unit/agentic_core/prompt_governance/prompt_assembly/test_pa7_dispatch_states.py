"""Unit tests for PA.7 dispatch states."""

from __future__ import annotations

import pytest

from agentic_core.prompt_governance.prompt_assembly.pa7_dispatch_states import (
    DispatchBlockReason,
    DispatchDisposition,
    DispatchOutcome,
    build_dispatch_outcome,
)


def test_eight_dispatch_states_present():
    expected = {
        "PASS",
        "BLOCKED_POLICY",
        "BLOCKED_CONTEXT",
        "BLOCKED_SCHEMA",
        "BLOCKED_BUDGET",
        "BLOCKED_REPLAY",
        "BLOCKED_TOOL",
        "BLOCKED_HITL",
    }
    assert {d.value for d in DispatchDisposition} == expected


def test_pass_outcome():
    o = build_dispatch_outcome(disposition=DispatchDisposition.PASS, detail="ok")
    assert o.dispatch_allowed is True
    assert o.block_reason is None


def test_pass_with_block_reason_rejected():
    with pytest.raises(ValueError):
        DispatchOutcome(
            disposition=DispatchDisposition.PASS, block_reason=DispatchBlockReason.POLICY_HASH_MISMATCH
        )


def test_block_requires_reason():
    with pytest.raises(ValueError):
        DispatchOutcome(disposition=DispatchDisposition.BLOCKED_POLICY, block_reason=None)


def test_block_reason_must_match_disposition():
    with pytest.raises(ValueError):
        DispatchOutcome(
            disposition=DispatchDisposition.BLOCKED_POLICY,
            block_reason=DispatchBlockReason.HITL_REVIEW_REQUIRED,
        )


@pytest.mark.parametrize(
    "reason,expected_disposition",
    [
        (DispatchBlockReason.POLICY_HASH_MISMATCH, DispatchDisposition.BLOCKED_POLICY),
        (DispatchBlockReason.POLICY_FENCE_VIOLATION, DispatchDisposition.BLOCKED_POLICY),
        (DispatchBlockReason.EVIDENCE_REQUIRED_MISSING, DispatchDisposition.BLOCKED_CONTEXT),
        (DispatchBlockReason.EVIDENCE_BLOCKED, DispatchDisposition.BLOCKED_CONTEXT),
        (DispatchBlockReason.EVIDENCE_CONFLICTED_NOT_PRESERVED, DispatchDisposition.BLOCKED_CONTEXT),
        (DispatchBlockReason.SCHEMA_INVALID, DispatchDisposition.BLOCKED_SCHEMA),
        (DispatchBlockReason.SCHEMA_PROVIDER_UNSUPPORTED, DispatchDisposition.BLOCKED_SCHEMA),
        (DispatchBlockReason.BUDGET_OVERFLOW, DispatchDisposition.BLOCKED_BUDGET),
        (DispatchBlockReason.BUDGET_REFINE_REQUIRED, DispatchDisposition.BLOCKED_BUDGET),
        (DispatchBlockReason.REPLAY_HASH_MISMATCH, DispatchDisposition.BLOCKED_REPLAY),
        (DispatchBlockReason.REPLAY_METADATA_MISSING, DispatchDisposition.BLOCKED_REPLAY),
        (DispatchBlockReason.TOOL_REGISTRY_MISMATCH, DispatchDisposition.BLOCKED_TOOL),
        (DispatchBlockReason.TOOL_CAPABILITY_MISMATCH, DispatchDisposition.BLOCKED_TOOL),
        (DispatchBlockReason.HITL_REVIEW_REQUIRED, DispatchDisposition.BLOCKED_HITL),
    ],
)
def test_reason_to_disposition_mapping(reason, expected_disposition):
    assert DispatchBlockReason.expected_disposition(reason) is expected_disposition


def test_build_dispatch_outcome_block_path():
    o = build_dispatch_outcome(
        disposition=DispatchDisposition.BLOCKED_BUDGET,
        block_reason=DispatchBlockReason.BUDGET_OVERFLOW,
        detail="over budget",
    )
    assert o.dispatch_allowed is False
    assert o.block_reason is DispatchBlockReason.BUDGET_OVERFLOW
    assert o.detail == "over budget"
