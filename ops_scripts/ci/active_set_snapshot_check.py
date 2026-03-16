"""Active Set Drift Snapshot Check — CI Gate.

Compares the current active set fingerprint against a committed snapshot.
If the fingerprint has changed, the commit must contain the tag:
    ACTIVE_SET_SNAPSHOT_BUMP:<reason>

This prevents silent active-set drift.

Exit 0 = pass, exit 1 = drift detected without acknowledgement.
"""
from __future__ import annotations

import json
import os
import sys
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "active_set_snapshot_check")
_emit_applies_guardrail("p0", "active_set_snapshot_check", "p0_governance")
_emit_reads_policy_state("p0", "active_set_snapshot_check", "policy_binding")
_emit_snapshots_state("p0", "active_set_snapshot_check", "state_snapshot")
emit_replay_key("p0", "active_set_snapshot_check")
emit_determinism_digest("p0", "active_set_snapshot_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
SNAPSHOT_PATH = 'artifacts/consolidation/active_set_snapshot.json'

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    snapshot_file = project_root / SNAPSHOT_PATH
    if not snapshot_file.is_file():
        print(f'FAIL: snapshot not found: {SNAPSHOT_PATH}', file=sys.stderr)
        return 1
    snapshot = json.loads(snapshot_file.read_text(encoding='utf-8'))
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))
    from ops_scripts.ci.active_set_helper import get_active_set
    result = get_active_set(project_root)
    print('Active Set Snapshot Check:')
    print(f"  snapshot_count={snapshot['count']}  current_count={result.count}")
    print(f"  snapshot_fingerprint={snapshot['fingerprint'][:16]}...")
    print(f'  current_fingerprint={result.fingerprint[:16]}...')
    if result.fingerprint == snapshot['fingerprint']:
        print('PASS: active set fingerprint matches snapshot')
        return 0
    commit_msg = os.environ.get('COMMIT_MESSAGE', '')
    if 'ACTIVE_SET_SNAPSHOT_BUMP:' in commit_msg:
        print(f"WARN: fingerprint changed ({snapshot['count']} → {result.count}) but ACTIVE_SET_SNAPSHOT_BUMP tag present")
        from ops_scripts.ci.baseline_io import write_json_atomic
        new_snapshot = {'count': result.count, 'fingerprint': result.fingerprint, 'first_10': list(result.agent_ids[:10]), 'last_10': list(result.agent_ids[-10:])}
        write_json_atomic(snapshot_file, new_snapshot)
        print(f"  AUTO-UPDATED snapshot: {snapshot['count']} → {result.count}")
        return 0
    print('FAIL: active set fingerprint changed without ACTIVE_SET_SNAPSHOT_BUMP tag')
    print(f"  old_count={snapshot['count']}  new_count={result.count}")
    print(f"  old_fingerprint={snapshot['fingerprint']}")
    print(f'  new_fingerprint={result.fingerprint}')
    old_first = snapshot.get('first_10', [])
    old_last = snapshot.get('last_10', [])
    new_first = list(result.agent_ids[:10])
    new_last = list(result.agent_ids[-10:])
    print(f'  old_first_10={old_first}')
    print(f'  new_first_10={new_first}')
    print(f'  old_last_10={old_last}')
    print(f'  new_last_10={new_last}')
    old_ids = set(old_first + old_last)
    new_ids = set(new_first + new_last)
    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    if added:
        print(f'  added: {added}')
    if removed:
        print(f'  removed: {removed}')
    print('  Fix: add ACTIVE_SET_SNAPSHOT_BUMP:<reason> to commit message and run:')
    print("    PYTHONPATH=. COMMIT_MESSAGE='ACTIVE_SET_SNAPSHOT_BUMP:<reason>' python ops_scripts/ci/active_set_snapshot_check.py")
    return 1
if __name__ == '__main__':
    sys.exit(main())
