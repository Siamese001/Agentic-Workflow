"""Unit tests for L2 Execute v3 named-receipt schemas.

Validates each v3 sub-item closure:
    E1.4 DeterminismBundle (incl. attempt_seed)
    E1.6 LineageRoot
    E1.8 PrepReceipt
    E2.8 ValidationReceipt
    E3.8 AttemptReceipt
    E4.7 HealReceipt
    E5.8 DispatchReceipt + invariant (no commit payload)
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    DeterminismBundle,
    DispatchReceipt,
    HealOutcomeStamp,
    HealReceipt,
    LineageRoot,
    PrepReceipt,
    ResultClass,
    SnapshotMismatchError,
    TerminalStamp,
    ValidationOutcome,
    ValidationReceipt,
    assert_snapshot_match,
)

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def determinism() -> DeterminismBundle:
    return DeterminismBundle(
        blueprint_hash="bp-abc",
        policy_hash="pol-xyz",
        prompt_hash="prompt-1",
        input_hash="input-1",
        replay_key="replay-1",
        attempt_seed="seed-001",
    )


@pytest.fixture
def lineage() -> LineageRoot:
    return LineageRoot(
        parent_route_id="route-1",
        parent_plan_id="plan-1",
        parent_step_id="step-1",
        ancestry_chain=("route-0", "plan-0", "step-0"),
        same_run_packet_family="family-1",
    )


@pytest.fixture
def prep(determinism: DeterminismBundle, lineage: LineageRoot) -> PrepReceipt:
    return PrepReceipt(
        prep_receipt_id=PrepReceipt.new_id(),
        run_id="run-1",
        idempotency_key="idem-1",
        route_id="route-1",
        step_id="step-1",
        capability_token="cap-1",
        compliance_hash="comp-1",
        sandbox_envelope_id="env-1",
        determinism=determinism,
        lineage=lineage,
    )


# ---------------------------------------------------------------------------
# E1.4 DeterminismBundle
# ---------------------------------------------------------------------------


class TestDeterminismBundle:
    def test_carries_all_v3_fields_including_attempt_seed(
        self, determinism: DeterminismBundle
    ) -> None:
        d = determinism.as_dict()
        assert set(d.keys()) == {
            "blueprint_hash",
            "policy_hash",
            "prompt_hash",
            "input_hash",
            "replay_key",
            "attempt_seed",
        }
        assert d["attempt_seed"] == "seed-001"

    def test_is_frozen(self, determinism: DeterminismBundle) -> None:
        with pytest.raises(FrozenInstanceError):
            determinism.blueprint_hash = "tamper"  # type: ignore[misc]

    def test_snapshot_match_passes_when_blueprint_and_policy_agree(
        self, determinism: DeterminismBundle
    ) -> None:
        other = DeterminismBundle(
            blueprint_hash=determinism.blueprint_hash,
            policy_hash=determinism.policy_hash,
            prompt_hash="different",
            input_hash="different",
            replay_key="different",
            attempt_seed="different",
        )
        # Other fields legitimately drift across heal attempts.
        assert_snapshot_match(determinism, other)

    def test_snapshot_match_raises_on_blueprint_drift(
        self, determinism: DeterminismBundle
    ) -> None:
        bad = DeterminismBundle(
            blueprint_hash="bp-WRONG",
            policy_hash=determinism.policy_hash,
            prompt_hash="x",
            input_hash="x",
            replay_key="x",
            attempt_seed="x",
        )
        with pytest.raises(SnapshotMismatchError, match="blueprint_hash mismatch"):
            assert_snapshot_match(determinism, bad)

    def test_snapshot_match_raises_on_policy_drift(
        self, determinism: DeterminismBundle
    ) -> None:
        bad = DeterminismBundle(
            blueprint_hash=determinism.blueprint_hash,
            policy_hash="pol-WRONG",
            prompt_hash="x",
            input_hash="x",
            replay_key="x",
            attempt_seed="x",
        )
        with pytest.raises(SnapshotMismatchError, match="policy_hash mismatch"):
            assert_snapshot_match(determinism, bad)


# ---------------------------------------------------------------------------
# E1.6 LineageRoot
# ---------------------------------------------------------------------------


class TestLineageRoot:
    def test_carries_all_v3_fields(self, lineage: LineageRoot) -> None:
        d = lineage.as_dict()
        assert d["parent_route_id"] == "route-1"
        assert d["parent_plan_id"] == "plan-1"
        assert d["parent_step_id"] == "step-1"
        assert d["ancestry_chain"] == ["route-0", "plan-0", "step-0"]
        assert d["same_run_packet_family"] == "family-1"

    def test_is_frozen(self, lineage: LineageRoot) -> None:
        with pytest.raises(FrozenInstanceError):
            lineage.parent_route_id = "tamper"  # type: ignore[misc]

    def test_minimum_required_fields(self) -> None:
        # parent_plan_id and parent_step_id are nullable.
        lr = LineageRoot(parent_route_id="r", parent_plan_id=None, parent_step_id=None)
        assert lr.ancestry_chain == ()


# ---------------------------------------------------------------------------
# E1.8 PrepReceipt
# ---------------------------------------------------------------------------


class TestPrepReceipt:
    def test_id_prefix(self) -> None:
        assert PrepReceipt.new_id().startswith("prep-")

    def test_carries_lineage_and_determinism(self, prep: PrepReceipt) -> None:
        assert prep.lineage.parent_route_id == "route-1"
        assert prep.determinism.attempt_seed == "seed-001"
        assert prep.capability_token == "cap-1"

    def test_is_frozen(self, prep: PrepReceipt) -> None:
        with pytest.raises(FrozenInstanceError):
            prep.run_id = "tamper"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# E2.8 ValidationReceipt
# ---------------------------------------------------------------------------


class TestValidationReceipt:
    def test_pass_outcome_is_approved(self, prep: PrepReceipt) -> None:
        v = ValidationReceipt(
            validation_packet_id=ValidationReceipt.new_id(),
            prep_receipt_id=prep.prep_receipt_id,
            outcome=ValidationOutcome.PASS,
            determinism=prep.determinism,
            lineage=prep.lineage,
            rules_passed=("schema", "capability", "budget"),
        )
        assert v.is_approved()
        assert v.failed_rule is None

    def test_fail_outcome_is_sealed_rejection(self, prep: PrepReceipt) -> None:
        v = ValidationReceipt(
            validation_packet_id=ValidationReceipt.new_id(),
            prep_receipt_id=prep.prep_receipt_id,
            outcome=ValidationOutcome.FAIL,
            determinism=prep.determinism,
            lineage=prep.lineage,
            failed_rule="capability_scope",
            rejection_reason="tool out of cap_token grant",
        )
        assert not v.is_approved()
        assert v.failed_rule == "capability_scope"
        assert v.rejection_reason == "tool out of cap_token grant"

    def test_id_prefix(self) -> None:
        assert ValidationReceipt.new_id().startswith("valid-")


# ---------------------------------------------------------------------------
# E3.8 AttemptReceipt
# ---------------------------------------------------------------------------


class TestAttemptReceipt:
    def test_carries_validation_packet_link(self, prep: PrepReceipt) -> None:
        a = AttemptReceipt(
            attempt_receipt_id=AttemptReceipt.new_id(),
            validation_packet_id="valid-xyz",
            attempt_count=1,
            determinism=prep.determinism,
            lineage=prep.lineage,
            trace_id="trace-1",
            span_id="span-1",
            latency_ms=12.5,
            tokens_used=42,
            return_code=0,
            result_class=ResultClass.SUCCESS,
            output_digest="sha-abc",
        )
        assert a.validation_packet_id == "valid-xyz"
        assert a.attempt_count == 1
        assert a.result_class is ResultClass.SUCCESS

    def test_all_v3_result_classes_present(self) -> None:
        # v4 extends v3 with DEGRADED_SUCCESS; assert v3 subset is preserved.
        names = {r.value for r in ResultClass}
        v3_required = {
            "SUCCESS",
            "SOFT_REPAIRABLE",
            "FAIL_TERMINAL",
            "NEEDS_HELP",
            "REJECTED",
        }
        assert v3_required.issubset(names)


# ---------------------------------------------------------------------------
# E4.7 HealReceipt
# ---------------------------------------------------------------------------


class TestHealReceipt:
    def test_pass_outcome_routes_back_to_e3(self, prep: PrepReceipt) -> None:
        h = HealReceipt(
            repair_attempt_id=HealReceipt.new_id(),
            parent_attempt_receipt_id="attempt-1",
            failed_span_id="span-1",
            reason_code="schema_drift",
            repair_count=1,
            determinism=prep.determinism,
            lineage=prep.lineage,
            outcome=HealOutcomeStamp.PASS,
        )
        assert h.routes_back_to_e3()

    def test_needs_help_does_not_route_back(self, prep: PrepReceipt) -> None:
        h = HealReceipt(
            repair_attempt_id=HealReceipt.new_id(),
            parent_attempt_receipt_id="attempt-1",
            failed_span_id=None,
            reason_code="unhealable",
            repair_count=2,
            determinism=prep.determinism,
            lineage=prep.lineage,
            outcome=HealOutcomeStamp.NEEDS_HELP,
        )
        assert not h.routes_back_to_e3()


# ---------------------------------------------------------------------------
# E5.8 DispatchReceipt + invariant
# ---------------------------------------------------------------------------


class TestDispatchReceipt:
    def test_default_targets_cover_v3_consumers(self, prep: PrepReceipt) -> None:
        d = DispatchReceipt(
            dispatch_receipt_id=DispatchReceipt.new_id(),
            sealed_l2_artifact_id="sealed-abc",
            terminal_stamp=TerminalStamp.SUCCESS,
            determinism=prep.determinism,
            lineage=prep.lineage,
            prep_receipt_id=prep.prep_receipt_id,
            validation_packet_id="valid-1",
            decisive_reason="attempt_succeeded",
        )
        assert "exit_eval" in d.targets
        assert "uwg_decision" in d.targets
        assert "l6_audit" in d.targets

    def test_carries_full_receipt_chain(self, prep: PrepReceipt) -> None:
        d = DispatchReceipt(
            dispatch_receipt_id=DispatchReceipt.new_id(),
            sealed_l2_artifact_id="sealed-abc",
            terminal_stamp=TerminalStamp.SUCCESS,
            determinism=prep.determinism,
            lineage=prep.lineage,
            prep_receipt_id=prep.prep_receipt_id,
            validation_packet_id="valid-1",
            attempt_receipt_ids=("attempt-1", "attempt-2"),
            heal_receipt_ids=("heal-1",),
            decisive_reason="ok",
        )
        assert d.attempt_receipt_ids == ("attempt-1", "attempt-2")
        assert d.heal_receipt_ids == ("heal-1",)

    def test_invariant_no_commit_payload(self, prep: PrepReceipt) -> None:
        with pytest.raises(ValueError, match="cannot carry a commit payload"):
            DispatchReceipt(
                dispatch_receipt_id=DispatchReceipt.new_id(),
                sealed_l2_artifact_id="sealed-x",
                terminal_stamp=TerminalStamp.SUCCESS,
                determinism=prep.determinism,
                lineage=prep.lineage,
                prep_receipt_id=prep.prep_receipt_id,
                validation_packet_id=None,
                has_commit_payload=True,
            )

    def test_terminal_stamps_match_v3_spec(self) -> None:
        # v4 adds DEGRADED_SUCCESS; v3 subset preserved.
        names = {t.value for t in TerminalStamp}
        v3_required = {"SUCCESS", "FAILURE", "NEEDS_HELP", "REJECTED"}
        assert v3_required.issubset(names)
