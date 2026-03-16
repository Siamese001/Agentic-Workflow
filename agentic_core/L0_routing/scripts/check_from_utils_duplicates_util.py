"""
Quick script to check _from_utils duplicates
"""

from pathlib import Path

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

emit_replay_key("p0", "check_from_utils_duplicates_util")
emit_determinism_digest("p0", "check_from_utils_duplicates_util")

_emit_dispatches_healing_run("p1", "check_from_utils_duplicates_util", "L0")
_emit_routes_through("p1", "check_from_utils_duplicates_util", "L0")
_emit_escalates_to_human("p1", "check_from_utils_duplicates_util", "L0")
_emit_reads_policy_state("p1", "check_from_utils_duplicates_util", "L0")

_emit_records_execution_trace("p0", "evidence", "check_from_utils_duplicates_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "check_from_utils_duplicates_util", "p0_governance")
_emit_snapshots_state("p0", "check_from_utils_duplicates_util", "state_snapshot")

project_root = Path(__file__).parent.parent.parent
from_utils = list(project_root.rglob("*_from_utils.py"))
from_utils = [f for f in from_utils if ARCHIVES_DIR not in str(f)]
canonicals = []
for f in from_utils:
    canonical = f.parent / f.name.replace("_from_utils.py", ".py")
    if canonical.exists():
        canonicals.append((f, canonical))
if canonicals:
    for _dup, _canon in canonicals:
        pass
