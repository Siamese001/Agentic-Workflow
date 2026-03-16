"""Full scanner violation dump for all buckets."""
from pathlib import Path

from agentic_core.L5_safety.static_checks.system_invariant_scanner import scan_repository_for_bypasses
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "check_scanner_full")
_emit_applies_guardrail("p0", "check_scanner_full", "p0_governance")
_emit_reads_policy_state("p0", "check_scanner_full", "policy_binding")
_emit_snapshots_state("p0", "check_scanner_full", "state_snapshot")
emit_replay_key("p0", "check_scanner_full")
emit_determinism_digest("p0", "check_scanner_full")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
root = Path(__file__).resolve().parents[2]
for bucket_rel in [L2_EXECUTION_DIR, L5_SAFETY_DIR, 'tests/sovereign_hardening']:
    bucket = (root / bucket_rel).resolve()
    violations = scan_repository_for_bypasses(bucket)
    prefix = str(bucket)
    filtered = [v for v in violations if str(Path(v.file_path).resolve()).startswith(prefix)]
    py_files = [f for f in bucket.rglob('*.py') if '__pycache__' not in f.parts]
    print(f'\n=== {bucket_rel}: {len(py_files)} files, {len(filtered)} violations ===')
    for v in filtered:
        print(f'  {Path(v.file_path).name}:{v.line} [{v.rule_id}]')
