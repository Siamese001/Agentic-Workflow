"""
BlastRadiusControls — Execution budget caps for L2 sandbox operations.

Hard limits enforced per execution trace to prevent runaway executions,
resource exhaustion, and denial-of-service via the healing/execution loop.

Phase 3.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

from dataclasses import dataclass


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

    max_state_diff_bytes: int = 65_536  # 64 KiB
    max_file_write_bytes: int = 1_048_576  # 1 MiB
    max_compute_ms: int = 30_000  # 30 s
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

    # ------------------------------------------------------------------
    # Enforcement helpers
    # ------------------------------------------------------------------

    def check_state_diff(self, diff_bytes: int) -> None:
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
                f"Tool calls in window {calls_in_window} exceeds rate limit "
                f"{self.max_tool_calls_per_minute}/min"
            )


# Canonical default — shared across L2 execution unless overridden per-trace.
DEFAULT_BLAST_RADIUS = BlastRadiusControls()

__all__ = [
    "BlastRadiusControls",
    "BlastRadiusExceeded",
    "DEFAULT_BLAST_RADIUS",
]
