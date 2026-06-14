"""Unit tests for agentic_core.runtime.reasoning.reasoning_control_resolver.

Wave 6.1 (P2 untested-module coverage) — pure resolver surface.
``reasoning_control_resolver`` maps a requested-kw mapping → control
requirements → a deterministic execution receipt. Covers the digest, the
default gateway requirement builder, the per-surface classifiers, the
aggregate roll-up, and the BLOCK enforcement. No LLM / IO — every input is a
plain Mapping built in-test.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.reasoning.reasoning_control_requirement import (
    AllowedSurface,
    DowngradeDisposition,
    ReceiptState,
    RequirementLevel,
)
from agentic_core.runtime.reasoning.reasoning_control_resolver import (
    ReasoningGovernanceError,
    build_execution_plan,
    canonical_plan_digest,
    default_gateway_control_requirements,
    enforce_blocked,
    reasoning_quality_certification_allowed,
    resolve_gateway_receipt,
)
from agentic_core.runtime.reasoning.transport_capabilities import TransportCapabilities


def _reqs_by_name(requested_kw: dict[str, object]) -> dict[str, object]:
    return {r.control_name: r for r in default_gateway_control_requirements(requested_kw)}


class TestCanonicalPlanDigest:
    def test_deterministic(self) -> None:
        kw = {"temperature": 0.7, "max_tokens": 256}
        assert canonical_plan_digest(kw) == canonical_plan_digest(kw)

    def test_key_order_independent(self) -> None:
        a = canonical_plan_digest({"temperature": 0.7, "max_tokens": 256})
        b = canonical_plan_digest({"max_tokens": 256, "temperature": 0.7})
        assert a == b

    def test_value_change_changes_digest(self) -> None:
        a = canonical_plan_digest({"temperature": 0.7})
        b = canonical_plan_digest({"temperature": 0.8})
        assert a != b

    def test_is_sha256_hex(self) -> None:
        d = canonical_plan_digest({"a": 1})
        assert len(d) == 64 and all(c in "0123456789abcdef" for c in d)


class TestDefaultGatewayControlRequirements:
    def test_temperature_optional_warn(self) -> None:
        r = _reqs_by_name({"temperature": 0.5})["temperature"]
        assert r.requirement_level == RequirementLevel.OPTIONAL
        assert r.downgrade_disposition == DowngradeDisposition.WARN
        assert r.allowed_surfaces == frozenset({AllowedSurface.TRANSPORT})

    def test_max_tokens_required_review(self) -> None:
        r = _reqs_by_name({"max_tokens": 128})["max_tokens"]
        assert r.requirement_level == RequirementLevel.REQUIRED
        assert r.downgrade_disposition == DowngradeDisposition.REVIEW
        assert r.fallback_allowed is False

    def test_temperature_absent_no_requirement(self) -> None:
        names = {r.control_name for r in default_gateway_control_requirements({})}
        assert "temperature" not in names
        assert "max_tokens" not in names

    def test_orchestration_controls_always_present(self) -> None:
        names = {r.control_name for r in default_gateway_control_requirements({})}
        for n in ("cot_paths", "tot_branches", "tot_depth", "reflexion_loops",
                  "self_consistency_samples", "scratchpad_transport_guard"):
            assert n in names

    @pytest.mark.parametrize("name", ["cot_paths", "tot_branches", "tot_depth"])
    def test_orch_active_when_positive(self, name: str) -> None:
        active = _reqs_by_name({name: 3})[name]
        assert active.requested is True
        assert active.requirement_level == RequirementLevel.QUALITY_REQUIRED
        inactive = _reqs_by_name({name: 0})[name]
        assert inactive.requested is False
        assert inactive.requirement_level == RequirementLevel.OPTIONAL

    def test_reflexion_loops_policy_required_when_active(self) -> None:
        r = _reqs_by_name({"reflexion_loops": 2})["reflexion_loops"]
        assert r.requested is True
        assert r.requirement_level == RequirementLevel.POLICY_REQUIRED
        assert r.downgrade_disposition == DowngradeDisposition.BLOCK

    def test_self_consistency_needs_gt_one(self) -> None:
        # 1 sample is not "active" (>1 required).
        one = _reqs_by_name({"self_consistency_samples": 1})["self_consistency_samples"]
        assert one.requested is False
        many = _reqs_by_name({"self_consistency_samples": 3})["self_consistency_samples"]
        assert many.requested is True
        assert many.requirement_level == RequirementLevel.QUALITY_REQUIRED

    def test_bool_value_not_treated_as_number(self) -> None:
        # A bool for an orch control must NOT count as a positive number.
        r = _reqs_by_name({"cot_paths": True})["cot_paths"]
        assert r.requested is False

    def test_scratch_guard_active_on_forbidden_key(self) -> None:
        r = _reqs_by_name({"scratchpad": "x"})["scratchpad_transport_guard"]
        assert r.requested is True
        assert r.requirement_level == RequirementLevel.POLICY_REQUIRED
        assert r.allowed_surfaces == frozenset({AllowedSurface.POLICY})


class TestBuildExecutionPlan:
    def test_plan_carries_digest_and_values(self) -> None:
        kw = {"temperature": 0.3, "max_tokens": 64}
        plan = build_execution_plan(kw)
        assert plan.plan_digest == canonical_plan_digest(kw)
        assert plan.requested_values == kw
        assert len(plan.control_requirements) >= 2


class TestResolveGatewayReceipt:
    def test_max_tokens_applied_when_forwarded_and_observed(self) -> None:
        plan = build_execution_plan({"max_tokens": 100})
        caps = TransportCapabilities(frozenset({"max_tokens"}))
        receipt = resolve_gateway_receipt(plan, caps, {"max_tokens": 100})
        row = next(r for r in receipt.ledger if r.control_name == "max_tokens")
        assert row.receipt_state == ReceiptState.APPLIED
        assert receipt.aggregate_blocked is False

    def test_max_tokens_ignored_when_not_forwarded_triggers_review(self) -> None:
        plan = build_execution_plan({"max_tokens": 100})
        caps = TransportCapabilities(frozenset())  # provider strips it
        receipt = resolve_gateway_receipt(plan, caps, {})
        row = next(r for r in receipt.ledger if r.control_name == "max_tokens")
        assert row.receipt_state == ReceiptState.IGNORED
        # REQUIRED + violated + REVIEW disposition → aggregate_review
        assert receipt.aggregate_review is True

    def test_temperature_mismatch_degraded_warns(self) -> None:
        plan = build_execution_plan({"temperature": 0.7})
        caps = TransportCapabilities(frozenset({"temperature"}))
        receipt = resolve_gateway_receipt(plan, caps, {"temperature": 0.9})
        row = next(r for r in receipt.ledger if r.control_name == "temperature")
        assert row.receipt_state == ReceiptState.DEGRADED
        assert receipt.aggregate_warn is True
        assert receipt.aggregate_blocked is False

    def test_temperature_float_close_is_applied(self) -> None:
        plan = build_execution_plan({"temperature": 0.7})
        caps = TransportCapabilities(frozenset({"temperature"}))
        receipt = resolve_gateway_receipt(plan, caps, {"temperature": 0.7000001})
        row = next(r for r in receipt.ledger if r.control_name == "temperature")
        assert row.receipt_state == ReceiptState.APPLIED

    def test_reflexion_active_blocks(self) -> None:
        plan = build_execution_plan({"reflexion_loops": 2})
        caps = TransportCapabilities(frozenset())
        receipt = resolve_gateway_receipt(plan, caps, {})
        # reflexion is POLICY_REQUIRED + orchestration IGNORED → blocked
        assert receipt.aggregate_blocked is True

    def test_scratchpad_leak_unsupported(self) -> None:
        plan = build_execution_plan({"scratchpad": "secret"})
        caps = TransportCapabilities(frozenset())
        # The forbidden key leaks onto observed transport.
        receipt = resolve_gateway_receipt(plan, caps, {"scratchpad": "secret"})
        row = next(r for r in receipt.ledger if r.control_name == "scratchpad_transport_guard")
        assert row.receipt_state == ReceiptState.UNSUPPORTED
        assert receipt.aggregate_blocked is True

    def test_scratchpad_absent_applied(self) -> None:
        plan = build_execution_plan({"scratchpad": "secret"})
        caps = TransportCapabilities(frozenset())
        receipt = resolve_gateway_receipt(plan, caps, {})  # not leaked
        row = next(r for r in receipt.ledger if r.control_name == "scratchpad_transport_guard")
        assert row.receipt_state == ReceiptState.APPLIED
        assert receipt.aggregate_blocked is False

    def test_quality_required_denies_certification(self) -> None:
        plan = build_execution_plan({"cot_paths": 3})
        caps = TransportCapabilities(frozenset())
        receipt = resolve_gateway_receipt(plan, caps, {})
        # cot_paths QUALITY_REQUIRED + orchestration always IGNORED → denied
        assert receipt.quality_certification_denied is True
        assert reasoning_quality_certification_allowed(receipt) is False

    def test_empty_request_is_clean(self) -> None:
        plan = build_execution_plan({})
        caps = TransportCapabilities(frozenset())
        receipt = resolve_gateway_receipt(plan, caps, {})
        assert receipt.aggregate_blocked is False
        assert receipt.aggregate_review is False
        assert receipt.quality_certification_denied is False
        assert reasoning_quality_certification_allowed(receipt) is True


class TestEnforceBlocked:
    def test_no_raise_when_not_blocked(self) -> None:
        plan = build_execution_plan({})
        receipt = resolve_gateway_receipt(plan, TransportCapabilities(frozenset()), {})
        enforce_blocked(receipt)  # should not raise

    def test_policy_block_raises_with_policy_prefix(self) -> None:
        plan = build_execution_plan({"reflexion_loops": 2})
        receipt = resolve_gateway_receipt(plan, TransportCapabilities(frozenset()), {})
        with pytest.raises(ReasoningGovernanceError, match="POLICY_BLOCKED:reflexion_loops"):
            enforce_blocked(receipt)
