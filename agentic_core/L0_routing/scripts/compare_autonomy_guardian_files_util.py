"""Compare the two AutonomyGuardianAgent.py files to understand their differences."""

import difflib
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

_emit_dispatches_healing_run("p1", "compare_autonomy_guardian_files_util", "L0")
_emit_routes_through("p1", "compare_autonomy_guardian_files_util", "L0")
_emit_escalates_to_human("p1", "compare_autonomy_guardian_files_util", "L0")
_emit_reads_policy_state("p1", "compare_autonomy_guardian_files_util", "L0")

_emit_records_execution_trace("p0", "evidence", "compare_autonomy_guardian_files_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "compare_autonomy_guardian_files_util", "p0_governance")
_emit_snapshots_state("p0", "compare_autonomy_guardian_files_util", "state_snapshot")

file1 = Path("agentic_core/L5_safety/validators/AutonomyGuardianAgent.py")
file2 = Path("agentic_core/config/blueprint_sovereign/AutonomyGuardianAgent.py")
content1 = file1.read_text(encoding="utf-8").splitlines()
content2 = file2.read_text(encoding="utf-8").splitlines()
print(f"L5 Validators version: {len(content1)} lines")
print(f"Blueprint version: {len(content2)} lines")
print(f"Difference: {len(content1) - len(content2)} lines")
print()
diff = list(
    difflib.unified_diff(content2, content1, fromfile=str(file2), tofile=str(file1), lineterm="", n=3)
)
if diff:
    print(f"Found {len(diff)} diff lines")
    print("\nFirst 100 lines of diff:")
    for line in diff[:100]:
        print(line)
else:
    print("Files are identical")
import re

classes1 = re.findall("^class\\s+(\\w+)", content1[0] if content1 else "", re.MULTILINE)
classes2 = re.findall("^class\\s+(\\w+)", content2[0] if content2 else "", re.MULTILINE)
print(f"\n\nClasses in L5 version: {(classes1[:5] if classes1 else 'None found')}")
print(f"Classes in Blueprint version: {(classes2[:5] if classes2 else 'None found')}")
print("\n\n=== L5 VERSION PURPOSE ===")
for i, line in enumerate(content1[:20]):
    if '"""' in line or "'''" in line:
        print("\n".join(content1[i : min(i + 10, len(content1))]))
        break
print("\n\n=== BLUEPRINT VERSION PURPOSE ===")
for i, line in enumerate(content2[:20]):
    if '"""' in line or "'''" in line:
        print("\n".join(content2[i : min(i + 10, len(content2))]))
        break
