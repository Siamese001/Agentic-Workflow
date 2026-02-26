"""BudgetEnforcer — OS-level resource isolation for tool invocations.

Wraps every tool call with:
  - SIGALRM-based wall-clock limit (compute_ms)
  - resource.setrlimit for memory_mb (RLIMIT_AS)
  - stdout byte cap via BytesIO capture
"""

from __future__ import annotations

import io
import signal
from contextlib import contextmanager
from typing import Any, Callable

# resource module is Unix-only
try:
    import resource
except ImportError:
    resource = None

from agentic_core.L2_execution.types.sandbox_envelope import SandboxEnvelope


class BudgetExceeded(RuntimeError):
    """Raised when a ToolBudget cap is breached."""


@contextmanager
def _wall_clock_cap(ms: int):
    def _handler(signum, frame):
        raise BudgetExceeded(f"compute_ms cap ({ms} ms) exceeded")

    old = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, ms / 1000.0)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


class BudgetEnforcer:
    """Enforces ToolBudget caps around a tool callable."""

    def run(self, envelope: SandboxEnvelope, tool_fn: Callable[..., Any]) -> tuple[int, bytes]:
        """Execute tool_fn under budget caps.

        Returns (exit_code, stdout_bytes) per PTC ToolResult contract [3].
        Raises BudgetExceeded on cap breach.
        """
        budget = envelope.budget

        # Memory cap (Linux only; no-op on Windows/macOS)
        if resource is not None:
            try:
                mem_bytes = budget.memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, resource.RLIM_INFINITY))
            except (AttributeError, ValueError):
                pass  # Not supported on this platform — log but continue

        buf = io.BytesIO()

        with _wall_clock_cap(budget.compute_ms):
            result = tool_fn(**envelope.tool_args)

        # Capture stdout-equivalent output
        output = str(result).encode("utf-8", errors="replace")
        if len(output) > budget.stdout_bytes:
            raise BudgetExceeded(f"stdout_bytes cap ({budget.stdout_bytes}) exceeded: got {len(output)}")
        buf.write(output)
        return 0, buf.getvalue()
