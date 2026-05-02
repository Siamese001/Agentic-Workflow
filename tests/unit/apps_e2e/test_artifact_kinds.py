"""Unit tests for ArtifactKind enum (W1.2, plan §6.5)."""
from __future__ import annotations

from tools.certification.apps_e2e.artifact_kinds import (
    SINGLE_OCCURRENCE_KINDS,
    TRACE_SLOT_KINDS,
    ArtifactKind,
)


class TestArtifactKindEnum:
    def test_string_value_equals_member(self):
        assert ArtifactKind.route_contract == "route_contract"
        assert ArtifactKind.l1_plan_contract == "l1_plan_contract"
        assert ArtifactKind.l3_runtime_receipt == "l3_runtime_receipt"
        assert ArtifactKind.l3_bypass_receipt == "l3_bypass_receipt"
        assert ArtifactKind.exit_x3_disposition == "exit_x3_disposition"
        assert ArtifactKind.runtime_exhaust_bundle == "runtime_exhaust_bundle"
        assert ArtifactKind.otel_trace == "otel_trace"
        assert ArtifactKind.runtime_adg_trace == "runtime_adg_trace"

    def test_values_helper_returns_all(self):
        vals = ArtifactKind.values()
        assert "route_contract" in vals
        assert "static_l3_dag_proof" in vals
        # Plan-required kinds are all present.
        for required in (
            "route_contract", "l1_plan_contract",
            "l3_runtime_receipt", "l3_bypass_receipt",
            "exit_x3_disposition", "runtime_exhaust_bundle",
            "otel_trace", "runtime_adg_trace",
            "c0_grounding_receipt", "prompt_assembly_receipt",
            "l2_sealed_artifact", "uwg_durable_write_receipt",
        ):
            assert required in vals


class TestSingleOccurrenceKinds:
    def test_single_occurrence_set_membership(self):
        # Single-occurrence kinds — duplicates fail strict.
        for k in (
            ArtifactKind.route_contract,
            ArtifactKind.l1_plan_contract,
            ArtifactKind.l3_runtime_receipt,
            ArtifactKind.l3_bypass_receipt,
            ArtifactKind.exit_x3_disposition,
            ArtifactKind.runtime_exhaust_bundle,
        ):
            assert k in SINGLE_OCCURRENCE_KINDS

    def test_trace_kinds_NOT_single_occurrence(self):
        # The otel_or_runtime_trace_ref slot accepts either kind. Trace
        # kinds are NOT single-occurrence (a bundle may legitimately have
        # both an OTEL trace and a runtime-ADG trace).
        assert ArtifactKind.otel_trace not in SINGLE_OCCURRENCE_KINDS
        assert ArtifactKind.runtime_adg_trace not in SINGLE_OCCURRENCE_KINDS


class TestTraceSlotKinds:
    def test_only_two_kinds_acceptable_in_trace_slot(self):
        assert TRACE_SLOT_KINDS == frozenset({
            ArtifactKind.otel_trace,
            ArtifactKind.runtime_adg_trace,
        })

    def test_route_contract_not_acceptable_in_trace_slot(self):
        assert ArtifactKind.route_contract not in TRACE_SLOT_KINDS
