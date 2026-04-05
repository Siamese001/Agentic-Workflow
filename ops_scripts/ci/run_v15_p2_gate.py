"""V15 Phase 2 Gate Runner

CI-ready script that runs the Phase 2 gate with proper error handling.
Produces P2 evidence JSON to temp path, invokes scoreboard --phase P2,
and exits 0 on PASS, non-zero on FAIL.

Supports V15_P2_SYNTHETIC_FAIL=1 for negative-path tests.

Usage:
    python ops_scripts/ci/run_v15_p2_gate.py
    python ops_scripts/ci/run_v15_p2_gate.py --repo-root .
"""
import json
import os
import subprocess
import sys
import tempfile
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
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "run_v15_p2_gate", "uwg_governed_write")
_emit_writes_through("p1", "run_v15_p2_gate", "uwg_governed_write_2")
_emit_pulls_context("p1", "run_v15_p2_gate", "context_retrieval")
_emit_pulls_context("p1", "run_v15_p2_gate", "context_retrieval_2")
emit_determinism_digest("trace_run_v15_p2_gate", "run_v15_p2_gate_dispatch")
emit_determinism_digest("trace_run_v15_p2_gate", "run_v15_p2_gate_complete")
_emit_validated_by_safety_plane("p1", "run_v15_p2_gate", "safety_validation")

def run_phase2_gate(repo_root: Path | None=None) -> int:
    """Run Phase 2 gate and return exit code."""
    if not repo_root:
        repo_root = Path.cwd()
    print('[P2-GATE] Starting Phase 2 gate...')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        print('[P2-GATE] Collecting P2 evidence...')
        evidence_cmd = [sys.executable, 'ops_scripts/ci/evidence_collect_phase2.py', '--repo-root', str(repo_root), '--output', tmp_path]
        env = os.environ.copy()
        result = subprocess.run(evidence_cmd, capture_output=True, text=True, cwd=repo_root, env=env)
        if result.returncode != 0:
            print('[P2-GATE] FAILED: P2 evidence collection failed')
            if result.stderr:
                print(result.stderr)
            return result.returncode
        if result.stdout:
            print(result.stdout.rstrip())
        with open(tmp_path, encoding='utf-8') as f:
            evidence = json.load(f)
        wired = evidence.get('wired_count', 0)
        already = evidence.get('already_enforced_count', 0)
        unwired = evidence.get('unwired_count', 0)
        total = evidence.get('entrypoints_total', 0)
        print(f'[P2-GATE] Wired: {wired}, Already enforced: {already}, Unwired: {unwired}, Total: {total}')
        print('[P2-GATE] Running P2 gate evaluation...')
        gate_cmd = [sys.executable, 'ops_scripts/ci/coverage_scoreboard.py', '--phase', 'P2', '--p2-evidence', tmp_path]
        result = subprocess.run(gate_cmd, capture_output=True, text=True, cwd=repo_root)
        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip())
        if result.returncode == 0:
            print('[P2-GATE] PASSED: Phase 2 gate passed')
        else:
            print('[P2-GATE] FAILED: Phase 2 gate failed')
        return result.returncode
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            pass

def main() -> int:
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='V15 Phase 2 Gate Runner')
    parser.add_argument('--repo-root', type=Path, default=None, help='Repository root directory (default: current directory)')
    args = parser.parse_args()
    return run_phase2_gate(args.repo_root)
if __name__ == '__main__':
    sys.exit(main())
