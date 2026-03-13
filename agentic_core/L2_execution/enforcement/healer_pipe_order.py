"""G-2-3 — Healer 10-Step Pipeline Order Enforcement.

Single runtime gate that validates the complete observed step sequence
against the canonical HEALER_PIPE_ORDER. Fail-closed on any mismatch:
reordering, missing steps, extra steps, or duplication.

Deterministic PermissionError includes: expected_step, observed_step,
step_index, trace_id.
"""

from __future__ import annotations

import logging
from typing import Sequence

logger = logging.getLogger(__name__)
_REQUIRED_STEP_COUNT = 10


def enforce_healer_pipe_order(
    expected_steps: tuple[str, ...], observed_steps: Sequence[str], trace_id: str | None = None
) -> None:
    """Validate that observed_steps exactly matches expected_steps.

    This is the SINGLE runtime gate for G-2-3 enforcement.

    Args:
        expected_steps: The canonical 10-step tuple (HEALER_PIPE_ORDER).
        observed_steps: Steps actually executed, in execution order.
        trace_id: Optional trace identifier for diagnostics.

    Raises:
        AssertionError: If expected_steps length != 10.
        PermissionError: If observed_steps does not exactly match expected_steps
            (wrong length, wrong order, missing/extra/duplicated steps).
    """
    assert len(expected_steps) == _REQUIRED_STEP_COUNT, (
        f"enforce_healer_pipe_order: expected_steps must have exactly {_REQUIRED_STEP_COUNT} entries, got {len(expected_steps)}"
    )
    trace_tag = f"trace_id={trace_id}" if trace_id else "trace_id=NONE"
    if len(observed_steps) != len(expected_steps):
        if len(observed_steps) < len(expected_steps):
            missing_idx = len(observed_steps)
            msg = f"HEALER_PIPE_ORDER_VIOLATION:MISSING_STEP|expected_step={expected_steps[missing_idx]}|observed_step=<absent>|step_index={missing_idx}|{trace_tag}|expected_count={len(expected_steps)}|observed_count={len(observed_steps)}"
        else:
            extra_idx = len(expected_steps)
            msg = f"HEALER_PIPE_ORDER_VIOLATION:EXTRA_STEP|expected_step=<none>|observed_step={observed_steps[extra_idx]}|step_index={extra_idx}|{trace_tag}|expected_count={len(expected_steps)}|observed_count={len(observed_steps)}"
        logger.error("HEALER_PIPE_ORDER DENY: %s", msg)
        raise PermissionError(msg)
    for idx, (exp, obs) in enumerate(zip(expected_steps, observed_steps)):
        if exp != obs:
            msg = f"HEALER_PIPE_ORDER_VIOLATION:WRONG_STEP|expected_step={exp}|observed_step={obs}|step_index={idx}|{trace_tag}"
            logger.error("HEALER_PIPE_ORDER DENY: %s", msg)
            raise PermissionError(msg)
    logger.info("HEALER_PIPE_ORDER PASS: all %d steps verified (%s)", len(expected_steps), trace_tag)


__all__ = ["enforce_healer_pipe_order"]
