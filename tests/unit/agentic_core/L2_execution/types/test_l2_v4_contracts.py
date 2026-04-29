"""Tests for v4 formal output contracts + decision tables + full invariants.

Closes the line-item gaps surfaced in the user audit:

    E1 INPUTS (9 fields)        — WorkOrderInputs
    E1 OUTPUT (4 fields)        — PrepOutput / FrozenExecutionContext /
                                   ReplayBindings / WriteLockAssertion
    E2 OUTPUT (6 fields)        — ValidationOutput / ApprovedWorkOrder /
                                   SealedRejectionPacket / CapabilityScopeSummary /
                                   BudgetSnapshot
    E3 OUTPUT (1 field)         — TelemetryBundle
    Decision tables             — VALIDATION_PASS_RULES / VALIDATION_FAIL_RULES
    Repair taxonomy             — SAFE_LOCAL_REPAIRS / DISALLOWED_REPAIRS
    Failure matrix              — FAILURE_MATRIX (11 rows)
    Invariants registry         — L2_FULL_INVARIANTS (all 15)
    E4.6 Revalidation           — revalidate_repaired_packet
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.l2_v3_receipts import (
    DeterminismBundle,
    LineageRoot,
    ResultClass,
)
from agentic_core.L2_execution.types.l2_v4_contracts import (
    DISALLOWED_REPAIRS,
    FAILURE_MATRIX,
    L2_FULL_INVARIANTS,
    SAFE_LOCAL_REPAIRS,
    VALIDATION_FAIL_RULES,
    VALIDATION_PASS_RULES,
    ApprovedWorkOrder,
    BudgetSnapshot,
    CapabilityScopeSummary,
    CapabilitySpec,
    ExecutionForm,
    FrozenExecutionContext,
    PrepOutput,
    ReplayBindings,
    SealedRejectionPacket,
    TaskSpec,
    TelemetryBundle,
    ValidationOutput,
    WorkOrderInputs,
    WriteLockAssertion,
    is_repair_allowed,
    lookup_failure_matrix,
    revalidate_repaired_packet,
)


@pytest.fixture
def determinism() -> DeterminismBundle:
    return DeterminismBundle(
        blueprint_hash="bp-1",
        policy_hash="pol-1",
        prompt_hash="pr-1",
        input_hash="in-1",
        replay_key="rk-1",
        attempt_seed="seed-1",
    )


@pytest.fixture
def lineage() -> LineageRoot:
    return LineageRoot(parent_route_id="route-1", parent_plan_id=None, parent_step_id=None)


# ---------------------------------------------------------------------------
# E1 INPUTS — WorkOrderInputs covers all 9 v4 input identifiers
# ---------------------------------------------------------------------------


class TestE1Inputs:
    def test_work_order_inputs_carries_all_v4_fields(self) -> None:
        wo = WorkOrderInputs(
            execution_form=ExecutionForm.L3_STEP,
            task_spec=TaskSpec(intent="answer", expected_output_contract="json"),
            tool_spec=CapabilitySpec(name="grep", version="1.0"),
            model_spec=CapabilitySpec(name="claude", version="opus-4.7"),
            action_spec=CapabilitySpec(name="git_commit"),
            cost_tier="premium",
            retry_ceiling=5,
            max_repair_count=2,
            slo_slice_ms=30_000,
        )
        assert wo.execution_form is ExecutionForm.L3_STEP
        assert wo.task_spec.intent == "answer"
        assert wo.tool_spec is not None and wo.tool_spec.name == "grep"
        assert wo.model_spec is not None and wo.model_spec.name == "claude"
        assert wo.action_spec is not None
        assert wo.cost_tier == "premium"
        assert wo.retry_ceiling == 5
        assert wo.max_repair_count == 2
        assert wo.slo_slice_ms == 30_000

    def test_execution_form_enum_v4_set(self) -> None:
        names = {e.value for e in ExecutionForm}
        assert names == {"SINGLE_STEP", "L3_STEP", "RESUMED_STEP"}


# ---------------------------------------------------------------------------
# E1 OUTPUT CONTRACT — PrepOutput + sub-types
# ---------------------------------------------------------------------------


class TestE1Output:
    def test_prep_output_carries_all_v4_fields(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        ctx = FrozenExecutionContext(
            tool_registry_version="reg-1",
            model_runtime_version="rt-1",
            provider_lane="anthropic",
            filesystem_view="ro",
            network_rules="deny-default",
            secrets_scope="step-scoped",
        )
        rb = ReplayBindings(
            determinism=determinism, snapshot_manifest="manifest-1"
        )
        wl = WriteLockAssertion()
        out = PrepOutput(
            prep_receipt_id="prep-1",
            frozen_execution_context=ctx,
            run_id="run-1",
            idempotency_key="idem-1",
            lineage_root=lineage,
            replay_bindings=rb,
            write_lock_assertion=wl,
            ready_for_validation=True,
        )
        assert out.frozen_execution_context.provider_lane == "anthropic"
        assert out.replay_bindings.determinism.blueprint_hash == "bp-1"
        assert out.write_lock_assertion.no_direct_l4_path is True
        assert out.ready_for_validation is True
        assert out.refusal_reason == ""

    def test_prep_output_refusal_path(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        out = PrepOutput(
            prep_receipt_id="prep-2",
            frozen_execution_context=FrozenExecutionContext(
                tool_registry_version="x",
                model_runtime_version="x",
                provider_lane="x",
                filesystem_view="x",
                network_rules="x",
                secrets_scope="x",
            ),
            run_id="run-2",
            idempotency_key="idem-2",
            lineage_root=lineage,
            replay_bindings=ReplayBindings(
                determinism=determinism, snapshot_manifest=""
            ),
            write_lock_assertion=WriteLockAssertion(),
            ready_for_validation=False,
            refusal_reason="missing_capability_token",
        )
        assert out.ready_for_validation is False
        assert out.refusal_reason == "missing_capability_token"


# ---------------------------------------------------------------------------
# E2 OUTPUT CONTRACT
# ---------------------------------------------------------------------------


class TestE2Output:
    def test_approved_work_order_carries_v4_fields(self) -> None:
        cap = CapabilityScopeSummary(
            capability_token_id="ct-1",
            granted_tools=("grep",),
            granted_models=("claude",),
            side_effect_envelope="READ",
        )
        budget = BudgetSnapshot(
            timeout_ms=60000,
            retry_ceiling=3,
            repair_ceiling=3,
            token_limit=8000,
            compute_limit=100,
        )
        awo = ApprovedWorkOrder(
            validation_packet_id="v-1",
            decisive_rule_id="rule_packet_signed",
            capability_scope=cap,
            budget_snapshot=budget,
            side_effect_class="READ",
        )
        assert awo.decisive_rule_id == "rule_packet_signed"
        assert awo.capability_scope.granted_tools == ("grep",)
        assert awo.budget_snapshot.token_limit == 8000
        assert awo.side_effect_class == "READ"

    def test_sealed_rejection_packet_carries_v4_fields(self) -> None:
        rej = SealedRejectionPacket(
            rejection_packet_id="rej-1",
            failed_validation_rule="action_outside_capability",
            side_effect_class="ACTION",
            missing_or_invalid_authority_field="capability_token",
            suggested_reentry_target="L0",
            decisive_rule_id="rule_capability_scope",
        )
        assert rej.failed_validation_rule == "action_outside_capability"
        assert rej.suggested_reentry_target == "L0"
        assert rej.decisive_rule_id == "rule_capability_scope"

    def test_validation_output_pass_path(self) -> None:
        out = ValidationOutput(
            validation_packet_id="v-1",
            validation_status="PASS",
            approved_work_order=ApprovedWorkOrder(
                validation_packet_id="v-1",
                decisive_rule_id="rule_packet_signed",
                capability_scope=CapabilityScopeSummary(
                    capability_token_id="ct"
                ),
                budget_snapshot=BudgetSnapshot(
                    timeout_ms=1, retry_ceiling=1, repair_ceiling=1,
                    token_limit=1, compute_limit=1,
                ),
                side_effect_class="READ",
            ),
        )
        assert out.validation_status == "PASS"
        assert out.approved_work_order is not None
        assert out.sealed_rejection_packet is None

    def test_validation_output_fail_path(self) -> None:
        out = ValidationOutput(
            validation_packet_id="v-2",
            validation_status="FAIL",
            sealed_rejection_packet=SealedRejectionPacket(
                rejection_packet_id="rej-1",
                failed_validation_rule="malformed_tool_args",
                side_effect_class="UNKNOWN",
                missing_or_invalid_authority_field="",
                suggested_reentry_target="L1",
                decisive_rule_id="rule_schema_shape",
            ),
        )
        assert out.validation_status == "FAIL"
        assert out.approved_work_order is None
        assert out.sealed_rejection_packet is not None


# ---------------------------------------------------------------------------
# E3 OUTPUT — TelemetryBundle
# ---------------------------------------------------------------------------


class TestE3Output:
    def test_telemetry_bundle_carries_v4_fields(self) -> None:
        tb = TelemetryBundle(
            trace_id="trace-1",
            span_ids=("span-1", "span-2"),
            parent_span_id="parent-1",
            latency_ms=12.5,
            tokens_used=42,
            cost_units=0.01,
            stdout_summary="ok",
            stderr_summary="",
            return_code=0,
            input_byte_count=1024,
            output_byte_count=2048,
            file_touches=("/tmp/out.txt",),
            network_destinations=("api.x.com",),
            model_or_tool_name="grep",
            provider_lane="local",
            circuit_breaker_state="CLOSED",
        )
        assert tb.trace_id == "trace-1"
        assert tb.span_ids == ("span-1", "span-2")
        assert tb.tokens_used == 42
        assert tb.file_touches == ("/tmp/out.txt",)


# ---------------------------------------------------------------------------
# Decision tables
# ---------------------------------------------------------------------------


class TestValidationDecisionTable:
    def test_pass_rules_match_v4_spec(self) -> None:
        # v4 §VALIDATION DECISION TABLE PASS section.
        for rule in (
            "packet_signed",
            "authority_scoped",
            "schema_valid",
            "side_effects_fit_envelope",
            "budget_sufficient",
            "replay_metadata_bound",
            "no_direct_write_path",
        ):
            assert rule in VALIDATION_PASS_RULES

    def test_fail_rules_match_v4_spec(self) -> None:
        # v4 §VALIDATION DECISION TABLE FAIL section.
        for rule in (
            "invalid_signature",
            "action_outside_capability",
            "missing_sandbox_envelope",
            "malformed_tool_args",
            "high_risk_mutation_lacks_clearance",
            "prompt_or_evidence_injection_breach",
            "unsupported_output_contract",
            "no_deterministic_replay_surface",
        ):
            assert rule in VALIDATION_FAIL_RULES


class TestRepairTaxonomy:
    def test_safe_repairs_set(self) -> None:
        for tactic in (
            "json_repair_intact_source",
            "schema_coercion_deterministic_field",
            "retry_same_transient_tool_call",
            "resume_from_existing_checkpoint",
            "trim_oversized_output_preserving_required_fields",
        ):
            assert tactic in SAFE_LOCAL_REPAIRS
            assert is_repair_allowed(tactic)

    def test_disallowed_repairs_set(self) -> None:
        for tactic in (
            "choose_different_route",
            "ask_human_directly",
            "broaden_sandbox_or_credentials",
            "silently_switch_provider_model_tool",
            "commit_state",
            "invent_missing_facts",
        ):
            assert tactic in DISALLOWED_REPAIRS
            assert not is_repair_allowed(tactic)

    def test_disallowed_and_safe_disjoint(self) -> None:
        assert set(SAFE_LOCAL_REPAIRS).isdisjoint(set(DISALLOWED_REPAIRS))


# ---------------------------------------------------------------------------
# Failure matrix
# ---------------------------------------------------------------------------


class TestFailureMatrix:
    def test_all_eleven_rows_present(self) -> None:
        # v4 §L2 FAILURE / REPAIR / EXIT MATRIX has exactly 11 observed conditions.
        assert len(FAILURE_MATRIX) == 11

    def test_lookup_each_condition(self) -> None:
        for observed in (
            "malformed_json_output",
            "transient_tool_timeout",
            "nonzero_tool_return",
            "missing_required_input",
            "action_outside_capability",
            "sandbox_escape_attempt",
            "policy_hash_mismatch",
            "weak_evidence_for_grounded_ask",
            "proposed_durable_write",
            "duplicate_packet",
            "route_mismatch",
        ):
            row = lookup_failure_matrix(observed)
            assert row is not None, f"missing row for {observed}"
            assert row.l2_classification, f"empty classification for {observed}"
            assert row.l2_may_do
            assert row.l2_must_not_do

    def test_action_outside_capability_classified_rejected(self) -> None:
        row = lookup_failure_matrix("action_outside_capability")
        assert row is not None
        assert ResultClass.REJECTED in row.l2_classification

    def test_unknown_condition_returns_none(self) -> None:
        assert lookup_failure_matrix("nonexistent_condition") is None


# ---------------------------------------------------------------------------
# Full 15-invariant registry
# ---------------------------------------------------------------------------


class TestFullInvariants:
    def test_all_fifteen_invariants_present(self) -> None:
        ids = {inv.invariant_id for inv in L2_FULL_INVARIANTS}
        assert ids == set(range(1, 16))

    def test_each_invariant_has_title_and_description(self) -> None:
        for inv in L2_FULL_INVARIANTS:
            assert inv.title
            assert inv.description
            assert len(inv.description) > 10

    def test_specific_v4_invariant_titles(self) -> None:
        titles = {inv.invariant_id: inv.title for inv in L2_FULL_INVARIANTS}
        # Spot-check the v4 doctrine ones the first wave missed.
        assert titles[3] == "no_workflow_expansion"
        assert titles[4] == "no_unsanctioned_retrieval"
        assert titles[5] == "no_direct_human_call"
        assert titles[9] == "no_uwg_bypass"
        assert titles[10] == "no_silent_swap"
        assert titles[11] == "bounded_repair_only"
        assert titles[14] == "downstream_consumers_only"
        assert titles[15] == "honest_now_no_future_rescue"


# ---------------------------------------------------------------------------
# E4.6 Revalidation
# ---------------------------------------------------------------------------


class TestRevalidation:
    def test_pass_when_snapshot_unchanged(
        self, determinism: DeterminismBundle
    ) -> None:
        cap = CapabilityScopeSummary(
            capability_token_id="ct", side_effect_envelope="READ"
        )
        result = revalidate_repaired_packet(
            repaired_payload={"answer": "ok"},
            original_capability_scope=cap,
            original_side_effect_class="READ",
            original_determinism=determinism,
            new_determinism=determinism,
        )
        assert result.passed is True
        assert result.failed_check == ""

    def test_fail_when_blueprint_changed(
        self, determinism: DeterminismBundle
    ) -> None:
        cap = CapabilityScopeSummary(
            capability_token_id="ct", side_effect_envelope="READ"
        )
        bad = DeterminismBundle(
            blueprint_hash="bp-DRIFT",
            policy_hash=determinism.policy_hash,
            prompt_hash="x",
            input_hash="x",
            replay_key="x",
            attempt_seed="x",
        )
        result = revalidate_repaired_packet(
            repaired_payload={"answer": "ok"},
            original_capability_scope=cap,
            original_side_effect_class="READ",
            original_determinism=determinism,
            new_determinism=bad,
        )
        assert result.passed is False
        assert result.failed_check == "snapshot_binding"

    def test_fail_when_payload_none(
        self, determinism: DeterminismBundle
    ) -> None:
        cap = CapabilityScopeSummary(
            capability_token_id="ct", side_effect_envelope="READ"
        )
        result = revalidate_repaired_packet(
            repaired_payload=None,
            original_capability_scope=cap,
            original_side_effect_class="READ",
            original_determinism=determinism,
            new_determinism=determinism,
        )
        assert result.passed is False
        assert result.failed_check == "payload_shape"
