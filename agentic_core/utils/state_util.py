"""
State utilities for common operations across the codebase.
"""

from agentic_core.mixins.safety_mixin import StateAnalysisMixin
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "state_util")
_emit_applies_guardrail("p0", "state_util", "p0_governance")
_emit_reads_policy_state("p0", "state_util", "policy_binding")
_emit_snapshots_state("p0", "state_util", "state_snapshot")
emit_replay_key("p0", "state_util")
emit_determinism_digest("p0", "state_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def check_past_failures(task: str) -> str:
    """Check telemetry for past failures on similar tasks.

    Args:
        task: Task description to check

    Returns:
        Recommendation string based on analysis
    """
    try:
        result = StateAnalysisMixin._check_past_failures([])
        return result["recommendation"]
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logging.getLogger(__name__).warning(f"State analysis error: {e}")
        return "Unable to check past failures"
    except (OSError, RuntimeError, MemoryError) as e:
        logging.getLogger(__name__).error(f"Critical state analysis error: {e}")
        return "Unable to check past failures"
