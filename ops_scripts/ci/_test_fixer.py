"""Test fixer directly on the specific file."""
import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_test_fixer")
_emit_applies_guardrail("p0", "_test_fixer", "p0_governance")
_emit_reads_policy_state("p0", "_test_fixer", "policy_binding")
_emit_snapshots_state("p0", "_test_fixer", "state_snapshot")
emit_replay_key("p0", "_test_fixer")
emit_determinism_digest("p0", "_test_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# guardian: allow-global-mutation
sys.path.insert(0, '.')
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from ops_scripts.ci._fix_hardcoded_ssot_literals import process_file

file_path = Path('agentic_core/L0_routing/utils/scorched_earth_merge_util.py')
dry_run = True
fixes = process_file(file_path, str(file_path), dry_run=dry_run)
print(f'Found {len(fixes)} fixes:')
for fix in fixes:
    print(f'  {fix}')
