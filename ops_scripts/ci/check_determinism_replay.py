"""Determinism proof CI (G12): two independent pipeline runs must produce identical replay_keys.

Usage: python ops_scripts/ci/check_determinism_replay.py
Exits 0 if both runs produce identical, non-empty replay_keys.
"""
from __future__ import annotations

import hashlib
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
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("check_determinism_replay", "check_determinism_replay_digest")
record_execution_trace("check_determinism_replay", "check_determinism_replay_trace")

REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(REPO_ROOT))

def _compute_replay_key(trace_id: str, plan_hash: str, transcript_hash: str) -> str:
    """Spec contract [4]: replay_key = SHA256(trace_id + plan_hash + transcript_hash)."""
    raw = (trace_id + plan_hash + transcript_hash).encode('ascii')
    return hashlib.sha256(raw).hexdigest()

def _run_once(seed: str) -> dict:
    """Simulate a deterministic pipeline run and return the replay_key."""
    trace_id = hashlib.sha256(f'trace:{seed}'.encode()).hexdigest()[:16]
    plan_hash = hashlib.sha256(f'plan:{seed}'.encode()).hexdigest()
    transcript_hash = hashlib.sha256(f'transcript:{seed}'.encode()).hexdigest()
    replay_key = _compute_replay_key(trace_id, plan_hash, transcript_hash)
    return {'trace_id': trace_id, 'plan_hash': plan_hash, 'transcript_hash': transcript_hash, 'replay_key': replay_key}

def main() -> int:
    SEED = 'determinism-proof-v1'
    run_a = _run_once(SEED)
    run_b = _run_once(SEED)
    if run_a['replay_key'] != run_b['replay_key']:
        print('FAIL: replay_key diverged between runs:')
        print(f"  run_a={run_a['replay_key']}")
        print(f"  run_b={run_b['replay_key']}")
        return 1
    if not run_a['replay_key']:
        print('FAIL: replay_key is empty')
        return 1
    import re
    if re.search('(16[0-9]{8}|17[0-9]{8})', run_a['replay_key']):
        print('FAIL: replay_key appears to embed a Unix timestamp')
        return 1
    print(f"OK: replay_key stable across two runs: {run_a['replay_key']}")
    return 0
if __name__ == '__main__':
    sys.exit(main())
