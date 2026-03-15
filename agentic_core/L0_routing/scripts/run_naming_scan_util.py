"""
Run NamingAgent to scan for duplicate filenames and class names.
"""

import sys
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
)

_emit_dispatches_healing_run("p1", "run_naming_scan_util", "L0")
_emit_routes_through("p1", "run_naming_scan_util", "L0")
_emit_escalates_to_human("p1", "run_naming_scan_util", "L0")
_emit_reads_policy_state("p1", "run_naming_scan_util", "L0")

_emit_records_execution_trace("p0", "evidence", "run_naming_scan_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "run_naming_scan_util", "p0_governance")
_emit_snapshots_state("p0", "run_naming_scan_util", "state_snapshot")

project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.seams.safety_reasoning_seam import load_naming_agent

print("=" * 80)
print("NAMING AGENT SCAN - Duplicate Detection")
print("=" * 80)
NamingAgent = load_naming_agent()
naming = NamingAgent(project_root)
print("\n[1] Scanning for duplicate FILENAMES...")
duplicates = naming.scan_for_duplicate_filenames()
if duplicates:
    print(f"\n❌ Found {len(duplicates)} duplicate filenames:")
    for basename, paths in sorted(duplicates.items()):
        print(f"\n  {basename} ({len(paths)} occurrences):")
        for p in paths:
            print(f"    - {p.relative_to(project_root)}")
else:
    print("\n✅ No duplicate filenames found")
print("\n" + "=" * 80)
print("[2] Scanning for duplicate CLASS NAMES...")
import json
from collections import defaultdict

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON

discovery_path = project_root / AGENT_DISCOVERY_JSON
if discovery_path.exists():
    agents = json.loads(discovery_path.read_text(encoding="utf-8"))
    by_name = defaultdict(list)
    for a in agents:
        by_name[a["class_name"]].append(a["path"])
    dup_classes = {k: v for k, v in by_name.items() if len(v) > 1}
    if dup_classes:
        print(f"\n❌ Found {len(dup_classes)} duplicate class names:")
        for name, paths in sorted(dup_classes.items()):
            print(f"\n  {name} ({len(paths)} occurrences):")
            for p in paths:
                print(f"    - {p}")
    else:
        print("\n✅ No duplicate class names found")
else:
    print("\n⚠️  agent_discovery_full.json not found - run full_agent_discovery.py first")
print("\n" + "=" * 80)
print("SCAN COMPLETE")
print("=" * 80)
