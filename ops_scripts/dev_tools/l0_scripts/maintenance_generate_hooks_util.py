"""
ops_scripts/dev_tools/l0_scripts/maintenance_generate_hooks_util.py
-----------------------------------------------------------------
DEPRECATED: Redirects to the unified 'generate_hooks.py' script.
This file is retained as a stub to prevent breaking existing automation
that calls this specific path.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "maintenance_generate_hooks_util")
_emit_applies_guardrail("p0", "maintenance_generate_hooks_util", "p0_governance")
_emit_reads_policy_state("p0", "maintenance_generate_hooks_util", "policy_binding")
_emit_snapshots_state("p0", "maintenance_generate_hooks_util", "state_snapshot")
emit_replay_key("p0", "maintenance_generate_hooks_util")
emit_determinism_digest("p0", "maintenance_generate_hooks_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
project_root = Path(__file__).resolve().parent.parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.scripts.generate_hooks import generate_sovereign_list, sync_pre_commit

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sync pre-commit config with SSOT (Redirect)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--list', action='store_true', help='List current sovereign roots')
    args = parser.parse_args()
    print('[*] maintenance_generate_hooks_util.py is DEPRECATED. Redirecting to generate_hooks.py...')
    if args.list:
        generate_sovereign_list()
    else:
        success = sync_pre_commit(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
