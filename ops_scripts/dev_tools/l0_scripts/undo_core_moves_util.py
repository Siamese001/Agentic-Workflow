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

_emit_records_execution_trace("p0", "evidence", "undo_core_moves_util")
_emit_applies_guardrail("p0", "undo_core_moves_util", "p0_governance")
_emit_reads_policy_state("p0", "undo_core_moves_util", "policy_binding")
_emit_snapshots_state("p0", "undo_core_moves_util", "state_snapshot")
emit_replay_key("p0", "undo_core_moves_util")
emit_determinism_digest("p0", "undo_core_moves_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
'\nUndo all the incorrect core/ subdirectory moves\n'
import shutil
from pathlib import Path
from typing import Any

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
from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR, SCRIPTS_DIR


def undo_core_moves() -> Any:
    """Move all files back from */core/ to parent directories"""
    root: Any = Path('.')
    directories: Any = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, 'config', 'observability', 'schemas', SCRIPTS_DIR, TOOLS_DIR, 'validator', 'prompt_governance']
    moved_count: Any = 0
    for dir_name in directories:
        core_path: Any = root / dir_name / 'core'
        if not core_path.exists():
            continue
        from agentic_core.utils.ssot_discovery_validator import get_python_files
        for py_file in get_python_files(core_path):
            if py_file.name == '__init__.py':
                continue
            target: Any = core_path.parent / py_file.name
            if target.exists():
                print(f'Skipping {py_file} (target exists)')
                continue
            print(f'Moving {py_file} -> {dir_name}/{py_file.name}')
            shutil.move(str(py_file), str(target))
            moved_count += 1
        try:
            core_path.rmdir()
            print(f'Removed {dir_name}/core/')
        # guardian: allow-silent-swallow
        except:
            pass
    print(f'\nTotal files moved back: {moved_count}')
if __name__ == '__main__':
    undo_core_moves()
