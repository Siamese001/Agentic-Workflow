"""Infrastructure dependency error types for fail-closed enforcement.

No component may silently degrade when a required infrastructure dependency
(Redis, vector store, FAISS, RAG) is unavailable.  Raise
InfrastructureDependencyError instead of falling back to a local or
in-process substitute.
"""

from __future__ import annotations

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

emit_replay_key("p0", "infra_error_types")
emit_determinism_digest("p0", "infra_error_types")

_emit_dispatches_healing_run("p1", "infra_error_types", "L2")
_emit_routes_through("p1", "infra_error_types", "L2")
_emit_escalates_to_human("p1", "infra_error_types", "L2")
_emit_reads_policy_state("p1", "infra_error_types", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "infra_error_types")
_emit_applies_guardrail("p0", "infra_error_types", "p0_governance")
_emit_snapshots_state("p0", "infra_error_types", "state_snapshot")


class InfrastructureDependencyError(RuntimeError):
    """Raised when a mandatory infrastructure dependency is unavailable.

    This error signals a hard failure — the system cannot continue safely
    without the required service.  Callers must not catch this error to
    implement a silent fallback; they should propagate it to the process
    boundary so the deployment is restarted or the operator is alerted.
    """
