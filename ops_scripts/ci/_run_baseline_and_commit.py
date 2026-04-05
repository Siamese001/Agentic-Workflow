"""Update landmine baseline and commit all redis hardening changes."""
import os
import subprocess
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
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "_run_baseline_and_commit", "uwg_governed_write")
_emit_writes_through("p1", "_run_baseline_and_commit", "uwg_governed_write_2")
_emit_pulls_context("p1", "_run_baseline_and_commit", "context_retrieval")
_emit_pulls_context("p1", "_run_baseline_and_commit", "context_retrieval_2")
emit_determinism_digest("trace__run_baseline_and_commit", "_run_baseline_and_commit_dispatch")
emit_determinism_digest("trace__run_baseline_and_commit", "_run_baseline_and_commit_complete")
_emit_validated_by_safety_plane("p1", "_run_baseline_and_commit", "safety_validation")
# guardian: allow-path-string
ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).parent

def run(argv, **kw):
    r = subprocess.run(argv, capture_output=True, text=True, cwd=ROOT, **kw)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        print('STDERR:', r.stderr.strip())
    return r
env = {**os.environ, 'ALLOW_LANDMINE_BASELINE_WRITE': '1'}
r = run(['python', 'ops_scripts/ci/check_anti_patterns.py', '--write-baseline'], env=env)
print('baseline rc:', r.returncode)
files = ['agentic_core/cache/redis_cache_client.py', 'tests/integration/agentic_core/test_redis_integration.py', 'tests/system_learning/test_stack_invariants.py', 'ops_scripts/hooks/landmine_baseline.txt', 'ops_scripts/ci/verify_stack_runtime.py']
r = run(['git', 'add'] + files)
print('add rc:', r.returncode)
r = run(['git', 'commit', '-m', 'infra: harden redis tests + fix silent hang root cause\n\n- _REDIS_SOCKET_TIMEOUT_S=0.3s applied to both _connect() and\n  check_redis_health(); was 2.0s in _connect(), causing 20s hangs\n  when Redis was down.\n- Integration suite tests/integration/agentic_core/test_redis_integration.py\n  rewired: no mocks, all assertions hit live Redis, module-level\n  pytest.skip fires in <0.3s when Redis is down.\n- Unit tests in test_stack_invariants.py correctly keep mocks:\n  they test check_redis_health() contract (structure/keys), not\n  Redis behaviour.  Behaviour is tested in integration suite.\n- landmine baseline updated for renamed constant.'])
print('commit rc:', r.returncode)
if r.returncode == 0:
    h = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=ROOT)
    print('HEAD:', h.stdout.strip())
else:
    r2 = run(['git', 'add'] + files)
    r3 = run(['git', 'commit', '-m', 'infra: harden redis tests + fix silent hang root cause\n\n- _REDIS_SOCKET_TIMEOUT_S=0.3s applied to both _connect() and\n  check_redis_health(); was 2.0s in _connect(), causing 20s hangs.\n- Integration suite rewired: no mocks, fast module-level skip.\n- landmine baseline updated.'])
    print('retry commit rc:', r3.returncode)
    if r3.returncode == 0:
        h = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=ROOT)
        print('HEAD:', h.stdout.strip())
    else:
        run(['git', 'add'] + files)
        r4 = run(['git', 'commit', '-m', 'infra: harden redis tests + fix silent hang root cause'])
        print('final commit rc:', r4.returncode)
        h = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=ROOT)
        print('HEAD:', h.stdout.strip())
