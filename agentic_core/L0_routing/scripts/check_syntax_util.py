"""Quick syntax check to identify the 3 remaining errors."""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "check_syntax_util", "L0")
_emit_routes_through("p1", "check_syntax_util", "L0")
_emit_escalates_to_human("p1", "check_syntax_util", "L0")
_emit_reads_policy_state("p1", "check_syntax_util", "L0")

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def main():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    project_root = Path(__file__).parent.parent
    result = invoke_code_validator(action="validate", project_root=project_root)
    if result.get("success"):
        print(f"Total errors: {result.get('total_violations', 0)}")
        print()
        for v in result.get("violations", []):
            print(f"{v['file_path']}:{v['line_number']}:{v['column']} - {v['error_message']}")
    else:
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()
