"""
Quick script to check _from_utils duplicates
"""

from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

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
