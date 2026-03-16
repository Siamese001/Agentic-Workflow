"""Quick check of scanner violation counts for test code."""

import ast
import tempfile
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L5_safety.static_checks.system_invariant_scanner import (
    SystemInvariantScanner,
    scan_repository_for_bypasses,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "check_scanner_violations")
_emit_applies_guardrail("p0", "check_scanner_violations", "p0_governance")
_emit_reads_policy_state("p0", "check_scanner_violations", "policy_binding")
_emit_snapshots_state("p0", "check_scanner_violations", "state_snapshot")
emit_replay_key("p0", "check_scanner_violations")
emit_determinism_digest("p0", "check_scanner_violations")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# Test 1: gateway bypass code
code = (
    "import os\n"
    "def f():\n"
    '    open("t.txt","w")\n'
    '    os.remove("x")\n'
    '    open("a.txt","w")  # guardian: allow-direct-write\n'
)
with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
    tmp.write(code)
    p = Path(tmp.name)

s = SystemInvariantScanner(p)
s.visit(ast.parse(code))
print(f"Gateway bypass violations: {len(s.violations)}")
for v in s.violations:
    print(f"  {v.rule_id}: {v.snippet}")
p.unlink()

# Test 2: scan L2_execution bucket
root = Path(__file__).resolve().parents[2]
bucket = root / AGENTIC_CORE_DIR / "L2_execution"
print(f"\nL2_execution bucket exists: {bucket.exists()}")
py_files = [f for f in bucket.rglob("*.py") if "__pycache__" not in f.parts]
print(f"L2_execution .py files: {len(py_files)}")
violations = scan_repository_for_bypasses(bucket)
prefix = str(bucket)
filtered = [v for v in violations if str(Path(v.file_path).resolve()).startswith(prefix)]
print(f"L2_execution violations: {len(filtered)}")
if filtered:
    for v in filtered[:5]:
        print(f"  {v.file_path}:{v.line} [{v.rule_id}]")
