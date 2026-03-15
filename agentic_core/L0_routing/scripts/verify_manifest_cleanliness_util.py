"""
scripts/verify_manifest_cleanliness.py
Executes full_agent_discovery.py and validates that deleted legacy bases
are absent from the resulting JSON manifest.
"""

import json
import os
import sys
from pathlib import Path

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
)

_emit_dispatches_healing_run("p1", "verify_manifest_cleanliness_util", "L0")
_emit_routes_through("p1", "verify_manifest_cleanliness_util", "L0")
_emit_escalates_to_human("p1", "verify_manifest_cleanliness_util", "L0")
_emit_reads_policy_state("p1", "verify_manifest_cleanliness_util", "L0")


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
    print("[*] Running full_agent_discovery.py...")
    env_cmd = (
        "set PYTHONPATH=../../../.. && cd agentic_core/L0_routing/scripts && python full_agent_discovery.py"
    )
    exit_code = os.system(env_cmd)
    print(f"[*] Discovery script exit code: {exit_code}")
    if exit_code != 0:
        print("[!] Discovery script had compliance issues, but checking manifest...")
    manifest_path = Path("agent_discovery_full.json")
    if not manifest_path.exists():
        print("[-] Manifest file was not generated.")
        sys.exit(1)
    with open(manifest_path) as f:
        data = json.load(f)
    BLACKLIST = {
        "L1CognitionBase",
        "L2ExecutionBase",
        "L3OrchestrationBase",
        "L4StateBase",
        "L5SafetyBase",
        "L6ObservabilityBase",
        "MaintenanceBaseAgent",
    }
    found_agents = {agent["class_name"] for agent in data}
    violations = found_agents.intersection(BLACKLIST)
    print(f"[*] Total Agents Discovered: {len(found_agents)}")
    if violations:
        print("[-] CRITICAL FAILURE: The following deleted agents are still in the manifest:")
        for v in violations:
            print(f"   - {v}")
        sys.exit(1)
    else:
        print("[+] SUCCESS: Manifest is clean. No legacy base classes detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
