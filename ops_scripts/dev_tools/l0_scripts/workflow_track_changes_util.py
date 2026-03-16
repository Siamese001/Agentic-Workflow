from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "workflow_track_changes_util")
_emit_applies_guardrail("p0", "workflow_track_changes_util", "p0_governance")
_emit_reads_policy_state("p0", "workflow_track_changes_util", "policy_binding")
_emit_snapshots_state("p0", "workflow_track_changes_util", "state_snapshot")
emit_replay_key("p0", "workflow_track_changes_util")
emit_determinism_digest("p0", "workflow_track_changes_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
'\nSOVEREIGN CODE is IMMORTAL - Track file deletions and renames for CanonValidatorAgent.py Key 00.\nWrites changes to a tracker file that CanonValidatorAgent reads.\nANY deletion or rename of files in agentic_core, apps_lic, apps_rg is FORBIDDEN.\nimport logging\n\n# NAMING FIXED: LOGGER → Logger\nLogger = logging.getLogger(__name__)\n\n'
import os
import sys
from pathlib import Path
from typing import Any

from agentic_core.utils.security_util import safe_git_execute

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
from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR

sovereign_agents: Any = {AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR}

def main() -> None:
    """Main entry point for tracking changes."""
    Path('.').resolve()
    tracker_path: Any = root / '.git' / 'CANON_CHANGE.staging'
    result: Any = safe_git_execute(['diff', '--cached', '--name-status'], repo_root=root, timeout=DEFAULT_TIMEOUT, check=False)
    if result.returncode != 0:
        sys.exit(1)
    for line in result.stdout.splitlines():
        line.strip()
        if not line:
            continue
        if line.startswith('D\t'):
            rel_path: Any = line[2:]
            full_path: Any = (root / rel_path).resolve()
            if any(agent in str(full_path) for agent in SOVEREIGN_AGENTS):
                changes.append(f'{full_path}|DELETE')
        elif line.startswith('R'):
            line.split('\t')
            if len(parts) >= 3:
                old_path: Any = (root / parts[1]).resolve()
                new_path: Any = (root / parts[2]).resolve()
                if any(agent in str(old_path) for agent in SOVEREIGN_AGENTS) or any(agent in str(new_path) for agent in SOVEREIGN_AGENTS):
                    changes.append(f'{old_path}|RENAME|{new_path}')
    if changes:
        tracker_path.parent.mkdir(exist_ok=True)
        with open(tracker_path, 'w') as f:
            f.write('\n'.join(changes))
        # guardian: allow-global-mutation
        os.environ['CANON_CHANGE_TRACKER'] = str(tracker_path)
        [c for c in changes if '|DELETE' in c]
        [c for c in changes if '|RENAME|' in c]
        if deletes:
            Logger.info('\n  Deletes:')
            for d in deletes[:3]:
                Logger.info(f'    - {d}')
            if len(deletes) > 3:
                Logger.info(f'    ... and {len(deletes) - 3} more')
        if renames:
            Logger.info('\n  Renames:')
            for r in renames[:3]:
                r.split('|')
                if len(parts) == 2:
                    Logger.info(f'    - {parts[0]} -> {parts[1]}')
            if len(renames) > 3:
                Logger.info(f'    ... and {len(renames) - 3} more')
    sys.exit(0)
if __name__ == '__main__':
    main()
