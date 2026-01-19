from __future__ import annotations
"""
Sovereign Prune Empties - Final Stage of Hierarchy Healing
Purges empty legacy folders and stale __init__.py files after bulk move.
"""
import os
import shutil
from datetime import datetime
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
target_root: Any = AGENTIC_CORE_DIR
legacy_folders: Any = ['P1_core', 'P2_tools', 'P3_engines', 'P4_agents', 'P5_healing', 'P1_domain', 'P1_interfaces', 'P2_domain', 'P3_aggregation', 'P5_meta', 'boundaries', 'discovery', 'identity', 'inference', 'planning', 'planning_logic', 'mcp', 'sandbox', 'tools', 'event_bus', 'framework', 'handoff_logic', 'health', 'P5_workflow', 'protocol', 'security', 'training', 'automation', 'migrations', 'cache', 'checkpoints', 'filesystem', 'memory', 'persistence_layer', 'S1_store', 'semantic', 'session_manager', 'vector', 'P1_red_team', 'P4_security', 'audit_logs', 'gravity', 'policy', 'validators']

def main() -> Any:
    """Brief description of functionality and purpose."""
    project_root: Any = Path(__file__).resolve().parent.parent
    target_dir: Any = project_root / TARGET_ROOT
    audit_log: Any = project_root / 'mission_audit.csv'
    print(f'--- SOVEREIGN PRUNE START: {TARGET_ROOT} ---')
    pruned_count: Any = 0
    for layer in target_dir.iterdir():
        if not layer.is_dir() or not layer.name.startswith('L'):
            continue
        for legacy in LEGACY_FOLDERS:
            legacy_path: Any = layer / legacy
            if legacy_path.exists():
                files: Any = [f for f in legacy_path.rglob('*') if f.is_file()]
                if len(files) <= 1:
                    if not files or files[0].name == '__init__.py':
                        try:
                            timestamp: Any = datetime.now().isoformat()
                            with open(audit_log, 'a') as f:
                                f.write(f'{timestamp},{legacy},PURGE,{legacy_path.relative_to(project_root)},None,Legacy Pruning\n')
                            shutil.rmtree(legacy_path)
                            print(f'   [PURGE] Removed legacy folder: {legacy_path.relative_to(project_root)}')
                            pruned_count += 1
                        except Exception as e:
                            print(f'   [!] Error pruning {legacy}: {e}')
    print(f'\n[OK] Pruning complete. {pruned_count} legacy folders removed.')
    print('Run your validator now. Sovereignty awaits.')
if __name__ == '__main__':
    main()
