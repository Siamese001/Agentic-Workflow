"""
Data-only module. No business logic, no healing, no orchestration. SSOT ordering.
Pins the canonical phase ordering extracted from ``execute_ssot._legacy_main``
to prevent accidental monolith reconstitution and to anchor future healer
Phase ordering (legacy mirror):
    1. pre_audit
    2. discovery
    3. reconciliation
    4. alignment
    5. arch_validation
    6. healing
    7. certification
"""

from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "l2_phase_spec", "L2")
_emit_routes_through("p1", "l2_phase_spec", "L2")
_emit_escalates_to_human("p1", "l2_phase_spec", "L2")
_emit_reads_policy_state("p1", "l2_phase_spec", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "l2_phase_spec")
_emit_applies_guardrail("p0", "l2_phase_spec", "p0_governance")
_emit_snapshots_state("p0", "l2_phase_spec", "state_snapshot")


@dataclass(frozen=True, slots=True)
class PhaseSpec:
    """Immutable specification for a single execution phase.

    Attributes:
        name: Canonical phase name (unique within a plan).
        guardian_ids: Guardian IDs to run before this phase (empty for now).
        healer_ids: Healer IDs to invoke during this phase (empty for now).
        rerun_guardians: Guardian IDs to re-run after healing (empty for now).
        approval_required: Whether human approval is needed (False for now).
        inputs_from_prior: Phase names whose outputs feed this phase (empty for now).
    """

    name: str
    guardian_ids: tuple[str, ...] = ()
    healer_ids: tuple[str, ...] = ()
    rerun_guardians: tuple[str, ...] = ()
    approval_required: bool = False
    inputs_from_prior: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class L2ExecutionPlan:
    """Immutable, ordered sequence of PhaseSpecs defining an execution plan."""

    phases: tuple[PhaseSpec, ...]


LEGACY_MIRROR_PLAN: L2ExecutionPlan = L2ExecutionPlan(
    phases=(
        PhaseSpec(name="pre_audit"),
        PhaseSpec(name="discovery"),
        PhaseSpec(name="reconciliation"),
        PhaseSpec(name="alignment"),
        PhaseSpec(name="arch_validation"),
        PhaseSpec(name="healing"),
        PhaseSpec(name="certification"),
    )
)
__all__ = ["L2ExecutionPlan", "LEGACY_MIRROR_PLAN", "PhaseSpec"]
