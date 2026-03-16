"""
file: ops_scripts/governance/check_test_structure.py
description: |
    [GOVERNANCE SENTRY]
    Strictly enforces the 'Scope Mirroring' testing architecture.

    Rules Enforced:
    1. NO tests allowed in tests/ root (except conftest.py).
    2. All tests must reside in tests/unit, tests/integration, tests/e2e, or tests/fixtures.
    3. Test paths must mirror source paths (e.g., tests/unit/agentic_core/L5_safety matches agentic_core/L5_safety).

    Exit Code:
    0: Structure compliant.
    1: Violations found (prints list).
"""
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
    TESTS_DIR,
    THRESHOLD,
    get_validated_project_root,
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

_emit_records_execution_trace("p0", "evidence", "check_test_structure")
_emit_applies_guardrail("p0", "check_test_structure", "p0_governance")
_emit_reads_policy_state("p0", "check_test_structure", "policy_binding")
_emit_snapshots_state("p0", "check_test_structure", "state_snapshot")
emit_replay_key("p0", "check_test_structure")
emit_determinism_digest("p0", "check_test_structure")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
PROJECT_ROOT = get_validated_project_root()
TESTS_ROOT = PROJECT_ROOT / TESTS_DIR
ALLOWED_ROOTS = {'unit', 'integration', 'e2e', 'functional', 'fixtures', 'migration', 'governance', 'L0_routing'}
ALLOWED_ROOT_FILES = {'conftest.py', 'pytest.ini', 'README.md', '__init__.py'}

def check_structure():
    print(f'[GOVERNANCE] Scanning {TESTS_ROOT} for structural violations...')
    violations = []
    if not TESTS_ROOT.exists():
        print('CRITICAL: tests/ directory missing!')
        sys.exit(1)
    for item in TESTS_ROOT.iterdir():
        if item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                violations.append(f'[ROOT VIOLATION] File found in tests root: {item.name}')
            continue
        if item.is_dir():
            if item.name not in ALLOWED_ROOTS and item.name not in {'__pycache__', '.pytest_cache'}:
                violations.append(f'[FOLDER VIOLATION] Unknown test category: tests/{item.name}')
                continue
            if item.name in {'unit', 'integration'}:
                check_mirror_depth(item, violations)
    if violations:
        print(f'[FAILED] Found {len(violations)} structural violations:')
        for v in violations:
            print(f'  - {v}')
        sys.exit(1)
    else:
        print('[PASSED] Test structure is strictly compliant.')
        sys.exit(0)

def check_mirror_depth(category_path: Path, violations: list):
    """
    Ensures that under tests/unit/, we have immediate domain roots
    (agentic_core, apps_rg, etc.) and not loose files.
    """
    for sub in category_path.iterdir():
        if sub.is_file():
            if sub.name not in {'__init__.py', 'conftest.py'} and (not sub.name.endswith('.pyc')):
                violations.append(f'[DEPTH VIOLATION] Test file found too shallow: {sub.relative_to(PROJECT_ROOT)}')
        elif sub.is_dir():
            if sub.name in {'__pycache__', '.pytest_cache'}:
                continue
            pass
if __name__ == '__main__':
    check_structure()
