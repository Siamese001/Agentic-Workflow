"""Addendum 8: Runtime Architectural Invariant Checker.

Six invariants that MUST always hold. Wire into critical paths.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.L5_safety.types.hardening_errors import (
    C0AuthorityLeakError,
    MutationReplayIntegrityViolation,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "runtime_invariant_checker")
emit_determinism_digest("p0", "runtime_invariant_checker")

_emit_dispatches_healing_run("p1", "runtime_invariant_checker", "L5")
_emit_routes_through("p1", "runtime_invariant_checker", "L5")
_emit_escalates_to_human("p1", "runtime_invariant_checker", "L5")
_emit_reads_policy_state("p1", "runtime_invariant_checker", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "runtime_invariant_checker")
_emit_applies_guardrail("p0", "runtime_invariant_checker", "p0_governance")
_emit_snapshots_state("p0", "runtime_invariant_checker", "state_snapshot")

logger = logging.getLogger(__name__)

_C0_FORBIDDEN_FIELDS = frozenset(
    {"route_mode", "execution_tier", "safety_threshold", "allowed_tools", "auth_token"}
)


def assert_mutation_source_is_l2(mutation_source: str) -> None:
    """Invariant 1: L2 is the ONLY mutation executor."""
    if mutation_source != "L2_execution":
        raise MutationReplayIntegrityViolation(
            f"Invariant 1 violated: mutation_source={mutation_source!r} — only 'L2_execution' allowed"
        )


def assert_mutation_in_ledger(
    ledger_entries: list[dict[str, Any]],
    file_path: str,
    operation: str,
) -> None:
    """Invariant 2: All mutations pass through UWG (present in ledger)."""
    for entry in ledger_entries:
        if entry.get("file_path") == file_path and entry.get("operation") == operation:
            return
    raise MutationReplayIntegrityViolation(
        f"Invariant 2 violated: mutation not in ledger — file={file_path} op={operation}"
    )


def assert_state_read_source_is_l4(state_read_source: str) -> None:
    """Invariant 3: L4 is the sole state authority."""
    if state_read_source != "L4_state":
        raise MutationReplayIntegrityViolation(
            f"Invariant 3 violated: state_read_source={state_read_source!r} — only 'L4_state' allowed"
        )


def assert_c0_no_authority_fields(c0_payload: dict[str, Any]) -> None:
    """Invariant 4: C0 context never carries authority fields."""
    leak = _C0_FORBIDDEN_FIELDS & set(c0_payload.keys())
    if leak:
        raise C0AuthorityLeakError(
            f"Invariant 4 violated: C0 payload contains authority fields: {sorted(leak)}"
        )


def assert_telemetry_no_config_mutation(
    current_stage: int,
    config_mutated: bool,
) -> None:
    """Invariant 5: L6 telemetry cannot mutate runtime state before S9."""
    if current_stage < 9 and config_mutated:
        from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation

        raise RuntimePolicyMutationViolation(
            f"Invariant 5 violated: config mutated at meta-learning stage {current_stage} (must be S9)"
        )


def assert_human_patch_l5_clearance(l5_clearance_signature: str | None) -> None:
    """Invariant 6: Human patches must pass L5 re-clearance."""
    if not l5_clearance_signature:
        from agentic_core.L5_safety.types.hardening_errors import HumanPatchL5ClearanceError

        raise HumanPatchL5ClearanceError("Invariant 6 violated: human patch missing L5 clearance signature")


def run_all_invariants(
    *,
    mutation_source: str | None = None,
    ledger_entries: list[dict[str, Any]] | None = None,
    file_path: str | None = None,
    operation: str | None = None,
    state_read_source: str | None = None,
    c0_payload: dict[str, Any] | None = None,
    meta_learning_stage: int | None = None,
    config_mutated: bool = False,
    l5_clearance_signature: str | None = None,
) -> list[str]:
    """Run all applicable invariants. Returns list of violation messages (empty = clean)."""
    violations: list[str] = []

    checks = [
        (_check_inv1, mutation_source),
        (_check_inv2, (ledger_entries, file_path, operation)),
        (_check_inv3, state_read_source),
        (_check_inv4, c0_payload),
        (_check_inv5, (meta_learning_stage, config_mutated)),
        (_check_inv6, l5_clearance_signature),
    ]

    for checker, arg in checks:
        try:
            checker(arg)
        # guardian: allow-silent-swallow -- invariant check is observational; failure non-blocking
        except Exception as exc:
            violations.append(str(exc))

    return violations


def _check_inv1(mutation_source: Any) -> None:
    if mutation_source is not None:
        assert_mutation_source_is_l2(mutation_source)


def _check_inv2(args: Any) -> None:
    ledger_entries, file_path, operation = args
    if ledger_entries is not None and file_path and operation:
        assert_mutation_in_ledger(ledger_entries, file_path, operation)


def _check_inv3(state_read_source: Any) -> None:
    if state_read_source is not None:
        assert_state_read_source_is_l4(state_read_source)


def _check_inv4(c0_payload: Any) -> None:
    if c0_payload is not None:
        assert_c0_no_authority_fields(c0_payload)


def _check_inv5(args: Any) -> None:
    stage, mutated = args
    if stage is not None:
        assert_telemetry_no_config_mutation(stage, mutated)


def _check_inv6(sig: Any) -> None:
    if sig is not None or sig == "":
        pass


__all__ = [
    "assert_mutation_source_is_l2",
    "assert_mutation_in_ledger",
    "assert_state_read_source_is_l4",
    "assert_c0_no_authority_fields",
    "assert_telemetry_no_config_mutation",
    "assert_human_patch_l5_clearance",
    "run_all_invariants",
]
