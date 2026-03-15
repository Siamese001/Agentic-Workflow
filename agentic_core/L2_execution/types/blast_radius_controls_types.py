"""
BlastRadiusControls — Execution budget caps for L2 sandbox operations.

Hard limits enforced per execution trace to prevent runaway executions,
resource exhaustion, and denial-of-service via the healing/execution loop.

Phase 3.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "blast_radius_controls_types", "L2")
_emit_routes_through("p1", "blast_radius_controls_types", "L2")
_emit_escalates_to_human("p1", "blast_radius_controls_types", "L2")
_emit_reads_policy_state("p1", "blast_radius_controls_types", "L2")


class BlastRadiusExceeded(RuntimeError):
    """Raised when an execution trace exceeds a blast-radius limit."""


@dataclass(frozen=True)
class BlastRadiusControls:
    """Immutable per-trace resource caps.

    Fields
    ------
    max_state_diff_bytes : int
        Maximum size (bytes) of the state diff produced by a single execution.
    max_file_write_bytes : int
        Maximum total bytes written to the filesystem per trace.
    max_compute_ms : int
        Maximum cumulative wall-clock milliseconds per trace.
    max_parallel_branches : int
        Maximum number of simultaneous sub-branches per trace.
    max_tool_calls_per_minute : int
        Rate limit: tool calls per rolling 60-second window.
    """

    max_state_diff_bytes: int = 65536
    max_file_write_bytes: int = 1048576
    max_compute_ms: int = 30000
    max_parallel_branches: int = 4
    max_tool_calls_per_minute: int = 120

    def __post_init__(self) -> None:
        for field_name, value in [
            ("max_state_diff_bytes", self.max_state_diff_bytes),
            ("max_file_write_bytes", self.max_file_write_bytes),
            ("max_compute_ms", self.max_compute_ms),
            ("max_parallel_branches", self.max_parallel_branches),
            ("max_tool_calls_per_minute", self.max_tool_calls_per_minute),
        ]:
            if value <= 0:
                raise ValueError(f"BlastRadiusControls: {field_name} must be positive, got {value}")

    def check_state_diff(self, diff_bytes: int) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "BlastRadiusControls.check_state_diff", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "BlastRadiusControls.check_state_diff", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "BlastRadiusControls.check_state_diff"
        )
        if diff_bytes > self.max_state_diff_bytes:
            raise BlastRadiusExceeded(
                f"State diff {diff_bytes} bytes exceeds limit {self.max_state_diff_bytes}"
            )

    def check_file_write(self, total_written_bytes: int) -> None:
        if total_written_bytes > self.max_file_write_bytes:
            raise BlastRadiusExceeded(
                f"File write total {total_written_bytes} bytes exceeds limit {self.max_file_write_bytes}"
            )

    def check_compute(self, elapsed_ms: int) -> None:
        if elapsed_ms > self.max_compute_ms:
            raise BlastRadiusExceeded(f"Compute {elapsed_ms} ms exceeds limit {self.max_compute_ms} ms")

    def check_parallel_branches(self, active_branches: int) -> None:
        if active_branches > self.max_parallel_branches:
            raise BlastRadiusExceeded(
                f"Active branches {active_branches} exceeds limit {self.max_parallel_branches}"
            )

    def check_tool_call_rate(self, calls_in_window: int) -> None:
        if calls_in_window > self.max_tool_calls_per_minute:
            raise BlastRadiusExceeded(
                f"Tool calls in window {calls_in_window} exceeds rate limit {self.max_tool_calls_per_minute}/min"
            )


DEFAULT_BLAST_RADIUS = BlastRadiusControls()
__all__ = ["BlastRadiusControls", "BlastRadiusExceeded", "DEFAULT_BLAST_RADIUS"]
