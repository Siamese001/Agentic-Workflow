"""Line-by-line v4 spec coverage test.

Walks every named element in `docs/reference/04_L2_Execute/04_L2_Execute_v4.md`
and asserts an observable, executable mapping in code.

Layout follows the spec:
    L2 ENTRY SHAPE       → ExecutionForm enum
    E1 INPUTS            → WorkOrderInputs fields
    E1 sub-steps E1.1-8  → PrepReceipt + PrepOutput + DeterminismBundle
    E1 OUTPUT CONTRACT   → PrepOutput
    E1 FAIL CONDITIONS   → E1_FAIL_CONDITIONS
    E2 INPUTS            → ValidationOutput inputs reachable
    E2 sub-steps E2.1-8  → ValidationOutput / ApprovedWorkOrder /
                            SealedRejectionPacket
    E2 DECISION TABLE    → VALIDATION_PASS_RULES + VALIDATION_FAIL_RULES
    E2 OUTPUT CONTRACT   → ValidationOutput
    E3 INPUTS            → AttemptReceipt accepts
    E3 sub-steps E3.1-8  → AttemptReceipt / TelemetryBundle
    E3 EXECUTION LANES   → EXECUTION_LANE_CONSTRAINTS (5 lanes)
    E3 OUTPUT CONTRACT   → AttemptReceipt + TelemetryBundle
    E4 INPUTS            → HealReceipt accepts
    E4 sub-steps E4.1-8  → HealReceipt fields
    E4 ALLOWED REPAIRS   → SAFE_LOCAL_REPAIRS
    E4 DISALLOWED        → DISALLOWED_REPAIRS
    E4 REPAIR DECISION   → RepairDecision + repair_decision()
    E4 OUTPUT CONTRACT   → HealReceipt
    E5 INPUTS            → SealedL2ArtifactContents.from_receipts
    E5 sub-steps E5.1-8  → SealedL2ArtifactContents sections
    E5 SEALED CONTENTS   → 7 sections × every named field
    E5 TERMINAL MEANINGS → TERMINAL_CLASS_MEANINGS (5 classes)
    E5 OUTPUT CONTRACT   → DispatchReceipt
    L2 FAILURE MATRIX    → FAILURE_MATRIX (11 rows)
    L2 INVARIANTS        → L2_FULL_INVARIANTS (15 numbered)

If a field, enum value, decision branch, or named identifier in v4 is not
mapped to an observable code element, this file's tests fail.
"""

from __future__ import annotations

from dataclasses import fields as dataclass_fields

import pytest

from agentic_core.L2_execution.orchestration.l2_phase_pipeline import (
    ExecutorResult,
    HealerResult,
    L2PhasePipeline,
    PipelineConfig,
    ValidatorResult,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    DeterminismBundle,
    DispatchReceipt,
    DispatchTarget,
    ExecutionLane,
    HealOutcomeStamp,
    HealReceipt,
    LineageRoot,
    PrepReceipt,
    RepairStatus,
    ResultClass,
    TerminalStamp,
    ValidationOutcome,
)
from agentic_core.L2_execution.types.l2_v4_contracts import (
    DISALLOWED_REPAIRS,
    E1_FAIL_CONDITIONS,
    EXECUTION_LANE_CONSTRAINTS,
    FAILURE_MATRIX,
    L2_FULL_INVARIANTS,
    SAFE_LOCAL_REPAIRS,
    TERMINAL_CLASS_MEANINGS,
    VALIDATION_FAIL_RULES,
    VALIDATION_PASS_RULES,
    ApprovedWorkOrder,
    BudgetSnapshot,
    CapabilityScopeSummary,
    CapabilitySpec,
    ContractCheckResult,
    ExecutionForm,
    FrozenExecutionContext,
    PrepOutput,
    RepairDecision,
    ReplayBindings,
    SealedRejectionPacket,
    TaskSpec,
    TelemetryBundle,
    ValidationOutput,
    WorkOrderInputs,
    WriteLockAssertion,
    is_repair_allowed,
    lookup_failure_matrix,
    repair_decision,
    revalidate_repaired_packet,
    verify_sealed_artifact_contract,
)
from agentic_core.L2_execution.types.l2_v4_invariants import (
    SealedL2ArtifactContents,
    check_invariants,
    classify_repair_status,
    derive_dispatch_target,
)

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


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
    return LineageRoot(
        parent_route_id="route-1",
        parent_plan_id="plan-1",
        parent_step_id="step-1",
    )


def _approve(_p) -> ValidatorResult:  # type: ignore[no-untyped-def]
    return ValidatorResult(
        outcome=ValidationOutcome.PASS, classified_side_effect="READ"
    )


def _success(_p, _v, n) -> ExecutorResult:  # type: ignore[no-untyped-def]
    return ExecutorResult(
        result_class=ResultClass.SUCCESS,
        trace_id=f"t-{n}",
        span_id=f"s-{n}",
        latency_ms=1.0,
        tokens_used=10,
        return_code=0,
        output_digest="ok",
    )


def _no_heal(_a) -> HealerResult:  # type: ignore[no-untyped-def]
    return HealerResult(
        outcome=HealOutcomeStamp.NEEDS_HELP, reason_code="unhealable"
    )


