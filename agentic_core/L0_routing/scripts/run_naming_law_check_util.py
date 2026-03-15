"""Run NamingAgent to detect agent file naming violations."""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "run_naming_law_check_util", "L0")
_emit_routes_through("p1", "run_naming_law_check_util", "L0")
_emit_escalates_to_human("p1", "run_naming_law_check_util", "L0")
_emit_reads_policy_state("p1", "run_naming_law_check_util", "L0")

PROJECT_ROOT = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.seams.safety_reasoning_seam import load_naming_agent
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
    NamingAgent = load_naming_agent()
    agent = NamingAgent(PROJECT_ROOT)
    scan_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
    violations = []
    compliant = 0
    for dir_name in scan_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if not dir_path.exists():
            continue
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(dir_path):
            if "__pycache__" in str(py_file) or "__init__.py" == py_file.name:
                continue
            is_valid, message = agent.validate_file_naming(py_file)
            if not is_valid and "AGENT FILE NAMING VIOLATION" in message:
                rel_path = py_file.relative_to(PROJECT_ROOT)
                violations.append((str(rel_path), message))
            elif is_valid:
                compliant += 1
    print("=" * 70)
    print("AGENT FILE NAMING LAW CHECK")
    print("=" * 70)
    print(f"\nCompliant files: {compliant}")
    print(f"Violations (agent classes in non-*Agent.py files): {len(violations)}")
    print("=" * 70)
    if violations:
        print("\nVIOLATIONS:\n")
        for path, msg in sorted(violations)[:50]:
            print(f"  {path}")
            if "Rename file to" in msg:
                suggested = msg.split("Rename file to '")[1].split("'")[0]
                print(f"    → Rename to: {suggested}")
            print()
        if len(violations) > 50:
            print(f"  ... and {len(violations) - 50} more violations")
    print("=" * 70)
    print(f"TOTAL: {len(violations)} files need renaming to *Agent.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
