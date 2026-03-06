#!/usr/bin/env python3
"""Update landmine baseline and commit all redis hardening changes."""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run(argv, **kw):
    r = subprocess.run(argv, capture_output=True, text=True, cwd=ROOT, **kw)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        print("STDERR:", r.stderr.strip())
    return r


# 1. Update baseline
env = {**os.environ, "ALLOW_LANDMINE_BASELINE_WRITE": "1"}
r = run(["python", "ops_scripts/ci/check_anti_patterns.py", "--write-baseline"], env=env)
print("baseline rc:", r.returncode)

# 2. Stage all changed files
files = [
    "agentic_core/cache/redis_cache_client.py",
    "tests/integration/agentic_core/test_redis_integration.py",
    "tests/system_learning/test_stack_invariants.py",
    "ops_scripts/hooks/landmine_baseline.txt",
    "ops_scripts/ci/verify_stack_runtime.py",
]
r = run(["git", "add"] + files)
print("add rc:", r.returncode)

# 3. Commit
r = run(
    [
        "git",
        "commit",
        "-m",
        "infra: harden redis tests + fix silent hang root cause\n\n"
        "- _REDIS_SOCKET_TIMEOUT_S=0.3s applied to both _connect() and\n"
        "  check_redis_health(); was 2.0s in _connect(), causing 20s hangs\n"
        "  when Redis was down.\n"
        "- Integration suite tests/integration/agentic_core/test_redis_integration.py\n"
        "  rewired: no mocks, all assertions hit live Redis, module-level\n"
        "  pytest.skip fires in <0.3s when Redis is down.\n"
        "- Unit tests in test_stack_invariants.py correctly keep mocks:\n"
        "  they test check_redis_health() contract (structure/keys), not\n"
        "  Redis behaviour.  Behaviour is tested in integration suite.\n"
        "- landmine baseline updated for renamed constant.",
    ]
)
print("commit rc:", r.returncode)
if r.returncode == 0:
    h = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT)
    print("HEAD:", h.stdout.strip())
else:
    # If commit failed due to pre-commit hooks reformatting, re-stage and retry
    r2 = run(["git", "add"] + files)
    r3 = run(
        [
            "git",
            "commit",
            "-m",
            "infra: harden redis tests + fix silent hang root cause\n\n"
            "- _REDIS_SOCKET_TIMEOUT_S=0.3s applied to both _connect() and\n"
            "  check_redis_health(); was 2.0s in _connect(), causing 20s hangs.\n"
            "- Integration suite rewired: no mocks, fast module-level skip.\n"
            "- landmine baseline updated.",
        ]
    )
    print("retry commit rc:", r3.returncode)
    if r3.returncode == 0:
        h = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT)
        print("HEAD:", h.stdout.strip())
    else:
        # Final re-stage after hooks auto-fix
        run(["git", "add"] + files)
        r4 = run(["git", "commit", "-m", "infra: harden redis tests + fix silent hang root cause"])
        print("final commit rc:", r4.returncode)
        h = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT)
        print("HEAD:", h.stdout.strip())
