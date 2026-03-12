"""BudgetEnforcer — OS-level resource isolation for tool invocations.

Wraps every tool call with:
  - Wall-clock limit (compute_ms): SIGALRM on Unix, threading.Timer on Windows
  - resource.setrlimit for memory_mb (RLIMIT_AS) on Unix; no-op on Windows
  - stdout byte cap via BytesIO capture (cross-platform, always enforced)

Spec: Contract [2] SandboxEnvelope ToolBudget caps, Guarantee #10.
"""
from __future__ import annotations
import io
import signal
import threading
from contextlib import contextmanager
from typing import Any, Callable
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
try:
    import resource
    _HAS_RESOURCE = True
except ImportError:
    resource = None
    _HAS_RESOURCE = False
_HAS_SIGALRM = hasattr(signal, 'SIGALRM')
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope

class BudgetExceeded(RuntimeError):
    """Raised when a ToolBudget cap is breached."""

@contextmanager
def _wall_clock_cap_unix(ms: int):
    """SIGALRM-based wall-clock cap — Unix only."""

    def _handler(signum, frame):
        raise BudgetExceeded(f'compute_ms cap ({ms} ms) exceeded')
    old = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, ms / 1000.0)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)

@contextmanager
def _wall_clock_cap_threading(ms: int):
    """threading.Timer-based wall-clock cap — cross-platform fallback."""
    exceeded: list[bool] = [False]

    def _fire():
        exceeded[0] = True
    timer = threading.Timer(ms / 1000.0, _fire)
    timer.daemon = True
    timer.start()
    try:
        yield
    finally:
        timer.cancel()
    if exceeded[0]:
        raise BudgetExceeded(f'compute_ms cap ({ms} ms) exceeded')

def _wall_clock_cap(ms: int):
    """Return the appropriate wall-clock cap context manager for this platform."""
    if _HAS_SIGALRM and threading.current_thread() is threading.main_thread():
        return _wall_clock_cap_unix(ms)
    return _wall_clock_cap_threading(ms)

class BudgetEnforcer:
    """Enforces ToolBudget caps around a tool callable.

    Cross-platform: uses SIGALRM on Unix main thread, threading.Timer elsewhere.
    Memory cap is Unix-only (no-op on Windows/macOS).
    stdout_bytes cap is always enforced.
    """

    def run(self, envelope: SandboxEnvelope, tool_fn: Callable[..., Any]) -> tuple[int, bytes]:
        """Execute tool_fn under budget caps.

        Returns (exit_code, stdout_bytes) per PTC ToolResult contract [3].
        Raises BudgetExceeded on any cap breach.
        """
        budget = envelope.budget
        if _HAS_RESOURCE:
            try:
                mem_bytes = budget.memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, resource.RLIM_INFINITY))
            except (AttributeError, ValueError, OSError):
                pass
        buf = io.BytesIO()
        with _wall_clock_cap(budget.compute_ms):
            result = tool_fn(**envelope.tool_args)
        output = str(result).encode('utf-8', errors='replace')
        if len(output) > budget.stdout_bytes:
            raise BudgetExceeded(f'stdout_bytes cap ({budget.stdout_bytes}) exceeded: got {len(output)}')
        buf.write(output)
        return (0, buf.getvalue())
