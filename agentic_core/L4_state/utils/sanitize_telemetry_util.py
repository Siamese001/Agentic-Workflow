"""
Telemetry Sanitizer - Anti-Observer Effect Protection.

Prevents token overload by intelligently pruning large tool outputs while
preserving critical information like error tracebacks.

COGNITIVE HARDENING (Feb 2026):
- Landmine #4 Prevention: Token Overload
- Preserves head/tail context for debugging
- Special handling for Python tracebacks to preserve actual errors
"""

from typing import Final

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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sanitize_telemetry_util")
emit_determinism_digest("p0", "sanitize_telemetry_util")

_emit_dispatches_healing_run("p1", "sanitize_telemetry_util", "L4")
_emit_routes_through("p1", "sanitize_telemetry_util", "L4")
_emit_escalates_to_human("p1", "sanitize_telemetry_util", "L4")
_emit_reads_policy_state("p1", "sanitize_telemetry_util", "L4")

DEFAULT_MAX_CHARS: Final[int] = 2000
HEAD_SIZE: Final[int] = 500
TAIL_SIZE: Final[int] = 500
TRACEBACK_PATTERNS: Final[tuple[str, ...]] = (
    "Traceback (most recent call last):",
    "Error:",
    "Exception:",
    "raise ",
)


def _is_traceback(output: str) -> bool:
    """Detect if output contains a Python traceback."""
    return any(pattern in output for pattern in TRACEBACK_PATTERNS)


# guardian: allow-magic-config
def _extract_traceback_tail(output: str, max_tail: int = 1000) -> str:
    """
    Extract the meaningful tail of a traceback.

    Python tracebacks have the actual error at the END, so we need to
    preserve more of the tail when dealing with tracebacks.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_extract_traceback_tail", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_extract_traceback_tail", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "_extract_traceback_tail")
    lines = output.splitlines()
    traceback_start = -1
    for i, line in enumerate(lines):
        if "Traceback (most recent call last):" in line:
            traceback_start = i
    if traceback_start >= 0:
        traceback_section = "\n".join(lines[traceback_start:])
        if len(traceback_section) <= max_tail:
            return traceback_section
        return traceback_section[-max_tail:]
    return output[-max_tail:] if len(output) > max_tail else output


def sanitize_tool_output(
    output: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    head_size: int | None = None,
    tail_size: int | None = None,
) -> str:
    """
    Sanitize tool output to prevent token overload.

    Args:
        output: The raw tool output string.
        max_chars: Maximum allowed characters before pruning.
        head_size: Number of characters to preserve from the start (default: 25% of max_chars).
        tail_size: Number of characters to preserve from the end (default: 25% of max_chars).

    Returns:
        Sanitized output string, pruned if necessary.

    Logic:
        1. If output is shorter than max_chars, return as-is.
        2. If longer, return Head + pruning marker + Tail.
        3. If output is a Python traceback, preserve the actual error (at the end).
    """
    if not output:
        return output
    output_len = len(output)
    if output_len <= max_chars:
        return output
    if head_size is None:
        head_size = min(HEAD_SIZE, max_chars // 4)
    if tail_size is None:
        tail_size = min(TAIL_SIZE, max_chars // 4)
    if head_size + tail_size >= output_len:
        return output
    pruned_chars = output_len - head_size - tail_size
    if _is_traceback(output):
        traceback_tail_size = min(1000, output_len - head_size)
        traceback_tail = _extract_traceback_tail(output, traceback_tail_size)
        head = output[:head_size]
        pruned_chars = output_len - head_size - len(traceback_tail)
        return f"{head}\n\n...[Pruned {pruned_chars} chars - Traceback preserved]...\n\n{traceback_tail}"
    head = output[:head_size]
    tail = output[-tail_size:]
    return f"{head}\n\n...[Pruned {pruned_chars} chars]...\n\n{tail}"


__all__ = ["sanitize_tool_output"]
