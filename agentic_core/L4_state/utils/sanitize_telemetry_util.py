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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
DEFAULT_MAX_CHARS: Final[int] = 2000
HEAD_SIZE: Final[int] = 500
TAIL_SIZE: Final[int] = 500
TRACEBACK_PATTERNS: Final[tuple[str, ...]] = ('Traceback (most recent call last):', 'Error:', 'Exception:', 'raise ')

def _is_traceback(output: str) -> bool:
    """Detect if output contains a Python traceback."""
    return any((pattern in output for pattern in TRACEBACK_PATTERNS))

# guardian: allow-magic-config
def _extract_traceback_tail(output: str, max_tail: int=1000) -> str:
    """
    Extract the meaningful tail of a traceback.

    Python tracebacks have the actual error at the END, so we need to
    preserve more of the tail when dealing with tracebacks.
    """
    lines = output.splitlines()
    traceback_start = -1
    for i, line in enumerate(lines):
        if 'Traceback (most recent call last):' in line:
            traceback_start = i
    if traceback_start >= 0:
        traceback_section = '\n'.join(lines[traceback_start:])
        if len(traceback_section) <= max_tail:
            return traceback_section
        return traceback_section[-max_tail:]
    return output[-max_tail:] if len(output) > max_tail else output

def sanitize_tool_output(output: str, max_chars: int=DEFAULT_MAX_CHARS, head_size: int | None=None, tail_size: int | None=None) -> str:
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
        return f'{head}\n\n...[Pruned {pruned_chars} chars - Traceback preserved]...\n\n{traceback_tail}'
    head = output[:head_size]
    tail = output[-tail_size:]
    return f'{head}\n\n...[Pruned {pruned_chars} chars]...\n\n{tail}'
__all__ = ['sanitize_tool_output']
