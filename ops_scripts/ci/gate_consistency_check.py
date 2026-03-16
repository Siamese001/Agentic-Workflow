"""CI Self-Consistency Gate — Cross-Gate Validation.

Verifies internal consistency across all CI gate artifacts:
  1. Active set snapshot count matches live helper count + fingerprint.
  2. Active set snapshot JSON has required keys.
  3. MRO baseline total == len(entries) + required keys present.
  4. Centrality baseline exists, loads, and has required structure.
  5. Target manifest + schema exist and are valid JSON.

Exit 0 = all consistent, exit 1 = mismatch found.
"""
from __future__ import annotations

import json
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

_emit_records_execution_trace("p0", "evidence", "gate_consistency_check")
_emit_applies_guardrail("p0", "gate_consistency_check", "p0_governance")
_emit_reads_policy_state("p0", "gate_consistency_check", "policy_binding")
_emit_snapshots_state("p0", "gate_consistency_check", "state_snapshot")
emit_replay_key("p0", "gate_consistency_check")
emit_determinism_digest("p0", "gate_consistency_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
MRO_BASELINE_PATH = 'artifacts/consolidation/mro_diamond_baseline.json'
SNAPSHOT_PATH = 'artifacts/consolidation/active_set_snapshot.json'
CENTRALITY_BASELINE_PATH = 'artifacts/consolidation/centrality_baseline.json'
TARGET_MANIFEST_PATH = 'artifacts/consolidation/target_manifest_v3.json'
TARGET_MANIFEST_SCHEMA_PATH = 'artifacts/consolidation/target_manifest.schema.json'
_SNAPSHOT_REQUIRED_KEYS = {'count', 'fingerprint', 'first_10', 'last_10'}
_MRO_REQUIRED_KEYS = {'total', 'entries'}

def _check_required_keys(data: dict, required: set[str], label: str, errors: list[str]) -> None:
    missing = required - set(data.keys())
    if missing:
        errors.append(f'{label} missing required keys: {sorted(missing)}. Regenerate with the appropriate gate command.')

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    errors: list[str] = []
    checks_run = 0
    snapshot_file = project_root / SNAPSHOT_PATH
    if snapshot_file.is_file():
        try:
            snapshot = json.loads(snapshot_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            errors.append(f'Snapshot invalid JSON: {e}. Regenerate: python ops_scripts/ci/active_set_snapshot_check.py')
            snapshot = None
        if snapshot is not None:
            _check_required_keys(snapshot, _SNAPSHOT_REQUIRED_KEYS, 'Snapshot', errors)
            checks_run += 1
            snapshot_count = snapshot.get('count', -1)
            if str(project_root) not in sys.path:
                # guardian: allow-global-mutation
                sys.path.insert(0, str(project_root))
            try:
                from ops_scripts.ci.active_set_helper import get_active_set
                result = get_active_set(project_root)
                if result.count != snapshot_count:
                    errors.append(f"Active set count mismatch: snapshot={snapshot_count} live={result.count}. Fix: COMMIT_MESSAGE='ACTIVE_SET_SNAPSHOT_BUMP:<reason>' python ops_scripts/ci/active_set_snapshot_check.py")
                if result.fingerprint != snapshot.get('fingerprint', ''):
                    errors.append(f"Active set fingerprint mismatch: snapshot={snapshot.get('fingerprint', '')[:16]}... live={result.fingerprint[:16]}... Fix: COMMIT_MESSAGE='ACTIVE_SET_SNAPSHOT_BUMP:<reason>' python ops_scripts/ci/active_set_snapshot_check.py")
            # guardian: allow-silent-swallower
            except Exception as e:
                errors.append(f'Active set helper failed: {e}')
    else:
        errors.append(f'Snapshot not found: {SNAPSHOT_PATH}. Create: python ops_scripts/ci/active_set_snapshot_check.py')
    checks_run += 1
    mro_file = project_root / MRO_BASELINE_PATH
    if mro_file.is_file():
        try:
            mro = json.loads(mro_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            errors.append(f'MRO baseline invalid JSON: {e}. Regenerate: python ops_scripts/ci/_update_mro_baseline.py')
            mro = None
        if mro is not None:
            _check_required_keys(mro, _MRO_REQUIRED_KEYS, 'MRO baseline', errors)
            declared_total = mro.get('total', -1)
            entry_count = len(mro.get('entries', []))
            if declared_total != entry_count:
                errors.append(f'MRO baseline internal mismatch: total={declared_total} entries={entry_count}. Fix: python ops_scripts/ci/_update_mro_baseline.py')
    else:
        errors.append(f'MRO baseline not found: {MRO_BASELINE_PATH}. Create: python ops_scripts/ci/_update_mro_baseline.py')
    checks_run += 1
    centrality_file = project_root / CENTRALITY_BASELINE_PATH
    if centrality_file.is_file():
        try:
            centrality = json.loads(centrality_file.read_text(encoding='utf-8'))
            if not isinstance(centrality, (dict, list)):
                errors.append('Centrality baseline is not a valid JSON object/array')
        except json.JSONDecodeError as e:
            errors.append(f'Centrality baseline invalid JSON: {e}. Regenerate: python ops_scripts/ci/centrality_gate.py')
    else:
        errors.append(f'Centrality baseline not found: {CENTRALITY_BASELINE_PATH}. Create: python ops_scripts/ci/centrality_gate.py')
    checks_run += 1
    manifest_file = project_root / TARGET_MANIFEST_PATH
    schema_file = project_root / TARGET_MANIFEST_SCHEMA_PATH
    if manifest_file.is_file():
        try:
            manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
            if not isinstance(manifest, (dict, list)):
                errors.append('Target manifest is not a valid JSON object/array')
        except json.JSONDecodeError as e:
            errors.append(f'Target manifest invalid JSON: {e}')
    else:
        errors.append(f'Target manifest not found: {TARGET_MANIFEST_PATH}')
    if schema_file.is_file():
        try:
            json.loads(schema_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            errors.append(f'Target manifest schema invalid JSON: {e}')
    else:
        errors.append(f'Target manifest schema not found: {TARGET_MANIFEST_SCHEMA_PATH}')
    checks_run += 1
    print('CI Self-Consistency Gate:')
    print(f'  checks_run={checks_run}  errors={len(errors)}')
    if errors:
        print(f'FAIL: {len(errors)} consistency issue(s):')
        for e in errors:
            print(f'  - {e}')
        return 1
    print('PASS: all cross-gate artifacts are internally consistent')
    return 0
if __name__ == '__main__':
    sys.exit(main())