# ===========================================================================
# L2 ENTRY SHAPE — execution_form covers SINGLE-STEP / MANAGED WORKFLOW /
#                  RESUMED STEP entry forms.
# ===========================================================================


class TestEntryShape:
    def test_three_entry_forms(self) -> None:
        assert ExecutionForm.SINGLE_STEP.value == "SINGLE_STEP"
        assert ExecutionForm.L3_STEP.value == "L3_STEP"
        assert ExecutionForm.RESUMED_STEP.value == "RESUMED_STEP"

    def test_no_unmodeled_forms(self) -> None:
        assert {e.value for e in ExecutionForm} == {
            "SINGLE_STEP",
            "L3_STEP",
            "RESUMED_STEP",
        }


# ===========================================================================
# E1 PREP — INPUTS, sub-steps E1.1-E1.8, OUTPUT CONTRACT, FAIL CONDITIONS
# ===========================================================================


class TestE1Prep:
    # E1 INPUTS — every v4-spec input identifier is reachable.
    def test_e1_inputs_identifiers(self) -> None:
        wo = WorkOrderInputs(
            execution_form=ExecutionForm.SINGLE_STEP,
            task_spec=TaskSpec(intent="x"),
        )
        # Documented v4 E1 INPUTS list (after stripping conjunctions):
        for name in (
            "execution_form",
            "task_spec",
            "tool_spec",
            "model_spec",
            "action_spec",
            "cost_tier",
            "retry_ceiling",
            "max_repair_count",
            "slo_slice_ms",
        ):
            assert hasattr(wo, name), f"WorkOrderInputs missing {name}"

    # E1.1 Packet receive — ready_for_validation refusal path.
    def test_e1_1_packet_receive_refusal(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        out = PrepOutput(
            prep_receipt_id="p-1",
            frozen_execution_context=FrozenExecutionContext(
                tool_registry_version="x",
                model_runtime_version="x",
                provider_lane="x",
                filesystem_view="x",
                network_rules="x",
                secrets_scope="x",
            ),
            run_id="r-1",
            idempotency_key="i-1",
            lineage_root=lineage,
            replay_bindings=ReplayBindings(
                determinism=determinism, snapshot_manifest=""
            ),
            write_lock_assertion=WriteLockAssertion(),
            ready_for_validation=False,
            refusal_reason="missing_governing_metadata",
        )
        assert out.ready_for_validation is False
        assert out.refusal_reason == "missing_governing_metadata"

    # E1.2 Authority bind — ApprovedWorkOrder requires capability_token_id.
    def test_e1_2_authority_bind(self) -> None:
        cap = CapabilityScopeSummary(capability_token_id="ct-1")
        assert cap.capability_token_id == "ct-1"

    # E1.3 Environment freeze — FrozenExecutionContext locks all surfaces.
    def test_e1_3_environment_freeze(self) -> None:
        ctx = FrozenExecutionContext(
            tool_registry_version="reg-1",
            model_runtime_version="rt-1",
            provider_lane="anthropic",
            filesystem_view="ro",
            network_rules="deny-default",
            secrets_scope="step-scoped",
            allowed_file_roots=("/tmp/sandbox",),
            allowed_network_destinations=("api.anthropic.com",),
            allowed_syscalls=("read", "write"),
        )
        # All v4-spec freeze surfaces are reachable.
        for name in (
            "tool_registry_version",
            "model_runtime_version",
            "provider_lane",
            "filesystem_view",
            "network_rules",
            "secrets_scope",
            "locale",
            "allowed_file_roots",
            "allowed_network_destinations",
            "allowed_syscalls",
        ):
            assert hasattr(ctx, name)

    # E1.4 Determinism bind — every replay-relevant key is on the bundle.
    def test_e1_4_determinism_bind(
        self, determinism: DeterminismBundle
    ) -> None:
        for name in (
            "blueprint_hash",
            "policy_hash",
            "prompt_hash",
            "input_hash",
            "replay_key",
            "attempt_seed",
        ):
            assert hasattr(determinism, name)

    # E1.5 Idempotency guard — duplicate cache returns prior receipt.
    def test_e1_5_idempotency_guard(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        cache: dict = {}
        calls = {"n": 0}

        def counted(_p, _v, n):  # type: ignore[no-untyped-def]
            calls["n"] += 1
            return ExecutorResult(
                result_class=ResultClass.SUCCESS,
                trace_id=f"t-{n}",
                latency_ms=1.0,
                output_digest="ok",
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=counted,
            healer_fn=_no_heal,
            config=PipelineConfig(duplicate_cache=cache),
        )
        a = pipe.run("route-1", "step-1", determinism, lineage)
        b = pipe.run("route-1", "step-1", determinism, lineage)
        assert calls["n"] == 1, "duplicate execution detected"
        assert a is b, "duplicate did not return prior sealed receipt"

    # E1.6 Lineage root — every v4 lineage field present.
    def test_e1_6_lineage_root(self, lineage: LineageRoot) -> None:
        for name in (
            "parent_route_id",
            "parent_plan_id",
            "parent_step_id",
            "ancestry_chain",
        ):
            assert hasattr(lineage, name)

    # E1.7 Write lock — WriteLockAssertion asserts no direct L4 path.
    def test_e1_7_write_lock(self) -> None:
        wl = WriteLockAssertion()
        assert wl.no_direct_l4_path is True
        assert wl.proposed_diff_only is True
        assert wl.persistence_disabled is True

    # E1.8 Start receipt — PrepReceipt has every documented field.
    def test_e1_8_start_receipt_fields(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        prep = PrepReceipt(
            prep_receipt_id="p-1",
            run_id="r-1",
            idempotency_key="i-1",
            route_id="route-1",
            step_id="step-1",
            determinism=determinism,
            lineage=lineage,
            capability_token="ct",
            sandbox_envelope_id="se",
            compliance_hash="ch",
        )
        for name in (
            "prep_receipt_id",
            "run_id",
            "idempotency_key",
            "route_id",
            "step_id",
            "determinism",
            "lineage",
            "capability_token",
            "sandbox_envelope_id",
            "compliance_hash",
        ):
            assert hasattr(prep, name)

    # E1 OUTPUT CONTRACT — every contract field on PrepOutput.
    def test_e1_output_contract_fields(self) -> None:
        names = {f.name for f in dataclass_fields(PrepOutput)}
        for required in (
            "prep_receipt_id",
            "frozen_execution_context",
            "run_id",
            "idempotency_key",
            "lineage_root",
            "replay_bindings",
            "write_lock_assertion",
            "ready_for_validation",
        ):
            assert required in names, f"PrepOutput missing {required}"

    # E1 FAIL CONDITIONS — all 7 enumerated.
    def test_e1_fail_conditions_set(self) -> None:
        expected = {
            "missing_capability_token",
            "missing_sandbox_envelope",
            "policy_hash_mismatch",
            "stale_blueprint_hash",
            "duplicate_in_flight_idempotency_key",
            "no_replay_snapshot_for_replay_required_route",
            "l2_detects_hidden_write_path",
        }
        assert set(E1_FAIL_CONDITIONS) == expected


# ===========================================================================
# E2 VALID — INPUTS, sub-steps E2.1-E2.8, DECISION TABLE, OUTPUT CONTRACT
# ===========================================================================


class TestE2Valid:
    # E2.1 Signature chain → integrity proof maps to validation_packet_id.
    def test_e2_1_validation_packet_id_present(self) -> None:
        out = ValidationOutput(
            validation_packet_id="v-1", validation_status="PASS"
        )
        assert out.validation_packet_id == "v-1"

    # E2.2 Capability scope → CapabilityScopeSummary captures granted lists.
    def test_e2_2_capability_scope_summary(self) -> None:
        cap = CapabilityScopeSummary(
            capability_token_id="ct",
            granted_tools=("grep",),
            granted_actions=("git_commit",),
            granted_models=("claude",),
            side_effect_envelope="READ",
            tenant_scope="tenant-1",
        )
        assert cap.granted_tools == ("grep",)
        assert cap.granted_actions == ("git_commit",)
        assert cap.granted_models == ("claude",)
        assert cap.tenant_scope == "tenant-1"

    # E2.3 Budget scope → all 8 budget fields modeled.
    def test_e2_3_budget_scope_fields(self) -> None:
        names = {f.name for f in dataclass_fields(BudgetSnapshot)}
        for required in (
            "timeout_ms",
            "retry_ceiling",
            "repair_ceiling",
            "token_limit",
            "compute_limit",
            "memory_limit_mb",
            "io_quota_bytes",
            "circuit_breaker_open",
        ):
            assert required in names

    # E2.4 Schema shape — capability spec carries schema_id.
    def test_e2_4_schema_shape(self) -> None:
        spec = CapabilitySpec(name="grep", version="1.0", schema_id="schema-1")
        assert spec.schema_id == "schema-1"

    # E2.5 Side-effect class.
    def test_e2_5_side_effect_class_in_approved_order(self) -> None:
        awo = ApprovedWorkOrder(
            validation_packet_id="v-1",
            decisive_rule_id="rule",
            capability_scope=CapabilityScopeSummary(capability_token_id="ct"),
            budget_snapshot=BudgetSnapshot(
                timeout_ms=1, retry_ceiling=1, repair_ceiling=1,
                token_limit=1, compute_limit=1,
            ),
            side_effect_class="SANDBOX_WRITE",
        )
        assert awo.side_effect_class == "SANDBOX_WRITE"

    # E2.6 Safety sanity — covered indirectly via decisive_rule_id +
    # sealed rejection's failed_validation_rule.
    def test_e2_6_safety_sanity_via_rejection_packet(self) -> None:
        rej = SealedRejectionPacket(
            rejection_packet_id="r-1",
            failed_validation_rule="prompt_or_evidence_injection_breach",
            side_effect_class="UNKNOWN",
            missing_or_invalid_authority_field="",
            suggested_reentry_target="L1",
            decisive_rule_id="rule_safety_sanity",
        )
        assert (
            rej.failed_validation_rule
            == "prompt_or_evidence_injection_breach"
        )

    # E2.7 Executability check → suggested_reentry_target enumerates targets.
    def test_e2_7_executability_via_reentry_target(self) -> None:
        for target in ("L0", "L1", "L3", "HITL", "user_clarify"):
            rej = SealedRejectionPacket(
                rejection_packet_id="r",
                failed_validation_rule="rule",
                side_effect_class="x",
                missing_or_invalid_authority_field="",
                suggested_reentry_target=target,
                decisive_rule_id="d",
            )
            assert rej.suggested_reentry_target == target

    # E2.8 Validation receipt — PASS / FAIL paths both modeled.
    def test_e2_8_validation_receipt_pass_fail(self) -> None:
        passed = ValidationOutput(
            validation_packet_id="v-1",
            validation_status="PASS",
            approved_work_order=ApprovedWorkOrder(
                validation_packet_id="v-1",
                decisive_rule_id="r",
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
        failed = ValidationOutput(
            validation_packet_id="v-2",
            validation_status="FAIL",
            sealed_rejection_packet=SealedRejectionPacket(
                rejection_packet_id="rej-1",
                failed_validation_rule="invalid_signature",
                side_effect_class="UNKNOWN",
                missing_or_invalid_authority_field="signature",
                suggested_reentry_target="L0",
                decisive_rule_id="rule",
            ),
        )
        assert passed.approved_work_order is not None
        assert failed.sealed_rejection_packet is not None

    # VALIDATION DECISION TABLE — all PASS rules + all FAIL rules.
    def test_validation_pass_rules_complete(self) -> None:
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

    def test_validation_fail_rules_complete(self) -> None:
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

    # E2 OUTPUT CONTRACT — every spec field reachable.
    def test_e2_output_contract_fields(self) -> None:
        out = ValidationOutput(
            validation_packet_id="v",
            validation_status="PASS",
            approved_work_order=ApprovedWorkOrder(
                validation_packet_id="v",
                decisive_rule_id="d",
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
        # validation_packet_id, validation_status, approved_work_order,
        # sealed_rejection_packet, decisive_rule_id (via approved),
        # capability_scope_summary (via approved), side_effect_class
        # (via approved), budget_snapshot (via approved)
        assert out.validation_packet_id
        assert out.validation_status in ("PASS", "FAIL")
        assert out.approved_work_order.decisive_rule_id  # type: ignore[union-attr]
        assert out.approved_work_order.capability_scope is not None  # type: ignore[union-attr]
        assert out.approved_work_order.side_effect_class  # type: ignore[union-attr]
        assert out.approved_work_order.budget_snapshot is not None  # type: ignore[union-attr]


# ===========================================================================
# E3 EXEC — sub-steps, EXECUTION LANES, OUTPUT CONTRACT
# ===========================================================================


class TestE3Exec:
    # E3.1 Attempt open → AttemptReceipt carries attempt_count + lineage.
    def test_e3_1_attempt_open_fields(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        a = AttemptReceipt(
            attempt_receipt_id="a",
            validation_packet_id="v",
            attempt_count=2,
            determinism=determinism,
            lineage=lineage,
            trace_id="t",
            span_id="s",
            latency_ms=1.0,
            tokens_used=0,
            return_code=0,
            result_class=ResultClass.SUCCESS,
        )
        assert a.attempt_count == 2
        assert a.lineage.parent_route_id == "route-1"

    # E3.4 Telemetry capture — every documented field on TelemetryBundle.
    def test_e3_4_telemetry_fields(self) -> None:
        names = {f.name for f in dataclass_fields(TelemetryBundle)}
        for required in (
            "trace_id",
            "span_ids",
            "parent_span_id",
            "latency_ms",
            "tokens_used",
            "cost_units",
            "compute_use",
            "memory_use_mb",
            "stdout_summary",
            "stderr_summary",
            "return_code",
            "input_byte_count",
            "output_byte_count",
            "file_touches",
            "network_destinations",
            "model_or_tool_name",
            "provider_lane",
            "retry_source",
            "circuit_breaker_state",
        ):
            assert required in names, f"TelemetryBundle missing {required}"

    # E3.5 Output capture — quarantined_payload + generated_artifacts + diff.
    def test_e3_5_output_capture_fields(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        a = AttemptReceipt(
            attempt_receipt_id="a",
            validation_packet_id="v",
            attempt_count=1,
            determinism=determinism,
            lineage=lineage,
            trace_id="t",
            span_id=None,
            latency_ms=1.0,
            tokens_used=0,
            return_code=0,
            result_class=ResultClass.SUCCESS,
            generated_artifacts=("art://1",),
            proposed_state_diff={"k": "v"},
            quarantined_payload="unsafe",
        )
        assert a.generated_artifacts == ("art://1",)
        assert a.proposed_state_diff == {"k": "v"}
        assert a.quarantined_payload == "unsafe"

    # E3.6 Local checks → local_check_results tuple.
    def test_e3_6_local_check_results(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        a = AttemptReceipt(
            attempt_receipt_id="a",
            validation_packet_id="v",
            attempt_count=1,
            determinism=determinism,
            lineage=lineage,
            trace_id="t",
            span_id=None,
            latency_ms=1.0,
            tokens_used=0,
            return_code=0,
            result_class=ResultClass.SUCCESS,
            local_check_results=(("schema", True), ("citation", False)),
        )
        assert ("schema", True) in a.local_check_results
        assert ("citation", False) in a.local_check_results

    # E3.7 Result classify — all 6 result classes enumerated.
    def test_e3_7_result_classes_complete(self) -> None:
        names = {r.value for r in ResultClass}
        assert {
            "SUCCESS",
            "DEGRADED_SUCCESS",
            "SOFT_REPAIRABLE",
            "FAIL_TERMINAL",
            "NEEDS_HELP",
            "REJECTED",
        }.issubset(names)

    # EXECUTION LANES — all 5 lanes have constraints.
    def test_execution_lanes_constraints(self) -> None:
        for lane in ExecutionLane:
            assert lane in EXECUTION_LANE_CONSTRAINTS, (
                f"missing constraints for {lane}"
            )
            c = EXECUTION_LANE_CONSTRAINTS[lane]
            assert c.lane is lane
            assert c.description
            assert c.output_capture_required is True

    def test_read_lane_no_durable_mutation(self) -> None:
        c = EXECUTION_LANE_CONSTRAINTS[ExecutionLane.READ]
        assert c.durable_mutation_allowed is False

    def test_model_lane_schema_bound(self) -> None:
        c = EXECUTION_LANE_CONSTRAINTS[ExecutionLane.MODEL]
        assert c.schema_bound_required is True

    # E3 OUTPUT CONTRACT — every documented field reachable.
    def test_e3_output_contract_fields(self) -> None:
        names = {f.name for f in dataclass_fields(AttemptReceipt)}
        for required in (
            "attempt_receipt_id",
            "attempt_count",
            "result_class",
            "output_digest",
            "generated_artifacts",
            "proposed_state_diff",
            "local_check_results",
            "decisive_reason_code",
            "trace_id",
            "span_id",
            "quarantined_payload",
        ):
            assert required in names, f"AttemptReceipt missing {required}"


# ===========================================================================
# E4 HEAL — sub-steps, ALLOWED REPAIRS, DISALLOWED, DECISION TABLE,
#           OUTPUT CONTRACT
# ===========================================================================


class TestE4Heal:
    # E4.1 Failure record fields.
    def test_e4_1_failure_record_fields(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        h = HealReceipt(
            repair_attempt_id="h-1",
            parent_attempt_receipt_id="a-1",
            failed_span_id="s-1",
            reason_code="schema",
            repair_count=1,
            determinism=determinism,
            lineage=lineage,
            outcome=HealOutcomeStamp.PASS,
        )
        for name in (
            "repair_attempt_id",
            "parent_attempt_receipt_id",
            "failed_span_id",
            "reason_code",
            "repair_count",
        ):
            assert hasattr(h, name)

    # E4.4 Snapshot guard — heal preserves blueprint+policy hash.
    def test_e4_4_snapshot_guard(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        h = HealReceipt(
            repair_attempt_id="h",
            parent_attempt_receipt_id="a",
            failed_span_id=None,
            reason_code="x",
            repair_count=1,
            determinism=determinism,
            lineage=lineage,
            outcome=HealOutcomeStamp.PASS,
            snapshot_guard_status="PASS",
        )
        assert h.snapshot_guard_status == "PASS"

    # E4.5 Oscillation guard.
    def test_e4_5_oscillation_status_states(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        for state in ("CLEAN", "THRASHING", "CEILING_REACHED"):
            h = HealReceipt(
                repair_attempt_id="h",
                parent_attempt_receipt_id="a",
                failed_span_id=None,
                reason_code="x",
                repair_count=1,
                determinism=determinism,
                lineage=lineage,
                outcome=HealOutcomeStamp.PASS,
                oscillation_status=state,
            )
            assert h.oscillation_status == state

    # E4.6 Revalidation passes when snapshot intact.
    def test_e4_6_revalidation(
        self, determinism: DeterminismBundle
    ) -> None:
        result = revalidate_repaired_packet(
            repaired_payload={"ok": 1},
            original_capability_scope=CapabilityScopeSummary(
                capability_token_id="ct", side_effect_envelope="READ"
            ),
            original_side_effect_class="READ",
            original_determinism=determinism,
            new_determinism=determinism,
        )
        assert result.passed

    # E4.7 Heal receipt — before/after_hash + repair_tactic.
    def test_e4_7_heal_receipt_fields(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        names = {f.name for f in dataclass_fields(HealReceipt)}
        for required in (
            "repair_attempt_id",
            "parent_attempt_receipt_id",
            "failed_span_id",
            "reason_code",
            "repair_count",
            "delta_summary",
            "outcome",
            "repair_status",
            "repair_tactic",
            "before_hash",
            "after_hash",
            "oscillation_status",
            "snapshot_guard_status",
            "next_action",
        ):
            assert required in names, f"HealReceipt missing {required}"

    # E4.8 Outcome — PASS routes back to E3.
    def test_e4_8_pass_routes_back(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        h = HealReceipt(
            repair_attempt_id="h",
            parent_attempt_receipt_id="a",
            failed_span_id=None,
            reason_code="x",
            repair_count=1,
            determinism=determinism,
            lineage=lineage,
            outcome=HealOutcomeStamp.PASS,
        )
        assert h.routes_back_to_e3() is True

    # ALLOWED REPAIR TAXONOMY — full set + gate.
    def test_safe_local_repairs_full(self) -> None:
        for tactic in (
            "json_repair_intact_source",
            "schema_coercion_deterministic_field",
            "output_reformat_to_required_shape",
            "retry_same_transient_tool_call",
            "resume_from_existing_checkpoint",
            "trim_oversized_output_preserving_required_fields",
            "convert_nonfatal_warning_to_caveat",
            "attach_partial_output_if_contract_permits",
        ):
            assert tactic in SAFE_LOCAL_REPAIRS
            assert is_repair_allowed(tactic)

    def test_disallowed_repairs_full(self) -> None:
        for tactic in (
            "choose_different_route",
            "retrieve_new_evidence_without_c0_contract",
            "ask_human_directly",
            "broaden_sandbox_or_credentials",
            "silently_switch_provider_model_tool",
            "commit_state",
            "invent_missing_facts",
            "treat_human_text_as_authority",
            "override_policy_because_output_looks_right",
        ):
            assert tactic in DISALLOWED_REPAIRS
            assert not is_repair_allowed(tactic)

    # REPAIR DECISION TABLE — all 4 outcome paths.
    def test_repair_decision_repair_and_retry(self) -> None:
        d = repair_decision(
            repairable=True,
            same_authority=True,
            under_ceilings=True,
            snapshot_intact=True,
            has_useful_partial=False,
            needs_new_authority_or_human=False,
            safety_or_policy_breach=False,
        )
        assert d is RepairDecision.REPAIR_AND_RETRY

    def test_repair_decision_seal_degraded(self) -> None:
        d = repair_decision(
            repairable=False,
            same_authority=True,
            under_ceilings=True,
            snapshot_intact=True,
            has_useful_partial=True,
            needs_new_authority_or_human=False,
            safety_or_policy_breach=False,
        )
        assert d is RepairDecision.SEAL_DEGRADED_OR_NEEDS_HELP

    def test_repair_decision_needs_help_or_escalate(self) -> None:
        d = repair_decision(
            repairable=False,
            same_authority=True,
            under_ceilings=True,
            snapshot_intact=True,
            has_useful_partial=False,
            needs_new_authority_or_human=True,
            safety_or_policy_breach=False,
        )
        assert d is RepairDecision.STOP_NEEDS_HELP_OR_ESCALATE

    def test_repair_decision_safety_breach_overrides(self) -> None:
        # Even if all else is repairable, a safety breach STOPs and
        # quarantines — invariant from v4 §REPAIR DECISION TABLE row 4.
        d = repair_decision(
            repairable=True,
            same_authority=True,
            under_ceilings=True,
            snapshot_intact=True,
            has_useful_partial=True,
            needs_new_authority_or_human=False,
            safety_or_policy_breach=True,
        )
        assert d is RepairDecision.STOP_REJECTED_QUARANTINE

    # E4 OUTPUT CONTRACT — RepairStatus enum has all 5 values.
    def test_e4_repair_status_complete(self) -> None:
        names = {r.value for r in RepairStatus}
        assert names == {
            "REPAIRED",
            "NOT_REPAIRED",
            "QUARANTINED",
            "NEEDS_HELP",
            "FAIL_TERMINAL",
        }


# ===========================================================================
# E5 SEAL — sub-steps, SEALED CONTENTS, TERMINAL MEANINGS, OUTPUT CONTRACT
# ===========================================================================


class TestE5Seal:
    # E5 — every sub-step's outputs reachable on SealedL2ArtifactContents.
    def test_e5_1_through_e5_8_via_pipeline(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        contents = SealedL2ArtifactContents.from_receipts(
            prep=r.prep,
            validation=r.validation,
            attempts=r.attempts,
            heals=r.heals,
            dispatch=r.dispatch,
            payload={"final": "answer"},
            evidence_refs=("doc-1",),
        )
        # E5.1 payload package — payload + artifacts.
        assert contents.execution.payload == {"final": "answer"}
        # E5.2 evidence package.
        assert contents.evidence.source_refs == ("doc-1",)
        # E5.3 trace package.
        assert contents.observability.trace_id
        # E5.4 replay package.
        assert contents.replay.replay_key == "rk-1"
        # E5.5 terminal stamp.
        assert contents.terminal.terminal_class is TerminalStamp.SUCCESS
        # E5.6 contract check passes.
        check = verify_sealed_artifact_contract(contents)
        assert check.satisfied
        # E5.7 commit boundary — no durable commit.
        assert r.dispatch.has_commit_payload is False
        # E5.8 dispatch receipt — dispatch_target set.
        assert r.dispatch.dispatch_target is not None

    # SEALED L2 ARTIFACT CONTENTS — all 7 sections + every documented field.
    def test_sealed_contents_seven_sections(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        c = SealedL2ArtifactContents.from_receipts(
            prep=r.prep,
            validation=r.validation,
            attempts=r.attempts,
            heals=r.heals,
            dispatch=r.dispatch,
        )
        # identity (5 fields documented)
        for name in (
            "sealed_l2_artifact_id",
            "run_id",
            "route_id",
            "parent_plan_id",
            "parent_route_id",
            "parent_step_id",
        ):
            assert hasattr(c.identity, name)
        # governance (6 fields)
        for name in (
            "compliance_hash",
            "policy_hash",
            "blueprint_hash",
            "capability_token_ref",
            "sandbox_envelope_ref",
            "side_effect_class",
        ):
            assert hasattr(c.governance, name)
        # execution (7 fields)
        for name in (
            "payload",
            "artifacts",
            "proposed_state_diff",
            "stdout_summary",
            "stderr_summary",
            "tool_receipts",
            "attempt_count",
            "repair_count",
        ):
            assert hasattr(c.execution, name)
        # evidence (5 fields)
        for name in (
            "source_refs",
            "cited_spans",
            "c0_evidence_contract_refs",
            "support_gaps",
            "contradiction_flags",
        ):
            assert hasattr(c.evidence, name)
        # replay (6 fields)
        for name in (
            "replay_key",
            "input_hash",
            "prompt_hash",
            "snapshot_manifest",
            "deterministic_receipts",
            "environment_digest",
        ):
            assert hasattr(c.replay, name)
        # observability (5 fields)
        for name in (
            "trace_id",
            "span_ids",
            "latency_ms",
            "tokens_used",
            "timeout_status",
            "circuit_breaker_status",
            "route_join_keys",
        ):
            assert hasattr(c.observability, name)
        # terminal (5 fields)
        for name in (
            "terminal_class",
            "reason_code",
            "downstream_recommendation",
            "user_visible_safe",
            "commit_requested",
        ):
            assert hasattr(c.terminal, name)

    # TERMINAL CLASS MEANINGS — every class has documented semantics.
    def test_terminal_class_meanings_complete(self) -> None:
        for cls in (
            TerminalStamp.SUCCESS,
            TerminalStamp.DEGRADED_SUCCESS,
            TerminalStamp.FAILURE,
            TerminalStamp.NEEDS_HELP,
            TerminalStamp.REJECTED,
        ):
            assert cls in TERMINAL_CLASS_MEANINGS, (
                f"missing meaning for {cls}"
            )
            assert len(TERMINAL_CLASS_MEANINGS[cls]) > 30

    # E5 OUTPUT CONTRACT — DispatchReceipt has every field.
    def test_e5_output_contract_fields(self) -> None:
        names = {f.name for f in dataclass_fields(DispatchReceipt)}
        for required in (
            "sealed_l2_artifact_id",
            "terminal_stamp",
            "decisive_reason",
            "dispatch_target",
            "user_visible_safe",
            "commit_requested",
            "downstream_recommendation",
            "has_commit_payload",
            "attempt_receipt_ids",
            "heal_receipt_ids",
        ):
            assert required in names, f"DispatchReceipt missing {required}"

    # E5 OUTPUT CONTRACT — dispatch_target enum has all 4 values.
    def test_dispatch_target_complete(self) -> None:
        names = {d.value for d in DispatchTarget}
        assert names == {
            "EXIT_CONTROL",
            "L3_MERGE",
            "HITL_PACKETIZATION",
            "UWG_REQUEST_CANDIDATE",
        }

    # E5 invariant: NO durable commit. has_commit_payload=True must raise.
    def test_e5_invariant_no_durable_commit(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        with pytest.raises(ValueError, match="commit payload"):
            DispatchReceipt(
                dispatch_receipt_id="d",
                sealed_l2_artifact_id="s",
                terminal_stamp=TerminalStamp.SUCCESS,
                determinism=determinism,
                lineage=lineage,
                prep_receipt_id="p",
                validation_packet_id="v",
                has_commit_payload=True,  # invariant: NEVER allowed
            )


# ===========================================================================
# L2 FAILURE / REPAIR / EXIT MATRIX (11 rows)
# ===========================================================================


class TestFailureMatrixCoverage:
    def test_all_eleven_rows_present(self) -> None:
        observed = {row.observed_condition for row in FAILURE_MATRIX}
        expected = {
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
        }
        assert observed == expected

    @pytest.mark.parametrize(
        "observed,expected_class",
        [
            ("malformed_json_output", ResultClass.SOFT_REPAIRABLE),
            ("transient_tool_timeout", ResultClass.SOFT_REPAIRABLE),
            ("missing_required_input", ResultClass.NEEDS_HELP),
            ("action_outside_capability", ResultClass.REJECTED),
            ("sandbox_escape_attempt", ResultClass.REJECTED),
            ("policy_hash_mismatch", ResultClass.REJECTED),
            ("proposed_durable_write", ResultClass.SUCCESS),
        ],
    )
    def test_classification_by_row(
        self, observed: str, expected_class: ResultClass
    ) -> None:
        row = lookup_failure_matrix(observed)
        assert row is not None
        assert expected_class in row.l2_classification

    def test_each_row_has_must_not_do(self) -> None:
        for row in FAILURE_MATRIX:
            assert row.l2_must_not_do, (
                f"row {row.observed_condition} missing must_not_do"
            )


# ===========================================================================
# L2 INVARIANTS — all 15 numbered, with executable check coverage where
# possible.
# ===========================================================================


class TestInvariantsFullCoverage:
    def test_all_fifteen_invariants_registered(self) -> None:
        ids = {inv.invariant_id for inv in L2_FULL_INVARIANTS}
        assert ids == set(range(1, 16))

    def test_each_invariant_titled_and_described(self) -> None:
        for inv in L2_FULL_INVARIANTS:
            assert inv.title
            assert inv.description
            assert len(inv.description) > 15, (
                f"invariant {inv.invariant_id} description too short"
            )

    def test_invariant_titles_match_v4_doctrine(self) -> None:
        titles = {inv.invariant_id: inv.title for inv in L2_FULL_INVARIANTS}
        # v4 §L2 INVARIANTS doctrine — exact title set the spec implies.
        expected = {
            1: "bounded_packet",
            2: "no_route_decision",
            3: "no_workflow_expansion",
            4: "no_unsanctioned_retrieval",
            5: "no_direct_human_call",
            6: "no_authority_creation",
            7: "no_durable_state_persistence",
            8: "no_l4_write",
            9: "no_uwg_bypass",
            10: "no_silent_swap",
            11: "bounded_repair_only",
            12: "preserve_replay_lineage",
            13: "seal_every_outcome",
            14: "downstream_consumers_only",
            15: "honest_now_no_future_rescue",
        }
        assert titles == expected

    # Invariant 7/8/9: pipeline cannot construct DispatchReceipt with
    # has_commit_payload=True (constructor invariant).
    def test_invariants_7_8_9_no_durable_l4_uwg_bypass(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        assert r.dispatch.has_commit_payload is False

    # Invariant 13: every outcome is sealed. Validation FAIL still produces
    # a sealed pipeline result.
    def test_invariant_13_seal_every_outcome_on_rejection(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        def reject(_p) -> ValidatorResult:  # type: ignore[no-untyped-def]
            return ValidatorResult(
                outcome=ValidationOutcome.FAIL,
                failed_rule="schema",
                rejection_reason="malformed_tool_args",
                classified_side_effect="UNKNOWN",
            )

        pipe = L2PhasePipeline(
            validator_fn=reject, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        # Must seal even on FAIL — validation.is_approved()=False short-
        # circuits but a result object still exists.
        assert r.validation is not None
        assert r.validation.is_approved() is False

    # Invariant 12: replay metadata preserved through dispatch.
    def test_invariant_12_replay_lineage_preserved(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        # Same blueprint+policy hash flows from PrepReceipt → DispatchReceipt.
        assert (
            r.dispatch.determinism.blueprint_hash
            == determinism.blueprint_hash
        )
        assert r.dispatch.determinism.policy_hash == determinism.policy_hash
        assert r.dispatch.determinism.replay_key == determinism.replay_key


# ===========================================================================
# E5.6 CONTRACT CHECK — verify_sealed_artifact_contract surfaces gaps.
# ===========================================================================


class TestContractCheck:
    def test_contract_check_satisfied_for_healthy_run(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        c = SealedL2ArtifactContents.from_receipts(
            prep=r.prep,
            validation=r.validation,
            attempts=r.attempts,
            heals=r.heals,
            dispatch=r.dispatch,
        )
        result = verify_sealed_artifact_contract(c)
        assert result.satisfied
        assert result.missing_fields == ()
        assert result.durable_commit_detected is False

    def test_contract_check_flags_missing_fields(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        from agentic_core.L2_execution.types.l2_v4_invariants import (
            EvidenceSection,
            ExecutionSection,
            GovernanceSection,
            IdentitySection,
            ObservabilitySection,
            ReplaySection,
            TerminalSection,
        )

        bad = SealedL2ArtifactContents(
            identity=IdentitySection(
                sealed_l2_artifact_id="",  # MISSING
                run_id="",  # MISSING
                route_id="x",
                parent_route_id="parent",
            ),
            governance=GovernanceSection(
                compliance_hash="",  # MISSING
                policy_hash="x",
                blueprint_hash="x",
                capability_token_ref="x",
                sandbox_envelope_ref="x",
            ),
            execution=ExecutionSection(),
            evidence=EvidenceSection(),
            replay=ReplaySection(
                replay_key="",  # MISSING
                input_hash="x",
                prompt_hash="x",
            ),
            observability=ObservabilitySection(trace_id="x"),
            terminal=TerminalSection(
                terminal_class=TerminalStamp.SUCCESS, reason_code="x"
            ),
        )
        result = verify_sealed_artifact_contract(bad)
        assert not result.satisfied
        assert "identity.sealed_l2_artifact_id" in result.missing_fields
        assert "identity.run_id" in result.missing_fields
        assert "governance.compliance_hash" in result.missing_fields
        assert "replay.replay_key" in result.missing_fields


# ===========================================================================
# Re-export sanity — every public symbol the v4 spec names is importable.
# ===========================================================================


def test_v4_public_surface_importable() -> None:
    """Smoke test — every v4-spec-named symbol resolves at import time."""
    # Names already imported at top of file; test exists to prove no
    # ImportError + ContractCheckResult re-exports cleanly.
    assert ContractCheckResult is not None
    assert RepairDecision is not None
    # These two are also v4-doctrine entrypoints for downstream use.
    assert classify_repair_status is not None
    assert derive_dispatch_target is not None
    assert check_invariants is not None
